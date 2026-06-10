/* Loom — live page runtime.
 *
 * Injected by compile.py AFTER engine.js, alongside:
 *   <script>window.__loom = <trace> ;</script>
 * Mounts a fixed, full-bleed background canvas behind the page and renders the
 * trace with the shared engine (window.Loom). No-op if no trace / no engine.
 *
 * The trace is the source of truth; this file is just the "live" renderer of it.
 */
(function () {
  'use strict';
  const trace = window.__loom;
  if (!trace || !window.Loom || !(trace.nodes || []).length) return;

  // image/video source nodes store a portable asset path ("images/foo.png");
  // on the live site assets are served at the domain root (nginx aliases
  // /assets/ → the artist's compiled assets dir), so resolve there.
  if (window.Loom.setAssetResolver) {
    window.Loom.setAssetResolver(function (rel) {
      if (!rel || /^(https?:|data:|blob:|\/)/.test(rel)) return rel || '';
      return '/assets/' + String(rel).split('/').map(encodeURIComponent).join('/');
    });
  }

  function mount() {
    if (document.getElementById('loom-bg')) return;
    const cv = document.createElement('canvas');
    cv.id = 'loom-bg';
    cv.width = (trace.size && trace.size.w) || 360;
    cv.height = (trace.size && trace.size.h) || 360;
    cv.style.cssText = [
      'position:fixed', 'inset:0', 'width:100vw', 'height:100vh',
      'z-index:-1', 'pointer-events:none', 'object-fit:cover',
      'image-rendering:pixelate',
    ].join(';');
    document.body.insertBefore(cv, document.body.firstChild);

    let rt = window.Loom.mount(cv, trace);
    // pause when tab hidden — don't burn battery on a background
    document.addEventListener('visibilitychange', () => {
      if (!rt) return;
      if (document.hidden) rt.stop(); else rt.start();
    });
  }

  if (document.readyState === 'loading')
    document.addEventListener('DOMContentLoaded', mount);
  else mount();
})();
