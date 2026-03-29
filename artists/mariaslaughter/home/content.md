<style>
@font-face {
    font-family: 'Ithornet';
    src: url('../assets/fonts/Ithornet.ttf') format('truetype');
}

@font-face {
    font-family: 'Cardinal';
    src: url('../assets/fonts/Cardinal.ttf') format('truetype');
}

@font-face {
    font-family: 'Teutonic';
    src: url('../assets/fonts/teutonic1.ttf') format('truetype');
}

@font-face {
    font-family: 'Aniron';
    src: url('../assets/fonts/anirb___.ttf') format('truetype');
}

html, body {
    margin: 0;
    padding: 0;
    min-height: 100%;
    height: auto;
    overflow-x: hidden;
}

body {
    background-color: #281800;
    background-image: url('../assets/gifs/ceramic.gif');
    background-repeat: repeat;
    color: #ff0000;
    font-family: Arial, Helvetica, sans-serif;
    padding-bottom: 50px;
}

a {
    color: #ffff00;
    text-decoration: none;
    font-weight: bold;
}

a:visited {
    color: #00fff0;
}

a:hover {
    color: #ffffff;
    text-decoration: underline;
}

center {
    display: block;
    text-align: center;
}

table {
    margin: 0 auto;
    border-color: #ff0000;
    border-style: outset;
    background-color: #000000;
}

th, td {
    color: #ffff00;
    padding: 5px;
}

img {
    image-rendering: auto;
    max-width: 100%; /* Make images responsive */
    height: auto; /* Maintain aspect ratio */
}

.gothic-sidebar {
    position: fixed; /* From music page */
    left: 0; /* From music page */
    top: 0; /* From music page */
    width: 200px; /* From music page */
    height: 100vh; /* From music page */
    background: linear-gradient(180deg, #1a0000 0%, #330000 100%);
    border-right: 3px solid #660000;
    padding: 20px;
    overflow-y: auto;
    z-index: 100;
    box-shadow: 5px 0 15px rgba(0,0,0,0.7);
}

.sidebar-logo {
    text-align: center;
    margin-bottom: 15px;
    padding-bottom: 10px;
}

.sidebar-logo img {
    filter: drop-shadow(0 0 8px #ff0000);
}

.sidebar-title {
    text-align: center;
    margin-bottom: 15px;
    font-family: 'Ithornet', serif;
    font-size: 18px;
    letter-spacing: 2px;
}

.sidebar-nav {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin: 20px 0;
}

.nav-link {
    display: block;
    padding: 10px 8px;
    color: #ffff00 !important;
    text-decoration: none;
    border: 2px solid #660000;
    border-radius: 0;
    transition: all 0.3s;
    background: #000000;
    font-family: 'Cardinal', serif;
    font-size: 14px;
}

.nav-link:hover {
    background: #660000;
    border-color: #ff0000;
    color: #ffffff !important;
    padding-left: 15px;
}

.sidebar-section {
    margin: 20px 0;
    line-height: 1.8;
    font-family: 'Teutonic', serif;
}

.sidebar-footer {
    position: absolute; /* From music page */
    bottom: 20px; /* From music page */
    left: 20px; /* From music page */
    right: 20px; /* From music page */
    text-align: center;
    padding-top: 15px;
    border-top: 2px solid #660000;
}

.main-content-1996 {
    margin-left: 350px; /* From music page */
    margin-right: 100px; /* From music page */
    position: relative;
    z-index: 2;
    padding: 20px; /* Keep existing padding */
}

.border-left {
    position: fixed;
    left: 240px;
    top: 0;
    height: 100%;
    z-index: 50;
}

.border-right {
    position: fixed;
    right: 0;
    top: 0;
    height: 100%;
    z-index: 1;
}

.border-bottom {
    display: block;
    width: 100%;
}

center {
    position: relative;
}

font {
    color: inherit;
}

b {
    color: #ffff00;
    text-shadow: 1px 1px 2px #ff0000;
    font-family: 'Aniron', serif;
}

.gothic-title {
    font-family: 'Ithornet', serif;
    font-size: 72px;
    color: #000000;
    -webkit-text-stroke: 2px #ff0000;
    paint-order: stroke fill;
    text-shadow: 0 0 20px #ff0000,
                 0 0 30px #ff0000;
    letter-spacing: 4px;
    margin: 20px 0;
    font-weight: normal;
}

.gallery-grid img {
    margin: 10px;
    border: 3px solid #660000;
    transition: all 0.3s;
}

.gallery-grid img:hover {
    border-color: #ff0000;
    transform: scale(1.05);
    box-shadow: 0 0 20px #ff0000;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
    body {
        display: flex;
        flex-direction: column; /* Ensure content stacks correctly */
        padding-bottom: 0;
    }

    .gothic-sidebar {
        position: static;
        width: 100%;
        height: auto;
        order: 2; /* Place below main content */
        border-right: none;
        border-top: 3px solid #660000;
        padding: 10px;
        box-shadow: none;
    }

    .gothic-sidebar .sidebar-footer {
        position: static;
        margin-top: 15px;
        border-top: none;
    }

    .sidebar-nav {
        flex-direction: row;
        flex-wrap: wrap;
        justify-content: center;
        gap: 5px;
        padding: 0 5px;
    }

    .nav-link {
        flex: 0 1 calc(50% - 5px);
        padding: 8px 5px;
        text-align: center;
        font-size: 11px;
        min-width: 0;
        box-sizing: border-box;
    }

    .nav-link:hover {
        padding-left: 5px;
        padding-right: 5px;
    }

    .main-content-1996 {
        margin-left: 0;
        margin-right: 0;
        width: 100%;
        order: 1; /* Place above sidebar */
        padding: 10px;
    }

    .border-left, .border-right {
        display: none;
    }

    .gothic-title {
        font-size: 48px;
    }

    table {
        width: 100%;
    }

    td {
        display: block;
        width: 100%;
        text-align: center;
    }

    .gallery-grid img {
        width: calc(100% - 20px);
        margin: 10px 0;
    }
}
</style>

<html>
<img class="border-left" src="../assets/gifs/left.gif">
<img class="border-right" src="../assets/gifs/right.gif">

<div class="site-container">
    <!-- Sidebar Navigation -->
    <div class="gothic-sidebar">
        <div class="sidebar-logo">
            <img src="../assets/gifs/eyedog.gif" width="120">
        </div>

        <div class="sidebar-title">
            <font size="3" color="#ffff00"><b>MARIA<br>SLAUGHTER</b></font>
        </div>

        <hr color="#660000" size="2">

        <div class="sidebar-nav">
            <a href="../home" class="nav-link">
                <font size="2">☩ HOME</font>
            </a>
            <a href="../gallery" class="nav-link">
                <font size="2">☩ GALLERY</font>
            </a>
            <a href="../music" class="nav-link">
                <font size="2">☩ MUSIC</font>
            </a>
            <a href="https://instagram.com/whitethornapple" target="_blank" class="nav-link">
                <font size="2">☩ INSTAGRAM</font>
            </a>
            <a href="https://soundcloud.com/adeleclifford" target="_blank" class="nav-link">
                <font size="2">☩ SOUNDCLOUD</font>
            </a>
        </div>

        <hr color="#660000" size="2">

        <div class="sidebar-section">
            <font size="2" color="#bb0000"><b>COLLECTIONS</b></font><br><br>
            <font size="1">
            → Dark Arts<br>
            → Photography<br>
            → Sound Works<br>
            → Archive<br>
            </font>
        </div>

        <div class="sidebar-footer">
            <font size="1" color="#880000">
            Est. MCMXCVI<br>
            Digital Necropolis
            </font>
            <br><br>
            <img src="../assets/gifs/spider.webp" width="60">
        </div>
    </div>

    <!-- Main Content -->
    <div class="main-content-1996">
    <center>
        <h1 class="gothic-title">MARIA SLAUGHTER</h1>
        <img src="../assets/gifs/jump.webp" width="100">
    </center>
    <br>

    <center>
        <font size="2" color="#ffff00" style="font-style: italic;">REVIVALIST OF THE DARK ARTS</font>
        <br>
        <font size="4"><b>FOR</b></font>
        <br><br>

        {}
    </center>
    <br><br>

    <center>
        <table border="5" cellpadding="10">
            <tr>
                <td align="center">
                    <a href="../gallery">
                        <img src="../assets/images/2025-12-21_21-44-10_UTC_1.jpg" width="200" border="0">
                        <br>
                        <font size="2"><b>ENTER GALLERY</b></font>
                    </a>
                </td>
                <td align="center">
                    <a href="../music">
                        <img src="../assets/images/2025-11-02_18-14-12_UTC_1.jpg" width="200" border="0">
                        <br>
                        <font size="2"><b>HEAR THE SOUNDS</b></font>
                    </a>
                </td>
            </tr>
        </table>
    </center>
    <br><br>

    <center>
        <font size="3">LATEST WORKS</font>
        <br><br>
        <table border="5" cellpadding="10">
            <tr>
                <td align="center">
                    <img src="../assets/images/2025-10-25_17-29-26_UTC_1.jpg" width="150" border="0">
                </td>
                <td align="center">
                    <img src="../assets/images/2023-10-05_16-13-19_UTC_1.jpg" width="150" border="0">
                </td>
                <td align="center">
                    <img src="../assets/images/2025-09-16_20-53-46_UTC_1.jpg" width="150" border="0">
                </td>
            </tr>
        </table>
    </center>
    <br><br>

    <center>
        <img src="../assets/gifs/email.webp" width="180" border="0">
        <br>
        <font size="4" color="#ff0000"><b>FALLENANGELSELVATICA@GMAIL.COM</b></font>
    </center>
    <br><br>

    <center>
        <font size="2">&copy; MARIA SLAUGHTER - DIGITAL NECROPOLIS</font>
    </center>
    <br><br>

    <center>
        <img src="../assets/gifs/bottom.gif" class="border-bottom">
    </center>
    </div>
</div>
</html>
</html>