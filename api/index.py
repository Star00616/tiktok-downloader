from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TikTok Video & MP3 Downloader</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            color: white;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            padding: 30px 20px;
            border-radius: 18px;
            width: 100%;
            max-width: 440px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.4);
        }
        h1 { font-size: 24px; margin-bottom: 8px; color: #ff2a5f; }
        p.subtitle { font-size: 14px; color: #cccccc; margin-bottom: 20px; }
        input {
            width: 100%;
            padding: 14px;
            border: none;
            border-radius: 10px;
            font-size: 15px;
            margin-bottom: 12px;
            outline: none;
        }
        .main-btn {
            width: 100%;
            padding: 14px;
            background: linear-gradient(90deg, #ff0050, #ff2a5f);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
        }
        .result-card {
            margin-top: 25px;
            background: rgba(0, 0, 0, 0.35);
            padding: 15px;
            border-radius: 12px;
        }
        .thumb {
            width: 120px;
            height: 160px;
            object-fit: cover;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        .title {
            font-size: 14px;
            color: #eeeeee;
            margin-bottom: 15px;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        .dl-btn {
            display: block;
            width: 100%;
            padding: 12px;
            margin: 8px 0;
            border-radius: 8px;
            text-decoration: none;
            color: white;
            font-weight: bold;
            font-size: 14px;
        }
        .btn-sd { background: #00b894; }
        .btn-hd { background: #0984e3; }
        .btn-mp3 { background: #6c5ce7; }
        .error {
            background: rgba(255, 71, 87, 0.2);
            color: #ff6b81;
            padding: 10px;
            border-radius: 8px;
            margin-top: 15px;
            font-size: 14px;
            word-wrap: break-word;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>TikTok Downloader</h1>
        <p class="subtitle">HD Video (No Watermark) & MP3 Audio</p>
        <form method="POST">
            <input type="text" name="url" placeholder="TikTok video link paste karen..." required>
            <button type="submit" class="main-btn">Get Video</button>
        </form>

        {% if error %}
            <div class="error">{{ error }}</div>
        {% endif %}

        {% if data %}
            <div class="result-card">
                <img src="{{ data.cover }}" alt="Thumbnail" class="thumb">
                <p class="title">{{ data.title or 'TikTok Video' }}</p>
                
                {% if data.play %}
                    <a href="{{ data.play }}" target="_blank" class="dl-btn btn-sd">Download Without Watermark</a>
                {% endif %}
                
                {% if data.hdplay %}
                    <a href="{{ data.hdplay }}" target="_blank" class="dl-btn btn-hd">Download HD Quality</a>
                {% endif %}
                
                {% if data.music %}
                    <a href="{{ data.music }}" target="_blank" class="dl-btn btn-mp3">Download MP3 Audio</a>
                {% endif %}
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def home(path=""):
    error = None
    data = None
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
        if url:
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/json'
                }
                response = requests.post(
                    "https://tikwm.com",
                    data={'url': url, 'hd': 1},
                    headers=headers,
                    timeout=15
                ).json()
                
                if response.get('code') == 0 and response.get('data'):
                    data = response['data']
                else:
                    error = response.get('msg') or "Video nahi mili. Sahi TikTok link paste karen."
            except Exception as e:
                error = f"Error: {str(e)}"
    return render_template_string(HTML_PAGE, error=error, data=data)
    
