<style>
/* About — built to the Figma spec (1920×1080).
   Everything is Lapture Display 30px/43px. Lapture isn't actually loaded on
   the site, so var(--display) resolves to Georgia (same as the Works page).
   If Lydia has an Adobe/Lapture kit, add its <link> site-wide for the real face. */

* { box-sizing: border-box; }
html, body {
  margin: 0;
  padding: 0;
  background: #fff;
  color: #000;
  font-family: var(--display, 'jaf-lapture-display', 'Lapture Display', Georgia, serif);
  font-weight: 400;
}

.about {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* ── Top nav: All Work · Lydia Lott · Info ── */
.ab-nav {
  display: flex;
  align-items: baseline;
  padding: clamp(18px, 1.4vw, 27px) 5.3vw;
  font-size: clamp(18px, 1.5625vw, 30px);   /* match Home/Works title size */
  line-height: 1.43;
}
.ab-nav a { text-decoration: none; color: #000; white-space: nowrap; }
.ab-nav a:hover { color: #C64646; }
.ab-brand {
  color: #C64646 !important;
  margin-left: clamp(28px, 19vw, 400px);   /* sits left-of-centre, per mockup */
}
.ab-info { margin-left: auto; }            /* pushed to the right edge */

/* ── Main: text column (left) + portrait (right) ── */
.ab-main {
  flex: 1 1 auto;
  display: grid;
  grid-template-columns: minmax(0, 48%) 1fr;
  column-gap: 5vw;
  align-items: start;
  padding: 0 5.3vw clamp(40px, 5vw, 80px);
}

.ab-text {
  position: relative;
  z-index: 1;
  padding-top: clamp(56px, 30vh, 320px);   /* large top whitespace ~y420/1080 */
  font-size: 14pt;                          /* match the Works page category text */
  line-height: 1.43;
  max-width: 921px;
}



.ab-text p { margin: 0 0 1.43em; }

.ab-contact { margin: 0; }
.ab-contact .ab-line { display: block; }
.ab-contact a { color: #000; text-decoration: none; }
.ab-contact a:hover { color: #C64646; }

/* ── Portrait ── */
.ab-figure {
  margin: clamp(40px, 9vh, 111px) 0 0;
  align-self: stretch;
}
.ab-figure img {
  display: block;
  width: 100%;
  height: clamp(380px, 80vh, 935px);
  object-fit: cover;
  background: #f0ede8;
}

/* ── Mobile ── */
@media (max-width: 760px) {
  .ab-nav {
    flex-wrap: wrap;
    gap: 4px 18px;
    font-size: 20px;
  }
  .ab-brand { margin-left: 0; }
  .ab-info { margin-left: auto; }
  .ab-main {
    grid-template-columns: 1fr;
    row-gap: 28px;
  }
  .ab-text {
    padding-top: 36px;
    font-size: 14pt;
    order: 2;
  }
  .ab-text::before { top: calc(36px + 1.5em); height: 170px; }
  .ab-figure { order: 1; margin-top: 12px; }
  .ab-figure img { height: 62vh; }
}
</style>

<html>
<div class="about" translate="no">

  <nav class="ab-nav">
    <a href="../works/">All Work</a>
    <a class="ab-brand" href="../home/">Lydia Lott</a>
    <a class="ab-info" href="../about/">Info</a>
  </nav>

  <main class="ab-main">
    <div class="ab-text">
      <p>Lydia Lott's practice explores the relationship between public and private selves, drawing on R.D. Laing's concept of the divided self. Through painting, textiles, and image-making, they investigate the spaces where interior life becomes visible and the boundaries between what is concealed and what is revealed begin to dissolve.</p>

      <p>Lott explores intimate subjects and domestic spaces: beds, bedrooms, naked bodies, family archives, and moments of emotional exposure. These motifs function as sites where vulnerability can emerge beyond performance. Rather than treating privacy as something to be protected, they are interested in what happens when private experience enters the public realm and becomes available to collective recognition.</p>

      <p>Underlying much of their work is a distinction between being seen and being displayed. They explores forms of nakedness, confession, and self-disclosure that resist spectacle, instead proposing visibility as a mode of connection. Figures are often presented in states of openness and exposure, not as objects to be consumed, but as subjects with complex inner lives.</p>

      <p>Material process plays an important role in this investigation. Whether through the visible ground of a painting or the tactile surface of tufted textiles, Lott allows traces of making to remain present. These gestures of incompleteness and exposure mirror the psychological concerns of the work itself. Ultimately, their practice asks what it might mean to inhabit public space without relinquishing intimacy, and to be encountered fully rather than merely looked at.</p>

      <p class="ab-contact">
        <span class="ab-line">Contact</span>
        <span class="ab-line">Lydia Lott</span>
        <a class="ab-line" href="tel:+447580248924">07580 248924</a>
        <a class="ab-line" href="mailto:lelott2@gmail.com">lelott2@gmail.com</a>
        <a class="ab-line" href="https://instagram.com/lydialottart" target="_blank" rel="noopener">Instagram</a>
      </p>
    </div>

    <!-- Studio portrait of Lydia with her textile works. -->
    <figure class="ab-figure">
      <img src="../assets/images/saatchi_art_pic_5.jpg" alt="Lydia Lott in her studio">
    </figure>
  </main>

</div>
</html>