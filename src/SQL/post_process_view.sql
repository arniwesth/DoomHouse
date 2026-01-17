/*
------------------------------------------------------------------------------------------------
  DOOMHOUSE POST-PROCESSOR: FAST GAUSSIAN BLUR APPROXIMATION (4-Way Split Pipeline)
------------------------------------------------------------------------------------------------
*/

-- =========================================================
-- VIEW 1: QUARTER 1
-- =========================================================
CREATE MATERIALIZED VIEW doomhouse.post_process_materialized_1
TO doomhouse.rendered_frame_post_processed_1
AS
WITH
    640 AS w,
    image_data AS src,
    length(src) AS len,
    arraySlice(arrayConcat([0], src), 1, len) AS l,
    arrayResize(arraySlice(src, 2), len, 0) AS r,
    arraySlice(arrayConcat(arrayWithConstant(w, 0), src), 1, len) AS u,
    arrayResize(arraySlice(src, w + 1), len, 0) AS d,
    0x00FF00FF AS mask_rb,
    0x0000FF00 AS mask_g
SELECT
    pos_x, pos_y,
    arrayMap((c, l, r, u, d) -> bitOr(bitAnd(bitShiftRight((bitAnd(c, mask_rb) * 4) + bitAnd(l, mask_rb) + bitAnd(r, mask_rb) + bitAnd(u, mask_rb) + bitAnd(d, mask_rb), 3), mask_rb), bitAnd(bitShiftRight((bitAnd(c, mask_g) * 4) + bitAnd(l, mask_g) + bitAnd(r, mask_g) + bitAnd(u, mask_g) + bitAnd(d, mask_g), 3), mask_g)), src, l, r, u, d) AS image_data
FROM doomhouse.rendered_frame_1;

-- =========================================================
-- VIEW 2: QUARTER 2
-- =========================================================
CREATE MATERIALIZED VIEW doomhouse.post_process_materialized_2
TO doomhouse.rendered_frame_post_processed_2
AS
WITH
    640 AS w,
    image_data AS src,
    length(src) AS len,
    arraySlice(arrayConcat([0], src), 1, len) AS l,
    arrayResize(arraySlice(src, 2), len, 0) AS r,
    arraySlice(arrayConcat(arrayWithConstant(w, 0), src), 1, len) AS u,
    arrayResize(arraySlice(src, w + 1), len, 0) AS d,
    0x00FF00FF AS mask_rb,
    0x0000FF00 AS mask_g
SELECT
    pos_x, pos_y,
    arrayMap((c, l, r, u, d) -> bitOr(bitAnd(bitShiftRight((bitAnd(c, mask_rb) * 4) + bitAnd(l, mask_rb) + bitAnd(r, mask_rb) + bitAnd(u, mask_rb) + bitAnd(d, mask_rb), 3), mask_rb), bitAnd(bitShiftRight((bitAnd(c, mask_g) * 4) + bitAnd(l, mask_g) + bitAnd(r, mask_g) + bitAnd(u, mask_g) + bitAnd(d, mask_g), 3), mask_g)), src, l, r, u, d) AS image_data
FROM doomhouse.rendered_frame_2;

-- =========================================================
-- VIEW 3: QUARTER 3
-- =========================================================
CREATE MATERIALIZED VIEW doomhouse.post_process_materialized_3
TO doomhouse.rendered_frame_post_processed_3
AS
WITH
    640 AS w,
    image_data AS src,
    length(src) AS len,
    arraySlice(arrayConcat([0], src), 1, len) AS l,
    arrayResize(arraySlice(src, 2), len, 0) AS r,
    arraySlice(arrayConcat(arrayWithConstant(w, 0), src), 1, len) AS u,
    arrayResize(arraySlice(src, w + 1), len, 0) AS d,
    0x00FF00FF AS mask_rb,
    0x0000FF00 AS mask_g
SELECT
    pos_x, pos_y,
    arrayMap((c, l, r, u, d) -> bitOr(bitAnd(bitShiftRight((bitAnd(c, mask_rb) * 4) + bitAnd(l, mask_rb) + bitAnd(r, mask_rb) + bitAnd(u, mask_rb) + bitAnd(d, mask_rb), 3), mask_rb), bitAnd(bitShiftRight((bitAnd(c, mask_g) * 4) + bitAnd(l, mask_g) + bitAnd(r, mask_g) + bitAnd(u, mask_g) + bitAnd(d, mask_g), 3), mask_g)), src, l, r, u, d) AS image_data
FROM doomhouse.rendered_frame_3;

-- =========================================================
-- VIEW 4: QUARTER 4
-- =========================================================
CREATE MATERIALIZED VIEW doomhouse.post_process_materialized_4
TO doomhouse.rendered_frame_post_processed_4
AS
WITH
    640 AS w,
    image_data AS src,
    length(src) AS len,
    arraySlice(arrayConcat([0], src), 1, len) AS l,
    arrayResize(arraySlice(src, 2), len, 0) AS r,
    arraySlice(arrayConcat(arrayWithConstant(w, 0), src), 1, len) AS u,
    arrayResize(arraySlice(src, w + 1), len, 0) AS d,
    0x00FF00FF AS mask_rb,
    0x0000FF00 AS mask_g
SELECT
    pos_x, pos_y,
    arrayMap((c, l, r, u, d) -> bitOr(bitAnd(bitShiftRight((bitAnd(c, mask_rb) * 4) + bitAnd(l, mask_rb) + bitAnd(r, mask_rb) + bitAnd(u, mask_rb) + bitAnd(d, mask_rb), 3), mask_rb), bitAnd(bitShiftRight((bitAnd(c, mask_g) * 4) + bitAnd(l, mask_g) + bitAnd(r, mask_g) + bitAnd(u, mask_g) + bitAnd(d, mask_g), 3), mask_g)), src, l, r, u, d) AS image_data
FROM doomhouse.rendered_frame_4;
