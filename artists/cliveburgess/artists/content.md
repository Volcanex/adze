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
a:hover { opacity: 0.85; }

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

.nav a[href*="artists"] {
    color: var(--page-title);
}

/* Artists Specific Layout */
.artists-container {
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
    justify-content: flex-end;
    padding-top: 0;
    padding-right: 250px;
}

.main-image img {
    max-width: 60%;
    height: auto;
    object-fit: contain;
}

/* Vertical Scroll Box */
.scroll-box {
    position: absolute;
    bottom: 20%;
    right: 550px;
    width: 320px;
    height: 400px;
    border: none;
    background: transparent;
    overflow-y: scroll;
    overflow-x: hidden;
    padding: 0;
    cursor: grab;
    user-select: none;
}

.scroll-content {
    display: flex;
    flex-direction: column;
    width: 100%;
}

.scroll-panel {
    display: block;
    width: 100%;
    padding: 32px;
    flex-shrink: 0;
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

    .artists-container {
        flex-direction: column;
        padding: 24px;
        overflow-y: auto;
    }

    .main-image {
        position: relative;
        margin-bottom: 24px;
        padding: 0;
        width: 100%;
        justify-content: center;
    }

    .main-image img {
        max-width: 100%;
        max-height: 400px;
    }

    .scroll-box {
        position: relative;
        bottom: 0;
        right: 0;
        width: 100%;
        height: auto;
        max-height: 500px;
        overflow-y: auto;
    }

    .scroll-content {
        padding-top: 0;
        padding-bottom: 0;
    }

    .scroll-panel {
        width: 100%;
        padding: 24px;
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

<main class="artists-container">
    <div class="main-image">
        <img src="../assets/images/Drill_v1ex1.jpg" alt="Tower" onclick="toggleContact(event)">
    </div>

    <div class="contact-details" id="contactDetails">
        <div class="contact-label">Contact</div>
        <div><a href="mailto:cliveburgess0@gmail.com">cliveburgess0@gmail.com</a></div>
        <div><a href="https://instagram.com/erlabrunn.imprint" target="_blank">@erlabrunn.imprint</a></div>
    </div>

    <div class="scroll-box">
        <div class="scroll-content">
            <div class="scroll-panel">
                <p>Erlabrunn works with, supports and represents a number of artists.</p>
                <p><br><br><br><br></p>
                <p>Sasha Lee (b. 2002) is a British sculptor based in Italy. His primary inspiration derives from the natural world. Organic forms and bodies are references for stone sculptures using traditional carving techniques. He foregrounds a simplicity of form and gesture, allowing the material to resonate beneath the chisel-marked or polished surfaces.</p>
                <p><br><br><br><br></p>
                <p>Maisie Ingram (b. 2003) is a figurative painter based in Glasgow. She works with and from observational drawings, personal archives and references to historical painting, discussing memory and time. Her current body of work concerns warmth, fire and gathering.</p>
                <p><em>"Day to day I see too much too quickly. Painting holds on to, and creates, moments where time opens up, slows and widens. These glances, that could have been fleeting, become the subjects of my paintings."</em></p>
                <p style="text-align: right;">- MI, 2025</p>
                <p><br><br><br><br></p>
                <p><a href="https://instagram.com/nellspracticing" target="_blank">Nell Burgess</a> (b. 2004) is a director, weaver and artist, currently based in Glasgow. Her research concerns natural fibres in industry and in relation to land. She works between drawing, performance, photography and textiles.</p>
                <p><br><br><br><br></p>
                <p>Clive Burgess (b. 2002) is an artist, director and designer working between many mediums. As of February 2026 he has been working on a series of proposals for film and performance works, as well as working with other artists and designers to show their work, both in exhibitions and publications.</p>
            </div>
        </div>
    </div>
</main>

<script>
// Enable vertical scroll with mouse wheel from anywhere on page
document.addEventListener('DOMContentLoaded', function() {
    const scrollBox = document.querySelector('.scroll-box');
    if (scrollBox) {
        // Global wheel event - scroll text box from anywhere on page
        document.addEventListener('wheel', (e) => {
            e.preventDefault();
            scrollBox.scrollTop += e.deltaY;
        }, { passive: false });

        // Touch support for mobile
        let isDown = false;
        let startY;
        let scrollTop;

        scrollBox.addEventListener('mousedown', (e) => {
            isDown = true;
            scrollBox.style.cursor = 'grabbing';
            startY = e.pageY - scrollBox.offsetTop;
            scrollTop = scrollBox.scrollTop;
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
            const y = e.pageY - scrollBox.offsetTop;
            const walk = (y - startY) * 2;
            scrollBox.scrollTop = scrollTop - walk;
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