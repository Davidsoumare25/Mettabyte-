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

# --- DESIGN ---
CSS = """
:root { --blue: #00d2ff; --purple: #9d50bb; --dark: #050505; --red: #ff4b2b; }
body { font-family: 'Segoe UI', sans-serif; margin: 0; background: var(--dark); color: #eee; line-height: 1.6; }
header { background: #000; padding: 20px; text-align: center; border-bottom: 1px solid #111; position: sticky; top:0; z-index:100; }
.logo { font-size: 1.8rem; font-weight: 900; color: #fff; text-decoration: none; letter-spacing: 2px; }
.logo span { color: var(--blue); }
.nav-cats { display: flex; gap: 15px; overflow-x: auto; padding: 15px; justify-content: center; background: #080808; border-bottom: 1px solid #111; }
.cat { color: #888; text-decoration: none; font-size: 0.9rem; font-weight: bold; padding: 5px 10px; }
.cat.active { color: var(--blue); border-bottom: 2px solid var(--blue); }
.container { width: 92%; max-width: 700px; margin: auto; padding: 20px 0; }
.card { background: #111; border-radius: 15px; overflow: hidden; margin-bottom: 30px; border: 1px solid #222; position: relative; }
.card-img { width: 100%; height: 230px; object-fit: cover; }
.card-body { padding: 20px; }
.card-title { font-size: 22px; font-weight: bold; color: #fff; text-decoration: none; margin-bottom: 10px; display: block; }
.btn { display: block; background: linear-gradient(135deg, var(--blue), var(--purple)); color: #fff; padding: 14px; text-align: center; border-radius: 12px; text-decoration: none; font-weight: bold; margin-top: 10px; border:none; cursor:pointer; width:100%; box-sizing:border-box; }
.btn-red { background: var(--red); margin-top: 5px; font-size: 12px; padding: 8px; }
.btn-edit { background: #333; margin-top: 5px; font-size: 12px; padding: 8px; border: 1px solid #444; }
input, textarea, select { width: 100%; padding: 12px; margin: 8px 0; background: #000; border: 1px solid #333; color: #fff; border-radius: 8px; box-sizing: border-box; }
"""

# --- ACCUEIL ---
@app.route('/')
def home():
    cat_filter = request.args.get('cat', 'Tous')
    params = {"order": "ts.desc"}
    if cat_filter != 'Tous': params["categorie"] = f"eq.{cat_filter}"
    try:
        r = requests.get(SUPABASE_URL, headers=HEADERS, params=params)
        articles = r.json()
    except: articles = []
    
    nav_html = "".join([f'<a href="/?cat={c}" class="cat {"active" if c==cat_filter else ""}">{c}</a>' for c in ["Tous", "Science", "Tech", "Espace", "IA"]])
    
    cards = ""
    for a in articles:
        cards += f'''
        <div class="card">
            <img src="{a.get('img_url')}" class="card-img">
            <div class="card-body">
                <span style="color:var(--blue); font-size:12px; font-weight:bold;">{a.get('categorie', 'TOUS').upper()}</span>
                <div class="card-title">{a.get('titre')}</div>
                <p style="color:#aaa; font-size:14px;">{a.get('resume')}...</p>
                <a href="/article/{a.get('id')}" class="btn">LIRE LA SUITE</a>
            </div>
        </div>'''
    return render_template_string(f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head><body><header><a href='/' class='logo'>METTA<span>BYTE</span></a></header><nav class='nav-cats'>{nav_html}</nav><div class='container'>{cards}</div></body></html>")

# --- LECTURE ---
@app.route('/article/<id>')
def read_article(id):
    try:
        r = requests.get(f"{SUPABASE_URL}?id=eq.{id}", headers=HEADERS)
        art = r.json()[0]
    except: return redirect('/')
    return render_template_string(f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head><body><header><a href='/' class='logo'>METTA<span>BYTE</span></a></header><div class='container'><img src='{art.get('img_url')}' style='width:100%; border-radius:15px;'><h1 style='margin:15px 0;'>{art.get('titre')}</h1><div style='white-space:pre-wrap;'>{art.get('texte')}</div><br><a href='/' class='btn' style='background:#222;'>RETOUR</a></div></body></html>")

# --- ADMIN (GESTION : AJOUTER / MODIFIER / SUPPRIMER) ---
@app.route(f'/{ADMIN_PATH}/', methods=['GET', 'POST'])
def admin():
    edit_id = request.args.get('edit')
    article_to_edit = None

    # Si on veut modifier, on récupère les données de l'article
    if edit_id:
        r = requests.get(f"{SUPABASE_URL}?id=eq.{edit_id}", headers=HEADERS)
        if r.json(): article_to_edit = r.json()[0]

    if request.method == 'POST':
        action = request.form.get('action')
        art_id = request.form.get('id')

        # SUPPRIMER
        if action == 'delete':
            requests.delete(f"{SUPABASE_URL}?id=eq.{art_id}", headers=HEADERS)
            return redirect(f'/{ADMIN_PATH}/')

        # PUBLIER OU METTRE À JOUR
        data = {
            "titre": request.form['titre'],
            "resume": request.form['texte'][:130],
            "texte": request.form['texte'],
            "img_url": request.form['img_url'],
            "categorie": request.form['categorie'],
            "ts": int(time.time())
        }
        
        if art_id: # Mise à jour
            requests.patch(f"{SUPABASE_URL}?id=eq.{art_id}", headers=HEADERS, json=data)
        else: # Nouvel article
            requests.post(SUPABASE_URL, headers=HEADERS, json=data)
        
        return redirect('/')

    # Liste des articles pour l'admin avec boutons Supprimer/Modifier
    try:
        r = requests.get(SUPABASE_URL, headers=HEADERS, params={"order": "ts.desc"})
        all_articles = r.json()
    except: all_articles = []

    admin_list = ""
    for a in all_articles:
        admin_list += f'''
        <div style="background:#111; padding:10px; border-radius:10px; margin-bottom:10px; border:1px solid #222;">
            <b style="font-size:14px;">{a.get('titre')}</b>
            <div style="display:flex; gap:10px;">
                <a href="/{ADMIN_PATH}/?edit={a.get('id')}" class="btn btn-edit">MODIFIER</a>
                <form method="post" style="flex:1;">
                    <input type="hidden" name="id" value="{a.get('id')}">
                    <input type="hidden" name="action" value="delete">
                    <button type="submit" class="btn btn-red" onclick="return confirm('Supprimer cet article ?')">SUPPRIMER</button>
                </form>
            </div>
        </div>'''

    return render_template_string(f"""
    <html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head><body>
        <header><span class="logo">ADMINISTRATION</span></header>
        <div class="container">
            <h3>{'MODIFIER ARTICLE' if article_to_edit else 'NOUVEL ARTICLE'}</h3>
            <form method="post">
                <input type="hidden" name="id" value="{article_to_edit.get('id') if article_to_edit else ''}">
                <input name="titre" placeholder="Titre" value="{article_to_edit.get('titre', '') if article_to_edit else ''}" required>
                <select name="categorie">
                    <option value="Tech" {'selected' if article_to_edit and article_to_edit.get('categorie')=='Tech' else ''}>Tech</option>
                    <option value="Science" {'selected' if article_to_edit and article_to_edit.get('categorie')=='Science' else ''}>Science</option>
                    <option value="IA" {'selected' if article_to_edit and article_to_edit.get('categorie')=='IA' else ''}>IA</option>
                    <option value="Espace" {'selected' if article_to_edit and article_to_edit.get('categorie')=='Espace' else ''}>Espace</option>
                </select>
                <input name="img_url" placeholder="URL Image" value="{article_to_edit.get('img_url', '') if article_to_edit else ''}" required>
                <textarea name="texte" rows="10" placeholder="Contenu" required>{article_to_edit.get('texte', '') if article_to_edit else ''}</textarea>
                <button type="submit" class="btn">{'ENREGISTRER LES MODIFICATIONS' if article_to_edit else 'PUBLIER'}</button>
                {f'<a href="/{ADMIN_PATH}/" style="color:#666; display:block; text-align:center; margin-top:10px;">Annuler la modification</a>' if article_to_edit else ''}
            </form>
            
            <hr style="border:0; border-top:1px solid #222; margin:30px 0;">
            <h3>MES ARTICLES</h3>
            {admin_list}
        </div>
    </body></html>""")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

