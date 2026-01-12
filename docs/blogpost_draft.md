# Blog Post Draft: DOOMHouse

## 1. Proposed Outline

1.  **Hook:** The "Can it run Doom?" meme, but with a twist—running it *inside* the database engine itself, not just storing the code.
2.  **The Concept:** "Database as GPU." Explaining the architecture where Python is just a dumb terminal and ClickHouse does the heavy lifting.
3.  **The "How" (Technical Deep Dive):**
    *   **Vectorized Raycasting:** How to do raycasting without `while` loops using `arrayMap` and `arraySort`.
    *   **The Pipeline:** Using Materialized Views to chain the render and post-processing stages.
    *   **Optimization:** Packed binary framebuffers (`Array(UInt32)`) and SWAR (SIMD Within A Register) for blur effects.
4.  **The "Meta" (AI-Assisted Development):**
    *   How LLMs (Gemini, Opus) acted as the "Senior Engineer" to help refactor and optimize.
    *   Moving from a basic script to a sophisticated SQL pipeline.
5.  **Conclusion:** The power of SQL and the future of "weird" computing.

---

## 2. Draft Content

# DOOMHouse: I Turned a ClickHouse Database into a 3D Rendering Engine

"Can it run Doom?"

It’s the ultimate benchmark for any piece of hardware. We’ve seen it on pregnancy tests, tractors, and even gut bacteria. But I wanted to try something different. I didn't want to just *store* the game data in a database.

**I wanted the database to be the GPU.**

Meet **DOOMHouse**: A proof-of-concept engine that renders 3D graphics in real-time using nothing but ClickHouse SQL queries.

## The Architecture of Madness

In a traditional game engine, the CPU handles game logic and the GPU handles rendering. In DOOMHouse, my Python script is effectively lobotomized. It has one job: capture keyboard input and display a raw array of pixels.

The "brain" is ClickHouse.

Here is the actual data flow:
1.  **Input:** Python inserts your position `(x, y, dir)` into a table.
2.  **Trigger:** This insert fires a **Materialized View**.
3.  **Render:** The view executes a massive SQL query that calculates ray intersections, texture mapping, and lighting.
4.  **Post-Process:** A second view applies a blur filter using bitwise operations.
5.  **Display:** Python selects the final `Array(UInt32)` and paints it to the screen.

The database isn't just retrieving data; it is **generating** the visual reality from scratch, 30 times a second.

## Deep Dive: Raycasting Without Loops

The biggest challenge? SQL hates loops.

Traditional raycasting (like in Wolfenstein 3D) uses a `while` loop to step a ray forward until it hits a wall. ClickHouse SQL doesn't have a `while` loop.

**The Solution: Vectorized Arrays.**

Instead of stepping iteratively, we pre-calculate *every possible* grid intersection the ray could hit within a maximum distance.

```sql
-- Generating candidate distances
arraySort(arrayConcat(
    -- X-axis intersections
    arrayMap(i -> (floor(valid_x) + (ray_dir_x > 0 ? i : -i + 1) - valid_x) / ray_dir_x, range(1, 14)),
    -- Y-axis intersections
    arrayMap(i -> (floor(valid_y) + (ray_dir_y > 0 ? i : -i + 1) - valid_y) / ray_dir_y, range(1, 14))
)) AS dists
```

We generate an array of potential distances, sort them, and then use `arrayFirst` to find the first one that actually contains a wall. It’s a brute-force vector approach that trades memory for the ability to run in a set-based language.

## Optimization: The "Slide-and-Collide"

Early versions felt like driving a tank on ice. You’d hit a wall and stop dead.

To fix this, I implemented a "slide-and-collide" system directly in the SQL. The engine checks the X and Y axes independently. If you hit a wall moving North, you can still slide East.

This logic lives inside the `render_view.sql`, ensuring that the physics calculations happen in the same millisecond as the rendering.

## The "Meta" Narrative: Coding with AI

I didn't build this alone. I built it with a team of AI assistants.

This project started as a "what if" conversation with Gemini 3.0. I asked, "Could you theoretically write a raycaster in SQL?"

The initial answer was a hesitant "Maybe."

We iterated through three major versions:
1.  **V1 (The Script):** A massive Python string formatting nightmare. Slow and buggy.
2.  **V2 (The Refactor):** Moving logic into Views.
3.  **V3 (The Pipeline):** The current architecture using Materialized Views and Packed Binary Framebuffers.

The AI was crucial for the **SWAR (SIMD Within A Register)** implementation. I needed to blur the image, but processing R, G, and B channels separately was too slow. The AI suggested packing them into a single `UInt32` and using bitwise magic to smooth all three channels in a single operation.

## Why Do This?

Is this the future of gaming? Absolutely not.
Is it a practical way to use a database? **Yes.**

If ClickHouse can render a 3D world at 30 FPS, imagine how fast it can process your logs, analytics, or financial data. DOOMHouse is a stress test that proves modern analytical databases are incredibly powerful computational engines.

Check out the code on GitHub and try running it yourself. Just don't blame me if your DBA starts asking questions.

---

## 3. AI Integration Analysis

This project is a prime example of **AI-Assisted Engineering**. The blog post highlights this in the "Meta" section, but here is a deeper breakdown of how AI was leveraged:

*   **Algorithm Translation:** The core raycasting algorithm (DDA) is standard in C++ or Python. Translating it to a vectorized SQL format (using `arrayMap` and `arrayFirst` instead of loops) is non-trivial. AI was instrumental in generating these complex SQL patterns.
*   **Optimization Strategies:** The suggestion to use **Materialized Views** to trigger the render pipeline upon data insertion was a key architectural shift suggested by AI to decouple the client from the render logic.
*   **Bitwise Math:** The SWAR (SIMD Within A Register) logic for the post-processing blur is complex bitwise arithmetic. AI generated the exact bit-shifting logic to average pixels without unpacking them, a significant performance win.

## 4. Structural Alternatives

### Alternative A: The "Problem-First" Approach
*   **Title:** Why SQL is Turing Complete (And How to Abuse It)
*   **Focus:** Start with the theoretical limitations of SQL. Discuss how developers usually view databases as passive storage.
*   **Pivot:** Introduce DOOMHouse as the counter-argument.
*   **Tone:** More academic and architectural. Less focus on the "game" aspect, more on the "compute" aspect.

### Alternative B: The "Dev Log" Narrative
*   **Title:** 48 Hours to Doom: My Journey Building a SQL Game Engine
*   **Focus:** A chronological story. "Day 1: It renders a black screen." "Day 2: I have walls, but they look like static."
*   **Highlight:** The struggle and the "Aha!" moments.
*   **Tone:** Personal, vulnerable, and storytelling-driven. Great for a dev.to or Medium audience.
