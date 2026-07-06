import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db.models import Sum, Q, Count
from .models import Product, Order, OrderItem

def catalog_view(request):
    category = request.GET.get('category', None)
    lang = request.GET.get('lang', 'bn')  # Default to Bengali or English
    
    products = Product.objects.all()
    if category and category != 'All':
        products = products.filter(category__iexact=category)

    categories = Product.objects.values_list('category', flat=True).distinct()

    context = {
        'products': products,
        'categories': categories,
        'selected_category': category or 'All',
        'language': lang,
    }
    return render(request, 'shop/catalog.html', context)


def track_view(request):
    tracking_num = request.GET.get('tracking_number', '').strip()
    lang = request.GET.get('lang', 'bn')
    order = None
    error = None

    if tracking_num:
        try:
            order = Order.objects.prefetch_related('items__product').get(tracking_number__iexact=tracking_num)
        except Order.DoesNotExist:
            error = f"Order with tracking number '{tracking_num}' was not found."

    context = {
        'tracking_number': tracking_num,
        'order': order,
        'error': error,
        'language': lang,
    }
    return render(request, 'shop/track.html', context)


def seller_view(request):
    lang = request.GET.get('lang', 'en')
    
    # Calculate statistics
    total_sales = Order.objects.filter(payment_status='paid').aggregate(total=Sum('total_amount'))['total'] or 0
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status__in=['pending', 'processing']).count()
    completed_orders = Order.objects.filter(status='delivered').count()

    products = Product.objects.all()
    orders = Order.objects.prefetch_related('items__product').all()

    context = {
        'stats': {
            'total_sales': total_sales,
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'completed_orders': completed_orders,
        },
        'products': products,
        'orders': orders,
        'language': lang,
    }
    return render(request, 'shop/seller.html', context)


# ==========================================
# JSON API ENDPOINTS (FOR AJAX / CART DRAWER)
# ==========================================

def api_products_list(request):
    category = request.GET.get('category')
    products = Product.objects.all()
    if category and category != 'All':
        products = products.filter(category__iexact=category)

    data = [
        {
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'price': p.price,
            'category': p.category,
            'image': p.image,
            'stock': p.stock,
        }
        for p in products
    ]
    return JsonResponse({'success': True, 'data': data})


@csrf_exempt
def api_checkout(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST method required'}, status=405)

    try:
        body = json.loads(request.body.decode('utf-8'))
        guest_name = body.get('guestName')
        guest_email = body.get('guestEmail')
        phone_number = body.get('phoneNumber')
        shipping_address = body.get('shippingAddress')
        payment_method = body.get('paymentMethod', 'cod')
        sender_number = body.get('senderNumber', '')
        transaction_id = body.get('transactionId', '')
        items = body.get('items', [])

        if not guest_name or not guest_email or not phone_number or not shipping_address:
            return JsonResponse({'success': False, 'error': 'Name, email, phone number, and address are required.'}, status=400)

        if not items:
            return JsonResponse({'success': False, 'error': 'Your cart is empty.'}, status=400)

        # Process order in a thread-safe database transaction with row locking
        with transaction.atomic():
            total_amount = 0
            order_items_to_create = []

            for item in items:
                product_id = item.get('productId')
                quantity = int(item.get('quantity', 1))

                # Lock product row to prevent stock race conditions
                product = Product.objects.select_for_update().get(id=product_id)

                if product.stock < quantity:
                    return JsonResponse({
                        'success': False,
                        'error': f"Insufficient stock for '{product.name}'. Only {product.stock} left in stock."
                    }, status=400)

                # Deduct stock
                product.stock -= quantity
                product.save()

                item_price = product.price
                total_amount += item_price * quantity
                order_items_to_create.append({
                    'product': product,
                    'quantity': quantity,
                    'price_at_purchase': item_price
                })

            # Format payment details
            payment_status = 'unpaid' if payment_method == 'cod' else 'paid'
            payment_details = f"CoD" if payment_method == 'cod' else f"{payment_method.upper()} Sender: {sender_number}, TrxID: {transaction_id}"

            formatted_guest_name = f"{guest_name} (Ph: {phone_number})"
            formatted_address = f"{shipping_address} [Payment: {payment_details}]"

            # Create Order
            new_order = Order.objects.create(
                guest_name=formatted_guest_name,
                guest_email=guest_email,
                phone_number=phone_number,
                shipping_address=formatted_address,
                payment_method=payment_method,
                payment_status=payment_status,
                payment_details=payment_details,
                status='processing',
                total_amount=total_amount
            )

            # Create Order Items
            for oi in order_items_to_create:
                OrderItem.objects.create(
                    order=new_order,
                    product=oi['product'],
                    quantity=oi['quantity'],
                    price_at_purchase=oi['price_at_purchase']
                )

            return JsonResponse({
                'success': True,
                'message': 'Order placed successfully',
                'trackingNumber': new_order.tracking_number,
                'totalAmount': new_order.total_amount,
            }, status=201)

    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Product not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def api_track_order(request, tracking_number):
    try:
        order = Order.objects.prefetch_related('items__product').get(tracking_number__iexact=tracking_number.strip())
        items_data = [
            {
                'id': item.id,
                'quantity': item.quantity,
                'priceAtPurchase': item.price_at_purchase,
                'product': {
                    'id': item.product.id,
                    'name': item.product.name,
                    'image': item.product.image,
                }
            }
            for item in order.items.all()
        ]
        
        return JsonResponse({
            'success': True,
            'data': {
                'id': order.id,
                'trackingNumber': order.tracking_number,
                'guestName': order.guest_name,
                'guestEmail': order.guest_email,
                'shippingAddress': order.shipping_address,
                'paymentMethod': order.payment_method,
                'paymentStatus': order.payment_status,
                'status': order.status,
                'totalAmount': order.total_amount,
                'createdAt': order.created_at.isoformat(),
                'items': items_data
            }
        })
    except Order.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Order not found with that tracking number.'}, status=404)


@csrf_exempt
def api_seller_update_stock(request, product_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST method required'}, status=405)

    try:
        body = json.loads(request.body.decode('utf-8'))
        stock = int(body.get('stock', 0))
        product = get_object_or_404(Product, id=product_id)
        product.stock = max(0, stock)
        product.save()
        return JsonResponse({'success': True, 'stock': product.stock})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
def api_seller_update_order_status(request, order_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST method required'}, status=405)

    try:
        body = json.loads(request.body.decode('utf-8'))
        new_status = body.get('status')
        order = get_object_or_404(Order, id=order_id)
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            if new_status == 'delivered' and order.payment_method == 'cod':
                order.payment_status = 'paid'
            order.save()
            return JsonResponse({'success': True, 'status': order.status, 'paymentStatus': order.payment_status})
        return JsonResponse({'success': False, 'error': 'Invalid status choice'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
def api_seller_add_product(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)

    try:
        body = json.loads(request.body.decode('utf-8'))
        product = Product.objects.create(
            name=body.get('name'),
            description=body.get('description'),
            price=int(body.get('price', 0)),
            category=body.get('category', 'General'),
            image=body.get('image') or "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&q=80&w=600",
            stock=int(body.get('stock', 10))
        )
        return JsonResponse({'success': True, 'productId': product.id}, status=201)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
