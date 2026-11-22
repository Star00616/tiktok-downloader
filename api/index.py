from flask import Flask, request, jsonify, render_template_string, Response
import requests, re, json, base64

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
<a id="v" class="btn" style="background:#00b894">Download Video (No Watermark)</a>
<a id="m" class="btn" style="background:#6c5ce7">Download MP3 Audio</a>
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
let m=document.getElementById('m');
if(d.music){m.href=d.music;m.style.display='block';}else{m.style.display='none';}
r.style.display='block';
}else{e.innerText=d.err;e.style.display='block';}
}catch(x){e.innerText='Error! Dobara try karen.';e.style.display='block';}
b.innerText='Get Video';b.disabled=false;}
</script></body></html>"""

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36'

def enc(s):
    return base64.urlsafe_b64encode(s.encode()).decode()

def dec(s):
    return base64.urlsafe_b64decode(s.encode()).decode()

@app.route('/api/dl', methods=['POST'])
def dl():
    url = (request.get_json() or {}).get('url', '').strip()
    s = requests.Session()
    s.headers.update({'User-Agent': UA, 'Referer': 'https://tiktok.com'})
    try:
        full = s.get(url, allow_redirects=True, timeout=10).url.split('?')
    except Exception:
        full = url
    try:
        tw = requests.post("https://tikwm.com", data={'url': full, 'hd': 1}, headers={'User-Agent': UA}, timeout=10).json()
        if tw.get('code') == 0 and tw.get('data'):
            d = tw['data']
            v = d.get('hdplay') or d.get('play')
            return jsonify({'ok': True, 'title': d.get('title'), 'cover': d.get('cover'), 'play': v, 'music': d.get('music')})
    except Exception:
        pass
    try:
        pg = s.get(full, timeout=12).text
        m = re.search(r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">(.*?)</script>', pg)
        if m:
            item = json.loads(m.group(1))['__DEFAULT_SCOPE__']['webapp.video-detail']['itemInfo']['itemStruct']
            v = item['video'].get('downloadAddr') or item['video'].get('playAddr')
            mu = item.get('music', {}).get('playUrl')
            ck = "; ".join([f"{k}={v}" for k, v in s.cookies.get_dict().items()])
            if v:
                return jsonify({
                    'ok': True, 'title': item.get('desc'), 'cover': item['video']['cover'],
                    'play': f"/api/st?u={enc(v)}&c={enc(ck)}&t=v",
                    'music': f"/api/st?u={enc(mu)}&c={enc(ck)}&t=a" if mu else None
                })
    except Exception:
        pass
    return jsonify({'ok': False, 'err': 'Video nahi mili. Public link try karen.'})

@app.route('/api/st')
def st():
    u, c, t = dec(request.args.get('u', '')), dec(request.args.get('c', '')), request.args.get('t', 'v')
    r = requests.get(u, headers={'User-Agent': UA, 'Referer': 'https://tiktok.com', 'Cookie': c}, stream=True, timeout=20)
    if r.status_code != 200:
        return "Video server ne block kiya, dobara Get Video dabayen.", 400
    fn, ct = ("audio.mp3", "audio/mpeg") if t == 'a' else ("video.mp4", "video/mp4")
    return Response(r.iter_content(65536), content_type=ct, headers={"Content-Disposition": f'attachment; filename="{fn}"'})

@app.route('/', defaults={'p': ''})
@app.route('/<path:p>')
def home(p):
    return render_template_string(HTML)
    
