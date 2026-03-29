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
    pointer-events: none;
}

.root-image {
    position: absolute;
    opacity: 0;
    transition: opacity 1s ease;
    mix-blend-mode: multiply;
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
    max-width: 500px;
    font-size: 11pt;
    line-height: 9pt;
    color: var(--primary);
    text-align: justify;
    text-align-last: left;
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

/* Click Zone */
.click-zone {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 50%;
    height: 100%;
    cursor: pointer;
    z-index: 2;
}

/* Mobile */
@media (max-width: 768px) {
    .header {
        padding: 24px;
        flex-direction: column;
        gap: 20px;
        align-items: flex-start;
    }

    .nav {
        gap: 24px;
    }

    .page-content {
        padding: 40px 24px;
    }

    .page-content h1 {
        font-size: 28px;
    }
}
</style>

<html>
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
    <div class="text-box">
        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium.</p>
    </div>

    <div class="contact-details" id="contactDetails">
        <div class="contact-label">Contact</div>
        <div><a href="mailto:cliveburgess0@gmail.com">cliveburgess0@gmail.com</a></div>
        <div><a href="https://instagram.com/erlabrunn.imprint" target="_blank">@erlabrunn.imprint</a></div>
    </div>

    <div class="click-zone" onclick="toggleContact(event)"></div>
</main>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // All available images - using root images for now
    // TODO: Add botanical drawings to ../assets/images/botanical/ folder
    const allImages = [
        '../assets/images/Roots_2_cropped.jpg',
        '../assets/images/Roots_2_-_Copy.jpg',
        '../assets/images/Root_Sectionv2.jpeg'
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

        // Random size
        const randomSize = Math.random() * 200 + 150; // 150-350px

        img.style.top = randomTop + '%';
        img.style.left = randomLeft + '%';
        img.style.width = randomSize + 'px';
        img.style.height = 'auto';

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