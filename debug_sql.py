import clickhouse_connect
import os
import re
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv('CLICKHOUSE_HOST', 'localhost')
PORT = int(os.getenv('CLICKHOUSE_PORT', '8123'))
USER = os.getenv('CLICKHOUSE_USER', 'default')
PASS = os.getenv('CLICKHOUSE_PASS', '')

def remove_comments(sql):
    # Remove block comments /* ... */
    sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
    # Remove line comments -- ...
    lines = sql.split('\n')
    clean_lines = []
    for line in lines:
        if '--' in line:
            line = line.split('--')[0]
        if line.strip():
            clean_lines.append(line)
    return '\n'.join(clean_lines)

def execute_sql_script(client, script_path):
    if not os.path.exists(script_path):
        print(f"Script not found: {script_path}")
        return

    with open(script_path, 'r') as f:
        content = f.read()

    # Remove comments first
    content = remove_comments(content)

    statements = content.split(';')
    for stmt in statements:
        stmt = stmt.strip()
        if not stmt:
            continue
            
        print(f"Executing statement from {script_path}...")
        try:
            client.command(stmt)
            print("Success!")
        except Exception as e:
            print(f"Error: {e}")

try:
    client = clickhouse_connect.get_client(host=HOST, port=PORT, username=USER, password=PASS)
    print("Connected to ClickHouse")
    
    execute_sql_script(client, "src/SQL/render_view.sql")

except Exception as e:
    print(f"Connection Error: {e}")
