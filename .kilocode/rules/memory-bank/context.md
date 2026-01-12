# DOOMHouse Current Context

## Current State
**Status**: Working Prototype  
**Last Updated**: 2026-01-12

The DOOMHouse project is functional with a complete raycasting engine implemented in ClickHouse SQL. The Python client successfully renders frames and handles user input.

## Recent Changes
- **Blog Post Documentation**: Added technical SQL snippets to `docs/blogpost_v1.md` covering collision detection, vectorized raycasting, texture mapping, shading, lighting, and post-processing.

Based on Notes.md, the project evolved through several iterations:
1. **Plans**: Initial planning (Gemini 3.0)
2. **clickhouse v1**: First implementation (Gemini 3.0 Flash)
3. **clickhouse v2**: Refinement (Opus 4.5)
4. **clickhouse v3**: Current version (Gemini 3.0 Pro)
5. **Materialized View Migration**: Moved rendering logic to a ClickHouse Materialized View for better performance and cleaner client code.
6. **Tkinter Migration**: Refactored the GUI from OpenCV to Tkinter to support real-time, non-queued keyboard input with proper key-up/down tracking.
7. **Packed Binary Framebuffer**: Replaced PPM string output with `Array(UInt32)` for faster data transfer.
8. **Post-Processing Pipeline**: Added a second Materialized View for SWAR-based smoothing/blurring.
9. **Dictionary Optimization**: Moved map and textures to ClickHouse Dictionaries with split R/G/B channels.
10. **Theme Support**: Added interactive theme switching (Classic/Dungeon) and high-res texture support (512x512).


Latest implementation includes:
- **Table-based Input/Output**: Client inserts to `player_input` and selects from `rendered_frame_post_processed`.
- **SQL-side Rendering**: All raycasting and pixel generation happens in the `render_materialized` view.
- **SWAR Post-Processing**: SIMD-style blur implemented in SQL.
- **Slide-and-Collide**: Improved collision detection in SQL.
- **Distance Lookups**: Pre-computed floor/ceiling distances for performance.

## Current Work Focus
Maintaining documentation and exploring further SQL-side optimizations.

## Known Issues to Address
1. **Texture Size Limits**: 1024x1024 textures cause memory/dictionary issues.

## Potential Next Steps
- [x] Make texture path relative to project root
- [ ] Add textures to version control or document how to obtain them
- [x] Create requirements.txt for Python dependencies
- [x] Add README.md with setup instructions
- [x] Expand README.md with Architecture and Optimizations details
- [ ] Consider continuous render loop option for smoother movement
- [ ] Explore ClickHouseDB optimizations for better frame rates
- [ ] Add more wall texture types for visual variety

## Environment Notes
- Project developed on macOS
- ClickHouse server expected on localhost:8123
- Python 3 with tkinter required
- Original SQL ported from CedarDB implementation
