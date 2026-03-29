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

.nav a[href*="shoulder"] {
    color: var(--page-title);
}

/* Shoulder Specific Layout */
.shoulder-container {
    flex: 1;
    display: flex;
    position: relative;
    padding: 0 60px 60px;
    align-items: flex-start;
    overflow: hidden;
}

.main-image {
    flex: 1;
    display: flex;
    align-items: flex-start;
    justify-content: flex-start;
    padding-top: 0;
    padding-left: 10%;
}

.main-image img {
    max-width: 52%;
    height: auto;
    object-fit: contain;
}

/* Horizontal Scroll Box */
.scroll-box {
    position: absolute;
    top: 60px;
    right: 13px;
    width: 320px;
    height: 400px;
    border: none;
    background: transparent;
    overflow-x: scroll;
    overflow-y: hidden;
    padding: 0;
    white-space: nowrap;
    cursor: grab;
    user-select: none;
}

.scroll-content {
    display: inline-flex;
    height: 100%;
}

.scroll-panel {
    display: inline-block;
    width: 320px;
    height: 100%;
    padding: 32px;
    white-space: normal;
    flex-shrink: 0;
}

.scroll-panel h2 {
    font-size: 11pt;
    font-weight: 400;
    margin-bottom: 0;
    color: var(--text-muted);
    line-height: 9pt;
    text-align: justify;
    text-align-last: left;
}

.scroll-panel p {
    font-size: 11pt;
    line-height: 9pt;
    color: var(--text-muted);
    margin-bottom: 12px;
    text-align: justify;
    text-align-last: left;
}

/* Hide scrollbar but keep functionality */
.scroll-box::-webkit-scrollbar {
    width: 0;
    height: 0;
}

.scroll-box {
    scrollbar-width: none;
    -ms-overflow-style: none;
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

.main-image img {
    cursor: pointer;
}

/* Mobile */
@media (max-width: 768px) {
    body {
        overflow-y: auto;
        position: relative;
    }

    .header {
        padding: 24px;
        flex-direction: column;
        gap: 20px;
        align-items: flex-start;
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

    .shoulder-container {
        flex-direction: column;
        padding: 24px;
        overflow-y: auto;
    }

    .main-image {
        position: relative;
        margin-bottom: 24px;
        padding: 0;
        width: 100%;
    }

    .main-image img {
        max-width: 100%;
        max-height: 400px;
    }

    .scroll-box {
        position: relative;
        top: 0;
        right: 0;
        width: 100%;
        height: auto;
        overflow-x: auto;
        overflow-y: visible;
        margin-bottom: 24px;
    }

    .scroll-content {
        display: block;
    }

    .scroll-panel {
        width: 100%;
        white-space: normal;
        padding: 24px 0;
        border-bottom: 1px solid var(--border);
    }

    .scroll-panel:last-child {
        border-bottom: none;
    }

    .contact-details {
        position: relative;
        top: auto;
        right: auto;
        transform: none;
        margin: 24px;
        font-size: 13pt;
        display: block;
        pointer-events: all;
    }
}
</style>

<html>
<div class="custom-cursor" id="customCursor"></div>

<header class="header">
    <a href="../home/" class="logo">Erlabrunn</a>
    <nav class="nav">
        <a href="../lastplace/">Last Place</a>
        <a href="../shoulder/">Shoulder</a>
        <a href="../artists/">Artists</a>
    </nav>
</header>

<main class="shoulder-container">
    <div class="main-image">
        <img src="../assets/images/Shoulder_Landing_v1.jpg" alt="Shoulder Residency" onclick="toggleContact(event)">
    </div>

    <div class="contact-details" id="contactDetails">
        <div class="contact-label">Contact</div>
        <div><a href="mailto:cliveburgess0@gmail.com">cliveburgess0@gmail.com</a></div>
        <div><a href="https://instagram.com/erlabrunn.imprint" target="_blank">@erlabrunn.imprint</a></div>
    </div>

    <div class="scroll-box">
        <div class="scroll-content">
            <div class="scroll-panel">
                <p>Shoulder began with, learns from, lives in, explores, and hopefully honors the small, remote, green valley of Bransdale. It has been our pleasure to have been able to share the valley with artists (and friends) over the course of the residency, and for the many years preceding it.</p>
            </div>
            <div class="scroll-panel">
                <p><em>"Here dry stone walls enclose pastures, creeping up the hillsides to meet the moor. Treacherous drops and coniferous woodlands bridge many of the gaps between. These woodlands, planted to be harvested decades ago, have grown into imposing wind shields and compost heaps of pine needles."</em></p>
                <p style="text-align: right;">- NB, 2025</p>
            </div>
            <div class="scroll-panel">
                <p>We look forward to returning to the valley in July 2026 with a new group of emerging artists.</p>
            </div>
            <div class="scroll-panel">
                <p>In June 2025 we ran the inaugural residency in Bransdale. With thanks to the people and the valley that supported us.</p>
                <p>Artists in Residence<br>
Sasha Lee, Rufus Finn, Kit Lovelock, Iris Allen</p>
                <p>Studio Team<br>
Ed Burgess, Raph Haque, Beau Beames, Alya Lothore</p>
            </div>
        </div>
    </div>
</main>

<script>
// Enable horizontal scroll with mouse wheel from anywhere on page
document.addEventListener('DOMContentLoaded', function() {
    const scrollBox = document.querySelector('.scroll-box');
    if (scrollBox) {
        // Global wheel event - scroll text box from anywhere on page
        document.addEventListener('wheel', (e) => {
            e.preventDefault();
            scrollBox.scrollLeft += e.deltaY;
        }, { passive: false });

        // Touch support for mobile
        let isDown = false;
        let startX;
        let scrollLeft;

        scrollBox.addEventListener('mousedown', (e) => {
            isDown = true;
            scrollBox.style.cursor = 'grabbing';
            startX = e.pageX - scrollBox.offsetLeft;
            scrollLeft = scrollBox.scrollLeft;
        });

        scrollBox.addEventListener('mouseleave', () => {
            isDown = false;
            scrollBox.style.cursor = 'grab';
        });

        scrollBox.addEventListener('mouseup', () => {
            isDown = false;
            scrollBox.style.cursor = 'grab';
        });

        scrollBox.addEventListener('mousemove', (e) => {
            if (!isDown) return;
            e.preventDefault();
            const x = e.pageX - scrollBox.offsetLeft;
            const walk = (x - startX) * 2;
            scrollBox.scrollLeft = scrollLeft - walk;
        });
    }
});

// Custom cursor
const cursor = document.getElementById('customCursor');
document.addEventListener('mousemove', (e) => {
    cursor.style.left = e.clientX + 'px';
    cursor.style.top = e.clientY + 'px';
});

// Change cursor color on hover over clickable elements
const clickableElements = document.querySelectorAll('a, .main-image img');
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

    // Position to the left and above cursor
    contactDetails.style.left = (mouseX - 200) + 'px';
    contactDetails.style.top = (mouseY - 80) + 'px';
    contactDetails.style.bottom = 'auto';
    contactDetails.style.right = 'auto';

    contactDetails.classList.add('visible');
}

// Hide contact details when clicking on non-clickable area
document.addEventListener('click', (e) => {
    const contactDetails = document.getElementById('contactDetails');
    const mainImage = document.querySelector('.main-image img');

    // Check if click is NOT on the main image
    if (!mainImage || !mainImage.contains(e.target)) {
        contactDetails.classList.remove('visible');
    }
});
</script>
</html>