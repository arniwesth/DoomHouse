CREATE DATABASE IF NOT EXISTS doomhouse;

-- 1. Map Data Source
CREATE TABLE doomhouse.map_source (
    id UInt32, 
    val UInt8
) ENGINE = MergeTree ORDER BY id;

INSERT INTO doomhouse.map_source
WITH [
    1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
    1,0,0,0,0,0,0,1,0,0,0,0,0,0,1,
    1,0,0,1,0,0,2,1,0,0,1,0,0,2,1,
    1,0,0,0,0,0,0,1,0,0,0,0,0,0,1,
    1,0,2,0,0,0,0,0,0,2,0,0,0,0,1,
    1,0,0,1,0,0,0,1,0,0,1,0,0,0,1,
    1,0,0,0,0,0,0,1,0,0,0,0,0,0,1,
    1,1,1,0,1,1,1,1,1,1,0,1,1,1,1,
    1,0,0,0,0,0,0,1,0,0,0,0,0,0,1,
    1,0,0,1,0,0,2,1,0,0,1,0,0,2,1,
    1,0,0,0,0,0,0,1,0,0,0,0,0,0,1,
    1,0,2,0,0,0,0,0,0,2,0,0,0,0,1,
    1,0,0,1,0,0,0,1,0,0,1,0,0,0,1,
    1,0,0,0,0,0,0,1,0,0,0,0,0,0,1,
    1,1,1,1,1,1,1,1,1,1,1,1,1,1,1
] AS map_data
SELECT 
    idx AS id, 
    map_data[idx] AS val 
FROM (SELECT arrayJoin(arrayEnumerate(map_data)) AS idx);

-- 2. Floor Distance Source
CREATE TABLE doomhouse.floor_dist_source (
    id UInt32, 
    dist Float32
) ENGINE = MergeTree ORDER BY id;

INSERT INTO doomhouse.floor_dist_source
SELECT 
    number + 1 as id, 
    if(number <= 240, 0.0, 480.0 / (2.0 * number - 480.0)) as dist
FROM numbers(480);

-- 3. Texture Data Sources (Placeholder tables, populated by Python client)
CREATE TABLE IF NOT EXISTS doomhouse.tex_wall1_source (id UInt32, v UInt8) ENGINE = MergeTree ORDER BY id;
CREATE TABLE IF NOT EXISTS doomhouse.tex_wall2_source (id UInt32, v UInt8) ENGINE = MergeTree ORDER BY id;
CREATE TABLE IF NOT EXISTS doomhouse.tex_floor_source (id UInt32, v UInt8) ENGINE = MergeTree ORDER BY id;
CREATE TABLE IF NOT EXISTS doomhouse.tex_ceiling_source (id UInt32, v UInt8) ENGINE = MergeTree ORDER BY id;