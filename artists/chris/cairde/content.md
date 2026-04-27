<meta property="og:title" content="Cairde - Our People - Wild Saunas Ireland">
<meta property="og:description" content="Meet the passionate people behind Wild Saunas Ireland. Book special sessions with our expert guides">

<style>
.header { padding: 6rem 1.5rem 3rem; text-align: center; background: var(--bg); }
.section { padding: 3rem 1.5rem; max-width: 1280px; margin: 0 auto; }
.grid { display: grid; gap: 3rem; }
@media (min-width: 768px) { .grid { grid-template-columns: repeat(2, 1fr); } }
@media (min-width: 1024px) { .grid { grid-template-columns: repeat(3, 1fr); } }
.cairde-card { background: white; border-radius: 8px; overflow: hidden; transition: transform 0.3s; border: 1px solid var(--border); }
.cairde-card:hover { transform: translateY(-6px); box-shadow: 0 12px 24px rgba(0,0,0,0.1); }
.cairde-img { width: 100%; height: 320px; object-fit: cover; }
.cairde-content { padding: 2rem; }
.cairde-name { font-size: 1.5rem; margin-bottom: 0.5rem; }
.cairde-role { color: var(--accent); font-weight: 600; font-size: 1rem; margin-bottom: 1rem; }
.cairde-bio { color: var(--muted-foreground); font-size: 0.875rem; line-height: 1.6; margin-bottom: 1.5rem; }
.session-list { margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid var(--border); }
.session-item { padding: 1rem; background: var(--bg); border-radius: 6px; margin-bottom: 0.75rem; }
.skeleton { background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%); background-size: 200% 100%; animation: loading 1.5s infinite; border-radius: 8px; }
@keyframes loading { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }
</style>

<html>
<div class="header">
    <h1 style="margin-bottom: 1rem;">Cairde — Our People</h1>
    <p style="color: var(--muted-foreground); font-size: 1.25rem; max-width: 42rem; margin: 0 auto;">
        Meet the passionate people behind Wild Saunas Ireland. Each brings unique expertise and offers special bookable sessions combining sauna with their craft.
    </p>
</div>

<section class="section">
    <div class="grid" id="cairde-grid">
        <div class="skeleton" style="height: 500px;"></div>
        <div class="skeleton" style="height: 500px;"></div>
        <div class="skeleton" style="height: 500px;"></div>
    </div>
</section>

<div style="padding: 4rem 1.5rem; text-align: center; background: var(--accent); color: white;">
    <h2 style="color: white; margin-bottom: 1rem;">Experience Something Special</h2>
    <p style="margin-bottom: 2rem; opacity: 0.95; max-width: 32rem; margin-left: auto; margin-right: auto;">
        Book a unique session with one of our cairde members and deepen your sauna practice
    </p>
    <a href="../book-cairde/"><button class="btn" style="background: white; color: var(--accent); font-size: 1.125rem; padding: 1rem 2rem;">Book Cairde Session</button></a>
</div>

<script>
const API = '/api/artists/chris';

async function loadCairde() {
    try {
        const res = await fetch(API + '/cairde');
        if (!res.ok) throw new Error('Failed to fetch');
        const cairde = await res.json();

        const grid = document.getElementById('cairde-grid');
        grid.innerHTML = cairde.map(person => `
            <div class="cairde-card">
                <img src="${person.image_url || '../assets/images/cairde/default.jpg'}" class="cairde-img" alt="${person.name}">
                <div class="cairde-content">
                    <h2 class="cairde-name">${person.name}</h2>
                    <p class="cairde-role">${person.role}</p>
                    ${person.bio ? `<p class="cairde-bio">${person.bio}</p>` : ''}

                    ${person.sessions && person.sessions.length ? `
                        <div class="session-list">
                            <h3 style="font-size: 1rem; margin-bottom: 1rem; color: var(--muted-foreground);">
                                Special Sessions (${person.sessions.length})
                            </h3>
                            ${person.sessions.map(s => `
                                <div class="session-item">
                                    <h4 style="font-size: 0.875rem; font-weight: 600; margin-bottom: 0.5rem;">${s.title}</h4>
                                    <p style="font-size: 0.75rem; color: var(--muted-foreground); margin-bottom: 0.5rem;">${s.description || ''}</p>
                                    <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.75rem;">
                                        <span>⏱️ ${s.duration}</span>
                                        <span style="font-weight: 600; color: var(--primary);">€${s.price}</span>
                                    </div>
                                </div>
                            `).join('')}
                            <a href="../book-cairde/?member=${person.id}">
                                <button class="btn" style="width: 100%; margin-top: 1rem;">Book Session</button>
                            </a>
                        </div>
                    ` : ''}
                </div>
            </div>
        `).join('');
    } catch (err) {
        console.error('Error loading cairde:', err);
        document.getElementById('cairde-grid').innerHTML = '<p style="grid-column: 1/-1; text-align: center;">Unable to load cairde members</p>';
    }
}

window.addEventListener('DOMContentLoaded', loadCairde);
</script>
</html>
