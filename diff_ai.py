import sys
import difflib
import requests
import argparse
from utils import generate_html

# ===== 建議：產品化，直接透過 server 呼叫 OpenAI API =====
#SERVER_URL = "http://127.0.0.1:5000/analyze"
SERVER_URL = "https://firmware-diff-ai.onrender.com/analyze"

def read_file(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.readlines()

def get_diff(old_lines, new_lines):
    diff = difflib.unified_diff(
        old_lines,
        new_lines,
        lineterm=""
    )
    return "\n".join(diff)

def analyze_diff_server(diff_text, key):
    payload = {"key": key, "diff": diff_text.splitlines()}
    try:
        response = requests.post(SERVER_URL, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get("status") == "OK":
            return data.get("result", "[Error] No result returned")
        else:
            return f"Access denied: {data.get('message', '')}"
    except Exception as e:
        return f"Error connecting to server: {e}"

def main():
    parser = argparse.ArgumentParser(description="Diff AI CLI with Server")
    parser.add_argument("old_file")
    parser.add_argument("new_file")
    parser.add_argument("--key", required=True, help="Product key")
    args = parser.parse_args()

    old_lines = read_file(args.old_file)
    new_lines = read_file(args.new_file)

    print("=== DIFF ===")
    diff_text = get_diff(old_lines, new_lines)
    print(diff_text[:2000])  # 避免太長

    print("\n=== AI ANALYSIS ===")
    result = analyze_diff_server(diff_text, args.key)
    print(result)

    html_content = generate_html(
        f"=== DIFF ===\n{diff_text}\n\n=== AI 分析 ===\n{result}",
        title="Diff Report"
    )

    with open("report.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    print("\n[OK] report.html 已產生")

if __name__ == "__main__":
    main()
