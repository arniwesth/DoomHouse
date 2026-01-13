CREATE TABLE doomhouse.rendered_frame_top
(
    pos_x Float32,
    pos_y Float32,
    image_data Array(UInt32)
)
ENGINE = Memory 
SETTINGS min_rows_to_keep = 1, max_rows_to_keep = 1;

CREATE TABLE doomhouse.rendered_frame_bottom
(
    pos_x Float32,
    pos_y Float32,
    image_data Array(UInt32)
)
ENGINE = Memory 
SETTINGS min_rows_to_keep = 1, max_rows_to_keep = 1;
