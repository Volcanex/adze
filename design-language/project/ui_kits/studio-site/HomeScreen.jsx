const homeStyles = {
  hero: {
    display: "grid",
    gridTemplateColumns: "1.25fr 0.75fr",
    gap: "48px",
    alignItems: "center",
    padding: "var(--space-10) var(--page-margin) var(--space-9)",
  },
  eyebrow: {
    fontFamily: "var(--font-mono)", fontSize: "11.5px", letterSpacing: "0.2em",
    textTransform: "uppercase", color: "var(--text-muted)", marginBottom: "28px",
  },
  h1: {
    fontFamily: "var(--font-serif)", fontWeight: 300, fontSize: "92px",
    lineHeight: 0.88, letterSpacing: "-0.02em", margin: "0 0 28px",
  },
  blue: { color: "var(--lp-blue)" },
  lede: {
    fontFamily: "var(--font-serif)", fontSize: "23px", lineHeight: 1.5,
    maxWidth: "40ch", color: "var(--text-body)", margin: "0 0 36px",
  },
  ctaRow: { display: "flex", gap: "16px", alignItems: "center" },
  art: { display: "flex", justifyContent: "center" },
  artImg: { width: "100%", maxWidth: "360px", height: "auto" },

  worksHead: {
    display: "flex", justifyContent: "space-between", alignItems: "baseline",
    padding: "0 var(--page-margin)", borderTop: "1px solid var(--border-hairline)",
    paddingTop: "var(--space-7)",
  },
  worksTitle: { fontFamily: "var(--font-serif)", fontWeight: 400, fontSize: "32px", letterSpacing: "-0.01em" },
  grid: {
    display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "28px",
    padding: "var(--space-6) var(--page-margin) var(--space-10)",
  },
};

function HomeScreen({ go }) {
  const { Button, Tag, Card, TextLink } = window.LastPlaceDesignSystem_2f29fe;
  const projects = window.LP_PROJECTS.slice(0, 3);
  return (
    <div>
      <section style={homeStyles.hero}>
        <div>
          <div style={homeStyles.eyebrow}>Web design studio — est. 2022</div>
          <h1 style={homeStyles.h1}>
            We are<br />Last <span style={homeStyles.blue}>Place</span>.
          </h1>
          <p style={homeStyles.lede}>
            A small studio that likes a lot of white space, a single confident
            blue, and websites that age well. We come last on purpose.
          </p>
          <div style={homeStyles.ctaRow}>
            <Button variant="primary" onClick={() => go("contact")}>Start a project</Button>
            <Button variant="link" onClick={() => go("work")}>see selected work</Button>
          </div>
        </div>
        <div style={homeStyles.art}>
          <img src="../../assets/plant-mark-blue-knockout.png" alt="Last Place plant mark" style={homeStyles.artImg} />
        </div>
      </section>

      <div style={homeStyles.worksHead}>
        <span style={homeStyles.worksTitle}>Selected works</span>
        <TextLink onClick={() => go("work")} arrow>The full index</TextLink>
      </div>
      <section style={homeStyles.grid}>
        {projects.map((p) => (
          <Card
            key={p.id}
            href="#"
            onClick={(e) => { e.preventDefault(); go("work"); }}
            eyebrow={p.tags.join(" · ")}
            title={p.title}
            meta={`${p.year} — ${p.client}`}
            mediaBg={window.LP_WELL(p.well).background}
            media={
              <div style={{ ...window.LP_WELL(p.well), width: "100%", height: "100%", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "var(--font-serif)", fontWeight: 300, fontSize: "72px" }}>
                {p.initials}
              </div>
            }
          >
            {p.blurb}
          </Card>
        ))}
      </section>
    </div>
  );
}

window.HomeScreen = HomeScreen;
