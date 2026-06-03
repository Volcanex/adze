<style>
:root {
  --tile-bg: transparent;
  --caption-bg: transparent;
  --ink: #280900;
  --accent: #0800FF;
  --tile-w: 320px;
  --tile-h: 248px;
  --caption-h: 46px;
  --gap: 18px;        /* column gap (horizontal) */
  --row-gap: 13px;    /* row gap (vertical) — slightly tighter than columns */
  --tick-ms: 480ms;
  --display: 'jaf-lapture-display', 'Lapture Display', Georgia, serif;
  --caption: 'Garamond ATF Text', 'Cardo', Georgia, serif;
}

* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: #fff; color: var(--ink); font-family: var(--caption); overflow: hidden; height: 100%; }
/* Fixed (not min-) height so the flex column is bounded to the screen — lets
   .ll-viewport scroll its content internally in vertical mode instead of the
   whole grid overflowing the (overflow:hidden) body and getting clipped. */
body { height: 100%; display: flex; flex-direction: column; }
.ll-page { flex: 1 1 auto; min-height: 0; display: flex; flex-direction: column; width: 100%; min-width: 0; overflow: hidden; }

/* ── Top bar ── */
.ll-bar {
  flex: 0 0 auto;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 24px 32px 16px;
  gap: 32px;
}

.ll-filters {
  display: flex;
  flex-wrap: nowrap;
  gap: 2px 16px;
  align-items: baseline;
  max-width: none;
  width: 100%;
  overflow-x: auto;
}
.ll-filter {
  font-family: var(--display);
  font-size: 14pt;
  line-height: 20px;
  color: var(--ink);
  background: none;
  border: 0;
  padding: 0;
  cursor: pointer;
  text-align: left;
  letter-spacing: 0.01em;
  white-space: nowrap;
  text-decoration: none;   /* the About entry is an <a> */
}
.ll-filter.is-active { color: var(--accent); }
.ll-filter:hover { color: var(--accent); }

.ll-orient {
  font-family: var(--display);
  font-size: 22px;
  display: flex;
  gap: 14px;
  white-space: nowrap;
}
.ll-orient button {
  background: none;
  border: 0;
  padding: 0;
  font: inherit;
  color: var(--ink);
  cursor: pointer;
  opacity: 1;
}
.ll-orient button.is-active { color: var(--accent); }

/* ── Grid viewport ── */
.ll-viewport {
  flex: 1 1 auto;
  min-height: 0;          /* allow the flex item to shrink below content so
                             overflow-y:auto actually scrolls in vertical mode */
  position: relative;
  width: 100%;
  overflow-x: auto;
  overflow-y: hidden;
  padding: 0 32px 32px;
  scrollbar-width: none;
  -ms-overflow-style: none;
}
.ll-viewport::-webkit-scrollbar {
  display: none;
}
.ll-grid {
  position: relative;
}

/* tile */
.ll-tile {
  position: absolute;
  width: var(--tile-w);
  height: calc(var(--tile-h) + var(--caption-h));
  transition: opacity 220ms, transform 900ms cubic-bezier(0.45, 0, 0.55, 1);
  /* will-change is applied transiently in reflow() during the animation and
     removed on transitionend — leaving it on permanently promotes all tiles to
     compositor layers and stutters vertical scroll. */
  cursor: pointer;
  top: 0;
  left: 0;
  opacity: 0;
}
.ll-grid.is-ready .ll-tile { opacity: 1; }
.ll-grid.is-ready .ll-tile.is-dim { opacity: 0.45; }
.ll-tile .ll-img {
  width: 100%;
  height: var(--tile-h);
  background: var(--tile-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}
.ll-tile .ll-img img {
  max-width: 100%;
  max-height: 100%;
  width: auto;
  height: auto;
  display: block;
}
.ll-tile .ll-caption {
  width: 100%;
  height: var(--caption-h);
  background: var(--caption-bg);
  display: flex;
  align-items: center;
  padding: 0 14px;
  font-family: var(--caption);
  font-style: italic;
  font-size: 15px;
  line-height: 1.2;
  color: #000;
}
.ll-tile.is-dim { opacity: 0.45; }

/* vertical mode — scrolls down, never sideways */
.ll-page.is-vertical .ll-viewport { overflow-x: hidden; overflow-y: auto; }

/* small screens */
@media (max-width: 720px) {
  :root { --tile-w: calc((100vw - 24px - 12px) / 2); --tile-h: calc(var(--tile-w) * 0.78); --caption-h: 40px; --gap: 12px; }
  .ll-bar { padding: 16px 12px 12px; flex-wrap: wrap; gap: 12px; }
  .ll-viewport { padding: 0 12px 24px; }
  .ll-filters { display: flex; flex-wrap: wrap; gap: 2px 16px; align-items: baseline; }
  .ll-filter { font-size: 14pt; line-height: 20px; }
  .ll-orient { display: none; }
}

/* narrow desktop: snap to 3 rows flex wrap */
@media (max-width: 1200px) and (min-width: 721px) {
  .ll-filters { display: flex; flex-wrap: wrap; gap: 2px 16px; align-items: baseline; overflow: visible; }
}

/* ── Lightbox: click a tile to view the work full-size ── */
.ll-lightbox {
  position: fixed;
  inset: 0;
  z-index: 50;
  display: none;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 6vh 6vw;
  background: rgba(255, 255, 255, 0.975);
}
.ll-lightbox.is-open { display: flex; }
.ll-lb-img {
  max-width: 88vw;
  max-height: 76vh;
  width: auto;
  height: auto;
  object-fit: contain;
  display: block;
}
.ll-lb-caption {
  margin-top: 20px;
  font-family: var(--caption);
  font-style: italic;
  font-size: 16px;
  line-height: 1.3;
  color: #000;
  text-align: center;
  max-width: 88vw;
}
.ll-lb-close,
.ll-lb-nav {
  position: absolute;
  background: none;
  border: 0;
  padding: 0;
  cursor: pointer;
  color: #000;
  font-family: var(--display);
  line-height: 1;
}
.ll-lb-close:hover,
.ll-lb-nav:hover { color: var(--accent); }
.ll-lb-close { top: 22px; right: 30px; font-size: 30px; }
.ll-lb-nav { top: 50%; transform: translateY(-50%); font-size: 42px; padding: 12px 18px; }
.ll-lb-prev { left: 10px; }
.ll-lb-next { right: 10px; }
@media (max-width: 720px) {
  .ll-lb-nav { font-size: 32px; padding: 8px 10px; }
  .ll-lb-caption { font-size: 15px; }
}
</style>

<html>
<div class="ll-page" id="ll-page" translate="no">
  <header class="ll-bar">
    <nav class="ll-filters" id="ll-filters" aria-label="Filter works by tag"></nav>
    <div class="ll-orient" id="ll-orient" role="group" aria-label="Layout orientation">
      <button data-orient="h" class="is-active">Horizontal</button>
      <button data-orient="v">Vertical</button>
    </div>
  </header>

  <div class="ll-viewport" id="ll-viewport">
    <div class="ll-grid" id="ll-grid"></div>
    <div id="ll-probe" aria-hidden="true" style="position:absolute;visibility:hidden;pointer-events:none;top:0;left:0;height:1px;"></div>
  </div>

  <div class="ll-lightbox" id="ll-lightbox" role="dialog" aria-modal="true" aria-label="Work detail" aria-hidden="true">
    <button class="ll-lb-close" id="ll-lb-close" type="button" aria-label="Close">&times;</button>
    <button class="ll-lb-nav ll-lb-prev" id="ll-lb-prev" type="button" aria-label="Previous work">&#8249;</button>
    <img class="ll-lb-img" id="ll-lb-img" alt="">
    <div class="ll-lb-caption" id="ll-lb-caption"></div>
    <button class="ll-lb-nav ll-lb-next" id="ll-lb-next" type="button" aria-label="Next work">&#8250;</button>
  </div>
</div>

<script>
(function () {
  const TAGS = [
    { id: 'all',         label: 'All' },
    { id: 'paintings',   label: 'Paintings' },
    { id: 'drawings',    label: 'Drawings' },
    { id: 'textiles',    label: 'Textiles' },
    { id: 'sculpture',   label: 'Sculpture' },
    { id: 'selected',    label: 'Selected Works' },
    { id: 'airbrushing', label: 'Airbrushing' },
    { id: 'landscapes',  label: 'Landscapes' },
    { id: 'soft-bodies', label: 'Soft Bodies' },
    { id: 'etchings',    label: 'Etchings' },
    { id: 'exhibitions', label: 'Exhibitions' },
    { id: 'workshops',   label: 'Workshops' },
    { id: 'about',       label: 'About', href: '../about/' },  // not a filter — links out
  ];

  const ROWS = 3;        // horizontal mode: fixed rows, scrolls sideways
  const VERT_COLS = 3;   // vertical mode: fixed columns, scrolls down
  const MOBILE_BP = 720;

  const page     = document.getElementById('ll-page');
  const filtersEl = document.getElementById('ll-filters');
  const orientEl = document.getElementById('ll-orient');
  const viewport = document.getElementById('ll-viewport');
  const grid     = document.getElementById('ll-grid');
  const lightbox = document.getElementById('ll-lightbox');
  const lbImg    = document.getElementById('ll-lb-img');
  const lbCap    = document.getElementById('ll-lb-caption');

  let works = [];
  let cols  = 3;
  let activeTag = 'all';
  let orientation = window.innerWidth < MOBILE_BP ? 'v' : 'h';
  let positions = {};

  function isMobile() { return window.innerWidth < MOBILE_BP; }

  function applyOrientationClass() {
    page.classList.toggle('is-vertical', orientation === 'v');
    orientEl.querySelectorAll('button').forEach(b => b.classList.toggle('is-active', b.dataset.orient === orientation));
  }

  function metrics() {
    // Resolve from CSS vars on :root. Handles `calc(...)` by writing the var
    // onto a temporary probe element and reading its computed pixel size.
    const probe = document.getElementById('ll-probe');
    const measure = (varName) => {
      probe.style.width = `var(${varName})`;
      const w = probe.getBoundingClientRect().width;
      probe.style.width = '';
      return w;
    };
    const tw  = measure('--tile-w')    || 320;
    const th  = measure('--tile-h')    || 248;
    const ch  = measure('--caption-h') || 46;
    const gap = measure('--gap')       || 18;
    const rowGap = measure('--row-gap') || gap;
    return { tw, th: th + ch, gap, rowGap, cellW: tw + gap, cellH: th + ch + rowGap };
  }

  function defaultOrder() {
    return works.slice().sort((a, b) => (b.date || '').localeCompare(a.date || ''));
  }

  function matches(w, tag) {
    if (tag === 'all') return true;
    return Array.isArray(w.tags) && w.tags.includes(tag);
  }

  // Order: matched first (top-left), unmatched after. Stable within each group.
  function orderedForTag(tag) {
    const ordered = defaultOrder();
    if (tag === 'all') return ordered;
    return ordered.filter(w => matches(w, tag)).concat(ordered.filter(w => !matches(w, tag)));
  }

  // Compute target {r,c} for every work given current orientation + active tag.
  function computePositions() {
    const ordered = orderedForTag(activeTag);
    const pos = {};
    if (orientation === 'h') {
      cols = Math.max(1, Math.ceil(ordered.length / ROWS));
      ordered.forEach((w, i) => {
        const c = Math.floor(i / ROWS);
        const r = i % ROWS;
        pos[w.id] = { r, c };
      });
    } else {
      cols = isMobile() ? 2 : VERT_COLS;
      ordered.forEach((w, i) => {
        const r = Math.floor(i / cols);
        const c = i % cols;
        pos[w.id] = { r, c };
      });
    }
    return pos;
  }

  function rowsForGrid() {
    if (orientation === 'h') return ROWS;
    let maxR = 0;
    for (const id in positions) if (positions[id].r > maxR) maxR = positions[id].r;
    return maxR + 1;
  }

  function sizeGrid() {
    const m = metrics();
    const rows = rowsForGrid();
    grid.style.width  = (cols * m.cellW - m.gap) + 'px';
    grid.style.height = (rows * m.cellH - m.rowGap) + 'px';
  }

  // Scale tile size so ROWS rows fit the viewport height, and use that SAME
  // size in both orientations. In horizontal the three rows fill the height
  // (bottom row no longer clipped); in vertical the tiles keep the identical
  // size and just scroll down — so toggling only changes the scroll axis, with
  // no size jump. Caption height and column gap stay fixed. Reverts to the
  // responsive mobile sizing below the breakpoint.
  const BASE_TW = 320, BASE_TH = 248, BASE_CH = 46, MIN_TH = 120;
  function fitTiles() {
    if (isMobile()) {
      page.style.removeProperty('--tile-w');
      page.style.removeProperty('--tile-h');
      return;
    }
    const rowGap = parseFloat(getComputedStyle(page).getPropertyValue('--row-gap')) || 13;
    const usableH = viewport.clientHeight - 32; // viewport bottom padding
    let th = (usableH - ROWS * BASE_CH - (ROWS - 1) * rowGap) / ROWS;
    th = Math.max(MIN_TH, Math.min(BASE_TH, th));
    const tw = th * (BASE_TW / BASE_TH);
    page.style.setProperty('--tile-h', th + 'px');
    page.style.setProperty('--tile-w', tw + 'px');
  }

  // Snap every tile to its target position (no animation). Used on init/resize.
  function snapAll() {
    const m = metrics();
    works.forEach(w => {
      const el = grid.querySelector(`[data-id="${w.id}"]`);
      const p = positions[w.id];
      if (!el || !p) return;
      el.style.transform = `translate(${p.c * m.cellW}px, ${p.r * m.cellH}px)`;
      el.style.transition = 'none';
    });
  }

  function layout() {
    fitTiles();
    positions = computePositions();
    sizeGrid();
    snapAll();
    grid.classList.add('is-ready');
  }

  function render() {
    grid.innerHTML = '';
    works.forEach(w => {
      const el = document.createElement('div');
      el.className = 'll-tile';
      el.dataset.id = w.id;

      const imgWrap = document.createElement('div');
      imgWrap.className = 'll-img';
      if (w.image) {
        const img = document.createElement('img');
        const thumbName = w.image.replace(/^images\//, 'images/thumbs/').replace(/\.[^.]+$/, '.webp');
        img.src = `../assets/${thumbName}`;
        img.alt = w.title || '';
        img.loading = 'lazy';
        imgWrap.appendChild(img);
      }

      const cap = document.createElement('div');
      cap.className = 'll-caption';
      const parts = [w.title, w.dimensions, w.medium].filter(Boolean);
      cap.textContent = parts.join(' — ');

      el.appendChild(imgWrap);
      el.appendChild(cap);
      el.addEventListener('click', () => openLightbox(w.id));
      grid.appendChild(el);
    });
  }

  function renderFilters() {
    filtersEl.innerHTML = '';
    TAGS.forEach(t => {
      // Entries with `href` (e.g. About) render as a link out, styled like a
      // category but they don't filter — they navigate.
      if (t.href) {
        const link = document.createElement('a');
        link.className = 'll-filter';
        link.href = t.href;
        link.textContent = t.label;
        filtersEl.appendChild(link);
        return;
      }
      const btn = document.createElement('button');
      btn.className = 'll-filter' + (t.id === activeTag ? ' is-active' : '');
      btn.textContent = t.label;
      btn.addEventListener('click', () => setActiveTag(t.id));
      filtersEl.appendChild(btn);
    });
  }

  function applyDim() {
    works.forEach(w => {
      const el = grid.querySelector(`[data-id="${w.id}"]`);
      if (el) el.classList.toggle('is-dim', !matches(w, activeTag));
    });
  }

  function setActiveTag(tag) {
    activeTag = tag;
    filtersEl.querySelectorAll('.ll-filter').forEach((b, i) => {
      b.classList.toggle('is-active', TAGS[i].id === tag);
    });
    applyDim();
    reflow();
  }

  // ── Reflow: compute new positions, animate every tile to its target ──
  // Traffic-jam feel: stagger by distance from origin (top-left) so the front
  // of the pack moves first and the rear "catches up" — like a jam clearing.
  function reflow() {
    fitTiles();
    positions = computePositions();
    sizeGrid();
    const m = metrics();

    // Build per-tile target list paired with current position for stagger calc.
    const items = [];
    works.forEach(w => {
      const el = grid.querySelector(`[data-id="${w.id}"]`);
      const p = positions[w.id];
      if (!el || !p) return;
      items.push({ el, w, p, targetX: p.c * m.cellW, targetY: p.r * m.cellH });
    });

    // Sort by target position (row then col) so tiles destined for the top-left
    // start moving first and a "wave" propagates outward.
    items.sort((a, b) => (a.p.r - b.p.r) || (a.p.c - b.p.c));

    const REFLOW_DURATION = 900;  // ms
    const REFLOW_STAGGER  = 450;  // total stagger spread in ms
    
    items.forEach((it, i) => {
      const delay = (i / items.length) * REFLOW_STAGGER;
      it.el.style.transition = `transform ${REFLOW_DURATION}ms cubic-bezier(0.45, 0, 0.55, 1) ${delay}ms, opacity 220ms`;
      // Promote to a compositor layer only for the duration of this animation.
      it.el.style.willChange = 'transform';
      // Force reflow so the browser applies the transition
      void it.el.offsetHeight;
      it.el.style.transform = `translate(${it.targetX}px, ${it.targetY}px)`;
      // Once the move settles, drop will-change and the long transform-transition
      // so a resting/scrolling tile isn't a permanent layer and won't animate on
      // an incidental resize.
      const done = (e) => {
        if (e.propertyName !== 'transform') return;
        it.el.style.willChange = '';
        it.el.style.transition = '';
        it.el.removeEventListener('transitionend', done);
      };
      it.el.addEventListener('transitionend', done);
    });
  }

  // ── Wheel → horizontal scroll when in horizontal mode ──
  viewport.addEventListener('wheel', (e) => {
    if (orientation !== 'h') return;
    // Only redirect when there's actually room to scroll horizontally.
    if (viewport.scrollWidth <= viewport.clientWidth) return;
    // Use the larger of deltaY/deltaX so trackpad side-swipes still work.
    const dy = e.deltaY;
    const dx = e.deltaX;
    const delta = Math.abs(dy) > Math.abs(dx) ? dy : dx;
    if (delta === 0) return;
    viewport.scrollLeft += delta;
    e.preventDefault();
  }, { passive: false });

  // ── Orientation toggle ──
  orientEl.addEventListener('click', (e) => {
    const btn = e.target.closest('button[data-orient]');
    if (!btn) return;
    setOrientation(btn.dataset.orient);
  });

  function setOrientation(o) {
    if (orientation === o) return;
    orientation = o;
    applyOrientationClass();
    // Reset scroll so the wave starts from the visible corner.
    viewport.scrollLeft = 0;
    viewport.scrollTop = 0;
    reflow();
    applyDim();
  }

  // ── Lightbox: view a single work full-size ──
  // Navigation follows the on-screen order for the active filter (matched
  // first), so prev/next steps through works as they're laid out.
  let lbList = [];
  let lbIdx  = -1;

  function showLb() {
    const w = lbList[lbIdx];
    if (!w) return;
    lbImg.src = w.image ? `../assets/${w.image}` : '';
    lbImg.alt = w.title || '';
    const parts = [w.title, w.dimensions, w.medium, w.year].filter(Boolean);
    lbCap.textContent = parts.join(' — ');
  }
  function openLightbox(id) {
    lbList = orderedForTag(activeTag);
    lbIdx  = lbList.findIndex(w => w.id === id);
    if (lbIdx < 0) return;
    showLb();
    lightbox.classList.add('is-open');
    lightbox.setAttribute('aria-hidden', 'false');
  }
  function closeLightbox() {
    lightbox.classList.remove('is-open');
    lightbox.setAttribute('aria-hidden', 'true');
    lbImg.removeAttribute('src');
  }
  function stepLb(delta) {
    if (!lbList.length) return;
    lbIdx = (lbIdx + delta + lbList.length) % lbList.length;
    showLb();
  }

  document.getElementById('ll-lb-close').addEventListener('click', closeLightbox);
  document.getElementById('ll-lb-prev').addEventListener('click', () => stepLb(-1));
  document.getElementById('ll-lb-next').addEventListener('click', () => stepLb(1));
  // Click on the backdrop (but not the image or buttons) closes.
  lightbox.addEventListener('click', (e) => { if (e.target === lightbox) closeLightbox(); });
  document.addEventListener('keydown', (e) => {
    if (!lightbox.classList.contains('is-open')) return;
    if (e.key === 'Escape') closeLightbox();
    else if (e.key === 'ArrowLeft') stepLb(-1);
    else if (e.key === 'ArrowRight') stepLb(1);
  });

  // ── Boot ──
  applyOrientationClass();
  fetch('../assets/works.json', { cache: 'no-cache' })
    .then(r => r.json())
    .then(data => {
      works = data.works || [];
      renderFilters();
      render();
      layout();
      applyDim();
    })
    .catch(err => {
      grid.innerHTML = `<div style="padding:24px;color:#a00">Could not load works.json: ${err}</div>`;
    });

  let lastMobile = isMobile();
  let resizeRaf = null;
  window.addEventListener('resize', () => {
    const m = isMobile();
    if (m !== lastMobile) {
      lastMobile = m;
      setOrientation(m ? 'v' : 'h');
      return;
    }
    if (resizeRaf) cancelAnimationFrame(resizeRaf);
    resizeRaf = requestAnimationFrame(() => {
      // re-snap to current metric (CSS vars may have changed)
      fitTiles();
      positions = computePositions();
      sizeGrid();
      snapAll();
    });
  });

  // ── Smart filter wrapping to avoid overlap with orientation buttons ──
  function manageFilterWrapping() {
    const w = window.innerWidth;
    
    // Remove all existing break elements
    filtersEl.querySelectorAll('.ll-break').forEach(br => br.remove());
    
    // Only apply smart wrapping on narrow desktop (721px–1200px)
    if (w <= 720 || w > 1200) return;
    
    const barRect = document.querySelector('.ll-bar').getBoundingClientRect();
    const orientRect = orientEl.getBoundingClientRect();
    const availableWidth = barRect.width - orientRect.width - 32; // 32px gap
    
    const filters = Array.from(filtersEl.querySelectorAll('.ll-filter'));
    let currentRowWidth = 0;
    const gap = 16;
    
    filters.forEach((filter, i) => {
      const filterWidth = filter.getBoundingClientRect().width;
      
      if (i === 0) {
        currentRowWidth = filterWidth;
        return;
      }
      
      // Check if adding this filter would exceed available width
      if (currentRowWidth + gap + filterWidth > availableWidth) {
        // Insert line break before this filter
        const breakEl = document.createElement('div');
        breakEl.className = 'll-break';
        breakEl.style.cssText = 'width:100%;height:0;';
        filter.before(breakEl);
        currentRowWidth = filterWidth;
      } else {
        currentRowWidth += gap + filterWidth;
      }
    });
  }
  
  // Run on load (after filters are rendered) and on resize
  let wrapRaf = null;
  window.addEventListener('resize', () => {
    if (wrapRaf) cancelAnimationFrame(wrapRaf);
    wrapRaf = requestAnimationFrame(manageFilterWrapping);
  });
  
  // Initial call after filters render (wait a tick for widths to settle)
  setTimeout(manageFilterWrapping, 100);
})();
</script>
</html>