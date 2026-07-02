const footerStyles = {
  wrap: {
    borderTop: "1px solid var(--border-hairline)",
    padding: "var(--space-9) var(--page-margin) var(--space-7)",
    display: "grid",
    gridTemplateColumns: "1.5fr 1fr 1fr",
    gap: "40px",
    alignItems: "start",
  },
  big: {
    fontFamily: "var(--font-serif)", fontWeight: 300, fontSize: "44px",
    lineHeight: 0.92, letterSpacing: "-0.015em", margin: 0, maxWidth: "12ch",
  },
  col: { display: "flex", flexDirection: "column", gap: "10px" },
  label: {
    fontFamily: "var(--font-mono)", fontSize: "11px", letterSpacing: "0.2em",
    textTransform: "uppercase", color: "var(--text-faint)", marginBottom: "6px",
  },
  line: { fontFamily: "var(--font-serif)", fontSize: "17px" },
  base: {
    gridColumn: "1 / -1", display: "flex", justifyContent: "space-between",
    borderTop: "1px solid var(--border-hairline)", paddingTop: "20px",
    marginTop: "20px", fontFamily: "var(--font-mono)", fontSize: "11px",
    letterSpacing: "0.12em", textTransform: "uppercase", color: "var(--text-faint)",
  },
};

function Footer({ go }) {
  const { TextLink } = window.LastPlaceDesignSystem_2f29fe;
  return (
    <footer style={footerStyles.wrap}>
      <h2 style={footerStyles.big}>Last but not least.</h2>
      <div style={footerStyles.col}>
        <span style={footerStyles.label}>Studio</span>
        <span style={footerStyles.line}><a onClick={() => go("work")} style={{cursor:"pointer"}}>Work</a></span>
        <span style={footerStyles.line}><a onClick={() => go("studio")} style={{cursor:"pointer"}}>About</a></span>
        <span style={footerStyles.line}><a onClick={() => go("contact")} style={{cursor:"pointer"}}>Contact</a></span>
      </div>
      <div style={footerStyles.col}>
        <span style={footerStyles.label}>Elsewhere</span>
        <span style={footerStyles.line}><TextLink href="#">Instagram</TextLink></span>
        <span style={footerStyles.line}><TextLink href="#">Are.na</TextLink></span>
        <span style={footerStyles.line}><TextLink href="#">hello@lastplace.co.uk</TextLink></span>
      </div>
      <div style={footerStyles.base}>
        <span>© Last Place {new Date().getFullYear()}</span>
        <span>Made last, with care</span>
      </div>
    </footer>
  );
}

window.Footer = Footer;
