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
ADSENSE_ID = "pub-2847151888169934"

# ⚠️ REMPLACE PAR TON VRAI CODE GOOGLE SEARCH CONSOLE
SEARCH_CONSOLE_CODE = "COLLE_TON_CODE_ICI"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": "Bearer " + str(SUPABASE_KEY),
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

BASE_HTML = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>%PAGE_TITLE%</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="description" content="%META_DESC%">

    <!-- Google Search Console -->
    <meta name="google-site-verification" content="%SEARCH_CONSOLE_CODE%">

    <!-- Google AdSense -->
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-%ADSENSE_ID%" crossorigin="anonymous"></script>

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
            background: rgba(0,0,0,0.9); backdrop-filter: blur(20px);
            padding: 15px; text-align: center; border-bottom: 0.5px solid #333;
            position: sticky; top: 0; z-index: 1000;
        }
        .logo { font-size: 1.6rem; font-weight: 800; color: #fff; text-decoration: none; font-family: 'Bebas Neue', sans-serif; }
        .logo span { color: var(--blue); }

        .nav-container { background: #000; border-bottom: 0.5px solid #222; padding: 12px 0; }
        .nav-cats { display: flex; gap: 12px; overflow-x: auto; padding: 0 20px; scroll-behavior: smooth; }
        .nav-cats::-webkit-scrollbar { display: none; }
        .cat { color: #8e8e93; text-decoration: none; font-size: 0.9rem; font-weight: 600; padding: 8px 18px; white-space: nowrap; border-radius: 20px; background: var(--gray); }
        .cat.active { color: #fff; background: linear-gradient(135deg, var(--blue), var(--purple)); }

        .container { width: 92%; max-width: 800px; margin: auto; padding: 20px 0; }

        /* CARDS */
        .card { background: var(--gray); border-radius: 24px; overflow: hidden; margin-bottom: 30px; border: 0.5px solid #333; text-decoration: none; display: block; color: inherit; transition: transform 0.2s; }
        .card:active { transform: scale(0.98); }
        .card-img { width: 100%; height: 280px; object-fit: cover; }
        .card-body { padding: 25px; }
        .card-tag { color: var(--blue); font-size: 11px; font-weight: 700; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 1px; }
        .card-title { margin: 5px 0; font-size: 24px; font-weight: 700; line-height: 1.2; color: #fff; }

        /* ARTICLE */
        .article-hero { min-height: 70vh; display: flex; flex-direction: column; justify-content: flex-end; padding: 4rem 2rem; position: relative; background-size: cover; background-position: center; }
        .article-hero::after { content: ''; position: absolute; inset: 0; background: linear-gradient(to top, var(--dark) 15%, transparent 100%); }
        .hero-content { position: relative; z-index: 2; max-width: 800px; margin: 0 auto; width: 100%; }
        .hero-title { font-family: 'Bebas Neue', sans-serif; font-size: clamp(3rem, 10vw, 6rem); line-height: 0.9; margin: 0; color: #fff; }
        .hero-meta { margin-top: 1rem; color: #aaa; font-size: 0.85rem; display: flex; gap: 1rem; flex-wrap: wrap; }

        .article-content { max-width: 740px; margin: 0 auto; padding: 3rem 2rem; color: #c8c0b8; font-size: 1.15rem; line-height: 1.8; }
        .article-content h2 { font-family: 'Bebas Neue', sans-serif; font-size: 2.5rem; color: var(--white); margin: 3rem 0 1rem; border-left: 4px solid var(--blue); padding-left: 15px; }
        .article-content h3 { font-family: 'Bebas Neue', sans-serif; font-size: 1.8rem; color: #ddd; margin: 2rem 0 0.75rem; }
        .article-content p { margin-bottom: 1.8rem; }
        .article-content img { max-width: 100%; border-radius: 15px; margin: 2rem 0; }
        .article-content blockquote { border-left: 3px solid var(--blue); padding: 1rem 1.5rem; background: #111; margin: 2rem 0; border-radius: 0 10px 10px 0; color: #aaa; font-style: italic; }
        .article-content ul, .article-content ol { padding-left: 1.5rem; margin-bottom: 1.5rem; }
        .article-content li { margin-bottom: 0.5rem; }
        .article-content a { color: var(--blue); }
        .article-content strong { color: #fff; }
        .article-content table { width: 100%; border-collapse: collapse; margin: 1.5rem 0; }
        .article-content th, .article-content td { border: 1px solid #333; padding: 10px; text-align: left; }
        .article-content th { background: #111; color: var(--blue); }
        .article-content pre { background: #111; padding: 1rem; border-radius: 8px; overflow-x: auto; font-family: monospace; color: #0f0; }

        /* PARTAGE */
        .share-bar { max-width: 740px; margin: 0 auto; padding: 0 2rem 2rem; display: flex; gap: 12px; flex-wrap: wrap; }
        .share-btn { display: inline-flex; align-items: center; gap: 8px; padding: 12px 20px; border-radius: 50px; font-size: 0.85rem; font-weight: 700; text-decoration: none; color: #fff; border: none; cursor: pointer; }
        .share-wa { background: #25D366; }
        .share-tw { background: #1DA1F2; }
        .share-copy { background: #333; }

        /* ARTICLES SIMILAIRES */
        .similaires { max-width: 740px; margin: 0 auto; padding: 0 2rem 3rem; }
        .similaires-title { font-family: 'Bebas Neue', sans-serif; font-size: 2rem; color: var(--blue); border-left: 4px solid var(--blue); padding-left: 15px; margin-bottom: 1.5rem; }
        .sim-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; }
        .sim-card { background: var(--gray); border-radius: 16px; overflow: hidden; text-decoration: none; display: block; color: inherit; border: 0.5px solid #333; transition: transform 0.2s; }
        .sim-card:active { transform: scale(0.97); }
        .sim-img { width: 100%; height: 130px; object-fit: cover; }
        .sim-body { padding: 12px; }
        .sim-tag { color: var(--blue); font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }
        .sim-title { font-size: 14px; font-weight: 700; color: #fff; margin: 4px 0 0; line-height: 1.3; }

        /* ADMIN */
        .admin-list-item { background: #111; padding: 12px 15px; margin-bottom: 6px; border-radius: 10px; display: flex; justify-content: space-between; align-items: center; gap: 10px; flex-wrap: wrap; }
        .btn-edit { color: var(--blue); font-size: 0.8rem; font-weight: 700; text-decoration: none; }
        .btn-delete { background: none; border: none; color: var(--red); font-size: 0.8rem; font-weight: 700; cursor: pointer; padding: 0; }

        .btn { display: block; background: linear-gradient(135deg, var(--blue), var(--purple)); color: #fff; padding: 18px; text-align: center; border-radius: 20px; text-decoration: none; font-weight: 700; border: none; font-size: 1rem; cursor: pointer; width: 100%; box-sizing: border-box; }

        .footer-nav { position: fixed; bottom: 0; left: 0; width: 100%; background: rgba(0,0,0,0.9); backdrop-filter: blur(15px); border-top: 0.5px solid #333; display: flex; justify-content: space-around; padding: 15px 0; z-index: 1000; }
        .footer-nav a { color: #888; text-decoration: none; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; }

        input, textarea, select { width: 100%; padding: 15px; margin: 10px 0; background: #1c1c1e; border: 1px solid #333; color: #fff; border-radius: 12px; font-size: 16px; box-sizing: border-box; }
        label { color: #888; font-size: 0.8rem; display: block; margin-top: 10px; }

        @media (max-width: 500px) { .sim-grid { grid-template-columns: 1fr; } }
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


def render_page(content, title, meta_desc="METTABYTE — Tech, IA, Science, Espace"):
    return (BASE_HTML
            .replace("%PAGE_TITLE%", title)
            .replace("%LOGO%", LOGO_URL)
            .replace("%RAW_CONTENT%", content)
            .replace("%META_DESC%", meta_desc)
            .replace("%SEARCH_CONSOLE_CODE%", SEARCH_CONSOLE_CODE)
            .replace("%ADSENSE_ID%", ADSENSE_ID))


def reading_time(html_text):
    import re
    clean = re.sub(r'<[^>]+>', '', html_text)
    words = len(clean.split())
    return max(1, round(words / 200))


# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────

@app.route('/')
def home():
    cat = request.args.get('cat', 'Tous')
    params = {"order": "ts.desc"}
    if cat != 'Tous':
        params["categorie"] = "eq." + cat
    try:
        r = requests.get(SUPABASE_URL, headers=HEADERS, params=params)
        articles = r.json() if isinstance(r.json(), list) else []
    except:
        articles = []

    cats_list = ["Tous", "Tech", "Science", "IA", "Espace", "Santé", "Sport"]
    nav = '<div class="nav-container"><nav class="nav-cats">' + "".join([
        f'<a href="/?cat={c}" class="cat {"active" if c == cat else ""}">{c}</a>'
        for c in cats_list
    ]) + '</nav></div>'

    cards = "".join([
        f'<a href="/article/{a["id"]}" class="card">'
        f'<img src="{a.get("img_url", LOGO_URL)}" class="card-img" loading="lazy">'
        f'<div class="card-body">'
        f'<div class="card-tag">{a.get("categorie","TECH")} · {reading_time(a.get("texte",""))} min de lecture</div>'
        f'<h2 class="card-title">{a["titre"]}</h2>'
        f'</div></a>'
        for a in articles
    ])

    return render_page(nav + '<div class="container">' + cards + '</div>', "METTABYTE")


@app.route('/article/<id>')
def read_article(id):
    try:
        r = requests.get(SUPABASE_URL + "?id=eq." + str(id), headers=HEADERS)
        art = r.json()[0]
    except:
        return redirect('/')

    # Articles similaires (même catégorie, exclut l'article actuel)
    try:
        cat = art.get("categorie", "Tech")
        rs = requests.get(SUPABASE_URL, headers=HEADERS, params={
            "categorie": "eq." + cat,
            "order": "ts.desc",
            "limit": "5"
        })
        similaires = [a for a in rs.json() if str(a["id"]) != str(id)][:4]
    except:
        similaires = []

    sim_cards = "".join([
        f'<a href="/article/{s["id"]}" class="sim-card">'
        f'<img src="{s.get("img_url", LOGO_URL)}" class="sim-img" loading="lazy">'
        f'<div class="sim-body">'
        f'<div class="sim-tag">{s.get("categorie","")}</div>'
        f'<div class="sim-title">{s["titre"]}</div>'
        f'</div></a>'
        for s in similaires
    ])

    sim_section = f"""
    <div class="similaires">
        <div class="similaires-title">À lire aussi</div>
        <div class="sim-grid">{sim_cards}</div>
    </div>
    """ if sim_cards else ""

    read_min = reading_time(art.get("texte", ""))
    article_url = request.url

    share_section = f"""
    <div class="share-bar">
        <a href="https://wa.me/?text={art['titre']}%20{article_url}" target="_blank" class="share-btn share-wa">📲 WhatsApp</a>
        <a href="https://twitter.com/intent/tweet?text={art['titre']}&url={article_url}" target="_blank" class="share-btn share-tw">🐦 Twitter / X</a>
        <button onclick="navigator.clipboard.writeText('{article_url}');this.innerText='✅ Copié !'" class="share-btn share-copy">🔗 Copier le lien</button>
    </div>
    """

    content = f"""
    <div class="article-hero" style="background-image: url('{art.get('img_url', LOGO_URL)}')">
        <div class="hero-content">
            <h1 class="hero-title">{art["titre"]}</h1>
            <div class="hero-meta">
                <span>🏷️ {art.get("categorie", "Tech")}</span>
                <span>⏱️ {read_min} min de lecture</span>
            </div>
        </div>
    </div>
    <div class="article-content">
        {art["texte"]}
        <br>
        <a href="/" class="btn" style="background:#222; width:fit-content; padding:12px 30px; display:inline-block; border-radius:15px;">← RETOUR</a>
    </div>
    {share_section}
    {sim_section}
    """
    return render_page(content, art['titre'], meta_desc=art['titre'] + " — METTABYTE")


@app.route('/ads.txt')
def ads_txt():
    return Response(
        f"google.com, {ADSENSE_ID}, DIRECT, f08c47fec0942fa0",
        mimetype='text/plain'
    )


@app.route('/sitemap.xml')
def sitemap():
    base_url = request.url_root.rstrip('/')
    try:
        r = requests.get(SUPABASE_URL, headers=HEADERS, params={"select": "id"})
        articles = r.json() if isinstance(r.json(), list) else []
    except:
        articles = []
    xml = '<?xml version="1.0" encoding="UTF-8"?>'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    xml += f'<url><loc>{base_url}/</loc><priority>1.0</priority></url>'
    for a in articles:
        xml += f'<url><loc>{base_url}/article/{a["id"]}</loc><priority>0.8</priority></url>'
    xml += '</urlset>'
    return Response(xml, mimetype='text/xml')


@app.route('/privacy')
def privacy():
    content = """
    <div class="container">
        <h1 style="font-family:'Bebas Neue'; font-size:3rem; color:var(--blue);">Confidentialité</h1>
        <h2 style="color:var(--blue); font-size:1.6rem; margin-top:30px;">Introduction</h2>
        <p style="color:#ccc;">Chez <strong>METTABYTE</strong>, la protection de la vie privée de nos visiteurs est l'une de nos priorités.</p>
        <h2 style="color:var(--blue); font-size:1.6rem; margin-top:30px;">Fichiers journaux</h2>
        <p style="color:#ccc;">Nous collectons les adresses IP, le type de navigateur, le FAI et l'horodatage à des fins d'analyse uniquement. Ces données ne permettent pas d'identifier personnellement les visiteurs.</p>
        <h2 style="color:var(--blue); font-size:1.6rem; margin-top:30px;">Publicités (Google AdSense)</h2>
        <p style="color:#ccc;">METTABYTE utilise Google AdSense. Google peut utiliser des cookies pour personnaliser les annonces selon vos centres d'intérêt.</p>
        <a href="/" style="background:#222; margin-top:30px; width:fit-content; padding:12px 30px; display:inline-block; border-radius:15px; text-decoration:none; color:#fff; font-weight:700;">← RETOUR</a>
    </div>
    """
    return render_page(content, "Confidentialité — METTABYTE")


@app.route('/' + ADMIN_PATH, methods=['GET', 'POST'])
def admin():
    # Connexion
    if request.method == 'POST' and request.form.get('password') == ADMIN_PASS_ENV:
        session['logged_in'] = True

    if not session.get('logged_in'):
        return render_page("""
        <div class="container" style="text-align:center; padding-top:100px;">
            <form method="post">
                <h1 style="font-family:'Bebas Neue'; font-size:3rem;">Studio Admin</h1>
                <input type="password" name="password" placeholder="Mot de passe" style="max-width:300px; margin:20px auto;">
                <button type="submit" class="btn" style="max-width:300px; margin:10px auto;">ENTRER</button>
            </form>
        </div>
        """, "Admin — METTABYTE")

    # ── SUPPRESSION ──
    if request.method == 'POST' and request.form.get('action') == 'delete':
        del_id = request.form.get('del_id')
        if del_id:
            requests.delete(SUPABASE_URL + "?id=eq." + del_id, headers=HEADERS)
        return redirect('/' + ADMIN_PATH)

    # ── ARTICLE À MODIFIER ──
    edit_id = request.args.get('edit')
    art = None
    if edit_id:
        res = requests.get(SUPABASE_URL + "?id=eq." + str(edit_id), headers=HEADERS)
        if res.json():
            art = res.json()[0]

    # ── ENREGISTREMENT ──
    if request.method == 'POST' and 'titre' in request.form:
        data = {
            "titre": request.form['titre'],
            "texte": request.form['texte'],
            "img_url": request.form['img_url'],
            "categorie": request.form['categorie'],
            "ts": int(time.time())
        }
        tid = request.form.get('id')
        if tid:
            requests.patch(SUPABASE_URL + "?id=eq." + tid, headers=HEADERS, json=data)
        else:
            requests.post(SUPABASE_URL, headers=HEADERS, json=data)
        return redirect('/' + ADMIN_PATH)

    # ── LISTE ARTICLES ──
    r_list = requests.get(SUPABASE_URL, headers=HEADERS, params={"order": "ts.desc"})
    all_arts = r_list.json() if isinstance(r_list.json(), list) else []

    list_html = "<h2 style='font-family:Bebas Neue; color:var(--blue); margin-top:40px;'>Articles publiés</h2>" + "".join([
        f'<div class="admin-list-item">'
        f'<span style="color:#ccc; font-size:0.9rem;">{a["titre"][:50]}...</span>'
        f'<div style="display:flex; gap:15px; align-items:center;">'
        f'<a href="/{ADMIN_PATH}?edit={a["id"]}" class="btn-edit">✏️ MODIFIER</a>'
        f'<form method="post" style="margin:0;" onsubmit="return confirm(\'Supprimer définitivement cet article ?\')">'
        f'<input type="hidden" name="action" value="delete">'
        f'<input type="hidden" name="del_id" value="{a["id"]}">'
        f'<button type="submit" class="btn-delete">🗑️ SUPPRIMER</button>'
        f'</form>'
        f'</div></div>'
        for a in all_arts
    ])

    cats_options = "".join([
        f'<option {"selected" if art and art.get("categorie") == c else ""}>{c}</option>'
        for c in ["Tech", "Science", "IA", "Espace", "Santé", "Sport"]
    ])

    texte_val = art['texte'].replace('</textarea>', '&lt;/textarea&gt;') if art else ''

    form = f"""
    <div class="container">
        <h1 style="font-family:'Bebas Neue'; font-size:2.5rem;">{"✏️ MODIFIER" if edit_id else "✍️ NOUVEL ARTICLE"}</h1>
        <form method="post">
            <input type="hidden" name="id" value="{art['id'] if art else ''}">
            <label>Titre</label>
            <input name="titre" placeholder="Titre de l'article" value="{art['titre'] if art else ''}" required>
            <label>URL de l'image de couverture</label>
            <input name="img_url" placeholder="https://..." value="{art.get('img_url','') if art else ''}">
            <label>Catégorie</label>
            <select name="categorie">{cats_options}</select>
            <label>Contenu HTML de l'article</label>
            <textarea name="texte" rows="20" placeholder="Colle ici le HTML de l'article...">{texte_val}</textarea>
            <button type="submit" class="btn">{"💾 ENREGISTRER LES MODIFICATIONS" if edit_id else "🚀 PUBLIER L'ARTICLE"}</button>
        </form>
        <hr style="border:0.5px solid #333; margin:40px 0;">
        {list_html}
    </div>
    """
    return render_page(form, "Studio Admin — METTABYTE")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
