/* DOOMHouse 8-Way Split Post-Process Views */

-- =========================================================
-- VIEW 1: STRIP 1
-- =========================================================
CREATE MATERIALIZED VIEW doomhouse.post_process_materialized_1
TO doomhouse.rendered_frame_post_processed_1
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
FROM doomhouse.rendered_frame_1;



-- =========================================================
-- VIEW 2: STRIP 2
-- =========================================================
CREATE MATERIALIZED VIEW doomhouse.post_process_materialized_2
TO doomhouse.rendered_frame_post_processed_2
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
FROM doomhouse.rendered_frame_2;



-- =========================================================
-- VIEW 3: STRIP 3
-- =========================================================
CREATE MATERIALIZED VIEW doomhouse.post_process_materialized_3
TO doomhouse.rendered_frame_post_processed_3
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
FROM doomhouse.rendered_frame_3;



-- =========================================================
-- VIEW 4: STRIP 4
-- =========================================================
CREATE MATERIALIZED VIEW doomhouse.post_process_materialized_4
TO doomhouse.rendered_frame_post_processed_4
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
FROM doomhouse.rendered_frame_4;



-- =========================================================
-- VIEW 5: STRIP 5
-- =========================================================
CREATE MATERIALIZED VIEW doomhouse.post_process_materialized_5
TO doomhouse.rendered_frame_post_processed_5
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
FROM doomhouse.rendered_frame_5;



-- =========================================================
-- VIEW 6: STRIP 6
-- =========================================================
CREATE MATERIALIZED VIEW doomhouse.post_process_materialized_6
TO doomhouse.rendered_frame_post_processed_6
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
FROM doomhouse.rendered_frame_6;



-- =========================================================
-- VIEW 7: STRIP 7
-- =========================================================
CREATE MATERIALIZED VIEW doomhouse.post_process_materialized_7
TO doomhouse.rendered_frame_post_processed_7
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
FROM doomhouse.rendered_frame_7;



-- =========================================================
-- VIEW 8: STRIP 8
-- =========================================================
CREATE MATERIALIZED VIEW doomhouse.post_process_materialized_8
TO doomhouse.rendered_frame_post_processed_8
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
FROM doomhouse.rendered_frame_8;


