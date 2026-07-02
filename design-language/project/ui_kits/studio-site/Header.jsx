const LP = window.LastPlaceDesignSystem_2f29fe;

const headerStyles = {
  bar: {
    position: "sticky",
    top: 0,
    zIndex: 10,
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "20px var(--page-margin)",
    background: "rgba(255,255,255,0.86)",
    backdropFilter: "saturate(180%) blur(8px)",
    borderBottom: "1px solid var(--border-hairline)",
  },
  brand: { display: "flex", alignItems: "center", gap: "14px", cursor: "pointer" },
  mono: {
    width: "34px", height: "34px", background: "var(--lp-blue)", color: "#fff",
    display: "flex", alignItems: "center", justifyContent: "center",
    fontFamily: "var(--font-serif)", fontWeight: 300, fontSize: "20px", lineHeight: 1,
  },
  word: { fontFamily: "var(--font-serif)", fontSize: "21px", letterSpacing: "0.01em" },
  nav: { display: "flex", gap: "32px", alignItems: "center" },
  link: (active) => ({
    fontFamily: "var(--font-mono)", fontSize: "11.5px", letterSpacing: "0.2em",
    textTransform: "uppercase", textDecoration: "none", cursor: "pointer",
    color: active ? "var(--lp-blue)" : "var(--lp-black)",
    transition: "color var(--dur-fast) var(--ease-out)",
  }),
};

function Header({ route, go }) {
  const items = [
    ["home", "Index"],
    ["work", "Work"],
    ["studio", "Studio"],
    ["contact", "Contact"],
  ];
  return (
    <header style={headerStyles.bar}>
      <div style={headerStyles.brand} onClick={() => go("home")}>
        <div style={headerStyles.word}>Last Place</div>
      </div>
      <nav style={headerStyles.nav}>
        {items.map(([key, label]) => (
          <a
            key={key}
            style={headerStyles.link(route === key)}
            onClick={() => go(key)}
            onMouseEnter={(e) => (e.currentTarget.style.color = "var(--lp-blue)")}
            onMouseLeave={(e) => (e.currentTarget.style.color = route === key ? "var(--lp-blue)" : "var(--lp-black)")}
          >
            {label}
          </a>
        ))}
      </nav>
    </header>
  );
}

window.Header = Header;
