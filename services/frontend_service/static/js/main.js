// Main JavaScript for E-Commerce Frontend

// Auto-hide messages after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const messages = document.querySelectorAll('[role="alert"]');
    messages.forEach(message => {
        setTimeout(() => {
            message.style.transition = 'opacity 0.5s';
            message.style.opacity = '0';
            setTimeout(() => message.remove(), 500);
        }, 5000);
    });
});

// Add to cart functionality
function addToCart(productId, quantity = 1) {
    // TODO: Implement add to cart logic
    console.log(`Adding product ${productId} to cart with quantity ${quantity}`);
}

// Update cart count
function updateCartCount() {
    // TODO: Fetch cart count from backend
    console.log('Updating cart count');
}

// Search functionality
function searchProducts(query) {
    // TODO: Implement search logic
    console.log(`Searching for: ${query}`);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    updateCartCount();
});
