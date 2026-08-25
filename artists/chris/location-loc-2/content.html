---
title: "Location Details - Wild Saunas Ireland"
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
        <a href="../locations/">Locations</a>
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

<!-- Hero Section -->
<div id="hero-section" style="position: relative; height: 20rem; overflow: hidden;">
  <div class="skeleton" style="position: absolute; inset: 0;"></div>
</div>

<main class="max-w-6xl mx-auto px-4 py-12">
  <!-- Book Button -->
  <div id="book-button" style="display: flex; flex-wrap: wrap; gap: 1rem; margin-bottom: 3rem;">
    <div class="skeleton" style="height: 3rem; width: 16rem; border-radius: 0.375rem;"></div>
  </div>

  <!-- About Section -->
  <section style="margin-bottom: 4rem;">
    <h2 class="font-serif text-2xl font-semibold mb-4">About This Location</h2>
    <div id="description">
      <div class="skeleton" style="height: 4rem; margin-bottom: 0.5rem; border-radius: 0.25rem;"></div>
    </div>
  </section>

  <!-- Amenities -->
  <section style="margin-bottom: 4rem;">
    <h2 class="font-serif text-2xl font-semibold mb-6">What's Included</h2>
    <div id="amenities-grid" class="grid sm\\:grid-cols-2 gap-3">
      <div class="skeleton" style="height: 3rem; border-radius: 0.5rem;"></div>
      <div class="skeleton" style="height: 3rem; border-radius: 0.5rem;"></div>
    </div>
  </section>

  <!-- Saunas -->
  <section style="margin-bottom: 4rem;">
    <h2 class="font-serif text-2xl font-semibold mb-6">Available Sauna Sessions</h2>
    <div id="saunas-grid" class="grid sm\\:grid-cols-2 lg\\:grid-cols-3 gap-4">
      <div class="skeleton" style="height: 18rem; border-radius: 0.5rem;"></div>
      <div class="skeleton" style="height: 18rem; border-radius: 0.5rem;"></div>
    </div>
  </section>

  <!-- Final CTA -->
  <section id="final-cta" style="text-align: center; padding: 3rem 1.5rem; background: linear-gradient(to bottom right, hsla(var(--primary), 0.1), hsla(var(--accent), 0.1)); border-radius: 1rem;">
    <i data-lucide="flame" style="width: 3rem; height: 3rem; color: hsl(var(--accent)); margin: 0 auto 1rem;"></i>
    <h2 class="font-serif text-2xl font-semibold mb-3">Ready for Your Wild Sauna Experience?</h2>
    <p class="text-muted-foreground mb-6" style="max-width: 32rem; margin-left: auto; margin-right: auto;">
      Book your session today and discover the restorative power of Ireland's most beautiful sauna locations.
    </p>
    <div id="cta-button">
      <div class="skeleton" style="height: 3rem; width: 16rem; margin: 0 auto; border-radius: 0.375rem;"></div>
    </div>
  </section>
</main>

<footer style="border-top: 1px solid hsl(var(--border)); padding: 2rem 0; margin-top: 3rem;">
  <div class="max-w-6xl mx-auto px-4" style="text-align: center; color: hsl(var(--muted-foreground));">
    <p>Wild Saunas Ireland - Experience nature's warmth</p>
  </div>
</footer>

<script src="https://unpkg.com/lucide@latest/dist/umd/lucide.min.js"></script>
<script>
const API = '/api/artists/chris';
const LOCATION_ID = 'loc-2';

if (typeof lucide !== 'undefined') {
  lucide.createIcons();
}

async function loadLocation() {
  try {
    const res = await fetch(`${API}/locations/${LOCATION_ID}`);
    const location = await res.json();
    
    // Update hero
    const heroSection = document.getElementById('hero-section');
    const heroImg = location.hero_image_url || location.image_url || '../assets/images/sauna-lakeside.png';
    heroSection.innerHTML = `
      <div style="position: absolute; inset: 0; background-image: url('${heroImg}'); background-size: cover; background-position: center;"></div>
      <div style="position: absolute; inset: 0; background: linear-gradient(to top, rgba(0,0,0,0.8), rgba(0,0,0,0.4), rgba(0,0,0,0.2));"></div>
      <div style="position: absolute; inset: 0; display: flex; flex-direction: column; justify-content: flex-end; padding: 1.5rem 3rem; max-width: 72rem; margin: 0 auto;">
        <a href="../locations/" class="btn btn-outline btn-sm" style="margin-bottom: 1rem; width: fit-content; background: rgba(255,255,255,0.1); border-color: rgba(255,255,255,0.2); color: white;">
          <i data-lucide="arrow-left" style="width: 1rem; height: 1rem; margin-right: 0.5rem;"></i>
          All Locations
        </a>
        <h1 class="font-serif text-3xl font-bold mb-3" style="color: white;">${location.name}</h1>
        <p style="color: rgba(255,255,255,0.9); display: flex; align-items: center; gap: 0.5rem; font-size: 1.125rem;">
          <i data-lucide="map-pin" style="width: 1.25rem; height: 1.25rem;"></i>
          ${location.address}
        </p>
      </div>
    `;
    
    // Update book button
    document.getElementById('book-button').innerHTML = `
      <a href="../book-session/?location=${location.id}" class="btn btn-primary" style="padding: 0.75rem 1.5rem; font-size: 1rem;">
        <i data-lucide="calendar" style="width: 1.25rem; height: 1.25rem; margin-right: 0.5rem;"></i>
        Book Your Session Now
      </a>
    `;
    
    // Update description
    const desc = location.long_description || location.description || 
      `Experience the magic of ${location.name}, where traditional sauna culture meets Ireland's wild beauty.`;
    document.getElementById('description').innerHTML = `
      <p class="text-lg text-muted-foreground" style="line-height: 1.7;">${desc}</p>
    `;
    
    // Update amenities
    const amenities = location.amenities?.length ? location.amenities : [
      "Traditional wood-fired sauna",
      "Cold plunge pool or lake access",
      "Relaxation area with views",
      "Towels and robes provided",
      "Herbal infusions and aromatherapy",
      "Private changing facilities",
      "Refreshments included"
    ];
    document.getElementById('amenities-grid').innerHTML = amenities.map(amenity => `
      <div style="display: flex; align-items: flex-start; gap: 0.75rem; padding: 0.75rem; border-radius: 0.5rem; background: hsla(var(--muted), 0.5);">
        <div style="width: 1.5rem; height: 1.5rem; border-radius: 9999px; background: hsla(var(--primary), 0.1); display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 0.125rem;">
          <i data-lucide="check" style="width: 1rem; height: 1rem; color: hsl(var(--primary));"></i>
        </div>
        <span>${amenity}</span>
      </div>
    `).join('');
    
    // Load saunas
    const saunasRes = await fetch(`${API}/saunas?location=${LOCATION_ID}`);
    const allSaunas = await saunasRes.json();
    const saunas = allSaunas.filter(s => s.location_id === LOCATION_ID);
    
    if (saunas.length > 0) {
      document.getElementById('saunas-grid').innerHTML = saunas.map(sauna => `
        <div class="card" style="overflow: hidden;">
          <div style="height: 10rem; background: hsl(var(--muted)); overflow: hidden;">
            ${sauna.imageUrl ? `
              <img src="${sauna.imageUrl}" alt="${sauna.name}" style="width: 100%; height: 100%; object-fit: cover;">
            ` : `
              <div style="width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; background: linear-gradient(to bottom right, hsla(var(--primary), 0.2), hsla(var(--accent), 0.2));">
                <i data-lucide="flame" style="width: 2.5rem; height: 2.5rem; color: hsla(var(--muted-foreground), 0.3);"></i>
              </div>
            `}
          </div>
          <div class="card-content" style="padding: 1rem;">
            <h3 class="font-semibold text-lg mb-2">${sauna.name}</h3>
            ${sauna.description ? `
              <p class="text-sm text-muted-foreground mb-3" style="display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">${sauna.description}</p>
            ` : ''}
            <div style="display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; margin-bottom: 1rem;">
              <span class="text-sm text-muted-foreground" style="display: flex; align-items: center; gap: 0.25rem;">
                <i data-lucide="users" style="width: 1rem; height: 1rem;"></i>
                Up to ${sauna.capacity} guests
              </span>
              <span class="font-semibold text-primary">€${sauna.price_per_seat}/seat</span>
            </div>
            <a href="../book-session/?sauna=${sauna.id}" class="btn btn-primary" style="width: 100%;">
              <i data-lucide="clock" style="width: 1rem; height: 1rem; margin-right: 0.5rem;"></i>
              View Available Times
            </a>
          </div>
        </div>
      `).join('');
    } else {
      document.getElementById('saunas-grid').innerHTML = `
        <div class="card" style="padding: 2rem; text-align: center; grid-column: 1/-1;">
          <i data-lucide="flame" style="width: 2.5rem; height: 2.5rem; color: hsla(var(--muted-foreground), 0.5); margin: 0 auto 0.75rem;"></i>
          <p class="text-muted-foreground">No saunas currently available at this location.</p>
        </div>
      `;
    }
    
    // Update CTA
    document.getElementById('cta-button').innerHTML = `
      <a href="../book-session/?location=${location.id}" class="btn btn-primary" style="padding: 0.75rem 1.5rem; font-size: 1rem;">
        Book Now at ${location.name}
      </a>
    `;
    
    lucide.createIcons();
  } catch (err) {
    console.error('Failed to load location:', err);
  }
}

loadLocation();
</script>
</html>
