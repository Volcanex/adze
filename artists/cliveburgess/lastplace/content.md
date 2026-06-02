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

/* Botanical Drawings Background */
.botanical-container {
     position: fixed;
     top: 0;
     left: 0;
     width: 100%;
     height: 100%;
     pointer-events: none;
     z-index: 1;
     overflow: hidden;
}

.botanical-drawing {
     position: fixed;
     opacity: 0;
     pointer-events: none;
     z-index: 1;
     object-fit: contain;
     animation: fadeIn 8s ease-in-out forwards;
}

@keyframes fadeIn {
     from {
         opacity: 0;
     }
     to {
         opacity: 0.2;
     }
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
    overflow-y: auto;
    position: relative;
    cursor: none;
}

/* Custom Cursor */
.custom-cursor {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--primary);
    position: fixed;
    pointer-events: none;
    z-index: 9999;
    transform: translate(-50%, -50%);
    transition: background-color 1.2s ease, border-radius 3.5s ease;
}

.custom-cursor.clickable {
    background: var(--page-title);
    border-radius: 0;
}

a {
    color: var(--primary);
    text-decoration: none;
    transition: opacity 0.2s ease;
    cursor: none;
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
    color: var(--primary);
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

.nav a[href*="lastplace"] {
    color: var(--page-title);
}

.nav a[href*="shoulder"] {
    color: var(--primary);
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
    pointer-events: none; /* Prevent text from being interactive */
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
        flex-wrap: wrap;
    }

    .nav a {
        min-height: 44px;
        display: flex;
        align-items: center;
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
        padding: 0;
    }

    .click-zone {
        display: none;
    }

    .clock-container {
        position: relative;
        top: auto;
        right: auto;
        margin: 24px;
        flex-wrap: wrap;
        gap: 20px;
        opacity: 1;
    }

    .clock-display {
        font-size: 16px;
    }
}
</style>

<html>
<div class="botanical-container" id="botanicalContainer"></div>

<div class="custom-cursor" id="customCursor"></div>

<header class="header">
    <a href="../home/" class="logo">Erlabrunn</a>
    <nav class="nav">
        <a href="../shoulder/">Shoulder</a>
        <a href="../lastplace/" class="active">Last Place</a>
        <a href="../artists/">Artists</a>
    </nav>
</header>

<main>
    <div class="contact-details" id="contactDetails">
        <div class="contact-label">Contact</div>
        <div><a href="mailto:cliveburgess0@gmail.com">cliveburgess0@gmail.com</a></div>
        <div><a href="https://instagram.com/erlabrunn.imprint" target="_blank">@erlabrunn.imprint</a></div>
    </div>

    <div class="about-text">
        <p>Last place is a web design and build service. Unlike a design and build service for your home, we will not let your roof cave in, we will not ignore your specific requests and we will never sell you a copy-paste design. There will eventually be a Wozniak vs Jobs moment, but as of now both Steves are getting on well.</p>
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
// Pool of botanical drawings
const botanicalPool = [
     '../assets/images/2026_04_22_Roots_Cleaned.png',
     '../assets/images/Artboard_24x.png',
     '../assets/images/Artboard_2_copy4x.png',
     '../assets/images/1744325358775.jpg',
     '../assets/images/Roots_2.jpg',
     '../assets/images/Roots_2_-_Copy.jpg',
     '../assets/images/betonica-altilis-coloring-page-lg.png',
     '../assets/images/hieracium-minus-coloring-page-original.png',
     '../assets/images/images10.jpg',
     '../assets/images/images20.jpg',
     '../assets/images/images8.jpg',
     '../assets/images/images7.jpg',
     '../assets/images/images30.jpg',
     '../assets/images/Root_Sectionv2.jpeg'
];

// Function to shuffle and select 3 random images
function getRandomBotanicals(count = 3) {
     const shuffled = [...botanicalPool].sort(() => Math.random() - 0.5);
     return shuffled.slice(0, count);
}

// Function to add a botanical drawing with random positioning and sizing
function addBotanicalDrawing(imageSrc, delay) {
     setTimeout(() => {
         const container = document.getElementById('botanicalContainer');
         const img = document.createElement('img');
         img.src = imageSrc;
         img.className = 'botanical-drawing';
         
         // Random size between 20% and 80% of window width
         const minWidth = window.innerWidth * 0.2;
         const maxWidth = window.innerWidth * 0.8;
         const randomWidth = minWidth + Math.random() * (maxWidth - minWidth);
         
         // Random horizontal position (center the image on this position)
         const randomLeft = Math.random() * (window.innerWidth - randomWidth);
         
         // Random vertical position
         const randomTop = Math.random() * (window.innerHeight - randomWidth);
         
         img.style.width = randomWidth + 'px';
         img.style.height = 'auto';
         img.style.left = randomLeft + 'px';
         img.style.top = randomTop + 'px';
         
         container.appendChild(img);
     }, delay);
}

// Initialize botanical drawings on page load
function initBotanicalDrawings() {
     const selectedImages = getRandomBotanicals(3);
     
     // Add first image at 0ms (starts immediately)
     addBotanicalDrawing(selectedImages[0], 0);
     
     // Add second image at 3000ms (3 seconds later)
     addBotanicalDrawing(selectedImages[1], 3000);
     
     // Add third image at 6000ms (6 seconds after start)
     addBotanicalDrawing(selectedImages[2], 6000);
     
     // Show contact info at 9000ms (9 seconds total: 6s for last image + 3s for it to be visible)
     setTimeout(() => {
         const contactDetails = document.getElementById('contactDetails');
         contactDetails.classList.add('visible');
     }, 9000);
}

// Update positions on window resize
window.addEventListener('resize', () => {
     const drawings = document.querySelectorAll('.botanical-drawing');
     drawings.forEach(img => {
         // Recalculate positioning on resize
         const currentWidth = parseFloat(img.style.width);
         const currentLeft = parseFloat(img.style.left);
         
         // Push across screen proportionally on window resize
         const widthRatio = window.innerWidth / parseFloat(img.dataset.originalWindowWidth || window.innerWidth);
         img.style.left = (currentLeft * widthRatio) + 'px';
     });
});

// Run when DOM is ready
document.addEventListener('DOMContentLoaded', initBotanicalDrawings);

// Fallback if DOM is already loaded
if (document.readyState === 'loading') {
     document.addEventListener('DOMContentLoaded', initBotanicalDrawings);
} else {
     initBotanicalDrawings();
}

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

// Custom cursor
const cursor = document.getElementById('customCursor');
document.addEventListener('mousemove', (e) => {
    cursor.style.left = e.clientX + 'px';
    cursor.style.top = e.clientY + 'px';
});

// Change cursor color on hover over clickable elements
const clickableElements = document.querySelectorAll('a, .click-zone');

// Make clock displays non-interactive
const clockDisplays = document.querySelectorAll('.clock-display');
clockDisplays.forEach(display => {
    display.style.pointerEvents = 'none';
});
clickableElements.forEach(el => {
    el.addEventListener('mouseenter', () => {
        cursor.classList.add('clickable');
    });
    el.addEventListener('mouseleave', () => {
        cursor.classList.remove('clickable');
    });
});

function toggleContact(event) {
    event.stopPropagation(); // Prevent body click from immediately hiding
    const contactDetails = document.getElementById('contactDetails');

    // Get mouse position
    const mouseX = event.clientX;
    const mouseY = event.clientY;

    // Position to the left and above cursor with no overlap
    contactDetails.style.left = (mouseX - 200) + 'px'; // Well to the left
    contactDetails.style.top = (mouseY - 80) + 'px';  // Well above
    contactDetails.style.bottom = 'auto';
    contactDetails.style.right = 'auto';

    contactDetails.classList.add('visible');
}

// Hide contact details when clicking on non-clickable area
document.addEventListener('click', (e) => {
    const contactDetails = document.getElementById('contactDetails');
    const clickZone = document.querySelector('.click-zone');

    // Check if click is NOT on the click zone
    if (!clickZone.contains(e.target)) {
        contactDetails.classList.remove('visible');
    }
});
</script>
</html>