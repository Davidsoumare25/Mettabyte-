from flask import Flask, render_template_string, request, redirect, url_for
import os
import time

# Installation automatique de TinyDB si nécessaire
try:
    from tinydb import TinyDB, Query
except ImportError:
    os.system('pip install tinydb')
    from tinydb import TinyDB, Query

app = Flask(__name__)

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db = TinyDB(os.path.join(BASE_DIR, 'mettabyte_db.json'))
SECRET_ADMIN_PATH = "moncode123"

def time_ago(ts):
    diff = int(time.time()) - ts
    if diff < 60: return "À l'instant"
    if diff < 3600: return f"Il y a {diff//60} min"
    if diff < 86400: return f"Il y a {diff//3600} h"
    return f"Il y a {diff//86400} jours"

# --- DESIGN CSS ---
CSS = """
:root { --blue: #00d2ff; --purple: #9d50bb; --dark: #050505; }
body { font-family: 'Segoe UI', sans-serif; margin: 0; background: var(--dark); color: #eee; }
header { background: #000; padding: 25px 10px; text-align: center; border-bottom: 1px solid #111; }
.logo-text { font-size: 2.2rem; font-weight: 900; color: #fff; text-decoration: none; letter-spacing: 3px; text-transform: uppercase; text-shadow: 0 0 15px var(--blue); display: inline-block; }
.byte-part { color: var(--blue); }
.nav-categories { display: flex; gap: 12px; padding: 15px; background: #000; overflow-x: auto; border-bottom: 1px solid #222; }
.nav-link { color: #666; text-decoration: none; font-size: 12px; font-weight: bold; text-transform: uppercase; padding: 8px 15px; border-radius: 20px; border: 1px solid #222; white-space: nowrap; }
.nav-link.active { color: #fff; border-color: var(--blue); background: rgba(0,210,255,0.1); }
.container { width: 92%; max-width: 600px; margin: auto; padding: 20px 0; }
.card { background: #111; border-radius: 20px; overflow: hidden; margin-bottom: 30px; border: 1px solid #222; position: relative; }
.card-img { width: 100%; height: 250px; object-fit: cover; display: block; background: #1a1a1a; }
.card-body { padding: 20px; }
.card-title { font-size: 22px; font-weight: bold; color: #fff; text-decoration: none; display: block; margin-bottom: 10px; }
.btn { display: inline-block; background: linear-gradient(135deg, var(--blue), var(--purple)); color: white; padding: 12px 25px; border-radius: 10px; text-decoration: none; font-weight: bold; border: none; width: 100%; text-align: center; box-sizing: border-box; cursor: pointer; }
input, textarea, select { width: 100%; padding: 15px; margin: 10px 0; border: 1px solid #333; border-radius: 12px; background: #000; color: white; box-sizing: border-box; }
.time-badge { position: absolute; bottom: 75px; right: 20px; font-size: 11px; color: var(--blue); font-weight: bold; }
.back-link { color: var(--blue); text-decoration: none; font-weight: bold; display: inline-block; margin-bottom: 20px; }
"""

# --- ROUTES ---
@app.route('/')
def home():
    cat = request.args.get('cat', 'Tous')
    articles = db.all() if cat == 'Tous' else [a for a in db.all() if a.get('categorie') == cat]
    articles = sorted(articles, key=lambda k: k.get('ts', 0), reverse=True)
    
    cats = ["Tous", "Mystère", "Technologie", "Sciences", "Découverte"]
    nav = ''.join([f'<a href="/?cat={c}" class="nav-link {"active" if cat==c else ""}">{c}</a>' for c in cats])

    html = '<div class="container">'
    if not articles:
        html += '<p style="text-align:center; color:#555;">Aucun article pour le moment.</p>'
    for art in articles:
        html += f"""
        <div class="card">
            <img src="{art['img_url']}" class="card-img" onerror="this.src='https://placehold.co/600x400?text=Image+Non+Trouvée'">
            <div class="card-body">
                <a href="/article/{art.doc_id}" class="card-title">{art['titre']}</a>
                <p style="color:#888; margin-bottom:20px;">{art['resume']}...</p>
                <div class="time-badge">{time_ago(art['ts'])}</div>
                <a href="/article/{art.doc_id}" class="btn">LIRE L'ARTICLE</a>
            </div>
        </div>"""
    return render_template_string(f"<html><head><title>METTABYTE</title><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head><body><header><a href='/' class='logo-text'>METTA<span class='byte-part'>BYTE</span></a></header><div class='nav-categories'>{nav}</div>{html}</div></body></html>")

@app.route('/article/<int:id>')
def article(id):
    art = db.get(doc_id=id)
    if not art: return redirect(url_for('home'))
    return render_template_string(f"""
    <html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head>
    <body>
        <header><a href="/" class="logo-text">METTA<span class="byte-part">BYTE</span></a></header>
        <div class="container">
            <a href="javascript:history.back()" class="back-link">← RETOUR</a>
            <h1 style="color:white; margin:10px 0 20px 0;">{art['titre']}</h1>
            <img src="{art['img_url']}" style="width:100%; border-radius:20px; border: 1px solid #222;">
            <div style="font-size:18px; line-height:1.8; margin-top:25px; color:#ddd; white-space:pre-wrap;">{art['texte']}</div>
        </div>
    </body></html>""")

@app.route(f'/{SECRET_ADMIN_PATH}')
def admin():
    articles = sorted(db.all(), key=lambda k: k.get('ts', 0), reverse=True)
    html = f"""<div class="container">
        <a href="/" class="back-link">← RETOUR AU SITE</a>
        <a href="/{SECRET_ADMIN_PATH}/add" class="btn">+ RÉDIGER UN ARTICLE</a><br><br>"""
    for art in articles:
        html += f'<div style="background:#111;padding:15px;margin-bottom:10px;border-radius:10px;display:flex;justify-content:space-between;border:1px solid #222;align-items:center;"><span>{art["titre"][:30]}...</span><a href="/{SECRET_ADMIN_PATH}/delete/{art.doc_id}" style="color:red;text-decoration:none;font-weight:bold;">Supprimer</a></div>'
    return render_template_string(f"<html><head><style>{CSS}</style></head><body><header><span class='logo-text'>CONSOLE ADMIN</span></header>{html}</div></body></html>")

@app.route(f'/{SECRET_ADMIN_PATH}/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        db.insert({
            'titre': request.form['titre'], 
            'resume': request.form['texte'][:100], 
            'texte': request.form['texte'], 
            'categorie': request.form['categorie'], 
            'img_url': request.form['img_url'], 
            'ts': int(time.time())
        })
        return redirect(f"/{SECRET_ADMIN_PATH}")
    return render_template_string(f"""
    <html><head><style>{CSS}</style></head><body><header><span class='logo-text'>NOUVEL ARTICLE</span></header>
    <div class='container'>
        <a href="/{SECRET_ADMIN_PATH}" class="back-link">← ANNULER</a>
        <form method='post'>
            <input name='titre' placeholder='Titre de l article' required>
            <select name='categorie'>
                <option>Mystère</option><option>Technologie</option><option>Sciences</option><option>Découverte</option>
            </select>
            <input name='img_url' placeholder="Lien direct de l'image (URL .jpg ou .png)" required>
            <textarea name='texte' rows='10' placeholder='Écrivez votre article ici...' required></textarea>
            <button type='submit' class='btn'>PUBLIER MAINTENANT</button>
        </form>
    </div></body></html>""")

@app.route(f'/{SECRET_ADMIN_PATH}/delete/<int:id>')
def delete(id):
    db.remove(doc_ids=[id])
    return redirect(f"/{SECRET_ADMIN_PATH}")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

