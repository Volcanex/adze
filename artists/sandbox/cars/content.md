<style>
body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
    color: #fff;
    margin: 0;
    padding: 40px 20px;
}
.container {
    max-width: 1200px;
    margin: 0 auto;
}
h1 {
    font-size: 64px;
    font-weight: 700;
    margin-bottom: 16px;
    text-align: center;
    background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.tagline {
    text-align: center;
    font-size: 20px;
    color: #aaa;
    margin-bottom: 60px;
    font-style: italic;
}
.cars-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 30px;
    margin-top: 40px;
}
.car-card {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 30px;
    transition: all 0.3s ease;
    backdrop-filter: blur(10px);
}
.car-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
    border-color: rgba(78, 205, 196, 0.5);
}
.car-emoji {
    font-size: 80px;
    text-align: center;
    margin-bottom: 20px;
}
.car-name {
    font-size: 28px;
    font-weight: 600;
    margin-bottom: 12px;
    text-align: center;
}
.car-specs {
    color: #4ecdc4;
    font-size: 14px;
    text-align: center;
    margin-bottom: 16px;
    font-weight: 500;
}
.car-description {
    color: #ccc;
    font-size: 15px;
    line-height: 1.6;
    text-align: center;
}
.fun-fact {
    background: rgba(78, 205, 196, 0.1);
    border-left: 3px solid #4ecdc4;
    padding: 16px;
    margin-top: 20px;
    border-radius: 4px;
    font-size: 13px;
    color: #fff;
}
</style>

<html>
<div class="container">
    <h1>🏎️ Cars 🏎️</h1>
    <p class="tagline">"Life is too short to drive boring cars"</p>

    <div class="cars-grid">
        <div class="car-card">
            <div class="car-emoji">🚗</div>
            <div class="car-name">The Classic</div>
            <div class="car-specs">0-60 in "eventually" | Top Speed: Who cares?</div>
            <div class="car-description">
                A timeless beauty that runs on nostalgia and regular unleaded. Features include: working radio (sometimes),
                AC (when it's not too hot), and that distinctive smell of vintage leather mixed with mystery.
            </div>
            <div class="fun-fact">
                <strong>Fun Fact:</strong> This car has been in 3 accidents, none of which were its fault.
            </div>
        </div>

        <div class="car-card">
            <div class="car-emoji">🏎️</div>
            <div class="car-name">Speed Demon</div>
            <div class="car-specs">0-60 in 2.8s | Top Speed: Too Fast for Mortals</div>
            <div class="car-description">
                Goes from 0 to "Why are there blue lights behind me?" faster than you can say "speeding ticket."
                Comes with free adrenaline rush and a complimentary nervous passenger experience.
            </div>
            <div class="fun-fact">
                <strong>Fun Fact:</strong> Insurance companies weep when they see this car's VIN number.
            </div>
        </div>

        <div class="car-card">
            <div class="car-emoji">🚙</div>
            <div class="car-name">The Family Hauler</div>
            <div class="car-specs">0-60 in "who's timing?" | Seats: Yes</div>
            <div class="car-description">
                A minivan in denial. Features 47 cup holders, permanent Cheerio dust in every crevice,
                and mysterious stains that defy the laws of chemistry. The automatic doors haven't worked since 2019.
            </div>
            <div class="fun-fact">
                <strong>Fun Fact:</strong> Scientists believe this car contains its own ecosystem.
            </div>
        </div>

        <div class="car-card">
            <div class="car-emoji">🚕</div>
            <div class="car-name">Urban Legend</div>
            <div class="car-specs">MPG: Optimistic | Parking: Impossible</div>
            <div class="car-description">
                A car that's seen things. Mostly traffic. Has parallel parked in spots that shouldn't exist and
                knows every pothole in a 50-mile radius by name. The horn hasn't stopped working; it's just tired.
            </div>
            <div class="fun-fact">
                <strong>Fun Fact:</strong> This car has been stuck in traffic longer than some civilizations have existed.
            </div>
        </div>

        <div class="car-card">
            <div class="car-emoji">🚐</div>
            <div class="car-name">The Adventuremobile</div>
            <div class="car-specs">MPG: What's fuel efficiency? | Capacity: Unlimited Dreams</div>
            <div class="car-description">
                Part van, part lifestyle choice, part hippie commune on wheels. Features a bed that's "totally comfortable,"
                a kitchen that works "if you're patient," and a bathroom that's definitely "somewhere nearby."
            </div>
            <div class="fun-fact">
                <strong>Fun Fact:</strong> This van has been to more music festivals than most people.
            </div>
        </div>

        <div class="car-card">
            <div class="car-emoji">🚜</div>
            <div class="car-name">Country Cruiser</div>
            <div class="car-specs">0-60 in "hold my beer" | Off-road: That's the only road</div>
            <div class="car-description">
                Lifted higher than your standards and louder than your opinions. Has mud in places mud shouldn't be able to reach.
                The check engine light is just a decoration at this point.
            </div>
            <div class="fun-fact">
                <strong>Fun Fact:</strong> This truck runs on diesel, determination, and country music.
            </div>
        </div>

        <div class="car-card">
            <div class="car-emoji">🏁</div>
            <div class="car-name">Track Day Special</div>
            <div class="car-specs">Horsepower: All of them | Comfort: None</div>
            <div class="car-description">
                A street-legal race car (barely). No radio, no AC, no comfort, no mercy. The suspension is "race-tuned"
                which means you'll feel every atom of the road. Your chiropractor's retirement plan.
            </div>
            <div class="fun-fact">
                <strong>Fun Fact:</strong> This car's natural habitat is the mechanic's garage.
            </div>
        </div>

        <div class="car-card">
            <div class="car-emoji">🚘</div>
            <div class="car-name">Eco Warrior</div>
            <div class="car-specs">0-60 in "saving the planet" | MPGe: Infinite Smugness</div>
            <div class="car-description">
                Runs on electricity and superiority. Silently judges gas stations as it glides by. Comes with a complimentary
                sense of environmental righteousness and anxiety about finding charging stations in rural areas.
            </div>
            <div class="fun-fact">
                <strong>Fun Fact:</strong> This car has caused more parking lot arguments about charging etiquette than actual miles driven.
            </div>
        </div>

        <div class="car-card">
            <div class="car-emoji">🎪</div>
            <div class="car-name">The Project Car</div>
            <div class="car-specs">Status: "Almost Done" (Since 2018) | Budget: ∞</div>
            <div class="car-description">
                A car in theory. Currently 73% complete and 127% over budget. Lives in the garage where it's been
                "just about ready" for the past 5 years. Every weekend is "the weekend it all comes together."
            </div>
            <div class="fun-fact">
                <strong>Fun Fact:</strong> This car's most frequent destination is the parts store.
            </div>
        </div>
    </div>
</div>
</html>
