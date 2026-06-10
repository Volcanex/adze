/**
 * Adze Image Pipeline — texture-based speed rendering.
 * Reads window.__imagePipeline config, finds <img data-thumb="..."> elements,
 * renders a styled canvas placeholder instantly, then lazy-loads the full image.
 * Injected only into sites where the image-pipeline feature is enabled.
 */
(function () {
  'use strict';

  var cfg = window.__imagePipeline || {};
  var mode = cfg.mode || 'halftone';

  // ── Sampling helpers ──────────────────────────────────────────────────────

  function samplePixels(img) {
    var oc = document.createElement('canvas');
    oc.width = img.naturalWidth; oc.height = img.naturalHeight;
    oc.getContext('2d').drawImage(img, 0, 0);
    return { d: oc.getContext('2d').getImageData(0, 0, oc.width, oc.height).data, w: oc.width, h: oc.height };
  }

  function sample(px, u, v) {
    var x = Math.max(0, Math.min(px.w - 1, Math.round(u * (px.w - 1))));
    var y = Math.max(0, Math.min(px.h - 1, Math.round(v * (px.h - 1))));
    var i = (y * px.w + x) * 4;
    return { r: px.d[i], g: px.d[i + 1], b: px.d[i + 2] };
  }

  function luma(c) { return (c.r * 0.299 + c.g * 0.587 + c.b * 0.114) / 255; }

  function hexRgb(hex) {
    hex = (hex || '#000000').replace('#', '');
    if (hex.length === 3) hex = hex[0]+hex[0]+hex[1]+hex[1]+hex[2]+hex[2];
    return { r: parseInt(hex.slice(0,2),16), g: parseInt(hex.slice(2,4),16), b: parseInt(hex.slice(4,6),16) };
  }

  // ── Halftone (single-colour rotated dot grid) ─────────────────────────────

  function renderHalftone(ctx, W, H, px) {
    var cs   = cfg.cellSize || 10;
    var ang  = ((cfg.angle != null ? cfg.angle : 45) * Math.PI / 180);
    var ink  = cfg.inkColor   || '#1a1a1a';
    var bg   = cfg.paperColor || '#f4f0e8';

    ctx.fillStyle = bg;
    ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = ink;

    var cos = Math.cos(ang), sin = Math.sin(ang);
    var icos = Math.cos(-ang), isin = Math.sin(-ang);
    var diag = Math.ceil(Math.sqrt(W * W + H * H));
    var hw = W / 2, hh = H / 2;
    var span = Math.ceil(diag / cs) + 2;
    var off  = -Math.floor(span / 2);

    for (var i = off; i < off + span; i++) {
      for (var j = off; j < off + span; j++) {
        var lx = (i + 0.5) * cs, ly = (j + 0.5) * cs;
        var sx = lx * icos - ly * isin + hw;
        var sy = lx * isin + ly * icos + hh;
        if (sx < -cs || sx > W + cs || sy < -cs || sy > H + cs) continue;
        var col = sample(px, Math.max(0, Math.min(1, sx/W)), Math.max(0, Math.min(1, sy/H)));
        var r = Math.sqrt(1 - luma(col)) * cs * 0.65;
        if (r < 0.4) continue;
        var dx = lx * cos - ly * sin + hw;
        var dy = lx * sin + ly * cos + hh;
        ctx.beginPath(); ctx.arc(dx, dy, r, 0, 6.2832); ctx.fill();
      }
    }
  }

  // ── Duotone halftone (risograph-style, 2 colour channels at offset angles) ─

  function renderDuotone(ctx, W, H, px) {
    var cs  = cfg.cellSize || 10;
    var c1  = cfg.color1 || '#1a1a1a';
    var c2  = cfg.color2 || '#c0392b';
    var bg  = cfg.paperColor || '#f9f5ee';
    var a1  = ((cfg.angle1 != null ? cfg.angle1 : 45) * Math.PI / 180);
    var a2  = ((cfg.angle2 != null ? cfg.angle2 : 15) * Math.PI / 180);

    ctx.fillStyle = bg; ctx.fillRect(0, 0, W, H);
    ctx.globalCompositeOperation = 'multiply';

    [[a1, c1, function(c){ return luma(c); }],
     [a2, c2, function(c){ return 1 - luma(c); }]].forEach(function(ch) {
      var ang = ch[0], col = ch[1], ex = ch[2];
      var cos = Math.cos(ang), sin = Math.sin(ang);
      var icos = Math.cos(-ang), isin = Math.sin(-ang);
      var diag = Math.ceil(Math.sqrt(W*W+H*H));
      var hw = W/2, hh = H/2;
      var span = Math.ceil(diag/cs)+2, off = -Math.floor(span/2);
      ctx.fillStyle = col;
      for (var i = off; i < off+span; i++) {
        for (var j = off; j < off+span; j++) {
          var lx=(i+0.5)*cs, ly=(j+0.5)*cs;
          var sx=lx*icos-ly*isin+hw, sy=lx*isin+ly*icos+hh;
          if (sx<-cs||sx>W+cs||sy<-cs||sy>H+cs) continue;
          var density = ex(sample(px, Math.max(0,Math.min(1,sx/W)), Math.max(0,Math.min(1,sy/H))));
          var r = Math.sqrt(density) * cs * 0.65;
          if (r < 0.4) continue;
          var dx=lx*cos-ly*sin+hw, dy=lx*sin+ly*cos+hh;
          ctx.beginPath(); ctx.arc(dx, dy, r, 0, 6.2832); ctx.fill();
        }
      }
    });
    ctx.globalCompositeOperation = 'source-over';
  }

  // ── CMYK halftone (4-colour offset-litho simulation) ──────────────────────

  function renderCMYK(ctx, W, H, px) {
    var cs = cfg.cellSize || 9;
    ctx.fillStyle = cfg.paperColor || '#fffdf8';
    ctx.fillRect(0, 0, W, H);
    ctx.globalCompositeOperation = 'multiply';

    var channels = [
      { ang: cfg.cAngle != null ? +cfg.cAngle : 15, rgb: [0, 183, 235],   ex: function(c){ var k=1-Math.max(c.r,c.g,c.b)/255; return k===1?0:(1-c.r/255-k)/(1-k); } },
      { ang: cfg.mAngle != null ? +cfg.mAngle : 75, rgb: [236, 0, 140],   ex: function(c){ var k=1-Math.max(c.r,c.g,c.b)/255; return k===1?0:(1-c.g/255-k)/(1-k); } },
      { ang: cfg.yAngle != null ? +cfg.yAngle : 90, rgb: [255, 239, 0],   ex: function(c){ var k=1-Math.max(c.r,c.g,c.b)/255; return k===1?0:(1-c.b/255-k)/(1-k); } },
      { ang: cfg.kAngle != null ? +cfg.kAngle : 45, rgb: [20, 20, 20],    ex: function(c){ return 1-Math.max(c.r,c.g,c.b)/255; } },
    ];

    channels.forEach(function(ch) {
      var ang = ch.ang * Math.PI / 180;
      var cos=Math.cos(ang), sin=Math.sin(ang);
      var icos=Math.cos(-ang), isin=Math.sin(-ang);
      var diag=Math.ceil(Math.sqrt(W*W+H*H));
      var hw=W/2, hh=H/2;
      var span=Math.ceil(diag/cs)+2, off=-Math.floor(span/2);
      ctx.fillStyle='rgb('+ch.rgb[0]+','+ch.rgb[1]+','+ch.rgb[2]+')';
      for (var i=off; i<off+span; i++) {
        for (var j=off; j<off+span; j++) {
          var lx=(i+0.5)*cs, ly=(j+0.5)*cs;
          var sx=lx*icos-ly*isin+hw, sy=lx*isin+ly*icos+hh;
          if (sx<-cs||sx>W+cs||sy<-cs||sy>H+cs) continue;
          var density = ch.ex(sample(px, Math.max(0,Math.min(1,sx/W)), Math.max(0,Math.min(1,sy/H))));
          var r = Math.sqrt(Math.max(0, density)) * cs * 0.65;
          if (r < 0.4) continue;
          var dx=lx*cos-ly*sin+hw, dy=lx*sin+ly*cos+hh;
          ctx.beginPath(); ctx.arc(dx, dy, r, 0, 6.2832); ctx.fill();
        }
      }
    });
    ctx.globalCompositeOperation = 'source-over';
  }

  // ── Bayer ordered dither ──────────────────────────────────────────────────

  var BAYER = [[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]];

  function renderDither(ctx, W, H, px) {
    var bs  = cfg.blockSize || 6;
    var ink = hexRgb(cfg.inkColor   || '#1a1a1a');
    var bg  = hexRgb(cfg.paperColor || '#f4f0e8');
    var cols = Math.ceil(W/bs), rows = Math.ceil(H/bs);
    var id = ctx.createImageData(W, H), d = id.data;

    for (var j=0; j<rows; j++) {
      for (var i=0; i<cols; i++) {
        var c   = sample(px, (i+0.5)/cols, (j+0.5)/rows);
        var thr = BAYER[j%4][i%4] / 16;
        var col = (luma(c) <= thr) ? ink : bg;
        for (var dy=0; dy<bs && j*bs+dy<H; dy++) {
          for (var dx=0; dx<bs && i*bs+dx<W; dx++) {
            var idx = ((j*bs+dy)*W + (i*bs+dx))*4;
            d[idx]=col.r; d[idx+1]=col.g; d[idx+2]=col.b; d[idx+3]=255;
          }
        }
      }
    }
    ctx.putImageData(id, 0, 0);
  }

  // ── Bitmap (pixelated upscale) ────────────────────────────────────────────

  function renderBitmap(ctx, W, H, srcImg) {
    ctx.imageSmoothingEnabled = false;
    ctx.drawImage(srcImg, 0, 0, W, H);
  }

  // ── Progressive blur (classic LQIP) ───────────────────────────────────────

  function renderProgressive(ctx, W, H, srcImg) {
    var b = cfg.blur != null ? cfg.blur : 20;
    ctx.filter = 'blur('+b+'px)';
    var pad = b*2;
    ctx.drawImage(srcImg, -pad, -pad, W+pad*2, H+pad*2);
    ctx.filter = 'none';
  }

  // ── Render dispatcher ─────────────────────────────────────────────────────

  function render(canvas, thumbImg) {
    var ctx = canvas.getContext('2d');
    var W = canvas.width, H = canvas.height;
    // dither thumb is already a quantised indexed PNG — just upscale pixelated
    if (mode === 'bitmap' || mode === 'dither') {
      renderBitmap(ctx, W, H, thumbImg);
    } else if (mode === 'progressive') {
      renderProgressive(ctx, W, H, thumbImg);
    } else {
      var px = samplePixels(thumbImg);
      if      (mode === 'duotone') renderDuotone(ctx, W, H, px);
      else if (mode === 'cmyk')    renderCMYK(ctx, W, H, px);
      else                         renderHalftone(ctx, W, H, px);
    }
  }

  // ── ThumbMap lookup ───────────────────────────────────────────────────────
  // Resolve a thumb data URI for any img.src, even ones created at runtime
  // (gallery tiles, lightboxes). Keys in thumbMap are asset stems without
  // extension, e.g. 'images/foo'. We strip the page-relative prefix and
  // extension from the img src to match.

  function thumbForSrc(src) {
    if (!src || !cfg.thumbMap) return null;
    // Normalise: strip any leading '../' segments and 'assets/' prefix
    var s = src.replace(/^(\.\.\/)+/, '').replace(/^assets\//, '');
    // Strip extension
    var stem = s.replace(/\.[^/.]+$/, '');
    return cfg.thumbMap[stem] || null;
  }

  // ── DOM processing ─────────────────────────────────────────────────────────

  function processImg(img) {
    if (img.dataset.pipeline) return;
    var thumb_uri = img.dataset.thumb || thumbForSrc(img.getAttribute('src'));
    if (!thumb_uri) return;

    var origSrc = img.getAttribute('src') || '';
    // Don't process data URIs or our own placeholder swaps
    if (!origSrc || origSrc.startsWith('data:') || origSrc.startsWith('blob:')) return;

    img.dataset.pipeline = '1';

    var rect = img.getBoundingClientRect();
    var W = Math.round(rect.width)  || img.offsetWidth  || 800;
    var H = Math.round(rect.height) || img.offsetHeight || W;

    // Lock the rendered aspect ratio BEFORE swapping src, so any container
    // whose height depends on the image's natural size doesn't collapse.
    // (Has no effect when both width+height are already explicitly set.)
    if (W > 0 && H > 0) img.style.aspectRatio = W + '/' + H;

    // Swap to transparent 1×1 GIF — stops progressive top-down rendering.
    img.src = 'data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==';

    var thumb = new Image();
    thumb.onload = function () {
      if (W < 2 || H < 2) {
        rect = img.getBoundingClientRect();
        W = Math.round(rect.width) || 800;
        H = Math.round(rect.height) || Math.round(W * thumb.naturalHeight / Math.max(1, thumb.naturalWidth));
      }
      // Always render to a canvas at display size — ensures the placeholder has
      // the correct natural dimensions for width:auto/height:auto containers.
      var canvas = document.createElement('canvas');
      canvas.width = W; canvas.height = H;
      if (mode === 'dither' || mode === 'bitmap') {
        // Pixelated upscale of the already-processed thumb
        var ctx2 = canvas.getContext('2d');
        ctx2.imageSmoothingEnabled = false;
        ctx2.drawImage(thumb, 0, 0, W, H);
        img.style.imageRendering = 'pixelated';
      } else {
        render(canvas, thumb);
      }
      img.src = canvas.toDataURL('image/webp', 0.82);

      // Lazy-load the full image, fade in via an overlay so the original img
      // never goes transparent (which would flash the background colour).
      var obs = new IntersectionObserver(function (entries) {
        if (!entries[0].isIntersecting) return;
        obs.disconnect();
        var full = new Image();
        full.onload = function () {
          img.style.imageRendering = '';

          var txStyle  = cfg.transitionStyle  || 'crystallise';
          var txMs     = cfg.transitionSpeed != null ? +cfg.transitionSpeed : 750;
          var txBlur   = cfg.transitionBlur  != null ? +cfg.transitionBlur  : 12;
          var txEase   = cfg.transitionEasing || 'ease';

          // 'none' — instant swap, no overlay
          if (txStyle === 'none') {
            img.dataset.pipeline = '1';
            img.style.aspectRatio = '';
            img.src = full.src;
            setTimeout(function () { delete img.dataset.pipeline; }, 0);
            return;
          }

          var ir = img.getBoundingClientRect();
          var cs = window.getComputedStyle(img);
          var ov = new Image();
          ov.src = full.src;
          var tx = txMs + 'ms ' + txEase;

          // Build overlay CSS — sharp overlay (no blur), position:fixed so no
          // parent is mutated and no layout shifts occur.
          var ovCSS = [
            'position:fixed',
            'left:' + ir.left + 'px', 'top:' + ir.top + 'px',
            'width:' + ir.width + 'px', 'height:' + ir.height + 'px',
            'object-fit:' + (cs.objectFit || 'cover'),
            'object-position:' + (cs.objectPosition || 'center'),
            'pointer-events:none', 'z-index:9999',
            'margin:0', 'padding:0', 'border:0', 'display:block',
          ];

          if (txStyle === 'wipe-right') {
            ovCSS.push('clip-path:inset(0 100% 0 0)', 'opacity:1',
                       'transition:clip-path ' + tx);
          } else if (txStyle === 'wipe-down') {
            ovCSS.push('clip-path:inset(100% 0 0 0)', 'opacity:1',
                       'transition:clip-path ' + tx);
          } else if (txStyle === 'zoom') {
            ovCSS.push('opacity:0', 'transform:scale(0.96)', 'transform-origin:center',
                       'transition:opacity ' + tx + ',transform ' + tx);
          } else {
            // crystallise, fade — overlay fades in sharp; placeholder blurs out (crystallise)
            ovCSS.push('opacity:0', 'transition:opacity ' + tx);
          }

          ov.style.cssText = ovCSS.join(';');
          document.body.appendChild(ov);

          // Also animate the placeholder out for crystallise/zoom
          if (txStyle === 'crystallise' || txStyle === 'zoom') {
            img.style.transition = 'filter ' + tx;
            var outBlur = txStyle === 'crystallise' ? txBlur : Math.round(txBlur * 0.4);
            requestAnimationFrame(function () { img.style.filter = 'blur(' + outBlur + 'px)'; });
          }

          requestAnimationFrame(function () {
            if (txStyle === 'wipe-right') ov.style.clipPath = 'inset(0 0% 0 0)';
            else if (txStyle === 'wipe-down') ov.style.clipPath = 'inset(0% 0 0 0)';
            else if (txStyle === 'zoom') { ov.style.opacity = '1'; ov.style.transform = 'scale(1)'; }
            else ov.style.opacity = '1';
          });

          ov.addEventListener('transitionend', function () {
            img.dataset.pipeline = '1';
            img.style.filter = '';
            img.style.transition = '';
            img.style.aspectRatio = '';
            img.src = full.src;
            if (document.body.contains(ov)) document.body.removeChild(ov);
            setTimeout(function () { delete img.dataset.pipeline; }, 0);
          }, { once: true });
        };
        full.onerror = function () { img.style.imageRendering = ''; img.src = origSrc; };
        full.src = origSrc;
      }, { rootMargin: '300px' });
      obs.observe(img);
    };
    thumb.onerror = function () {};
    thumb.src = thumb_uri;
  }

  function init() {
    document.querySelectorAll('img').forEach(processImg);

    new MutationObserver(function (muts) {
      muts.forEach(function (m) {
        if (m.type === 'childList') {
          m.addedNodes.forEach(function (n) {
            if (n.tagName === 'IMG') processImg(n);
            else if (n.querySelectorAll) n.querySelectorAll('img').forEach(processImg);
          });
        }
        // Lightbox pattern: existing img whose src is changed by app code.
        // Guard: only act on real URL changes (not our own data: swaps).
        if (m.type === 'attributes' && m.target.tagName === 'IMG') {
          var src = m.target.getAttribute('src') || '';
          if (src && !src.startsWith('data:') && !src.startsWith('blob:') && !m.target.dataset.pipeline) {
            processImg(m.target);
          }
        }
      });
    }).observe(document.body, {
      childList: true, subtree: true,
      attributes: true, attributeFilter: ['src'],
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
