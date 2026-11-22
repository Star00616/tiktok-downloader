from flask import Flask, request, redirect, render_template_string
import requests

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TikTok Downloader</title>
    <style>
        body { font-family: sans-serif; text-align: center; background: #121212; color: white; padding: 20px; }
        .box { background: #1e1e1e; padding: 25px; border-radius: 12px; max-width: 400px; margin: 40px auto; }
        input { width: 90%; padding: 12px; margin: 15px 0; border: none; border-radius: 6px; font-size: 16px; }
        button { width: 95%; padding: 12px; background: #fe2c55; color: white; border: none; border-radius: 6px; font-size: 16px; font-weight: bold; }
        .error { color: #ff6b6b; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="box">
        <h2>TikTok Downloader</h2>
        <p>Baghair Watermark Video Download Karen</p>
        <form method="POST">
            <input type="text" name="url" placeholder="TikTok link yahan paste karen..." required>
            <button type="submit">Download Video</button>
        </form>
        {% if error %}
            <p class="error">{{ error }}</p>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    @app.route('/', methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def home(path=""):
    error = None
    if request.method == 'POST':
        url = request.form.get('url')
        if url:
            try:
                api_url = f"https://tikwm.com{url}"
                response = requests.get(api_url).json()
                if response.get('code') == 0:
                    video_url = response['data']['play']
                    return redirect(video_url)
                else:
                    error = "Video nahi mili. Sahi TikTok link paste karen."
            except Exception:
                error = "Server error. Dobara koshish karen."
    return render_template_string(HTML_PAGE, error=error)
  
