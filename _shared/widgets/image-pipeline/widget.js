// Widget: Image Pipeline
// Configure texture-based speed rendering for this artist's site.

(function (ctx) {
  const c = ctx.container;
  c.style.cssText = 'display:flex;flex-direction:column;flex:1;min-height:0;overflow:hidden;';

  // ── Mode definitions ──────────────────────────────────────────────────────

  const MODES = [
    { id: 'halftone',    label: 'Halftone',     desc: 'Classic dot-grid — single colour at a rotated angle.' },
    { id: 'duotone',     label: 'Duotone',      desc: 'Risograph-style — two overlapping colour channels.' },
    { id: 'cmyk',        label: 'CMYK',          desc: 'Four-colour offset litho simulation with rosette.' },
    { id: 'dither',      label: 'Dither',        desc: 'Bayer ordered dithering — zine / retro pixel look.' },
    { id: 'bitmap',      label: 'Bitmap',        desc: 'Raw pixelated upscale from the micro-thumbnail.' },
    { id: 'progressive', label: 'Blur fade',     desc: 'Classic LQIP — blurred placeholder that sharpens in.' },
  ];

  const MODE_PARAMS = {
    halftone:    ['cellSize','angle','inkColor','paperColor'],
    duotone:     ['cellSize','angle1','angle2','color1','color2','paperColor'],
    cmyk:        ['cellSize','paperColor'],
    dither:      ['colorDepth','paletteType','ditherAlgo','blockSize'],
    bitmap:      [],
    progressive: ['blur'],
  };

  const PARAM_META = {
    cellSize:        { label: 'Cell size',      type: 'range',  min: 2,  max: 20, step: 1, def: 10 },
    angle:           { label: 'Grid angle',     type: 'range',  min: 0,  max: 90, step: 1, def: 45 },
    angle1:          { label: 'Angle 1',        type: 'range',  min: 0,  max: 90, step: 1, def: 45 },
    angle2:          { label: 'Angle 2',        type: 'range',  min: 0,  max: 90, step: 1, def: 15 },
    inkColor:        { label: 'Ink',            type: 'color',  def: '#1a1a1a' },
    paperColor:      { label: 'Paper',          type: 'color',  def: '#f4f0e8' },
    color1:          { label: 'Colour 1',       type: 'color',  def: '#1a1a1a' },
    color2:          { label: 'Colour 2',       type: 'color',  def: '#c0392b' },
    blockSize:       { label: 'Display scale',  type: 'range',  min: 2,  max: 16, step: 1, def: 6 },
    blur:            { label: 'Blur amount',    type: 'range',  min: 4,  max: 40, step: 1, def: 20 },
    colorDepth:  { label: 'Colour depth',   type: 'select', def: '4',
      options: [
        { v: '1', l: '1-bit  —  2 colours' },
        { v: '2', l: '2-bit  —  4 colours' },
        { v: '3', l: '3-bit  —  8 colours' },
        { v: '4', l: '4-bit  —  16 colours' },
        { v: '6', l: '6-bit  —  64 colours' },
        { v: '8', l: '8-bit  —  256 colours' },
      ]
    },
    paletteType: { label: 'Palette',        type: 'select', def: 'auto',
      options: [
        { v: 'auto',      l: 'Auto  (from image)' },
        { v: 'grayscale', l: 'Greyscale' },
      ]
    },
    ditherAlgo:  { label: 'Dithering',      type: 'select', def: 'floyd-steinberg',
      options: [
        { v: 'floyd-steinberg', l: 'Floyd-Steinberg' },
        { v: 'none',            l: 'None  (hard edges)' },
      ]
    },
  };

  // Transition params are mode-independent
  const TX_PARAMS = ['transitionStyle', 'transitionSpeed', 'transitionBlur'];
  const TX_META = {
    transitionStyle: { label: 'Style', type: 'select', def: 'crystallise',
      options: [
        { v: 'crystallise', l: 'Crystallise — blur resolves in' },
        { v: 'fade',        l: 'Fade — opacity only' },
        { v: 'none',        l: 'None — instant swap' },
      ]
    },
    transitionSpeed: { label: 'Speed', type: 'select', def: '750',
      options: [
        { v: '350',  l: 'Fast  (0.35s)' },
        { v: '750',  l: 'Medium  (0.75s)' },
        { v: '1400', l: 'Slow  (1.4s)' },
      ]
    },
    transitionBlur: { label: 'Blur', type: 'range', min: 2, max: 30, step: 1, def: 12 },
  };

  // ── State ─────────────────────────────────────────────────────────────────

  let currentCfg = null;   // null = feature disabled
  let previewSrc = null;   // currently selected preview image URL
  let saving = false;

  // ── Render ────────────────────────────────────────────────────────────────

  c.innerHTML = `
  <div style="flex:1;overflow-y:auto;">
    <div style="max-width:760px;margin:0 auto;padding:24px;">

      <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:20px;">
        <div>
          <h3 style="margin:0 0 3px;font-family:var(--heading-font);font-weight:400;font-style:italic;font-size:16px;">Image Pipeline</h3>
          <p style="color:var(--text2);font-size:10px;margin:0;">Texture-based speed rendering · per-site opt-in</p>
        </div>
        <label style="display:flex;align-items:center;gap:8px;cursor:pointer;font-size:11px;color:var(--text2);">
          <span id="pip-toggle-label">Off</span>
          <input type="checkbox" id="pip-toggle" style="width:14px;height:14px;cursor:pointer;">
        </label>
      </div>

      <div id="pip-body" style="display:none;">

        <!-- Mode selector -->
        <div style="margin-bottom:20px;">
          <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:var(--text2);margin-bottom:8px;">Mode</div>
          <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;" id="pip-modes"></div>
        </div>

        <!-- Params + preview side by side -->
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">

          <!-- Params -->
          <div>
            <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:var(--text2);margin-bottom:8px;">Parameters</div>
            <div id="pip-params" style="display:flex;flex-direction:column;gap:10px;"></div>
          </div>

          <!-- Preview -->
          <div>
            <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:var(--text2);margin-bottom:8px;">Preview</div>
            <div style="position:relative;background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);overflow:hidden;aspect-ratio:4/3;">
              <canvas id="pip-canvas" style="width:100%;height:100%;display:block;"></canvas>
              <div id="pip-no-preview" style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:11px;color:var(--text2);">
                Pick an image below
              </div>
            </div>
            <div style="display:flex;gap:6px;margin-top:8px;">
              <select id="pip-img-select" style="flex:1;padding:5px 8px;font-size:10px;border:1px solid var(--border);border-radius:var(--radius);background:var(--surface);color:var(--text);">
                <option value="">— pick a preview image —</option>
              </select>
              <button id="pip-play" title="Play transition" style="padding:5px 10px;font-size:11px;border:1px solid var(--border);border-radius:var(--radius);background:var(--surface);color:var(--text2);cursor:pointer;">▶</button>
            </div>
          </div>

        </div>

        <!-- Transition params -->
        <div style="margin-top:20px;padding-top:16px;border-top:1px solid var(--border);">
          <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:var(--text2);margin-bottom:10px;">Transition</div>
          <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;" id="pip-tx-params"></div>
        </div>

        <!-- Actions -->
        <div style="display:flex;gap:8px;margin-top:20px;align-items:center;">
          <button id="pip-save" style="padding:6px 18px;font-size:11px;border:1px solid var(--accent);border-radius:var(--radius);background:var(--accent);color:var(--accent-text);cursor:pointer;font-weight:600;">
            Save &amp; Recompile
          </button>
          <span id="pip-status" style="font-size:10px;color:var(--text2);"></span>
        </div>

      </div>

      <!-- Disabled state -->
      <div id="pip-off-msg" style="font-size:11px;color:var(--text2);padding:8px 0;">
        Enable above to configure how images load on this site.
        When active, a small script is injected at compile time — no effect on sites that don't opt in.
      </div>

    </div>
  </div>`;

  // ── Helpers ───────────────────────────────────────────────────────────────

  function getCfg() {
    const mode = document.querySelector('#pip-modes .pip-mode-btn.active')?.dataset.mode || 'halftone';
    const cfg = { mode };
    // Mode-specific params
    (MODE_PARAMS[mode] || []).forEach(p => {
      const meta = PARAM_META[p];
      const el = document.getElementById('pip-p-' + p);
      if (!el) return;
      cfg[p] = meta.type === 'range' ? +el.value : el.value;
    });
    // Transition params
    TX_PARAMS.forEach(p => {
      const meta = TX_META[p];
      const el = document.getElementById('pip-tx-' + p);
      if (!el) return;
      cfg[p] = meta.type === 'range' ? +el.value : el.value;
    });
    return cfg;
  }

  function buildTxParams(existingCfg) {
    const wrap = document.getElementById('pip-tx-params');
    wrap.innerHTML = '';
    TX_PARAMS.forEach(p => {
      const meta = TX_META[p];
      const val  = existingCfg?.[p] != null ? existingCfg[p] : meta.def;
      const row  = document.createElement('div');
      if (meta.type === 'range') {
        row.innerHTML = `
          <label style="font-size:10px;color:var(--text2);display:flex;justify-content:space-between;">
            <span>${meta.label}</span><span id="pip-tx-${p}-val">${val}</span>
          </label>
          <input id="pip-tx-${p}" type="range" min="${meta.min}" max="${meta.max}" step="${meta.step}" value="${val}"
            style="width:100%;margin-top:3px;accent-color:var(--accent);">`;
        row.querySelector('input').oninput = function () {
          document.getElementById('pip-tx-' + p + '-val').textContent = this.value;
        };
      } else {
        const opts = meta.options.map(o =>
          `<option value="${o.v}"${String(val) === String(o.v) ? ' selected' : ''}>${o.l}</option>`
        ).join('');
        row.innerHTML = `
          <label style="font-size:10px;color:var(--text2);display:block;margin-bottom:3px;">${meta.label}</label>
          <select id="pip-tx-${p}" style="width:100%;padding:3px 6px;font-size:10px;border:1px solid var(--border);border-radius:var(--radius);background:var(--surface);color:var(--text);">${opts}</select>`;
      }
      wrap.appendChild(row);
    });
    // Show/hide blur slider based on style
    function syncBlurVisibility() {
      const style = document.getElementById('pip-tx-transitionStyle')?.value;
      const blurRow = document.getElementById('pip-tx-transitionBlur')?.parentNode;
      if (blurRow) blurRow.style.opacity = style === 'crystallise' ? '1' : '0.35';
    }
    syncBlurVisibility();
    document.getElementById('pip-tx-transitionStyle')?.addEventListener('change', syncBlurVisibility);
  }

  function buildModes(activeModeId) {
    const grid = document.getElementById('pip-modes');
    grid.innerHTML = '';
    MODES.forEach(m => {
      const btn = document.createElement('button');
      btn.className = 'pip-mode-btn' + (m.id === activeModeId ? ' active' : '');
      btn.dataset.mode = m.id;
      btn.style.cssText = 'padding:8px 10px;font-size:11px;border-radius:var(--radius);cursor:pointer;text-align:left;transition:border-color 0.15s,background 0.15s;';
      btn.style.border    = m.id === activeModeId ? '1px solid var(--accent)' : '1px solid var(--border)';
      btn.style.background = m.id === activeModeId ? 'var(--accent)' : 'var(--surface)';
      btn.style.color      = m.id === activeModeId ? 'var(--accent-text)' : 'var(--text)';
      btn.innerHTML = `<div style="font-weight:600;margin-bottom:2px;">${m.label}</div><div style="font-size:9px;opacity:0.75;line-height:1.3;">${m.desc}</div>`;
      btn.onclick = () => { selectMode(m.id); };
      grid.appendChild(btn);
    });
  }

  function buildParams(modeId, existingCfg) {
    const wrap = document.getElementById('pip-params');
    wrap.innerHTML = '';
    const params = MODE_PARAMS[modeId] || [];
    if (params.length === 0) {
      wrap.innerHTML = '<p style="font-size:10px;color:var(--text2);">No parameters for this mode.</p>';
      return;
    }
    params.forEach(p => {
      const meta = PARAM_META[p];
      const val  = existingCfg?.[p] != null ? existingCfg[p] : meta.def;
      const row  = document.createElement('div');

      if (meta.type === 'range') {
        row.innerHTML = `
          <label style="font-size:10px;color:var(--text2);display:flex;justify-content:space-between;">
            <span>${meta.label}</span>
            <span id="pip-p-${p}-val">${val}</span>
          </label>
          <input id="pip-p-${p}" type="range" min="${meta.min}" max="${meta.max}" step="${meta.step}" value="${val}"
            style="width:100%;margin-top:3px;accent-color:var(--accent);">`;
        row.querySelector('input').oninput = function () {
          document.getElementById('pip-p-' + p + '-val').textContent = this.value;
          debouncePreview();
        };
      } else if (meta.type === 'select') {
        const opts = meta.options.map(o =>
          `<option value="${o.v}"${String(val) === String(o.v) ? ' selected' : ''}>${o.l}</option>`
        ).join('');
        row.innerHTML = `
          <label style="font-size:10px;color:var(--text2);display:flex;justify-content:space-between;align-items:center;gap:8px;">
            <span style="flex-shrink:0;">${meta.label}</span>
            <select id="pip-p-${p}" style="flex:1;padding:3px 6px;font-size:10px;border:1px solid var(--border);border-radius:var(--radius);background:var(--surface);color:var(--text);">${opts}</select>
          </label>`;
        row.querySelector('select').onchange = () => debouncePreview();
      } else {
        row.innerHTML = `
          <label style="font-size:10px;color:var(--text2);display:flex;justify-content:space-between;align-items:center;">
            <span>${meta.label}</span>
            <input id="pip-p-${p}" type="color" value="${val}" style="width:36px;height:22px;border:none;background:none;cursor:pointer;padding:0;">
          </label>`;
        row.querySelector('input').oninput = () => debouncePreview();
      }
      wrap.appendChild(row);
    });
  }

  function selectMode(modeId) {
    buildModes(modeId);
    buildParams(modeId, null);
    debouncePreview();
  }

  function buildTxParamsFromCfg(cfg) {
    buildTxParams(cfg);
  }

  // ── Preview renderer (mirrors image-pipeline.js logic) ───────────────────

  let _prevTimer = null;
  function debouncePreview() {
    clearTimeout(_prevTimer);
    _prevTimer = setTimeout(drawPreview, 180);
  }

  let _placeholderCanvas = null; // snapshot of last rendered placeholder

  function drawPreview() {
    if (!previewSrc) return;
    const canvas = document.getElementById('pip-canvas');
    const noMsg  = document.getElementById('pip-no-preview');
    const cfg    = getCfg();

    const img = new Image();
    img.onload = function () {
      const thumb = document.createElement('canvas');
      const ts = 64;
      thumb.width = ts; thumb.height = ts;
      thumb.getContext('2d').drawImage(img, 0, 0, ts, ts);
      const thumbImg = new Image();
      thumbImg.onload = function () {
        canvas.width  = canvas.offsetWidth  || 320;
        canvas.height = canvas.offsetHeight || 240;
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        renderPipeline(ctx, canvas.width, canvas.height, thumbImg, cfg);
        noMsg.style.display = 'none';
        // Save snapshot for transition play
        _placeholderCanvas = document.createElement('canvas');
        _placeholderCanvas.width = canvas.width;
        _placeholderCanvas.height = canvas.height;
        _placeholderCanvas.getContext('2d').drawImage(canvas, 0, 0);
      };
      thumbImg.src = thumb.toDataURL('image/webp', 0.9);
    };
    img.onerror = function () {
      document.getElementById('pip-no-preview').textContent = 'Could not load image';
    };
    img.src = previewSrc;
  }

  function playTransition() {
    if (!previewSrc || !_placeholderCanvas) { ctx.toast('Render a preview first', 'error'); return; }
    const canvas = document.getElementById('pip-canvas');
    const cfg    = getCfg();
    const txStyle = cfg.transitionStyle || 'crystallise';
    const txMs    = +(cfg.transitionSpeed || 750);
    const txBlur  = cfg.transitionBlur != null ? +cfg.transitionBlur : 12;
    const W = canvas.width, H = canvas.height;

    const fullImg = new Image();
    fullImg.onload = function () {
      if (txStyle === 'none') {
        const c2 = canvas.getContext('2d');
        c2.drawImage(fullImg, 0, 0, W, H);
        setTimeout(drawPreview, 1200);
        return;
      }
      const start = performance.now();
      const snap  = _placeholderCanvas;
      function frame(now) {
        const t    = Math.min(1, (now - start) / txMs);
        const ease = t < 0.5 ? 2*t*t : -1 + (4-2*t)*t;
        const c2   = canvas.getContext('2d');
        c2.clearRect(0, 0, W, H);

        // Draw full image (fading in)
        if (txStyle === 'crystallise') c2.filter = `blur(${txBlur * (1 - ease)}px)`;
        c2.globalAlpha = ease;
        c2.drawImage(fullImg, 0, 0, W, H);
        c2.filter = 'none';

        // Draw placeholder on top, fading out
        c2.globalAlpha = 1 - ease;
        c2.drawImage(snap, 0, 0, W, H);
        c2.globalAlpha = 1;

        if (t < 1) requestAnimationFrame(frame);
        else setTimeout(drawPreview, 1200);
      }
      requestAnimationFrame(frame);
    };
    fullImg.src = previewSrc;
  }

  // Minimal render functions (mirrors image-pipeline.js)
  function renderPipeline(ctx, W, H, srcImg, cfg) {
    function samplePx(img) {
      const oc = document.createElement('canvas');
      oc.width = img.naturalWidth; oc.height = img.naturalHeight;
      oc.getContext('2d').drawImage(img, 0, 0);
      return { d: oc.getContext('2d').getImageData(0,0,oc.width,oc.height).data, w:oc.width, h:oc.height };
    }
    function smp(px, u, v) {
      const x=Math.max(0,Math.min(px.w-1,Math.round(u*(px.w-1))));
      const y=Math.max(0,Math.min(px.h-1,Math.round(v*(px.h-1))));
      const i=(y*px.w+x)*4;
      return {r:px.d[i],g:px.d[i+1],b:px.d[i+2]};
    }
    function lum(c){return(c.r*.299+c.g*.587+c.b*.114)/255;}
    function hx(hex){hex=(hex||'#000').replace('#','');if(hex.length===3)hex=hex[0]+hex[0]+hex[1]+hex[1]+hex[2]+hex[2];return{r:parseInt(hex.slice(0,2),16),g:parseInt(hex.slice(2,4),16),b:parseInt(hex.slice(4,6),16)};}

    const BAYER=[[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]];

    function dotGrid(ctx, W, H, px, ang, fillStyle, extractor) {
      const cs = cfg.cellSize || 10;
      const ar = ang * Math.PI / 180;
      const cos=Math.cos(ar),sin=Math.sin(ar),icos=Math.cos(-ar),isin=Math.sin(-ar);
      const diag=Math.ceil(Math.sqrt(W*W+H*H));
      const hw=W/2,hh=H/2,span=Math.ceil(diag/cs)+2,off=-Math.floor(span/2);
      ctx.fillStyle = fillStyle;
      for(let i=off;i<off+span;i++){for(let j=off;j<off+span;j++){
        const lx=(i+.5)*cs,ly=(j+.5)*cs;
        const sx=lx*icos-ly*isin+hw,sy=lx*isin+ly*icos+hh;
        if(sx<-cs||sx>W+cs||sy<-cs||sy>H+cs)continue;
        const density=extractor(smp(px,Math.max(0,Math.min(1,sx/W)),Math.max(0,Math.min(1,sy/H))));
        const r=Math.sqrt(Math.max(0,density))*cs*.65;
        if(r<.4)continue;
        const dx=lx*cos-ly*sin+hw,dy=lx*sin+ly*cos+hh;
        ctx.beginPath();ctx.arc(dx,dy,r,0,6.2832);ctx.fill();
      }}
    }

    const mode = cfg.mode || 'halftone';

    if (mode === 'bitmap') {
      ctx.imageSmoothingEnabled = false;
      ctx.drawImage(srcImg, 0, 0, W, H);
      return;
    }
    if (mode === 'progressive') {
      const b = cfg.blur != null ? cfg.blur : 20;
      ctx.filter = `blur(${b}px)`;
      ctx.drawImage(srcImg, -b*2, -b*2, W+b*4, H+b*4);
      ctx.filter = 'none';
      return;
    }

    const px = samplePx(srcImg);

    if (mode === 'dither') {
      // Preview: quantise to N colours client-side using Bayer dithering
      const depth  = parseInt(cfg.colorDepth || '4');
      const nCols  = Math.pow(2, depth);
      const step   = 255 / (nCols - 1);
      const gray   = cfg.paletteType === 'grayscale';
      const useDit = cfg.ditherAlgo !== 'none';
      const bs     = cfg.blockSize || 6;
      const cols   = Math.ceil(W / bs), rows = Math.ceil(H / bs);
      const id     = ctx.createImageData(W, H), dat = id.data;
      for (let j = 0; j < rows; j++) {
        for (let i = 0; i < cols; i++) {
          const c   = smp(px, (i+.5)/cols, (j+.5)/rows);
          const thr = useDit ? (BAYER[j%4][i%4]/16 - 0.5) * step : 0;
          function quant(v){ return Math.round(Math.max(0,Math.min(255, v+thr)) / step) * step; }
          const r = gray ? quant((c.r+c.g+c.b)/3) : quant(c.r);
          const g = gray ? r : quant(c.g);
          const b = gray ? r : quant(c.b);
          for (let dy=0; dy<bs && j*bs+dy<H; dy++) {
            for (let dx=0; dx<bs && i*bs+dx<W; dx++) {
              const idx = ((j*bs+dy)*W + (i*bs+dx))*4;
              dat[idx]=r; dat[idx+1]=g; dat[idx+2]=b; dat[idx+3]=255;
            }
          }
        }
      }
      ctx.putImageData(id, 0, 0);
      return;
    }

    if (mode === 'duotone') {
      ctx.fillStyle = cfg.paperColor || '#f9f5ee';
      ctx.fillRect(0,0,W,H);
      ctx.globalCompositeOperation = 'multiply';
      dotGrid(ctx,W,H,px,cfg.angle1!=null?cfg.angle1:45, cfg.color1||'#1a1a1a', c=>lum(c));
      dotGrid(ctx,W,H,px,cfg.angle2!=null?cfg.angle2:15, cfg.color2||'#c0392b', c=>1-lum(c));
      ctx.globalCompositeOperation = 'source-over';
      return;
    }

    if (mode === 'cmyk') {
      ctx.fillStyle = cfg.paperColor || '#fffdf8';
      ctx.fillRect(0,0,W,H);
      ctx.globalCompositeOperation = 'multiply';
      const chs=[
        {a:15,c:'rgb(0,183,235)',  ex:c=>{const k=1-Math.max(c.r,c.g,c.b)/255;return k===1?0:(1-c.r/255-k)/(1-k);}},
        {a:75,c:'rgb(236,0,140)',  ex:c=>{const k=1-Math.max(c.r,c.g,c.b)/255;return k===1?0:(1-c.g/255-k)/(1-k);}},
        {a:90,c:'rgb(255,239,0)',  ex:c=>{const k=1-Math.max(c.r,c.g,c.b)/255;return k===1?0:(1-c.b/255-k)/(1-k);}},
        {a:45,c:'rgb(20,20,20)',   ex:c=>1-Math.max(c.r,c.g,c.b)/255},
      ];
      chs.forEach(ch=>dotGrid(ctx,W,H,px,ch.a,ch.c,ch.ex));
      ctx.globalCompositeOperation = 'source-over';
      return;
    }

    // default: halftone
    ctx.fillStyle = cfg.paperColor || '#f4f0e8';
    ctx.fillRect(0,0,W,H);
    dotGrid(ctx,W,H,px,cfg.angle!=null?cfg.angle:45, cfg.inkColor||'#1a1a1a', c=>1-lum(c));
  }

  // ── Load state from server ────────────────────────────────────────────────

  async function loadState() {
    try {
      const r = await ctx.apiFetch('/api/adze/artist-info');
      const data = await r.json();
      const savedCfg = (data.config?.features || {}).image_pipeline || null;
      currentCfg = savedCfg;

      const toggle = document.getElementById('pip-toggle');
      toggle.checked = !!savedCfg;
      document.getElementById('pip-toggle-label').textContent = savedCfg ? 'On' : 'Off';
      document.getElementById('pip-body').style.display    = savedCfg ? '' : 'none';
      document.getElementById('pip-off-msg').style.display = savedCfg ? 'none' : '';

      const activeMode = savedCfg?.mode || 'halftone';
      buildModes(activeMode);
      buildParams(activeMode, savedCfg);
      buildTxParams(savedCfg);
    } catch (e) {
      document.getElementById('pip-status').textContent = 'Could not load config';
    }

    // Populate image picker
    try {
      const r2 = await ctx.apiFetch('/api/adze/list-assets');
      const data2 = await r2.json();
      const sel = document.getElementById('pip-img-select');
      (data2.assets || []).filter(a => a.is_image).forEach(a => {
        const opt = document.createElement('option');
        opt.value = `/artists/${ctx.artistSlug}/assets/${a.path}`;
        opt.textContent = a.filename;
        sel.appendChild(opt);
      });
    } catch (e) {}
  }

  // ── Event wiring ──────────────────────────────────────────────────────────

  c.querySelector('#pip-toggle').onchange = function () {
    const on = this.checked;
    document.getElementById('pip-toggle-label').textContent = on ? 'On' : 'Off';
    document.getElementById('pip-body').style.display    = on ? '' : 'none';
    document.getElementById('pip-off-msg').style.display = on ? 'none' : '';
    if (on && !document.querySelector('#pip-modes .pip-mode-btn')) {
      buildModes('halftone');
      buildParams('halftone', null);
      buildTxParams(null);
    }
  };

  c.querySelector('#pip-img-select').onchange = function () {
    previewSrc = this.value || null;
    if (previewSrc) drawPreview();
    else document.getElementById('pip-no-preview').style.display = '';
  };

  c.querySelector('#pip-play').onclick = function () { playTransition(); };

  c.querySelector('#pip-save').onclick = async function () {
    if (saving) return;
    saving = true;
    const btn    = this;
    const status = document.getElementById('pip-status');
    btn.disabled = true; btn.textContent = 'Saving…'; status.textContent = '';

    const enabled = document.getElementById('pip-toggle').checked;
    const payload = enabled ? getCfg() : null;

    try {
      // Backfill thumbs for any images uploaded before this feature was enabled
      if (payload && !currentCfg) {
        status.textContent = 'Generating thumbnails…';
        await ctx.apiFetch('/api/adze/generate-thumbs', { method: 'POST' });
      }

      const r = await ctx.apiFetch('/api/adze/save-feature', {
        method: 'POST',
        body: { feature: 'image_pipeline', config: payload },
      });
      const d = await r.json();
      if (!r.ok || d.error) {
        status.textContent = d.error || 'Save failed';
        ctx.toast(d.error || 'Save failed', 'error');
      } else if (!d.compile_ok) {
        status.textContent = 'Saved — compile error: ' + (d.compile_error || '?');
        ctx.toast('Saved but compile failed', 'error');
      } else {
        status.textContent = 'Saved and recompiled ✓';
        ctx.toast(payload ? 'Image pipeline active' : 'Pipeline disabled', 'success');
        currentCfg = payload;
      }
    } catch (e) {
      status.textContent = 'Error: ' + e.message;
    }

    btn.disabled = false; btn.textContent = 'Save & Recompile';
    saving = false;
  };

  loadState();
})(ctx);
