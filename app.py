import os
import requests
import time
from flask import Flask, render_template_string, request, redirect

app = Flask(__name__)

# --- TES NOUVELLES CLÉS ---
SUPABASE_URL = "https://xwzjlddgqwlrxgetahvp.supabase.co/rest/v1/articles"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh3empsZGRncXdscnhnZXRhaHZwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk3MzY1NTQsImV4cCI6MjA4NTMxMjU1NH0.MsCgDKBz3jXrJ_dOcJ35koaLi-uBpNXoAoaFLAWDbkg"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

ADMIN_PATH = "moncode123"

def time_ago(ts):
    try:
        diff = int(time.time()) - int(ts)
        if diff < 60: return "À l'instant"
        if diff < 3600: return f"Il y a {diff//60} min"
        if diff < 86400: return f"Il y a {diff//3600} h"
        return f"Il y a {diff//86400} j"
    except: return "Récemment"

CSS = """
:root { --blue: #00d2ff; --purple: #9d50bb; --dark: #050505; }
body { font-family: 'Segoe UI', sans-serif; margin: 0; background: var(--dark); color: #eee; }
header { background: #000; padding: 20px; text-align: center; border-bottom: 1px solid #111; position: sticky; top:0; z-index:100; }
.logo { font-size: 1.8rem; font-weight: 900; color: #fff; text-decoration: none; letter-spacing: 2px; }
.logo span { color: var(--blue); }
.nav-cats { display: flex; gap: 15px; overflow-x: auto; padding: 15px; justify-content: center; background: #080808; border-bottom: 1px solid #111; }
.cat { color: #888; text-decoration: none; font-size: 0.9rem; font-weight: bold; white-space: nowrap; }
.cat.active { color: var(--blue); border-bottom: 2px solid var(--blue); }
.container { width: 92%; max-width: 600px; margin: auto; padding: 20px 0; }
.card { background: #111; border-radius: 15px; overflow: hidden; margin-bottom: 25px; border: 1px solid #222; position: relative; }
.card-img { width: 100%; height: 230px; object-fit: cover; background: #1a1a1a; }
.card-body { padding: 18px; text-align: left; }
.card-title { font-size: 20px; font-weight: bold; color: #fff; text-decoration: none; margin-bottom: 8px; display: block; }
.time { position: absolute; top: 15px; right: 15px; background: rgba(0,0,0,0.6); padding: 4px 10px; border-radius: 8px; font-size: 11px; color: var(--blue); }
.btn { display: block; background: linear-gradient(135deg, var(--blue), var(--purple)); color: #fff; padding: 12px; text-align: center; border-radius: 10px; text-decoration: none; font-weight: bold; margin-top: 15px; border:none; width:100%; }
input, textarea, select { width: 100%; padding: 12px; margin: 8px 0; background: #000; border: 1px solid #333; color: #fff; border-radius: 8px; box-sizing: border-box; }
"""

@app.route('/')
def home():
    cat_filter = request.args.get('cat', 'Tous')
    params = {"order": "ts.desc"}
    if cat_filter != 'Tous':
        params["categorie"] = f"eq.{cat_filter}"
    
    try:
        # On demande les données à Supabase
        r = requests.get(SUPABASE_URL, headers=HEADERS, params=params)
        articles = r.json() if r.status_code == 200 else []
    except:
        articles = []

    categories = ["Tous", "Science", "Tech", "Espace", "IA"]
    nav_html = "".join([f'<a href="/?cat={c}" class="cat {"active" if c==cat_filter else ""}">{c}</a>' for c in categories])
    
    cards = ""
    if isinstance(articles, list):
        for a in articles:
            cards += f'''
            <div class="card">
                <img src="{a.get('img_url', '')}" class="card-img" onerror="this.src='https://placehold.co/600x400?text=Image+Indisponible'">
                <div class="time">{time_ago(a.get('ts', 0))}</div>
                <div class="card-body">
                    <span style="color:var(--blue); font-size:12px; font-weight:bold;">{a.get('categorie', 'Tous').upper()}</span>
                    <a href="#" class="card-title">{a.get('titre', 'Sans titre')}</a>
                    <p style="color:#aaa; font-size:14px; line-height:1.5;">{a.get('resume', '')}...</p>
                    <a href="#" class="btn">LIRE L'ARTICLE</a>
                </div>
            </div>
            '''

    return render_template_string(f"""
    <html><head><title>METTABYTE</title><meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="google-site-verification" content="dDTFaN2k3Nh2HOiJF_R7J-8PaUw0LZ6enE0yTGFKrSA" />
    <style>{CSS}</style></head><body>
        <header><a href="/" class="logo">METTA<span>BYTE</span></a></header>
        <nav class="nav-cats">{nav_html}</nav>
        <div class="container">
            {cards if cards else "<p style='text-align:center;color:#666;padding:50px;'>Aucun article trouvé. Allez sur /moncode123/ pour publier.</p>"}
        </div>
    </body></html>""")

@app.route(f'/{ADMIN_PATH}/', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        data = {
            "titre": request.form['titre'],
            "resume": request.form['texte'][:120],
            "texte": request.form['texte'],
            "img_url": request.form['img_url'],
            "categorie": request.form['categorie'],
            "ts": int(time.time())
        }
        requests.post(SUPABASE_URL, headers=HEADERS, json=data)
        return redirect('/')
    
    return render_template_string(f"""
    <html><head><style>{CSS}</style></head><body>
        <header><span class="logo">PUBLIER</span></header>
        <div class="container">
            <form method="post">
                <input name="titre" placeholder="Titre de l'article" required>
                <select name="categorie">
                    <option value="Science">Science</option>
                    <option value="Tech">Tech</option>
                    <option value="Espace">Espace</option>
                    <option value="IA">IA</option>
                </select>
                <input name="img_url" placeholder="URL de l'image" required>
                <textarea name="texte" rows="8" placeholder="Contenu de l'article" required></textarea>
                <button type="submit" class="btn">METTRE EN LIGNE</button>
            </form>
        </div>
    </body></html>""")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
