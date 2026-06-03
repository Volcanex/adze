<style>
body {
    background: #ffffff;
    margin: 0;
    padding: 0;
    min-height: 100vh;
    font-family: var(--text-font);
    color: var(--primary);
}

.header {
    padding: var(--page-padding);
    border-bottom: 1px solid var(--border);
}

.nav {
    font-size: var(--nav-size);
    font-weight: var(--nav-weight);
}

.nav a {
    margin-right: 24px;
    text-decoration: none;
    color: var(--primary);
}

.nav a:hover {
    color: var(--accent);
}

.content {
    padding: var(--page-padding);
    max-width: var(--content-max-width);
    margin: 0 auto;
}

h1 {
    font-family: var(--heading-font);
    font-size: var(--h1-size);
    font-weight: var(--h1-weight);
    line-height: var(--heading-line-height);
    margin: 0 0 var(--section-gap) 0;
}

p {
    font-size: var(--body-size);
    font-weight: var(--body-weight);
    line-height: var(--body-line-height);
    margin: 0 0 var(--section-gap) 0;
}

@media (max-width: 768px) {
    .header, .content {
        padding: 24px;
    }
    
    h1 {
        font-size: 1.8rem;
    }
}
</style>

<html>
<div class="header">
    <div class="nav">
        <a href="../home/">Home</a>
        <a href="../about/">About</a>
        <a href="../singleview/">Single View</a>
    </div>
</div>

<div class="content">
    <h1>Single View</h1>
    <p>Feature a single piece of work, project, or showcase item with dedicated focus.</p>
</div>
</html>
