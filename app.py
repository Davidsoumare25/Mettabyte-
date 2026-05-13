import os
import requests
import time
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

# --- CONFIGURATION ---
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

# --- DESIGN AMÉLIORÉ ---
CSS = """
:root { --blue: #00d2ff; --purple: #9d50bb; --dark: #050505; }
body { font-family: 'Segoe UI', sans-serif; margin: 0; background: var(--dark); color: #eee; line-height: 1.6; }
header { background: #000; padding: 20px; text-align: center; border-bottom: 1px solid #111; position: sticky; top:0; z-index:100; }
.logo { font-size: 1.8rem; font-weight: 900; color: #fff; text-decoration: none; letter-spacing: 2px; }
.logo span { color: var(--blue); }
.nav-cats { display: flex; gap: 15px; overflow-x: auto; padding: 15px; justify-content: center; background: #080808; border-bottom: 1px solid #111; }
.cat { color: #888; text-decoration: none; font-size: 0.9rem; font-weight: bold; padding: 5px 10px; }
.cat.active { color: var(--blue); border-bottom: 2px solid var(--blue); }
.container { width: 92%; max-width: 700px; margin: auto; padding: 20px 0; }
.card { background: #111; border-radius: 15px; overflow: hidden; margin-bottom: 30px; border: 1px solid #222; position: relative; }
.card-img { width: 100%; height: 250px; object-fit: cover; }
.card-body { padding: 20px; }
.card-title { font-size: 22px; font-weight: bold; color: #fff; text-decoration: none; margin-bottom: 10px; display: block; }
.time { position: absolute; top: 15px; right: 15px; background: rgba(0,0,0,0.7); padding: 5px 12px; border-radius: 8px; font-size: 11px; color: var(--blue); font-weight: bold; }
.btn { display: block; background: linear-gradient(135deg, var(--blue), var(--purple)); color: #fff; padding: 14px; text-align: center; border-radius: 12px; text-decoration: none; font-weight: bold; margin-top: 15px; border:none; }
.full-text { font-size: 18px; color: #ccc; white-space: pre-wrap; margin-top: 20px; }
input, textarea, select { width: 100%; padding: 12px; margin: 8px 0; background: #000; border: 1px solid #333; color: #fff; border-radius: 8px; box-sizing: border-box; }
"""

# --- ACCUEIL (Avec résumés uniquement) ---
@app.route('/')
def home():
    cat_filter = request.args.get('cat', 'Tous')
    params = {"order": "ts.desc"}
    if cat_filter != 'Tous': params["categorie"] = f"eq.{cat_filter}"
    
    try:
        r = requests.get(SUPABASE_URL, headers=HEADERS, params=params)
        articles = r.json()
    except: articles = []

    categories = ["Tous", "Science", "Tech", "Espace", "IA"]
    nav_html = "".join([f'<a href="/?cat={c}" class="cat {"active" if c==cat_filter else ""}">{c}</a>' for c in categories])
    
    cards = ""
    if isinstance(articles, list):
        for a in articles:
            # On n'affiche que le début du texte (le résumé)
            cards += f'''
            <div class="card">
                <img src="{a.get('img_url', '')}" class="card-img" onerror="this.src='https://placehold.co/600x400?text=Image+Indisponible'">
                <div class="time">{time_ago(a.get('ts', 0))}</div>
                <div class="card-body">
                    <span style="color:var(--blue); font-size:12px; font-weight:bold;">{a.get('categorie', 'Tous').upper()}</span>
                    <div class="card-title">{a.get('titre', 'Sans titre')}</div>
                    <p style="color:#aaa; font-size:15px;">{a.get('resume', '')}...</p>
                    <a href="/article/{a.get('id')}" class="btn">LIRE LA SUITE</a>
                </div>
            </div>
            '''

    return render_template_string(f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1"><style>{CSS}</style></head><body>
        <header><a href="/" class="logo">METTA<span>BYTE</span></a></header>
        <nav class="nav-cats">{nav_html}</nav>
        <div class="container">{cards if cards else "<p style='text-align:center;color:#666;'>Aucun article trouvé.</p>"}</div>
    </body></html>""")

# --- PAGE DE LECTURE (Texte complet) ---
@app.route('/article/<id>')
def read_article(id):
    try:
        r = requests.get(f"{SUPABASE_URL}?id=eq.{id}", headers=HEADERS)
        art = r.json()[0]
    except: return redirect('/')

    return render_template_string(f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1"><style>{CSS}</style></head><body>
        <header><a href="/" class="logo">METTA<span>BYTE</span></a></header>
        <div class="container">
            <img src="{art.get('img_url')}" style="width:100%; border-radius:20px; margin-bottom:20px;">
            <span style="color:var(--blue); font-weight:bold;">{art.get('categorie', 'TOUS').upper()} • {time_ago(art.get('ts'))}</span>
            <h1 style="font-size:32px; margin:10px 0;">{art.get('titre')}</h1>
            <div class="full-text">{art.get('texte')}</div>
            <br><br>
            <a href="/" class="btn" style="background:#222; border:1px solid #444;">RETOUR À L'ACCUEIL</a>
        </div>
    </body></html>""")

# --- PAGE ADMIN ---
@app.route(f'/{ADMIN_PATH}/', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        data = {
            "titre": request.form['titre'],
            "resume": request.form['texte'][:130], # Le site prend les 130 premiers caractères pour l'accueil
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
                    <option value="Science">Science</option><option value="Tech">Tech</option>
                    <option value="Espace">Espace</option><option value="IA">IA</option>
                </select>
                <input name="img_url" placeholder="URL de l'image" required>
                <textarea name="texte" rows="12" placeholder="Écrivez l'article complet ici..." required></textarea>
                <button type="submit" class="btn">METTRE EN LIGNE</button>
            </form>
        </div>
    </body></html>""")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

