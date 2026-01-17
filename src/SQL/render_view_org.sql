/*
   ========================================================================================
   DOOMHOUSE RENDER ENGINE: 3D Raycasting in Pure SQL
   ========================================================================================

   OVERVIEW:
   This script implements a Wolfenstein 3D-style raycasting engine entirely within a 
   ClickHouse Materialized View. It transforms player coordinates and a 2D map into 
   a rendered 3D frame buffer.

   CORE CONCEPTS:

   1. VECTORIZED RAYCASTING (Replacing Loops with Arrays):
      SQL is declarative and lacks efficient imperative `for` or `while` loops needed 
      to march a ray step-by-step until it hits a wall.
      
      We solve this using High-Order Array Functions:
      - `range(1, RAY_STEPS)`: Generates an array of indices [1, 2, ... 15].
      - `arrayMap(func, array)`: Applies the ray trajectory logic to *every* step 
        simultaneously (vectorization) rather than sequentially.
      - `arrayMin(array)`: Analyzing the results of the map to find the *first* 
        step where a wall intersection occurred (Minimum distance).

   2. DICTIONARY TEXTURE MAPPING (Split Channels):
      Textures and Map data are stored in memory-mapped ClickHouse Dictionaries.
      To optimize memory access and CPU cycles, texture data is split into separate 
      `r`, `g`, and `b` (UInt8) columns. This avoids the overhead of bitwise unpacking 
      a single UInt32 color integer during the shading step.

   3. FISH-EYE CORRECTION:
      Raw Euclidean distance creates a "fish-eye" lens effect. We correct this by 
      projecting the ray distance onto the camera plane vector (Dot Product), 
      ensuring walls appear straight.

   4. LIGHTING & ATMOSPHERE:
      To create 3D depth, the engine applies two shading techniques:
      - Distance Fog: Pixel colors are multiplied by a decay factor based on distance. 
        Everything fades to black at a distance of ~20 units.
      - Fake Contrast: Walls facing North/South are rendered 40% darker than walls 
        facing East/West. This visually separates corners without needing real light sources.

   5. COLLISION DETECTION (Slide-and-Collide):
      Movement logic includes a collision check against the map dictionary. 
      Before updating the player's position, the engine checks the target coordinates 
      (with a +/- 0.2 buffer radius). If a wall is detected, the movement along that 
      specific axis is rejected. This independent axis check allows the player to 
      "slide" along walls rather than getting stuck.

   6. LOOKUP TABLES (Pre-computed Floor Distances):
      Floor and ceiling casting typically requires an expensive division operation 
      for every single pixel (`distance = height / pixel_row`).
      To optimize this, we pre-calculate these values into `doomhouse.dict_floor_dist`.
      The engine performs a fast O(1) dictionary lookup instead of performing floating-point 
      division at runtime.

   7. OPTIMIZED SHADER PIPELINE (Pre-calculation):
      Texture coordinate math (scaling, wrapping, clamping) is expensive.
      - Pre-calculation: We calculate the dictionary lookup index (`w_tex_idx`, `f_tex_idx`) 
        once per pixel in a subquery, rather than repeating the math for every color channel.
      - Assembly: The final pixel color is packed into a UInt32 (0xBBGGRR) using 
        fast bitwise shifts at the very end of the pipeline.

   ========================================================================================
*/

CREATE MATERIALIZED VIEW doomhouse.render_materialized
TO doomhouse.rendered_frame
AS
WITH 
    -- =========================================================
    -- RESOLUTION SETTINGS
    -- =========================================================
    -- Lower resolution = higher FPS. 640x480 is standard VGA.
    640 AS W,
    480 AS H,
    240 AS H_HALF,

    -- =========================================================
    -- MAP SETTINGS
    -- =========================================================
    -- This constant is used to calculate 1D array indices from 2D coordinates.
    15 AS MAP_W,
    
    -- =========================================================
    -- TEXTURE SETTINGS
    -- =========================================================
    512 AS TEX_SIZE,
    CAST(TEX_SIZE - 1, 'Int32') AS TEX_MAX,
    
    -- =========================================================
    -- RAYCASTING SETTINGS
    -- =========================================================
    -- RAY_STEPS limits how far the engine "sees". 
    -- Optimization: Keeping this low prevents processing too much array data per row.
    25 AS RAY_STEPS,
    CAST(1.0 / W, 'Float32') AS W_INV

SELECT
    -- Aggregating the final result into a single buffer for the frontend.
    -- arraySort ensures pixels are ordered correctly (0..W) in the final blob.
    any(valid_x) as pos_x,
    any(valid_y) as pos_y,
    arrayMap(x -> x.2, arraySort(k -> k.1, groupArray((y * W + x, final_color)))) AS image_data

FROM
(
    SELECT
        x, y,
        valid_x, valid_y,
        
        -- =========================================================
        -- SHADING & TEXTURE MAPPING LOGIC (THE "PIXEL SHADER")
        -- =========================================================
        -- This 'multiIf' acts as the pixel shader.
        -- It calculates the final RGB integer based on whether the pixel is Wall, Ceiling, or Floor.
        multiIf(
            -- CASE 1: DRAWING A WALL
            toInt32(y) >= draw_start AND toInt32(y) <= draw_end,
            CAST(
                -- OPTIMIZATION: Channel Split & Pre-calc
                -- 1. Instead of unpacking a UInt32 color (bitShiftRight + bitAnd), we access
                --    separate 'r', 'g', 'b' columns (UInt8) directly from the dictionary.
                -- 2. We use the pre-calculated 'w_tex_idx' calculated in the subquery below.
                --    This prevents calculating the texture coordinate 3 times per pixel.
                -- 3. We use bitOr/bitShiftLeft to pack the result into 0xBBGGRR format.
                bitOr(
                    bitOr(
                        bitShiftLeft(toUInt32(dictGet('doomhouse.dict_tex_wall1_data', 'r', w_tex_idx) * base_shade), 0),
                        bitShiftLeft(toUInt32(dictGet('doomhouse.dict_tex_wall1_data', 'g', w_tex_idx) * base_shade), 8)
                    ),
                    bitShiftLeft(toUInt32(dictGet('doomhouse.dict_tex_wall1_data', 'b', w_tex_idx) * base_shade), 16)
                )
            , 'UInt32'),

            -- CASE 2: DRAWING CEILING
            -- Uses 'floor_shade' (distance based) to darken the ceiling further away.
            toInt32(y) < draw_start,
            CAST(
                bitOr(
                    bitOr(
                        bitShiftLeft(toUInt32(dictGet('doomhouse.dict_tex_ceiling_data', 'r', f_tex_idx) * floor_shade), 0),
                        bitShiftLeft(toUInt32(dictGet('doomhouse.dict_tex_ceiling_data', 'g', f_tex_idx) * floor_shade), 8)
                    ),
                    bitShiftLeft(toUInt32(dictGet('doomhouse.dict_tex_ceiling_data', 'b', f_tex_idx) * floor_shade), 16)
                )
            , 'UInt32'),

            -- CASE 3: DRAWING FLOOR
            CAST(
                bitOr(
                    bitOr(
                        bitShiftLeft(toUInt32(dictGet('doomhouse.dict_tex_floor_data', 'r', f_tex_idx) * floor_shade), 0),
                        bitShiftLeft(toUInt32(dictGet('doomhouse.dict_tex_floor_data', 'g', f_tex_idx) * floor_shade), 8)
                    ),
                    bitShiftLeft(toUInt32(dictGet('doomhouse.dict_tex_floor_data', 'b', f_tex_idx) * floor_shade), 16)
                )
            , 'UInt32')
        ) AS final_color
    FROM 
    (
        SELECT 
            x, y,
            rays.valid_x, rays.valid_y,

            rays.draw_start, rays.draw_end, rays.base_shade, 

            -- LIGHTING EFFECT: Distance Fog (Floor/Ceiling)
            -- As 'floor_dist' increases, the shade value drops from 1.0 towards 0.0.
            (1.0 - least(floor_dist * 0.125, 1.0)) as floor_shade,

            -- =========================================================
            -- OPTIMIZATION: PRE-CALCULATED TEXTURE INDICES
            -- =========================================================
            -- Previously, the texture index math was repeated 3 times (once per color channel) 
            -- inside the shader. Now we calculate the exact dictionary key ONCE per pixel here.
            
            -- Wall Texture Index Calculation:
            toUInt64((least(greatest(toInt32(y * rays.tex_step + rays.tex_base), 0), TEX_MAX) * TEX_SIZE) + rays.tx + 1) as w_tex_idx,

            -- Floor/Ceiling Texture Index Calculation:
            -- We cast a ray from the player's feet to the pixel on screen to map it to a texture coordinate (f_tx, f_ty).
            toUInt64((
                bitAnd(toInt32((rays.valid_y + floor_dist * ((rays.hit_y - rays.valid_y) / (rays.perp_wall_dist + 0.001))) * TEX_SIZE), TEX_MAX) * TEX_SIZE) 
                + bitAnd(toInt32((rays.valid_x + floor_dist * ((rays.hit_x - rays.valid_x) / (rays.perp_wall_dist + 0.001))) * TEX_SIZE), TEX_MAX) 
                + 1
            ) as f_tex_idx

        FROM 
        (
            -- =========================================================
            -- STAGE 1: RAY GEOMETRY & WALL CALCULATION
            -- =========================================================
            SELECT 
                x, valid_x, valid_y,
                -- Determine which vertical pixels contain the wall strip
                toInt32(H_HALF - (H / (perp_wall_dist + 0.0001)) * 0.5) AS draw_start,
                toInt32(H_HALF + (H / (perp_wall_dist + 0.0001)) * 0.5) AS draw_end,
                
                -- Texture scaling factors for the vertical strip
                (1.0 / (H / (perp_wall_dist + 0.0001))) * TEX_SIZE as tex_step,
                -(H_HALF - (H / (perp_wall_dist + 0.0001)) * 0.5) * tex_step as tex_base,
                
                -- LIGHTING EFFECT: Fake Contrast & Fog
                -- 1. `if(side, 0.6, 1.0)` checks if the ray hit a N/S wall or E/W wall. 
                --    We darken one side to 0.6 to create pseudo-3D contrast at corners.
                -- 2. `(1.0 - least(...))` applies distance fog. If hit_dist > 20, it's pitch black.
                (if(side, 0.6, 1.0) * (1.0 - least(least(hit_dist, 20.0) * 0.125, 1.0))) AS base_shade,
                
                least(if(side, hit_x_wall, hit_y_wall), TEX_MAX) AS tx,
                
                -- Pass through raw hit data for floor calculation
                hit_x, hit_y, perp_wall_dist
            FROM 
            (
                SELECT 
                    *,
                    -- =========================================================
                    -- FISH-EYE EFFECT AVOIDANCE
                    -- =========================================================
                    -- Problem: If we use Euclidean distance (sqrt(dx^2 + dy^2)), walls look rounded 
                    -- because rays at the edge of the screen travel further than center rays.
                    -- Solution: Project the distance onto the camera plane direction vector.
                    -- Formula: raw_dist * dot_product(player_dir, ray_dir)
                    raw_hit_dist * (p_dir_x * r_dir_x + p_dir_y * r_dir_y) as perp_wall_dist,
                    
                    (valid_x + r_dir_x * raw_hit_dist) as hit_x,
                    (valid_y + r_dir_y * raw_hit_dist) as hit_y,
                    
                    -- Texture mapping: Calculate where exactly on the wall unit the ray hit (0.0 to 1.0)
                    toInt32((hit_x - floor(hit_x)) * TEX_SIZE) as hit_x_wall_raw,
                    toInt32((hit_y - floor(hit_y)) * TEX_SIZE) as hit_y_wall_raw,
                    
                    -- Texture mirroring (visual fix for alignment)
                    if(bitAnd(intHash32(toInt32(hit_y)), 1) = 0, TEX_MAX - hit_x_wall_raw, hit_x_wall_raw) as hit_x_wall,
                    if(bitAnd(intHash32(toInt32(hit_x)), 1) = 0, TEX_MAX - hit_y_wall_raw, hit_y_wall_raw) as hit_y_wall
                FROM 
                (
                    SELECT *, least(dist_x, dist_y) as raw_hit_dist, least(dist_x, dist_y) as hit_dist, (dist_y < dist_x) as side
                    FROM (
                        -- OPTIMIZATION: Vectorized Raycasting
                        -- SQL cannot do a "While Loop" efficiently per row.
                        -- Instead, we generate an array of steps (1..RAY_STEPS) and map over them.
                        -- We calculate the distance for every step and use arrayMin to find the first wall hit.                        
                        SELECT 
                            *,
                            arrayMap(i -> (i - valid_x) / r_dir_x, steps) as d_x,
                            -- Check X-axis intersections. Uses MAP_W for index calculation.
                            arrayMin(arrayMap((d, i) -> if(d > 0 AND d < 30 AND dictGet('doomhouse.dict_map_data', 'val', toUInt64(floor(valid_y + r_dir_y * d) * MAP_W + floor(valid_x + r_dir_x * d + if(r_dir_x > 0, 0.005, -0.005)) + 1)) > 0, d, 999.0), d_x, steps)) as dist_x,
                            
                            arrayMap(i -> (i - valid_y) / r_dir_y, steps) as d_y,
                            -- Check Y-axis intersections. Uses MAP_W for index calculation.
                            arrayMin(arrayMap((d, i) -> if(d > 0 AND d < 30 AND dictGet('doomhouse.dict_map_data', 'val', toUInt64(floor(valid_y + r_dir_y * d + if(r_dir_y > 0, 0.005, -0.005)) * MAP_W + floor(valid_x + r_dir_x * d) + 1)) > 0, d, 999.0), d_y, steps)) as dist_y
                        FROM 
                        (
                            SELECT 
                                -- SIMPLIFIED: Directly use the column number 0..W
                                screen_col.number AS x,
                                p.valid_x, p.valid_y,
                                p.dir_x as p_dir_x, p.dir_y as p_dir_y,
                                -- Calculate Ray Direction for this specific column (x)
                                (p.dir_x + p.plane_x * (2.0 * screen_col.number * W_INV - 1.0)) as r_dir_x,
                                (p.dir_y + p.plane_y * (2.0 * screen_col.number * W_INV - 1.0)) as r_dir_y,
                                range(1, RAY_STEPS) as steps
                            FROM 
                            (
                                -- =========================================================
                                -- COLLISION DETECTION & PLAYER INPUT
                                -- =========================================================
                                SELECT 
                                    toFloat32(dir_x) as dir_x, toFloat32(dir_y) as dir_y, 
                                    toFloat32(plane_x) as plane_x, toFloat32(plane_y) as plane_y,
                                    
                                    -- Collision Logic Y:
                                    -- Try to move Y. If the new coordinate hits a wall (dictGet > 0), 
                                    -- we revert to 'old_y'. We add +/- 0.2 buffering to prevent sticking.
                                    -- Uses MAP_W for index calculation.
                                    if(dictGet('doomhouse.dict_map_data', 'val', toUInt64(floor(try_y + if(try_y > old_y, 0.2, -0.2)) * MAP_W + floor(valid_x_inter) + 1)) = 0, try_y, old_y) as valid_y,
                                    valid_x_inter as valid_x
                                FROM (
                                    -- Collision Logic X:
                                    -- Try to move X. If dictGet returns wall, keep old_x.
                                    -- Uses MAP_W for index calculation.
                                    SELECT *, if(dictGet('doomhouse.dict_map_data', 'val', toUInt64(floor(old_y) * MAP_W + floor(try_x + if(try_x > old_x, 0.2, -0.2)) + 1)) = 0, try_x, old_x) as valid_x_inter
                                    FROM doomhouse.player_input
                                ) AS pi
                            ) AS p
                            -- =========================================================
                            -- SCREEN GENERATION (Simplified)
                            -- =========================================================
                            -- Instead of complex sharding, we simply join numbers(W) 
                            -- to generate one row for every vertical column on the screen.
                            CROSS JOIN numbers(W) AS screen_col
                        )
                    )
                )
            )
        ) AS rays
        -- =========================================================
        -- OPTIMIZATION: PRE-CALCULATED FLOOR DISTANCES
        -- =========================================================
        -- Instead of calculating floor distances per pixel (expensive division),
        -- we join with a pre-calculated lookup table for vertical screen positions.
        CROSS JOIN (
            SELECT 
                number as y,
                if(number < H_HALF, toInt32(H - 1 - number), toInt32(number)) as dist_lookup_idx,
                dictGet('doomhouse.dict_floor_dist', 'dist', toUInt64(dist_lookup_idx + 1)) as floor_dist
            FROM numbers(H)
        ) AS v_lines
    ) AS sub
)