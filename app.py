from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory
import os
import datetime
import time

try:
    from tinydb import TinyDB, Query
except ImportError:
    os.system('pip install tinydb')
    from tinydb import TinyDB, Query

app = Flask(__name__)

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_FOLDER = os.path.join(BASE_DIR, 'images_articles')
LOGO_FILENAME = '26091.png' 

if not os.path.exists(IMG_FOLDER):
    os.makedirs(IMG_FOLDER)

SECRET_ADMIN_PATH = "moncode123" 
db = TinyDB(os.path.join(BASE_DIR, 'frandroid_db.json'))

def time_ago(ts):
    diff = int(time.time()) - ts
    if diff < 60: return "À l'instant"
    if diff < 3600: return f"Il y a {diff//60} min"
    if diff < 86400: return f"Il y a {diff//3600} h"
    return f"Il y a {diff//86400} jours"

# --- DESIGN CSS CORRIGÉ ---
CSS = """
:root { --blue: #00d2ff; --purple: #9d50bb; --dark: #050505; }
body { font-family: 'Segoe UI', sans-serif; margin: 0; background: var(--dark); color: #eee; scroll-behavior: smooth; }

header { background: #000; padding: 25px 10px 10px 10px; text-align: center; }
.logo-text { font-size: 2.2rem; font-weight: 900; color: #fff; text-decoration: none; letter-spacing: 3px; text-transform: uppercase; text-shadow: 0 0 15px var(--blue); }
.byte-part { color: var(--blue); }

/* Correction du menu : Ajout de padding latéral pour le clic */
.nav-categories { 
    display: flex; 
    justify-content: flex-start; 
    gap: 12px; 
    padding: 15px 20px; 
    background: #000; 
    border-bottom: 1px solid #222; 
    overflow-x: auto; 
    -webkit-overflow-scrolling: touch;
}
/* Cacher la scrollbar mais garder le défilement */
.nav-categories::-webkit-scrollbar { display: none; }

.nav-link { 
    color: #666; 
    text-decoration: none; 
    font-size: 13px; 
    font-weight: bold; 
    text-transform: uppercase; 
    padding: 10px 18px; 
    border-radius: 25px; 
    border: 1px solid #222; 
    white-space: nowrap;
    transition: 0.3s;
}
.nav-link.active { color: #fff; border-color: var(--blue); background: rgba(0,210,255,0.15); box-shadow: 0 0 10px rgba(0,210,255,0.2); }

.container { width: 92%; max-width: 600px; margin: auto; padding: 20px 0; }
.card { background: #111; border-radius: 20px; overflow: hidden; margin-bottom: 30px; border: 1px solid #222; position: relative; scroll-margin-top: 100px; }
.card-img { width: 100%; height: auto; display: block; }
.card-body { padding: 20px; }
.card-title { font-size: 22px; font-weight: bold; color: #fff; text-decoration: none; display: block; margin-bottom: 10px; }

.time-badge { position: absolute; bottom: 18px; right: 20px; font-size: 11px; color: var(--blue); font-weight: bold; }

.btn { display: inline-block; background: linear-gradient(135deg, var(--blue), var(--purple)); color: white; padding: 14px 28px; border-radius: 12px; text-decoration: none; font-weight: bold; border: none; cursor: pointer; }
.btn-back { display: inline-block; margin-bottom: 25px; color: var(--blue); text-decoration: none; font-weight: bold; font-size: 18px; }

input, textarea, select { width: 100%; padding: 15px; margin: 10px 0; border: 1px solid #333; border-radius: 12px; background: #000; color: white; font-size: 16px; }
"""

@app.route('/logo.png')
def get_logo():
    return send_from_directory(BASE_DIR, LOGO_FILENAME)

# --- ACCUEIL ---
@app.route('/')
def home():
    cat = request.args.get('cat', 'Tous')
    if cat == 'Tous':
        articles = db.all()
    else:
        articles = [a for a in db.all() if a.get('categorie') == cat]
    
    articles = sorted(articles, key=lambda k: k.get('ts', 0), reverse=True)
    
    cats = ["Tous", "Mystère", "Technologie", "Sciences", "Découverte"]
    nav_html = '<div class="nav-categories">'
    for c in cats:
        active = "active" if cat == c else ""
        nav_html += f'<a href="/?cat={c}" class="nav-link {active}">{c}</a>'
    nav_html += '</div>'

    html = '<div class="container">'
    for art in articles:
        # On passe la catégorie actuelle dans le lien de l'article pour le retour
        html += f"""
        <div class="card" id="art-{art.doc_id}">
            <img src="/images/{art['img']}" class="card-img">
            <div class="card-body">
                <a href="/article/{art.doc_id}?from_cat={cat}" class="card-title">{art['titre']}</a>
                <p style="color:#888; font-size:15px; margin-bottom:40px;">{art['resume']}...</p>
                <div class="time-badge">{time_ago(art['ts'])}</div>
                <a href="/article/{art.doc_id}?from_cat={cat}" class="btn">DÉCOUVRIR</a>
            </div>
        </div>"""
    html += '</div>'
    
    return render_template_string(f"""
    <html><head><title>METTABYTE</title><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head>
    <body><header><a href="/" class="logo-text">METTA<span class="byte-part">BYTE</span></a></header>
    {nav_html}{html}</body></html>""")

# --- ARTICLE (Correction de la mémoire de catégorie) ---
@app.route('/article/<int:id>')
def article(id):
    art = db.get(doc_id=id)
    # On récupère la catégorie d'origine via l'URL
    from_cat = request.args.get('from_cat', 'Tous')
    
    # Le lien de retour pointe maintenant vers la catégorie ET l'ancre de l'article
    back_url = f"/?cat={from_cat}#art-{id}"
    
    return render_template_string(f"""
    <html><head><title>{art['titre']}</title><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head>
    <body>
        <header><a href="/" class="logo-text">METTA<span class="byte-part">BYTE</span></a></header>
        <div class="container">
            <a href="{back_url}" class="btn-back">← RETOUR ({from_cat})</a>
            <h1 style="color:white; font-size:28px;">{art['titre']}</h1>
            <img src="/images/{art['img']}" style="width:100%; border-radius:20px;">
            <div style="font-size:18px; line-height:1.8; margin-top:25px; color:#ddd; white-space:pre-wrap;">{art['texte']}</div>
            
            <div style="margin-top:40px; text-align:center; border-top:1px solid #222; padding-top:20px;">
                <button onclick="navigator.clipboard.writeText(window.location.href); alert('Lien copié !')" class="btn">🔗 PARTAGER</button>
            </div>
        </div>
    </body></html>""")

# --- ADMIN (Toujours identique) ---
@app.route(f'/{SECRET_ADMIN_PATH}')
def admin_home():
    articles = sorted(db.all(), key=lambda k: k.get('ts', 0), reverse=True)
    html = f"""<div class="container"><a href="/" class="btn" style="width:100%; background:#222; margin-bottom:20px;">🏠 RETOUR SITE</a><a href="/{SECRET_ADMIN_PATH}/add" class="btn" style="width:100%; margin-bottom:20px;">+ RÉDIGER</a>"""
    for art in articles:
        html += f"""<div style="background:#1a1a1a; padding:15px; margin-bottom:10px; border-radius:15px; display:flex; justify-content:space-between; border:1px solid #333;"><span>{art['titre'][:30]}...</span><div><a href="/{SECRET_ADMIN_PATH}/edit/{art.doc_id}" style="color:var(--blue); text-decoration:none; margin-right:10px;">EDIT</a><a href="/{SECRET_ADMIN_PATH}/delete/{art.doc_id}" style="color:red; text-decoration:none;">X</a></div></div>"""
    return render_template_string(f"<html><head><style>{CSS}</style></head><body><header><a href='/' class='logo-text'>METTA<span class='byte-part'>ADMIN</span></a></header>{html}</div></body></html>")

@app.route(f'/{SECRET_ADMIN_PATH}/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        img = request.files['img_file']
        if img:
            ts = int(time.time())
            img_name = f"img_{ts}.jpg"
            img.save(os.path.join(IMG_FOLDER, img_name))
            db.insert({'titre': request.form['titre'], 'resume': request.form['texte'][:100], 'texte': request.form['texte'], 'categorie': request.form['categorie'], 'img': img_name, 'ts': ts})
            return redirect(f"/{SECRET_ADMIN_PATH}")
    return render_template_string(f"""<html><head><style>{CSS}</style></head><body><header><a href='/' class='logo-text'>PUBLIER</a></header><div class='container'><form method='post' enctype='multipart/form-data'><input type='text' name='titre' placeholder='Titre' required><select name="categorie"><option>Mystère</option><option>Technologie</option><option>Sciences</option><option>Découverte</option></select><input type='file' name='img_file' accept='image/*' required><textarea name='texte' rows='10' placeholder='Texte...' required></textarea><button type='submit' class='btn' style='width:100%'>PUBLIER</button></form></div></body></html>""")

@app.route(f'/{SECRET_ADMIN_PATH}/delete/<int:id>')
def delete(id):
    art = db.get(doc_id=id)
    if art:
        try: os.remove(os.path.join(IMG_FOLDER, art['img']))
        except: pass
        db.remove(doc_ids=[id])
    return redirect(f"/{SECRET_ADMIN_PATH}")

@app.route(f'/{SECRET_ADMIN_PATH}/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    art = db.get(doc_id=id)
    if request.method == 'POST':
        img_name = art['img']
        if request.files['img_file']:
            img_name = f"img_{int(time.time())}.jpg"
            request.files['img_file'].save(os.path.join(IMG_FOLDER, img_name))
        db.update({'titre': request.form['titre'], 'resume': request.form['texte'][:100], 'texte': request.form['texte'], 'categorie': request.form['categorie'], 'img': img_name}, doc_ids=[id])
        return redirect(f"/{SECRET_ADMIN_PATH}")
    return render_template_string(f"<html><head><style>{CSS}</style></head><body><header><a href='/' class='logo-text'>ÉDITER</a></header><div class='container'><form method='post' enctype='multipart/form-data'><input type='text' name='titre' value=\"{art['titre']}\" required><select name='categorie'><option {'selected' if art['categorie']=='Mystère' else ''}>Mystère</option><option {'selected' if art['categorie']=='Technologie' else ''}>Technologie</option><option {'selected' if art['categorie']=='Sciences' else ''}>Sciences</option><option {'selected' if art['categorie']=='Découverte' else ''}>Découverte</option></select><input type='file' name='img_file' accept='image/*'><textarea name='texte' rows='10' required>{art['texte']}</textarea><button type='submit' class='btn' style='width:100%'>SAUVEGARDER</button></form></div></body></html>")

@app.route('/images/<filename>')
def get_img(filename):
    return send_from_directory(IMG_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
