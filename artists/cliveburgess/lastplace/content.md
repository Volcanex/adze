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

.nav a[href*="lastplace"] {
    color: var(--page-title);
}

.nav a[href*="shoulder"] {
    color: var(--primary);
}

/* Background Images */
.background-images {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 1;
}

.root-image {
    position: absolute;
    opacity: 0;
    transition: opacity 1s ease;
    mix-blend-mode: multiply;
    pointer-events: auto;
    cursor: none;
}

.root-image.visible {
    opacity: 0.4;
}

/* Page Content */
.page-content {
    flex: 1;
    padding: 40px 60px 80px;
    position: relative;
    z-index: 5;
    display: flex;
    align-items: flex-start;
    gap: 60px;
}

.text-box {
    max-width: 320px;
    font-size: 11pt;
    line-height: 9pt;
    color: var(--primary);
    text-align: justify;
    text-align-last: left;
    cursor: none;
    position: relative;
    z-index: 10;
}

.text-box p {
    margin: 0;
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

    .page-content {
        padding: 24px;
        flex-direction: column;
    }

    .text-box {
        max-width: 100%;
        margin-bottom: 24px;
    }
}
</style>

<html>
<div class="custom-cursor" id="customCursor"></div>
<div class="background-images" id="backgroundImages"></div>

<header class="header">
    <a href="../home/" class="logo">Erlabrunn</a>
    <nav class="nav">
        <a href="../lastplace/">Last Place</a>
        <a href="../shoulder/">Shoulder</a>
        <a href="../artists/">Artists</a>
    </nav>
</header>

<main class="page-content">
    <div class="text-box" onclick="showContact(event)">
        <p>Last Place is a web design and build service. Unlike a design and build service for your home extension, we will not let your roof cave in, we will not ignore your specific requests and we will never sell you a copy-paste design. There will eventually be a Wozniak vs Jobs moment, but as of now both Steve's are getting on well.</p>
    </div>

    <div class="contact-details" id="contactDetails">
        <div class="contact-label">Contact</div>
        <div><a href="mailto:cliveburgess0@gmail.com">cliveburgess0@gmail.com</a></div>
        <div><a href="https://instagram.com/erlabrunn.imprint" target="_blank">@erlabrunn.imprint</a></div>
    </div>
</main>

<script>
// Custom cursor
const cursor = document.getElementById('customCursor');
document.addEventListener('mousemove', (e) => {
    cursor.style.left = e.clientX + 'px';
    cursor.style.top = e.clientY + 'px';
});

// Change cursor color on hover over clickable elements
function updateClickableElements() {
    const clickableElements = document.querySelectorAll('a, .root-image, .text-box');
    clickableElements.forEach(el => {
        el.addEventListener('mouseenter', () => {
            cursor.classList.add('clickable');
        });
        el.addEventListener('mouseleave', () => {
            cursor.classList.remove('clickable');
        });
    });
}

// Initial update
updateClickableElements();

// Update after images are added
setTimeout(() => {
    updateClickableElements();
}, 10000); // After all images have loaded

function showContact(event) {
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
    const images = document.querySelectorAll('.root-image');
    const textBox = document.querySelector('.text-box');

    // Check if click is NOT on any image or text box
    let clickedOnClickable = false;
    images.forEach(img => {
        if (img.contains(e.target)) {
            clickedOnClickable = true;
        }
    });
    if (textBox && textBox.contains(e.target)) {
        clickedOnClickable = true;
    }

    if (!clickedOnClickable) {
        contactDetails.classList.remove('visible');
    }
});

document.addEventListener('DOMContentLoaded', function() {
    // All available botanical and root images
    const allImages = [
        '../assets/images/Roots_2_cropped.jpg',
        '../assets/images/Roots_2_-_Copy.jpg',
        '../assets/images/Root_Sectionv2.jpeg',
        '../assets/images/hieracium-minus-coloring-page-original.png',
        '../assets/images/1744325358775.jpg',
        '../assets/images/images20.jpg',
        '../assets/images/images7.jpg',
        '../assets/images/images30.jpg',
        '../assets/images/images8.jpg',
        '../assets/images/default-3.jpg',
        '../assets/images/images10.jpg',
        '../assets/images/betonica-altilis-coloring-page-lg.png'
    ];

    // Randomly select 3 images from the pool
    const shuffled = allImages.sort(() => 0.5 - Math.random());
    const selectedImages = shuffled.slice(0, 3);

    const container = document.getElementById('backgroundImages');
    let imageIndex = 0;

    function addRandomImage() {
        if (imageIndex >= selectedImages.length) return;

        const img = document.createElement('img');
        img.src = selectedImages[imageIndex];
        img.className = 'root-image';

        // Random position
        const randomTop = Math.random() * 60 + 10; // 10-70%
        const randomLeft = Math.random() * 60 + 10; // 10-70%

        // Random size with possibility of massive images
        // 70% chance: 150-400px, 30% chance: 500-800px (massive)
        const isMassive = Math.random() < 0.3;
        const randomSize = isMassive
            ? Math.random() * 300 + 500  // 500-800px
            : Math.random() * 250 + 150; // 150-400px

        img.style.top = randomTop + '%';
        img.style.left = randomLeft + '%';
        img.style.width = randomSize + 'px';
        img.style.height = 'auto';

        // Add click handler to show contact
        img.onclick = function(e) {
            showContact(e);
        };

        // Add cursor hover listeners
        img.addEventListener('mouseenter', () => {
            cursor.classList.add('clickable');
        });
        img.addEventListener('mouseleave', () => {
            cursor.classList.remove('clickable');
        });

        container.appendChild(img);

        // Trigger fade in
        setTimeout(() => {
            img.classList.add('visible');
        }, 100);

        imageIndex++;

        // Schedule next image
        if (imageIndex < selectedImages.length) {
            setTimeout(addRandomImage, 3000);
        }
    }

    // Start adding images
    setTimeout(addRandomImage, 500);
});
</script>
</html>