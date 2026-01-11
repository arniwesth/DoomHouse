# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Added `CHANGELOG.md` to track project history.
- Comprehensive "Architecture and Rendering Optimizations" section to `README.md`.
- Interactive theme switching (Classic/Dungeon) and high-res texture support (512x512).
- SWAR-based post-processing pipeline for smoothing/blurring.
- `requirements.txt` for Python dependencies.

### Changed
- Migrated rendering logic to ClickHouse Materialized Views for better performance.
- Refactored GUI from OpenCV to Tkinter for improved keyboard input handling.
- Replaced PPM string output with `Array(UInt32)` packed binary framebuffer for faster data transfer.
- Moved map and textures to ClickHouse Dictionaries with split R/G/B channels for O(1) lookup.
- Improved collision detection with "slide-and-collide" logic in SQL.
- Updated texture paths to be relative to the project root.

### Fixed
- Visual alignment issues with texture mirroring.
- Collision sticking by adding a 0.2 unit buffer.

## [0.2.0] - 2026-01-11
### Added
- Materialized View rendering pipeline.
- SWAR post-processing.
- Tkinter-based client.

## [0.1.0] - 2025-12-20
### Added
- Basic raycasting in SQL.
- Project initialization and planning.
- Prototype implementations.
