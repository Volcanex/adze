<style>
body {
    margin: 0;
    padding: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #f5f5f5;
}

.nav {
    display: flex;
    justify-content: center;
    gap: 30px;
    padding: 20px;
    background: white;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.nav a {
    color: #333;
    text-decoration: none;
    font-weight: 600;
    transition: color 0.2s;
}

.nav a:hover {
    color: #667eea;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 60px 20px;
}

.header {
    text-align: center;
    margin-bottom: 60px;
}

.header h1 {
    font-size: 48px;
    margin: 0 0 10px 0;
}

.header p {
    color: #666;
    font-size: 18px;
}

.gallery-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 30px;
}

.gallery-item {
    background: white;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    transition: transform 0.2s;
}

.gallery-item:hover {
    transform: translateY(-5px);
    box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}

.gallery-item-image {
    width: 100%;
    height: 250px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 24px;
}

.gallery-item-content {
    padding: 20px;
}

.gallery-item-title {
    font-size: 20px;
    font-weight: 600;
    margin: 0 0 10px 0;
}

.gallery-item-description {
    color: #666;
    font-size: 14px;
    line-height: 1.6;
}
</style>

<html>
<div class="nav">
    <a href="/">Home</a>
    <a href="/gallery">Gallery</a>
</div>

<div class="container">
    <div class="header">
        <h1>Gallery</h1>
        <p>My collection of work</p>
    </div>

    <div class="gallery-grid">
        <div class="gallery-item">
            <div class="gallery-item-image">📷</div>
            <div class="gallery-item-content">
                <div class="gallery-item-title">Artwork 1</div>
                <div class="gallery-item-description">Upload your images using the admin dashboard</div>
            </div>
        </div>

        <div class="gallery-item">
            <div class="gallery-item-image">🎨</div>
            <div class="gallery-item-content">
                <div class="gallery-item-title">Artwork 2</div>
                <div class="gallery-item-description">Customize this gallery page to showcase your work</div>
            </div>
        </div>

        <div class="gallery-item">
            <div class="gallery-item-image">🖼️</div>
            <div class="gallery-item-content">
                <div class="gallery-item-title">Artwork 3</div>
                <div class="gallery-item-description">Add as many items as you need</div>
            </div>
        </div>
    </div>
</div>
</html>
