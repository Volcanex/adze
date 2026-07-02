const workStyles = {
  head: { padding: "var(--space-9) var(--page-margin) var(--space-6)" },
  eyebrow: {
    fontFamily: "var(--font-mono)", fontSize: "11.5px", letterSpacing: "0.2em",
    textTransform: "uppercase", color: "var(--text-muted)", marginBottom: "20px",
  },
  h1: { fontFamily: "var(--font-serif)", fontWeight: 300, fontSize: "72px", lineHeight: 0.92, letterSpacing: "-0.02em", margin: "0 0 18px" },
  lede: { fontFamily: "var(--font-serif)", fontSize: "21px", lineHeight: 1.5, maxWidth: "46ch", color: "var(--text-muted)", margin: 0 },
  list: { padding: "0 var(--page-margin) var(--space-10)" },
  row: {
    display: "grid", gridTemplateColumns: "64px 1fr auto 140px 40px",
    alignItems: "baseline", gap: "24px",
    padding: "26px 0", borderTop: "1px solid var(--border-hairline)",
    cursor: "pointer", textDecoration: "none", color: "var(--text-body)",
    transition: "padding-left var(--dur-base) var(--ease-out)",
  },
  num: { fontFamily: "var(--font-mono)", fontSize: "13px", color: "var(--text-faint)" },
  title: { fontFamily: "var(--font-serif)", fontSize: "40px", lineHeight: 1, letterSpacing: "-0.01em" },
  tags: { display: "flex", gap: "10px" },
  year: { fontFamily: "var(--font-mono)", fontSize: "13px", color: "var(--text-muted)", textAlign: "right" },
  arrow: { fontFamily: "var(--font-serif)", fontSize: "28px", color: "var(--lp-blue)", textAlign: "right" },
};

function WorkScreen({ go }) {
  const { Tag } = window.LastPlaceDesignSystem_2f29fe;
  const [hover, setHover] = React.useState(null);
  return (
    <div>
      <header style={workStyles.head}>
        <div style={workStyles.eyebrow}>Index — selected works</div>
        <h1 style={workStyles.h1}>Things we have made.</h1>
        <p style={workStyles.lede}>
          Identities and websites for arts, culture, and quietly ambitious
          businesses. A representative few — ask us for the rest.
        </p>
      </header>
      <div style={workStyles.list}>
        {window.LP_PROJECTS.map((p, i) => (
          <a
            key={p.id}
            href="#"
            onClick={(e) => { e.preventDefault(); go("contact"); }}
            onMouseEnter={() => setHover(p.id)}
            onMouseLeave={() => setHover(null)}
            style={{
              ...workStyles.row,
              paddingLeft: hover === p.id ? "16px" : "0",
              borderTopColor: hover === p.id ? "var(--lp-black)" : "var(--border-hairline)",
            }}
          >
            <span style={workStyles.num}>{String(i + 1).padStart(2, "0")}</span>
            <span style={{ ...workStyles.title, color: hover === p.id ? "var(--lp-blue)" : "var(--text-body)", transition: "color var(--dur-fast) var(--ease-out)" }}>{p.title}</span>
            <span style={workStyles.tags}>{p.tags.map((t) => <Tag key={t} tone="muted">{t}</Tag>)}</span>
            <span style={workStyles.year}>{p.year} — {p.client}</span>
            <span style={{ ...workStyles.arrow, opacity: hover === p.id ? 1 : 0.25, transition: "opacity var(--dur-fast) var(--ease-out)" }}>↳</span>
          </a>
        ))}
      </div>
    </div>
  );
}

window.WorkScreen = WorkScreen;
