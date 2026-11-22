from flask import Flask, request, jsonify, render_template_string
import requests

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
<a id="h" class="btn" style="background:#0984e3">Download HD Video</a>
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
let h=document.getElementById('h');
if(d.hd){h.href=d.hd;h.style.display='block';}else{h.style.display='none';}
let m=document.getElementById('m');
if(d.music){m.href=d.music;m.style.display='block';}else{m.style.display='none';}
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

    # Engine 1: Lovetik API (Works reliably on Vercel & gives direct CDN links)
    try:
        lt = requests.post(
            "https://lovetik.com",
            data={'query': url},
            headers={'User-Agent': 'Mozilla/5.0', 'X-Requested-With': 'XMLHttpRequest'},
            timeout=12
        ).json()
        if lt.get('status') == 'ok' and lt.get('links'):
            links = lt['links']
            sd = next((x['a'] for x in links if 'NO WATERMARK' in x.get('t', '').upper() and 'HD' not in x.get('t', '').upper()), links[0]['a'])
            hd = next((x['a'] for x in links if 'HD' in x.get('t', '').upper()), None)
            mp3 = next((x['a'] for x in links if 'MP3' in x.get('t', '').upper()), None)
            return jsonify({
                'ok': True,
                'title': lt.get('desc', 'TikTok Video'),
                'cover': lt.get('cover'),
                'play': sd,
                'hd': hd,
                'music': mp3
            })
    except Exception:
        pass

    # Engine 2: TikWM API
    try:
        tw = requests.post(
            "https://tikwm.com",
            data={'url': url, 'count': 12, 'cursor': 0, 'web': 1, 'hd': 1},
            headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://tikwm.com'},
            timeout=12
        ).json()
        if tw.get('code') == 0 and tw.get('data'):
            d = tw['data']
            base = "https://tikwm.com"
            play = d.get('play', '')
            hd = d.get('hdplay', '')
            music = d.get('music', '')
            cover = d.get('cover', '')
            return jsonify({
                'ok': True,
                'title': d.get('title', 'TikTok Video'),
                'cover': cover if cover.startswith('http') else base + cover,
                'play': play if play.startswith('http') else base + play,
                'hd': (hd if hd.startswith('http') else base + hd) if hd else None,
                'music': (music if music.startswith('http') else base + music) if music else None
            })
    except Exception:
        pass

    return jsonify({'ok': False, 'err': 'Video nahi mili. Koi doosri public video try karen.'})

@app.route('/', defaults={'p': ''})
@app.route('/<path:p>')
def home(p):
    return render_template_string(HTML)
    
