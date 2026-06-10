/* Loom engine — the shared core.
 *
 * ONE engine renders a trace (see SCHEMA.md). Consumed by the editor preview
 * (widget.js fetches this file), the live page background (compile.py injects
 * it + features/loom.js), and (next bone) the baker.
 *
 * No build step, no deps. Exposes window.Loom. Canvas2d — the low-res-then-
 * upscale path IS the aesthetic. Adding a node = Loom.register(type, def).
 */
(function () {
  'use strict';
  if (window.Loom) return; // idempotent — editor + feature may both load it

  const REG = {};
  const register = (type, def) => { REG[type] = def; };
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const lerp = (a, b, t) => a + (b - a) * t;
  const smooth = (t) => t * t * (3 - 2 * t);
  const rnd = () => Math.random();

  // small helpers reused by procedural sources
  function ensureGrid(s, n) {
    if (s.grid) return s.grid;
    const g = new Float32Array(n * n);
    for (let i = 0; i < g.length; i++) g[i] = rnd();
    s.grid = g; s.gs = n; return g;
  }
  function vnoise(s, x, y) { // bilinear value noise on the unit grid, tiling
    const n = s.gs, g = s.grid;
    const xi = Math.floor(x), yi = Math.floor(y);
    const fx = smooth(x - xi), fy = smooth(y - yi);
    const at = (a, b) => g[((b % n + n) % n) * n + ((a % n + n) % n)];
    const top = lerp(at(xi, yi), at(xi + 1, yi), fx);
    const bot = lerp(at(xi, yi + 1), at(xi + 1, yi + 1), fx);
    return lerp(top, bot, fy);
  }
  function lowResPass(node, lr, fill) { // render into node.cx via a small offscreen, upscale nearest
    const { cx, cv } = node, w = cv.width, h = cv.height;
    const s = node.state;
    if (!s.lr || s.lr.width !== lr) {
      s.lr = document.createElement('canvas'); s.lr.width = lr; s.lr.height = lr;
      s.lcx = s.lr.getContext('2d', { willReadFrequently: true });
    }
    const img = s.lcx.getImageData(0, 0, lr, lr), d = img.data;
    fill(d, lr);
    s.lcx.putImageData(img, 0, 0);
    cx.imageSmoothingEnabled = false;
    cx.clearRect(0, 0, w, h);
    cx.drawImage(s.lr, 0, 0, lr, lr, 0, 0, w, h);
  }
  function hsl(d, i, h, s, l) { // write HSL (0..1 s/l, 0..360 h) into rgba buffer at i
    h = ((h % 360) + 360) % 360 / 360;
    const q = l < 0.5 ? l * (1 + s) : l + s - l * s, p = 2 * l - q;
    const hk = [h + 1 / 3, h, h - 1 / 3].map((t) => {
      t = (t + 1) % 1;
      if (t < 1 / 6) return p + (q - p) * 6 * t;
      if (t < 1 / 2) return q;
      if (t < 2 / 3) return p + (q - p) * (2 / 3 - t) * 6;
      return p;
    });
    d[i] = hk[0] * 255; d[i + 1] = hk[1] * 255; d[i + 2] = hk[2] * 255; d[i + 3] = 255;
  }

  // ── asset media (image/video sources pull from the artist's assets) ─────────
  // A trace stores a *portable* asset path (e.g. "images/foo.png"); the renderer
  // resolves it to a real URL via assetResolver. The editor points this at the
  // dashboard's asset-thumb route; the live page (features/loom.js) at /assets/.
  let assetResolver = (s) => s;            // default: identity (already a URL)
  const setAssetResolver = (fn) => { assetResolver = (typeof fn === 'function') ? fn : ((s) => s); };
  const resolveAsset = (s) => (s ? assetResolver(s) : '');

  // Media cache keyed by resolved URL so rebuilds (every param tweak in the
  // editor remounts) reuse one <img>/<video> instead of reloading — crucial so
  // a video doesn't restart on each edit.
  const mediaCache = {};
  function loadImage(url) {
    if (!url) return null;
    let m = mediaCache[url];
    if (!m) {
      m = { el: new Image(), ready: false };
      m.el.onload = () => { m.ready = true; };
      m.el.src = url; mediaCache[url] = m;
    }
    return m;
  }
  function loadVideo(url) {
    if (!url) return null;
    const key = 'v:' + url;
    let m = mediaCache[key];
    if (!m) {
      const v = document.createElement('video');
      v.muted = true; v.loop = true; v.autoplay = true; v.playsInline = true;
      v.setAttribute('playsinline', ''); v.src = url;
      const pr = v.play(); if (pr && pr.catch) pr.catch(() => {});
      m = { el: v }; mediaCache[key] = m;
    }
    return m;
  }
  // draw a loaded image/video into a w×h ctx honouring a fit mode + scale
  function drawFitted(cx, media, w, h, fit, scale) {
    scale = scale || 1;
    const iw = media.videoWidth || media.naturalWidth || media.width;
    const ih = media.videoHeight || media.naturalHeight || media.height;
    if (!iw || !ih) return;
    if (fit === 'tile') {
      const tw = iw * scale, th = ih * scale;
      for (let y = 0; y < h; y += th) for (let x = 0; x < w; x += tw) cx.drawImage(media, x, y, tw, th);
      return;
    }
    if (fit === 'stretch') { cx.drawImage(media, 0, 0, w, h); return; }
    const ir = iw / ih, cr = w / h, wider = ir > cr;
    let dw, dh;
    if (fit === 'cover') { if (wider) { dh = h; dw = h * ir; } else { dw = w; dh = w / ir; } }
    else /* contain */   { if (wider) { dw = w; dh = w / ir; } else { dh = h; dw = h * ir; } }
    dw *= scale; dh *= scale;
    cx.drawImage(media, (w - dw) / 2, (h - dh) / 2, dw, dh);
  }

  // ════════ SOURCES (no inlets — they generate a texture) ════════

  register('solid', {
    kind: 'source', inlets: [], cat: 'source',
    params: { color: { def: '#10101a', type: 'color' } },
    render(node, _i, p) { const { cx, cv } = node; cx.fillStyle = p.color; cx.fillRect(0, 0, cv.width, cv.height); },
  });

  register('gradient', {
    kind: 'source', inlets: [], cat: 'source',
    params: { angle: { def: 45, min: 0, max: 360 }, hue: { def: 280, min: 0, max: 360 }, spread: { def: 60, min: 0, max: 180 } },
    render(node, _i, p) {
      const { cx, cv } = node, w = cv.width, h = cv.height, a = p.angle * Math.PI / 180;
      const g = cx.createLinearGradient(0, 0, Math.cos(a) * w, Math.sin(a) * h);
      g.addColorStop(0, `hsl(${p.hue},70%,12%)`);
      g.addColorStop(1, `hsl(${(p.hue + p.spread) % 360},80%,55%)`);
      cx.fillStyle = g; cx.fillRect(0, 0, w, h);
    },
  });

  // The strange attractor — Lorenz, with persistent trails.
  register('lorenz', {
    kind: 'source', inlets: [], cat: 'source',
    params: { speed: { def: 1, min: 0.1, max: 4 }, hue: { def: 200, min: 0, max: 360 }, fade: { def: 0.08, min: 0.01, max: 0.4 } },
    render(node, _i, p, t) {
      const { cx, cv } = node, w = cv.width, h = cv.height, s = node.state;
      if (s.x === undefined) { s.x = 0.1; s.y = 0; s.z = 0; }
      cx.fillStyle = `rgba(8,8,14,${p.fade})`; cx.fillRect(0, 0, w, h);
      const sig = 10, rho = 28, beta = 8 / 3, steps = Math.round(18 * p.speed), dt = 0.006;
      cx.lineWidth = 1; cx.beginPath();
      for (let i = 0; i < steps; i++) {
        const dx = sig * (s.y - s.x), dy = s.x * (rho - s.z) - s.y, dz = s.x * s.y - beta * s.z;
        s.x += dx * dt; s.y += dy * dt; s.z += dz * dt;
        const px = w / 2 + s.x * (w / 60), py = h * 0.92 - s.z * (h / 55);
        i === 0 ? cx.moveTo(px, py) : cx.lineTo(px, py);
      }
      cx.strokeStyle = `hsl(${(p.hue + s.z * 4) % 360},90%,60%)`; cx.stroke();
    },
  });

  register('noise', {
    kind: 'source', inlets: [], cat: 'source',
    params: { scale: { def: 4, min: 1, max: 16 }, speed: { def: 0.3, min: 0, max: 2 }, hue: { def: 210, min: 0, max: 360 }, contrast: { def: 1.2, min: 0.4, max: 3 } },
    render(node, _i, p, t) {
      ensureGrid(node.state, 64);
      lowResPass(node, 128, (d, lr) => {
        const sc = p.scale, off = t * p.speed;
        for (let y = 0; y < lr; y++) for (let x = 0; x < lr; x++) {
          let n = vnoise(node.state, x / lr * sc + off, y / lr * sc) * 0.6
                + vnoise(node.state, x / lr * sc * 2.3 - off, y / lr * sc * 2.3) * 0.4;
          n = clamp((n - 0.5) * p.contrast + 0.5, 0, 1);
          hsl(d, (y * lr + x) * 4, p.hue + n * 40, 0.5, 0.12 + n * 0.6);
        }
      });
    },
  });

  register('plasma', {
    kind: 'source', inlets: [], cat: 'source',
    params: { freq: { def: 6, min: 1, max: 20 }, speed: { def: 1, min: 0, max: 4 }, hue: { def: 300, min: 0, max: 360 } },
    render(node, _i, p, t) {
      lowResPass(node, 120, (d, lr) => {
        const f = p.freq / lr, tt = t * p.speed;
        for (let y = 0; y < lr; y++) for (let x = 0; x < lr; x++) {
          const v = Math.sin(x * f + tt) + Math.sin(y * f - tt)
                  + Math.sin((x + y) * f * 0.7 + tt) + Math.sin(Math.hypot(x - lr / 2, y - lr / 2) * f - tt * 2);
          const n = (v + 4) / 8;
          hsl(d, (y * lr + x) * 4, p.hue + n * 120, 0.7, 0.25 + n * 0.4);
        }
      });
    },
  });

  register('cells', { // drifting Voronoi
    kind: 'source', inlets: [], cat: 'source',
    params: { count: { def: 14, min: 3, max: 40 }, drift: { def: 0.4, min: 0, max: 2 }, hue: { def: 30, min: 0, max: 360 }, edge: { def: 0.6, min: 0, max: 1 } },
    render(node, _i, p, t) {
      const s = node.state, N = Math.round(p.count);
      if (!s.seeds || s.seeds.length !== N) {
        s.seeds = Array.from({ length: N }, () => ({ x: rnd(), y: rnd(), vx: (rnd() - 0.5), vy: (rnd() - 0.5), h: rnd() * 60 }));
      }
      lowResPass(node, 96, (d, lr) => {
        const seeds = s.seeds.map((sd) => ({
          x: (sd.x + Math.sin(t * 0.2 * p.drift + sd.h) * 0.15) * lr,
          y: (sd.y + Math.cos(t * 0.23 * p.drift + sd.h) * 0.15) * lr, h: sd.h,
        }));
        for (let y = 0; y < lr; y++) for (let x = 0; x < lr; x++) {
          let d1 = 1e9, d2 = 1e9, hh = 0;
          for (const sd of seeds) {
            const dd = (sd.x - x) * (sd.x - x) + (sd.y - y) * (sd.y - y);
            if (dd < d1) { d2 = d1; d1 = dd; hh = sd.h; } else if (dd < d2) d2 = dd;
          }
          const border = clamp((Math.sqrt(d2) - Math.sqrt(d1)) / 6, 0, 1);
          const l = 0.15 + 0.5 * (1 - p.edge * (1 - border));
          hsl(d, (y * lr + x) * 4, p.hue + hh, 0.6, l);
        }
      });
    },
  });

  register('text', { // type as a texture — feed it through dither/glitch/feedback
    kind: 'source', inlets: [], cat: 'source',
    params: {
      text: { def: 'LOOM', type: 'text' },
      size: { def: 90, min: 8, max: 260 },
      hue: { def: 50, min: 0, max: 360 },
      weight: { def: 700, min: 100, max: 900 },
      bg: { def: '#0a0a12', type: 'color' },
    },
    render(node, _i, p) {
      const { cx, cv } = node, w = cv.width, h = cv.height;
      cx.fillStyle = p.bg; cx.fillRect(0, 0, w, h);
      cx.fillStyle = `hsl(${p.hue},85%,60%)`;
      cx.textAlign = 'center'; cx.textBaseline = 'middle';
      cx.font = `${Math.round(p.weight)} ${Math.round(p.size)}px Inter, system-ui, sans-serif`;
      const lines = String(p.text == null ? '' : p.text).split('\n');
      const lh = p.size * 1.05, y0 = h / 2 - (lines.length - 1) * lh / 2;
      lines.forEach((ln, i) => cx.fillText(ln, w / 2, y0 + i * lh));
    },
  });

  register('image', { // an asset image as a texture — feed it through vhs/dither/feedback
    kind: 'source', inlets: [], cat: 'source',
    params: {
      src: { def: '', type: 'asset', accept: 'image' },
      fit: { def: 'cover', type: 'select', options: ['cover', 'contain', 'stretch', 'tile'] },
      scale: { def: 1, min: 0.1, max: 3 },
    },
    render(node, _i, p) {
      const { cx, cv } = node, w = cv.width, h = cv.height;
      cx.clearRect(0, 0, w, h);
      const m = loadImage(resolveAsset(p.src));
      if (m && m.ready) drawFitted(cx, m.el, w, h, p.fit, p.scale);
    },
  });

  register('video', { // an asset video as a live texture (muted/looping)
    kind: 'source', inlets: [], cat: 'source',
    params: {
      src: { def: '', type: 'asset', accept: 'video' },
      fit: { def: 'cover', type: 'select', options: ['cover', 'contain', 'stretch', 'tile'] },
      speed: { def: 1, min: 0, max: 3 },
    },
    render(node, _i, p) {
      const { cx, cv } = node, w = cv.width, h = cv.height;
      cx.clearRect(0, 0, w, h);
      const m = loadVideo(resolveAsset(p.src));
      if (!m) return;
      const v = m.el;
      if (p.speed === 0) { if (!v.paused) v.pause(); }
      else { if (v.paused) { const pr = v.play(); if (pr && pr.catch) pr.catch(() => {}); } if (v.playbackRate !== p.speed) { try { v.playbackRate = p.speed; } catch (_) {} } }
      if (v.readyState >= 2) drawFitted(cx, v, w, h, p.fit, 1);
    },
  });

  // ════════ EFFECTS (one buffer inlet 'in') ════════

  register('dither', {
    kind: 'effect', inlets: ['in'], cat: 'effect',
    params: { blockSize: { def: 6, min: 2, max: 14 }, levels: { def: 4, min: 2, max: 8 } },
    render(node, inputs, p) {
      const { cx, cv } = node, w = cv.width, h = cv.height, src = inputs.in;
      if (!src) { cx.clearRect(0, 0, w, h); return; }
      const bs = Math.max(1, Math.round(p.blockSize)), sw = Math.max(1, Math.floor(w / bs)), sh = Math.max(1, Math.floor(h / bs));
      cx.imageSmoothingEnabled = true; cx.clearRect(0, 0, w, h); cx.drawImage(src, 0, 0, sw, sh);
      const img = cx.getImageData(0, 0, sw, sh), d = img.data, lv = Math.max(2, Math.round(p.levels)), step = 255 / (lv - 1);
      const B = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]];
      for (let y = 0; y < sh; y++) for (let x = 0; x < sw; x++) {
        const i = (y * sw + x) * 4, thr = (B[y & 3][x & 3] / 16 - 0.5) * step;
        for (let c = 0; c < 3; c++) d[i + c] = clamp(Math.round((d[i + c] + thr) / step) * step, 0, 255);
      }
      cx.putImageData(img, 0, 0);
      cx.imageSmoothingEnabled = false; cx.drawImage(cv, 0, 0, sw, sh, 0, 0, w, h);
    },
  });

  register('pixelate', {
    kind: 'effect', inlets: ['in'], cat: 'effect',
    params: { size: { def: 8, min: 2, max: 40 } },
    render(node, inputs, p) {
      const { cx, cv } = node, w = cv.width, h = cv.height, src = inputs.in;
      cx.clearRect(0, 0, w, h); if (!src) return;
      const bs = Math.max(1, Math.round(p.size)), sw = Math.max(1, Math.floor(w / bs)), sh = Math.max(1, Math.floor(h / bs));
      cx.imageSmoothingEnabled = true; cx.drawImage(src, 0, 0, sw, sh);
      cx.imageSmoothingEnabled = false; cx.drawImage(cv, 0, 0, sw, sh, 0, 0, w, h);
    },
  });

  register('blur', {
    kind: 'effect', inlets: ['in'], cat: 'effect',
    params: { radius: { def: 4, min: 0, max: 24 } },
    render(node, inputs, p) {
      const { cx, cv } = node, w = cv.width, h = cv.height, src = inputs.in;
      cx.clearRect(0, 0, w, h); if (!src) return;
      cx.filter = `blur(${p.radius}px)`; cx.drawImage(src, 0, 0, w, h); cx.filter = 'none';
    },
  });

  register('levels', {
    kind: 'effect', inlets: ['in'], cat: 'effect',
    params: { brightness: { def: 1, min: 0, max: 2 }, contrast: { def: 1, min: 0, max: 3 }, saturate: { def: 1, min: 0, max: 3 }, invert: { def: 0, min: 0, max: 1 } },
    render(node, inputs, p) {
      const { cx, cv } = node, w = cv.width, h = cv.height, src = inputs.in;
      cx.clearRect(0, 0, w, h); if (!src) return;
      cx.filter = `brightness(${p.brightness}) contrast(${p.contrast}) saturate(${p.saturate}) invert(${clamp(p.invert, 0, 1)})`;
      cx.drawImage(src, 0, 0, w, h); cx.filter = 'none';
    },
  });

  register('colorize', {
    kind: 'effect', inlets: ['in'], cat: 'effect',
    params: { hueShift: { def: 0, min: 0, max: 360 }, saturate: { def: 1.4, min: 0, max: 3 }, sepia: { def: 0, min: 0, max: 1 } },
    render(node, inputs, p) {
      const { cx, cv } = node, w = cv.width, h = cv.height, src = inputs.in;
      cx.clearRect(0, 0, w, h); if (!src) return;
      cx.filter = `sepia(${clamp(p.sepia, 0, 1)}) hue-rotate(${p.hueShift}deg) saturate(${p.saturate})`;
      cx.drawImage(src, 0, 0, w, h); cx.filter = 'none';
    },
  });

  register('grain', { // true per-pixel film grain
    kind: 'effect', inlets: ['in'], cat: 'effect',
    params: { amount: { def: 0.25, min: 0, max: 1 }, size: { def: 1, min: 1, max: 6 } },
    render(node, inputs, p) {
      const { cx, cv } = node, w = cv.width, h = cv.height, src = inputs.in;
      cx.clearRect(0, 0, w, h); if (!src) return;
      const bs = Math.max(1, Math.round(p.size));
      cx.imageSmoothingEnabled = bs === 1;
      cx.drawImage(src, 0, 0, Math.ceil(w / bs), Math.ceil(h / bs));
      const gw = Math.ceil(w / bs), gh = Math.ceil(h / bs);
      const img = cx.getImageData(0, 0, gw, gh), d = img.data, a = p.amount * 140;
      for (let i = 0; i < d.length; i += 4) {
        const n = (rnd() - 0.5) * a;
        d[i] = clamp(d[i] + n, 0, 255); d[i + 1] = clamp(d[i + 1] + n, 0, 255); d[i + 2] = clamp(d[i + 2] + n, 0, 255);
      }
      cx.putImageData(img, 0, 0);
      if (bs > 1) { cx.imageSmoothingEnabled = false; cx.drawImage(cv, 0, 0, gw, gh, 0, 0, w, h); }
    },
  });

  register('glitch', {
    kind: 'effect', inlets: ['in'], cat: 'effect',
    params: { amount: { def: 0.3, min: 0, max: 1 }, shift: { def: 12, min: 0, max: 60 } },
    render(node, inputs, p, t) {
      const { cx, cv } = node, w = cv.width, h = cv.height, src = inputs.in;
      cx.clearRect(0, 0, w, h); if (!src) return;
      cx.drawImage(src, 0, 0, w, h);
      const bands = Math.round(p.amount * 16);
      for (let b = 0; b < bands; b++) {
        const seed = Math.sin((b * 12.9898 + t * 7.13) * 43758.5453), frac = seed - Math.floor(seed);
        const y = Math.floor(frac * h), bh = 2 + Math.floor((seed * seed % 1) * (h / 12)), dx = Math.round((frac - 0.5) * 2 * p.shift);
        cx.drawImage(cv, 0, y, w, bh, dx, y, w, bh);
      }
    },
  });

  register('mirror', { // kaleidoscope-style symmetry
    kind: 'effect', inlets: ['in'], cat: 'effect',
    params: { mode: { def: 'quad', type: 'select', options: ['x', 'y', 'quad'] } },
    render(node, inputs, p) {
      const { cx, cv } = node, w = cv.width, h = cv.height, src = inputs.in;
      cx.clearRect(0, 0, w, h); if (!src) return;
      cx.drawImage(src, 0, 0, w / 2, h / 2 + (p.mode === 'x' ? h / 2 : 0), 0, 0, w / 2, p.mode === 'x' ? h : h / 2);
      cx.save();
      if (p.mode === 'x' || p.mode === 'quad') { cx.translate(w, 0); cx.scale(-1, 1); cx.drawImage(cv, 0, 0, w / 2, h, 0, 0, w / 2, h); cx.restore(); cx.save(); }
      if (p.mode === 'y' || p.mode === 'quad') {
        if (p.mode === 'y') cx.drawImage(src, 0, 0, w, h / 2, 0, 0, w, h / 2);
        cx.translate(0, h); cx.scale(1, -1); cx.drawImage(cv, 0, 0, w, h / 2, 0, 0, w, h / 2);
      }
      cx.restore();
    },
  });

  register('feedback', { // frame feedback — the classic TouchDesigner trails
    kind: 'effect', inlets: ['in'], cat: 'effect',
    params: { decay: { def: 0.92, min: 0.5, max: 0.99 }, zoom: { def: 1.01, min: 0.95, max: 1.1 }, rotate: { def: 0.4, min: -4, max: 4 }, mix: { def: 0.5, min: 0, max: 1 } },
    render(node, inputs, p) {
      const { cx, cv } = node, w = cv.width, h = cv.height, src = inputs.in, s = node.state;
      if (!s.prev) { s.prev = document.createElement('canvas'); s.prev.width = w; s.prev.height = h; s.pcx = s.prev.getContext('2d'); }
      cx.clearRect(0, 0, w, h);
      cx.save();
      cx.translate(w / 2, h / 2); cx.rotate(p.rotate * Math.PI / 180); cx.scale(p.zoom, p.zoom); cx.translate(-w / 2, -h / 2);
      cx.globalAlpha = p.decay; cx.drawImage(s.prev, 0, 0); cx.restore();
      if (src) { cx.globalAlpha = p.mix; cx.drawImage(src, 0, 0, w, h); }
      cx.globalAlpha = 1;
      s.pcx.clearRect(0, 0, w, h); s.pcx.drawImage(cv, 0, 0);
    },
  });

  // ── VHS family — analog tape / CRT degradation ──────────────────────────────

  register('vhs', { // the works: chroma bleed + scanlines + grain + tracking tears
    kind: 'effect', inlets: ['in'], cat: 'effect',
    params: {
      bleed: { def: 2, min: 0, max: 8 },          // RGB horizontal split (px)
      scanlines: { def: 0.4, min: 0, max: 1 },    // darken alternate rows
      noise: { def: 0.15, min: 0, max: 1 },       // tape grain
      tracking: { def: 0.3, min: 0, max: 1 },     // horizontal tear bands
    },
    render(node, inputs, p, t) {
      const { cx, cv } = node, w = cv.width, h = cv.height, src = inputs.in;
      cx.clearRect(0, 0, w, h); if (!src) return;
      cx.drawImage(src, 0, 0, w, h);
      const img = cx.getImageData(0, 0, w, h), d = img.data, s = d.slice();
      const sh = Math.round(p.bleed), grain = p.noise * 120, scan = p.scanlines * 0.55;
      for (let y = 0; y < h; y++) {
        const dark = scan > 0 && (y & 1) ? (1 - scan) : 1;
        for (let x = 0; x < w; x++) {
          const i = (y * w + x) * 4;
          const rx = x - sh < 0 ? 0 : (x - sh >= w ? w - 1 : x - sh);
          const bx = x + sh < 0 ? 0 : (x + sh >= w ? w - 1 : x + sh);
          let r = s[(y * w + rx) * 4], g = s[i + 1], b = s[(y * w + bx) * 4 + 2];
          if (grain) { const n = (rnd() - 0.5) * grain; r += n; g += n; b += n; }
          d[i] = clamp(r * dark, 0, 255); d[i + 1] = clamp(g * dark, 0, 255); d[i + 2] = clamp(b * dark, 0, 255);
        }
      }
      cx.putImageData(img, 0, 0);
      const bands = Math.round(p.tracking * 10);
      for (let b = 0; b < bands; b++) {
        const seed = Math.sin((b * 78.233 + t * 3.1) * 43758.5453), frac = seed - Math.floor(seed);
        const y = Math.floor(frac * h), bh = 1 + Math.floor((seed * seed % 1) * 9), dx = Math.round((frac - 0.5) * 2 * p.tracking * 28);
        cx.drawImage(cv, 0, y, w, bh, dx, y, w, bh);
      }
    },
  });

  register('scanlines', { // CRT lines + vignette — gentler than full vhs
    kind: 'effect', inlets: ['in'], cat: 'effect',
    params: { gap: { def: 2, min: 1, max: 8 }, depth: { def: 0.5, min: 0, max: 1 }, vignette: { def: 0.4, min: 0, max: 1 } },
    render(node, inputs, p) {
      const { cx, cv } = node, w = cv.width, h = cv.height, src = inputs.in;
      cx.clearRect(0, 0, w, h); if (!src) return;
      cx.drawImage(src, 0, 0, w, h);
      const gap = Math.max(1, Math.round(p.gap));
      cx.globalCompositeOperation = 'multiply';
      cx.fillStyle = `rgba(0,0,0,${clamp(p.depth, 0, 1)})`;
      for (let y = 0; y < h; y += gap) cx.fillRect(0, y, w, 1);
      if (p.vignette > 0) {
        const g = cx.createRadialGradient(w / 2, h / 2, h * 0.3, w / 2, h / 2, h * 0.78);
        g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, `rgba(0,0,0,${clamp(p.vignette, 0, 1)})`);
        cx.fillStyle = g; cx.fillRect(0, 0, w, h);
      }
      cx.globalCompositeOperation = 'source-over';
    },
  });

  register('chromashift', { // pure RGB split at an angle — patch an LFO into amount
    kind: 'effect', inlets: ['in'], cat: 'effect',
    params: { amount: { def: 3, min: 0, max: 24 }, angle: { def: 0, min: 0, max: 360 } },
    render(node, inputs, p) {
      const { cx, cv } = node, w = cv.width, h = cv.height, src = inputs.in;
      cx.clearRect(0, 0, w, h); if (!src) return;
      cx.drawImage(src, 0, 0, w, h);
      const a = p.angle * Math.PI / 180, ox = Math.round(Math.cos(a) * p.amount), oy = Math.round(Math.sin(a) * p.amount);
      if (!ox && !oy) return;
      const img = cx.getImageData(0, 0, w, h), d = img.data, s = d.slice();
      for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
        const i = (y * w + x) * 4;
        const rx = clamp(x - ox, 0, w - 1), ry = clamp(y - oy, 0, h - 1);
        const bx = clamp(x + ox, 0, w - 1), by = clamp(y + oy, 0, h - 1);
        d[i] = s[(ry * w + rx) * 4]; d[i + 2] = s[(by * w + bx) * 4 + 2];
      }
      cx.putImageData(img, 0, 0);
    },
  });

  // ════════ COMPOSITE (two buffer inlets a, b) ════════

  register('blend', {
    kind: 'effect', inlets: ['a', 'b'], cat: 'composite',
    params: { mode: { def: 'screen', type: 'select', options: ['screen', 'multiply', 'overlay', 'lighter', 'difference', 'soft-light'] }, mix: { def: 1, min: 0, max: 1 } },
    render(node, inputs, p) {
      const { cx, cv } = node, w = cv.width, h = cv.height;
      cx.clearRect(0, 0, w, h);
      if (inputs.a) cx.drawImage(inputs.a, 0, 0, w, h);
      if (inputs.b) { cx.globalCompositeOperation = p.mode; cx.globalAlpha = p.mix; cx.drawImage(inputs.b, 0, 0, w, h); cx.globalCompositeOperation = 'source-over'; cx.globalAlpha = 1; }
    },
  });

  // ════════ MODULATORS (emit a scalar 0..1 via sample(); patch into params) ════════

  register('lfo', {
    kind: 'modulator', inlets: [], cat: 'modulator',
    params: { shape: { def: 'sine', type: 'select', options: ['sine', 'saw', 'tri', 'square'] }, freq: { def: 0.25, min: 0.01, max: 4 }, phase: { def: 0, min: 0, max: 1 } },
    sample(p, t) {
      const ph = (t * p.freq + p.phase) % 1;
      if (p.shape === 'saw') return ph;
      if (p.shape === 'tri') return 1 - Math.abs(2 * ph - 1);
      if (p.shape === 'square') return ph < 0.5 ? 1 : 0;
      return 0.5 + 0.5 * Math.sin(2 * Math.PI * ph);
    },
  });

  register('noisemod', { // smooth random — interpolated value noise over time
    kind: 'modulator', inlets: [], cat: 'modulator',
    params: { freq: { def: 0.4, min: 0.01, max: 4 } },
    sample(p, t) {
      const s = this._s || (this._s = {});
      if (!s.arr) { s.arr = Array.from({ length: 32 }, () => rnd()); }
      const pos = t * p.freq, i = Math.floor(pos) % s.arr.length, f = smooth(pos - Math.floor(pos));
      return lerp(s.arr[i], s.arr[(i + 1) % s.arr.length], f);
    },
  });

  register('pulse', { // gate that's high for `width` of each cycle
    kind: 'modulator', inlets: [], cat: 'modulator',
    params: { freq: { def: 0.5, min: 0.01, max: 6 }, width: { def: 0.3, min: 0.02, max: 0.98 } },
    sample(p, t) { return ((t * p.freq) % 1) < p.width ? 1 : 0; },
  });

  // ════════ OUTPUT (the sink) ════════
  register('output', { kind: 'output', inlets: ['in'], cat: 'output', params: {}, render() {} });

  // ── Compile: validate + topo-sort the buffer graph ─────────────────────────
  function compile(graph) {
    const nodes = {};
    for (const n of (graph.nodes || [])) {
      const def = REG[n.type]; if (!def) { console.warn('[loom] unknown node', n.type); continue; }
      nodes[n.id] = { ...n, def, state: {} };
    }
    const w = (graph.size && graph.size.w) || 360, h = (graph.size && graph.size.h) || 360;
    for (const id in nodes) {
      const nd = nodes[id]; if (nd.def.kind === 'modulator') continue;
      nd.cv = document.createElement('canvas'); nd.cv.width = w; nd.cv.height = h;
      nd.cx = nd.cv.getContext('2d', { willReadFrequently: true });
    }
    const edges = graph.edges || [];
    const bufferEdges = edges.filter((e) => e.kind !== 'control' && nodes[e.from[0]] && nodes[e.to[0]]);
    const controlEdges = edges.filter((e) => e.kind === 'control' && nodes[e.from[0]] && nodes[e.to[0]]);
    const order = [], visited = {}, temp = {};
    const incoming = (id) => bufferEdges.filter((e) => e.to[0] === id);
    function visit(id) {
      if (visited[id] || !nodes[id]) return;
      if (temp[id]) { console.warn('[loom] cycle at', id); return; }
      temp[id] = true; for (const e of incoming(id)) visit(e.from[0]); temp[id] = false; visited[id] = true; order.push(id);
    }
    for (const id in nodes) if (nodes[id].def.kind !== 'modulator') visit(id);
    const outputId = order.find((id) => nodes[id].def.kind === 'output');
    return { nodes, order, bufferEdges, controlEdges, outputId, w, h, fps: graph.fps != null ? graph.fps : 30 };
  }

  function resolveParams(prog, node, t) {
    const p = {};
    for (const k in (node.def.params || {})) p[k] = (node.params && node.params[k] != null) ? node.params[k] : node.def.params[k].def;
    for (const e of prog.controlEdges) {
      if (e.to[0] !== node.id) continue;
      const mod = prog.nodes[e.from[0]]; if (!mod || mod.def.kind !== 'modulator') continue;
      const s = mod.def.sample(resolveParams(prog, mod, t), t);
      const pd = node.def.params[e.to[1]] || {}, range = e.range || [pd.min != null ? pd.min : 0, pd.max != null ? pd.max : 1];
      p[e.to[1]] = lerp(range[0], range[1], clamp(s, 0, 1));
    }
    return p;
  }

  // ── Runtime ────────────────────────────────────────────────────────────────
  class Runtime {
    constructor(target, graph) { this.target = target; this.tx = target.getContext('2d'); this.prog = compile(graph); this.t0 = null; this.raf = null; this.lastDraw = 0; }
    frame(t) {
      const prog = this.prog;
      for (const id of prog.order) {
        const nd = prog.nodes[id]; if (nd.def.kind === 'output') continue;
        const inputs = {};
        for (const e of prog.bufferEdges) if (e.to[0] === id) { const up = prog.nodes[e.from[0]]; if (up) inputs[e.to[1]] = up.cv; }
        nd.def.render(nd, inputs, resolveParams(prog, nd, t), t);
      }
      const out = prog.nodes[prog.outputId];
      this.tx.imageSmoothingEnabled = false; this.tx.clearRect(0, 0, this.target.width, this.target.height);
      if (out) {
        const fe = prog.bufferEdges.find((e) => e.to[0] === out.id);
        const src = fe && prog.nodes[fe.from[0]] && prog.nodes[fe.from[0]].cv;
        if (src) this.tx.drawImage(src, 0, 0, this.target.width, this.target.height);
      }
    }
    loop(now) {
      if (this.t0 == null) this.t0 = now;
      const t = (now - this.t0) / 1000, interval = this.prog.fps > 0 ? 1000 / this.prog.fps : Infinity;
      if (now - this.lastDraw >= interval || this.prog.fps === 0) { this.frame(t); this.lastDraw = now; }
      if (this.prog.fps !== 0) this.raf = requestAnimationFrame(this.loop.bind(this));
    }
    start() { this.stop(); this.raf = requestAnimationFrame(this.loop.bind(this)); return this; }
    stop() { if (this.raf) cancelAnimationFrame(this.raf); this.raf = null; this.t0 = null; this.lastDraw = 0; }
  }

  // metadata helpers for the editor (ports per node type)
  function ports(type) {
    const def = REG[type]; if (!def) return { inlets: [], hasOut: false, outKind: null, params: {} };
    return {
      inlets: def.inlets || [],
      hasOut: def.kind !== 'output',
      outKind: def.kind === 'modulator' ? 'control' : 'buffer',
      params: def.params || {},
      kind: def.kind, cat: def.cat || def.kind,
    };
  }
  // modulatable params = numeric (have min/max), not selects/colors
  function modTargets(type) {
    const def = REG[type]; if (!def) return [];
    return Object.keys(def.params || {}).filter((k) => def.params[k].min != null);
  }

  window.Loom = {
    register, compile, Runtime, REG, ports, modTargets, setAssetResolver,
    types: () => Object.keys(REG),
    mount(target, graph) { return new Runtime(target, graph).start(); },
    starter() {
      return {
        version: 1, size: { w: 360, h: 360 }, fps: 30,
        nodes: [
          { id: 'src', type: 'lorenz', x: 40, y: 60, params: { speed: 1, hue: 200, fade: 0.08 } },
          { id: 'lfo', type: 'lfo', x: 40, y: 280, params: { shape: 'sine', freq: 0.15 } },
          { id: 'dith', type: 'dither', x: 320, y: 60, params: { blockSize: 6, levels: 4 } },
          { id: 'out', type: 'output', x: 600, y: 60, params: {} },
        ],
        edges: [
          { from: ['src', 'out'], to: ['dith', 'in'], kind: 'buffer' },
          { from: ['dith', 'out'], to: ['out', 'in'], kind: 'buffer' },
          { from: ['lfo', 'out'], to: ['dith', 'blockSize'], kind: 'control', range: [3, 12] },
        ],
      };
    },
  };
})();
