import os
from flask import Flask, request, jsonify
from openai import OpenAI
from datetime import datetime
from utils import generate_html
from utils import DEBUG

DAILY_LIMIT = 3

app = Flask(__name__)

# ===== 從環境變數讀取 OpenAI API key =====
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("請先在環境變數設置 OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# 最小 product key 列表
def load_keys():
    keys = {}
    try:
        with open("db.txt") as f:
            for line in f:
                if ":" in line:
                    uid, pwd = line.strip().split(":", 1)
                    keys[pwd] = uid
    except:
        pass
    return keys

def check_usage_limit(key):
    today = datetime.now().strftime("%Y-%m-%d")
    usage = {}

    try:
        with open("usage.txt") as f:
            for line in f:
                k, d, count = line.strip().split("|")
                usage[(k, d)] = int(count)
    except:
        pass

    current = usage.get((key, today), 0)

    if current >= DAILY_LIMIT:
        return False

    return True

def increment_usage(key):
    today = datetime.now().strftime("%Y-%m-%d")
    usage = {}

    try:
        with open("usage.txt") as f:
            for line in f:
                k, d, count = line.strip().split("|")
                usage[(k, d)] = int(count)
    except:
        pass

    current = usage.get((key, today), 0)

    if current >= DAILY_LIMIT:
        return False

    usage[(key, today)] = current + 1

    try:
        with open("usage.txt", "w") as f:
            for (k, d), c in usage.items():
                f.write(f"{k}|{d}|{c}\n")
    except:
        pass

    return True

@app.route("/analyze", methods=["POST"])
def analyze():
    raise Exception("test error") # RXX for test, remove it after test!!!
    data = request.json
    key = data.get("key")
    diff = data.get("diff")

    keys = load_keys()
    if key not in keys:
        return jsonify({"status": "DENY", "message": "Invalid key"}), 403

    if not check_usage_limit(key):
        return jsonify({"status": "DENY", "message": "Daily limit reached"}), 403

    # 呼叫 OpenAI API 進行分析
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

        increment_usage(key)   # ✅ 成功後才扣

        return jsonify({"status": "OK", "result": analysis_result})

    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)}), 500

# ===== 新增測試 usage.txt 的 route（安全用，正式可移除） =====
@app.route("/usage_check", methods=["GET"])
def usage_check():
    if not DEBUG:
        return "Not allowed", 403

    try:
        with open("usage.txt") as f:
            content = f.read()
    except FileNotFoundError:
        content = "usage.txt not found"

    return generate_html(content, title="Usage")

@app.route("/reset_usage", methods=["POST"])
def reset_usage():
    if not DEBUG:
        return "Not allowed", 403

    with open("usage.txt", "w") as f:
        f.write("")
    return "usage reset OK"

if __name__ == "__main__":
    # Render.com 會提供 PORT 環境變數
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
