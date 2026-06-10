<style>
:root {
    --ink: #000;
    --bg: #fff;
    --works: #0000FF;
    --exhibitions: #1AFF00;
    --about: #FF0033;
    --contact: #8C00FF;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

html, body { height: 100%; }

body {
    font-family: 'Quasimoda', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: var(--bg);
    color: var(--ink);
    overflow: hidden;
}

.stage {
    position: relative;
    width: min(92vw, 720px);
    margin: 0 auto;
    min-height: 100vh;
    padding: clamp(48px, 12vh, 140px) 0;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.number {
    font-weight: 400;
    font-size: clamp(96px, 22vw, 220px);
    line-height: 0.9;
    color: var(--about);
    letter-spacing: -0.03em;
    display: block;
    margin-left: 10%;
}

.message {
    font-weight: 300;
    font-size: clamp(16px, 3vw, 22px);
    line-height: 1.4;
    color: #000;
    margin-top: clamp(24px, 5vh, 48px);
    margin-left: 12%;
}

.home-link {
    display: inline-block;
    margin-top: clamp(32px, 6vh, 60px);
    margin-left: 12%;
    font-weight: 400;
    font-size: clamp(28px, 5vw, 52px);
    line-height: 1;
    color: var(--works);
    text-decoration: none;
    transition: opacity 0.2s ease;
}
.home-link:hover { opacity: 0.55; }

@keyframes title-drift {
    from { transform: translateY(0); }
    to   { transform: translateY(10px); }
}
.number { animation: title-drift 2.2s ease-out forwards; }
</style>

<html>
<div class="stage">
    <span class="number">404</span>
    <p class="message">This page doesn't exist.</p>
    <a class="home-link" href="/">Rose Jones</a>
</div>
</html>
