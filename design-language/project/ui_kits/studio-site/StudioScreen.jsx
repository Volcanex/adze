const studioStyles = {
  head: { padding: "var(--space-9) var(--page-margin) var(--space-7)", display: "grid", gridTemplateColumns: "1fr 0.7fr", gap: "48px", alignItems: "end" },
  eyebrow: { fontFamily: "var(--font-mono)", fontSize: "11.5px", letterSpacing: "0.2em", textTransform: "uppercase", color: "var(--text-muted)", marginBottom: "24px" },
  big: { fontFamily: "var(--font-serif)", fontWeight: 300, fontSize: "64px", lineHeight: 0.98, letterSpacing: "-0.02em", margin: 0, maxWidth: "16ch" },
  art: { display: "flex", justifyContent: "flex-end" },
  artImg: { width: "100%", maxWidth: "220px", filter: "none" },

  body: { padding: "var(--space-6) var(--page-margin) var(--space-8)", display: "grid", gridTemplateColumns: "1fr 1fr", gap: "48px" },
  p: { fontFamily: "var(--font-serif)", fontSize: "19px", lineHeight: 1.62, color: "var(--text-body)", margin: "0 0 22px", maxWidth: "52ch" },

  services: { borderTop: "1px solid var(--border-hairline)", padding: "var(--space-7) var(--page-margin) var(--space-10)" },
  sLabel: { fontFamily: "var(--font-mono)", fontSize: "11.5px", letterSpacing: "0.2em", textTransform: "uppercase", color: "var(--text-faint)", marginBottom: "28px" },
  sGrid: { display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "1px", background: "var(--border-hairline)", border: "1px solid var(--border-hairline)" },
  sCell: { background: "var(--surface-page)", padding: "28px 24px" },
  sNum: { fontFamily: "var(--font-mono)", fontSize: "12px", color: "var(--lp-blue)", marginBottom: "14px" },
  sName: { fontFamily: "var(--font-serif)", fontSize: "26px", marginBottom: "10px" },
  sDesc: { fontFamily: "var(--font-serif)", fontSize: "16px", lineHeight: 1.5, color: "var(--text-muted)" },
};

function StudioScreen() {
  const services = [
    ["Brand identity", "Wordmarks, systems, and the small print that holds them together."],
    ["Websites", "Hand-built, fast, and quiet. Made to age well, not to trend."],
    ["Editorial", "Type-led layouts for publications, archives, and reading."],
    ["Art direction", "A point of view, applied consistently across everything."],
    ["Lino & print", "We still cut blocks by hand — it keeps the eye honest."],
    ["Care", "We answer emails, hit dates, and explain ourselves plainly."],
  ];
  return (
    <div>
      <header style={studioStyles.head}>
        <div>
          <div style={studioStyles.eyebrow}>Studio — est. 2022</div>
          <h1 style={studioStyles.big}>A small studio, and proud to come last.</h1>
        </div>
        <div style={studioStyles.art}>
          <img src="../../assets/plant-mark-blue.png" alt="Last Place plant mark" style={studioStyles.artImg} />
        </div>
      </header>

      <section style={studioStyles.body}>
        <div>
          <p style={studioStyles.p}>
            Last Place is a two-person web design studio working with arts,
            culture and third-sector clients across the UK. We believe a website
            is mostly white space with a few good decisions inside it.
          </p>
          <p style={studioStyles.p}>
            We name ourselves after the finish line on purpose. Coming last
            means we are never in a hurry — we take the time to draw the thing
            properly, set the type by hand, and leave room to breathe.
          </p>
        </div>
        <div>
          <p style={studioStyles.p}>
            Everything starts in blue. We cut lino blocks, print them, and let
            the rough edge of the press find its way into the digital work. The
            result is something hand-made and a little imperfect — which is the
            point.
          </p>
          <p style={studioStyles.p}>
            If your values match ours and you have a project that deserves
            care, we would love to hear about it.
          </p>
        </div>
      </section>

      <section style={studioStyles.services}>
        <div style={studioStyles.sLabel}>What we do</div>
        <div style={studioStyles.sGrid}>
          {services.map(([name, desc], i) => (
            <div key={name} style={studioStyles.sCell}>
              <div style={studioStyles.sNum}>{String(i + 1).padStart(2, "0")}</div>
              <div style={studioStyles.sName}>{name}</div>
              <div style={studioStyles.sDesc}>{desc}</div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

window.StudioScreen = StudioScreen;
