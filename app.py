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
        :root { --blue: #00d2ff; --purple: #9d50bb; --dark: #050505; --gray: #1c1c1e; --white: #f5f0eb; --red: #e63022; }
        body { font-family: 'DM Sans', sans-serif; margin: 0; background: var(--dark); color: #fff; line-height: 1.6; }
        header { background: #000; padding: 15px; text-align: center; border-bottom: 1px solid #333; position: sticky; top:0; z-index:1000; }
        .logo { font-size: 1.6rem; font-weight: 800; color: #fff; text-decoration: none; font-family: 'Bebas Neue', sans-serif; }
        .logo span { color: var(--blue); }
        .container { width: 92%; max-width: 800px; margin: auto; padding: 20px 0; }
        input, textarea, select { width: 100%; padding: 15px; margin: 10px 0; background: #1c1c1e; border: 1px solid #333; color: #fff; border-radius: 10px; box-sizing: border-box; font-size: 16px; }
        .btn { display: block; background: linear-gradient(135deg, var(--blue), var(--purple)); color: #fff; padding: 16px; text-align: center; border-radius: 15px; text-decoration: none; font-weight: 700; border: none; width: 100%; cursor: pointer; margin-top: 10px; }
        .card { background: var(--gray); border-radius: 20px; overflow: hidden; margin-bottom: 25px; border: 1px solid #333; text-decoration: none; display: block; color: inherit; }
        .card-img { width: 100%; height: 250px; object-fit: cover; }
        .card-body { padding: 20px; }
        /* Styles pour l'article */
        .article-hero { height: 50vh; background-size: cover; background-position: center; display: flex; align-items: flex-end; padding: 40px 20px; position: relative; }
        .article-hero::after { content: ''; position: absolute; inset: 0; background: linear-gradient(to top, #000, transparent); }
        .hero-text { position: relative; z-index: 2; }
        .article-content { padding: 20px; max-width: 700px; margin: auto; color: #ccc; }
        .stat-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px; margin: 20px 0; text-align: center; }
        .stat-item { background: #111; padding: 20px; border-radius: 10px; border: 1px solid #333; }
        .stat-number { font-size: 2rem; color: var(--red); font-family: 'Bebas Neue'; }
        .big-quote { font-size: 1.5rem; border-left: 4px solid var(--blue); padding-left: 20px; margin: 30px 0; font-style: italic; }
        .diff-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 20px 0; }
        .diff-card { padding: 15px; border-radius: 10px; border: 1px solid #333; font-size: 0.9rem; }
        @media (max-width: 600px) { .diff-grid { grid-template-columns: 1fr; } }
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
    try:
        r = requests.get(SUPABASE_URL, headers=HEADERS, params={"order": "ts.desc"})
        articles = r.json() if isinstance(r.json(), list) else []
    except: articles = []
    
    content = """
    <div class="container">
        {% for a in articles %}
        <a href="/article/{{ a.id }}" class="card">
            <img src="{{ a.img_url or logo }}" class="card-img">
            <div class="card-body">
                <div style="color:var(--blue); font-size:12px; font-weight:700;">{{ a.categorie }}</div>
                <h2 style="margin:5px 0;">{{ a.titre }}</h2>
                <div class="btn" style="padding:10px; width:150px;">LIRE</div>
            </div>
        </a>
        {% endfor %}
    </div>
    """
    return render_template_string(BASE_HTML.replace('{% block content %}{% endblock %}', content), title="METTABYTE", logo=LOGO_URL, articles=articles)

@app.route('/article/<id>')
def read_article(id):
    try:
        r = requests.get(SUPABASE_URL + "?id=eq." + str(id), headers=HEADERS)
        art = r.json()[0]
    except: return redirect('/')
    content = """
    <div class="article-hero" style="background-image: url('{{ art.img_url }}')">
        <div class="hero-text"><h1 style="font-family:'Bebas Neue'; font-size:3rem; margin:0;">{{ art.titre }}</h1></div>
    </div>
    <div class="article-content">
        {{ art.texte|safe }}
        <a href="/" class="btn" style="background:#222; margin-top:40px;">RETOUR</a>
    </div>
    """
    return render_template_string(BASE_HTML.replace('{% block content %}{% endblock %}', content), title=art['titre'], logo=LOGO_URL, art=art)

@app.route('/' + ADMIN_PATH, methods=['GET', 'POST'])
def admin():
    if request.method == 'POST' and 'password' in request.form:
        if request.form['password'] == ADMIN_PASS_ENV:
            session['logged_in'] = True
    
    if not session.get('logged_in'):
        return render_template_string(BASE_HTML.replace('{% block content %}{% endblock %}', '<div class="container" style="text-align:center;"><form method="post"><h3>Admin Access</h3><input type="password" name="password" placeholder="Pass"><button type="submit" class="btn">LOG IN</button></form></div>'), title="Admin", logo=LOGO_URL)

    if request.method == 'POST' and 'titre' in request.form:
        data = {"titre": request.form['titre'], "texte": request.form['texte'], "img_url": request.form['img_url'], "categorie": request.form['categorie'], "ts": int(time.time())}
        requests.post(SUPABASE_URL, headers=HEADERS, json=data)
        return redirect('/' + ADMIN_PATH)

    admin_form = """
    <div class="container">
        <h2>STUDIO DE PUBLICATION</h2>
        <form method="post">
            <input name="titre" placeholder="Titre" required>
            <input name="img_url" placeholder="Lien image" required>
            <select name="categorie"><option>Tech</option><option>IA</option><option>Science</option></select>
            <textarea name="texte" rows="15" placeholder="Contenu HTML" required></textarea>
            <button type="submit" class="btn">PUBLIER L'ARTICLE</button>
        </form>
    </div>
    """
    return render_template_string(BASE_HTML.replace('{% block content %}{% endblock %}', admin_form), title="Admin Panel", logo=LOGO_URL)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

