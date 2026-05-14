import os
import requests
import time
from flask import Flask, request, redirect, session, Response

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_KEY") or "mettabyte_ultra_secret_2026"

# --- CONFIGURATION ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
ADMIN_PASS_ENV = os.environ.get("ADMIN_PASSWORD")
ADMIN_PATH = "moncode123"
LOGO_URL = "https://i.ibb.co/GfZxNrFq/img-1778540891.png"

# TON IDENTIFIANT RÉCUPÉRÉ
ADSENSE_ID = "pub-2847151888169934"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": "Bearer " + str(SUPABASE_KEY),
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# ─────────────────────────────────────────────
# LE DESIGN COMPLET (300 LIGNES DE STYLE)
# ─────────────────────────────────────────────
BASE_HTML = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>%PAGE_TITLE%</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-""" + ADSENSE_ID + """" crossorigin="anonymous"></script>

    <link rel="icon" href="%LOGO%">
    <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:ital,wght@0,300;0,400;0,700;1,300&family=Playfair+Display:ital@1&display=swap" rel="stylesheet">
    
    <style>
        :root { --blue: #00d2ff; --purple: #9d50bb; --dark: #050505; --gray: #1c1c1e; --white: #f5f0eb; --red: #e63022; }
        
        body { 
            font-family: 'DM Sans', -apple-system, sans-serif;
            margin: 0; background: var(--dark); color: #fff; line-height: 1.6; 
            -webkit-font-smoothing: antialiased; overflow-x: hidden;
            padding-bottom: 80px;
        }

        header { 
            background: rgba(0, 0, 0, 0.9); backdrop-filter: blur(20px);
            padding: 15px; text-align: center; border-bottom: 0.5px solid #333; position: sticky; top:0; z-index:1000;
        }

        .logo { font-size: 1.6rem; font-weight: 800; color: #fff; text-decoration: none; letter-spacing: -0.5px; font-family: 'Bebas Neue', sans-serif; }
        .logo span { color: var(--blue); }

        .nav-container { background: #000; border-bottom: 0.5px solid #222; padding: 12px 0; }
        .nav-cats { display: flex; gap: 12px; overflow-x: auto; padding: 0 20px; scroll-behavior: smooth; }
        .nav-cats::-webkit-scrollbar { display: none; }
        .cat { color: #8e8e93; text-decoration: none; font-size: 0.9rem; font-weight: 600; padding: 8px 18px; white-space: nowrap; border-radius: 20px; background: var(--gray); }
        .cat.active { color: #fff; background: linear-gradient(135deg, var(--blue), var(--purple)); }

        .container { width: 92%; max-width: 800px; margin: auto; padding: 20px 0; }
        
        /* STYLE MAGAZINE CARDS */
        .card { background: var(--gray); border-radius: 24px; overflow: hidden; margin-bottom: 30px; border: 0.5px solid #333; text-decoration: none; display: block; color: inherit; transition: transform 0.2s; }
        .card:active { transform: scale(0.98); }
        .card-img { width: 100%; height: 280px; object-fit: cover; }
        .card-body { padding: 25px; }
        .card-tag { color: var(--blue); font-size: 11px; font-weight: 700; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 1px; }
        .card-title { margin: 5px 0; font-size: 24px; font-weight: 700; line-height: 1.2; color: #fff; }

        /* DESIGN ÉDITORIAL ARTICLE */
        .article-hero { min-height: 70vh; display: flex; flex-direction: column; justify-content: flex-end; padding: 4rem 2rem; position: relative; background-size: cover; background-position: center; }
        .article-hero::after { content: ''; position: absolute; inset: 0; background: linear-gradient(to top, var(--dark) 15%, transparent 100%); }
        .hero-content { position: relative; z-index: 2; max-width: 800px; margin: 0 auto; width: 100%; }
        .hero-title { font-family: 'Bebas Neue', sans-serif; font-size: clamp(3rem, 10vw, 6rem); line-height: 0.9; margin: 0; color: #fff; }
        
        .article-content { max-width: 740px; margin: 0 auto; padding: 3rem 2rem; color: #c8c0b8; font-size: 1.15rem; line-height: 1.8; }
        .article-content h2 { font-family: 'Bebas Neue', sans-serif; font-size: 2.5rem; color: var(--white); margin: 3rem 0 1rem; border-left: 4px solid var(--blue); padding-left: 15px; }
        .article-content p { margin-bottom: 1.8rem; }
        .article-content img { max-width: 100%; border-radius: 15px; margin: 2rem 0; }

        .btn { display: block; background: linear-gradient(135deg, var(--blue), var(--purple)); color: #fff; padding: 18px; text-align: center; border-radius: 20px; text-decoration: none; font-weight: 700; border: none; font-size: 1rem; }
        
        .footer-nav { position: fixed; bottom: 0; left: 0; width: 100%; background: rgba(0,0,0,0.9); backdrop-filter: blur(15px); border-top: 0.5px solid #333; display: flex; justify-content: space-around; padding: 15px 0; z-index: 1000; }
        .footer-nav a { color: #888; text-decoration: none; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; }
        
        input, textarea, select { width: 100%; padding: 15px; margin: 10px 0; background: #1c1c1e; border: 1px solid #333; color: #fff; border-radius: 12px; font-size: 16px; }
    </style>
</head>
<body>
    <header><a href="/" class="logo">METTA<span>BYTE</span></a></header>
    %RAW_CONTENT%
    <div class="footer-nav">
        <a href="/">Accueil</a>
        <a href="mailto:mettabytesite@gmail.com">Contact</a>
        <a href="/privacy">Privacy</a>
    </div>
</body>
</html>"""

def render_page(content, title, logo=LOGO_URL):
    return BASE_HTML.replace("%PAGE_TITLE%", title).replace("%LOGO%", logo).replace("%RAW_CONTENT%", content)

# ─────────────────────────────────────────────
# ROUTES FONCTIONNELLES
# ─────────────────────────────────────────────

@app.route('/')
def home():
    cat = request.args.get('cat', 'Tous')
    params = {"order": "ts.desc"}
    if cat != 'Tous': params["categorie"] = "eq." + cat
    try:
        r = requests.get(SUPABASE_URL, headers=HEADERS, params=params)
        articles = r.json() if isinstance(r.json(), list) else []
    except: articles = []

    cats_list = ["Tous", "Tech", "Science", "IA", "Espace", "Santé", "Sport"]
    nav = '<div class="nav-container"><nav class="nav-cats">' + "".join([
        f'<a href="/?cat={c}" class="cat {"active" if c == cat else ""}">{c}</a>' for c in cats_list
    ]) + '</nav></div>'

    cards = "".join([
        f'<a href="/article/{a["id"]}" class="card">'
        f'<img src="{a.get("img_url", LOGO_URL)}" class="card-img">'
        f'<div class="card-body">'
        f'<div class="card-tag">{a.get("categorie", "TECH")}</div>'
        f'<h2 class="card-title">{a["titre"]}</h2>'
        f'</div></a>' for a in articles
    ])
    return render_page(nav + '<div class="container">' + cards + '</div>', "METTABYTE")

@app.route('/article/<id>')
def read_article(id):
    try:
        r = requests.get(SUPABASE_URL + "?id=eq." + str(id), headers=HEADERS)
        art = r.json()[0]
    except: return redirect('/')

    content = f"""
    <div class="article-hero" style="background-image: url('{art.get('img_url', LOGO_URL)}')">
        <div class="hero-content">
            <h1 class="hero-title">{art["titre"]}</h1>
        </div>
    </div>
    <div class="article-content">
        {art["texte"]}
        <br><br>
        <a href="/" class="btn" style="background:#222; width:fit-content; padding:12px 30px;">← RETOUR</a>
    </div>
    """
    return render_page(content, art['titre'])

@app.route('/ads.txt')
def ads_txt():
    return Response(f"google.com, {ADSENSE_ID}, DIRECT, f08c47fec0942fa0", mimetype='text/plain')

@app.route('/sitemap.xml')
def sitemap():
    base_url = request.url_root.rstrip('/')
    r = requests.get(SUPABASE_URL, headers=HEADERS, params={"select": "id"})
    articles = r.json() if isinstance(r.json(), list) else []
    xml = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    xml += f'<url><loc>{base_url}/</loc><priority>1.0</priority></url>'
    for a in articles: xml += f'<url><loc>{base_url}/article/{a["id"]}</loc></url>'
    xml += '</urlset>'
    return Response(xml, mimetype='text/xml')

@app.route('/' + ADMIN_PATH, methods=['GET', 'POST'])
def admin():
    if request.method == 'POST' and request.form.get('password') == ADMIN_PASS_ENV:
        session['logged_in'] = True
    if not session.get('logged_in'):
        return render_page('<div class="container" style="text-align:center;padding-top:100px;"><form method="post"><h1>Admin</h1><input type="password" name="password" placeholder="Pass"><button type="submit" class="btn">ENTRER</button></form></div>', "Admin")

    edit_id = request.args.get('edit')
    art = None
    if edit_id:
        res = requests.get(SUPABASE_URL + "?id=eq." + str(edit_id), headers=HEADERS)
        if res.json(): art = res.json()[0]

    if request.method == 'POST' and 'titre' in request.form:
        data = {"titre": request.form['titre'], "texte": request.form['texte'], "img_url": request.form['img_url'], "categorie": request.form['categorie'], "ts": int(time.time())}
        tid = request.form.get('id')
        if tid: requests.patch(SUPABASE_URL + "?id=eq." + tid, headers=HEADERS, json=data)
        else: requests.post(SUPABASE_URL, headers=HEADERS, json=data)
        return redirect('/' + ADMIN_PATH)

    r_list = requests.get(SUPABASE_URL, headers=HEADERS, params={"order": "ts.desc"})
    all_arts = r_list.json() if isinstance(r_list.json(), list) else []
    list_h = "".join([f'<div style="background:#111;padding:10px;margin:5px;border-radius:10px;">{a["titre"][:40]}... <a href="/{ADMIN_PATH}?edit={a["id"]}" style="color:var(--blue)">EDIT</a></div>' for a in all_arts])

    form = f"""<div class="container"><h1>PUBLIER</h1><form method="post"><input type="hidden" name="id" value="{art['id'] if art else ''}"><input name="titre" value="{art['titre'] if art else ''}" placeholder="Titre"><input name="img_url" value="{art['img_url'] if art else ''}" placeholder="Image"><textarea name="texte" rows="15" placeholder="Contenu HTML">{art['texte'] if art else ''}</textarea><select name="categorie"><option>Tech</option><option>Science</option><option>IA</option></select><button type="submit" class="btn">ENREGISTRER</button></form>{list_h}</div>"""
    return render_page(form, "Studio Admin")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

