<meta property="og:title" content="Book Sauna Session - Wild Saunas Ireland">
<meta property="og:description" content="Book your wild sauna session">

<style>
.header { padding: 6rem 1.5rem 2rem; text-align: center; background: var(--bg); }
.section { padding: 2rem 1.5rem; max-width: 800px; margin: 0 auto; }
.form-group { margin-bottom: 1.5rem; }
.form-label { display: block; margin-bottom: 0.5rem; font-weight: 600; }
.form-input, .form-select { width: 100%; padding: 0.75rem; border: 2px solid var(--border); border-radius: 8px; font-size: 1rem; font-family: var(--text-font); }
.form-input:focus, .form-select:focus { outline: none; border-color: var(--accent); }
.grid-2 { display: grid; gap: 1rem; grid-template-columns: 1fr 1fr; }
.success-msg { background: #d4edda; border: 2px solid #c3e6cb; color: #155724; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; }
.error-msg { background: #f8d7da; border: 2px solid #f5c6cb; color: #721c24; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; }
</style>

<html>
<div class="header">
    <h1>Book Sauna Session</h1>
    <p style="color: var(--muted-foreground);">Choose your sauna, date, and reserve your seats</p>
</div>

<section class="section">
    <div id="message"></div>

    <form id="booking-form">
        <div class="form-group">
            <label class="form-label">Select Sauna</label>
            <select class="form-select" id="sauna-select" required>
                <option value="">Loading saunas...</option>
            </select>
        </div>

        <div class="form-group">
            <label class="form-label">Select Date</label>
            <input type="date" class="form-input" id="date-select" required>
        </div>

        <div class="form-group">
            <label class="form-label">Select Time Slot</label>
            <select class="form-select" id="slot-select" required disabled>
                <option value="">Choose a date first</option>
            </select>
        </div>

        <div class="form-group">
            <label class="form-label">Number of Seats</label>
            <input type="number" class="form-input" id="seats-input" min="1" max="8" value="1" required>
        </div>

        <div class="grid-2">
            <div class="form-group">
                <label class="form-label">Your Name</label>
                <input type="text" class="form-input" id="name-input" required>
            </div>
            <div class="form-group">
                <label class="form-label">Your Email</label>
                <input type="email" class="form-input" id="email-input" required>
            </div>
        </div>

        <div style="margin-top: 2rem; padding-top: 2rem; border-top: 2px solid var(--border);">
            <div style="display: flex; justify-content: space-between; margin-bottom: 1.5rem;">
                <span style="font-size: 1.125rem;">Total Price:</span>
                <span id="total-price" style="font-size: 1.5rem; font-weight: 700; color: var(--primary);">€0</span>
            </div>
            <button type="submit" class="btn" style="width: 100%; font-size: 1.125rem; padding: 1rem;" id="submit-btn">Complete Booking</button>
        </div>
    </form>
</section>

<script>
const API = '/api/artists/chris';
let saunas = [];
let timeSlots = [];
let selectedSauna = null;

async function loadSaunas() {
    const res = await fetch(API + '/saunas');
    saunas = await res.json();
    const select = document.getElementById('sauna-select');
    select.innerHTML = '<option value="">Select a sauna...</option>' + saunas.map(s =>
        `<option value="${s.id}">${s.name} - ${s.location_id} (€${s.price_per_seat}/seat, ${s.capacity} seats)</option>`
    ).join('');
}

async function loadTimeSlots() {
    const saunaId = document.getElementById('sauna-select').value;
    const date = document.getElementById('date-select').value;
    if (!saunaId || !date) return;

    selectedSauna = saunas.find(s => s.id === saunaId);
    const res = await fetch(API + `/time-slots?sauna_id=${saunaId}&date=${date}`);
    timeSlots = await res.json();

    const select = document.getElementById('slot-select');
    select.disabled = false;
    if (timeSlots.length === 0) {
        select.innerHTML = '<option value="">No slots available</option>';
    } else {
        select.innerHTML = '<option value="">Select a time...</option>' + timeSlots.map(t =>
            `<option value="${t.id}">${t.start_time} - ${t.end_time} (${t.available_seats} seats available)</option>`
        ).join('');
    }
}

function updatePrice() {
    const seats = parseInt(document.getElementById('seats-input').value) || 0;
    if (selectedSauna) {
        const total = seats * parseFloat(selectedSauna.price_per_seat);
        document.getElementById('total-price').textContent = '€' + total.toFixed(2);
    }
}

document.getElementById('sauna-select').addEventListener('change', loadTimeSlots);
document.getElementById('date-select').addEventListener('change', loadTimeSlots);
document.getElementById('seats-input').addEventListener('input', updatePrice);

document.getElementById('booking-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = document.getElementById('submit-btn');
    btn.disabled = true;
    btn.textContent = 'Processing...';

    try {
        const res = await fetch(API + '/bookings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                sauna_id: document.getElementById('sauna-select').value,
                time_slot_id: document.getElementById('slot-select').value,
                seats_booked: parseInt(document.getElementById('seats-input').value),
                customer_name: document.getElementById('name-input').value,
                customer_email: document.getElementById('email-input').value
            })
        });

        const data = await res.json();
        if (res.ok) {
            document.getElementById('message').innerHTML = `<div class="success-msg"><strong>Booking Confirmed!</strong><br>Booking ID: ${data.id}<br>Total: €${data.total_price}<br>A confirmation email has been sent to ${document.getElementById('email-input').value}</div>`;
            document.getElementById('booking-form').reset();
            loadTimeSlots();
        } else {
            throw new Error(data.error || 'Booking failed');
        }
    } catch (err) {
        document.getElementById('message').innerHTML = `<div class="error-msg"><strong>Error:</strong> ${err.message}</div>`;
    } finally {
        btn.disabled = false;
        btn.textContent = 'Complete Booking';
    }
});

// Initialize
window.addEventListener('DOMContentLoaded', () => {
    loadSaunas();
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('date-select').min = today;
});
</script>
</html>
