from flask import Flask, request, jsonify, render_template_string, Response
import yt_dlp, base64

app = Flask(__name__)

HTML = """<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="google-site-verification" content="UMewe7bBLjcW2zzrgzxKgO-3Uf5-mOcNc7-MeRg6lmA" />
<title>TikTok Video Downloader Without Watermark - HD 1080p & MP3</title>
<meta name="description" content="Download TikTok videos without watermark in HD 1080p quality and convert TikTok to MP3 audio online for free. Fast, free, and no app required.">
<meta name="keywords" content="tiktok downloader, tiktok video downloader without watermark, download tiktok hd, tiktok to mp3, save tiktok video">
<meta name="robots" content="index, follow">
<meta property="og:title" content="TikTok Downloader - No Watermark HD & MP3">
<meta property="og:description" content="Free online tool to download TikTok videos without watermark in HD quality and MP3 audio.">
<meta property="og:type" content="website">
<style>
body{font-family:sans-serif;background:#121224;color:#fff;display:flex;flex-direction:column;align-items:center;padding:20px;margin:0}
.box{background:#1e1e36;padding:25px;border-radius:16px;width:100%;max-width:420px;text-align:center;margin-top:20px;box-shadow:0 8px 25px rgba(0,0,0,0.4)}
h1{color:#ff2a5f;font-size:24px;margin:0 0 8px}p{color:#ccc;font-size:14px;margin:0 0 18px}
input{width:92%;padding:13px;border:none;border-radius:8px;font-size:15px;margin-bottom:12px;outline:none}
button{width:98%;padding:13px;background:#ff2a5f;color:#fff;border:none;border-radius:8px;font-size:16px;font-weight:bold;cursor:pointer}
.res{display:none;margin-top:20px;background:#141426;padding:15px;border-radius:12px}
img{width:110px;height:150px;object-fit:cover;border-radius:8px}
.btn{display:block;padding:12px;margin:8px 0;border-radius:8px;text-decoration:none;color:#fff;font-weight:bold;font-size:14px}
.err{display:none;color:#ff6b81;margin-top:15px;font-size:14px}
.info{max-width:420px;margin-top:20px;color:#aaa;font-size:13px;line-height:1.6;text-align:left;background:#1a1a2e;padding:18px;border-radius:12px}
.info h2{color:#fff;font-size:16px;margin:0 0 8px}
</style></head><body>
<div class="box">
<h1>TikTok Downloader</h1><p>HD Video (No Watermark) & MP3</p>
<input id="u" placeholder="TikTok link paste karen...">
<button id="b" onclick="go()">Get Video</button>
<div class="err" id="e"></div>
<div class="res" id="r"><img id="im"><p id="t"></p>
<a id="v" class="btn" style="background:#00b894">Download Normal (No Watermark)</a>
<a id="h" class="btn" style="background:#0984e3">Download HD Quality (1080p)</a>
<a id="m" class="btn" style="background:#6c5ce7">Download MP3 Audio</a>
</div></div>
<div class="info">
<h2>How to Download TikTok Videos Without Watermark?</h2>
<p>1. Open TikTok and copy the video link.<br>2. Paste the link in the box above and tap Get Video.<br>3. Choose Normal MP4, HD 1080p, or MP3 Audio to save directly to your phone.</p>
</div>
<script>
async function go(){
let u=document.getElementById('u').value.trim(),b=document.getElementById('b'),e=document.getElementById('e'),r=document.getElementById('r');
e.style.display='none';r.style.display='none';
if(!u){e.innerText='Link paste karen!';e.style.display='block';return;}
b.innerText='Loading...';b.disabled=true;
try{
let res=await fetch('/api/dl',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url:u})});
let d=await res.json();
if(d.ok){
document.getElementById('im').src=d.cover||'';
document.getElementById('t').innerText=d.title||'TikTok Video';
document.getElementById('v').href='/api/file?t=v&u='+d.enc;
document.getElementById('h').href='/api/file?t=hd&u='+d.enc;
document.getElementById('m').href='/api/file?t=a&u='+d.enc;
r.style.display='block';
}else{e.innerText=d.err;e.style.display='block';}
}catch(x){e.innerText='Error! Dobara try karen.';e.style.display='block';}
b.innerText='Get Video';b.disabled=false;}
</script>
<script async data-cfasync="false" src="https://bicea.org"></script>
</body></html>"""

@app.route('/api/dl', methods=['POST'])
def dl():
    url = (request.get_json() or {}).get('url', '').strip()
    if not url:
        return jsonify({'ok': False, 'err': 'Link khali hai'})
    try:
        opts = {'quiet': True, 'no_warnings': True}
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            enc_url = base64.urlsafe_b64encode(url.encode()).decode()
            return jsonify({
                'ok': True,
                'title': info.get('title', 'TikTok Video'),
                'cover': info.get('thumbnail'),
                'enc': enc_url
            })
    except Exception as ex:
        return jsonify({'ok': False, 'err': f'Error: {str(ex)[:60]}'})

@app.route('/api/file')
def get_file():
    t = request.args.get('t', 'v')
    url = base64.urlsafe_b64decode(request.args.get('u', '').encode()).decode()
    fmt = 'bestaudio/best' if t == 'a' else 'best[ext=mp4]/best'
    opts = {'quiet': True, 'no_warnings': True, 'format': fmt}
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if t == 'a':
            target = info
            fn, ct = "tiktok_audio.mp3", "audio/mpeg"
        else:
            vids = [f for f in info.get('formats', []) if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and 'watermark' not in f.get('format_id', '').lower() and f.get('ext') == 'mp4']
            vids.sort(key=lambda x: (x.get('height') or 0, x.get('tbr') or 0))
            best_vid = vids[-1] if vids else info
            if t == 'hd':
                target = best_vid
                fn = "tiktok_HD.mp4"
            else:
                target = vids[-2] if len(vids) > 1 else best_vid
                fn = "tiktok_normal.mp4"
            ct = "video/mp4"
        try:
            stream = ydl.urlopen(target.get('url'))
        except Exception:
            stream = ydl.urlopen(best_vid.get('url'))
        def generate():
            while True:
                chunk = stream.read(65536)
                if not chunk:
                    break
                yield chunk
        return Response(generate(), content_type=ct, headers={"Content-Disposition": f'attachment; filename="{fn}"'})

@app.route('/', defaults={'p': ''})
@app.route('/<path:p>')
def home(p):
    return render_template_string(HTML)
  
