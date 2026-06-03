<style>
/* Home — the cover served at the site root.
   Built 1:1 to the Figma "Landing PC" frame (1920×1080, #FFFFFF):
   a small "Lydia Lott" label top-left (30px Lapture Display, #000 at
   102,111) and one large image rectangle on the right (984×935 at
   531,111, #EDE9FF placeholder). Positions are expressed as % of the
   frame so the whole composition scales down proportionally; clamp()
   keeps the label legible. Lapture isn't loaded site-wide, so the
   font falls back to Georgia. Swap noise-wide.png for the real cover. */

* { box-sizing: border-box; }
html, body {
  margin: 0;
  padding: 0;
  background: #fff;
  color: #000;
  font-family: var(--display, 'jaf-lapture-display', 'Lapture Display', Georgia, serif);
  font-weight: 400;
}

.landing {
  position: relative;
  width: 100%;
  min-height: 100vh;
  overflow: hidden;
}

/* ── "Lydia Lott" label — left 102px, top 111px on the 1920×1080 frame ── */
.ld-name {
  position: absolute;
  left: 5.31%;            /* 102 / 1920 */
  top: 10.28vh;           /* 111 / 1080 */
  margin: 0;
  font-size: clamp(18px, 1.5625vw, 30px);
  line-height: 1.43;      /* 43 / 30 */
  font-weight: 400;
  color: #000;
}

/* ── Cover image — 984×935 at left 531, top 111 ── */
.ld-figure {
  position: absolute;
  left: 27.66%;           /* 531 / 1920 */
  top: 10.28vh;           /* 111 / 1080 */
  width: 51.25%;          /* 984 / 1920 */
  height: 86.57vh;        /* 935 / 1080 */
  margin: 0;
  background: #EDE9FF;
  display: block;
}
.ld-figure img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* ── Mobile: name on top, image full-width beneath ── */
@media (max-width: 760px) {
  .landing {
    display: flex;
    flex-direction: column;
    overflow: visible;
  }
  .ld-name {
    position: static;
    padding: 28px 24px 16px;
    font-size: 24px;
  }
  .ld-figure {
    position: static;
    width: 100%;
    height: 70vh;
    margin: 0 24px 28px;
    width: calc(100% - 48px);
  }
}
</style>

<html>
<div class="landing" translate="no">

  <p class="ld-name">Lydia Lott</p>

  <!-- Placeholder cover (#EDE9FF) — swap noise-wide.png for a real image in assets/. -->
  <a class="ld-figure" href="../works/" aria-label="Enter — all work">
    <img src="../assets/images/thumbs/2025_Bulk_Textiles_4.webp" alt="">
  </a>

</div>
</html>
