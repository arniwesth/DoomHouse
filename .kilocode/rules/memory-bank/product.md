# DOOMHouse Product Overview

## Why This Project Exists
DOOMHouse exists as a proof-of-concept to demonstrate that modern analytical databases like ClickHouse are powerful enough to handle complex, non-traditional computational tasks—specifically real-time 3D graphics generation.

## Problems It Solves
- **Educational**: Demonstrates advanced SQL capabilities and computational power of modern column-oriented databases
- **Technical Curiosity**: Answers the question "Can a database render 3D graphics?" with a resounding "Yes"
- **Benchmarking**: Provides a unique stress test for database query optimization and execution speed
- **Inspiration**: Shows developers the creative possibilities when thinking outside traditional use cases

## How It Works

### Core Rendering Pipeline
1. **Input**: Player position and direction vectors are inserted into `doomhouse.player_input`.
2. **Processing**: A multi-stage SQL pipeline executes:
   - **Stage 1 (Raycasting)**: `render_view` performs raycasting, texture mapping, and lighting.
   - **Stage 2 (Post-Processing)**: `post_process_view` applies a SWAR-based blur/smoothing filter.
3. **Output**: ClickHouse returns an `Array(UInt32)` representing the packed framebuffer.
4. **Display**: Python client converts the array to bytes and displays it via `tkinter` and `PIL`.

### User Experience Goals
- **Real-time Interactivity**: Maintain responsive movement and rotation.
- **Visual Quality**: High-resolution textures (512x512) and post-processed smoothing.
- **Thematic Variety**: Support for multiple texture themes (Classic, Dungeon).
- **Educational Value**: Demonstrate advanced SQL techniques like SWAR and vectorized raycasting.

## User Interaction

### Controls
| Key | Action |
|-----|--------|
| ↑ / W | Move forward |
| ↓ / S | Move backward |
| ← / A | Rotate view left |
| → / D | Rotate view right |
| T | Switch texture theme |
| Escape | Exit game |

### Visual Elements
- **Walls**: Textured surfaces with distance-based fog and side-shading
- **Ceiling**: Textured surfaces with distance-based fog
- **Floor**: Textured surfaces with distance-based fog

## Success Criteria
1. Maintain interactive frame rates (subjectively smooth movement)
2. Correct collision detection (player cannot walk through walls)
3. Proper texture mapping without obvious visual artifacts
4. Natural-looking texture variation using hash-based random flipping
