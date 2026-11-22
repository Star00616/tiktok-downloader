from flask import Flask, request, jsonify, render_template_string
import requests
import re
import json

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
        .main-btn:disabled { opacity: 0.6; }
        .result-card {
            display: none;
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
            display: none;
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
        
        <input type="text" id="videoUrl" placeholder="TikTok video link paste karen...">
        <button class="main-btn" id="getBtn" onclick="fetchVideo()">Get Video</button>

        <div class="error" id="errorBox"></div>

        <div class="result-card" id="resultBox">
            <img id="thumbImg" src="" alt="Thumbnail" class="thumb" style="display:none;">
            <p class="title" id="videoTitle">TikTok Video Ready!</p>
            <a id="sdLink" href="#" target="_blank" class="dl-btn btn-sd">Download Without Watermark</a>
            <a id="hdLink" href="#" target="_blank" class="dl-btn btn-hd" style="display:none;">Download HD Quality</a>
            <a id="mp3Link" href="#" target="_blank" class="dl-btn btn-mp3" style="display:none;">Download MP3 Audio</a>
        </div>
    </div>

    <script>
        async function fetchVideo() {
            const url = document.getElementById('videoUrl').value.trim();
            const btn = document.getElementById('getBtn');
            const errorBox = document.getElementById('errorBox');
            const resultBox = document.getElementById('resultBox');

            errorBox.style.display = 'none';
            resultBox.style.display = 'none';

            if (!url) {
                errorBox.innerText = "Pehle TikTok video ka link paste karen!";
                errorBox.style.display = 'block';
                return;
            }

            btn.innerText = "Loading...";
            btn.disabled = true;

            try {
                const res = await fetch('/api/download', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: url })
                });
                const json = await res.json();

                if (json.status === 'ok') {
                    const thumb = document.getElementById('thumbImg');
                    if (json.cover) {
                        thumb.src = json.cover;
                        thumb.style.display = 'inline-block';
                    } else {
                        thumb.style.display = 'none';
                    }
                    
                    document.getElementById('videoTitle').innerText = json.title || "TikTok Video";
                    document.getElementById('sdLink').href = json.play;
                    
                    const hdBtn = document.getElementById('hdLink');
                    if (json.hdplay) {
                        hdBtn.href = json.hdplay;
                        hdBtn.style.display = 'block';
                    } else {
                        hdBtn.style.display = 'none';
                    }

                    const mp3Btn = document.getElementById('mp3Link');
                    if (json.music) {
                        mp3Btn.href = json.music;
                        mp3Btn.style.display = 'block';
                    } else {
                        mp3Btn.style.display = 'none';
                    }

                    resultBox.style.display = 'block';
                } else {
                    errorBox.innerText = json.error || "Video nahi mili. Link check karen.";
                    errorBox.style.display = 'block';
                }
            } catch (err) {
                errorBox.innerText = "Server error. Dobara koshish karen.";
                errorBox.style.display = 'block';
            } finally {
                btn.innerText = "Get Video";
                btn.disabled = false;
            }
        }
    </script>
</body>
</html>
"""

@app.route('/api/download', methods=['POST'])
def download_api():
    req_data = request.get_json() or {}
    url = req_data.get('url', '').strip()
    if not url:
        return jsonify({'status': 'error', 'error': 'Link khali hai'})

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    }

    # Step 1: Expand short URL (://tiktok.com / ://tiktok.com) to full URL
    try:
        r = requests.get(url, headers=headers, allow_redirects=True, timeout=10)
        full_url = r.url.split('?')[0]
    except Exception:
        full_url = url

    # Method 1: Try TikWM with expanded full URL
    try:
        tikwm = requests.get(
            f"https://tikwm.com{full_url}&hd=1",
            headers=headers,
            timeout=10
        ).json()
        if tikwm.get('code') == 0 and tikwm.get('data'):
            d = tikwm['data']
            return jsonify({
                'status': 'ok',
                'title': d.get('title', 'TikTok Video'),
                'cover': d.get('cover'),
                'play': d.get('play'),
                'hdplay': d.get('hdplay'),
                'music': d.get('music')
            })
    except Exception:
        pass

    # Method 2: Direct TikTok HTML Extraction (No Third-Party API Needed)
    try:
        page = requests.get(full_url, headers=headers, timeout=12).text
        match = re.search(r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">(.*?)</script>', page)
        if match:
            data = json.loads(match.group(1))
            video_detail = data['__DEFAULT_SCOPE__']['webapp.video-detail']['itemInfo']['itemStruct']
            video_url = video_detail['video']['playAddr']
            cover_url = video_detail['video']['cover']
            title = video_detail.get('desc', 'TikTok Video')
            music_url = video_detail.get('music', {}).get('playUrl')
            if video_url:
                return jsonify({
                    'status': 'ok',
                    'title': title,
                    'cover': cover_url,
                    'play': video_url,
                    'music': music_url
                })
    except Exception:
        pass

    return jsonify({'status': 'error', 'error': f'Video nahi mil saki ({full_url[:35]}...). Public video ka link try karen.'})

@app.route('/', methods=['GET'])
@app.route('/<path:path>', methods=['GET'])
def home(path=""):
    return render_template_string(HTML_PAGE)
    
