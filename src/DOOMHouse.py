import clickhouse_connect
import sys
import array
import math
import os
import time
import tkinter as tk
import concurrent.futures
from PIL import Image, ImageDraw, ImageFont, ImageTk
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
#TEXTURE_SIZE = 64  # 64x64 pixels
#TEXTURE_SIZE = 256  # 256x256 pixels
TEXTURE_SIZE = 512  # 512x512 pixels
#OBS: Loading 1024x1024 texture maps currently does not work
#TEXTURE_SIZE = 1024  # 1024x1024 pixels
TEXTURE_INTENSITY = 1.2  # Texture intensity factor (1.0 = normal, <1.0 = darker, >1.0 = brighter)

# NOTE: Wall2 is currently not used
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

class DOOMHouse:
    def __init__(self):
        self.window_name = "DOOMHouse - ClickHouse SQL Game Engine"
        
        # Tkinter Setup
        self.root = tk.Tk()
        self.root.title(self.window_name)
        self.root.geometry("640x540")
        self.root.resizable(False, False)
        self.root.configure(bg="black")
        
        self.label = tk.Label(self.root, bg="black")
        self.label.pack()

        # Status Label at the bottom (Multi-line)
        self.status_label = tk.Label(
            self.root,
            text="",
            bg="black",
            fg="#00FF00",
            font=("Courier", 11, "bold"),
            justify=tk.LEFT,
            anchor="w",
            padx=10,
            pady=5
        )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Key State Tracking
        self.keys_pressed = set()
        self.root.bind("<KeyPress>", self._on_key_press)
        self.root.bind("<KeyRelease>", self._on_key_release)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # Connect to DB
        try:
            self.client = clickhouse_connect.get_client(
                host=HOST, port=PORT, username=USER, password=PASS
            )
            # Second client for parallel queries
            self.client2 = clickhouse_connect.get_client(
                host=HOST, port=PORT, username=USER, password=PASS
            )
            self.client3 = clickhouse_connect.get_client(
                host=HOST, port=PORT, username=USER, password=PASS
            )
            self.client4 = clickhouse_connect.get_client(
                host=HOST, port=PORT, username=USER, password=PASS
            )
            
            # Get and print ClickHouse version
            version = self.client.query("SELECT version()").result_rows[0][0]
            print(f"Connected to ClickHouse version: {version}")
            
            # Version check
            try:
                v_parts = [int(p) for p in version.split('.')]
                required_v = [26, 1, 1, 562]
                is_supported = True
                for i in range(min(len(v_parts), len(required_v))):
                    if v_parts[i] < required_v[i]:
                        is_supported = False
                        break
                    elif v_parts[i] > required_v[i]:
                        break
                
                if not is_supported:
                    print("\n" + "="*80)
                    print("**OBS**: Due to an issue with some newer versions of ClickHouse this program only supports ClickHosue version `26.1.1.562` or later.")
                    print("="*80 + "\n")
            except Exception as ve:
                print(f"Could not parse ClickHouse version for compatibility check: {ve}")
            
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

        # GUI Setup
        self.running = True
        self.in_splash = True

        # Performance Tracking
        self.total_insert_time = 0.0
        self.insert_count = 0
        self.total_select_time = 0.0
        self.select_count = 0
                
        # Show Splash Screen
        self.show_splash()

    def show_splash(self):
        splash_path = os.path.join("images", "splash.png")
        if os.path.exists(splash_path):
            try:
                with Image.open(splash_path) as img:
                    img = img.convert("RGB")
                    img = img.resize((640, 480), Image.LANCZOS)
                    
                    # Add text
                    draw = ImageDraw.Draw(img)
                    text = "Press any key to start"
                    
                    # Try to load a bigger font
                    font = None
                    font_paths = [
                        "/System/Library/Fonts/Supplemental/Arial.ttf",
                        "/Library/Fonts/Arial.ttf",
                        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
                    ]
                    for path in font_paths:
                        if os.path.exists(path):
                            try:
                                font = ImageFont.truetype(path, 30)
                                break
                            except:
                                continue
                    
                    if font is None:
                        font = ImageFont.load_default()

                    # Center text
                    try:
                        # Pillow >= 8.0.0
                        left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
                        w, h = right - left, bottom - top
                    except AttributeError:
                        # Fallback for older Pillow
                        w, h = draw.textsize(text, font=font)
                    
                    x = (640 - w) / 2
                    y = 400
                    
                    # Draw shadow for visibility
                    draw.text((x+2, y+2), text, fill=(0, 0, 0), font=font)
                    # Draw main text
                    draw.text((x, y), text, fill=(255, 255, 255), font=font)
                    
                    # Convert PIL to ImageTk
                    self.photo = ImageTk.PhotoImage(img)
                    self.label.config(image=self.photo)
                    self.root.update_idletasks()
            except Exception as e:
                print(f"Error loading splash screen: {e}")

    def start_game(self):
        if not self.in_splash:
            return
        self.in_splash = False
        # Initial Input to ensure a frame exists
        self.push_input(self.pos_x, self.pos_y)

    def _on_key_press(self, event):
        key = event.keysym.lower()
        self.keys_pressed.add(key)
        if self.in_splash:
            self.start_game()
        
        # Theme switching
        if key == 't':
            self.switch_theme()

    def _on_key_release(self, event):
        key = event.keysym.lower()
        self.keys_pressed.discard(key)

    def _on_close(self):
        self.running = False
        self.root.destroy()

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
                    v UInt8
                ) ENGINE = MergeTree ORDER BY id
            """)
            
            self.client.command(f"DROP DICTIONARY IF EXISTS doomhouse.{dict_name}")
            self.client.command(f"""
                CREATE DICTIONARY doomhouse.{dict_name} (
                    id UInt32,
                    v UInt8
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
                    max(0, min(255, int(((r + g + b) / 3.0) * TEXTURE_INTENSITY)))
                ]
                for i, (r, g, b) in enumerate(tex_data)
            ]
            self.client.insert(f'doomhouse.{table_name}', data)
            
            print(f"🔄 Reloading dictionary doomhouse.{dict_name}...")
            self.client.command(f"SYSTEM RELOAD DICTIONARY doomhouse.{dict_name}")
        except Exception as e:
            print(f"Error initializing texture {dict_name}: {e}")

    def switch_theme(self):
        self.current_theme_idx = (self.current_theme_idx + 1) % len(self.theme_names)
        self.current_theme = self.theme_names[self.current_theme_idx]
        print(f"🎭 Switching to theme: {self.current_theme}")
        self.initialize_texture()
        # We don't necessarily need to re-initialize tables, but we might need to reload the view
        # if we change how it references dictionaries. For now, let's just reload textures.
        # Actually, if we use the same dictionary names, we just need to reload them.
        self.push_input(self.pos_x, self.pos_y) # Force a re-render

    def initialize_texture(self):
        theme = TEXTURE_THEMES[self.current_theme]
        print(f"🌟 Initializing textures for theme: {self.current_theme}")
        
        # Initialize Wall Textures
        self._setup_texture_resource("tex_wall1_source", "dict_tex_wall1_data", theme["wall1"])
        self._setup_texture_resource("tex_wall2_source", "dict_tex_wall2_data", theme["wall2"])
        
        # Initialize Floor Texture
        self._setup_texture_resource("tex_floor_source", "dict_tex_floor_data", theme["floor"])
        
        # Initialize Ceiling Texture
        self._setup_texture_resource("tex_ceiling_source", "dict_tex_ceiling_data", theme["ceiling"])

    def cleanup_database(self):
        print("🧹 Cleaning up existing database objects to avoid dependency errors...")
        try:
            # 1. Drop Materialized Views first
            self.client.command("DROP VIEW IF EXISTS doomhouse.render_materialized")
            self.client.command("DROP VIEW IF EXISTS doomhouse.post_process_materialized")
            self.client.command("DROP VIEW IF EXISTS doomhouse.render_materialized_top")
            self.client.command("DROP VIEW IF EXISTS doomhouse.render_materialized_bottom")
            self.client.command("DROP VIEW IF EXISTS doomhouse.post_process_materialized_top")
            self.client.command("DROP VIEW IF EXISTS doomhouse.post_process_materialized_bottom")
            for i in range(1, 5):
                self.client.command(f"DROP VIEW IF EXISTS doomhouse.render_materialized_{i}")
                self.client.command(f"DROP VIEW IF EXISTS doomhouse.post_process_materialized_{i}")
            
            # 2. Drop Dictionaries
            dicts = [
                "dict_map_data", "dict_floor_dist", "dict_tex_data", "dict_tex_wall_data",
                "dict_tex_wall1_data", "dict_tex_wall2_data", "dict_tex_floor_data", "dict_tex_ceiling_data"
            ]
            for d in dicts:
                self.client.command(f"DROP DICTIONARY IF EXISTS doomhouse.{d}")
                
            # 3. Drop Tables
            tables = [
                "map_source", "floor_dist_source", "tex_source", "tex_wall_source",
                "tex_wall1_source", "tex_wall2_source", "tex_floor_source", "tex_ceiling_source",
                "player_input", "rendered_frame", "rendered_frame_post_processed",
                "rendered_frame_top", "rendered_frame_bottom",
                "rendered_frame_post_processed_top", "rendered_frame_post_processed_bottom"
            ]
            for t in tables:
                self.client.command(f"DROP TABLE IF EXISTS doomhouse.{t}")
            for i in range(1, 5):
                self.client.command(f"DROP TABLE IF EXISTS doomhouse.rendered_frame_{i}")
                self.client.command(f"DROP TABLE IF EXISTS doomhouse.rendered_frame_post_processed_{i}")
        except Exception as e:
            print(f"Note: Cleanup encountered an issue: {e}")

    def execute_sql_script(self, script_path):
        """Helper to execute a SQL script that may contain multiple statements."""
        if not os.path.exists(script_path):
            print(f"⚠️ Warning: SQL script '{script_path}' not found.")
            return
        
        with open(script_path, 'r') as f:
            content = f.read()
            
        # Split by semicolon
        statements = content.split(';')
        for stmt in statements:
            # Remove comments
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
            
            # Try to extract name for dropping
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
            
            print(f"💾 Executing statement from {script_path}...")
            try:
                self.client.command(stmt)
            except Exception as e:
                print(f"Error executing statement: {e}")

    def initialize_game_data(self):
        print("🎮 Initializing game data (map, floor distances)...")
        self.execute_sql_script("src/SQL/create_source_tables.sql")
        self.execute_sql_script("src/SQL/create_dictionaries.sql")

    def initialize_tables(self):
        # Re-create tables to ensure schema matches
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

    def process_input(self):
        moved = False
        
        # Rotation
        if 'left' in self.keys_pressed or 'a' in self.keys_pressed:
            self.turn_left_logic()
            moved = True
        if 'right' in self.keys_pressed or 'd' in self.keys_pressed:
            self.turn_right_logic()
            moved = True
            
        # Movement
        tx, ty = self.pos_x, self.pos_y
        if 'up' in self.keys_pressed or 'w' in self.keys_pressed:
            tx += self.dir_x * MOVE_SPEED
            ty += self.dir_y * MOVE_SPEED
            moved = True
        if 'down' in self.keys_pressed or 's' in self.keys_pressed:
            tx -= self.dir_x * MOVE_SPEED
            ty -= self.dir_y * MOVE_SPEED
            moved = True
            
        if moved:
            self.push_input(tx, ty)

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
            print(f"Insert: {self.insert_time:.2f}ms (Avg: {self.avg_insert_time:.2f}ms)")

            self.render()
        except Exception as e:
            print(f"Input Error: {e}")

    def run(self):
        self.update_loop()
        self.root.mainloop()

    def update_loop(self):
        if not self.running:
            return
            
        if not self.in_splash:
            if 'escape' in self.keys_pressed:
                self._on_close()
                return
            self.process_input()
            
        self.root.after(16, self.update_loop) # ~60 FPS target for input check

    def render(self):
        try:
            start_time = time.time()
            
            # Parallel Query Execution
            # We launch four concurrent queries to fetch the quarters of the frame.
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                future1 = executor.submit(
                    self.client.query,
                    "SELECT pos_x, pos_y, image_data FROM doomhouse.rendered_frame_post_processed_1"
                )
                future2 = executor.submit(
                    self.client2.query,
                    "SELECT pos_x, pos_y, image_data FROM doomhouse.rendered_frame_post_processed_2"
                )
                future3 = executor.submit(
                    self.client3.query,
                    "SELECT pos_x, pos_y, image_data FROM doomhouse.rendered_frame_post_processed_3"
                )
                future4 = executor.submit(
                    self.client4.query,
                    "SELECT pos_x, pos_y, image_data FROM doomhouse.rendered_frame_post_processed_4"
                )
                
                result1 = future1.result()
                result2 = future2.result()
                result3 = future3.result()
                result4 = future4.result()

            if not result1.result_rows or not result2.result_rows or not result3.result_rows or not result4.result_rows:
                return

            # Calculate render time
            select_time = (time.time() - start_time) * 1000 # in ms
            self.total_select_time += select_time
            self.select_count += 1
            avg_select_time = self.total_select_time / self.select_count
            print(f"Select (Parallel 4-way): {select_time:.2f}ms (Avg: {avg_select_time:.2f}ms)")

            # Set new position (synced from DB - using first result)
            self.pos_x = result1.result_rows[0][0]
            self.pos_y = result1.result_rows[0][1]
            
            # Compositing Step: Stitch the four partial image buffers
            pixel_data = (
                result1.result_rows[0][2] + 
                result2.result_rows[0][2] + 
                result3.result_rows[0][2] + 
                result4.result_rows[0][2]
            )
            
            # Convert list of UInt32 to bytes efficiently.
            # Each UInt32 is [R, G, B, 0] in little-endian memory.
            raw_bytes = array.array('I', pixel_data).tobytes()
            
            # Create image from raw bytes (640x480)
            image = Image.frombytes("RGB", (640, 480), raw_bytes, "raw", "RGBX")

            # Convert PIL to ImageTk
            self.photo = ImageTk.PhotoImage(image)
            self.label.config(image=self.photo)
            
            # Update status text (Multi-line)
            fps = 1000/(self.insert_time + select_time)
            avgfps = 1000/(self.avg_insert_time + avg_select_time)
            line1 = f"{fps:2.1f}fps (avg: {avgfps:2.1f}fps) | Insert: {self.insert_time:3.2f}ms (avg: {self.avg_insert_time:3.2f}ms) | Select: {select_time:3.2f}ms (avg: {avg_select_time:3.2f}ms)"
            line2 = f"Pos: ({self.pos_x:5.2f}, {self.pos_y:5.2f}) | Theme: {self.current_theme.upper()} (Press 'T' to switch theme)"

            self.status_label.config(text=f"{line1}\n{line2}")
            
            self.root.update_idletasks()

            self.pos_x = result1.result_rows[0][0]
            self.pos_y = result1.result_rows[0][1]
        except Exception as e:
            print(f"Render Error: {e}")

def main():
    app = DOOMHouse()
    app.run()

if __name__ == "__main__":
    main()
