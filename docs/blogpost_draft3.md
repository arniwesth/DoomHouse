# I Built a Doom Engine in SQL... or rather, AI Did.

**Date:** January 13, 2026  
**Topic:** AI-Driven Engineering, SQL, Raycasting  
**Repository:** [DOOMHouse](https://github.com/yourusername/DOOMHouse)

---

If you told a senior engineer in 2023 that you wanted to build a real-time, 3D raycasting engine (like Wolfenstein 3D) entirely inside a ClickHouse database using only SQL, they would probably laugh. If you then told them you weren't going to write a single line of the complex vector math yourself, they'd call you crazy.

Yet, here we are. **DOOMHouse** is a fully functional 3D game engine where the "GPU" is a database, and the "Graphics Driver" is a set of SQL queries. And the most shocking part? The entire codebase was synthesized by frontier AI models, primarily **Gemini 3.0 Pro** and **Flash Preview**.

This isn't a simple "Hello World" script or a boilerplate React app. This is enterprise-grade, constraint-heavy engineering that pushes the boundaries of what SQL is supposed to do.

## The "Impossible" Task

Raycasting is an algorithm that typically relies on imperative programming concepts: `while` loops to march a ray forward until it hits a wall, and mutable state to track distance.

SQL is declarative. It doesn't *do* loops. It doesn't *do* mutable state. It operates on sets of data.

Asking an AI to "write a raycaster in SQL" is a stress test of reasoning capabilities. It requires the model to not just know the syntax, but to fundamentally re-architect an algorithm to fit a hostile environment.

## Evidence of Senior-Level Engineering

The AI didn't just port C++ code to SQL (which wouldn't work). It invented novel solutions to bypass SQL's limitations. Here are three examples of sophisticated logic that demonstrate the model's engineering depth.

### 1. Vectorized Raycasting (The "No-Loop" Loop)

Since SQL lacks `while` loops, the AI implemented a **vectorized approach**. Instead of marching a ray step-by-step, it generates an array of potential steps (`range(1, RAY_STEPS)`) and calculates the trajectory for *all* steps simultaneously using high-order array functions.

**Code Snippet from [`src/SQL/render_view.sql`](src/SQL/render_view.sql:240):**

```sql
-- OPTIMIZATION: Vectorized Raycasting
-- SQL cannot do a "While Loop" efficiently per row.
-- Instead, we generate an array of steps (1..RAY_STEPS) and map over them.
SELECT 
    *,
    -- Calculate distance for every step simultaneously
    arrayMap(i -> (i - valid_x) / r_dir_x, steps) as d_x,
    
    -- Find the first step where a wall exists (Minimum positive distance)
    arrayMin(arrayMap((d, i) -> 
        if(d > 0 AND dictGet('doomhouse.dict_map_data', 'val', ...) > 0, d, 999.0), 
        d_x, steps
    )) as dist_x
```

**Why this is impressive:** The AI understood that `arrayMap` + `arrayMin` is functionally equivalent to a `while` loop finding the first intersection, but fits the set-based paradigm of ClickHouse.

### 2. SWAR Post-Processing (SIMD in SQL)

To add a "blur" effect for smoother visuals, the AI implemented a post-processing pass. A naive approach would unpack the Red, Green, and Blue channels, average them, and repack them. This is slow.

The AI instead implemented **SWAR (SIMD Within A Register)** logic. It performs bitwise math on the packed 32-bit integer to process Red and Blue channels in parallel, masking out the Green channel to prevent overflow.

**Code Snippet from [`src/SQL/post_process_view.sql`](src/SQL/post_process_view.sql:58):**

```sql
-- CHANNEL 1 & 3: RED and BLUE (Calculated in parallel)
-- We mask out Green, perform the math, then mask again to clear overflows
bitAnd(
    bitShiftRight(
        (bitAnd(c, mask_rb) * 4) + 
        bitAnd(l, mask_rb) + bitAnd(r, mask_rb) + 
        bitAnd(u, mask_rb) + bitAnd(d, mask_rb), 
        3 -- Divide by 8
    ), 
    mask_rb
)
```

**Why this is impressive:** This is a low-level optimization technique usually reserved for C/Assembly graphics programming. The AI applied it correctly within a high-level SQL query to optimize performance.

### 3. Dictionary Channel Splitting

In the initial versions, the engine was slow because it had to unpack the 32-bit texture color (UInt32) into R, G, B components for every pixel to apply shading.

The AI suggested a structural change: split the texture data into separate columns (`r`, `g`, `b`) in the ClickHouse Dictionary. This allows the engine to fetch the exact byte needed without bitwise overhead during the shading phase.

**Code Snippet from [`src/SQL/render_view.sql`](src/SQL/render_view.sql:126):**

```sql
-- Instead of unpacking a UInt32 color, we access separate 'r', 'g', 'b' columns
bitOr(
    bitOr(
        bitShiftLeft(toUInt32(dictGet('doomhouse.dict_tex_wall1_data', 'r', w_tex_idx) * base_shade), 0),
        bitShiftLeft(toUInt32(dictGet('doomhouse.dict_tex_wall1_data', 'g', w_tex_idx) * base_shade), 8)
    ),
    bitShiftLeft(toUInt32(dictGet('doomhouse.dict_tex_wall1_data', 'b', w_tex_idx) * base_shade), 16)
)
```

## Methodology: The AI Workflow

This project wasn't generated by a single prompt like "Make me Doom." It was an iterative collaboration:

1.  **Architectural Planning (Gemini 3.0 Pro):** We started by defining the constraints. "We need to render a frame in SQL. How?" The model proposed the Materialized View pipeline.
2.  **Core Logic Implementation (Gemini 3.0 Flash):** For the heavy lifting of writing the 300-line SQL query, we used Flash. Its speed allowed for rapid iteration when syntax errors occurred.
3.  **Optimization & Refactoring (Gemini 3.0 Pro):** When performance was low, we asked the Pro model to "optimize for memory." It came up with the SWAR and Dictionary splitting techniques.

## Challenges Overcome

*   **The "Context Window" Trap:** SQL queries for raycasting are long and dense. Keeping the model focused on the correct part of the query without hallucinating non-existent columns was a challenge. We solved this by modularizing the SQL into logical blocks (Geometry, Shading, Post-Processing).
*   **Debugging the Black Box:** You can't `print()` inside a SQL query. When the screen was black, the AI had to reason through the logic purely statically. It correctly identified issues like integer overflow in the texture mapping logic just by reading the code.

## The Future of AI Development

DOOMHouse proves that AI is ready to graduate from "Copilot" to "Engine Architect."

*   **It handles complexity:** It didn't choke on a 300-line SQL query with nested subqueries.
*   **It understands constraints:** It respected the "no loops" rule of SQL.
*   **It optimizes:** It didn't just write working code; it wrote *fast* code using advanced techniques.

We are moving toward a future where we describe the *system* we want, and the AI handles the implementation details—even if that implementation requires turning a database into a video game console.

---

*Check out the code in `src/SQL/render_view.sql` to see the magic for yourself.*
