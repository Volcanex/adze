"""
Bookings feature — per-artist booking/enquiry system.

Opt in via config.json: { "features": ["bookings"] }
Registers routes at /api/artists/{slug}/bookings/...
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from flask import Blueprint, jsonify, request, abort

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from auth import get_authenticated_artist, verify_artist_token


FEATURE_NAME = 'bookings'

ENDPOINT_DESCRIPTIONS = {
    'submit': {
        'summary': 'Booking form submission',
        'detail': 'Public endpoint — this is where your booking/contact form sends data. No login required.',
        'auth': False,
    },
    'list': {
        'summary': 'View bookings',
        'detail': 'See all enquiries people have submitted through your site.',
        'auth': True,
    },
    'update': {
        'summary': 'Update a booking',
        'detail': 'Change the status or add notes to a booking enquiry.',
        'auth': True,
    },
    'delete': {
        'summary': 'Delete a booking',
        'detail': 'Remove a booking enquiry permanently.',
        'auth': True,
    },
}


def _get_bookings_path(artist_slug):
    return Path(f'pages/artists/{artist_slug}/bookings.json')


def _load_bookings(artist_slug):
    path = _get_bookings_path(artist_slug)
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return []


def _save_bookings(artist_slug, bookings):
    path = _get_bookings_path(artist_slug)
    with open(path, 'w') as f:
        json.dump(bookings, f, indent=2)


def create_blueprint(artist_slug):
    """
    Create a bookings Blueprint scoped to a specific artist.

    Routes:
        POST /api/artists/{slug}/bookings/submit   (public)
        GET  /api/artists/{slug}/bookings/list      (auth)
        POST /api/artists/{slug}/bookings/update    (auth)
        POST /api/artists/{slug}/bookings/delete    (auth)
    """
    bp = Blueprint(
        f'bookings_{artist_slug}',
        __name__,
        url_prefix=f'/api/artists/{artist_slug}/bookings'
    )

    def _require_auth():
        """Check auth for this specific artist."""
        slug = request.headers.get('X-Artist-Slug', '')
        token = request.headers.get('X-Admin-Token', '')
        if slug != artist_slug or not verify_artist_token(artist_slug, token):
            abort(401, description='Authentication required')

    @bp.route('/submit', methods=['POST'])
    def submit_enquiry():
        """Public endpoint — no auth needed."""
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        subject = data.get('subject', '').strip()
        message = data.get('message', '').strip()
        service = data.get('service', '').strip()

        if not name or not email or not message:
            return jsonify({'error': 'Name, email and message are required'}), 400

        enquiry = {
            'id': str(uuid.uuid4())[:8],
            'name': name,
            'email': email,
            'subject': subject,
            'service': service,
            'message': message,
            'date': datetime.utcnow().isoformat() + 'Z',
            'status': 'new',
            'notes': ''
        }

        bookings = _load_bookings(artist_slug)
        bookings.insert(0, enquiry)
        _save_bookings(artist_slug, bookings)

        return jsonify({'ok': True, 'message': 'Enquiry submitted successfully'})

    @bp.route('/list', methods=['GET'])
    def list_bookings():
        """List all booking enquiries. Requires auth."""
        _require_auth()
        bookings = _load_bookings(artist_slug)
        return jsonify({'bookings': bookings})

    @bp.route('/update', methods=['POST'])
    def update_booking():
        """Update a booking's status or notes. Requires auth."""
        _require_auth()
        data = request.get_json()
        booking_id = data.get('id')
        if not booking_id:
            return jsonify({'error': 'Booking ID required'}), 400

        bookings = _load_bookings(artist_slug)
        for b in bookings:
            if b['id'] == booking_id:
                if 'status' in data:
                    b['status'] = data['status']
                if 'notes' in data:
                    b['notes'] = data['notes']
                _save_bookings(artist_slug, bookings)
                return jsonify({'ok': True})

        return jsonify({'error': 'Booking not found'}), 404

    @bp.route('/delete', methods=['POST'])
    def delete_booking():
        """Delete a booking enquiry. Requires auth."""
        _require_auth()
        data = request.get_json()
        booking_id = data.get('id')
        if not booking_id:
            return jsonify({'error': 'Booking ID required'}), 400

        bookings = _load_bookings(artist_slug)
        bookings = [b for b in bookings if b['id'] != booking_id]
        _save_bookings(artist_slug, bookings)
        return jsonify({'ok': True})

    return bp
