import os
import requests
import time
from flask import Flask, render_template_string, request, redirect, session

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_KEY") or "mettabyte_ultra_secret_2026"

# --- CONFIGURATION ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
ADMIN_PASS_ENV = os.environ.get("ADMIN_PASSWORD")
ADMIN_PATH = "moncode123" 
LOGO_URL = "https://i.ibb.co/GfZxNrFq/img-1778540891.png"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": "Bearer " + str(SUPABASE_KEY),
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

BASE_HTML = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>{{ title }}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="{{ logo }}">
    <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@400;700&display=swap" rel="stylesheet">
    <style>
        :root { --blue: #00d2ff; --purple: #9d50bb; --dark: #050505; --gray: #1c1c1e; --red: #e63022; }
        body { font-family: 'DM Sans', sans-serif; margin: 0; background: var(--dark); color: #fff; padding-bottom: 80px; }
        header { background: #000; padding: 15px; text-align: center; border-bottom: 1px solid #333; position: sticky; top:0; z-index:1000; }
        .logo { font-size: 1.6rem; font-weight: 800; color: #fff; text-decoration: none; font-family: 'Bebas Neue', sans-serif; }
        .logo span { color: var(--blue); }
        .container { width: 92%; max-width: 800px; margin: auto; padding: 20px 0; }
        
        /* Navigation Categories */
        .nav-cats { display: flex; gap: 10px; overflow-x: auto; padding: 10px 20px; background: #0a0a0a; border-bottom: 1px solid #222; }
        .cat { color: #888; text-decoration: none; font-size: 0.8rem; font-weight: 700; padding: 8px 15px; border-radius: 20px; background: #1a1a1a; white-space: nowrap; }
        .cat.active { background: var(--blue); color: #000; }

        /* Article Styles */
        .article-banner { width: 100%; height: 350px; background-size: cover; background-position: center; position: relative; }
        .article-banner::after { content: ''; position: absolute; inset: 0; background: linear-gradient(to top, var(--dark), transparent); }
        .card { background: var(--gray); border-radius: 20px; overflow: hidden; margin-bottom: 25px; border: 1px solid #333; text-decoration: none; display: block; color: inherit; }
        .card-img { width: 100%; height: 230px; object-fit: cover; }
        .card-body { padding: 20px; }
        .btn { display: block; background: linear-gradient(135deg, var(--blue), var(--purple)); color: #fff; padding: 16px; text-align: center; border-radius: 15px; text-decoration: none; font-weight: 700; border: none; cursor: pointer; }

        /* Footer */
        .footer-nav { position: fixed; bottom: 0; left: 0; width: 100%; background: rgba(0,0,0,0.9); backdrop-filter: blur(10px); border-top: 1px solid #333; display: flex; justify-content: space-around; padding: 15px 0; z-index: 1000; }
        .footer-nav a { color: #888; text-decoration: none; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; }
        
        input, textarea, select { width: 100%; padding: 15px; margin: 10px 0; background: #1c1c1e; border: 1px solid #333; color: #fff; border-radius: 10px; box-sizing: border-box; }
        h1, h2 { font-family: 'Bebas Neue'; color: var(--blue); }
    </style>
</head>
<body>
    <header><a href="/" class="logo">METTA<span>BYTE</span></a></header>
    {% block content %}{% endblock %}
    <div class="footer-nav">
        <a href="/">Accueil</a>
        <a href="mailto:mettabytesite@gmail.com">Contact</a>
        <a href="/privacy">Confidentialité</a>
    </div>
</body>
</html>
"""

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
    nav = '<div class="nav-cats">' + "".join([f'<a href="/?cat={c}" class="cat {"active" if c==cat else ""}">{c}</a>' for c in cats_list]) + '</div>'
    cards = "".join([f'<a href="/article/{a["id"]}" class="card"><img src="{a.get("img_url", LOGO_URL)}" class="card-img"><div class="card-body"><small style="color:var(--blue)">{a.get("categorie", "TECH")}</small><h2 style="margin:5px 0; color:white;">{a["titre"]}</h2></div></a>' for a in articles])
    return render_template_string(BASE_HTML.replace('{% block content %}{% endblock %}', nav + '<div class="container">' + cards + '</div>'), title="METTABYTE", logo=LOGO_URL)

@app.route('/article/<id>')
def read_article(id):
    try:
        r = requests.get(SUPABASE_URL + "?id=eq." + str(id), headers=HEADERS)
        art = r.json()[0]
    except: return redirect('/')
    content = f"""
    <div class="article-banner" style="background-image: url('{art.get('img_url', LOGO_URL)}')"></div>
    <div class="container">
        <h1 style="font-size:3.5rem; margin-top:-50px; position:relative; z-index:2; color:white;">{art["titre"]}</h1>
        <div style="color:#ccc; font-size:1.1rem; margin-top:20px;">{art["texte"]}</div>
        <a href="/" class="btn" style="background:#222; margin-top:40px;">RETOUR</a>
    </div>
    """
    return render_template_string(BASE_HTML.replace('{% block content %}{% endblock %}', content), title=art['titre'], logo=LOGO_URL)

@app.route('/privacy')
def privacy():
    content = """
    <div class="container">
        <h1 style="font-size:3rem;">Nos politiques de confidentialité</h1>
        <h2 style="font-size:1.8rem; margin-top:30px;">Introduction</h2>
        <p style="color:#ccc;">Chez <strong>METTABYTE</strong>, accessible via notre site web, la protection de la vie privée de nos visiteurs est l'une de nos priorités. Ce document détaille les types d'informations collectées et la manière dont nous les utilisons.</p>
        
        <h2 style="font-size:1.8rem; margin-top:30px;">Fichiers journaux (Logs)</h2>
        <p style="color:#ccc;">METTABYTE suit une procédure standard d'utilisation des fichiers journaux. Ces fichiers enregistrent les visiteurs lorsqu'ils visitent des sites web. Toutes les sociétés d'hébergement font cela dans le cadre des analyses des services d'hébergement. Les informations collectées par les fichiers journaux comprennent les adresses de protocole internet (IP), le type de navigateur, le fournisseur d'accès à internet (FAI), l'horodatage, les pages de renvoi/sortie, et éventuellement le nombre de clics.</p>
        
        <p style="color:#ccc; margin-top:20px;">Ces données ne sont liées à aucune information permettant une identification personnelle. Le but de ces informations est d'analyser les tendances, d'administrer le site, de suivre les mouvements des utilisateurs sur le site web et de recueillir des informations démographiques.</p>
        
        <a href="/" class="btn" style="background:#222; margin-top:40px; width:fit-content; padding:10px 25px;">RETOUR À L'ACCUEIL</a>
    </div>
    """
    return render_template_string(BASE_HTML.replace('{% block content %}{% endblock %}', content), title="Confidentialité - METTABYTE", logo=LOGO_URL)

@app.route('/' + ADMIN_PATH, methods=['GET', 'POST'])
def admin():
    if request.method == 'POST' and 'password' in request.form:
        if request.form['password'] == ADMIN_PASS_ENV: session['logged_in'] = True
    if not session.get('logged_in'):
        return render_template_string(BASE_HTML.replace('{% block content %}{% endblock %}', '<div class="container" style="text-align:center;"><form method="post"><h3>Connexion Studio</h3><input type="password" name="password" placeholder="Code Admin"><button type="submit" class="btn">ENTRER</button></form></div>'), title="Admin", logo=LOGO_URL)
    edit_id = request.args.get('edit')
    art_to_edit = None
    if edit_id:
        r = requests.get(SUPABASE_URL + "?id=eq." + str(edit_id), headers=HEADERS)
        if r.json(): art_to_edit = r.json()[0]
    if request.method == 'POST' and 'titre' in request.form:
        data = {"titre": request.form['titre'], "texte": request.form['texte'], "img_url": request.form['img_url'], "categorie": request.form['categorie'], "ts": int(time.time())}
        target_id = request.form.get('id')
        if target_id: requests.patch(SUPABASE_URL + "?id=eq." + target_id, headers=HEADERS, json=data)
        else: requests.post(SUPABASE_URL, headers=HEADERS, json=data)
        return redirect('/' + ADMIN_PATH)
    r_list = requests.get(SUPABASE_URL, headers=HEADERS, params={"order": "ts.desc"})
    all_arts = r_list.json() if isinstance(r_list.json(), list) else []
    list_html = "<h3>Modifier un article</h3>" + "".join([f'<div style="background:#111; padding:10px; margin-bottom:5px; border-radius:10px; display:flex; justify-content:space-between;"><span>{a["titre"][:30]}...</span><a href="/{ADMIN_PATH}?edit={a["id"]}" style="color:var(--blue)">MODIFIER</a></div>' for a in all_arts])
    form_html = f"""
    <div class="container">
        <h2>{"MODIFIER" if edit_id else "NOUVEL ARTICLE"}</h2>
        <form method="post">
            <input type="hidden" name="id" value="{art_to_edit['id'] if art_to_edit else ''}">
            <input name="titre" placeholder="Titre" value="{art_to_edit['titre'] if art_to_edit else ''}" required>
            <input name="img_url" placeholder="Lien image" value="{art_to_edit['img_url'] if art_to_edit else ''}" required>
            <select name="categorie">
                {"".join([f'<option {"selected" if art_to_edit and art_to_edit["categorie"]==c else ""}>{c}</option>' for c in ["Tech", "Science", "IA", "Espace", "Santé", "Sport"]])}
            </select>
            <textarea name="texte" rows="15" placeholder="Contenu HTML">{art_to_edit['texte'] if art_to_edit else ''}</textarea>
            <button type="submit" class="btn">{"ENREGISTRER" if edit_id else "PUBLIER"}</button>
        </form>
        <hr style="border:0.5px solid #333; margin:40px 0;">
        {list_html}
    </div>
    """
    return render_template_string(BASE_HTML.replace('{% block content %}{% endblock %}', form_html), title="Studio Admin", logo=LOGO_URL)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

