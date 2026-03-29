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
    right: 32px;
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

    .shoulder-container {
        flex-direction: column;
        padding: 24px;
    }

    .main-image {
        margin-bottom: 24px;
    }

    .main-image img {
        max-height: 400px;
    }

    .scroll-box {
        position: relative;
        top: 0;
        right: 0;
        width: 100%;
        height: 300px;
    }

    .scroll-panel {
        width: 280px;
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

<main class="shoulder-container">
    <div class="main-image">
        <img src="../assets/images/Shoulder_Landing_v1.jpg" alt="Shoulder Residency">
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
// Enable horizontal scroll with mouse wheel
document.addEventListener('DOMContentLoaded', function() {
    const scrollBox = document.querySelector('.scroll-box');
    if (scrollBox) {
        // Mouse wheel scroll
        scrollBox.addEventListener('wheel', (e) => {
            e.preventDefault();
            e.stopPropagation();
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
</script>
</html>