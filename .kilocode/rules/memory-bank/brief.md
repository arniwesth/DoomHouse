# DOOMHouse Project Overview

## Objective
DOOMHouse is an experimental "Doom-like" game engine that offloads 3D rendering logic entirely to a ClickHouse database. The primary goal is to demonstrate the computational capabilities of SQL and ClickHouse by implementing a real-time raycasting engine within database queries.

## Key Features
- **SQL-Powered Rendering**: Core graphics logic—including raycasting, texture mapping, and shading—is executed via complex SQL queries.
- **Raycasting Engine**: Implements a Wolfenstein 3D-style rendering technique with wall textures, floor/ceiling casting, and depth shading.
- **Interactive Gameplay**: Supports real-time movement (forward/backward, rotation) and collision detection.
- **Texture Management**: Features "Natural Texture Mapping" with randomized texture flipping to reduce visual repetition.
- **Python Client**: A lightweight frontend using `tkinter` and `PIL` to handle user input and display the rendered frames returned by the database.

## Technologies
- **Core Engine**: ClickHouse (SQL)
- **Client Application**: Python 3
- **Libraries**: `clickhouse_connect`, `tkinter`, `Pillow (PIL)`
- **Concepts**: Raycasting, Vector Math, SQL-based Image Generation (Packed Binary)

## Significance
This project serves as a unique proof-of-concept, showcasing that modern analytical databases like ClickHouse are powerful enough to handle complex, non-traditional computational tasks like real-time 3D graphics generation, effectively turning the database into a GPU.
