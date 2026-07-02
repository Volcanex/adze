const contactStyles = {
  wrap: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: "64px", padding: "var(--space-9) var(--page-margin) var(--space-10)", alignItems: "start" },
  eyebrow: { fontFamily: "var(--font-mono)", fontSize: "11.5px", letterSpacing: "0.2em", textTransform: "uppercase", color: "var(--text-muted)", marginBottom: "24px" },
  big: { fontFamily: "var(--font-serif)", fontWeight: 300, fontSize: "60px", lineHeight: 0.94, letterSpacing: "-0.02em", margin: "0 0 28px", maxWidth: "12ch" },
  blue: { color: "var(--lp-blue)" },
  p: { fontFamily: "var(--font-serif)", fontSize: "19px", lineHeight: 1.6, color: "var(--text-muted)", maxWidth: "40ch", margin: "0 0 32px" },
  detail: { fontFamily: "var(--font-mono)", fontSize: "13px", letterSpacing: "0.04em", color: "var(--text-body)", lineHeight: 2 },
  form: { display: "flex", flexDirection: "column", gap: "28px" },
  budgetRow: { display: "flex", gap: "10px", flexWrap: "wrap" },
  chip: (on) => ({
    fontFamily: "var(--font-mono)", fontSize: "12px", letterSpacing: "0.1em",
    padding: "8px 14px", cursor: "pointer", border: "1px solid",
    borderColor: on ? "var(--lp-blue)" : "var(--border-strong)",
    background: on ? "var(--lp-blue)" : "transparent",
    color: on ? "#fff" : "var(--lp-black)",
    transition: "all var(--dur-fast) var(--ease-out)",
  }),
  chipLabel: { fontFamily: "var(--font-mono)", fontSize: "11px", letterSpacing: "0.18em", textTransform: "uppercase", color: "var(--text-muted)", marginBottom: "12px", display: "block" },
  sent: { fontFamily: "var(--font-serif)", fontSize: "26px", color: "var(--lp-green)", lineHeight: 1.4 },
};

function ContactScreen() {
  const { Field, Checkbox, Button } = window.LastPlaceDesignSystem_2f29fe;
  const [budget, setBudget] = React.useState("£5–10k");
  const [keep, setKeep] = React.useState(true);
  const [sent, setSent] = React.useState(false);
  const budgets = ["< £5k", "£5–10k", "£10–25k", "£25k +"];
  return (
    <section style={contactStyles.wrap}>
      <div>
        <div style={contactStyles.eyebrow}>Contact</div>
        <h1 style={contactStyles.big}>Let's make something <span style={contactStyles.blue}>quiet</span> and good.</h1>
        <p style={contactStyles.p}>
          Tell us a little about the project. A sentence or two is plenty — we
          reply within a day, and there's no harm in just saying hello.
        </p>
        <div style={contactStyles.detail}>
          hello@lastplace.co.uk<br />
          +44 (0)20 7946 0102<br />
          Bradford · United Kingdom
        </div>
      </div>

      <div>
        {sent ? (
          <p style={contactStyles.sent}>Thank you — that's landed.<br />We'll be in touch within a day. ↳</p>
        ) : (
          <form style={contactStyles.form} onSubmit={(e) => { e.preventDefault(); setSent(true); }}>
            <Field label="Your name" placeholder="Jane Appleseed" />
            <Field label="Email" type="email" placeholder="you@studio.com" />
            <div>
              <span style={contactStyles.chipLabel}>Budget</span>
              <div style={contactStyles.budgetRow}>
                {budgets.map((b) => (
                  <span key={b} style={contactStyles.chip(budget === b)} onClick={() => setBudget(b)}>{b}</span>
                ))}
              </div>
            </div>
            <Field label="Tell us about the project" multiline placeholder="A sentence or two is plenty." />
            <Checkbox checked={keep} onChange={setKeep} label="Keep me posted on studio news" />
            <div>
              <Button variant="primary" type="submit">Send it our way</Button>
            </div>
          </form>
        )}
      </div>
    </section>
  );
}

window.ContactScreen = ContactScreen;
