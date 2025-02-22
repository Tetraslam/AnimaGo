# AnimaGo Developer Documentation

## Project Architecture

### Overview
AnimaGo uses a client-server architecture where:
- **Mobile Client**: Flet-based UI running on the user's device
- **Backend Server**: FastAPI server handling heavy processing
- **Storage**: Firebase for data persistence

### Directory Structure
```
src/
├── main.py              # Main Flet UI application
├── server/
│   └── app.py          # FastAPI backend server
├── vision/
│   └── __init__.py     # Computer vision system (Moondream, YOLO, SAM)
├── geo/
│   └── __init__.py     # Geospatial services
├── core/
│   └── __init__.py     # Core data models and business logic
├── config/
│   └── __init__.py     # Configuration and environment settings
├── services/
│   └── api.py          # API client for backend communication
└── ui/                 # (Future) Reusable UI components
```

## Framework-Specific Notes

### Flet (0.27.0)
- **Mobile Development**:
  - Use `flet run --android` or `flet run --ios` for testing
  - Camera access requires file picker simulation in development
  - Add top padding (50px) for camera safety area
  - Use `Colors` and `Icons` (uppercase) instead of deprecated `colors`/`icons`

- **Navigation**:
  - Tabs component works best for mobile bottom navigation
  - Each tab's content should be pre-loaded for smooth transitions
  - Use `animation_duration` for smoother tab switches

- **State Management**:
  - Always call `page.update()` after modifying UI
  - Use `page.overlay` for dialogs and pickers
  - State persists only within the same session

### Moondream
- **API Usage**:
  ```python
  import moondream as md
  model = md.vl(api_key="your-api-key")
  encoded_image = model.encode_image(image)
  result = model.query(encoded_image, "What animals do you see?")
  ```
- Requires API key from moondream.ai
- Best for detailed image analysis and species identification
- Can process both full images and cropped regions

### YOLOv8
- Used for real-time object detection
- Provides bounding boxes and confidence scores
- Can be combined with Moondream for detailed analysis
- Models will be loaded on-demand to save resources

### SAM (Segment Anything Model)
- Used for precise animal segmentation
- Helps with image quality assessment
- Can isolate animals from background
- Resource-intensive, use strategically

### FastAPI Backend
- Handles compute-intensive tasks
- Endpoints:
  - `/vision/process`: Image analysis
  - `/geo/nearby`: Location-based queries
  - `/users/sync`: User data synchronization
- Uses async/await for better performance
- Includes CORS middleware for mobile access

## Development Workflow

### Setting Up
1. Create virtual environment:
   ```bash
   python -m pip install uv
   uv venv
   .venv\Scripts\activate  # Windows
   ```

2. Install dependencies:
   ```bash
   uv pip sync requirements.lock
   ```

3. Configure environment:
   - Copy `.env.example` to `.env`
   - Add required API keys

### Running the App
1. Start the backend:
   ```bash
   uvicorn src.server.app:app --reload --reload-dir src
   ```

2. Start the Flet app:
   ```bash
   flet run --android  # or --ios
   ```

## Key Features & Implementation Notes

### Camera/Image Capture
- Currently uses file picker for testing
- Will need native camera integration
- Process images in backend to avoid mobile resource constraints

### Map Integration
- Planned: Leaflet integration via WebView
- Need to handle location permissions
- Consider offline map caching

### Biodex System
- Firebase sync for cloud backup
- Consider caching common species data

### User System
- Firebase Authentication
- Progress syncing between devices

## Common Gotchas & Solutions

1. **Mobile Performance**
   - Pre-load and cache images
   - Lazy load tab contents
   - Use backend for heavy processing

2. **State Management**
   - Keep state in dedicated classes
   - Use proper update patterns
   - Consider implementing proper state management

3. **Network Handling**
   - Implement retry logic
   - Show loading states
   - Handle offline mode gracefully

4. **Image Processing**
   - Process on backend when possible
   - Implement proper error handling
   - Consider image compression

## Future Considerations

1. **Scaling**
   - Implement proper caching
   - Consider CDN for assets
   - Optimize database queries

2. **Features to Add**
   - Push notifications
   - Social features
   - Achievement system

3. **Performance Optimization**
   - Image optimization
   - Lazy loading
   - Background processing

## Contributing
1. Follow the existing architecture
2. Document new features
3. Update CHANGELOG.md
4. Test on both Android and iOS
5. Consider offline capabilities 