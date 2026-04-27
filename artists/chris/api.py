from flask import Blueprint, jsonify, request
import sqlite3
import json
import os
from datetime import datetime
import uuid

bp = Blueprint('artist_chris', __name__, url_prefix='/api/artists/chris')

DB_PATH = os.path.join(os.path.dirname(__file__), 'bookings.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def row_to_dict(row):
    if row is None:
        return None
    d = dict(row)
    # Parse JSON fields
    if 'amenities' in d and d['amenities']:
        try:
            d['amenities'] = json.loads(d['amenities'])
        except:
            d['amenities'] = []
    return d

# ============ LOCATIONS ============

@bp.route('/locations')
def get_locations():
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT * FROM locations WHERE is_active = 1 ORDER BY name')
        locations = [row_to_dict(row) for row in c.fetchall()]
        conn.close()
        return jsonify(locations)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/locations/<location_id>')
def get_location(location_id):
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT * FROM locations WHERE id = ? AND is_active = 1', (location_id,))
        location = row_to_dict(c.fetchone())
        
        if not location:
            conn.close()
            return jsonify({'error': 'Location not found'}), 404
        
        # Get saunas at this location
        c.execute('SELECT * FROM saunas WHERE location_id = ? AND is_active = 1', (location_id,))
        location['saunas'] = [row_to_dict(row) for row in c.fetchall()]
        
        # Get testimonials
        c.execute('SELECT * FROM testimonials WHERE location_id = ? ORDER BY created_at DESC', (location_id,))
        location['testimonials'] = [row_to_dict(row) for row in c.fetchall()]
        
        # Get team members
        c.execute('SELECT * FROM team_members WHERE location_id = ? ORDER BY created_at', (location_id,))
        location['team_members'] = [row_to_dict(row) for row in c.fetchall()]
        
        conn.close()
        return jsonify(location)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ SAUNAS ============

@bp.route('/saunas')
def get_saunas():
    try:
        conn = get_db()
        c = conn.cursor()
        location_id = request.args.get('location_id')
        
        if location_id:
            c.execute('SELECT * FROM saunas WHERE location_id = ? AND is_active = 1 ORDER BY name', (location_id,))
        else:
            c.execute('SELECT * FROM saunas WHERE is_active = 1 ORDER BY name')
        
        saunas = [row_to_dict(row) for row in c.fetchall()]
        conn.close()
        return jsonify(saunas)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/saunas/<sauna_id>')
def get_sauna(sauna_id):
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT * FROM saunas WHERE id = ? AND is_active = 1', (sauna_id,))
        sauna = row_to_dict(c.fetchone())
        
        if not sauna:
            conn.close()
            return jsonify({'error': 'Sauna not found'}), 404
        
        # Get location info
        c.execute('SELECT * FROM locations WHERE id = ?', (sauna['location_id'],))
        sauna['location'] = row_to_dict(c.fetchone())
        
        conn.close()
        return jsonify(sauna)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ TIME SLOTS ============

@bp.route('/time-slots')
def get_time_slots():
    try:
        conn = get_db()
        c = conn.cursor()
        
        sauna_id = request.args.get('sauna_id')
        date = request.args.get('date')
        
        query = 'SELECT * FROM time_slots WHERE is_active = 1'
        params = []
        
        if sauna_id:
            query += ' AND sauna_id = ?'
            params.append(sauna_id)
        
        if date:
            query += ' AND date = ?'
            params.append(date)
        
        query += ' ORDER BY date, start_time'
        
        c.execute(query, params)
        slots = [row_to_dict(row) for row in c.fetchall()]
        
        # Get sauna info for each slot
        for slot in slots:
            c.execute('SELECT * FROM saunas WHERE id = ?', (slot['sauna_id'],))
            slot['sauna'] = row_to_dict(c.fetchone())
        
        conn.close()
        return jsonify(slots)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ BOOKINGS ============

@bp.route('/bookings', methods=['POST'])
def create_booking():
    try:
        data = request.json
        
        # Validate required fields
        required = ['time_slot_id', 'sauna_id', 'seats_booked', 'customer_email', 'customer_name']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        conn = get_db()
        c = conn.cursor()
        
        # Check availability
        c.execute('SELECT available_seats FROM time_slots WHERE id = ? AND is_active = 1', 
                  (data['time_slot_id'],))
        slot = c.fetchone()
        
        if not slot:
            conn.close()
            return jsonify({'error': 'Time slot not found'}), 404
        
        if slot['available_seats'] < data['seats_booked']:
            conn.close()
            return jsonify({'error': 'Not enough seats available'}), 400
        
        # Get sauna price
        c.execute('SELECT price_per_seat FROM saunas WHERE id = ?', (data['sauna_id'],))
        sauna = c.fetchone()
        total_price = float(sauna['price_per_seat']) * data['seats_booked']
        
        # Create booking
        booking_id = str(uuid.uuid4())
        c.execute('''INSERT INTO bookings (id, user_id, sauna_id, time_slot_id, seats_booked, 
                     total_price, status, customer_email, customer_name)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (booking_id, data.get('user_id', 'guest'), data['sauna_id'], 
                   data['time_slot_id'], data['seats_booked'], total_price, 
                   'confirmed', data['customer_email'], data['customer_name']))
        
        # Update available seats
        c.execute('UPDATE time_slots SET available_seats = available_seats - ? WHERE id = ?',
                  (data['seats_booked'], data['time_slot_id']))
        
        conn.commit()
        conn.close()
        
        return jsonify({'id': booking_id, 'total_price': total_price, 'status': 'confirmed'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/bookings')
def get_bookings():
    try:
        conn = get_db()
        c = conn.cursor()
        
        email = request.args.get('email')
        
        if email:
            c.execute('''SELECT b.*, s.name as sauna_name, ts.date, ts.start_time, ts.end_time
                        FROM bookings b
                        JOIN saunas s ON b.sauna_id = s.id
                        JOIN time_slots ts ON b.time_slot_id = ts.id
                        WHERE b.customer_email = ?
                        ORDER BY ts.date DESC, ts.start_time DESC''', (email,))
        else:
            c.execute('''SELECT b.*, s.name as sauna_name, ts.date, ts.start_time, ts.end_time
                        FROM bookings b
                        JOIN saunas s ON b.sauna_id = s.id
                        JOIN time_slots ts ON b.time_slot_id = ts.id
                        ORDER BY ts.date DESC, ts.start_time DESC''')
        
        bookings = [row_to_dict(row) for row in c.fetchall()]
        conn.close()
        return jsonify(bookings)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ CAIRDE ============

@bp.route('/cairde')
def get_cairde():
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT * FROM cairde ORDER BY name')
        cairde_list = [row_to_dict(row) for row in c.fetchall()]
        
        # Get sessions for each cairde member
        for person in cairde_list:
            c.execute('SELECT * FROM cairde_sessions WHERE cairde_id = ?', (person['id'],))
            person['sessions'] = [row_to_dict(row) for row in c.fetchall()]
        
        conn.close()
        return jsonify(cairde_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/cairde/<cairde_id>')
def get_cairde_member(cairde_id):
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT * FROM cairde WHERE id = ?', (cairde_id,))
        person = row_to_dict(c.fetchone())
        
        if not person:
            conn.close()
            return jsonify({'error': 'Cairde member not found'}), 404
        
        # Get sessions
        c.execute('SELECT * FROM cairde_sessions WHERE cairde_id = ?', (cairde_id,))
        person['sessions'] = [row_to_dict(row) for row in c.fetchall()]
        
        conn.close()
        return jsonify(person)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/cairde-sessions/<session_id>/time-slots')
def get_cairde_time_slots(session_id):
    try:
        conn = get_db()
        c = conn.cursor()
        
        date = request.args.get('date')
        query = 'SELECT * FROM cairde_time_slots WHERE session_id = ? AND is_active = 1'
        params = [session_id]
        
        if date:
            query += ' AND date = ?'
            params.append(date)
        
        query += ' ORDER BY date, start_time'
        c.execute(query, params)
        slots = [row_to_dict(row) for row in c.fetchall()]
        conn.close()
        return jsonify(slots)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/cairde-bookings', methods=['POST'])
def create_cairde_booking():
    try:
        data = request.json
        required = ['time_slot_id', 'session_id', 'seats_booked', 'customer_email', 'customer_name']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        conn = get_db()
        c = conn.cursor()
        
        # Check availability
        c.execute('SELECT available_seats FROM cairde_time_slots WHERE id = ?', (data['time_slot_id'],))
        slot = c.fetchone()
        
        if not slot or slot['available_seats'] < data['seats_booked']:
            conn.close()
            return jsonify({'error': 'Not enough seats available'}), 400
        
        # Get session price
        c.execute('SELECT price FROM cairde_sessions WHERE id = ?', (data['session_id'],))
        session = c.fetchone()
        total_price = float(session['price']) * data['seats_booked']
        
        # Create booking
        booking_id = str(uuid.uuid4())
        c.execute('''INSERT INTO cairde_bookings (id, user_id, session_id, time_slot_id, 
                     seats_booked, total_price, status, customer_email, customer_name)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (booking_id, data.get('user_id', 'guest'), data['session_id'],
                   data['time_slot_id'], data['seats_booked'], total_price,
                   'confirmed', data['customer_email'], data['customer_name']))
        
        # Update available seats
        c.execute('UPDATE cairde_time_slots SET available_seats = available_seats - ? WHERE id = ?',
                  (data['seats_booked'], data['time_slot_id']))
        
        conn.commit()
        conn.close()
        
        return jsonify({'id': booking_id, 'total_price': total_price, 'status': 'confirmed'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ LEARNING ============

@bp.route('/learning')
def get_learning():
    try:
        conn = get_db()
        c = conn.cursor()
        
        type_filter = request.args.get('type')
        category = request.args.get('category')
        
        query = 'SELECT * FROM learning_items WHERE 1=1'
        params = []
        
        if type_filter:
            query += ' AND type = ?'
            params.append(type_filter)
        
        if category:
            query += ' AND category = ?'
            params.append(category)
        
        query += ' ORDER BY type, title'
        c.execute(query, params)
        items = [row_to_dict(row) for row in c.fetchall()]
        conn.close()
        return jsonify(items)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/learning/<item_id>')
def get_learning_item(item_id):
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT * FROM learning_items WHERE id = ?', (item_id,))
        item = row_to_dict(c.fetchone())
        
        if not item:
            conn.close()
            return jsonify({'error': 'Learning item not found'}), 404
        
        conn.close()
        return jsonify(item)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/learning/<item_id>/time-slots')
def get_learning_time_slots(item_id):
    try:
        conn = get_db()
        c = conn.cursor()
        date = request.args.get('date')
        
        query = 'SELECT * FROM learning_time_slots WHERE learning_item_id = ? AND is_active = 1'
        params = [item_id]
        
        if date:
            query += ' AND date = ?'
            params.append(date)
        
        query += ' ORDER BY date, start_time'
        c.execute(query, params)
        slots = [row_to_dict(row) for row in c.fetchall()]
        conn.close()
        return jsonify(slots)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/learning-bookings', methods=['POST'])
def create_learning_booking():
    try:
        data = request.json
        required = ['time_slot_id', 'learning_item_id', 'seats_booked', 'customer_email', 'customer_name']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        conn = get_db()
        c = conn.cursor()
        
        # Check availability
        c.execute('SELECT available_seats FROM learning_time_slots WHERE id = ?', (data['time_slot_id'],))
        slot = c.fetchone()
        
        if not slot or slot['available_seats'] < data['seats_booked']:
            conn.close()
            return jsonify({'error': 'Not enough seats available'}), 400
        
        # Get item price
        c.execute('SELECT price FROM learning_items WHERE id = ?', (data['learning_item_id'],))
        item = c.fetchone()
        total_price = float(item['price']) * data['seats_booked']
        
        # Create booking
        booking_id = str(uuid.uuid4())
        c.execute('''INSERT INTO learning_bookings (id, user_id, learning_item_id, time_slot_id,
                     seats_booked, total_price, status, customer_email, customer_name)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (booking_id, data.get('user_id', 'guest'), data['learning_item_id'],
                   data['time_slot_id'], data['seats_booked'], total_price,
                   'confirmed', data['customer_email'], data['customer_name']))
        
        # Update available seats
        c.execute('UPDATE learning_time_slots SET available_seats = available_seats - ? WHERE id = ?',
                  (data['seats_booked'], data['time_slot_id']))
        
        conn.commit()
        conn.close()
        
        return jsonify({'id': booking_id, 'total_price': total_price, 'status': 'confirmed'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ MEMBERSHIPS ============

@bp.route('/memberships')
def get_memberships():
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT * FROM memberships WHERE is_active = 1 ORDER BY monthly_price')
        memberships = [row_to_dict(row) for row in c.fetchall()]
        conn.close()
        return jsonify(memberships)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
