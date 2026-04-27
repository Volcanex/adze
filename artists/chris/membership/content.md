<meta property="og:title" content="Membership - Wild Saunas Ireland">
<meta property="og:description" content="Become a Wild Saunas member and enjoy exclusive benefits, priority booking, and savings">

<style>
.header { padding: 6rem 1.5rem 3rem; text-align: center; background: var(--bg); }
.section { padding: 3rem 1.5rem; max-width: 1100px; margin: 0 auto; }
.grid { display: grid; gap: 2rem; }
@media (min-width: 768px) { .grid { grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); } }
.membership-card { background: white; border: 2px solid var(--border); border-radius: 12px; padding: 2.5rem; transition: all 0.3s; position: relative; overflow: hidden; }
.membership-card.featured { border-color: var(--accent); box-shadow: 0 8px 24px rgba(122,138,110,0.15); transform: scale(1.05); }
.membership-card.featured::before { content: 'Most Popular'; position: absolute; top: 1rem; right: -2rem; background: var(--accent); color: white; padding: 0.25rem 3rem; transform: rotate(45deg); font-size: 0.75rem; font-weight: 600; }
.membership-card:hover { transform: translateY(-4px); box-shadow: 0 12px 28px rgba(0,0,0,0.12); }
.membership-card.featured:hover { transform: scale(1.05) translateY(-4px); }
.price-tag { font-size: 3rem; font-weight: 700; color: var(--primary); margin: 1.5rem 0; }
.price-tag span { font-size: 1rem; color: var(--muted-foreground); font-weight: 400; }
.features-list { list-style: none; margin: 2rem 0; }
.features-list li { padding: 0.875rem 0; display: flex; align-items: flex-start; gap: 0.75rem; border-bottom: 1px solid var(--bg-muted); }
.features-list li:last-child { border-bottom: none; }
.check-icon { width: 20px; height: 20px; border-radius: 50%; background: var(--accent); color: white; display: flex; align-items: center; justify-content: center; flex-shrink: 0; font-size: 0.75rem; }
.skeleton { background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%); background-size: 200% 100%; animation: loading 1.5s infinite; border-radius: 12px; }
@keyframes loading { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }
</style>

<html>
<div class="header">
    <h1 style="margin-bottom: 1rem;">Membership Plans</h1>
    <p style="color: var(--muted-foreground); font-size: 1.25rem; max-width: 42rem; margin: 0 auto;">
        Join Wild Saunas Ireland and enjoy exclusive member benefits, priority booking, and significant savings on your sauna sessions.
    </p>
</div>

<section class="section">
    <div class="grid" id="memberships-grid">
        <div class="skeleton" style="height: 550px;"></div>
        <div class="skeleton" style="height: 550px;"></div>
        <div class="skeleton" style="height: 550px;"></div>
    </div>
</section>

<div style="padding: 4rem 1.5rem; background: var(--bg-muted); text-align: center;">
    <h2 style="margin-bottom: 1rem;">Not Ready to Commit?</h2>
    <p style="color: var(--muted-foreground); margin-bottom: 2rem; max-width: 32rem; margin-left: auto; margin-right: auto;">
        You can always book individual sessions as a pay-as-you-go visitor. Try us out first!
    </p>
    <a href="../book-session/"><button class="btn-outline" style="font-size: 1.125rem; padding: 1rem 2rem;">Book Single Session</button></a>
</div>

<script>
const API = '/api/artists/chris';

async function loadMemberships() {
    try {
        const res = await fetch(API + '/memberships');
        if (!res.ok) throw new Error('Failed to fetch');
        const memberships = await res.json();

        const grid = document.getElementById('memberships-grid');

        // Determine which one is featured (middle price tier)
        const sorted = [...memberships].sort((a,b) => parseFloat(a.monthly_price) - parseFloat(b.monthly_price));
        const featuredId = sorted[Math.floor(sorted.length / 2)]?.id;

        grid.innerHTML = sorted.map(m => `
            <div class="membership-card ${m.id === featuredId ? 'featured' : ''}">
                <h2 style="font-size: 1.875rem; margin-bottom: 0.5rem;">${m.name}</h2>
                <p style="color: var(--muted-foreground); margin-bottom: 1rem;">${m.description || ''}</p>

                <div class="price-tag">
                    €${m.monthly_price}<span>/month</span>
                </div>

                <ul class="features-list">
                    ${m.sessions_per_month ? `
                        <li>
                            <span class="check-icon">✓</span>
                            <span><strong>${m.sessions_per_month} sauna sessions</strong> per month included</span>
                        </li>
                    ` : `
                        <li>
                            <span class="check-icon">✓</span>
                            <span><strong>Unlimited sessions</strong> - visit as often as you like</span>
                        </li>
                    `}
                    <li>
                        <span class="check-icon">✓</span>
                        <span>Priority booking access</span>
                    </li>
                    ${m.discount_percent > 0 ? `
                        <li>
                            <span class="check-icon">✓</span>
                            <span><strong>${m.discount_percent}% discount</strong> on additional sessions</span>
                        </li>
                    ` : ''}
                    <li>
                        <span class="check-icon">✓</span>
                        <span>Bring guests at member rates</span>
                    </li>
                    <li>
                        <span class="check-icon">✓</span>
                        <span>Cancel anytime</span>
                    </li>
                    <li>
                        <span class="check-icon">✓</span>
                        <span>Member-only events & workshops</span>
                    </li>
                </ul>

                <button class="btn ${m.id === featuredId ? '' : 'btn-outline'}" style="width: 100%; font-size: 1.125rem; padding: 1rem; ${m.id === featuredId ? 'background: var(--accent);' : ''}">
                    Choose ${m.name}
                </button>
            </div>
        `).join('');
    } catch (err) {
        console.error('Error loading memberships:', err);
        document.getElementById('memberships-grid').innerHTML = '<p style="grid-column: 1/-1; text-align: center;">Unable to load membership plans</p>';
    }
}

window.addEventListener('DOMContentLoaded', loadMemberships);
</script>
</html>
