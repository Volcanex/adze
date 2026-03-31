<style>
body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: #f5f2ed;
    color: #2a2a28;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    margin: 0;
    padding: 20px;
}
.container {
    max-width: 500px;
    width: 100%;
    background: white;
    padding: 40px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
h1 {
    font-size: 32px;
    font-weight: 300;
    margin-bottom: 8px;
    color: #2a2a28;
}
.subtitle {
    color: #6b6860;
    font-size: 14px;
    margin-bottom: 32px;
}
.form-group {
    margin-bottom: 20px;
}
label {
    display: block;
    font-size: 13px;
    font-weight: 500;
    margin-bottom: 6px;
    color: #2a2a28;
}
input, textarea {
    width: 100%;
    padding: 12px;
    border: 1px solid #d9d4cd;
    border-radius: 6px;
    font-family: inherit;
    font-size: 14px;
    box-sizing: border-box;
    transition: border-color 0.2s;
}
input:focus, textarea:focus {
    outline: none;
    border-color: #2a2a28;
}
textarea {
    resize: vertical;
    min-height: 100px;
}
button {
    width: 100%;
    padding: 14px;
    background: #2a2a28;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.2s;
}
button:hover {
    background: #1a1a18;
}
button:disabled {
    background: #d9d4cd;
    cursor: not-allowed;
}
.message {
    padding: 12px;
    border-radius: 6px;
    margin-bottom: 20px;
    font-size: 14px;
}
.message.success {
    background: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
}
.message.error {
    background: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
}
.hidden {
    display: none;
}
</style>

<html>
<div class="container">
    <h1>Book a Session</h1>
    <p class="subtitle">Fill out the form below to request a booking</p>

    <div id="message" class="hidden"></div>

    <form id="bookingForm">
        <div class="form-group">
            <label for="name">Name *</label>
            <input type="text" id="name" name="name" required>
        </div>

        <div class="form-group">
            <label for="email">Email *</label>
            <input type="email" id="email" name="email" required>
        </div>

        <div class="form-group">
            <label for="date">Preferred Date *</label>
            <input type="date" id="date" name="date" required>
        </div>

        <div class="form-group">
            <label for="time">Preferred Time *</label>
            <input type="time" id="time" name="time" required>
        </div>

        <div class="form-group">
            <label for="notes">Additional Notes</label>
            <textarea id="notes" name="notes" placeholder="Tell me about your project or session..."></textarea>
        </div>

        <button type="submit" id="submitBtn">Submit Booking Request</button>
    </form>
</div>

<script>
const form = document.getElementById('bookingForm');
const submitBtn = document.getElementById('submitBtn');
const messageDiv = document.getElementById('message');

form.addEventListener('submit', async (e) => {
    e.preventDefault();

    submitBtn.disabled = true;
    submitBtn.textContent = 'Submitting...';
    messageDiv.className = 'hidden';

    const formData = {
        name: document.getElementById('name').value,
        email: document.getElementById('email').value,
        date: document.getElementById('date').value,
        time: document.getElementById('time').value,
        notes: document.getElementById('notes').value
    };

    try {
        const response = await fetch('/api/artists/sandbox/book', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (response.ok) {
            messageDiv.className = 'message success';
            messageDiv.textContent = 'Booking request submitted successfully! I\'ll be in touch soon.';
            form.reset();
        } else {
            messageDiv.className = 'message error';
            messageDiv.textContent = data.error || 'Something went wrong. Please try again.';
        }
    } catch (error) {
        messageDiv.className = 'message error';
        messageDiv.textContent = 'Network error. Please check your connection and try again.';
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Submit Booking Request';
        messageDiv.classList.remove('hidden');
    }
});
</script>
</html>
