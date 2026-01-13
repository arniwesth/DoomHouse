/*
------------------------------------------------------------------------------------------------
 DOOMHOUSE POST-PROCESSOR: FAST GAUSSIAN BLUR APPROXIMATION (Split Pipeline)
------------------------------------------------------------------------------------------------
*/

-- =========================================================
-- VIEW 1: TOP HALF
-- =========================================================
CREATE MATERIALIZED VIEW doomhouse.post_process_materialized_top
TO doomhouse.rendered_frame_post_processed_top
AS
WITH
    640 AS w,
    image_data AS src,
    length(src) AS len,

    -- 1. GENERATE NEIGHBORS ON PACKED DATA 
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
                bitAnd(
                    bitShiftRight(
                        (bitAnd(c, mask_rb) * 4) + 
                        bitAnd(l, mask_rb) + bitAnd(r, mask_rb) + 
                        bitAnd(u, mask_rb) + bitAnd(d, mask_rb), 
                        3 -- Divide by 8
                    ), 
                    mask_rb
                ),
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
FROM doomhouse.rendered_frame_top;

-- =========================================================
-- VIEW 2: BOTTOM HALF
-- =========================================================
CREATE MATERIALIZED VIEW doomhouse.post_process_materialized_bottom
TO doomhouse.rendered_frame_post_processed_bottom
AS
WITH
    640 AS w,
    image_data AS src,
    length(src) AS len,

    -- 1. GENERATE NEIGHBORS ON PACKED DATA 
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
                bitAnd(
                    bitShiftRight(
                        (bitAnd(c, mask_rb) * 4) + 
                        bitAnd(l, mask_rb) + bitAnd(r, mask_rb) + 
                        bitAnd(u, mask_rb) + bitAnd(d, mask_rb), 
                        3 -- Divide by 8
                    ), 
                    mask_rb
                ),
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
FROM doomhouse.rendered_frame_bottom;
