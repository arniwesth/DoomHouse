/*
------------------------------------------------------------------------------------------------
 DOOMHOUSE POST-PROCESSOR: FAST GAUSSIAN BLUR APPROXIMATION
------------------------------------------------------------------------------------------------
 This Materialized View acts as a pixel shader, applying a post-processing smoothing filter
 to the rendered Doom frames. It utilizes high-performance bitwise arithmetic to process
 packed RGB integers without unpacking them.

 CONCEPTS USED:

 1. STENCIL CONVOLUTION (via Array Shifting):
    Instead of complex 2D spatial joins, we generate "neighbor" arrays (Left, Right, Up, Down)
    by shifting the source array using `arraySlice` and `arrayResize`.
    - w = 640 represents the stride (screen width).
    - This aligns the neighbor pixels with the center pixel at the same array index.

 2. WEIGHTED AVERAGE KERNEL:
    The script applies a 5-point smoothing kernel (Low-Pass Filter):
    Formula: Pixel = (4 * Center + Left + Right + Up + Down) / 8
    - Weighting the center by 4 and neighbors by 1 creates a subtle blur.
    - Dividing by 8 (bitShiftRight 3) normalizes the brightness.

 3. SWAR (SIMD Within A Register) / BITWISE PARALLELISM:
    Standard math on packed RGB integers (e.g., 0x00RRGGBB) causes color bleeding 
    (e.g., Green overflows into Red). To avoid expensive unpacking:
    - We use masks (0x00FF00FF and 0x0000FF00) to isolate channels.
    - Red and Blue are processed together in one operation (spaced by 8 bits of zeros).
    - Green is processed separately.
    - bitOr combines them back into the final pixel.
------------------------------------------------------------------------------------------------
*/

CREATE MATERIALIZED VIEW doomhouse.post_process_materialized
TO doomhouse.rendered_frame_post_processed
AS
WITH
    640 AS w,
    image_data AS src,
    length(src) AS len,

    -- 1. GENERATE NEIGHBORS ON PACKED DATA 
    -- (Saves 66% RAM by not unpacking R/G/B yet)
    arraySlice(arrayConcat([0], src), 1, len) AS l,
    arrayResize(arraySlice(src, 2), len, 0) AS r,
    arraySlice(arrayConcat(arrayWithConstant(w, 0), src), 1, len) AS u,
    arrayResize(arraySlice(src, w + 1), len, 0) AS d,

    -- Constants for SWAR masking
    0x00FF00FF AS mask_rb, -- Mask for Red and Blue
    0x0000FF00 AS mask_g   -- Mask for Green

SELECT
    pos_x,
    pos_y,
    arrayMap(
        (c, l, r, u, d) ->
            bitOr(
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
                ),
                
                -- CHANNEL 2: GREEN (Calculated separately)
                -- We mask out R/B, perform math, mask again
                bitAnd(
                    bitShiftRight(
                        (bitAnd(c, mask_g) * 4) + 
                        bitAnd(l, mask_g) + bitAnd(r, mask_g) + 
                        bitAnd(u, mask_g) + bitAnd(d, mask_g), 
                        3 -- Divide by 8
                    ), 
                    mask_g
                )
            ),
        src, l, r, u, d
    ) AS image_data
FROM doomhouse.rendered_frame;