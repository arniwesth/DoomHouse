# DOOMHouse: 3D game rendering engine in pure ClickHouse SQL
### How my X-mas vacation got DOOMed trying to push coding agents to the limit.

## TLDR;
First result and final result.


## Motivation
Pushing frontier models to the limit by creating complex, non-trivial code that demonstrates concept
understanding in novel settings. 


## Limimtations
Only implement 3D rendering engine (no monsters this time).


## Initial approach
First prompt.


## Iterative optimization
Show a table with iterative optimizations
(Requires back-tracking changes and making diffs and summaries of diffs)


## Visual debugging
Show example screenshots that were succesfully debugged.


## Concepts

### Collision detection
"Slide-and-Collide" Physics Engine

```sql
-- Independent axis checks allow sliding along walls
if(dictGet('doomhouse.dict_map_data', 'val',
    toUInt64(floor(try_y + if(try_y > old_y, 0.2, -0.2)) * MAP_W + floor(valid_x_inter) + 1)) = 0,
    try_y, old_y) as valid_y
```

### Vectorized Ray-tracing
Using Array Functions like `arrayMap`, `arraySort`, `groupArray`, `arrayMin` to replace imperative loops.

```sql
-- Find the first wall intersection by mapping over a range of steps
arrayMin(arrayMap((d, i) ->
    if(d > 0 AND d < 30 AND dictGet('doomhouse.dict_map_data', 'val',
    toUInt64(floor(valid_y + r_dir_y * d) * MAP_W + floor(valid_x + r_dir_x * d + 0.005) + 1)) > 0,
    d, 999.0), d_x, steps)) as dist_x
```

### Texture mapping
Using ClickHouse Dictionaries for O(1) texture lookups.

```sql
-- Calculate 1D dictionary index from 2D texture coordinates
toUInt64((least(greatest(toInt32(y * rays.tex_step + rays.tex_base), 0), TEX_MAX) * TEX_SIZE) + rays.tx + 1) as w_tex_idx
```

### Shading
RGB channel split to avoid bit-unpacking overhead.

```sql
-- Reassemble channels into a packed UInt32 after applying shade
bitOr(
    bitOr(
        bitShiftLeft(toUInt32(dictGet('doomhouse.dict_tex_wall1_data', 'r', w_tex_idx) * base_shade), 0),
        bitShiftLeft(toUInt32(dictGet('doomhouse.dict_tex_wall1_data', 'g', w_tex_idx) * base_shade), 8)
    ),
    bitShiftLeft(toUInt32(dictGet('doomhouse.dict_tex_wall1_data', 'b', w_tex_idx) * base_shade), 16)
)
```

### Lightning
Distance Fog and North/South light difference.
(Show image without texture that shows the lightning effect.)

```sql
-- Darken N/S walls (side=1) and apply exponential distance fog
(if(side, 0.6, 1.0) * (1.0 - least(least(hit_dist, 20.0) * 0.125, 1.0))) AS base_shade
```

### Post processing
Anti-aliasing using SWAR (SIMD Within A Register) for fast box blur.

```sql
-- Process Red and Blue channels in parallel within a single UInt32
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


## Optimizations

### Array maps

### Lookup tables




