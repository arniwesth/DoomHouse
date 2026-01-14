
template = """
-- =========================================================
-- VIEW {i}: STRIP {i} (Rows {start}-{end})
-- =========================================================
CREATE MATERIALIZED VIEW doomhouse.render_materialized_{i}
TO doomhouse.rendered_frame_{i}
AS
WITH 
    640 AS W,
    480 AS H,
    240 AS H_HALF,
    15 AS MAP_W,
    512 AS TEX_SIZE,
    CAST(TEX_SIZE - 1, 'Int32') AS TEX_MAX,
    25 AS RAY_STEPS,
    CAST(1.0 / W, 'Float32') AS W_INV

SELECT
    any(valid_x) as pos_x,
    any(valid_y) as pos_y,
    arrayMap(x -> x.2, arraySort(k -> k.1, groupArray((y * W + x, final_color)))) AS image_data
FROM
(
    SELECT
        x, y,
        valid_x, valid_y,
        multiIf(
            toInt32(y) >= draw_start AND toInt32(y) <= draw_end,
            CAST(
                bitOr(
                    bitOr(
                        bitShiftLeft(toUInt32(dictGet('doomhouse.dict_tex_wall1_data', 'r', w_tex_idx) * base_shade), 0),
                        bitShiftLeft(toUInt32(dictGet('doomhouse.dict_tex_wall1_data', 'g', w_tex_idx) * base_shade), 8)
                    ),
                    bitShiftLeft(toUInt32(dictGet('doomhouse.dict_tex_wall1_data', 'b', w_tex_idx) * base_shade), 16)
                )
            , 'UInt32'),

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
            (1.0 - least(floor_dist * 0.125, 1.0)) as floor_shade,
            toUInt32((least(greatest(toInt32(y * rays.tex_step + rays.tex_base), 0), TEX_MAX) * TEX_SIZE) + rays.tx + 1) as w_tex_idx,
            toUInt32((
                bitAnd(toInt32((rays.valid_y + floor_dist * ((rays.hit_y - rays.valid_y) / (rays.perp_wall_dist + 0.001))) * TEX_SIZE), TEX_MAX) * TEX_SIZE) 
                + bitAnd(toInt32((rays.valid_x + floor_dist * ((rays.hit_x - rays.valid_x) / (rays.perp_wall_dist + 0.001))) * TEX_SIZE), TEX_MAX) 
                + 1
            ) as f_tex_idx
        FROM 
        (
            SELECT 
                x, valid_x, valid_y,
                toInt32(H_HALF - (H / (perp_wall_dist + 0.0001)) * 0.5) AS draw_start,
                toInt32(H_HALF + (H / (perp_wall_dist + 0.0001)) * 0.5) AS draw_end,
                (1.0 / (H / (perp_wall_dist + 0.0001))) * TEX_SIZE as tex_step,
                -(H_HALF - (H / (perp_wall_dist + 0.0001)) * 0.5) * tex_step as tex_base,
                (if(side, 0.6, 1.0) * (1.0 - least(least(hit_dist, 20.0) * 0.125, 1.0))) AS base_shade,
                least(if(side, hit_x_wall, hit_y_wall), TEX_MAX) AS tx,
                hit_x, hit_y, perp_wall_dist
            FROM 
            (
                SELECT 
                    *,
                    raw_hit_dist * (p_dir_x * r_dir_x + p_dir_y * r_dir_y) as perp_wall_dist,
                    (valid_x + r_dir_x * raw_hit_dist) as hit_x,
                    (valid_y + r_dir_y * raw_hit_dist) as hit_y,
                    toInt32((hit_x - floor(hit_x)) * TEX_SIZE) as hit_x_wall_raw,
                    toInt32((hit_y - floor(hit_y)) * TEX_SIZE) as hit_y_wall_raw,
                    if(bitAnd(intHash32(toInt32(hit_y)), 1) = 0, TEX_MAX - hit_x_wall_raw, hit_x_wall_raw) as hit_x_wall,
                    if(bitAnd(intHash32(toInt32(hit_x)), 1) = 0, TEX_MAX - hit_y_wall_raw, hit_y_wall_raw) as hit_y_wall
                FROM 
                (
                    SELECT *, least(dist_x, dist_y) as raw_hit_dist, least(dist_x, dist_y) as hit_dist, (dist_y < dist_x) as side
                    FROM (
                        SELECT 
                            *,
                            arrayMap(i -> (i - valid_x) / r_dir_x, steps) as d_x,
                            arrayMin(arrayMap((d, i) -> if(d > 0 AND d < 30 AND dictGet('doomhouse.dict_map_data', 'val', toUInt32(floor(valid_y + r_dir_y * d) * MAP_W + floor(valid_x + r_dir_x * d + if(r_dir_x > 0, 0.005, -0.005)) + 1)) > 0, d, 999.0), d_x, steps)) as dist_x,
                            arrayMap(i -> (i - valid_y) / r_dir_y, steps) as d_y,
                            arrayMin(arrayMap((d, i) -> if(d > 0 AND d < 30 AND dictGet('doomhouse.dict_map_data', 'val', toUInt32(floor(valid_y + r_dir_y * d + if(r_dir_y > 0, 0.005, -0.005)) * MAP_W + floor(valid_x + r_dir_x * d) + 1)) > 0, d, 999.0), d_y, steps)) as dist_y
                        FROM 
                        (
                            SELECT 
                                screen_col.number AS x,
                                p.valid_x, p.valid_y,
                                p.dir_x as p_dir_x, p.dir_y as p_dir_y,
                                (p.dir_x + p.plane_x * (2.0 * screen_col.number * W_INV - 1.0)) as r_dir_x,
                                (p.dir_y + p.plane_y * (2.0 * screen_col.number * W_INV - 1.0)) as r_dir_y,
                                range(1, RAY_STEPS) as steps
                            FROM 
                            (
                                SELECT 
                                    toFloat32(dir_x) as dir_x, toFloat32(dir_y) as dir_y, 
                                    toFloat32(plane_x) as plane_x, toFloat32(plane_y) as plane_y,
                                    if(dictGet('doomhouse.dict_map_data', 'val', toUInt32(floor(try_y + if(try_y > old_y, 0.2, -0.2)) * MAP_W + floor(valid_x_inter) + 1)) = 0, try_y, old_y) as valid_y,
                                    valid_x_inter as valid_x
                                FROM (
                                    SELECT *, if(dictGet('doomhouse.dict_map_data', 'val', toUInt32(floor(old_y) * MAP_W + floor(try_x + if(try_x > old_x, 0.2, -0.2)) + 1)) = 0, try_x, old_x) as valid_x_inter
                                    FROM doomhouse.player_input
                                ) AS pi
                            ) AS p
                            CROSS JOIN numbers(W) AS screen_col
                        )
                    )
                )
            )
        ) AS rays
        CROSS JOIN (
            SELECT 
                number + {offset} as y,
                if(number + {offset} < H_HALF, toInt32(H - 1 - (number + {offset})), toInt32(number + {offset})) as dist_lookup_idx,
                dictGet('doomhouse.dict_floor_dist', 'dist', toUInt32(dist_lookup_idx + 1)) as floor_dist
            FROM numbers(60)
        ) AS v_lines
    ) AS sub
);
"""

with open("src/SQL/render_view.sql", "w") as f:
    f.write("/* DOOMHouse 8-Way Split Render Views */\n")
    for i in range(1, 9):
        offset = (i - 1) * 60
        end = offset + 59
        f.write(template.format(i=i, start=offset, end=end, offset=offset))
        f.write("\n\n")
