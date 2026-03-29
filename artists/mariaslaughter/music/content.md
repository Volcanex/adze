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
    max-width: 100%;
    height: auto;
}

.gothic-sidebar {
    position: fixed;
    left: 0;
    top: 0;
    width: 200px;
    height: 100vh;
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
    position: absolute;
    bottom: 20px;
    left: 20px;
    right: 20px;
    text-align: center;
    padding-top: 15px;
    border-top: 2px solid #660000;
}

.main-content-1996 {
    margin-left: 350px;
    margin-right: 100px;
    position: relative;
    z-index: 2;
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

/* Mobile styles */
@media (max-width: 768px) {
    body {
        display: flex;
        flex-direction: column; /* Stacks content vertically */
    }

    .gothic-sidebar {
        position: static; /* Remove fixed positioning */
        width: 100%; /* Full width */
        height: auto; /* Auto height */
        order: 2; /* Place below main content */
        border-right: none; /* Remove right border */
        box-shadow: none; /* Remove shadow */
        padding: 10px; /* Adjust padding for mobile */
    }

    .main-content-1996 {
        margin-left: 0; /* Remove left margin */
        margin-right: 0; /* Remove right margin */
        width: 100%; /* Full width */
        order: 1; /* Place above sidebar */
        padding: 10px; /* Add some padding */
    }

    .border-left,
    .border-right {
        display: none; /* Hide the fixed borders on mobile */
    }

    .sidebar-footer {
        position: static;
        padding-top: 10px;
        border-top: 1px solid #660000;
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
}
</style>

<html>
<img class="border-left" src="../assets/gifs/left.gif">
<img class="border-right" src="../assets/gifs/right.gif">

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
    <h1 class="gothic-title">SOUND WORKS</h1>
    <font size="2" color="#ffff00" style="font-style: italic;">ECHOES FROM THE VOID</font>
</center>
<br><br>

<center>
    <table border="5" cellpadding="15" width="80%">
        <tr>
            <th colspan="2">
                <font size="4"><b>LISTEN ON SOUNDCLOUD</b></font>
            </th>
        </tr>
        <tr>
            <td align="center">
                <a href="https://soundcloud.com/adeleclifford" target="_blank">
                    <img src="../assets/images/2023-07-18_11-41-08_UTC_1.jpg" width="300" border="0">
                    <br><br>
                    <font size="3"><b>→ VISIT SOUNDCLOUD PROFILE ←</b></font>
                </a>
            </td>
        </tr>
    </table>
</center>
<br><br>

<center>
    <font size="3"><b>SONIC NECROMANCY</b></font>
    <br><br>
    <font size="2">
    Crafting soundscapes that traverse the liminal spaces between<br>
    darkness and light, beauty and decay, past and present.<br><br>

    Each composition is a ritual, summoning frequencies from the depths<br>
    of consciousness and the shadows of forgotten dreams.
    </font>
</center>
<br><br>

<center>
    <table border="5" cellpadding="10">
        <tr>
            <td align="center">
                <img src="../assets/images/2023-02-20_11-56-28_UTC_1.jpg" width="200" border="0">
            </td>
            <td align="center">
                <img src="../assets/images/2023-02-23_21-59-22_UTC_1.jpg" width="200" border="0">
            </td>
            <td align="center">
                <img src="../assets/images/2023-08-31_12-36-44_UTC_1.jpg" width="200" border="0">
            </td>
        </tr>
    </table>
</center>
<br><br>

<center>
    <table border="5" cellpadding="15" width="70%">
        <tr>
            <th><font size="3">THEMES & INFLUENCES</font></th>
        </tr>
        <tr>
            <td>
                <font size="2">
                <b>→</b> Gothic Ambient<br>
                <b>→</b> Dark Industrial<br>
                <b>→</b> Neo-Classical Darkwave<br>
                <b>→</b> Experimental Noise<br>
                <b>→</b> Ritual Soundscapes<br>
                </font>
            </td>
        </tr>
    </table>
</center>
<br><br>

<center>
    <img src="../assets/gifs/email.webp" width="180" border="0">
    <br>
    <font size="3" color="#ff0000"><b>FOR COLLABORATIONS & COMMISSIONS</b></font>
    <br>
    <font size="4" color="#ff0000"><b>FALLENANGELSELVATICA@GMAIL.COM</b></font>
</center>
<br><br>

<center>
    <font size="3"><a href="../home">← RETURN TO HOME</a></font>
</center>
<br><br>

<center>
    <img src="../assets/gifs/bottom.gif" class="border-bottom">
</center>
</div>