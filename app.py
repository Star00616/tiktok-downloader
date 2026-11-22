from flask import Flask, render_template, request, redirect
import requests

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
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
    return render_template('index.html', error=error)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
  
