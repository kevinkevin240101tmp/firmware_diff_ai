import os
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)

# ===== 從環境變數讀取 OpenAI API key =====
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("請先在環境變數設置 OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# 最小 product key 列表
VALID_KEYS = ["ABCD-1234", "XYZ-999"]

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    key = data.get("key")
    diff = data.get("diff")

    if key not in VALID_KEYS:
        return jsonify({"status": "DENY", "message": "Invalid key"}), 403

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

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    analysis_result = response.choices[0].message.content.strip()

    return jsonify({"status": "OK", "result": analysis_result})

if __name__ == "__main__":
    # Render.com 會提供 PORT 環境變數
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
