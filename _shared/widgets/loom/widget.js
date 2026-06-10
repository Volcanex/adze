// Widget: Loom — visual-synth node editor.
// Drag-to-wire patching: sources → effects → output (buffer wires) and
// modulators → params (control wires). Live preview, pan/zoom, node palette.
// Loads the shared engine (engine.js); saves the trace via save-feature.

(function (ctx) {
  const c = ctx.container;
  c.style.cssText = 'display:flex;flex-direction:column;flex:1;min-height:0;overflow:hidden;';

  // ── state ──────────────────────────────────────────────────────────────────
  let trace = null, enabled = false, rt = null, saving = false;
  let presets = [], presetName = 'untitled';
  let scale = 1, panX = 24, panY = 24;
  let pending = null;          // in-progress wire: {fromEl, role, kind, node, name}
  let dragNode = null;         // {id, dx, dy}
  let panning = null;          // {x, y, px, py}
  let rebuildQueued = false;

  const NODE_W = 220;
  const CATS = { source: '#4ea3d6', effect: '#d68a4e', composite: '#b06ad6', modulator: '#6ad67e', output: '#9aa' };

  // ── styles ───────────────────────────────────────────────────────────────
  const style = document.createElement('style');
  style.textContent = `
  .lm-wrap{display:flex;flex-direction:column;flex:1;min-height:0;}
  .lm-bar{display:flex;align-items:center;gap:6px;padding:8px 12px;border-bottom:1px solid var(--border);min-height:0;}
  .lm-bar-right{display:flex;align-items:center;gap:6px;margin-left:auto;}
  .lm-sep{width:1px;height:16px;background:var(--border);margin:0 4px;flex-shrink:0;}
  .lm-btn{padding:5px 10px;font-size:11px;border-radius:var(--radius);cursor:pointer;border:1px solid var(--border);background:var(--surface);color:var(--text);white-space:nowrap;line-height:1.4;}
  .lm-btn:hover{background:var(--bg2);}
  .lm-btn.ghost{background:transparent;border-color:transparent;color:var(--text2);padding:5px 8px;}
  .lm-btn.ghost:hover{background:var(--bg2);color:var(--text);border-color:transparent;}
  .lm-btn.pri{background:var(--accent);color:#fff;border-color:transparent;}
  .lm-btn.pri:hover{opacity:.88;}
  .lm-wordmark{font-family:var(--heading-font);font-style:italic;font-weight:400;font-size:15px;letter-spacing:-.01em;padding-right:2px;white-space:nowrap;}
  .lm-preset-grp{display:flex;border:1px solid var(--border);border-radius:var(--radius);overflow:hidden;}
  .lm-preset-grp .lm-preset-name{border:none;border-right:1px solid var(--border);border-radius:0;width:100px;font-size:11px;padding:4px 8px;background:var(--bg);color:var(--text);}
  .lm-preset-grp .lm-preset-name:focus{outline:none;background:var(--surface);}
  .lm-preset-grp .pg-btn{padding:4px 9px;font-size:11px;background:var(--surface);color:var(--text);border:none;border-right:1px solid var(--border);cursor:pointer;white-space:nowrap;}
  .lm-preset-grp .pg-btn:last-child{border-right:none;}
  .lm-preset-grp .pg-btn:hover{background:var(--bg2);}
  .lm-live-wrap{display:flex;border:1px solid var(--accent);border-radius:var(--radius);overflow:hidden;}
  .lm-live-toggle{display:flex;align-items:center;gap:5px;padding:4px 9px;font-size:11px;color:var(--text2);cursor:pointer;background:var(--surface);border-right:1px solid var(--accent);white-space:nowrap;}
  .lm-live-toggle input{width:13px;height:13px;cursor:pointer;accent-color:var(--accent);}
  .lm-live-btn{padding:4px 11px;font-size:11px;font-weight:600;background:var(--accent);color:#fff;border:none;cursor:pointer;white-space:nowrap;}
  .lm-live-btn:hover{opacity:.88;}
  .lm-vp{position:relative;flex:1;min-height:340px;overflow:hidden;background:
     radial-gradient(circle at 1px 1px, rgba(255,255,255,.06) 1px, transparent 0) 0 0/22px 22px, var(--bg);cursor:grab;}
  .lm-vp.grab{cursor:grabbing;}
  .lm-world{position:absolute;top:0;left:0;transform-origin:0 0;}
  .lm-svg{position:absolute;top:0;left:0;width:5000px;height:5000px;overflow:visible;pointer-events:none;}
  .lm-svg path{pointer-events:stroke;cursor:pointer;}
  .lm-node{position:absolute;width:${NODE_W}px;background:var(--surface);border:1px solid var(--border);
     border-radius:8px;box-shadow:0 4px 14px rgba(0,0,0,.28);font-size:10px;user-select:none;}
  .lm-head{display:flex;align-items:center;gap:5px;padding:5px 8px;border-bottom:1px solid var(--border);
     border-radius:8px 8px 0 0;cursor:grab;font-weight:600;}
  .lm-head .dot{width:7px;height:7px;border-radius:50%;flex:0 0 auto;}
  .lm-head .id{color:var(--text2);font-weight:400;font-size:9px;margin-left:auto;}
  .lm-head .x{cursor:pointer;color:var(--text2);padding:0 2px;}
  .lm-head .x:hover{color:#e66;}
  .lm-body{padding:4px 8px 7px;}
  .lm-row{position:relative;display:flex;align-items:center;gap:5px;min-height:24px;padding:1px 0;}
  .lm-row .lbl{color:var(--text2);flex:0 0 68px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
  .lm-row input[type=range]{flex:1;min-width:0;height:3px;}
  .lm-row select,.lm-row input[type=text]{flex:1;font-size:10px;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:1px 3px;min-width:0;}
  .lm-row input[type=color]{width:24px;height:16px;padding:0;border:1px solid var(--border);background:none;}
  .lm-num{width:42px;font-size:10px;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:1px 3px;text-align:right;flex:0 0 auto;-moz-appearance:textfield;}
  .lm-num::-webkit-outer-spin-button,.lm-num::-webkit-inner-spin-button{-webkit-appearance:none;}
  .lm-bounds{font-size:9px;color:var(--text2);flex:0 0 auto;white-space:nowrap;opacity:.7;}
  .lm-port{position:absolute;width:10px;height:10px;border-radius:50%;border:2px solid var(--bg);cursor:crosshair;z-index:2;}
  .lm-port.buf{background:#4ea3d6;} .lm-port.ctl{background:#6ad67e;}
  .lm-port.inp{left:-16px;top:50%;transform:translateY(-50%);}
  .lm-port.outp{right:-7px;}
  .lm-port.inp:hover{transform:translateY(-50%) scale(1.35);}
  .lm-port.outp:hover{transform:scale(1.35);}
  .lm-float{position:absolute;right:12px;top:12px;width:280px;height:280px;
     background:var(--surface);border:1px solid var(--border);border-radius:8px;
     box-shadow:0 6px 20px rgba(0,0,0,.45);display:flex;flex-direction:column;
     overflow:hidden;z-index:10;min-width:160px;min-height:120px;}
  .lm-float.hidden{display:none;}
  .lm-float-head{display:flex;align-items:center;padding:5px 8px;gap:6px;
     border-bottom:1px solid var(--border);cursor:grab;user-select:none;flex:0 0 auto;}
  .lm-float-head.grab{cursor:grabbing;}
  .lm-float-head span{font-size:10px;font-weight:600;color:var(--text2);flex:1;}
  .lm-float-head button{background:none;border:none;color:var(--text2);cursor:pointer;padding:0 2px;font-size:13px;line-height:1;}
  .lm-float-head button:hover{color:#e66;}
  .lm-float-canvas{display:block;width:100%;height:100%;image-rendering:pixelated;background:#08080e;flex:1;min-height:0;}
  .lm-float-rsz{position:absolute;right:0;bottom:0;width:14px;height:14px;cursor:se-resize;opacity:.4;}
  .lm-float-rsz:hover{opacity:.9;}
  .lm-float-rsz::after{content:'';position:absolute;right:3px;bottom:3px;width:6px;height:6px;border-right:2px solid var(--text2);border-bottom:2px solid var(--text2);}
  .lm-menu{position:absolute;z-index:20;background:var(--surface);border:1px solid var(--border);border-radius:8px;
     box-shadow:0 8px 24px rgba(0,0,0,.4);padding:6px;max-height:320px;overflow:auto;display:none;}
  .lm-menu h5{margin:6px 6px 2px;font-size:9px;text-transform:uppercase;letter-spacing:.5px;color:var(--text2);}
  .lm-menu button{display:block;width:150px;text-align:left;padding:4px 8px;font-size:11px;background:none;border:none;
     color:var(--text);cursor:pointer;border-radius:4px;}
  .lm-menu button:hover{background:var(--bg2);}
  .lm-status{font-size:10px;color:var(--text2);}
  .lm-preset-name{font-size:11px;}
  .lm-preset-drop{position:absolute;top:100%;left:0;margin-top:4px;z-index:30;background:var(--surface);border:1px solid var(--border);border-radius:8px;box-shadow:0 8px 24px rgba(0,0,0,.4);padding:4px;min-width:180px;display:none;}
  .lm-preset-drop.open{display:block;}
  .lm-preset-item{display:flex;align-items:center;padding:4px 8px;border-radius:4px;cursor:pointer;font-size:11px;gap:6px;}
  .lm-preset-item:hover{background:var(--bg2);}
  .lm-preset-item span{flex:1;}
  .lm-preset-item .del{color:var(--text2);font-size:12px;padding:0 2px;cursor:pointer;opacity:0;}
  .lm-preset-item:hover .del{opacity:1;}
  .lm-preset-item .del:hover{color:#e66;}
  .lm-preset-empty{padding:8px;font-size:11px;color:var(--text2);text-align:center;}`;
  c.appendChild(style);

  c.insertAdjacentHTML('beforeend', `
  <div class="lm-wrap">
    <div class="lm-bar">
      <span class="lm-wordmark">Loom</span>
      <div class="lm-sep"></div>
      <span style="position:relative;">
        <button class="lm-btn" data-action="palette">+ Node</button>
        <div class="lm-menu" id="lm-menu"></div>
      </span>
      <button class="lm-btn ghost" data-action="reset" title="Reset to empty patch">Reset</button>
      <button class="lm-btn ghost" data-action="fit" title="Fit nodes to view">Fit</button>
      <button class="lm-btn ghost" data-action="preview" title="Show preview window">Preview</button>
      <div class="lm-bar-right">
        <span class="lm-status" id="lm-status"></span>
        <div class="lm-sep"></div>
        <span style="position:relative;">
          <div class="lm-preset-grp">
            <input class="lm-preset-name" id="lm-preset-name" type="text" value="untitled" placeholder="name…" title="Preset name">
            <button class="pg-btn" data-action="preset-save" title="Save preset">Save</button>
            <button class="pg-btn" data-action="preset-list" title="Load preset">▾</button>
          </div>
          <div class="lm-preset-drop" id="lm-preset-drop"></div>
        </span>
        <div class="lm-sep"></div>
        <div class="lm-live-wrap">
          <label class="lm-live-toggle" title="Enable Loom on your live site">
            <input type="checkbox" id="lm-toggle"><span id="lm-toggle-label">Off</span>
          </label>
          <button class="lm-live-btn" data-action="go-live" title="Compile and publish to site">Go Live</button>
        </div>
      </div>
    </div>
    <div class="lm-vp" id="lm-vp">
      <div class="lm-world" id="lm-world">
        <svg class="lm-svg" id="lm-svg"></svg>
      </div>
      <div class="lm-float" id="lm-float">
        <div class="lm-float-head" id="lm-float-head">
          <span>Preview</span>
          <button data-action="preview-close" title="Close">×</button>
        </div>
        <canvas class="lm-float-canvas" id="lm-pv" width="360" height="360"></canvas>
        <div class="lm-float-rsz" id="lm-float-rsz"></div>
      </div>
    </div>
  </div>`);

  const $ = (s) => c.querySelector(s);
  const vp = $('#lm-vp'), world = $('#lm-world'), svg = $('#lm-svg'), preview = $('#lm-pv'),
        menu = $('#lm-menu'), statusEl = $('#lm-status'), toggle = $('#lm-toggle');
  const floatPanel = $('#lm-float'), floatHead = $('#lm-float-head'), floatRsz = $('#lm-float-rsz');
  const presetNameEl = $('#lm-preset-name'), presetDrop = $('#lm-preset-drop');

  // ── float preview drag + resize ───────────────────────────────────────────
  (function initFloat() {
    let fdrag = null, fresize = null;
    floatHead.addEventListener('mousedown', (e) => {
      if (e.target.closest('button')) return;
      e.preventDefault();
      const fr = floatPanel.getBoundingClientRect(), vr = vp.getBoundingClientRect();
      fdrag = { ox: e.clientX, oy: e.clientY, startL: fr.left - vr.left, startT: fr.top - vr.top };
      floatHead.classList.add('grab');
    });
    floatRsz.addEventListener('mousedown', (e) => {
      e.preventDefault(); e.stopPropagation();
      const fr = floatPanel.getBoundingClientRect();
      fresize = { ox: e.clientX, oy: e.clientY, startW: fr.width, startH: fr.height };
    });
    document.addEventListener('mousemove', (e) => {
      if (fdrag) {
        const vr = vp.getBoundingClientRect(), pw = floatPanel.offsetWidth, ph = floatPanel.offsetHeight;
        let nx = Math.max(0, Math.min(vr.width  - pw, fdrag.startL + (e.clientX - fdrag.ox)));
        let ny = Math.max(0, Math.min(vr.height - ph, fdrag.startT + (e.clientY - fdrag.oy)));
        floatPanel.style.right = 'auto'; floatPanel.style.left = nx + 'px'; floatPanel.style.top = ny + 'px';
      }
      if (fresize) {
        floatPanel.style.width  = Math.max(160, fresize.startW + (e.clientX - fresize.ox)) + 'px';
        floatPanel.style.height = Math.max(120, fresize.startH + (e.clientY - fresize.oy)) + 'px';
      }
    });
    document.addEventListener('mouseup', () => { fdrag = null; fresize = null; floatHead.classList.remove('grab'); });
  })();

  // redraw wires whenever the viewport becomes visible (tab switch / initial show)
  new ResizeObserver(() => { if (vp.offsetWidth > 0) redrawWires(); }).observe(vp);

  // ── engine load ────────────────────────────────────────────────────────────
  function loadEngine() {
    return new Promise(async (resolve, reject) => {
      if (window.Loom) return resolve();
      try {
        const r = await ctx.apiFetch('/api/adze/get-widget?filename=loom/engine.js&tier=platform');
        if (!r.ok) throw new Error('engine fetch ' + r.status);
        const s = document.createElement('script'); s.textContent = await r.text(); document.head.appendChild(s);
        window.Loom ? resolve() : reject(new Error('engine did not register'));
      } catch (e) { reject(e); }
    });
  }

  // ── coords ──────────────────────────────────────────────────────────────────
  function applyTransform() { world.style.transform = `translate(${panX}px,${panY}px) scale(${scale})`; }
  function screenToWorld(cx_, cy_) { const r = vp.getBoundingClientRect(); return { x: (cx_ - r.left - panX) / scale, y: (cy_ - r.top - panY) / scale }; }
  function portCenter(el) { const r = el.getBoundingClientRect(); return screenToWorld(r.left + r.width / 2, r.top + r.height / 2); }
  function uid(type) { let i = 1, base = type.slice(0, 3); while (trace.nodes.some((n) => n.id === base + i)) i++; return base + i; }

  // ── render nodes ──────────────────────────────────────────────────────────
  function paramVal(n, k) { const def = window.Loom.REG[n.type].params[k]; return (n.params && n.params[k] != null) ? n.params[k] : def.def; }
  function modEdgeTo(id, name) { return (trace.edges || []).find((e) => e.kind === 'control' && e.to[0] === id && e.to[1] === name); }

  function renderNodes() {
    [...world.querySelectorAll('.lm-node')].forEach((n) => n.remove());
    const REG = window.Loom.REG;
    for (const n of trace.nodes) {
      const def = REG[n.type]; if (!def) continue;
      const cat = def.cat || def.kind, color = CATS[cat] || '#888';
      const el = document.createElement('div');
      el.className = 'lm-node'; el.dataset.id = n.id; el.style.left = n.x + 'px'; el.style.top = n.y + 'px';
      let body = '';
      // buffer inlets
      for (const inl of (def.inlets || [])) {
        body += `<div class="lm-row"><span class="lm-port buf inp" data-node="${n.id}" data-role="in" data-kind="buffer" data-name="${inl}"></span><span class="lbl">${inl}</span></div>`;
      }
      // params
      for (const k in (def.params || {})) {
        const pd = def.params[k], v = paramVal(n, k), modded = !!modEdgeTo(n.id, k), canMod = pd.min != null;
        const port = canMod ? `<span class="lm-port ctl inp" data-node="${n.id}" data-role="in" data-kind="control" data-name="${k}" title="modulate ${k}"></span>` : '';
        let ctrl;
        if (pd.type === 'asset') {
          const accept = pd.accept || 'image';
          const isVid = (a) => /\.(mp4|webm|mov|m4v|ogv|ogg)$/i.test(a.path || '');
          const opts = (ctx.assetList || []).filter((a) => accept === 'video' ? isVid(a) : (a.is_image && !isVid(a)));
          ctrl = `<select data-node="${n.id}" data-param="${k}"><option value="" ${!v ? 'selected' : ''}>— pick ${accept} —</option>` +
            opts.map((a) => `<option value="${ctx.escHtml(a.path)}" ${a.path === v ? 'selected' : ''}>${ctx.escHtml(a.filename || a.path)}</option>`).join('') + `</select>`;
        }
        else if (pd.type === 'select') ctrl = `<select data-node="${n.id}" data-param="${k}">${pd.options.map((o) => `<option ${o === v ? 'selected' : ''}>${ctx.escHtml(o)}</option>`).join('')}</select>`;
        else if (pd.type === 'color') ctrl = `<input type="color" data-node="${n.id}" data-param="${k}" value="${ctx.escHtml(v)}">`;
        else if (pd.type === 'text') ctrl = `<input type="text" data-node="${n.id}" data-param="${k}" value="${ctx.escHtml(v)}">`;
        else {
          const step = (pd.max - pd.min) / 100;
          const fmt = (x) => Number.isInteger(x) ? x : +x.toFixed(1);
          ctrl = `<input type="range" data-node="${n.id}" data-param="${k}" min="${pd.min}" max="${pd.max}" step="${step}" value="${v}" ${modded ? 'disabled' : ''} title="${k}: ${(+v).toFixed(2)}"><input type="number" class="lm-num" data-node="${n.id}" data-param="${k}" min="${pd.min}" max="${pd.max}" step="${step}" value="${(+v).toFixed(2)}" ${modded ? 'disabled' : ''}><span class="lm-bounds">${fmt(pd.min)}–${fmt(pd.max)}</span>`;
        }
        body += `<div class="lm-row">${port}<span class="lbl">${k}</span>${ctrl}</div>`;
      }
      const out = def.kind === 'output' ? '' :
        `<span class="lm-port ${def.kind === 'modulator' ? 'ctl' : 'buf'} outp" data-node="${n.id}" data-role="out" data-kind="${def.kind === 'modulator' ? 'control' : 'buffer'}" style="top:9px;"></span>`;
      el.innerHTML = `<div class="lm-head" data-drag="${n.id}"><span class="dot" style="background:${color}"></span>${ctx.escHtml(n.type)}<span class="id">${ctx.escHtml(n.id)}</span><span class="x" data-del="${n.id}">×</span></div><div class="lm-body">${body}</div>${out}`;
      world.appendChild(el);
    }
    requestAnimationFrame(redrawWires);
  }

  // ── render wires ────────────────────────────────────────────────────────────
  function portEl(node, role, name) {
    const sel = `.lm-port[data-node="${node}"][data-role="${role}"]` + (name ? `[data-name="${name}"]` : '');
    return world.querySelector(sel);
  }
  function pathD(a, b) { const co = Math.max(40, Math.abs(b.x - a.x) * 0.5); return `M ${a.x} ${a.y} C ${a.x + co} ${a.y}, ${b.x - co} ${b.y}, ${b.x} ${b.y}`; }
  function redrawWires() {
    svg.innerHTML = '';
    for (let i = 0; i < (trace.edges || []).length; i++) {
      const e = trace.edges[i];
      const oEl = portEl(e.from[0], 'out'), iEl = portEl(e.to[0], 'in', e.to[1]);
      if (!oEl || !iEl) continue;
      const a = portCenter(oEl), b = portCenter(iEl), ctl = e.kind === 'control';
      const p = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      p.setAttribute('d', pathD(a, b));
      p.setAttribute('fill', 'none');
      p.setAttribute('stroke', ctl ? '#6ad67e' : '#4ea3d6');
      p.setAttribute('stroke-width', '2'); p.setAttribute('opacity', '.8');
      if (ctl) p.setAttribute('stroke-dasharray', '5 4');
      p.dataset.edge = i;
      p.addEventListener('click', (ev) => { ev.stopPropagation(); trace.edges.splice(+ev.target.dataset.edge, 1); renderNodes(); queueRebuild(); });
      svg.appendChild(p);
    }
    if (pending && pending.tmp) svg.appendChild(pending.tmp);
  }

  // ── engine rebuild (debounced) ──────────────────────────────────────────────
  function queueRebuild() {
    if (rebuildQueued) return; rebuildQueued = true;
    requestAnimationFrame(() => {
      rebuildQueued = false;
      if (rt) rt.stop();
      preview.width = trace.size.w; preview.height = trace.size.h;
      rt = window.Loom.mount(preview, trace);
    });
  }

  // ── connections ─────────────────────────────────────────────────────────────
  function startWire(portElm, ev) {
    ev.stopPropagation(); ev.preventDefault();
    pending = { node: portElm.dataset.node, role: portElm.dataset.role, kind: portElm.dataset.kind, name: portElm.dataset.name, el: portElm };
    const tmp = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    tmp.setAttribute('fill', 'none'); tmp.setAttribute('stroke', pending.kind === 'control' ? '#6ad67e' : '#4ea3d6');
    tmp.setAttribute('stroke-width', '2'); tmp.setAttribute('stroke-dasharray', '4 4'); tmp.setAttribute('opacity', '.7');
    pending.tmp = tmp; svg.appendChild(tmp);
  }
  function moveWire(ev) {
    const a = portCenter(pending.el), b = screenToWorld(ev.clientX, ev.clientY);
    pending.tmp.setAttribute('d', pathD(pending.role === 'out' ? a : b, pending.role === 'out' ? b : a));
  }
  function endWire(ev) {
    const tgt = ev.target.closest && ev.target.closest('.lm-port');
    if (tgt && tgt.dataset.role !== pending.role && tgt.dataset.kind === pending.kind && tgt.dataset.node !== pending.node) {
      const fromNode = pending.role === 'out' ? pending.node : tgt.dataset.node;
      const toNode = pending.role === 'in' ? pending.node : tgt.dataset.node;
      const toName = pending.role === 'in' ? pending.name : tgt.dataset.name;
      trace.edges = (trace.edges || []).filter((e) => !(e.to[0] === toNode && e.to[1] === toName)); // one source per inlet/param
      const edge = { from: [fromNode, 'out'], to: [toNode, toName], kind: pending.kind };
      if (pending.kind === 'control') { const pd = window.Loom.REG[trace.nodes.find((n) => n.id === toNode).type].params[toName]; edge.range = [pd.min, pd.max]; }
      trace.edges.push(edge);
      renderNodes(); queueRebuild();
    } else { pending.tmp.remove(); }
    pending = null;
  }

  // ── pointer routing ─────────────────────────────────────────────────────────
  world.addEventListener('dblclick', (e) => {
    const port = e.target.closest('.lm-port'); if (!port) return;
    e.stopPropagation();
    const id = port.dataset.node, name = port.dataset.name, role = port.dataset.role;
    const before = (trace.edges || []).length;
    trace.edges = (trace.edges || []).filter((ed) =>
      role === 'out' ? ed.from[0] !== id : !(ed.to[0] === id && ed.to[1] === name)
    );
    if (trace.edges.length !== before) { renderNodes(); queueRebuild(); }
  });
  world.addEventListener('mousedown', (e) => {
    const port = e.target.closest('.lm-port'); if (port) return startWire(port, e);
    const drag = e.target.closest('[data-drag]');
    if (drag) {
      const n = trace.nodes.find((x) => x.id === drag.dataset.drag);
      const w = screenToWorld(e.clientX, e.clientY); dragNode = { id: n.id, dx: w.x - n.x, dy: w.y - n.y }; e.preventDefault();
    }
  });
  vp.addEventListener('mousedown', (e) => {
    if (e.target === vp || e.target === world || e.target === svg) { panning = { x: e.clientX, y: e.clientY, px: panX, py: panY }; vp.classList.add('grab'); }
  });
  document.addEventListener('mousemove', (e) => {
    if (pending) moveWire(e);
    else if (dragNode) { const w = screenToWorld(e.clientX, e.clientY), n = trace.nodes.find((x) => x.id === dragNode.id); n.x = Math.round(w.x - dragNode.dx); n.y = Math.round(w.y - dragNode.dy); const el = world.querySelector(`.lm-node[data-id="${n.id}"]`); el.style.left = n.x + 'px'; el.style.top = n.y + 'px'; redrawWires(); }
    else if (panning) { panX = panning.px + (e.clientX - panning.x); panY = panning.py + (e.clientY - panning.y); applyTransform(); }
  });
  document.addEventListener('mouseup', (e) => { if (pending) endWire(e); dragNode = null; panning = null; vp.classList.remove('grab'); });
  vp.addEventListener('wheel', (e) => {
    e.preventDefault(); const r = vp.getBoundingClientRect(), mx = e.clientX - r.left, my = e.clientY - r.top;
    const ns = Math.max(0.3, Math.min(2.5, scale * (e.deltaY < 0 ? 1.1 : 0.9)));
    panX = mx - (mx - panX) * (ns / scale); panY = my - (my - panY) * (ns / scale); scale = ns; applyTransform();
  }, { passive: false });

  // ── palette ─────────────────────────────────────────────────────────────────
  function buildMenu() {
    const REG = window.Loom.REG, groups = {};
    for (const ty of window.Loom.types()) { const cat = REG[ty].cat || REG[ty].kind; if (ty === 'output') continue; (groups[cat] = groups[cat] || []).push(ty); }
    let h = '';
    for (const cat of ['source', 'effect', 'composite', 'modulator']) if (groups[cat]) h += `<h5>${cat}</h5>` + groups[cat].map((ty) => `<button data-add="${ty}">${ty}</button>`).join('');
    menu.innerHTML = h;
  }
  function addNode(type) {
    const ctr = screenToWorld(vp.getBoundingClientRect().left + vp.clientWidth / 2, vp.getBoundingClientRect().top + vp.clientHeight / 2);
    trace.nodes.push({ id: uid(type), type, x: Math.round(ctr.x - NODE_W / 2), y: Math.round(ctr.y - 30), params: {} });
    renderNodes(); queueRebuild();
  }
  function fitView() {
    if (!trace.nodes.length) return;
    const xs = trace.nodes.map((n) => n.x), ys = trace.nodes.map((n) => n.y);
    const minX = Math.min(...xs) - 30, minY = Math.min(...ys) - 30, maxX = Math.max(...xs) + NODE_W + 60, maxY = Math.max(...ys) + 220;
    const sx = vp.clientWidth / (maxX - minX), sy = vp.clientHeight / (maxY - minY);
    scale = Math.max(0.3, Math.min(1.4, Math.min(sx, sy))); panX = -minX * scale + 20; panY = -minY * scale + 20; applyTransform();
  }

  // ── top-bar actions ──────────────────────────────────────────────────────────
  c.addEventListener('click', (e) => {
    const a = e.target.closest('[data-action]'), add = e.target.closest('[data-add]'), del = e.target.closest('[data-del]');
    if (del) { const id = del.dataset.del; trace.nodes = trace.nodes.filter((n) => n.id !== id); trace.edges = (trace.edges || []).filter((ed) => ed.from[0] !== id && ed.to[0] !== id); renderNodes(); queueRebuild(); return; }
    if (add) { addNode(add.dataset.add); menu.style.display = 'none'; return; }
    if (!a) { if (menu.style.display === 'block' && !e.target.closest('#lm-menu')) menu.style.display = 'none'; return; }
    if (a.dataset.action === 'palette') { menu.style.display = menu.style.display === 'block' ? 'none' : 'block'; menu.style.left = '0px'; menu.style.top = '30px'; }
    else if (a.dataset.action === 'reset') { trace = window.Loom.starter(); renderNodes(); queueRebuild(); fitView(); }
    else if (a.dataset.action === 'fit') fitView();
    else if (a.dataset.action === 'preview') floatPanel.classList.remove('hidden');
    else if (a.dataset.action === 'preview-close') floatPanel.classList.add('hidden');
    else if (a.dataset.action === 'preset-save') savePreset();
    else if (a.dataset.action === 'preset-list') presetDrop.classList.toggle('open');
    else if (a.dataset.action === 'go-live') goLive();
  });

  c.addEventListener('input', (e) => {
    const el = e.target.closest('[data-param]'); if (!el) return;
    const n = trace.nodes.find((x) => x.id === el.dataset.node); if (!n) return;
    n.params = n.params || {};
    const isRange = el.type === 'range', isNum = el.type === 'number';
    n.params[el.dataset.param] = (isRange || isNum) ? parseFloat(el.value) : el.value;
    if (isRange || isNum) {
      const row = el.closest('.lm-row');
      if (isRange) { el.title = el.dataset.param + ': ' + (+el.value).toFixed(2); const num = row && row.querySelector('.lm-num'); if (num) num.value = (+el.value).toFixed(2); }
      if (isNum)   { const rng = row && row.querySelector('input[type=range]'); if (rng) rng.value = el.value; }
    }
    queueRebuild();
  });

  toggle.addEventListener('change', () => { enabled = toggle.checked; $('#lm-toggle-label').textContent = enabled ? 'On' : 'Off'; });

  // ── presets ──────────────────────────────────────────────────────────────────
  function renderPresetDrop() {
    if (!presets.length) { presetDrop.innerHTML = '<div class="lm-preset-empty">No saved presets</div>'; return; }
    presetDrop.innerHTML = presets.map((p) =>
      `<div class="lm-preset-item" data-load="${ctx.escHtml(p.name)}"><span>${ctx.escHtml(p.name)}</span><span class="del" data-del-preset="${ctx.escHtml(p.name)}">×</span></div>`
    ).join('');
  }

  async function loadPresets() {
    try {
      const r = await ctx.apiFetch('/api/adze/loom-presets');
      const d = await r.json();
      presets = d.presets || [];
      renderPresetDrop();
    } catch (_) {}
  }

  async function savePreset() {
    const name = presetNameEl.value.trim();
    if (!name) { ctx.toast('Enter a preset name', 'error'); presetNameEl.focus(); return; }
    presetName = name;
    statusEl.textContent = 'Saving…';
    try {
      const r = await ctx.apiFetch('/api/adze/loom-preset', { method: 'POST', body: { name, trace } });
      const d = await r.json();
      if (!r.ok || d.error) { ctx.toast(d.error || 'Save failed', 'error'); statusEl.textContent = ''; }
      else { statusEl.textContent = `"${d.name}" saved`; await loadPresets(); }
    } catch (err) { ctx.toast(err.message, 'error'); statusEl.textContent = ''; }
  }

  async function deletePreset(name) {
    try {
      await ctx.apiFetch(`/api/adze/loom-preset/${encodeURIComponent(name)}`, { method: 'DELETE' });
      presets = presets.filter((p) => p.name !== name);
      renderPresetDrop();
    } catch (_) {}
  }

  async function goLive() {
    if (saving) return; saving = true; statusEl.textContent = 'Publishing…';
    try {
      const r = await ctx.apiFetch('/api/adze/save-feature', { method: 'POST', body: { feature: 'loom', config: enabled ? trace : null } });
      const d = await r.json();
      if (!r.ok || d.error) { statusEl.textContent = d.error || 'Failed'; ctx.toast(d.error || 'Failed', 'error'); }
      else if (!d.compile_ok) { statusEl.textContent = 'Compile error'; ctx.toast('Compile failed', 'error'); }
      else { statusEl.textContent = enabled ? 'Live ✓' : 'Disabled ✓'; ctx.toast(enabled ? 'Loom is live' : 'Loom disabled', 'success'); }
    } catch (err) { statusEl.textContent = 'Error: ' + err.message; }
    saving = false;
  }

  presetDrop.addEventListener('click', (e) => {
    const del = e.target.closest('[data-del-preset]');
    if (del) { e.stopPropagation(); deletePreset(del.dataset.delPreset); return; }
    const load = e.target.closest('[data-load]');
    if (load) {
      const p = presets.find((x) => x.name === load.dataset.load);
      if (p) { trace = p.trace; presetName = p.name; presetNameEl.value = p.name; renderNodes(); queueRebuild(); fitView(); statusEl.textContent = `"${p.name}" loaded`; }
      presetDrop.classList.remove('open');
    }
  });

  document.addEventListener('click', (e) => {
    if (!presetDrop.contains(e.target) && !e.target.closest('[data-action="preset-list"]')) presetDrop.classList.remove('open');
  });

  // ── boot ─────────────────────────────────────────────────────────────────────
  (async function init() {
    try {
      await loadEngine();
      // Resolve portable asset paths in image/video nodes to the dashboard's
      // authed asset-thumb route (same-origin → preview canvas stays readable
      // for downstream getImageData effects like vhs/chromashift).
      window.Loom.setAssetResolver((rel) => {
        if (!rel || /^(https?:|data:|blob:|\/)/.test(rel)) return rel || '';
        const path = String(rel).split('/').map(encodeURIComponent).join('/');
        return `/api/adze/asset-thumb/${encodeURIComponent(ctx.artistSlug)}/${path}?t=${encodeURIComponent(ctx.token || '')}`;
      });
      buildMenu();
      const [infoRes, _] = await Promise.all([ctx.apiFetch('/api/adze/artist-info'), loadPresets()]);
      const data = await infoRes.json();
      const active = (data.config && data.config.features && data.config.features.loom) || null;
      enabled = !!active; toggle.checked = enabled; $('#lm-toggle-label').textContent = enabled ? 'On' : 'Off';
      trace = active || window.Loom.starter();
      applyTransform(); renderNodes(); queueRebuild(); fitView();
      statusEl.textContent = window.Loom.types().length + ' node types · drag ports to wire';
    } catch (e) { statusEl.textContent = 'Failed to load: ' + e.message; }
  })();
})(ctx);
