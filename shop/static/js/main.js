/**
 * AuraMarket - Sleek Slate & Minimal Gold Client Logic
 * Handles Cart, 3D Card Tilt, Language Switcher, and Checkout AJAX
 */

let cart = JSON.parse(localStorage.getItem('auramarket_cart') || '[]');
let currentPaymentMethod = 'cod';

document.addEventListener('DOMContentLoaded', () => {
    updateCartUI();
    init3DTilt();
    initLucideIcons();
});

// Initialize Lucide Icons if available
function initLucideIcons() {
    if (window.lucide) {
        window.lucide.createIcons();
    }
}

// ------------------------------------
// 3D Tilt Effect for Product Cards
// ------------------------------------
function init3DTilt() {
    const cards = document.querySelectorAll('.card-perspective');
    cards.forEach(wrapper => {
        const card = wrapper.querySelector('.product-card-3d');
        if (!card) return;

        wrapper.addEventListener('mousemove', (e) => {
            const rect = wrapper.getBoundingClientRect();
            const x = (e.clientX - rect.left) / rect.width - 0.5;
            const y = (e.clientY - rect.top) / rect.height - 0.5;

            const rotateX = -y * 14;
            const rotateY = x * 14;
            const shadowX = -x * 15;
            const shadowY = -y * 15;

            card.style.transform = `rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`;
            card.style.boxShadow = `${shadowX}px ${shadowY}px 25px rgba(0, 0, 0, 0.12), 0 8px 16px rgba(0, 0, 0, 0.06)`;
        });

        wrapper.addEventListener('mouseleave', () => {
            card.style.transform = 'rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)';
            card.style.boxShadow = '0 1px 3px rgba(0,0,0,0.05)';
        });
    });
}

// ------------------------------------
// Shopping Cart Operations
// ------------------------------------
function addToCart(productId, name, price, image, maxStock) {
    const existing = cart.find(item => item.id === productId);
    if (existing) {
        if (existing.quantity < maxStock) {
            existing.quantity += 1;
        } else {
            alert(`Sorry! Maximum stock limit (${maxStock}) reached for this product.`);
            return;
        }
    } else {
        cart.push({
            id: productId,
            name: name,
            price: price,
            image: image,
            quantity: 1,
            maxStock: maxStock
        });
    }

    saveCart();
    openCartDrawer();
}

function updateCartQuantity(productId, newQty) {
    const item = cart.find(i => i.id === productId);
    if (item) {
        item.quantity = Math.min(item.maxStock, Math.max(1, parseInt(newQty)));
        saveCart();
    }
}

function removeFromCart(productId) {
    cart = cart.filter(item => item.id !== productId);
    saveCart();
}

function saveCart() {
    localStorage.setItem('auramarket_cart', JSON.stringify(cart));
    updateCartUI();
}

function updateCartUI() {
    const countBadge = document.getElementById('cart-count-badge');
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);

    if (countBadge) {
        countBadge.innerText = totalItems;
        countBadge.style.display = totalItems > 0 ? 'inline-block' : 'none';
    }

    renderCartItems();
}

function renderCartItems() {
    const container = document.getElementById('cart-items-container');
    const totalDisplay = document.getElementById('cart-total-display');
    const checkoutBtn = document.getElementById('cart-checkout-submit-btn');

    if (!container) return;

    if (cart.length === 0) {
        container.innerHTML = `
            <div class="flex flex-col items-center justify-center py-20 text-center">
                <div class="p-4 bg-gray-50 rounded-full text-gray-400 mb-4">
                    <i data-lucide="shopping-bag" class="w-10 h-10"></i>
                </div>
                <p class="text-gray-500 font-medium">Your shopping bag is empty.</p>
                <p class="text-gray-400 text-xs mt-1">Add products from our catalog to proceed with checkout.</p>
            </div>
        `;
        if (totalDisplay) totalDisplay.innerText = '৳0';
        if (checkoutBtn) checkoutBtn.disabled = true;
        initLucideIcons();
        return;
    }

    if (checkoutBtn) checkoutBtn.disabled = false;

    let totalAmount = 0;
    let html = '<div class="divide-y divide-gray-100 space-y-3">';

    cart.forEach(item => {
        const itemTotal = item.price * item.quantity;
        totalAmount += itemTotal;

        html += `
            <div class="py-3 flex justify-between space-x-4 items-center">
                <img src="${item.image}" alt="${item.name}" class="w-16 h-16 object-cover rounded-xl border border-gray-100">
                <div class="flex-1">
                    <p class="font-semibold text-gray-900 text-sm">${item.name}</p>
                    <p class="text-xs text-amber-700 font-mono font-medium">৳${item.price.toLocaleString()} each</p>
                    <div class="flex items-center space-x-2 mt-1">
                        <label class="text-xs text-gray-400">Qty:</label>
                        <select onchange="updateCartQuantity(${item.id}, this.value)" class="bg-gray-50 border border-gray-200 text-xs rounded-md px-1 py-0.5">
                            ${Array.from({ length: item.maxStock }, (_, i) => i + 1).map(n => 
                                `<option value="${n}" ${n === item.quantity ? 'selected' : ''}>${n}</option>`
                            ).join('')}
                        </select>
                    </div>
                </div>
                <div class="flex flex-col items-end space-y-2">
                    <span class="font-bold text-gray-900 text-sm">৳${itemTotal.toLocaleString()}</span>
                    <button onclick="removeFromCart(${item.id})" class="text-gray-400 hover:text-red-500 p-1">
                        <i data-lucide="trash-2" class="w-4 h-4"></i>
                    </button>
                </div>
            </div>
        `;
    });

    html += '</div>';
    container.innerHTML = html;

    if (totalDisplay) {
        totalDisplay.innerText = `৳${totalAmount.toLocaleString()}`;
    }

    initLucideIcons();
}

// Drawer Controls
function openCartDrawer() {
    const drawer = document.getElementById('cart-drawer');
    if (drawer) drawer.classList.remove('hidden');
}

function closeCartDrawer() {
    const drawer = document.getElementById('cart-drawer');
    if (drawer) drawer.classList.add('hidden');
}

// Payment Method Selector (CoD, bKash, Nagad)
function selectPaymentMethod(method) {
    currentPaymentMethod = method;
    const codBox = document.getElementById('payment-instructions-cod');
    const mobileBox = document.getElementById('payment-instructions-mobile');

    document.querySelectorAll('.payment-method-btn').forEach(btn => {
        btn.classList.remove('bg-black', 'text-white', 'border-black', 'bg-pink-600', 'bg-orange-600');
        btn.classList.add('bg-gray-50', 'text-gray-600', 'border-gray-200');
    });

    const activeBtn = document.getElementById(`payment-btn-${method}`);
    if (activeBtn) {
        activeBtn.classList.remove('bg-gray-50', 'text-gray-600', 'border-gray-200');
        if (method === 'cod') activeBtn.classList.add('bg-black', 'text-white', 'border-black');
        if (method === 'bkash') activeBtn.classList.add('bg-pink-600', 'text-white', 'border-pink-600');
        if (method === 'nagad') activeBtn.classList.add('bg-orange-600', 'text-white', 'border-orange-600');
    }

    if (method === 'cod') {
        if (codBox) codBox.classList.remove('hidden');
        if (mobileBox) mobileBox.classList.add('hidden');
    } else {
        if (codBox) codBox.classList.add('hidden');
        if (mobileBox) mobileBox.classList.remove('hidden');
    }
}

// Submit Order via AJAX
async function handleCheckoutFormSubmit(event) {
    event.preventDefault();

    if (cart.length === 0) {
        alert("Your cart is empty!");
        return;
    }

    const name = document.getElementById('guest_name').value.trim();
    const email = document.getElementById('guest_email').value.trim();
    const phone = document.getElementById('phone_number').value.trim();
    const address = document.getElementById('shipping_address').value.trim();
    const senderNumber = document.getElementById('sender_number')?.value.trim() || '';
    const transactionId = document.getElementById('transaction_id')?.value.trim() || '';

    const errorDiv = document.getElementById('checkout-error-msg');
    if (errorDiv) errorDiv.classList.add('hidden');

    if (currentPaymentMethod !== 'cod' && (!senderNumber || !transactionId)) {
        if (errorDiv) {
            errorDiv.innerText = "Please enter both Sender Mobile Number and Transaction ID (TrxID).";
            errorDiv.classList.remove('hidden');
        }
        return;
    }

    const payload = {
        guestName: name,
        guestEmail: email,
        phoneNumber: phone,
        shippingAddress: address,
        paymentMethod: currentPaymentMethod,
        senderNumber: senderNumber,
        transactionId: transactionId,
        items: cart.map(item => ({ productId: item.id, quantity: item.quantity }))
    };

    const submitBtn = document.getElementById('cart-checkout-submit-btn');
    if (submitBtn) submitBtn.disabled = true;

    try {
        const response = await fetch('/api/checkout/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const res = await response.json();

        if (response.ok && res.success) {
            cart = [];
            saveCart();
            closeCartDrawer();
            window.location.href = `/track/?tracking_number=${res.trackingNumber}`;
        } else {
            throw new Error(res.error || 'Failed to place order.');
        }
    } catch (err) {
        if (errorDiv) {
            errorDiv.innerText = err.message;
            errorDiv.classList.remove('hidden');
        } else {
            alert(err.message);
        }
    } finally {
        if (submitBtn) submitBtn.disabled = false;
    }
}
