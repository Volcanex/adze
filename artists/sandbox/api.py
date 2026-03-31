import os
import json
from flask import Blueprint, jsonify, request
from pathlib import Path

bp = Blueprint('artist_sandbox', __name__, url_prefix='/api/artists/sandbox')

# Load .env
_env = {}
_env_path = Path(__file__).parent / '.env'
if _env_path.exists():
    for line in _env_path.read_text().strip().split('\n'):
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, _, v = line.partition('=')
            _env[k.strip()] = v.strip().strip('"').strip("'")


# ── Stripe Checkout ──────────────────────────────────────────────────────

@bp.route('/create-checkout', methods=['POST'])
def create_checkout():
    """Create a Stripe Checkout Session and return the URL."""
    import stripe
    stripe.api_key = _env.get('STRIPE_SECRET_KEY', '')
    if not stripe.api_key:
        return jsonify({'error': 'Stripe not configured'}), 400

    data = request.get_json()
    price_id = data.get('price_id')
    if not price_id:
        return jsonify({'error': 'price_id required'}), 400

    # Dynamically determine the base URL from the request
    # This works for both localhost and custom domains
    host = request.headers.get('Host', 'localhost:5000')
    scheme = request.headers.get('X-Forwarded-Proto', 'https' if request.is_secure else 'http')
    base_url = f'{scheme}://{host}'

    # Determine the shop path based on whether we're on a custom domain
    config_path = Path(__file__).parent / 'config.json'
    if config_path.exists():
        try:
            config = json.loads(config_path.read_text())
            domain = config.get('domain', '')
            # If the host matches our custom domain, use root-level paths
            if domain and domain in host:
                shop_path = '/shop'
            else:
                shop_path = '/artists/sandbox/shop'
        except:
            shop_path = '/artists/sandbox/shop'
    else:
        shop_path = '/artists/sandbox/shop'

    try:
        session = stripe.checkout.Session.create(
            mode='payment',
            line_items=[{'price': price_id, 'quantity': 1}],
            success_url=f'{base_url}{shop_path}?success=true&session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=f'{base_url}{shop_path}?canceled=true',
            shipping_address_collection={'allowed_countries': ['GB', 'US', 'CA', 'AU', 'DE', 'FR', 'NL', 'IE']},
            metadata={'artist': 'sandbox'},
        )
        return jsonify({'url': session.url})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events (payment confirmations, etc.)."""
    import stripe
    stripe.api_key = _env.get('STRIPE_SECRET_KEY', '')
    endpoint_secret = _env.get('STRIPE_ENDPOINT_SECRET', '')

    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature', '')

    if endpoint_secret:
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except ValueError:
            return 'Invalid payload', 400
        except stripe.error.SignatureVerificationError:
            return 'Invalid signature', 400
    else:
        # No webhook secret configured — parse but don't verify (dev mode)
        event = json.loads(payload)

    event_type = event.get('type', '')

    if event_type == 'checkout.session.completed':
        session_data = event['data']['object']
        # Store the order
        orders_file = Path(__file__).parent / 'orders.json'
        orders = []
        if orders_file.exists():
            try:
                orders = json.loads(orders_file.read_text())
            except:
                pass
        orders.append({
            'session_id': session_data.get('id'),
            'customer_email': session_data.get('customer_details', {}).get('email', ''),
            'amount_total': session_data.get('amount_total'),
            'currency': session_data.get('currency'),
            'status': session_data.get('payment_status'),
            'created': session_data.get('created'),
            'shipping': session_data.get('shipping_details'),
        })
        orders_file.write_text(json.dumps(orders, indent=2))

    return 'OK', 200


@bp.route('/orders', methods=['GET'])
def list_orders():
    """List orders (for dashboard use — requires auth header check in production)."""
    orders_file = Path(__file__).parent / 'orders.json'
    if not orders_file.exists():
        return jsonify({'orders': []})
    try:
        orders = json.loads(orders_file.read_text())
        return jsonify({'orders': orders})
    except:
        return jsonify({'orders': []})


# ── Booking System ───────────────────────────────────────────────────────

@bp.route('/book', methods=['POST'])
def create_booking():
    """Create a new booking and save to bookings.json."""
    data = request.get_json()

    # Validate required fields
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    date = data.get('date', '').strip()
    time = data.get('time', '').strip()
    notes = data.get('notes', '').strip()

    if not all([name, email, date, time]):
        return jsonify({'error': 'Name, email, date, and time are required'}), 400

    # Load existing bookings
    bookings_file = Path(__file__).parent / 'bookings.json'
    bookings = []
    if bookings_file.exists():
        try:
            bookings = json.loads(bookings_file.read_text())
        except:
            pass

    # Create new booking
    import time as time_module
    booking = {
        'id': len(bookings) + 1,
        'name': name,
        'email': email,
        'date': date,
        'time': time,
        'notes': notes,
        'created_at': int(time_module.time()),
        'status': 'pending'
    }

    bookings.append(booking)
    bookings_file.write_text(json.dumps(bookings, indent=2))

    return jsonify({'success': True, 'booking': booking}), 201


@bp.route('/bookings', methods=['GET'])
def list_bookings():
    """List all bookings (for dashboard widget)."""
    bookings_file = Path(__file__).parent / 'bookings.json'
    if not bookings_file.exists():
        return jsonify({'bookings': []})
    try:
        bookings = json.loads(bookings_file.read_text())
        return jsonify({'bookings': bookings})
    except:
        return jsonify({'bookings': []})
