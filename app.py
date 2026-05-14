import os
import requests
import time
from flask import Flask, request, redirect, session

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

# ─────────────────────────────────────────────
# BASE HTML — on utilise %RAW_CONTENT% comme
# marqueur neutre à la place de {% block %}
# pour éviter tout conflit Jinja2
# ─────────────────────────────────────────────
BASE_HTML = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>%PAGE_TITLE%</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="%LOGO%">
    <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@400;700&display=swap" rel="stylesheet">
    <style>
        :root { --blue: #00d2ff; --purple: #9d50bb; --dark: #050505; --gray: #1c1c1e; --red: #e63022; }
        body { font-family: 'DM Sans', sans-serif; margin: 0; background: var(--dark); color: #fff; padding-bottom: 80px; }
        header { background: #000; padding: 15px; text-align: center; border-bottom: 1px solid #333; position: sticky; top:0; z-index:1000; }
        .logo { font-size: 1.6rem; font-weight: 800; color: #fff; text-decoration: none; font-family: 'Bebas Neue', sans-serif; }
        .logo span { color: var(--blue); }
        .container { width: 92%; max-width: 800px; margin: auto; padding: 20px 0; }
        .nav-cats { display: flex; gap: 10px; overflow-x: auto; padding: 10px 20px; background: #0a0a0a; border-bottom: 1px solid #222; }
        .cat { color: #888; text-decoration: none; font-size: 0.8rem; font-weight: 700; padding: 8px 15px; border-radius: 20px; background: #1a1a1a; white-space: nowrap; }
        .cat.active { background: var(--blue); color: #000; }
        .article-banner { width: 100%; height: 350px; background-size: cover; background-position: center; position: relative; }
        .article-banner::after { content: ''; position: absolute; inset: 0; background: linear-gradient(to top, var(--dark), transparent); }
        .card { background: var(--gray); border-radius: 20px; overflow: hidden; margin-bottom: 25px; border: 1px solid #333; text-decoration: none; display: block; color: inherit; }
        .card-img { width: 100%; height: 230px; object-fit: cover; }
        .card-body { padding: 20px; }
        .btn { display: block; background: linear-gradient(135deg, var(--blue), var(--purple)); color: #fff; padding: 16px; text-align: center; border-radius: 15px; text-decoration: none; font-weight: 700; border: none; cursor: pointer; }
        .footer-nav { position: fixed; bottom: 0; left: 0; width: 100%; background: rgba(0,0,0,0.9); backdrop-filter: blur(10px); border-top: 1px solid #333; display: flex; justify-content: space-around; padding: 15px 0; z-index: 1000; }
        .footer-nav a { color: #888; text-decoration: none; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; }
        input, textarea, select { width: 100%; padding: 15px; margin: 10px 0; background: #1c1c1e; border: 1px solid #333; color: #fff; border-radius: 10px; box-sizing: border-box; }
        h1, h2 { font-family: 'Bebas Neue'; color: var(--blue); }

        /* ── STYLES ARTICLE ── */
        .article-content { color: #ccc; font-size: 1.05rem; line-height: 1.85; }
        .article-content h1,
        .article-content h2,
        .article-content h3 { font-family: 'Bebas Neue', sans-serif; color: var(--blue); margin: 1.5rem 0 0.75rem; }
        .article-content h1 { font-size: 2.2rem; }
        .article-content h2 { font-size: 1.8rem; }
        .article-content h3 { font-size: 1.4rem; color: #fff; }
        .article-content p  { margin-bottom: 1.2rem; }
        .article-content strong { color: #fff; }
        .article-content em { color: var(--blue); font-style: normal; }
        .article-content blockquote {
            border-left: 3px solid var(--blue);
            padding: 0.75rem 1.25rem;
            background: #111;
            margin: 1.5rem 0;
            border-radius: 0 8px 8px 0;
            color: #aaa;
            font-style: italic;
        }
        .article-content img { max-width: 100%; border-radius: 10px; margin: 1rem 0; }
        .article-content ul, .article-content ol { padding-left: 1.5rem; margin-bottom: 1.2rem; }
        .article-content li { margin-bottom: 0.4rem; }
        .article-content a { color: var(--blue); }
        .article-content table { width: 100%; border-collapse: collapse; margin: 1.5rem 0; }
        .article-content th, .article-content td { border: 1px solid #333; padding: 10px; text-align: left; }
        .article-content th { background: #111; color: var(--blue); }
        .article-content hr { border: 0; border-top: 1px solid #333; margin: 2rem 0; }
        .article-content pre {
            background: #111;
            padding: 1rem;
            border-radius: 8px;
            overflow-x: auto;
            font-family: monospace;
            font-size: 0.9rem;
            color: #0f0;
            margin-bottom: 1.2rem;
        }
    </style>
</head>
<body>
    <header><a href="/" class="logo">METTA<span>BYTE</span></a></header>
    %RAW_CONTENT%
    <div class="footer-nav">
        <a href="/">Accueil</a>
        <a href="mailto:mettabytesite@gmail.com">Contact</a>
        <a href="/privacy">Confidentialité</a>
    </div>
</body>
</html>"""


def render_page(content, title, logo=LOGO_URL):
    """
    Assemble la page sans passer par Jinja2.
    Le contenu HTML brut est injecté directement via str.replace()
    — aucun risque de conflit avec {{ }} ou {% %}.
    """
    html = BASE_HTML
    html = html.replace("%PAGE_TITLE%", title)
    html = html.replace("%LOGO%", logo)
    html = html.replace("%RAW_CONTENT%", content)
    return html


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
    nav = '<div class="nav-cats">' + "".join([
        f'<a href="/?cat={c}" class="cat {"active" if c == cat else ""}">{c}</a>'
        for c in cats_list
    ]) + '</div>'

    cards = "".join([
        f'<a href="/article/{a["id"]}" class="card">'
        f'<img src="{a.get("img_url", LOGO_URL)}" class="card-img">'
        f'<div class="card-body">'
        f'<small style="color:var(--blue)">{a.get("categorie", "TECH")}</small>'
        f'<h2 style="margin:5px 0; color:white;">{a["titre"]}</h2>'
        f'</div></a>'
        for a in articles
    ])

    content = nav + '<div class="container">' + cards + '</div>'
    return render_page(content, "METTABYTE")


@app.route('/article/<id>')
def read_article(id):
    try:
        r = requests.get(SUPABASE_URL + "?id=eq." + str(id), headers=HEADERS)
        art = r.json()[0]
    except:
        return redirect('/')

    # Le texte de l'article est injecté tel quel dans .article-content
    # — aucun passage par Jinja2, donc aucun conflit possible
    content = f"""
    <div class="article-banner" style="background-image: url('{art.get('img_url', LOGO_URL)}')"></div>
    <div class="container">
        <h1 style="font-size:clamp(2rem,6vw,3.5rem); margin-top:-50px; position:relative; z-index:2; color:white; font-family:'Bebas Neue';">
            {art["titre"]}
        </h1>
        <div class="article-content" style="margin-top:20px;">
            {art["texte"]}
        </div>
        <a href="/" class="btn" style="background:#222; margin-top:40px;">← RETOUR</a>
    </div>
    """
    return render_page(content, art['titre'])


@app.route('/privacy')
def privacy():
    content = """
    <div class="container">
        <h1 style="font-size:3rem;">Nos politiques de confidentialité</h1>
        <h2 style="font-size:1.8rem; margin-top:30px;">Introduction</h2>
        <p style="color:#ccc;">Chez <strong>METTABYTE</strong>, accessible via notre site web, la protection de la vie privée de nos visiteurs est l'une de nos priorités.</p>
        <h2 style="font-size:1.8rem; margin-top:30px;">Fichiers journaux (Logs)</h2>
        <p style="color:#ccc;">METTABYTE suit une procédure standard d'utilisation des fichiers journaux. Ces fichiers enregistrent les visiteurs lorsqu'ils visitent des sites web. Les informations collectées comprennent les adresses IP, le type de navigateur, le FAI, l'horodatage, les pages de renvoi/sortie.</p>
        <p style="color:#ccc; margin-top:20px;">Ces données ne sont liées à aucune information permettant une identification personnelle.</p>
        <a href="/" class="btn" style="background:#222; margin-top:40px; width:fit-content; padding:10px 25px;">RETOUR À L'ACCUEIL</a>
    </div>
    """
    return render_page(content, "Confidentialité - METTABYTE")


@app.route('/' + ADMIN_PATH, methods=['GET', 'POST'])
def admin():
    # Connexion
    if request.method == 'POST' and 'password' in request.form:
        if request.form['password'] == ADMIN_PASS_ENV:
            session['logged_in'] = True

    if not session.get('logged_in'):
        login_form = """
        <div class="container" style="text-align:center; padding-top:80px;">
            <form method="post">
                <h1 style="font-size:2.5rem;">Studio Admin</h1>
                <input type="password" name="password" placeholder="Mot de passe admin" style="max-width:300px; margin:20px auto;">
                <button type="submit" class="btn" style="max-width:300px; margin:auto;">ENTRER</button>
            </form>
        </div>
        """
        return render_page(login_form, "Admin - METTABYTE")

    # Récupérer article à modifier si ?edit=id
    edit_id = request.args.get('edit')
    art_to_edit = None
    if edit_id:
        r = requests.get(SUPABASE_URL + "?id=eq." + str(edit_id), headers=HEADERS)
        if r.json():
            art_to_edit = r.json()[0]

    # Suppression
    if request.method == 'POST' and request.form.get('action') == 'delete':
        del_id = request.form.get('id')
        if del_id:
            requests.delete(SUPABASE_URL + "?id=eq." + del_id, headers=HEADERS)
        return redirect('/' + ADMIN_PATH)

    # Enregistrement article (nouveau ou modif)
    if request.method == 'POST' and 'titre' in request.form:
        data = {
            "titre": request.form['titre'],
            "texte": request.form['texte'],   # HTML brut conservé intact
            "img_url": request.form['img_url'],
            "categorie": request.form['categorie'],
            "ts": int(time.time())
        }
        target_id = request.form.get('id')
        if target_id:
            requests.patch(SUPABASE_URL + "?id=eq." + target_id, headers=HEADERS, json=data)
        else:
            requests.post(SUPABASE_URL, headers=HEADERS, json=data)
        return redirect('/' + ADMIN_PATH)

    # Liste des articles existants
    r_list = requests.get(SUPABASE_URL, headers=HEADERS, params={"order": "ts.desc"})
    all_arts = r_list.json() if isinstance(r_list.json(), list) else []

    list_html = "<h2 style='margin-top:40px;'>Articles publiés</h2>" + "".join([
        f'<div style="background:#111; padding:12px 15px; margin-bottom:6px; border-radius:10px; display:flex; justify-content:space-between; align-items:center; gap:10px; flex-wrap:wrap;">'
        f'<span style="color:#ccc; font-size:0.9rem;">{a["titre"][:45]}...</span>'
        f'<div style="display:flex; gap:10px;">'
        f'<a href="/{ADMIN_PATH}?edit={a["id"]}" style="color:var(--blue); font-size:0.8rem; font-weight:700;">MODIFIER</a>'
        f'<form method="post" style="margin:0;" onsubmit="return confirm(\'Supprimer cet article ?\');">'
        f'<input type="hidden" name="action" value="delete">'
        f'<input type="hidden" name="id" value="{a["id"]}">'
        f'<button type="submit" style="background:none; border:none; color:#e63022; font-size:0.8rem; font-weight:700; cursor:pointer; padding:0;">SUPPRIMER</button>'
        f'</form>'
        f'</div></div>'
        for a in all_arts
    ])

    cats_options = "".join([
        f'<option {"selected" if art_to_edit and art_to_edit["categorie"] == c else ""}>{c}</option>'
        for c in ["Tech", "Science", "IA", "Espace", "Santé", "Sport"]
    ])

    # Échapper les guillemets dans le texte de l'article pour l'attribut value du textarea
    texte_val = art_to_edit['texte'].replace('</textarea>', '&lt;/textarea&gt;') if art_to_edit else ''
    titre_val = art_to_edit['titre'] if art_to_edit else ''
    img_val   = art_to_edit['img_url'] if art_to_edit else ''
    id_val    = str(art_to_edit['id']) if art_to_edit else ''

    form_html = f"""
    <div class="container">
        <h1 style="font-size:2.5rem;">{"MODIFIER L'ARTICLE" if edit_id else "NOUVEL ARTICLE"}</h1>
        <form method="post">
            <input type="hidden" name="id" value="{id_val}">
            <input name="titre" placeholder="Titre de l'article" value="{titre_val}" required>
            <input name="img_url" placeholder="URL de l'image de couverture" value="{img_val}">
            <select name="categorie">{cats_options}</select>
            <label style="color:#888; font-size:0.8rem; margin-top:10px; display:block;">
                Contenu HTML de l'article — colle ici le HTML généré
            </label>
            <textarea name="texte" rows="20" placeholder="Contenu HTML de l'article...">{texte_val}</textarea>
            <button type="submit" class="btn">{"ENREGISTRER LES MODIFICATIONS" if edit_id else "PUBLIER L'ARTICLE"}</button>
        </form>
        <hr style="border:0.5px solid #333; margin:40px 0;">
        {list_html}
    </div>
    """
    return render_page(form_html, "Studio Admin - METTABYTE")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

