<style>
body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: #f5f2ed;
    color: #2a2a28;
    margin: 0;
    padding: 40px 20px;
}
.container {
    max-width: 1200px;
    margin: 0 auto;
}
h1 {
    font-size: 48px;
    font-weight: 300;
    margin-bottom: 40px;
    text-align: center;
}
.products {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 30px;
    margin-top: 40px;
}
.product {
    background: white;
    border-radius: 8px;
    padding: 24px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    transition: transform 0.2s;
}
.product:hover {
    transform: translateY(-4px);
    box-shadow: 0 4px 16px rgba(0,0,0,0.12);
}
.product-image {
    width: 100%;
    height: 200px;
    background: #e8e5df;
    border-radius: 4px;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 48px;
}
.product-title {
    font-size: 20px;
    font-weight: 500;
    margin-bottom: 8px;
}
.product-description {
    color: #6b6860;
    font-size: 14px;
    line-height: 1.6;
    margin-bottom: 16px;
}
.product-price {
    font-size: 24px;
    font-weight: 600;
    margin-bottom: 16px;
}
.buy-button {
    width: 100%;
    background: #2a2a28;
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 4px;
    font-size: 16px;
    cursor: pointer;
    transition: background 0.2s;
}
.buy-button:hover {
    background: #3a3a38;
}
.buy-button:disabled {
    background: #ccc;
    cursor: not-allowed;
}
#status-message {
    text-align: center;
    padding: 16px;
    margin: 20px 0;
    border-radius: 4px;
    display: none;
}
.success {
    background: #d4edda;
    color: #155724;
}
.error {
    background: #f8d7da;
    color: #721c24;
}
</style>

<html>
<div class="container">
    <h1>Shop</h1>

    <div id="status-message"></div>

    <div class="products">
        <div class="product">
            <div class="product-image">🫘</div>
            <div class="product-title">Beans</div>
            <div class="product-description">A can of premium beans. The finest legumes money can buy.</div>
            <div class="product-price">$5.00</div>
            <button class="buy-button" onclick="checkout('price_1TGNLiC8ujWrRfLqBI1stNML', 'Beans')">Buy Now</button>
        </div>
    </div>
</div>

<script>
async function checkout(priceId, productName) {
    const button = event.target;
    button.disabled = true;
    button.textContent = 'Loading...';

    try {
        // Call your backend to create a checkout session
        const response = await fetch('/api/artists/sandbox/create-checkout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                price_id: priceId
            })
        });

        const text = await response.text();
        let data;

        try {
            data = JSON.parse(text);
        } catch (e) {
            console.error('Failed to parse response:', text);
            throw new Error('Invalid response from server. Please check the console for details.');
        }

        if (!response.ok) {
            throw new Error(data.error || 'Network response was not ok');
        }

        // Redirect to Stripe Checkout URL
        if (data.url) {
            window.location.href = data.url;
        } else {
            throw new Error('No checkout URL received');
        }
    } catch (error) {
        console.error('Error:', error);
        showMessage(error.message || 'Failed to initiate checkout. Please try again.', 'error');
        button.disabled = false;
        button.textContent = 'Buy Now';
    }
}

function showMessage(message, type) {
    const statusDiv = document.getElementById('status-message');
    statusDiv.textContent = message;
    statusDiv.className = type;
    statusDiv.style.display = 'block';

    setTimeout(() => {
        statusDiv.style.display = 'none';
    }, 5000);
}

// Check for success/cancel in URL params
const urlParams = new URLSearchParams(window.location.search);
if (urlParams.get('success')) {
    showMessage('Payment successful! Thank you for your purchase.', 'success');
}
if (urlParams.get('canceled')) {
    showMessage('Payment was canceled. Feel free to try again.', 'error');
}
</script>
</html>