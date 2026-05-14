import os
import requests
import time
from flask import Flask, render_template_string, request, redirect, session

app = Flask(__name__)
app.secret_key = "cle_session_mettabyte" # Nécessaire pour la connexion

# --- CONFIGURATION SÉCURISÉE ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
# Le mot de passe est masqué ici, il est récupéré sur Render
ADMIN_PASS_ENV = os.environ.get("ADMIN_PASSWORD") 
ADMIN_PATH = "moncode123" 
LOGO_URL = "https://i.ibb.co/GfZxNrFq/img-1778540891.png"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# --- STYLE CSS ---
BASE_HTML = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>{{ title }}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="{{ logo }}">
    <style>
        :root { --blue: #00d2ff; --purple: #9d50bb; --dark: #050505; }
        body { font-family: 'Segoe UI', sans-serif; margin: 0; background: var(--dark); color: #eee; line-height: 1.6; }
        header { background: #000; padding: 20px; text-align: center; border-bottom: 1px solid #111; position: sticky; top:0; z-index:100; }
        .logo { font-size: 1.8rem; font-weight: 900; color: #fff; text-decoration: none; letter-spacing: 2px; }
        .logo span { color: var(--blue); }
        .nav-cats { display: flex; gap: 10px; overflow-x: auto; padding: 15px; justify-content: center; background: #080808; border-bottom: 1px solid #111; }
        .cat { color: #888; text-decoration: none; font-size: 0.85rem; font-weight: bold; padding: 5px 10px; white-space: nowrap; border-radius: 20px; }
        .cat.active { color: #fff; background: linear-gradient(135deg, var(--blue), var(--purple)); }
        .container { width: 92%; max-width: 700px; margin: auto; padding: 20px 0; }
        .card { background: #111; border-radius: 15px; overflow: hidden; margin-bottom: 30px; border: 1px solid #222; }
        .card-img { width: 100%; height: 230px; object-fit: cover; }
        .card-body { padding: 20px; }
        .tag { background: #222; color: #aaa; font-size: 10px; padding: 3px 8px; border-radius: 5px; margin-right: 5px; text-transform: uppercase; }
        .btn { display: block; background: linear-gradient(135deg, var(--blue), var(--purple)); color: #fff; padding: 14px; text-align: center; border-radius: 12px; text-decoration: none; font-weight: bold; margin-top: 10px; border:none; width:100%; box-sizing:border-box; cursor:pointer; }
        input, textarea, select { width: 100%; padding: 12px; margin: 8px 0; background: #000; border: 1px solid #333; color: #fff; border-radius: 8px; box-sizing: border-box; }
        .admin-item { display:flex; justify-content:space-between; padding:10px; background:#181818; border-radius:8px; margin-bottom:8px; align-items:center; }
    </style>
</head>
<body>
    <header><a href="/" class="logo">METTA<span>BYTE</span></a></header>
    {% block content %}{% endblock %}
</body>
</html>
"""

@app.route('/')
def home():
    cat_filter = request.args.get('cat', 'Tous')
    params = {"order": "ts.desc"}
    if cat_filter != 'Tous': params["categorie"] = f"eq.{cat_filter}"
    try:
        r = requests.get(SUPABASE_URL, headers=HEADERS, params=params)
        articles = r.json() if isinstance(r.json(), list) else []
    except: articles = []
    
    # AJOUT SANTÉ ET SPORT ICI
    cats = ["Tous", "Science", "Tech", "IA", "Espace", "Santé", "Sport"]
    content = """
    <nav class="nav-cats">
        {% for c in cats %}
        <a href="/?cat={{c}}" class="cat {% if c == active_cat %}active{% endif %}">{{c}}</a>
        {% endfor %}
    </nav>
    <div class="container">
        {% for a in articles %}
        <div class="card">
            <img src="{{ a.get('img_url') or logo }}" class="card-img" onerror="this.src='{{ logo }}'">
            <div class="card-body">
                <span style="color:var(--blue); font-size:12px; font-weight:bold;">{{ (a.get('categorie') or 'NEWS')|upper }}</span>
                <h2 style="margin: 10px 0; font-size: 22px;">{{ a.get('titre') }}</h2>
                <a href="/article/{{ a.get('id') }}" class="btn">LIRE LA SUITE</a>
            </div>
        </div>
        {% endfor %}
    </div>
    """
    return render_template_string(BASE_HTML.replace('{% block content %}{% endblock %}', content), 
                                title="METTABYTE", logo=LOGO_URL, cats=cats, active_cat=cat_filter, articles=articles)

@app.route('/article/<id>')
def read_article(id):
    try:
        r = requests.get(f"{SUPABASE_URL}?id=eq.{id}", headers=HEADERS)
        art = r.json()[0]
    except: return redirect('/')
    content = f'<div class="container"><img src="{art.get("img_url") or LOGO_URL}" style="width:100%; border-radius:15px;"><h1 style="margin:20px 0;">{art.get("titre")}</h1><div style="white-space:pre-wrap; font-size:18px;">{art.get("texte")}</div><br><a href="/" class="btn" style="background:#222;">RETOUR</a></div>'
    return render_template_string(BASE_HTML.replace('{% block content %}{% endblock %}', content), title=art.get('titre'), logo=LOGO_URL)

# --- GESTION DE L'ADMIN AVEC MOT DE PASSE ---
@app.route(f'/{ADMIN_PATH}', methods=['GET', 'POST'])
def admin():
    # 1. Vérifier si on demande la connexion
    if request.method == 'POST' and 'password' in request.form:
        if request.form['password'] == ADMIN_PASS_ENV:
            session['logged_in'] = True
            return redirect(f'/{ADMIN_PATH}')
        else:
            return "Mot de passe incorrect."

    # 2. Si pas connecté, afficher le formulaire de mot de passe
    if not session.get('logged_in'):
        login_ui = """
        <div class="container" style="text-align:center; padding-top:100px;">
            <h3>Accès Restreint</h3>
            <form method="post">
                <input type="password" name="password" placeholder="Mot de passe" required>
                <button type="submit" class="btn">SE CONNECTER</button>
            </form>
        </div>
        """
        return render_template_string(BASE_HTML.replace('{% block content %}{% endblock %}', login_ui), title="Connexion", logo=LOGO_URL)

    # 3. Si connecté, gérer les articles (Post/Edit)
    edit_id = request.args.get('edit')
    article_to_edit = None
    if edit_id:
        r = requests.get(f"{SUPABASE_URL}?id=eq.{edit_id}", headers=HEADERS)
        if r.json(): article_to_edit = r.json()[0]

    if request.method == 'POST' and 'titre' in request.form:
        art_id = request.form.get('id')
        data = {
            "titre": request.form['titre'],
            "resume": request.form['texte'][:130],
            "texte": request.form['texte'],
            "img_url": request.form['img_url'],
            "categorie": request.form['categorie'],
            "mots_cles": request.form.get('mots_cles', ''),
            "ts": int(time.time())
        }
        if art_id: requests.patch(f"{SUPABASE_URL}?id=eq.{art_id}", headers=HEADERS, json=data)
        else: requests.post(SUPABASE_URL, headers=HEADERS, json=data)
        return redirect(f'/{ADMIN_PATH}')

    r = requests.get(SUPABASE_URL, headers=HEADERS, params={"order": "ts.desc"})
    all_arts = r.json() if isinstance(r.json(), list) else []
    
    admin_ui = """
    <div class="container">
        <h3>GESTIONNAIRE</h3>
        <form method="post">
            <input type="hidden" name="id" value="{{ art_edit.get('id') if art_edit else '' }}">
            <input name="titre" placeholder="Titre" value="{{ art_edit.get('titre') if art_edit else '' }}" required>
            <select name="categorie">
                {% for cat in ["Tech", "Science", "IA", "Espace", "Santé", "Sport"] %}
                <option value="{{cat}}" {% if art_edit and art_edit.get('categorie') == cat %}selected{% endif %}>{{cat}}</option>
                {% endfor %}
            </select>
            <input name="img_url" placeholder="URL Image" value="{{ art_edit.get('img_url') if art_edit else '' }}" required>
            <textarea name="texte" rows="10" placeholder="Contenu..." required>{{ art_edit.get('texte') if art_edit else '' }}</textarea>
            <button type="submit" class="btn">PUBLIER / MODIFIER</button>
            <a href="/" style="color:#888; text-decoration:none; display:block; text-align:center; margin-top:10px;">Quitter</a>
        </form>
        <div style="margin-top:30px;">
            {% for a in all_arts %}
            <div class="admin-item">
                <span>{{ a.get('titre')[:40] }}...</span>
                <a href="/{{ admin_path }}?edit={{ a.get('id') }}" style="color:var(--blue); font-weight:bold; text-decoration:none;">EDIT</a>
            </div>
            {% endfor %}
        </div>
    </div>
    """
    return render_template_string(BASE_HTML.replace('{% block content %}{% endblock %}', admin_ui), 
                                title="Admin", logo=LOGO_URL, art_edit=article_to_edit, all_arts=all_arts, admin_path=ADMIN_PATH)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

