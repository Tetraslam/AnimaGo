# AnimaGo: Pokemon Go IRL

AnimaGo gamifies wildlife conservation by harnessing the power of videogame addicts to promote wildlife fundraisers, increase outdoor activity, and popularize citizen science.

## Tech Stack  
### Core  
- Python 3.11  
- uv 0.27.0  
- Flet  
- Firebase
- FastAPI  

### Computer Vision & AI  
- Moondream  
- OpenCV  
- PyTorch  
- YOLOv8  
- Segment Anything Model 2

### Geospatial & Mapping  
- GeoPy  
- Leaflet (via WebView)  


## Features

- [ ] Real-time animal recognition
- [ ] AR overlay
- [ ] Pokedex (biodex? idk)
- [ ] Gamified capture system (image clearness, resolution, etc)
- [ ] Live tracking map
- [ ] Daily/weekly animal challenges to encourage tracking of certain species
- [ ] XP/leveling system
- [ ] Leaderboard (animals found, accuracy, streaks)
- [ ] Weather & time integration
- [ ] Global heatmap of sightings + comments on each sighting
- [ ] Guilds (turn-based battler with animals you've found)
- [ ] Animal leveling based on number found
- [ ] Achievements & badges
- [ ] Sound recognition
- [ ] ML-based image enhancement
- [ ] Behavior recognition
- [ ] Auto-generate stickers
- [ ] Wildlife conservation donations + time-limited/sponsored events
- [ ] "Triple Kill" (multiple in one image; maybe call it multi-capture bonus)
- [ ] Thermal camera mode for nocturnal animals
- [ ] Animal migration events (birds, sea turtles, wildebeests)
- [ ] Nature preservation quests (clean up trash, plant trees, report illegal poaching)
- [ ] Biome mastery (80% documentation of a certain biome)
- [ ] PvP mode (biome mastery battles between guilds where you try and fill a biodiversity bar before the other guild; like clan wars)
- [ ] Livestreaming with chats + donations
- [ ] SPECIES DISCOVERY: visually distinct species which haven't been named get bonuses
- [ ] Virtual museum of rare species
- [ ] "Education Edition"
- [ ] Colorblind mode

## Setup Instructions

### Prerequisites
- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

1. Install uv globally:
```bash
python -m pip install uv
```

2. Clone the repository:
```bash
git clone https://github.com/Tetraslam/AnimaGo.git
cd AnimaGo
```

3. Create and activate a virtual environment with uv:
```bash
uv venv
# On Windows
.venv\Scripts\activate
# On macOS/Linux
source .venv/bin/activate
```

4. Install dependencies:
```bash
uv pip compile pyproject.toml -o requirements.lock
uv pip sync requirements.lock
```

### Update Dependencies after a commit
```bash
git pull
uv pip sync requirements.lock
```

### Running the Application

To run the app on your mobile device:
```bash
# For Android
flet run src/main.py --android

# For iOS
flet run src/main.py --ios
```

Scan the QR code that appears with your device's camera app.
