CREATE TABLE doomhouse.player_input
(
    frame_id UInt64,
    old_x Float64,
    old_y Float64,
    try_x Float64,
    try_y Float64,
    dir_x Float64,
    dir_y Float64,
    plane_x Float64,
    plane_y Float64,
    timestamp DateTime DEFAULT now()
)
ENGINE = Memory 
SETTINGS min_rows_to_keep = 1, max_rows_to_keep = 1;
