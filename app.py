import os
import requests
import time
from flask import Flask, render_template_string, request, redirect, session

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_KEY") or "mettabyte_secret_super_2026"

# --- CONFIGURATION ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
ADMIN_PASS_ENV = os.environ.get("ADMIN_PASSWORD")
ADMIN_PATH = "moncode123" 
LOGO_URL = "https://i.ibb.co/GfZxNrFq/img-1778540891.png"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# --- DESIGN IPHONE 17 (Ultra Fluide) ---
BASE_HTML = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>{{ title }}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <link rel="icon" href="{{ logo }}">
    <style>
        :root { --blue: #00d2ff; --purple: #9d50bb; --dark: #050505; --gray: #1c1c1e; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif;
            margin: 0; background: var(--dark); color: #fff; line-height: 1.5; 
            -webkit-font-smoothing: antialiased;
        }
        header { 
            background: rgba(0, 0, 0, 0.8); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
            padding: 15px; text-align: center; border-bottom: 0.5px solid #333; position: sticky; top:0; z-index:100;
        }
        .logo { font-size: 1.6rem; font-weight: 800; color: #fff; text-decoration: none; letter-spacing: -0.5px; }
        .logo span { color: var(--blue); }
        .nav-container { background: rgba(0,0,0,0.3); border-bottom: 0.5px solid #222; padding: 12px 0; }
        .nav-cats { 
            display: flex; gap: 12px; overflow-x: auto; padding: 0 20px;
            scroll-behavior: smooth; -webkit-overflow-scrolling: touch;
        }
        .nav-cats::-webkit-scrollbar { display: none; }
        .cat { 
            color: #8e8e93; text-decoration: none; font-size: 0.9rem; font-weight: 600; 
            padding: 8px 18px; white-space: nowrap; border-radius: 20px;
            background: var(--gray); transition: all 0.2s ease;
        }
        .cat.active { 
            color: #fff; background: linear-gradient(135deg, var(--blue), var(--purple));
        }
        .container { width: 92%; max-width: 600px; margin: auto; padding: 20px 0; }
        .card { 
            background: var(--gray); border-radius: 24px; overflow: hidden; 
            margin-bottom: 25px; border: 0.5px solid #333; transition: transform 0.2s ease;
        }
        .card:active { transform: scale(0.97); }
        .card-img { width: 100%; height: 250px; object-fit: cover; }
        .card-body { padding: 20px; }
        .card-tag { color: var(--blue); font-size: 11px; font-weight: 700; text-transform: uppercase; margin-bottom: 5px; }
        .card-title { margin: 5px 0; font-size: 20px; font-weight: 700; }
        .btn { 
            display: block; background: linear-gradient(135deg, var(--blue), var(--purple)); 
            color: #fff; padding: 16px; text-align: center; border-radius: 18px; 
            text-decoration: none; font-weight: 700; margin-top: 15px; border:none; width:100%; box-sizing:border-box;
        }
        input, textarea, select { 
            width: 100%; padding: 15px; margin: 10px 0; background: #2c2c2e; 
            border: none; color: #fff; border-radius: 12px; font-size: 16px; box-sizing: border-box;
        }
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
    
    cats = ["Tous", "Science", "Tech", "IA", "Espace", "Santé", "Sport"]
    
    content = """
    <div class="nav-container">
        <nav class="nav-cats">
            {% for c in cats %}
            <a href="/?cat={{c}}" class="cat {% if c == active_cat %}active{% endif %}">{{c}}</a>
            {% endfor %}
        </nav>
    </div>
    <div class="container">
        {% for a in articles %}
        <div class="card">
            <img src="{{ a.get('img_url') or logo }}" class="card-img" onerror="this.src='{{ logo }}'">
            <div class="card-body">
                <div class="card-tag">{{ (a.get('categorie') or 'INFO')|upper }}</div>
                <h2 class="card-title">{{ a.get('titre') }}</h2>
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
    content = """
    <div class="container">
        <img src="{{ art.get('img_url') or logo }}" style="width:100%; border-radius:24px; margin-bottom:20px;">
        <h1 style="font-size:28px;">{{ art.get('titre') }}</h1>
        <div style="white-space:pre-wrap; font-size:18px; color:#d1d1d6;">{{ art.get('texte') }}</div>
        <br><a href="/" class="btn" style="background:#3a3a3c;">RETOUR</a>
    </div>
    """
    return render_template_string(BASE_HTML.replace('{% block content %}{% endblock %}', content), title=art.get('titre'), logo=LOGO_URL, art=art)

@app.route(f'/{ADMIN_PATH}', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST' and 'password' in request.form:
        if request.form['password'] == ADMIN_PASS_ENV:
            session['logged_in'] = True
            return redirect(f'/{ADMIN_PATH}')
        return "Accès refusé."

    if not session.get('logged_in'):
        login_ui = '<div class="container" style="padding-top:100px; text-align:center;"><h3>Accès Admin</h3><form method="post"><input type="password" name="password" placeholder="Mot de passe" required><button type="submit" class="btn">ENTRER</button></form></div>'
        return render_template_string(BASE_HTML.replace('{% block content %}{% endblock %}', login_ui), title="Connexion", logo=LOGO_URL)

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
            "ts": int(time.time())
        }
        if art_id: requests.patch(f"{SUPABASE_URL}?id=eq.{art_id}", headers=HEADERS, json=data)
        else: requests.post(SUPABASE_URL, headers=HEADERS, json=data)
        return redirect(f'/{ADMIN_PATH}')

    r = requests.get(SUPABASE_URL, headers=HEADERS, params={"order": "ts.desc"})
    all_arts = r.json() if isinstance(r.json(), list) else []
    
    admin_ui = """
    <div class="container">
        <h3>RÉDACTION</h3>
        <form method="post">
            <input type="hidden" name="id" value="{{ art_edit.get('id') if art_edit else '' }}">
            <input name="titre" placeholder="Titre" value="{{ art_edit.get('titre') if art_edit else '' }}" required>
            <select name="categorie">
                {% for cat in ["Tech", "Science", "IA", "Espace", "Santé", "Sport"] %}
                <option value="{{cat}}" {% if art_edit and art_edit.get('categorie') == cat %}selected{% endif %}>{{cat}}</option>
                {% endfor %}
            </select>
            <input name="img_url" placeholder="URL Image" value="{{ art_edit.get('img_url') if art_edit else '' }}" required>
            <textarea name="texte" rows="8" placeholder="Contenu..." required>{{ art_edit.get('texte') if art_edit else '' }}</textarea>
            <button type="submit" class="btn">ENREGISTRER</button>
        </form>
        <div style="margin-top:30px;">
            {% for a in all_arts %}
            <div style="background:#1c1c1e; padding:15px; border-radius:15px; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center; border:0.5px solid #333;">
                <span style="font-size:14px;">{{ a.get('titre')[:35] }}...</span>
                <a href="/{{ admin_path }}?edit={{ a.get('id') }}" style="color:var(--blue); font-weight:700; text-decoration:none;">EDIT</a>
            </div>
            {% endfor %}
        </div>
    </div>
    """
    return render_template_string(BASE_HTML.replace('{% block content %}{% endblock %}', admin_ui), 
                                title="Admin", logo=LOGO_URL, art_edit=article_to_edit, all_arts=all_arts, admin_path=ADMIN_PATH)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

