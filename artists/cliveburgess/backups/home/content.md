<style>
@font-face {
    font-family: 'Cormorant';
    src: url('../assets/fonts/Cormorant[wght].ttf') format('truetype');
    font-weight: 300 700;
    font-style: normal;
    font-display: swap;
}

@font-face {
    font-family: 'Cormorant';
    src: url('../assets/fonts/Cormorant-Italic[wght].ttf') format('truetype');
    font-weight: 300 700;
    font-style: italic;
    font-display: swap;
}

:root {
    --primary: #280300;
    --bg: #ffffff;
    --border: #e0e0e0;
    --text-muted: #280300;
    --page-title: #0000ff;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html {
    overflow: hidden;
    height: 100%;
}

body {
    font-family: 'Cormorant', Georgia, serif;
    color: var(--primary);
    background: var(--bg);
    line-height: 1.6;
    font-size: 16px;
    font-weight: 400;
    height: 100%;
    width: 100%;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    position: fixed;
    top: 0;
    left: 0;
}

a {
    color: var(--primary);
    text-decoration: none;
    transition: opacity 0.2s ease;
}
a:hover { opacity: 0.6; }

/* Header */
.header {
    padding: 60px 60px 20px;
    border-bottom: none;
    background: transparent;
    display: flex;
    justify-content: flex-start;
    align-items: flex-end;
    gap: 53px;
    position: relative;
    z-index: 10;
}

.logo {
    font-size: 18px;
    font-weight: 400;
    letter-spacing: 0.5px;
    color: var(--page-title);
}

.nav {
    display: flex;
    gap: 25px;
}

.nav a {
    font-size: 18px;
    font-weight: 400;
    color: var(--primary);
}

.nav a[href*="shoulder"] {
    color: var(--primary);
}

/* Baby Image */
.baby-image-container {
    position: absolute;
    top: 50%;
    right: 250px;
    transform: translateY(-50%);
    cursor: pointer;
    z-index: 5;
}

.baby-image {
    width: 300px;
    height: auto;
    object-fit: cover;
    display: block;
}

/* Contact Details */
.contact-details {
    position: fixed;
    font-size: 11pt;
    line-height: 9pt;
    color: var(--primary);
    display: none;
    pointer-events: none;
    z-index: 100;
}

.contact-details.visible {
    display: block;
}

.contact-details .contact-label {
    margin-bottom: 8px;
}

.contact-details a {
    color: var(--primary);
    text-decoration: none;
    pointer-events: all;
}

.contact-details a:hover {
    opacity: 0.6;
}

/* Click Zone */
.click-zone {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 50%;
    cursor: pointer;
    z-index: 2;
}

/* About Text */
.about-text {
    position: absolute;
    top: 50%;
    right: 570px;
    transform: translateY(-50%);
    max-width: 400px;
    font-size: 11pt;
    line-height: 9pt;
    color: var(--primary);
    text-align: justify;
    text-align-last: left;
}

.about-text p {
    margin: 0;
}

/* Clock containers */
.clock-container {
    position: fixed;
    top: 80px;
    right: 250px;
    display: flex;
    align-items: flex-end;
    gap: 40px;
    padding: 0 0 20px;
    z-index: 100;
    pointer-events: none;
    opacity: 0.7;
}

.clock-display {
    font-size: 18px;
    font-weight: 400;
    color: var(--primary);
    font-family: 'Cormorant', Georgia, serif;
    transform: scaleX(0.9);
    letter-spacing: -0.5px;
    transform-origin: left center;
}

/* Mobile */
@media (max-width: 768px) {
    body {
        overflow-y: auto;
        position: relative;
    }

    .header {
        padding: 24px;
        gap: 20px;
        align-items: flex-start;
        flex-wrap: wrap;
    }

    .nav {
        gap: 20px;
    }

    .baby-image-container {
        position: relative;
        top: auto;
        right: auto;
        transform: none;
        margin: 24px;
        width: calc(100% - 48px);
        text-align: center;
    }

    .baby-image {
        width: 100%;
        max-width: 300px;
    }

    .contact-details {
        position: relative;
        top: auto;
        right: auto;
        transform: none;
        margin: 24px;
        font-size: 13pt;
    }

    .about-text {
        position: relative;
        top: auto;
        right: auto;
        transform: none;
        margin: 24px;
        max-width: 100%;
        font-size: 11pt;
    }
}
</style>

<html>
<header class="header">
    <a href="../home/" class="logo">Erlabrunn</a>
    <nav class="nav">
        <a href="../lastplace/">Last Place</a>
        <a href="../shoulder/">Shoulder</a>
        <a href="../artists/">Artists</a>
    </nav>
</header>

<main>
    <div class="baby-image-container" onclick="toggleContact(event)">
        <img src="../assets/2026_02_Baby_photo_only.jpg" alt="Erlabrunn" class="baby-image">
    </div>

    <div class="contact-details" id="contactDetails">
        <div class="contact-label">Contact</div>
        <div><a href="mailto:cliveburgess0@gmail.com">cliveburgess0@gmail.com</a></div>
        <div><a href="https://instagram.com/erlabrunn.imprint" target="_blank">@erlabrunn.imprint</a></div>
    </div>

    <div class="about-text">
        <p>Erlabrunn is a young publishing imprint based in London, run by Nell Burgess and Clive Burgess (pictured), focussing on exhibition books, illustration, platforming emerging writers and working with alternative and traditional materials and handbinding techniques.</p>
    </div>

    <div class="click-zone" onclick="toggleContact(event)"></div>

    <div class="clock-container">
        <div class="clock-display" id="hours"></div>
        <div class="clock-display" id="updateText">Updated March 2026 © Erlabrunn</div>
        <div class="clock-display" id="minutes"></div>
    </div>
</main>

<script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.7.0/p5.min.js"></script>
<script>
function setup() {
    noCanvas();
}

function draw() {
    let h = hour();
    let m = minute();

    // Format with leading zeros
    let hoursDisplay = nf(h, 2);
    let minutesDisplay = nf(m, 2);

    // Update DOM elements
    document.getElementById('hours').textContent = hoursDisplay;
    document.getElementById('minutes').textContent = minutesDisplay;

    // Calculate time since March 2026
    let now = new Date();
    let updateDate = new Date(2026, 2, 1); // March 1, 2026 (month is 0-indexed)
    let diffMs = now - updateDate;

    let diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    let diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    let diffMonths = Math.floor(diffMs / (1000 * 60 * 60 * 24 * 30.44));

    let timeText;
    if (diffHours < 1) {
        timeText = "updated less than an hour ago";
    } else if (diffHours === 1) {
        timeText = "updated an hour ago";
    } else if (diffHours < 24) {
        timeText = "updated " + diffHours + " hours ago";
    } else if (diffDays === 1) {
        timeText = "updated a day ago";
    } else if (diffDays < 30) {
        timeText = "updated " + diffDays + " days ago";
    } else if (diffMonths === 1) {
        timeText = "updated a month ago";
    } else if (diffMonths < 12) {
        timeText = "updated " + diffMonths + " months ago";
    } else {
        let years = Math.floor(diffMonths / 12);
        let remainingMonths = diffMonths % 12;
        if (years === 1 && remainingMonths === 0) {
            timeText = "updated a year ago";
        } else if (years === 1) {
            timeText = "updated a year and " + remainingMonths + " months ago";
        } else if (remainingMonths === 0) {
            timeText = "updated " + years + " years ago";
        } else {
            timeText = "updated " + years + " years and " + remainingMonths + " months ago";
        }
    }

    document.getElementById('updateText').textContent = timeText + " © Erlabrunn";
}

function toggleContact(event) {
    const contactDetails = document.getElementById('contactDetails');

    if (contactDetails.classList.contains('visible')) {
        contactDetails.classList.remove('visible');
    } else {
        // Get mouse position
        const mouseX = event.clientX;
        const mouseY = event.clientY;

        // Position to the left and above cursor with no overlap
        // Offset by estimated width/height of contact box to ensure visibility
        contactDetails.style.left = (mouseX - 200) + 'px'; // Well to the left
        contactDetails.style.top = (mouseY - 80) + 'px';  // Well above
        contactDetails.style.bottom = 'auto';
        contactDetails.style.right = 'auto';

        contactDetails.classList.add('visible');
    }
}
</script>
</html>