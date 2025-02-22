# Changelog

All notable changes to AnimaGo will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project setup with uv package manager
- Basic Flet application structure
- Project dependencies configuration in pyproject.toml
- Storage directory structure for data and temporary files
- Basic README with feature roadmap
- Assets directory with initial icon
- Real-time camera view implementation using OpenCV
- Custom CameraView control with 30 FPS preview
- Proper camera cleanup on app exit
- Direct frame capture for vision processing

### Changed
- Replaced file picker camera simulation with real camera feed
- Updated dependencies to include OpenCV and Pillow
- Improved capture UI with live preview

### Infrastructure
- Python 3.11+ environment setup
- Firebase integration preparation
- Computer vision dependencies (Moondream, YOLOv8, SAM2)
- Geospatial tools setup (GeoPy)
- Client-server architecture implementation:
  - FastAPI backend for heavy processing
  - Async API client for mobile communication
  - CORS middleware for cross-origin requests
  - File upload handling for image processing

### Development
- Created CHANGELOG.md for tracking project changes
- Implemented modular project structure:
  - `config/`: Environment and settings management
  - `core/`: Base classes and data models
  - `vision/`: Computer vision system with Moondream, YOLO, and SAM integration
  - `geo/`: Geospatial services with GeoPy integration
  - `services/`: API client for mobile-backend communication
  - `server/`: FastAPI backend implementation
  - Additional directories for future modules:
    - `ui/`: Flet UI components
    - `utils/`: Utility functions
    - `models/`: ML model management
    - `tests/`: Test suite 