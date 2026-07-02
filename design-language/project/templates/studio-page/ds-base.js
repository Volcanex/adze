// Last Place — design-system base loader for templates.
// Loads this DS's global stylesheet(s) and the compiled component bundle so a
// consuming page needs just one line: <script src="./ds-base.js"></script>.
(() => {
  const base = '../..'; // path from this template folder to the DS root
  for (const p of ['styles.css']) {
    const l = document.createElement('link');
    l.rel = 'stylesheet';
    l.href = base + '/' + p;
    document.head.appendChild(l);
  }
  const s = document.createElement('script');
  s.src = base + '/_ds_bundle.js';
  s.onerror = () => console.error(
    'ds-base.js: failed to load ' + s.src +
    ' — if this is a consuming project, point the base line at the bound _ds/<folder> tree relative to this page; in a fresh design system this can just mean the bundle is not compiled yet'
  );
  document.head.appendChild(s);
})();
