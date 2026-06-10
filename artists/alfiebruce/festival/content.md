<style>
:root{--bg:#000;--text:#fff;--muted:#999;--line:rgba(255,255,255,.14);--sans:'Helvetica Neue',Helvetica,Arial,sans-serif;}
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:var(--sans);background:var(--bg);color:var(--text);-webkit-font-smoothing:antialiased;opacity:0;animation:fade .6s ease forwards;}
@keyframes fade{to{opacity:1;}}
img{display:block;max-width:100%;}
a{color:inherit;text-decoration:none;}
.bar{position:fixed;top:0;left:0;right:0;z-index:50;display:flex;align-items:center;justify-content:space-between;padding:22px 34px;mix-blend-mode:difference;}
.bar .mark{font-size:15px;letter-spacing:.32em;text-transform:uppercase;font-weight:500;}
.bar nav{display:flex;gap:30px;font-size:13px;letter-spacing:.18em;text-transform:uppercase;}
.bar nav a{color:var(--muted);transition:color .2s ease;}
.bar nav a:hover{color:var(--text);}
.head{padding:30vh 34px 8vh;border-bottom:1px solid var(--line);}
.head h1{font-size:clamp(38px,8vw,104px);font-weight:600;letter-spacing:.04em;text-transform:uppercase;line-height:.95;}
.head p{margin-top:18px;font-size:13px;letter-spacing:.2em;text-transform:uppercase;color:var(--muted);}
.gallery{display:flex;flex-wrap:wrap;gap:3px;padding:3px;}
.gallery a{position:relative;height:320px;overflow:hidden;background:#111;cursor:pointer;}
.gallery img{width:100%;height:100%;object-fit:cover;filter:grayscale(8%) brightness(.86);transition:filter .5s ease,transform .9s cubic-bezier(.2,.7,.2,1);}
.gallery a:hover img{filter:grayscale(0%) brightness(1);transform:scale(1.04);}
.foot{padding:14vh 34px;text-align:center;border-top:1px solid var(--line);}
.foot a{font-size:13px;letter-spacing:.18em;text-transform:uppercase;color:var(--muted);border-bottom:1px solid transparent;padding-bottom:3px;transition:color .2s,border-color .2s;}
.foot a:hover{color:var(--text);border-color:var(--text);}
.lb{position:fixed;inset:0;z-index:100;background:rgba(0,0,0,.96);display:none;align-items:center;justify-content:center;}
.lb.open{display:flex;}
.lb img{max-width:92vw;max-height:88vh;object-fit:contain;}
.lb .x,.lb .nav-arrow{position:absolute;color:#fff;cursor:pointer;user-select:none;opacity:.65;transition:opacity .2s;}
.lb .x:hover,.lb .nav-arrow:hover{opacity:1;}
.lb .x{top:24px;right:30px;font-size:30px;line-height:1;}
.lb .nav-arrow{top:50%;transform:translateY(-50%);font-size:44px;padding:20px;}
.lb .prev{left:14px;}
.lb .next{right:14px;}
.lb .count{position:absolute;bottom:24px;left:0;right:0;text-align:center;font-size:12px;letter-spacing:.18em;color:var(--muted);}
@media(max-width:720px){.bar{padding:18px 20px;}.bar nav{gap:18px;}.head{padding:24vh 20px 6vh;}.gallery a{height:auto;flex:1 1 100% !important;}.gallery img{height:auto;}.lb .nav-arrow{font-size:34px;padding:10px;}}
</style>
<html>
<div class="bar">
    <a href="../home/" class="mark">Alfie Bruce</a>
    <nav>
        <a href="../home/#work">Work</a>
        <a href="../home/#contact">Contact</a>
    </nav>
</div>

<header class="head">
    <h1>Festival</h1>
    <p>162 photographs &middot; 2025</p>
</header>

<section class="gallery" id="gallery">
    <a data-src="../assets/work/festival/001.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/001.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/002.jpg" style="flex:0.6665 1 213px"><img src="../assets/work/festival/002.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/003.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/003.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/004.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/004.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/005.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/005.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/006.jpg" style="flex:0.6665 1 213px"><img src="../assets/work/festival/006.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/007.jpg" style="flex:0.6665 1 213px"><img src="../assets/work/festival/007.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/008.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/008.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/009.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/009.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/010.jpg" style="flex:0.6665 1 213px"><img src="../assets/work/festival/010.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/011.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/011.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/012.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/012.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/013.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/013.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/014.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/014.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/015.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/015.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/016.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/016.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/017.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/017.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/018.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/018.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/019.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/019.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/020.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/020.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/021.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/021.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/022.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/022.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/023.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/023.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/024.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/024.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/025.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/025.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/026.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/026.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/027.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/027.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/028.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/028.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/029.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/029.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/030.jpg" style="flex:0.6665 1 213px"><img src="../assets/work/festival/030.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/031.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/031.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/032.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/032.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/033.jpg" style="flex:0.6665 1 213px"><img src="../assets/work/festival/033.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/034.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/034.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/035.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/035.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/036.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/036.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/037.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/037.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/038.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/038.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/039.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/039.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/040.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/040.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/041.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/041.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/042.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/042.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/043.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/043.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/044.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/044.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/045.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/045.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/046.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/046.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/047.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/047.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/048.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/048.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/049.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/049.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/050.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/050.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/051.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/051.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/052.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/052.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/053.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/053.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/054.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/054.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/055.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/055.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/056.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/056.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/057.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/057.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/058.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/058.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/059.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/059.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/060.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/060.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/061.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/061.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/062.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/062.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/063.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/063.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/064.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/064.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/065.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/065.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/066.jpg" style="flex:1.4233 1 455px"><img src="../assets/work/festival/066.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/067.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/067.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/068.jpg" style="flex:1.435 1 459px"><img src="../assets/work/festival/068.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/069.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/069.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/070.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/070.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/071.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/071.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/072.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/072.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/073.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/073.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/074.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/074.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/075.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/075.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/076.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/076.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/077.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/077.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/078.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/078.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/079.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/079.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/080.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/080.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/081.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/081.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/082.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/082.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/083.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/083.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/084.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/084.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/085.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/085.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/086.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/086.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/087.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/087.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/088.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/088.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/089.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/089.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/090.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/090.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/091.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/091.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/092.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/092.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/093.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/093.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/094.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/094.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/095.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/095.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/096.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/096.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/097.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/097.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/098.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/098.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/099.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/099.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/100.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/100.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/101.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/101.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/102.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/102.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/103.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/103.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/104.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/104.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/105.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/105.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/106.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/106.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/107.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/107.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/108.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/108.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/109.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/109.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/110.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/110.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/111.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/111.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/112.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/112.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/113.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/113.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/114.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/114.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/115.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/115.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/116.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/116.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/117.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/117.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/118.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/118.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/119.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/119.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/120.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/120.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/121.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/121.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/122.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/122.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/123.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/123.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/124.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/124.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/125.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/125.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/126.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/126.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/127.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/127.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/128.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/128.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/129.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/129.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/130.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/130.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/131.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/131.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/132.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/132.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/133.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/133.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/134.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/134.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/135.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/135.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/136.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/136.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/137.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/137.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/138.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/138.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/139.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/139.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/140.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/140.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/141.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/141.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/142.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/142.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/143.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/143.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/144.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/144.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/145.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/145.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/146.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/146.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/147.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/147.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/148.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/148.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/149.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/149.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/150.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/150.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/151.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/151.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/152.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/152.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/153.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/153.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/154.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/154.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/155.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/155.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/156.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/156.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/157.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/157.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/158.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/158.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/159.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/159.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/160.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/160.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/161.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/161.jpg" loading="lazy" alt="Festival"></a>
    <a data-src="../assets/work/festival/162.jpg" style="flex:1.5 1 480px"><img src="../assets/work/festival/162.jpg" loading="lazy" alt="Festival"></a>
</section>

<div class="foot"><a href="../home/#work">&larr; Back to all work</a></div>

<div class="lb" id="lb">
    <span class="x" data-act="close">&times;</span>
    <span class="nav-arrow prev" data-act="prev">&#8249;</span>
    <img id="lb-img" src="" alt="">
    <span class="nav-arrow next" data-act="next">&#8250;</span>
    <div class="count" id="lb-count"></div>
</div>

<script>
(function(){
  var links=[].slice.call(document.querySelectorAll('.gallery a'));
  var lb=document.getElementById('lb'),img=document.getElementById('lb-img'),cnt=document.getElementById('lb-count'),i=0;
  function show(n){i=(n+links.length)%links.length;img.src=links[i].getAttribute('data-src');cnt.textContent=(i+1)+' / '+links.length;}
  links.forEach(function(a,n){a.addEventListener('click',function(e){e.preventDefault();show(n);lb.classList.add('open');});});
  lb.addEventListener('click',function(e){var act=e.target.getAttribute('data-act');if(act==='close'||e.target===lb)lb.classList.remove('open');else if(act==='next')show(i+1);else if(act==='prev')show(i-1);});
  document.addEventListener('keydown',function(e){if(!lb.classList.contains('open'))return;if(e.key==='Escape')lb.classList.remove('open');else if(e.key==='ArrowRight')show(i+1);else if(e.key==='ArrowLeft')show(i-1);});
})();
</script>
</html>