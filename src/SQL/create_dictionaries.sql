CREATE DICTIONARY doomhouse.dict_map_data (id UInt32, val UInt8)
PRIMARY KEY id
SOURCE(CLICKHOUSE(TABLE 'map_source' DB 'doomhouse'))
LIFETIME(MIN 3600 MAX 3600)
LAYOUT(FLAT());

CREATE DICTIONARY doomhouse.dict_floor_dist (id UInt32, dist Float32)
PRIMARY KEY id
SOURCE(CLICKHOUSE(TABLE 'floor_dist_source' DB 'doomhouse'))
LIFETIME(MIN 3600 MAX 3600)
LAYOUT(FLAT());

-- Texture dictionaries are created and managed by the Python client in DOOMHouse.py