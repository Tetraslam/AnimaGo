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
git clone https://github.com/yourusername/AnimaGo.git
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
# Install flet globally first
uv pip install "flet[all]>=0.27.0"

# Install project dependencies
uv pip sync
```

### Running the Application

1. Start the application:
```bash
# For development
flet run src/main.py

# For specific platforms
flet run src/main.py -d android
flet run src/main.py -d ios
flet run src/main.py -d web
```

### Development Setup

For development work:
```bash
# Install dev dependencies
uv pip sync --dev
```

### Troubleshooting

- If you get any Python version errors, verify your Python version:
  ```bash
  python --version  # Should be 3.11 or higher
  ```
- For GPU support with computer vision features, ensure you have the appropriate CUDA toolkit installed for your system.
- If you encounter any issues with Flet, try reinstalling it globally:
  ```bash
  uv pip install --upgrade "flet[all]>=0.27.0"
  ```

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
```
