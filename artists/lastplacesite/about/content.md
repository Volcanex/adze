<style>
@font-face {
    font-family: 'Cormorant';
    src: url('../assets/fonts/Cormorant[wght].ttf') format('truetype');
    font-weight: 300 700; font-style: normal; font-display: swap;
}
@font-face {
    font-family: 'Cormorant';
    src: url('../assets/fonts/Cormorant-Italic[wght].ttf') format('truetype');
    font-weight: 300 700; font-style: italic; font-display: swap;
}

:root {
    --primary: #280300;
    --bg: #ffffff;
    --accent: #0000ff;
    --ink-soft: oklch(from var(--primary) calc(l + 0.35) c h);
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: 'Cormorant', Georgia, serif;
    color: var(--primary);
    background: var(--bg);
    line-height: 1.6;
    font-size: 17px;
    cursor: none;
    overflow-x: hidden;
}
a { color: var(--primary); text-decoration: none; cursor: none; transition: opacity .25s; }
a:hover { opacity: .55; }
p { text-wrap: pretty; }
h1, h2 { font-weight: 400; text-wrap: balance; }

.cursor {
    width: 8px; height: 8px; border-radius: 50%;
    background: var(--primary); position: fixed;
    pointer-events: none; z-index: 9999;
    transform: translate(-50%, -50%);
    transition: background-color 1.2s, border-radius 3.5s, width .4s, height .4s;
    mix-blend-mode: difference; filter: invert(1);
}
.cursor.clickable { background: var(--accent); border-radius: 0; width: 14px; height: 14px; }

.header {
    padding: 20px 60px;
    display: flex; justify-content: space-between; align-items: center;
    position: fixed; top: 0; left: 0; right: 0; z-index: 100;
    color: var(--primary);
    background: color-mix(in oklch, var(--bg) 78%, transparent);
    backdrop-filter: saturate(1.1) blur(12px);
    -webkit-backdrop-filter: saturate(1.1) blur(12px);
    border-bottom: 1px solid color-mix(in oklch, var(--primary) 8%, transparent);
}
.header a { color: inherit; }
.logo { font-size: 18px; letter-spacing: 0.5px; color: var(--accent); }
.nav { display: flex; gap: 28px; font-size: 16px; }

main { max-width: 820px; margin: 0 auto; padding: 200px 60px 120px; }

h1 {
    font-size: clamp(44px, 6vw, 88px);
    line-height: 1;
    letter-spacing: -0.02em;
    font-weight: 300;
    margin-bottom: 80px;
}
h1 em { color: var(--accent); font-style: italic; }

.essay p {
    font-size: 18px;
    line-height: 1.7;
    margin-bottom: 1.2em;
    max-width: 62ch;
}
.essay p:first-of-type::first-letter {
    font-size: 3.4em;
    float: left;
    line-height: 0.88;
    padding: 6px 10px 0 0;
    font-style: italic;
    color: var(--accent);
}
.essay em { font-style: italic; }
.essay .pull {
    font-size: 32px;
    line-height: 1.2;
    margin: 60px 0;
    padding-left: 24px;
    border-left: 2px solid var(--accent);
    max-width: 28ch;
    color: var(--primary);
}

.sign {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 60px;
    margin-top: 120px;
}
.sign figure { margin: 0; }
.sign img { width: 100%; aspect-ratio: 4/5; object-fit: cover; }
.sign figcaption {
    margin-top: 16px;
    font-size: 14px;
    color: var(--ink-soft);
    display: flex; justify-content: space-between;
}
.sign figcaption .role { color: var(--accent); text-transform: uppercase; letter-spacing: 0.15em; font-size: 11px; }

@media (max-width: 840px) {
    body { cursor: auto; }
    .cursor { display: none; }
    a { cursor: pointer; }
    .header { padding: 24px; }
    main { padding: 120px 24px 60px; }
    .sign { grid-template-columns: 1fr; gap: 40px; }
}
</style>

<html>
<div class="cursor" id="cursor"></div>

<header class="header">
    <a href="../home/" class="logo">Last Place</a>
    <nav class="nav">
        <a href="../home/#work">Work</a>
        <a href="./">Studio</a>
        <a href="../home/#contact">Contact</a>
    </nav>
</header>

<main class="essay">
    <h1>Two people, <em>one small studio</em>, built the slow way.</h1>

    <p>Last Place is a design and build studio for websites. We take on a handful of projects a year and make them properly. There is no dashboard to log into, no subscription to cancel, no template with three hundred other artists' work sitting underneath it. You commission a site, you get a site, and then the site is yours.</p>

    <p>The studio is two people. Clive draws, John builds. The work happens on a long phone call, then on a flat file, then on a server in Germany. We don't work in sprints. We work in weeks, sometimes months, until the thing feels right.</p>

    <p class="pull">"Unlike a design and build service for your home extension, we will not let your roof cave in."</p>

    <p>There will eventually be a Wozniak versus Jobs moment. For now both Steves are getting on well. Clive is usually the one saying <em>this looks like a bank</em> and John is usually the one saying <em>this won't work on an iPhone 7</em>, and somewhere between those two objections the site gets made.</p>

    <p>We work with artists, musicians, cultural projects, independent imprints, and the occasional restaurant if the food is interesting enough. We don't do brand guidelines, landing pages for AI startups, or anything that requires the word <em>synergy</em> in a kickoff call. If you've been on Squarespace for three years and you're tired of looking like everybody else, this is probably the studio for you.</p>

    <p>Sites start at £400. Each one includes the design, the build, a year of hosting on our machine, and the domain transferred into your name. After that it's yours. Change it yourself, email us for changes, or leave it alone for five years. Websites, properly made, will sit quietly and do their job.</p>

    <div class="sign">
        <figure>
            <img src="../assets/images/portrait-john.svg" alt="Gabriel John Penman">
            <figcaption><span>Gabriel John Penman</span><span class="role">the build</span></figcaption>
        </figure>
        <figure>
            <img src="../assets/images/portrait-clive.svg" alt="Clive Burgess">
            <figcaption><span>Clive Burgess</span><span class="role">the design</span></figcaption>
        </figure>
    </div>
</main>

<script>
const cursor = document.getElementById('cursor');
document.addEventListener('mousemove', e => {
    cursor.style.left = e.clientX + 'px';
    cursor.style.top  = e.clientY + 'px';
});
document.querySelectorAll('a').forEach(el => {
    el.addEventListener('mouseenter', () => cursor.classList.add('clickable'));
    el.addEventListener('mouseleave', () => cursor.classList.remove('clickable'));
});
</script>
</html>
