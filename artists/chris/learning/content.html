<meta property="og:title" content="Learning & Events - Wild Saunas Ireland">
<meta property="og:description" content="Discover courses, retreats, and events combining sauna with mindfulness, yoga, breathwork, and self-development">

<style>
.header { padding: 6rem 1.5rem 3rem; text-align: center; background: var(--bg); }
.section { padding: 2rem 1.5rem; max-width: 1280px; margin: 0 auto; }
.filters { display: flex; gap: 1rem; flex-wrap: wrap; justify-content: center; margin-bottom: 3rem; }
.filter-btn { padding: 0.75rem 1.5rem; border: 2px solid var(--border); background: white; border-radius: 8px; cursor: pointer; transition: all 0.2s; }
.filter-btn:hover { border-color: var(--accent); }
.filter-btn.active { background: var(--accent); color: white; border-color: var(--accent); }
.grid { display: grid; gap: 2rem; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); }
.learning-card { background: white; border-radius: 8px; overflow: hidden; transition: transform 0.3s; border: 1px solid var(--border); }
.learning-card:hover { transform: translateY(-4px); box-shadow: 0 8px 16px rgba(0,0,0,0.1); }
.learning-img { width: 100%; height: 220px; object-fit: cover; }
.badge { display: inline-block; background: var(--accent); color: white; font-size: 0.75rem; padding: 0.375rem 0.75rem; border-radius: 4px; font-weight: 600; }
.badge.type { background: var(--bg-muted); color: var(--foreground); }
.skeleton { background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%); background-size: 200% 100%; animation: loading 1.5s infinite; border-radius: 8px; }
@keyframes loading { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }
</style>

<html>
<div class="header">
    <h1 style="margin-bottom: 1rem;">Learning & Events</h1>
    <p style="color: var(--muted-foreground); font-size: 1.25rem; max-width: 42rem; margin: 0 auto;">
        Grow through sauna experiences. Explore our courses, retreats, and special events combining traditional sauna with mindfulness, yoga, breathwork, and self-development.
    </p>
</div>

<section class="section">
    <div class="filters">
        <button class="filter-btn active" data-filter="all">All</button>
        <button class="filter-btn" data-filter="course">Courses</button>
        <button class="filter-btn" data-filter="retreat">Retreats</button>
        <button class="filter-btn" data-filter="event">Events</button>
    </div>

    <div class="grid" id="learning-grid">
        <div class="skeleton" style="height: 400px;"></div>
        <div class="skeleton" style="height: 400px;"></div>
        <div class="skeleton" style="height: 400px;"></div>
        <div class="skeleton" style="height: 400px;"></div>
    </div>

    <div id="empty-state" style="display: none; text-align: center; padding: 4rem 1rem; color: var(--muted-foreground);">
        <p style="font-size: 1.125rem;">No items found for this filter</p>
    </div>
</section>

<div style="padding: 4rem 1.5rem; text-align: center; background: var(--bg-muted);">
    <h2 style="margin-bottom: 1rem;">Questions About Our Learning Programs?</h2>
    <p style="color: var(--muted-foreground); margin-bottom: 2rem; max-width: 32rem; margin-left: auto; margin-right: auto;">
        Get in touch to learn more about our courses, retreats, and events. We're here to help you find the perfect experience.
    </p>
    <a href="../book/"><button class="btn-outline" style="font-size: 1.125rem; padding: 1rem 2rem;">Explore Booking Options</button></a>
</div>

<script>
const API = '/api/artists/chris';
let allItems = [];
let currentFilter = 'all';

async function loadLearning() {
    try {
        const res = await fetch(API + '/learning');
        if (!res.ok) throw new Error('Failed to fetch');
        allItems = await res.json();
        renderItems();
    } catch (err) {
        console.error('Error loading learning items:', err);
        document.getElementById('learning-grid').innerHTML = '<p style="grid-column: 1/-1; text-align: center;">Unable to load learning items</p>';
    }
}

function renderItems() {
    const filtered = currentFilter === 'all' ? allItems : allItems.filter(i => i.type === currentFilter);
    const grid = document.getElementById('learning-grid');
    const emptyState = document.getElementById('empty-state');

    if (filtered.length === 0) {
        grid.style.display = 'none';
        emptyState.style.display = 'block';
        return;
    }

    grid.style.display = 'grid';
    emptyState.style.display = 'none';

    grid.innerHTML = filtered.map(item => `
        <div class="learning-card">
            ${item.image_url ? `<img src="${item.image_url}" class="learning-img" alt="${item.title}">` : ''}
            <div style="padding: 1.5rem;">
                <div style="display: flex; gap: 0.5rem; margin-bottom: 1rem; flex-wrap: wrap;">
                    <span class="badge">${item.category || 'general'}</span>
                    <span class="badge type">${item.type}</span>
                </div>
                <h3 style="font-size: 1.25rem; margin-bottom: 0.75rem; line-height: 1.3;">${item.title}</h3>
                <p style="color: var(--muted-foreground); font-size: 0.875rem; margin-bottom: 1rem; line-height: 1.6;">
                    ${item.description || ''}
                </p>
                <div style="display: flex; justify-content: space-between; align-items: center; padding-top: 1rem; border-top: 1px solid var(--border);">
                    <span style="font-size: 0.875rem; color: var(--muted-foreground);">⏱️ ${item.duration}</span>
                    <span style="font-weight: 600; font-size: 1.125rem; color: var(--primary);">€${item.price}</span>
                </div>
                <a href="../book-learning/?item=${item.id}">
                    <button class="btn" style="width: 100%; margin-top: 1rem;">Book Now</button>
                </a>
            </div>
        </div>
    `).join('');
}

function setupFilters() {
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentFilter = btn.dataset.filter;
            renderItems();
        });
    });
}

window.addEventListener('DOMContentLoaded', () => {
    loadLearning();
    setupFilters();
});
</script>
</html>
