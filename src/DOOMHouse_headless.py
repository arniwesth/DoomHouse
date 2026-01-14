import clickhouse_connect
import sys
import array
import math
import os
import time
import concurrent.futures
import random
from PIL import Image
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
HOST = os.getenv('CLICKHOUSE_HOST', 'localhost')
PORT = int(os.getenv('CLICKHOUSE_PORT', '8123'))
USER = os.getenv('CLICKHOUSE_USER', 'default')
PASS = os.getenv('CLICKHOUSE_PASS', '')

# Movement Constants
MOVE_SPEED = 0.3
ROT_SPEED = 0.15

# Texture Settings
TEXTURE_SIZE = 512  # 512x512 pixels
TEXTURE_INTENSITY = 1.2

TEXTURE_THEMES = {
    "classic": {
        "wall1": "texture20.png",
        "wall2": "texture20.png",
        "floor": "texture28.png",
        "ceiling": "texture38.png"
    },
    "dungeon": {
        "wall1": "texture41.png",
        "wall2": "texture41.png",
        "floor": "texture40.png",
        "ceiling": "texture39.png"
    }
}

class DOOMHouseHeadless:
    def __init__(self):
        print("🚀 Starting DOOMHouse Headless Performance Profiler")
        
        # Connect to DB
        try:
            # Create a pool of clients for parallel queries (8 streams)
            self.clients = []
            print("🔌 Connecting to ClickHouse (initializing 8 clients)...")
            for i in range(8):
                self.clients.append(clickhouse_connect.get_client(
                    host=HOST, port=PORT, username=USER, password=PASS
                ))
            self.client = self.clients[0] # Main client for other ops

            # Print ClickHouse version
            version = self.client.query("SELECT version()").result_rows[0][0]
            print(f"ClickHouse version: {version}")

            self.client.command("CREATE DATABASE IF NOT EXISTS doomhouse")
            self.cleanup_database()
            self.initialize_game_data()
            
            # Theme selection
            self.theme_names = list(TEXTURE_THEMES.keys())
            self.current_theme_idx = 0
            self.current_theme = self.theme_names[self.current_theme_idx]
            
            self.initialize_texture()
            self.initialize_tables()
        except Exception as e:
            print(f"Error connecting to ClickHouse: {e}")
            sys.exit(1)

        # Frame tracking
        self.frame_id = 0

        # Initial Player State
        self.pos_x = 3.5
        self.pos_y = 3.5
        self.dir_x = -1.0
        self.dir_y = 0.0
        self.plane_x = 0.0
        self.plane_y = 0.66

        # Performance Tracking
        self.total_insert_time = 0.0
        self.insert_count = 0
        self.total_select_time = 0.0
        self.select_count = 0
        
        # Simulation State
        self.sim_state = "forward"
        self.sim_state_duration = 0

    def load_texture(self, filename):
        if not os.path.exists(filename):
            print(f"⚠️ Warning: '{filename}' not found. Using fallback gray noise.")
            fallback = [(100, 100, 100) for _ in range(TEXTURE_SIZE**2)]
            return fallback

        print(f"🎨 Loading '{filename}' for database initialization...")
        try:
            with Image.open(filename) as img:
                img = img.convert("RGB")
                img = img.resize((TEXTURE_SIZE, TEXTURE_SIZE), Image.NEAREST)
                pixels = list(img.getdata())
                return pixels
        except Exception as e:
            print(f"Error processing texture: {e}")
            sys.exit(1)

    def _setup_texture_resource(self, table_name, dict_name, texture_file):
        """Helper to create table, dictionary and load texture data."""
        try:
            self.client.command(f"DROP TABLE IF EXISTS doomhouse.{table_name}")
            self.client.command(f"""
                CREATE TABLE doomhouse.{table_name} (
                    id UInt32,
                    r UInt8,
                    g UInt8,
                    b UInt8
                ) ENGINE = MergeTree ORDER BY id
            """)
            
            self.client.command(f"DROP DICTIONARY IF EXISTS doomhouse.{dict_name}")
            self.client.command(f"""
                CREATE DICTIONARY doomhouse.{dict_name} (
                    id UInt32,
                    r UInt8,
                    g UInt8,
                    b UInt8
                )
                PRIMARY KEY id
                SOURCE(CLICKHOUSE(TABLE '{table_name}' DB 'doomhouse'))
                LIFETIME(MIN 3600 MAX 3600)
                LAYOUT(FLAT())
            """)
        except Exception as e:
            print(f"Error creating texture table/dictionary {dict_name}: {e}")

        texture_path = os.path.join("textures", texture_file)
        tex_data = self.load_texture(texture_path)
        
        print(f"💾 Initializing doomhouse.{table_name} table with {len(tex_data)} pixels...")
        try:
            self.client.command(f"TRUNCATE TABLE doomhouse.{table_name}")
            data = [
                [
                    i + 1,
                    max(0, min(255, int(r * TEXTURE_INTENSITY))),
                    max(0, min(255, int(g * TEXTURE_INTENSITY))),
                    max(0, min(255, int(b * TEXTURE_INTENSITY)))
                ]
                for i, (r, g, b) in enumerate(tex_data)
            ]
            self.client.insert(f'doomhouse.{table_name}', data)
            
            print(f"🔄 Reloading dictionary doomhouse.{dict_name}...")
            self.client.command(f"SYSTEM RELOAD DICTIONARY doomhouse.{dict_name}")
        except Exception as e:
            print(f"Error initializing texture {dict_name}: {e}")

    def initialize_texture(self):
        theme = TEXTURE_THEMES[self.current_theme]
        print(f"🌟 Initializing textures for theme: {self.current_theme}")
        
        self._setup_texture_resource("tex_wall1_source", "dict_tex_wall1_data", theme["wall1"])
        self._setup_texture_resource("tex_wall2_source", "dict_tex_wall2_data", theme["wall2"])
        self._setup_texture_resource("tex_floor_source", "dict_tex_floor_data", theme["floor"])
        self._setup_texture_resource("tex_ceiling_source", "dict_tex_ceiling_data", theme["ceiling"])

    def cleanup_database(self):
        print("🧹 Cleaning up existing database objects...")
        try:
            self.client.command("DROP VIEW IF EXISTS doomhouse.render_materialized")
            self.client.command("DROP VIEW IF EXISTS doomhouse.post_process_materialized")
            self.client.command("DROP VIEW IF EXISTS doomhouse.render_materialized_top")
            self.client.command("DROP VIEW IF EXISTS doomhouse.render_materialized_bottom")
            self.client.command("DROP VIEW IF EXISTS doomhouse.post_process_materialized_top")
            self.client.command("DROP VIEW IF EXISTS doomhouse.post_process_materialized_bottom")
            
            for i in range(1, 9):
                self.client.command(f"DROP VIEW IF EXISTS doomhouse.render_materialized_{i}")
                self.client.command(f"DROP VIEW IF EXISTS doomhouse.post_process_materialized_{i}")

            dicts = [
                "dict_map_data", "dict_floor_dist", "dict_tex_data", "dict_tex_wall_data",
                "dict_tex_wall1_data", "dict_tex_wall2_data", "dict_tex_floor_data", "dict_tex_ceiling_data"
            ]
            for d in dicts:
                self.client.command(f"DROP DICTIONARY IF EXISTS doomhouse.{d}")
                
            tables = [
                "map_source", "floor_dist_source", "tex_source", "tex_wall_source",
                "tex_wall1_source", "tex_wall2_source", "tex_floor_source", "tex_ceiling_source",
                "player_input", "rendered_frame", "rendered_frame_post_processed",
                "rendered_frame_top", "rendered_frame_bottom",
                "rendered_frame_post_processed_top", "rendered_frame_post_processed_bottom"
            ]
            for t in tables:
                self.client.command(f"DROP TABLE IF EXISTS doomhouse.{t}")
            
            for i in range(1, 9):
                self.client.command(f"DROP TABLE IF EXISTS doomhouse.rendered_frame_{i}")
                self.client.command(f"DROP TABLE IF EXISTS doomhouse.rendered_frame_post_processed_{i}")

        except Exception as e:
            print(f"Note: Cleanup encountered an issue: {e}")

    def execute_sql_script(self, script_path):
        if not os.path.exists(script_path):
            print(f"⚠️ Warning: SQL script '{script_path}' not found.")
            return
        
        with open(script_path, 'r') as f:
            content = f.read()
            
        statements = content.split(';')
        for stmt in statements:
            lines = stmt.split('\n')
            clean_lines = []
            in_block_comment = False
            for line in lines:
                if in_block_comment:
                    if '*/' in line:
                        in_block_comment = False
                        line = line.split('*/', 1)[1]
                    else:
                        continue
                
                if not in_block_comment:
                    if '/*' in line:
                        if '*/' in line:
                            import re
                            line = re.sub(r'/\*.*?\*/', '', line)
                        else:
                            in_block_comment = True
                            line = line.split('/*', 1)[0]
                    
                    if '--' in line:
                        line = line.split('--', 1)[0]
                    
                    if line.strip():
                        clean_lines.append(line)
            
            stmt = '\n'.join(clean_lines).strip()
            if not stmt:
                continue
            
            # Try to extract name for dropping (simplified for headless)
            name = None
            upper_stmt = stmt.upper()
            if "CREATE TABLE" in upper_stmt:
                parts = stmt.split()
                for i, p in enumerate(parts):
                    if p.upper() == "TABLE":
                        name = parts[i+1]
                        break
            elif "CREATE DICTIONARY" in upper_stmt:
                parts = stmt.split()
                for i, p in enumerate(parts):
                    if p.upper() == "DICTIONARY":
                        name = parts[i+1]
                        break
            elif "CREATE MATERIALIZED VIEW" in upper_stmt:
                parts = stmt.split()
                for i, p in enumerate(parts):
                    if p.upper() == "VIEW":
                        name = parts[i+1]
                        break
            
            if name:
                name = name.split('(')[0].strip()
                if "DICTIONARY" in upper_stmt:
                    self.client.command(f"DROP DICTIONARY IF EXISTS {name}")
                elif "VIEW" in upper_stmt:
                    self.client.command(f"DROP VIEW IF EXISTS {name}")
                else:
                    self.client.command(f"DROP TABLE IF EXISTS {name}")
            
            try:
                self.client.command(stmt)
            except Exception as e:
                print(f"Error executing statement: {e}")

    def initialize_game_data(self):
        print("🎮 Initializing game data (map, floor distances)...")
        self.execute_sql_script("src/SQL/create_source_tables.sql")
        self.execute_sql_script("src/SQL/create_dictionaries.sql")

    def initialize_tables(self):
        sql_files = [
            "src/SQL/player_input_table.sql",
            "src/SQL/rendered_frame_table.sql",
            "src/SQL/rendered_frame_post_processed_table.sql",
            "src/SQL/render_view.sql",
            "src/SQL/post_process_view.sql",
        ]
        
        for sql_file in sql_files:
            self.execute_sql_script(sql_file)

    def turn_right_logic(self):
        old_dir_x = self.dir_x
        self.dir_x = self.dir_x * math.cos(-ROT_SPEED) - self.dir_y * math.sin(-ROT_SPEED)
        self.dir_y = old_dir_x * math.sin(-ROT_SPEED) + self.dir_y * math.cos(-ROT_SPEED)
        old_plane_x = self.plane_x
        self.plane_x = self.plane_x * math.cos(-ROT_SPEED) - self.plane_y * math.sin(-ROT_SPEED)
        self.plane_y = old_plane_x * math.sin(-ROT_SPEED) + self.plane_y * math.cos(-ROT_SPEED)

    def turn_left_logic(self):
        old_dir_x = self.dir_x
        self.dir_x = self.dir_x * math.cos(ROT_SPEED) - self.dir_y * math.sin(ROT_SPEED)
        self.dir_y = old_dir_x * math.sin(ROT_SPEED) + self.dir_y * math.cos(ROT_SPEED)
        old_plane_x = self.plane_x
        self.plane_x = self.plane_x * math.cos(ROT_SPEED) - self.plane_y * math.sin(ROT_SPEED)
        self.plane_y = old_plane_x * math.sin(ROT_SPEED) + self.plane_y * math.cos(ROT_SPEED)

    def simulate_input(self):
        # Simple state machine for random movement
        if self.sim_state_duration <= 0:
            # Pick new state
            r = random.random()
            if r < 0.6:
                self.sim_state = "forward"
                self.sim_state_duration = random.randint(10, 30)
            elif r < 0.7:
                self.sim_state = "backward"
                self.sim_state_duration = random.randint(5, 15)
            elif r < 0.85:
                self.sim_state = "left"
                self.sim_state_duration = random.randint(3, 10)
            else:
                self.sim_state = "right"
                self.sim_state_duration = random.randint(3, 10)
        
        self.sim_state_duration -= 1
        
        tx, ty = self.pos_x, self.pos_y
        
        if self.sim_state == "left":
            self.turn_left_logic()
        elif self.sim_state == "right":
            self.turn_right_logic()
        elif self.sim_state == "forward":
            tx += self.dir_x * MOVE_SPEED
            ty += self.dir_y * MOVE_SPEED
        elif self.sim_state == "backward":
            tx -= self.dir_x * MOVE_SPEED
            ty -= self.dir_y * MOVE_SPEED
            
        return tx, ty

    def push_input(self, target_x, target_y):
        try:
            start_time = time.time()
            self.frame_id += 1
            self.client.command(f"""
                INSERT INTO doomhouse.player_input
                (frame_id, old_x, old_y, try_x, try_y, dir_x, dir_y, plane_x, plane_y)
                VALUES ({self.frame_id}, {self.pos_x}, {self.pos_y}, {target_x}, {target_y},
                        {self.dir_x}, {self.dir_y}, {self.plane_x}, {self.plane_y})
            """)            
            self.insert_time = (time.time() - start_time) * 1000 # in ms
            self.total_insert_time += self.insert_time
            self.insert_count += 1
            self.avg_insert_time = self.total_insert_time / self.insert_count
            
            # In headless mode, we call render immediately after push
            self.render()
        except Exception as e:
            print(f"Input Error: {e}")

    def render(self):
        try:
            start_time = time.time()
            
            # Parallel Query Execution
            results = [None] * 8
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                futures = []
                for i in range(8):
                    query = f"SELECT pos_x, pos_y, image_data FROM doomhouse.rendered_frame_post_processed_{i+1}"
                    futures.append(executor.submit(self.clients[i].query, query))
                
                for i, future in enumerate(futures):
                    results[i] = future.result()

            if any(not r.result_rows for r in results):
                return

            select_time = (time.time() - start_time) * 1000 # in ms
            self.total_select_time += select_time
            self.select_count += 1
            avg_select_time = self.total_select_time / self.select_count

            # Update position from DB result (collision detection happened in DB)
            new_x = results[0].result_rows[0][0]
            new_y = results[0].result_rows[0][1]
            
            # Check if we actually moved (for simulation logic)
            if abs(new_x - self.pos_x) < 0.001 and abs(new_y - self.pos_y) < 0.001:
                # We hit a wall or didn't move
                if self.sim_state == "forward":
                    # If we were trying to move forward and stopped, force a turn next
                    self.sim_state = random.choice(["left", "right"])
                    self.sim_state_duration = random.randint(5, 15)

            self.pos_x = new_x
            self.pos_y = new_y
            
            # Calculate stats
            fps = 1000/(self.insert_time + select_time)
            avgfps = 1000/(self.avg_insert_time + avg_select_time)
            
            # Console Logging
            print(f"Frame {self.frame_id:05d} | FPS: {fps:5.1f} (Avg: {avgfps:5.1f}) | "
                  f"Ins: {self.insert_time:5.1f}ms | Sel: {select_time:5.1f}ms | "
                  f"Pos: ({self.pos_x:5.2f}, {self.pos_y:5.2f}) | State: {self.sim_state}")

        except Exception as e:
            print(f"Render Error: {e}")

    def run(self):
        print("🏃 Starting continuous simulation loop (Press Ctrl+C to stop)...")
        try:
            while True:
                tx, ty = self.simulate_input()
                self.push_input(tx, ty)
                # No sleep - run as fast as possible for stress testing
        except KeyboardInterrupt:
            print("\n🛑 Simulation stopped by user.")
            print(f"Final Stats: {self.frame_id} frames rendered.")
            print(f"Average FPS: {1000/(self.avg_insert_time + self.total_select_time / self.select_count):.2f}")

def main():
    app = DOOMHouseHeadless()
    app.run()

if __name__ == "__main__":
    main()
