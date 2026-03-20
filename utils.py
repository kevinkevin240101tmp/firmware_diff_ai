# DEBUG = True / False
DEBUG = True

def generate_html(content, title="Report"):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
    body {{
        background-color: #343541;
        color: #ECECF1;
        font-family: monospace;
    }}
    pre {{
        background-color: #444654;
        color: #F5F5F5;
        padding: 10px;
        border-radius: 6px;
        overflow-x: auto;
    }}
</style>
</head>
<body>
<h2>{title}</h2>
<pre>{content}</pre>
</body>
</html>"""
