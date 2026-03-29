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

    .artists-container {
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
        bottom: 0;
        right: 0;
        width: 100%;
        height: 300px;
    }

    .scroll-panel {
        width: 100%;
    }

    .clock-container {
        position: relative;
        bottom: auto;
        left: auto;
        margin: 24px;
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

<main class="artists-container">
    <div class="main-image">
        <img src="../assets/images/Drill_v1ex1.jpg" alt="Tower">
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
                <p>Nell Burgess (b. 2004) is a director, weaver and artist, currently based in Glasgow. Her research concerns natural fibres in industry and in relation to land. She works between drawing, performance, photography and textiles.</p>
                <p><br><br><br><br></p>
                <p>Clive Burgess is an artist, director and designer working between many mediums. As of February 2026 he has been working on a series of proposals for film and performance works, as well as working with other artists and designers to show their work, both in exhibitions and publications.</p>
            </div>
        </div>
    </div>
</main>

<script>
// Enable vertical scroll with mouse wheel
document.addEventListener('DOMContentLoaded', function() {
    const scrollBox = document.querySelector('.scroll-box');
    if (scrollBox) {
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
</script>
</html>