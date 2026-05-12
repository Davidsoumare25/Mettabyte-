import os
import requests
import time
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

# --- CONFIGURATION SUPABASE ---
SUPABASE_URL = "https://xwzjlddgqwlrxgetahvp.supabase.co/rest/v1/articles"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh3empsZGRncXdscnhnZXRhaHZwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk3MzY1NTQsImV4cCI6MjA4NTMxMjU1NH0.MsCgDKBz3jXrJ_dOcJ35koaLi-uBpNXoAoaFLAWDbkg"
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

ADMIN_PATH = "moncode123"

# --- FONCTION TEMPS ---
def time_ago(ts):
    diff = int(time.time()) - ts
    if diff < 60: return "À l'instant"
    if diff < 3600: return f"Il y a {diff//60} min"
    if diff < 86400: return f"Il y a {diff//3600} h"
    return f"Il y a {diff//86400} jours"

# --- DESIGN COMPLET METTABYTE ---
CSS = """
:root { --blue: #00d2ff; --purple: #9d50bb; --dark: #050505; }
body { font-family: 'Segoe UI', sans-serif; margin: 0; background: var(--dark); color: #eee; }
header { background: #000; padding: 25px 10px; text-align: center; border-bottom: 1px solid #111; position: sticky; top:0; z-index:100; }
.logo-text { font-size: 2.2rem; font-weight: 900; color: #fff; text-decoration: none; letter-spacing: 3px; text-transform: uppercase; text-shadow: 0 0 15px var(--blue); }
.byte-part { color: var(--blue); }
.container { width: 92%; max-width: 600px; margin: auto; padding: 20px 0; }
.card { background: #111; border-radius: 20px; overflow: hidden; margin-bottom: 30px; border: 1px solid #222; position: relative; transition: 0.3s; }
.card:hover { border-color: var(--blue); transform: translateY(-5px); }
.card-img { width: 100%; height: 250px; object-fit: cover; display: block; background: #1a1a1a; }
.card-body { padding: 20px; }
.card-title { font-size: 22px; font-weight: bold; color: #fff; text-decoration: none; display: block; margin-bottom: 10px; }
.btn { display: inline-block; background: linear-gradient(135deg, var(--blue), var(--purple)); color: white; padding: 12px 25px; border-radius: 12px; text-decoration: none; font-weight: bold; width: 100%; text-align: center; box-sizing: border-box; border:none; cursor: pointer; }
.time-badge { position: absolute; bottom: 85px; right: 20px; font-size: 11px; color: var(--blue); font-weight: bold; background: rgba(0,0,0,0.7); padding: 5px 10px; border-radius: 10px; }
input, textarea { width: 100%; padding: 15px; margin: 10px 0; border: 1px solid #333; border-radius: 12px; background: #000; color: white; box-sizing: border-box; }
"""

# --- ROUTES ---
@app.route('/')
def home():
    try:
        r = requests.get(SUPABASE_URL, headers=HEADERS, params={"order": "ts.desc"})
        articles = r.json() if r.status_code == 200 else []
    except:
        articles = []
    
    html_cards = ""
    for art in articles:
        html_cards += f'''
        <div class="card">
            <img src="{art.get('img_url')}" class="card-img" onerror="this.src='https://placehold.co/600x400?text=METTABYTE'">
            <div class="time-badge">{time_ago(art.get('ts', int(time.time())))}</div>
            <div class="card-body">
                <a href="#" class="card-title">{art.get('titre')}</a>
                <p style="color:#888; margin-bottom:20px;">{art.get('resume')}...</p>
                <a href="#" class="btn">DÉCOUVRIR</a>
            </div>
        </div>
        '''
    
    return render_template_string(f"""
    <html><head><title>METTABYTE</title><meta name='viewport' content='width=device-width, initial-scale=1'>
    <meta name="google-site-verification" content="dDTFaN2k3Nh2HOiJF_R7J-8PaUw0LZ6enE0yTGFKrSA" />
    <style>{CSS}</style></head>
    <body>
        <header><a href="/" class="logo-text">METTA<span class="byte-part">BYTE</span></a></header>
        <div class="container">{html_cards if html_cards else "<p style='text-align:center;'>Aucun article pour le moment.</p>"}</div>
    </body></html>""")

@app.route(f'/{ADMIN_PATH}/', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        data = {
            "titre": request.form['titre'],
            "resume": request.form['texte'][:120],
            "texte": request.form['texte'],
            "img_url": request.form['img_url'],
            "ts": int(time.time())
        }
        requests.post(SUPABASE_URL, headers=HEADERS, json=data)
        return redirect('/')
    
    return render_template_string(f"""
    <html><head><style>{CSS}</style></head><body>
        <header><span class="logo-text">RÉDACTION</span></header>
        <div class="container">
            <form method="post">
                <input name="titre" placeholder="Titre de l'article" required>
                <input name="img_url" placeholder="Lien de l'image (URL)" required>
                <textarea name="texte" rows="10" placeholder="Écrivez votre article ici..." required></textarea>
                <button type="submit" class="btn">PUBLIER SUR LE SITE</button>
            </form>
        </div>
    </body></html>""")

@app.route('/googleaa97466e31055bc3.html')
def google():
    return "google-site-verification: googleaa97466e31055bc3.html"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
