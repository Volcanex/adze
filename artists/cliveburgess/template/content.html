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
    --mm-to-px: 5.56; /* 100px = 18mm, so 1mm = 5.56px */
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

.calibration-info {
    position: fixed;
    top: 60px;
    right: 60px;
    font-size: 11pt;
    color: var(--primary);
    z-index: 20;
    cursor: pointer;
}

.calibration-dropdown {
    display: none;
    margin-top: 5px;
    font-size: 11pt;
    line-height: 1.4;
    opacity: 0;
    transition: opacity 0.2s ease;
}

.calibration-info.active .calibration-dropdown {
    display: block;
}

.calibration-info.active .calibration-dropdown.visible {
    opacity: 1;
}

.calibration-box {
    width: 100px;
    height: 100px;
    background: black;
    margin: 10px 0;
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

.binding-image {
    position: absolute;
    opacity: 0;
    transition: opacity 1s ease;
    mix-blend-mode: multiply;
}

.binding-image.visible {
    opacity: 0.3;
}

/* Content */
.page-content {
    flex: 1;
    padding: 40px 60px 80px;
    position: relative;
    z-index: 5;
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
    margin: 0 0 12px 0;
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

    .page-content {
        padding: 24px;
    }

    .text-box {
        max-width: 100%;
    }
}
</style>

<html>
<div class="background-images" id="backgroundImages"></div>

<div class="calibration-info" id="calibrationInfo">
    Screen Calibration
    <div class="calibration-dropdown" id="calibrationDropdown">
        <div class="calibration-box"></div>
        100px = 18mm<br>
        1mm = 5.56px<br>
        <br>
        <em>Calibrated for ASUS native screen.<br>
        Recalibrate if using different display.</em>
    </div>
</div>

<header class="header">
    <a href="../home/" class="logo">Erlabrunn</a>
    <nav class="nav">
        <a href="../lastplace/">Last Place</a>
        <a href="../shoulder/">Shoulder</a>
    </nav>
</header>

<main class="page-content">
    <div class="text-box">
        <p>Template</p>
    </div>
</main>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // Calibration info toggle
    const calibrationInfo = document.getElementById('calibrationInfo');
    const calibrationDropdown = document.getElementById('calibrationDropdown');

    calibrationInfo.addEventListener('click', function() {
        if (calibrationInfo.classList.contains('active')) {
            calibrationDropdown.classList.remove('visible');
            setTimeout(() => {
                calibrationInfo.classList.remove('active');
            }, 200);
        } else {
            calibrationInfo.classList.add('active');
            setTimeout(() => {
                calibrationDropdown.classList.add('visible');
            }, 200);
        }
    });

    // Add bookbinding images to ../assets/images/bookbinding/ folder
    // Named: bookbinding_1.jpg, bookbinding_2.jpg, bookbinding_3.jpg
    const images = [
        '../assets/images/bookbinding/bookbinding_1.jpg',
        '../assets/images/bookbinding/bookbinding_2.jpg',
        '../assets/images/bookbinding/bookbinding_3.jpg'
    ];

    const container = document.getElementById('backgroundImages');
    let imageIndex = 0;

    function addRandomImage() {
        if (imageIndex >= images.length) return;

        const img = document.createElement('img');
        img.src = images[imageIndex];
        img.className = 'binding-image';

        // Random position
        const randomTop = Math.random() * 60 + 10; // 10-70%
        const randomLeft = Math.random() * 60 + 10; // 10-70%

        // Random size - 30% chance of large, 70% medium
        const isLarge = Math.random() < 0.3;
        const randomSize = isLarge
            ? Math.random() * 200 + 400  // 400-600px for detail
            : Math.random() * 200 + 200; // 200-400px for variety

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
        if (imageIndex < images.length) {
            setTimeout(addRandomImage, 3000);
        }
    }

    // Start adding images
    setTimeout(addRandomImage, 500);
});
</script>
</html>