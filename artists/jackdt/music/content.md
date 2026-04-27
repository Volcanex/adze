<style>
@font-face {
    font-family: 'Barlow';
    font-style: normal;
    font-weight: 200;
    font-display: fallback;
    src: url('../assets/fonts/barlow-200.ttf') format('truetype');
}
@font-face {
    font-family: 'Barlow';
    font-style: normal;
    font-weight: 700;
    font-display: fallback;
    src: url('../assets/fonts/barlow-700.ttf') format('truetype');
}

:root {
    --primary: #000000;
    --accent: #6495ED;
    --accent-hover: #FFB6C1;
    --bg: #ffffff;
    --bg-alt: #f0f0f0;
    --border: #000000;
    --text-muted: #333333;
    --pink: #FFB6C1;
    --blue: #6495ED;
    --text-font: 'Barlow', sans-serif;
    --heading-font: 'Barlow', sans-serif;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: var(--text-font);
    color: var(--primary);
    background: var(--bg);
    line-height: 1.5;
    font-size: 1rem;
    font-weight: 400;
    min-height: 100vh;
    display: flex;
    opacity: 0;
    animation: pageIn 0.3s ease-out forwards;
    position: relative;
}

body::after {
    content: '';
    position: fixed;
    top: 0;
    left: 200px;
    width: 4px;
    height: 100vh;
    background: #000;
    z-index: 100;
}

@keyframes pageIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes glitch {
    0%, 100% { transform: translate(0); }
    20% { transform: translate(-2px, 2px); }
    40% { transform: translate(-2px, -2px); }
    60% { transform: translate(2px, 2px); }
    80% { transform: translate(2px, -2px); }
}

h1, h2, h3, h4, h5, h6 {
    font-family: var(--heading-font);
    color: var(--primary);
    line-height: 1.4;
}

a { color: var(--primary); text-decoration: none; transition: color 0.4s ease; }
a:hover { color: var(--accent); }

/* ── Sidebar ── */
.sidebar {
    width: 200px;
    min-width: 200px;
    min-height: 100vh;
    padding: 40px 30px;
    display: flex;
    flex-direction: column;
    gap: 40px;
    background: #000;
    color: #fff;
    border-right: 4px solid #000;
    position: relative;
    z-index: 10;
}

.site-name {
    font-family: var(--heading-font);
    font-weight: 900;
    font-size: 24px;
    color: #fff;
    text-decoration: none;
    display: block;
    letter-spacing: -1px;
    text-transform: uppercase;
    transition: all 0.1s ease;
    border: 3px solid #fff;
    padding: 10px;
    text-align: center;
}
.site-name:hover {
    background: var(--accent);
    color: #000;
    border-color: var(--accent);
}

/* ── Navigation ── */
.nav-links {
    list-style: none;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 0;
}
.nav-links a {
    font-size: 16px;
    font-weight: 700;
    display: block;
    transition: all 0.1s ease;
    padding: 12px 0;
    color: #fff;
    text-transform: uppercase;
    letter-spacing: -0.5px;
    border-bottom: 2px solid #333;
}
.nav-links a:hover {
    background: var(--accent);
    color: #000;
    padding-left: 10px;
    border-bottom-color: var(--accent);
}

.social-links {
    display: flex;
    flex-direction: column;
    gap: 0;
    margin-top: auto;
}
.social-links a {
    font-size: 14px;
    font-weight: 700;
    color: #fff;
    letter-spacing: -0.5px;
    transition: all 0.1s ease;
    text-transform: uppercase;
    padding: 12px 0;
    border-bottom: 2px solid #333;
}
.social-links a:hover {
    background: var(--pink);
    color: #000;
    padding-left: 10px;
}

/* ── Mobile ── */
.menu-toggle {
    display: none;
    background: none;
    border: none;
    cursor: pointer;
    width: 28px;
    height: 20px;
    position: relative;
    z-index: 1001;
}
.menu-toggle span {
    display: block;
    width: 100%;
    height: 1.5px;
    background: var(--primary);
    position: absolute;
    left: 0;
    transition: transform 0.35s ease, opacity 0.25s ease;
}
.menu-toggle span:nth-child(1) { top: 4px; }
.menu-toggle span:nth-child(2) { bottom: 4px; }
.menu-toggle.active span:nth-child(1) { top: 50%; transform: translateY(-50%) rotate(45deg); }
.menu-toggle.active span:nth-child(2) { bottom: auto; top: 50%; transform: translateY(-50%) rotate(-45deg); }

.mobile-header { display: none; }

@media (max-width: 768px) {
    body { flex-direction: column; font-size: 14px; }
    body::after { display: none; }

    .mobile-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 16px;
        position: sticky;
        top: 0;
        background: #000;
        z-index: 1000;
        border-bottom: 1px solid #000;
    }
    .mobile-header .site-name {
        font-size: 13px;
        line-height: 1;
        animation: none;
        padding: 5px 8px;
        border-width: 2px;
    }
    .menu-toggle { display: block; height: 14px; width: 22px; align-self: center; }
    .menu-toggle span { background: #fff; }
    .menu-toggle span:nth-child(1) { top: 2px; }
    .menu-toggle span:nth-child(2) { bottom: 2px; }

    .sidebar {
        width: 100%; min-width: 100%; min-height: 0;
        padding: 0 20px;
        gap: 0;
        overflow: hidden;
        display: grid;
        grid-template-rows: 0fr;
        transition: grid-template-rows 0.45s ease;
        border: none;
        box-shadow: none;
    }
    .sidebar.open { grid-template-rows: 1fr; }
    .sidebar > .sidebar-inner { overflow: hidden; padding: 10px 0; }
    .sidebar .site-name { display: none; }
    .sidebar .nav-links { flex-direction: column; gap: 0; }
    .sidebar .nav-links a {
        font-size: 13px;
        padding: 8px 0;
        border-bottom-width: 1px;
    }
    .sidebar .social-links { margin-top: 0; padding-bottom: 4px; }
    .sidebar .social-links a {
        font-size: 13px;
        padding: 8px 0;
        border-bottom-width: 1px;
        letter-spacing: -0.5px;
    }
    .sidebar .social-links a:hover {
        background: var(--accent);
        border-bottom-color: var(--accent);
    }
}

/* ── Main Content ── */
.main-content {
    flex: 1;
    padding: 80px 60px;
    max-width: 900px;
    animation: pageIn 1s ease-out 0.3s both;
}
.main-content h1 {
    font-style: normal;
    font-weight: 900;
    font-size: 3rem;
    margin-bottom: 12px;
    letter-spacing: -2px;
    text-transform: uppercase;
}
.main-content p {
    color: var(--text-muted);
    margin-bottom: 24px;
    font-size: 16px;
    line-height: 1.6;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: -0.5px;
}

.music-player {
    margin-top: 32px;
}

.track {
    padding: 24px;
    margin-bottom: 20px;
    background: #fff;
    border: 4px solid #000;
    border-radius: 0;
    transition: all 0.1s ease;
}

.track:hover {
    border-color: var(--accent);
    transform: translateX(2px);
}

.track-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 16px;
}

.track-info h3 {
    font-family: var(--heading-font);
    font-size: 20px;
    font-weight: 900;
    color: var(--primary);
    margin-bottom: 4px;
    letter-spacing: -1px;
    text-transform: uppercase;
}

.track-meta {
    font-size: 14px;
    color: var(--text-muted);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: -0.5px;
}

.track-duration {
    font-size: 14px;
    color: var(--primary);
    font-family: 'Courier New', monospace;
    font-weight: 700;
}

.waveform {
    height: 80px;
    display: flex;
    align-items: flex-end;
    gap: 3px;
    margin-bottom: 16px;
    padding: 12px;
    background: #fff;
    border-radius: 0;
    border: 3px solid #000;
}

.waveform-bar {
    flex: 1;
    background: var(--accent);
    border-radius: 0;
    transition: all 0.1s ease;
    opacity: 1;
}

.track:hover .waveform-bar {
    opacity: 1;
}

.play-button {
    width: 100%;
    padding: 14px;
    background: #fff;
    color: var(--primary);
    border: 3px solid #000;
    border-radius: 0;
    font-family: var(--text-font);
    font-size: 14px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: -0.5px;
    cursor: pointer;
    transition: all 0.1s ease;
    position: relative;
}

.play-button:hover {
    background: var(--accent);
    border-color: var(--accent);
    color: #000;
}

.play-button:active {
    background: var(--accent-hover);
}

.platform-note {
    margin-top: 48px;
    padding: 24px 28px;
    background: #fff;
    border: 4px solid #000;
    border-radius: 0;
    font-size: 14px;
    line-height: 1.7;
    color: var(--text-muted);
}

.platform-note strong {
    color: var(--primary);
    font-weight: 900;
    text-transform: uppercase;
}

.platform-note ul {
    padding-left: 20px;
}

@media (max-width: 768px) {
    .main-content { padding: 32px 20px; }
    .main-content h1 { font-size: 1.8rem; }
    .track { padding: 16px; }
    .waveform { height: 60px; gap: 2px; }
    .track-header { flex-direction: column; gap: 8px; }
}
</style>

<html>
<div class="mobile-header">
    <a href="../home/" class="site-name">KESKESAY</a>
    <button class="menu-toggle" onclick="this.classList.toggle('active'); document.querySelector('.sidebar').classList.toggle('open');" aria-label="Menu">
        <span></span>
        <span></span>
    </button>
</div>

<div class="sidebar">
    <div class="sidebar-inner">
    <a href="../home/" class="site-name">KESKESAY</a>

    <ul class="nav-links">
        <li><a href="../about/">About</a></li>
        <li><a href="../music/">Music</a></li>
        <li><a href="../writing/">Writing</a></li>
    </ul>

    <div class="social-links">
        <a href="#">Instagram</a>
    </div>
    </div>
</div>

<main class="main-content">
    <h1>Music</h1>
    <p>Custom waveform player with interactive playback controls.</p>

    <div class="livestream-section" style="margin-bottom: 40px;">
        <h2 style="font-size: 1.5rem; margin-bottom: 16px; text-transform: uppercase; letter-spacing: -1px; font-weight: 900;">Live Radio</h2>
        <div class="track" id="livestreamPlayer">
            <div class="track-header">
                <div class="track-info">
                    <h3>NTS Radio Live</h3>
                    <div class="track-meta">London • Live Stream</div>
                </div>
                <div class="track-duration" id="streamStatus" style="color: var(--accent);">● LIVE</div>
            </div>
            <div class="waveform" id="liveWaveform">
                <!-- Live waveform bars will be generated here -->
            </div>
            <button class="play-button" id="streamButton">
                <span class="play-icon">▶</span>
                <span class="pause-icon" style="display:none;">⏸</span>
                <span class="button-text">Play Stream</span>
            </button>
        </div>
    </div>

    <div class="music-player" id="musicPlayer">
        <!-- Tracks will be dynamically loaded here -->
    </div>

    <script>
    // Track data - you can replace these URLs with your own audio files
    const tracks = [
        {
            title: "Volume Variation Demo",
            artist: "Keskesay",
            duration: "0:10",
            audioUrl: "../assets/volume-variation.mp3",
            color: "#8eb8e5"
        },
        {
            title: "Frequency Sweep (220→440→880 Hz)",
            artist: "Keskesay",
            duration: "0:10",
            audioUrl: "../assets/frequency-sweep.mp3",
            color: "#7c99b4"
        },
        {
            title: "Constant Tone (440 Hz)",
            artist: "Keskesay",
            duration: "0:10",
            audioUrl: "../assets/test-track-1.mp3",
            color: "#6b7f82"
        }
    ];

    let currentAudio = null;
    let currentTrackIndex = -1;
    let streamAudio = null;
    let streamAnimationInterval = null;
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();

    // Initialize livestream waveform
    function initLivestream() {
        const liveWaveform = document.getElementById('liveWaveform');
        const bars = 60;
        let waveformBars = [];

        // Create initial waveform bars
        for (let i = 0; i < bars; i++) {
            const bar = document.createElement('div');
            bar.className = 'waveform-bar';
            bar.style.height = '20%';
            bar.style.background = 'var(--accent)';
            liveWaveform.appendChild(bar);
            waveformBars.push(bar);
        }

        // Setup stream button
        const streamButton = document.getElementById('streamButton');
        streamButton.addEventListener('click', toggleStream);

        function toggleStream() {
            const playIcon = streamButton.querySelector('.play-icon');
            const pauseIcon = streamButton.querySelector('.pause-icon');
            const buttonText = streamButton.querySelector('.button-text');

            if (streamAudio && !streamAudio.paused) {
                // Pause stream
                streamAudio.pause();
                clearInterval(streamAnimationInterval);
                playIcon.style.display = 'inline';
                pauseIcon.style.display = 'none';
                buttonText.textContent = 'Play Stream';

                // Reset waveform
                waveformBars.forEach(bar => {
                    bar.style.height = '20%';
                    bar.style.background = 'var(--accent)';
                });
            } else {
                // Stop any currently playing track
                if (currentAudio) {
                    currentAudio.pause();
                    const oldButton = document.querySelector(`button[data-track="${currentTrackIndex}"]`);
                    if (oldButton) {
                        oldButton.querySelector('.play-icon').style.display = 'inline';
                        oldButton.querySelector('.pause-icon').style.display = 'none';
                        oldButton.querySelector('.button-text').textContent = 'Play';
                    }
                }

                // Play stream
                if (!streamAudio) {
                    // NTS Radio stream
                    streamAudio = new Audio('https://stream-relay-geo.ntslive.net/stream');
                    streamAudio.crossOrigin = 'anonymous';
                }

                streamAudio.play().then(() => {
                    playIcon.style.display = 'none';
                    pauseIcon.style.display = 'inline';
                    buttonText.textContent = 'Pause Stream';

                    // Animate waveform
                    animateLiveWaveform(waveformBars);
                }).catch(err => {
                    console.error('Stream error:', err);
                    buttonText.textContent = 'Stream Unavailable';
                });
            }
        }

        function animateLiveWaveform(bars) {
            let offset = 0;
            streamAnimationInterval = setInterval(() => {
                bars.forEach((bar, index) => {
                    // Create wave pattern with some randomness
                    const wave1 = Math.sin((index + offset) * 0.3) * 0.3;
                    const wave2 = Math.sin((index + offset) * 0.15) * 0.2;
                    const noise = Math.random() * 0.3;
                    const height = Math.max(0.15, Math.min(0.95, 0.4 + wave1 + wave2 + noise));

                    bar.style.height = (height * 100) + '%';

                    // Color variation
                    if (height > 0.7) {
                        bar.style.background = 'var(--pink)';
                    } else if (height > 0.5) {
                        bar.style.background = 'var(--accent)';
                    } else {
                        bar.style.background = 'var(--accent)';
                        bar.style.opacity = '0.7';
                    }
                });
                offset += 0.5;
            }, 50); // Update every 50ms for smooth animation
        }
    }

    // Analyze audio file and generate real waveform data
    async function analyzeAudioFile(url, bars = 60) {
        try {
            const response = await fetch(url);
            const arrayBuffer = await response.arrayBuffer();
            const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

            // Get audio data from the first channel
            const rawData = audioBuffer.getChannelData(0);
            const samples = bars;
            const blockSize = Math.floor(rawData.length / samples);
            const waveformData = [];

            // Calculate RMS (Root Mean Square) for each block to get amplitude
            for (let i = 0; i < samples; i++) {
                let sum = 0;
                for (let j = 0; j < blockSize; j++) {
                    const value = rawData[(i * blockSize) + j];
                    sum += value * value;
                }
                const rms = Math.sqrt(sum / blockSize);
                waveformData.push(rms);
            }

            // Normalize the data to 0-1 range
            const max = Math.max(...waveformData);
            return waveformData.map(val => (val / max) * 0.9 + 0.1);
        } catch (err) {
            console.error('Error analyzing audio:', err);
            // Fallback to random data if analysis fails
            return Array.from({length: bars}, () => Math.random() * 0.7 + 0.3);
        }
    }

    // Create track element
    async function createTrackElement(track, index) {
        const trackDiv = document.createElement('div');
        trackDiv.className = 'track';
        trackDiv.dataset.index = index;

        trackDiv.innerHTML = `
            <div class="track-header">
                <div class="track-info">
                    <h3>${track.title}</h3>
                    <div class="track-meta">${track.artist}</div>
                </div>
                <div class="track-duration">${track.duration}</div>
            </div>
            <div class="waveform" data-track="${index}">
                <div style="text-align: center; padding: 40px 0; color: var(--text-light);">Analyzing audio...</div>
            </div>
            <button class="play-button" data-track="${index}">
                <span class="play-icon">▶</span>
                <span class="pause-icon" style="display:none;">⏸</span>
                <span class="button-text">Play</span>
            </button>
        `;

        // Analyze audio and update waveform asynchronously
        analyzeAudioFile(track.audioUrl).then(waveformData => {
            const waveform = trackDiv.querySelector('.waveform');
            const waveformBars = waveformData.map(height =>
                `<div class="waveform-bar" style="height: ${height * 100}%"></div>`
            ).join('');
            waveform.innerHTML = waveformBars;
        });

        return trackDiv;
    }

    // Initialize player
    async function initPlayer() {
        console.log('Initializing music player with', tracks.length, 'tracks');
        const playerContainer = document.getElementById('musicPlayer');
        if (!playerContainer) {
            console.error('Player container not found!');
            return;
        }

        for (let index = 0; index < tracks.length; index++) {
            const track = tracks[index];
            console.log('Adding track:', track.title);
            const trackElement = await createTrackElement(track, index);
            playerContainer.appendChild(trackElement);
        }

        // Add event listeners to all play buttons
        document.querySelectorAll('.play-button').forEach(button => {
            button.addEventListener('click', function() {
                const trackIndex = parseInt(this.dataset.track);
                togglePlayPause(trackIndex);
            });
        });

        // Add click to waveform bars
        document.querySelectorAll('.waveform').forEach(waveform => {
            waveform.addEventListener('click', function(e) {
                if (currentAudio && currentTrackIndex === parseInt(this.dataset.track)) {
                    const rect = this.getBoundingClientRect();
                    const clickX = e.clientX - rect.left;
                    const percentage = clickX / rect.width;
                    currentAudio.currentTime = currentAudio.duration * percentage;
                }
            });
        });
    }

    // Toggle play/pause
    function togglePlayPause(trackIndex) {
        const track = tracks[trackIndex];
        const button = document.querySelector(`button[data-track="${trackIndex}"]`);
        const playIcon = button.querySelector('.play-icon');
        const pauseIcon = button.querySelector('.pause-icon');
        const buttonText = button.querySelector('.button-text');

        // If clicking the same track that's playing
        if (currentAudio && currentTrackIndex === trackIndex) {
            if (currentAudio.paused) {
                currentAudio.play();
                playIcon.style.display = 'none';
                pauseIcon.style.display = 'inline';
                buttonText.textContent = 'Pause';
            } else {
                currentAudio.pause();
                playIcon.style.display = 'inline';
                pauseIcon.style.display = 'none';
                buttonText.textContent = 'Play';
            }
        } else {
            // Stop current track if playing
            if (currentAudio) {
                currentAudio.pause();
                const oldButton = document.querySelector(`button[data-track="${currentTrackIndex}"]`);
                if (oldButton) {
                    oldButton.querySelector('.play-icon').style.display = 'inline';
                    oldButton.querySelector('.pause-icon').style.display = 'none';
                    oldButton.querySelector('.button-text').textContent = 'Play';
                }
            }

            // Play new track
            currentAudio = new Audio(track.audioUrl);
            currentTrackIndex = trackIndex;

            // Add error handling
            currentAudio.addEventListener('error', (e) => {
                console.error('Audio error:', e);
                alert('Error loading audio: ' + track.audioUrl);
            });

            currentAudio.play().catch(err => {
                console.error('Play error:', err);
                alert('Error playing audio: ' + err.message);
            });

            playIcon.style.display = 'none';
            pauseIcon.style.display = 'inline';
            buttonText.textContent = 'Pause';

            // Animate waveform during playback
            currentAudio.addEventListener('timeupdate', () => {
                animateWaveform(trackIndex);
            });

            // Reset button when track ends
            currentAudio.addEventListener('ended', () => {
                playIcon.style.display = 'inline';
                pauseIcon.style.display = 'none';
                buttonText.textContent = 'Play';
                resetWaveform(trackIndex);
            });
        }
    }

    // Animate waveform based on playback
    function animateWaveform(trackIndex) {
        if (!currentAudio) return;
        const progress = currentAudio.currentTime / currentAudio.duration;
        const waveform = document.querySelector(`.waveform[data-track="${trackIndex}"]`);
        const bars = waveform.querySelectorAll('.waveform-bar');

        bars.forEach((bar, index) => {
            if (index / bars.length < progress) {
                bar.style.opacity = '1';
                bar.style.background = 'var(--accent-hover)';
            } else {
                bar.style.opacity = '0.6';
                bar.style.background = 'var(--accent)';
            }
        });
    }

    // Reset waveform animation
    function resetWaveform(trackIndex) {
        const waveform = document.querySelector(`.waveform[data-track="${trackIndex}"]`);
        const bars = waveform.querySelectorAll('.waveform-bar');
        bars.forEach(bar => {
            bar.style.opacity = '0.6';
            bar.style.background = 'var(--accent)';
        });
    }

    // Initialize on page load
    initLivestream();
    initPlayer();
    </script>

    <div class="platform-note">
        <strong>This is a custom waveform player with real audio analysis</strong>
        <br><br>
        Features:
        <ul style="margin-top: 12px;">
            <li>Waveforms are generated from real audio data using Web Audio API</li>
            <li>Click play to hear the tracks with animated playback progress</li>
            <li>Click anywhere on the waveform to skip to that position</li>
            <li><strong>First track</strong> shows volume changes: quiet → medium → loud → quiet → loud</li>
            <li><strong>Second track</strong> is a frequency sweep that rises in pitch</li>
            <li><strong>Third track</strong> is a constant tone (flat waveform)</li>
            <li>Waveform heights represent amplitude (volume), not pitch</li>
        </ul>
        <br>
        To use your own tracks, update the audioUrl in the tracks array above and click Save to rebuild.
    </div>
</main>
</html>