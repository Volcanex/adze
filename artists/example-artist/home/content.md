<style>
body {
    margin: 0;
    padding: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #f5f5f5;
}

.hero {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 100px 20px;
    text-align: center;
}

.hero h1 {
    font-size: 48px;
    margin: 0 0 20px 0;
}

.hero p {
    font-size: 20px;
    opacity: 0.9;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 60px 20px;
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

.content {
    background: white;
    padding: 40px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.admin-link {
    text-align: center;
    margin-top: 40px;
}

.admin-link a {
    background: #667eea;
    color: white;
    padding: 12px 24px;
    border-radius: 6px;
    text-decoration: none;
    display: inline-block;
}

.admin-link a:hover {
    background: #5568d3;
}
</style>

<html>
<div class="nav">
    <a href="/">Home</a>
    <a href="/gallery">Gallery</a>
</div>

<div class="hero">
    <h1>Example Artist</h1>
    <p>Welcome to my portfolio</p>
</div>

<div class="container">
    <div class="content">
        <h2>About Me</h2>
        <p>This is an example artist site built with the blog-new artist system.</p>
        <p>You can customize this page by editing the content in the admin dashboard.</p>

        <h2>Features</h2>
        <ul>
            <li>Custom domain support</li>
            <li>Admin dashboard for easy editing</li>
            <li>Multiple pages (home, gallery, etc.)</li>
            <li>File uploads for images and assets</li>
            <li>Simple token-based authentication</li>
        </ul>
    </div>

    <div class="admin-link">
        <a href="/api/sandbox/dashboard">Admin Dashboard</a>
    </div>
</div>
</html>
