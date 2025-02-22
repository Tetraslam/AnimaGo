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
- Segment Anything Model  

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
- [ ] Global heatmap of sightings
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

4. Install dependencies with uv:
```bash
# Install project dependencies using the lockfile
uv pip sync uv.lock

# Install flet with all extras
uv pip install "flet[all]>=0.27.0"
```

### Running the Application

1. Start the application:
```bash
# For desktop development
python src/main.py

# For web deployment
flet run src/main.py --web

# For mobile deployment
flet run src/main.py --android  # For Android
flet run src/main.py --ios      # For iOS
```

### Development Setup

For development work:
```bash
# Install all dependencies including development ones
uv pip sync uv.lock pyproject.toml
```

### Troubleshooting

- If you get any Python version errors, verify your Python version:
  ```bash
  python --version  # Should be 3.11 or higher
  ```
- For GPU support with computer vision features, ensure you have the appropriate CUDA toolkit installed for your system.
- If you encounter dependency issues:
  ```bash
  # Clean the environment and reinstall
  uv pip uninstall --all
  uv pip sync uv.lock
  uv pip install "flet[all]>=0.27.0"
  ```
- On Linux systems, you may need additional dependencies. Check the [Flet Linux prerequisites](https://flet.dev/docs/getting-started#linux).

### Environment Variables

Create a `.env` file in the project root with the following variables:
```env
# Firebase Configuration (required for authentication and database)
FIREBASE_API_KEY=your_api_key
FIREBASE_AUTH_DOMAIN=your_auth_domain
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_STORAGE_BUCKET=your_storage_bucket
FIREBASE_MESSAGING_SENDER_ID=your_sender_id
FIREBASE_APP_ID=your_app_id

# Flet Configuration (optional)
FLET_SESSION_TIMEOUT=3600  # Session timeout in seconds
FLET_FORCE_WEB_VIEW=true  # Force web view for desktop apps
```
