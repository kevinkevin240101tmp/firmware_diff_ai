# server.py (SQLite version for atomic credits & usage)

import os
import sqlite3
from flask import Flask, request, jsonify
from openai import OpenAI
from datetime import datetime
from utils import generate_html
from utils import DEBUG

DAILY_LIMIT = 3
DB_FILE = 'app_data.sqlite'

app = Flask(__name__)

# ===== 從環境變數讀取 OpenAI API key =====
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("請先在環境變數設置 OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# ===== Database init =====
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS keys (key TEXT PRIMARY KEY, uid TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS credits (key TEXT PRIMARY KEY, count INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS usage (key TEXT, date TEXT, count INTEGER, PRIMARY KEY(key, date))''')
    conn.commit()
    conn.close()

init_db()

# ===== Load keys =====
def load_keys():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT key FROM keys')
    keys = [row[0] for row in c.fetchall()]
    conn.close()
    return keys

# ===== Credits system =====
def check_credits_limit(key):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT count FROM credits WHERE key=?', (key,))
    row = c.fetchone()
    conn.close()
    return row is not None and row[0] > 0

def decrement_credits(key):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT count FROM credits WHERE key=?', (key,))
    row = c.fetchone()
    if not row or row[0] <= 0:
        conn.close()
        return False
    new_count = row[0] - 1
    c.execute('UPDATE credits SET count=? WHERE key=?', (new_count, key))
    conn.commit()
    conn.close()
    return True

# ===== Usage system =====
def check_usage_limit(key):
    today = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT count FROM usage WHERE key=? AND date=?', (key, today))
    row = c.fetchone()
    conn.close()
    return row is None or row[0] < DAILY_LIMIT

def increment_usage(key):
    today = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT count FROM usage WHERE key=? AND date=?', (key, today))
    row = c.fetchone()
    if row:
        if row[0] >= DAILY_LIMIT:
            conn.close()
            return False
        new_count = row[0] + 1
        c.execute('UPDATE usage SET count=? WHERE key=? AND date=?', (new_count, key, today))
    else:
        c.execute('INSERT INTO usage(key, date, count) VALUES (?, ?, ?)', (key, today, 1))
    conn.commit()
    conn.close()
    return True

# ===== Analyze route =====
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    key = data.get("key")
    diff = data.get("diff")

    keys = load_keys()
    if key not in keys:
        return jsonify({"status": "DENY", "message": "Invalid key"}), 403

    if not check_credits_limit(key):
        return jsonify({"status": "DENY", "message": "Credits limit reached"}), 403

    if not check_usage_limit(key):
        return jsonify({"status": "DENY", "message": "Daily limit reached"}), 403

    prompt = f"""
你是一位資深 firmware / embedded 工程師。

請分析以下 diff，並用「繁體中文」輸出。

請嚴格使用以下格式（不要多、不要少）：

【主要變更】
- 條列式列出關鍵改動

【可能影響】
- 條列式說明對系統行為的影響

【風險等級】
低 / 中 / 高（只能選一個）

【建議】
- 條列式給出具體可執行建議


Diff:
{''.join(diff[:8000])}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            timeout=60
        )
        analysis_result = response.choices[0].message.content.strip()

        # ===== Atomic operation =====
        if not increment_usage(key):
            return jsonify({"status": "DENY", "message": "Daily limit reached"}), 403
        decrement_credits(key)

        return jsonify({"status": "OK", "result": analysis_result})

    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)}), 500

# ===== Debug routes (optional) =====
@app.route("/usage_check", methods=["GET"])
def usage_check():
    if not DEBUG:
        return "Not allowed", 403
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT key, date, count FROM usage')
    rows = c.fetchall()
    conn.close()
    content = "\n".join([f"{k}|{d}|{c}" for k, d, c in rows])
    return generate_html(content, title="Usage")

@app.route("/credits_check", methods=["GET"])
def credits_check():
    if not DEBUG:
        return "Not allowed", 403
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT key, count FROM credits')
    rows = c.fetchall()
    conn.close()
    content = "\n".join([f"{k}|{c}" for k, c in rows])
    return generate_html(content, title="Credits")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
