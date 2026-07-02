// Shared fake project data for the Last Place studio site.
window.LP_PROJECTS = [
  { id: "onwards", title: "Onwards Norfolk", tags: ["Branding", "Web"], year: "2025", client: "Norfolk BIDs", well: "blue", initials: "ON", blurb: "An events platform and identity for the Norfolk district." },
  { id: "marsh", title: "Marsh & Co.", tags: ["Identity"], year: "2025", client: "Marsh & Co.", well: "ink", initials: "M&", blurb: "A wordmark and stationery for a coastal architecture practice." },
  { id: "behrens", title: "Behrens Typography", tags: ["Web", "Editorial"], year: "2024", client: "HSD Düsseldorf", well: "paper", initials: "BT", blurb: "A teaching archive for a design-history workshop series." },
  { id: "field", title: "Field Recordings", tags: ["Web", "Sound"], year: "2024", client: "Independent", well: "blue", initials: "FR", blurb: "A quiet listening site for a location-sound label." },
  { id: "almanac", title: "The Slow Almanac", tags: ["Editorial"], year: "2023", client: "Almanac Press", well: "ink", initials: "SA", blurb: "An annual of essays, set entirely in one serif." },
  { id: "verge", title: "Verge Garden Co.", tags: ["Branding", "Web"], year: "2023", client: "Verge", well: "paper", initials: "VG", blurb: "Identity and shop for a wild-planting nursery." },
];

window.LP_WELL = function (kind) {
  if (kind === "ink") return { background: "var(--lp-black)", color: "#fff" };
  if (kind === "paper") return { background: "var(--lp-paper)", color: "var(--lp-blue)", border: "1px solid var(--border-hairline)" };
  return { background: "var(--lp-blue)", color: "#fff" };
};
