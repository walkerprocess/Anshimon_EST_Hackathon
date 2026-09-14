# ANSIMON Shelter Routing

Finds a nearby cooling shelter from an older adult's latitude and longitude, then ranks practical pedestrian routes with TMAP.

## How It Works

1. Sort all shelters by straight-line distance to create a small candidate set.
2. Request TMAP pedestrian routes for the five nearest candidates concurrently.
3. Rank successful routes by walking time and then by crossing count.
4. Return the best shelter, route steps, and up to four alternatives.

Straight-line distance is used only for candidate reduction. The final recommendation is based on a pedestrian route because rivers, highways, and inaccessible crossings can make a geographically close shelter impractical. TMAP search option `30` prefers a short route that avoids stairs.

## Install and Run

```bash
pip install aiohttp python-dotenv
cp .env.example .env

python recommend.py --demo
python recommend.py 37.5301 127.1236
python recommend.py 37.5301 127.1236 --file=cooling_shelters.csv
```

Use `--file` for reliable demonstrations when a local CSV or JSON dataset is available. The loader detects common latitude and longitude columns by valid Korean coordinate ranges.

## Output

The JSON result includes `name`, `address`, coordinates, `walk_minutes`, `walk_meters`, `crossings`, `open_status`, `needs_review`, route instructions, and alternatives.

`needs_review` becomes `true` when route calculation fails or walking time exceeds 20 minutes. The component deliberately does not replace a failed TMAP route with a confident straight-line estimate.

The recommended result can be persisted by the Spring shelter domain and passed directly into the voice call plan. Production use should cache route results and use current validated shelter data.

For original project notes, see [README.ko.md](README.ko.md).
