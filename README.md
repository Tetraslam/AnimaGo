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
- uv package manager (recommended) or pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/AnimaGo.git
cd AnimaGo
```

2. Create and activate a virtual environment:
```bash
# Using venv
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On macOS/Linux
source .venv/bin/activate
```

3. Install dependencies:
```bash
# Using uv (recommended)
uv pip install -r requirements.txt
```

### Running the Application

1. Start the application:
```bash
# From the project root
flet run --YOUR_PLATFORM_HERE(android/ios/web)
```



### Development Setup

For development, install development dependencies:
```bash
# Using uv
uv pip install --dev

# Or using pip
pip install -e ".[dev]"
```

### Troubleshooting

- If you encounter any issues with Flet installation, make sure you have the latest version of pip:
  ```bash
  python -m pip install --upgrade pip
  ```
- For GPU support with computer vision features, ensure you have the appropriate CUDA toolkit installed for your system.
- Make sure your Python version matches the required version (3.11+) by running:
  ```bash
  python --version
  ```

### Environment Variables

Create a `.env` file in the project root with the following variables:
```env
# Add your environment variables here
# Example:
# FIREBASE_API_KEY=your_api_key
```
