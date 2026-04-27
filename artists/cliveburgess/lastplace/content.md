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
    font-size: 11pt;
    line-height: 9pt;
    color: var(--primary);
    text-align: justify;
    text-align-last: left;
    cursor: none;
    position: relative;
    z-index: 10;
    max-width: 680px;
}

.text-box p {
    margin: 0;
}

.text-box > p {
    max-width: 320px;
}

.bios-row {
    display: flex;
    flex-direction: row;
    gap: 40px;
    max-width: 680px;
}

.bios-row .bio {
    flex: 1;
    max-width: 320px;
    min-width: 0;
}

.bios-row .bio-offset {
    padding-top: 180px;
}

.bio-left {
    text-align: left;
    text-align-last: justify;
}

/* Contact Details */
.contact-details {
    position: absolute;
    font-size: 11pt;
    line-height: 9pt;
    color: var(--primary);
    opacity: 0;
    transition: opacity 1s ease;
    z-index: 100;
    pointer-events: auto;
}

.contact-details.visible {
    opacity: 1;
}

.contact-details .contact-label {
    margin-bottom: 8px;
}

.contact-details a {
    color: var(--primary);
    text-decoration: none;
    cursor: none;
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

    .text-box > p {
        max-width: 100%;
    }

    .bios-row {
        flex-direction: column;
        max-width: 100%;
    }

    .bios-row .bio,
    .bios-row .bio-offset {
        max-width: 100%;
        padding-top: 0;
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
    <div class="text-box">
        <p>Last Place&nbsp;&nbsp;Work About Contact</p>
        <p>Websites for artists, musicians, and cultural projects. Made once, made properly.</p>
        <p>Last Place is a small studio making websites for people whose work deserves more than a template. We do it the old way, one at a time. Each site is designed by hand and checked by hand. Then we hand over the domain and the keys. We keep hosting it, for free, forever (unless you get really famous, at which point we'll have a conversation).</p>
        <p>You pay once<br>and the code is yours.</p>
        <p>There will eventually be a Wozniak vs Jobs moment, but for now both Steve's are getting on well.</p>
        <p>Service — A one-of-one site, designed around your work. Your own domain, to keep. A simple dashboard to tend it, when you want to. One payment. No roof caving in.</p>
        <p>Recent work</p>
        <p>2024 - 2026</p>
        <p>Maria Slaughter — 11 2025</p>
        <p>Nina Sere — 04 2026</p>
        <p>Rose F. P. Jones — rosefpjones.com<br>View ↗ — 06 2025</p>
        <p>Erlabrunn — erlabrunn.org.uk<br>Visit ↗ — 02 2026</p>
        <p>About</p>
        <p>Last Place is one designer<br>and one engineer.</p>
        <div class="bios-row">
            <div class="bio">
                <p class="bio-left">Clive Burgess (b. 2002) is an artist, director and designer working between many mediums. He studied Architecture at The Bartlett School of Architecture, UCL (2021–2024). Alongside Last Place he co-runs Erlabrunn, a young London publishing imprint focussed on exhibitions, books, illustration, artist residencies, platforming emerging writers and handbinding, with his sister Nell. His practice and freelance work spans visual communication, model making, metalworking and drawing. He brings the eye, the hands and the patience.</p>
                <p>erlabrunn.org.uk →</p>
            </div>
            <div class="bio bio-offset">
                <p>Gabriel Penman (b. 2002) is a developer and machine learning engineer currently based in Cambodia. He's completing an MSc in Artificial Intelligence at the University of Huddersfield, and is Lead Developer at Baseline Labs, an Irish AI startup. He considers his study of AI something like the Dark Arts in Harry Potter — useful, dangerous, faintly embarrassing to admit in polite company — and finds the use of AI for creative outlets pretty abhorrent. Specialising in autonomic infrastructure has its benefits, though, and it means your website runs very cleanly.</p>
                <p>gabrielpenman.com →</p>
            </div>
        </div>
        <p>We first met at UCL Tree Soc in 2022. A society Clive ran, ostensibly about trees, it's now proof that Gabriel does sometimes go outside. We've been working together one way or another since then.</p>
        <p>There will eventually be a Wozniak vs. Jobs moment, but as of now both Steves are getting on well.</p>
        <p>Tell us about your site. Send us a sentence about your practice and a link to your work, we'll get back to you within a week.</p>
        <p>hello@lastplace.co.uk</p>
        <p>Last Place, London</p>
        <p>[clock — e.g.<br>"14 : 32 · updated today"]</p>
        <p>© [year] Last Place.<br>Made by two humans.</p>
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
const clickableElements = document.querySelectorAll('a');
clickableElements.forEach(el => {
    el.addEventListener('mouseenter', () => {
        cursor.classList.add('clickable');
    });
    el.addEventListener('mouseleave', () => {
        cursor.classList.remove('clickable');
    });
});

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
let itemIndex = 0;

function addRandomItem() {
    // First 3 items are images
    if (itemIndex < 3) {
        const img = document.createElement('img');
        img.src = selectedImages[itemIndex];
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

        container.appendChild(img);

        // Trigger fade in
        setTimeout(() => {
            img.classList.add('visible');
        }, 100);
    }
    // 4th item is contact info
    else if (itemIndex === 3) {
        const contactDiv = document.createElement('div');
        contactDiv.className = 'contact-details';

        // Position in bottom half of screen (50-80% from top)
        const randomTop = Math.random() * 30 + 50; // 50-80%
        const randomLeft = Math.random() * 60 + 10; // 10-70%

        contactDiv.style.top = randomTop + '%';
        contactDiv.style.left = randomLeft + '%';

        contactDiv.innerHTML = `
            <div class="contact-label">Contact</div>
            <div><a href="mailto:cliveburgess0@gmail.com">cliveburgess0@gmail.com</a></div>
            <div><a href="https://instagram.com/erlabrunn.imprint" target="_blank">@erlabrunn.imprint</a></div>
        `;

        container.appendChild(contactDiv);

        // Add hover listeners for the links
        const links = contactDiv.querySelectorAll('a');
        links.forEach(link => {
            link.addEventListener('mouseenter', () => {
                cursor.classList.add('clickable');
            });
            link.addEventListener('mouseleave', () => {
                cursor.classList.remove('clickable');
            });
        });

        // Trigger fade in
        setTimeout(() => {
            contactDiv.classList.add('visible');
        }, 100);
    }

    itemIndex++;

    // Schedule next item (3 images + 1 contact = 4 total)
    if (itemIndex < 4) {
        setTimeout(addRandomItem, 3000);
    }
}

// Start adding items
setTimeout(addRandomItem, 500);
</script>
</html>