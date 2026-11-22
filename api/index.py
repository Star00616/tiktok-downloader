from flask import Flask, request, jsonify, render_template_string
import yt_dlp

app = Flask(__name__)

HTML = """<!DOCTYPE html>
<html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>TikTok Downloader</title>
<style>
body{font-family:sans-serif;background:#121224;color:#fff;display:flex;justify-content:center;padding:20px}
.box{background:#1e1e36;padding:25px;border-radius:16px;width:100%;max-width:420px;text-align:center}
h2{color:#ff2a5f;margin:0 0 8px}p{color:#ccc;font-size:14px;margin:0 0 18px}
input{width:92%;padding:13px;border:none;border-radius:8px;font-size:15px;margin-bottom:12px}
button{width:98%;padding:13px;background:#ff2a5f;color:#fff;border:none;border-radius:8px;font-size:16px;font-weight:bold}
.res{display:none;margin-top:20px;background:#141426;padding:15px;border-radius:12px}
img{width:110px;height:150px;object-fit:cover;border-radius:8px}
.btn{display:block;padding:12px;margin:8px 0;border-radius:8px;text-decoration:none;color:#fff;font-weight:bold;font-size:14px}
.err{display:none;color:#ff6b81;margin-top:15px;font-size:14px}
</style></head><body><div class="box">
<h2>TikTok Downloader</h2><p>HD Video (No Watermark) & MP3</p>
<input id="u" placeholder="TikTok link paste karen...">
<button id="b" onclick="go()">Get Video</button>
<div class="err" id="e"></div>
<div class="res" id="r"><img id="im"><p id="t"></p>
<a id="v" target="_blank" class="btn" style="background:#00b894">Download Video (No Watermark)</a>
</div></div><script>
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
document.getElementById('v').href=d.play;
r.style.display='block';
}else{e.innerText=d.err;e.style.display='block';}
}catch(x){e.innerText='Error! Dobara try karen.';e.style.display='block';}
b.innerText='Get Video';b.disabled=false;}
</script></body></html>"""

@app.route('/api/dl', methods=['POST'])
def dl():
    url = (request.get_json() or {}).get('url', '').strip()
    if not url:
        return jsonify({'ok': False, 'err': 'Link khali hai'})
    try:
        opts = {'quiet': True, 'no_warnings': True, 'format': 'best[ext=mp4]/best'}
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = [f for f in info.get('formats', []) if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and 'watermark' not in f.get('format_id', '').lower()]
            video_url = formats[-1]['url'] if formats else info.get('url')
            return jsonify({
                'ok': True,
                'title': info.get('title', 'TikTok Video'),
                'cover': info.get('thumbnail'),
                'play': video_url
            })
    except Exception as ex:
        return jsonify({'ok': False, 'err': f'Error: {str(ex)[:60]}'})

@app.route('/', defaults={'p': ''})
@app.route('/<path:p>')
def home(p):
    return render_template_string(HTML)
    
