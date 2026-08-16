<style>
@font-face {
    font-family: 'Inter';
    font-style: normal;
    font-weight: 300 900;
    font-display: fallback;
    src: url('../assets/fonts/Inter-Variable.woff2') format('woff2');
}
@font-face {
    font-family: 'Cardo';
    font-style: normal;
    font-weight: 400;
    font-display: fallback;
    src: url('../assets/fonts/Cardo-Regular.woff2') format('woff2');
}
@font-face {
    font-family: 'Cardo';
    font-style: italic;
    font-weight: 400;
    font-display: fallback;
    src: url('../assets/fonts/Cardo-Italic.woff2') format('woff2');
}
@font-face {
    font-family: 'Cardo';
    font-style: normal;
    font-weight: 700;
    font-display: fallback;
    src: url('../assets/fonts/Cardo-Bold.woff2') format('woff2');
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: 'Cardo', serif;
    color: var(--primary);
    background: var(--bg);
    line-height: 1.3;
    font-size: 12pt;
    font-weight: 400;
    text-align: left;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 48px;
    opacity: 0;
    animation: pageIn 1s ease-out forwards;
}

@keyframes pageIn { from { opacity: 0; } to { opacity: 1; } }

a { 
    color: var(--primary); 
    text-decoration: none; 
    transition: opacity 0.3s ease; 
}
a:hover { opacity: 0.6; }

/* ── Layout ── */
.text-content {
    flex: 1;
    max-width: 600px;
    padding-right: 48px;
}

.text-content p {
    margin: 0;
    line-height: 1.6;
}

/* Bigger gap between the bio and the contact details */
.contact-info {
    margin-top: 6.25em;
}

.text-content a {
    cursor: pointer;
}

/* Watch link with wide gap */
.watch-link {
    white-space: pre;
}

/* Fade-out targets when video is open */
.text-content .fadeable {
    transition: opacity 0.6s ease;
}
.text-content .fadeable.hidden {
    opacity: 0;
    pointer-events: none;
}

/* Esc button replacing the name */
#name-line {
    transition: opacity 0.6s ease;
}
#esc-btn {
    display: none;
    cursor: pointer;
    transition: opacity 0.3s ease;
}
#esc-btn:hover { opacity: 0.6; }

/* Video in place of image */
.image-container video {
    width: 100%;
    height: auto;
    display: block;
}

.image-container {
    width: 40%;
    max-width: 600px;
    min-width: 300px;
    margin-right: 48px;
    flex-shrink: 0;
}

.image-container img {
    width: 100%;
    height: auto;
    display: block;
}

/* ── Mobile breakpoint ── */
@media (max-width: 900px) {
    body {
        flex-direction: column;
        padding: 24px;
        align-items: stretch;
    }

    .text-content {
        padding-right: 0;
        margin-bottom: 32px;
        max-width: 100%;
    }

    .image-container {
        width: 96%;
        max-width: none;
        margin: 0 2%;
    }
}
</style>

<html>
<div class="text-content">
    <p id="name-line">Nell Burgess</p>
    <p id="esc-btn">esc</p>
    <p class="fadeable">is a weaver based in Glasgow</p>
    <div class="contact-info fadeable">
        <p><a id="watch-link" class="watch-link" href="#">Watch:                    Swiss Arm, 2026</a></p>
        <p><a href="https://instagram.com/nellspracticing" target="_blank">Instagram</a></p>
        <p><a id="email-link">n3llburgess@gmail.com</a></p>
    </div>
</div>

<div class="image-container">
    <img id="hero-image" src="../assets/images/DSC_0091.JPG" alt="Nell Burgess weaving">
    <video id="hero-video" style="display:none;" playsinline></video>
</div>

<script>
var imagePool = [
    'DSC_0077.JPG',
    'DSC_0081.JPG',
    'DSC_0091.JPG',
    'DSC_0100.JPG',
    'DSC_0114.JPG',
    'Islay_4.jpg'
];
var videoPool = [
    '../assets/videos/swiss-arm-1.mp4',
    '../assets/videos/swiss-arm-2.mp4'
];

// Random hero image on load
document.getElementById('hero-image').src =
    '../assets/images/' + imagePool[Math.floor(Math.random() * imagePool.length)];

// Email copy
document.getElementById('email-link').addEventListener('click', function(e) {
    e.preventDefault();
    navigator.clipboard.writeText('n3llburgess@gmail.com').then(function() {
        var el = document.getElementById('email-link');
        var orig = el.textContent;
        el.textContent = 'Copied';
        setTimeout(function() { el.textContent = orig; }, 1500);
    });
});

// Watch link — show Swiss Arm video
function openVideo() {
    var img = document.getElementById('hero-image');
    var vid = document.getElementById('hero-video');
    
    // Hide image, show video
    img.style.display = 'none';
    vid.style.display = 'block';
    
    // Load and play MDSC_0084
    vid.src = '../assets/MDSC_0084.mp4';
    vid.play();
    
    document.querySelectorAll('.fadeable').forEach(function(el) {
        el.classList.add('hidden');
    });
    document.getElementById('name-line').style.display = 'none';
    document.getElementById('esc-btn').style.display = 'block';
}

function closeVideo() {
    var img = document.getElementById('hero-image');
    var vid = document.getElementById('hero-video');
    
    // Stop and hide video, show image
    vid.pause();
    vid.style.display = 'none';
    img.style.display = 'block';
    
    document.querySelectorAll('.fadeable').forEach(function(el) {
        el.classList.remove('hidden');
    });
    document.getElementById('esc-btn').style.display = 'none';
    document.getElementById('name-line').style.display = 'block';
}

document.getElementById('watch-link').addEventListener('click', function(e) {
    e.preventDefault();
    openVideo();
});

document.getElementById('esc-btn').addEventListener('click', closeVideo);

document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') closeVideo();
});
</script>
</html>