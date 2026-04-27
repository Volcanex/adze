---
title: "Our Locations - Wild Saunas Ireland"
---

<html>

<!-- Navigation -->
<nav>
  <div class="nav-container">
    <div class="nav-content">
      <a href="../home/" class="logo">
        <i data-lucide="flame" style="color: hsl(var(--accent)); width: 1.75rem; height: 1.75rem;"></i>
        <span>Wild Saunas</span>
      </a>
      
      <div class="nav-links">
        <a href="../locations/" class="active">Locations</a>
        <a href="../learning/">Learning</a>
        <a href="../cairde/">Cairde</a>
      </div>
      
      <div class="nav-actions">
        <a href="../book-session/" class="btn btn-primary">Book Now</a>
        <button class="btn btn-ghost btn-icon mobile-menu-btn" onclick="alert('Mobile menu')">
          <i data-lucide="menu" style="width: 1.25rem; height: 1.25rem;"></i>
        </button>
      </div>
    </div>
  </div>
</nav>

<main class="max-w-6xl mx-auto px-4 py-8">
  <a href="../home/" class="btn btn-ghost btn-sm mb-6" style="display: inline-flex;">
    <i data-lucide="arrow-left" style="width: 1rem; height: 1rem; margin-right: 0.5rem;"></i>
    Back to Home
  </a>

  <h1 class="font-serif text-3xl font-bold mb-2">Our Locations</h1>
  <p class="text-muted-foreground mb-8">
    Discover wild saunas across Ireland's most breathtaking landscapes
  </p>

  <div id="locations-container" style="margin-bottom: 2rem;">
    <!-- Loading skeletons -->
    <div class="skeleton" style="height: 24rem; margin-bottom: 2rem; border-radius: 0.5rem;"></div>
    <div class="skeleton" style="height: 24rem; margin-bottom: 2rem; border-radius: 0.5rem;"></div>
  </div>
</main>

<script src="https://unpkg.com/lucide@latest/dist/umd/lucide.min.js"></script>
<script>
const API = '/api/artists/chris';

// Initialize Lucide icons
if (typeof lucide !== 'undefined') {
  lucide.createIcons();
}

async function loadLocations() {
  try {
    const [locsRes, saunasRes] = await Promise.all([
      fetch(API + '/locations'),
      fetch(API + '/saunas')
    ]);
    const locations = await locsRes.json();
    const saunas = await saunasRes.json();
    
    const container = document.getElementById('locations-container');
    
    container.innerHTML = locations.map(loc => {
      const locationSaunas = saunas.filter(s => s.location_id === loc.id);
      return `
        <div class="card" style="overflow: hidden; margin-bottom: 2rem;">
          <div class="grid md\\:grid-cols-2">
            <div style="height: 16rem; background: hsl(var(--muted)); overflow: hidden;">
              ${loc.image_url ? `
                <img src="${loc.image_url}" alt="${loc.name}" style="width: 100%; height: 100%; object-fit: cover;">
              ` : `
                <div style="width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; background: linear-gradient(to bottom right, hsla(var(--primary), 0.2), hsla(var(--accent), 0.2));">
                  <i data-lucide="map-pin" style="width: 4rem; height: 4rem; color: hsla(var(--muted-foreground), 0.3);"></i>
                </div>
              `}
            </div>
            <div style="padding: 1.5rem;">
              <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem; margin-bottom: 0.75rem;">
                <h2 class="font-serif text-2xl font-semibold">${loc.name}</h2>
                <span class="badge" style="flex-shrink: 0;">
                  ${locationSaunas.length} ${locationSaunas.length === 1 ? 'sauna' : 'saunas'}
                </span>
              </div>
              <p class="text-muted-foreground mb-2" style="display: flex; align-items: center; gap: 0.25rem;">
                <i data-lucide="map-pin" style="width: 1rem; height: 1rem;"></i>
                ${loc.address}
              </p>
              ${loc.description ? `
                <p class="text-muted-foreground mb-6">${loc.description}</p>
              ` : ''}
              
              <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
                <a href="../location-${loc.id}/" class="btn btn-primary">
                  View Details
                  <i data-lucide="arrow-right" style="width: 1rem; height: 1rem; margin-left: 0.5rem;"></i>
                </a>
                <span class="text-sm text-muted-foreground">
                  ${locationSaunas.length} ${locationSaunas.length === 1 ? 'sauna' : 'saunas'} available
                </span>
              </div>
              
              ${locationSaunas.length > 0 ? `
                <div style="margin-top: 1rem;">
                  <h3 class="font-medium text-sm text-muted-foreground" style="text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">
                    Quick Book
                  </h3>
                  ${locationSaunas.slice(0, 2).map(sauna => `
                    <a href="../book-session/?sauna=${sauna.id}" style="text-decoration: none;">
                      <div class="card card-hover" style="padding: 0.75rem; margin-bottom: 0.5rem; cursor: pointer;">
                        <div style="display: flex; justify-content: space-between; align-items: center; gap: 1rem;">
                          <div>
                            <h4 class="font-medium text-sm">${sauna.name}</h4>
                            <p class="text-xs text-muted-foreground" style="display: flex; align-items: center; gap: 0.25rem;">
                              <i data-lucide="users" style="width: 0.75rem; height: 0.75rem;"></i>
                              Up to ${sauna.capacity} guests • €${sauna.price_per_seat}/seat
                            </p>
                          </div>
                          <i data-lucide="arrow-right" style="width: 1rem; height: 1rem; color: hsl(var(--muted-foreground));"></i>
                        </div>
                      </div>
                    </a>
                  `).join('')}
                </div>
              ` : ''}
            </div>
          </div>
        </div>
      `;
    }).join('');
    
    lucide.createIcons();
  } catch (err) {
    console.error('Failed to load locations:', err);
    document.getElementById('locations-container').innerHTML = `
      <div class="card" style="padding: 3rem; text-align: center;">
        <i data-lucide="map-pin" style="width: 4rem; height: 4rem; color: hsla(var(--muted-foreground), 0.5); margin: 0 auto 1rem;"></i>
        <h3 class="font-serif text-xl font-semibold mb-2">No locations yet</h3>
        <p class="text-muted-foreground">Check back soon for new wild sauna locations across Ireland!</p>
      </div>
    `;
    lucide.createIcons();
  }
}

loadLocations();
</script>
</html>
