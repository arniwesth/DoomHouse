# DOOMHouse Technical Documentation

## Technology Stack

### Primary Technologies

| Component | Technology | Purpose |
|-----------|------------|---------|
| Rendering Engine | ClickHouse SQL | Executes raycasting and pixel generation |
| Client Application | Python 3 | GUI and input handling |
| GUI Framework | tkinter | Window and keyboard events |
| Image Processing | Pillow (PIL) | Texture loading and PPM parsing |
| DB Connector | clickhouse_connect | Query execution and result handling |
| Env Management | python-dotenv | Loading configuration from .env |

### ClickHouse Requirements
- **Version**: 26.1.x
- **Default Connection**: `localhost:8123`
- **Authentication**: Default user with no password (configurable)
- **No Tables Required**: The engine uses pure SQL computing with no persistent data

## Development Setup

### Prerequisites
```bash
# Python 3.x with pip
python3 --version

# ClickHouse server running locally
clickhouse-server --version
```

### Python Dependencies
```bash
pip install -r requirements.txt
```

Note: tkinter is included with standard Python installations on most systems.

### Running the Application
```bash
# From project root
python src/DOOMHouse.py
```

### Configuration Constants

Located at the top of [`DOOMHouse.py`](src/DOOMHouse.py:12), configuration is loaded from environment variables (via `.env` file):

| Variable | Env Key | Default |
|----------|---------|---------|
| `HOST` | `CLICKHOUSE_HOST` | `localhost` |
| `PORT` | `CLICKHOUSE_PORT` | `8123` |
| `USER` | `CLICKHOUSE_USER` | `default` |
| `PASS` | `CLICKHOUSE_PASS` | `''` |


## Technical Constraints

### Performance Considerations
- Each frame requires a full SQL query execution
- Query includes ~300+ lines of SQL logic
- Texture data (~16KB) is embedded in every query
- Network latency adds to frame time

### Resolution Limits
- Internal rendering: 640×480 pixels
- Each pixel requires color calculation in SQL
- Total: 307,200 pixels per frame

### ClickHouse SQL Limitations
- No recursive CTEs (limits raycasting iteration count to fixed range)
- Array operations are memory-intensive
- String formatting for PPM output adds overhead

## Dependencies Deep Dive

### clickhouse_connect
- PyPI: `clickhouse-connect`
- Used via [`get_client()`](src/DOOMHouse.py:32) for connection
- [`command()`](src/DOOMHouse.py:260) method executes queries and returns scalar result

### Pillow (PIL)
- [`Image.open()`](src/DOOMHouse.py:74) - Load texture PNG files
- [`Image.open(io.BytesIO())`](src/DOOMHouse.py:269) - Parse from bytes
- [`ImageTk.PhotoImage()`](src/DOOMHouse.py:271) - Convert to tkinter-displayable format
- `Image.NEAREST` - Nearest-neighbor interpolation for pixel-art style

### tkinter
- [`tk.Tk()`](src/DOOMHouse.py:278) - Main window
- [`tk.Label()`](src/DOOMHouse.py:51) - Image display widget
- [`root.bind()`](src/DOOMHouse.py:58) - Keyboard event bindings

## Development Patterns

### Texture Initialization Process
Textures are loaded into ClickHouse tables and dictionaries at startup:
1. Load PNG from disk via PIL.
2. Resize to 512×512 (or configured `TEXTURE_SIZE`).
3. Extract R, G, B channels.
4. Insert into `doomhouse.tex_source` tables.
5. Reload ClickHouse Dictionaries.

### Error Handling
- Connection failure: Print error and exit.
- Missing texture: Fall back to gray noise.
- Query failure: Print error, skip frame.

## Known Issues

### Texture Size Limits
Loading 1024x1024 texture maps currently does not work reliably due to dictionary/memory limits. 512x512 is the recommended maximum.

### No Frame Rate Control
The render loop is event-driven (only on keypress), not continuous. This is intentional for SQL performance, but limits smooth movement.

## Testing

No automated tests exist. Manual testing involves:
1. Launch application
2. Verify initial render displays correctly
3. Test all movement keys
4. Test collision against walls
5. Test texture rendering at various angles
