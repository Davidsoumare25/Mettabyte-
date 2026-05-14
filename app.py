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
MY_EMAIL = "mettabytesite@gmail.com"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# --- DESIGN GLOBAL ---
BASE_HTML = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>{{ title }}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <link rel="icon" href="{{ logo }}">
    <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@400;700&display=swap" rel="stylesheet">
    
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-2847151888169934" crossorigin="anonymous"></script>

    <style>
        :root { --blue: #00d2ff; --purple: #9d50bb; --dark: #050505; --gray: #1c1c1e; --white: #f5f0eb; --red: #e63022; }
        body { font-family: 'DM Sans', sans-serif; margin: 0; background: var(--dark); color: #fff; line-height: 1.6; overflow-x: hidden; }
        
        header { 
            background: rgba(0, 0, 0, 0.9); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
            padding: 15px 20px; display: flex; align-items: center; justify-content: space-between;
            border-bottom: 0.5px solid #333; position: sticky; top:0; z-index:1000; 
        }

        .menu-btn { background: none; border: none; color: white; font-size: 28px; cursor: pointer; padding: 0; line-height: 1; }
        .logo { font-size: 1.6rem; font-weight: 800; color: #fff; text-decoration: none; font-family: 'Bebas Neue', sans-serif; letter-spacing: 1px; }
        .logo span { color: var(--blue); }
        .placeholder-right { width: 28px; }

        .sidebar {
            position: fixed; top: 0; left: -300px; width: 300px; height: 100%;
            background: var(--gray); z-index: 2000; transition: 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            padding: 60px 30px; box-shadow: 15px 0 50px rgba(0,0,0,0.8);
        }
        .sidebar.active { left: 0; }
        .sidebar-close { position: absolute; top: 20px; right: 25px; font-size: 35px; cursor: pointer; color: #666; }
        .sidebar-link { 
            display: block; color: white; text-decoration: none; font-size: 1.5rem; 
            padding: 18px 0; border-bottom: 0.5px solid #333; font-family: 'Bebas Neue', sans-serif; letter-spacing: 2px;
            transition: 0.2s;
        }
        .sidebar-link:hover { color: var(--blue); padding-left: 10px; }
        
        .overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.8); display: none; z-index: 1500; backdrop-filter: blur(4px); }
        .overlay.active { display: block; }

        /* Contenu & Cartes */
        .ad-slot { width: 100%; margin: 30px auto; min-height: 120px; display: flex; align-items: center; justify-content: center; background: rgba(255,255,255,0.02); color: #444; font-size: 10px; border: 1px dashed #333; border-radius: 12px; }
        .nav-container { background: rgba(0,0,0,0.2); border-bottom: 0.5px solid #222; padding: 12px 0; }
        .nav-cats { display: flex; gap: 12px; overflow-x: auto; padding: 0 20px; -webkit-overflow-scrolling: touch; }
        .nav-cats::-webkit-scrollbar { display: none; }
        .cat { color: #8e8e93; text-decoration: none; font-size: 0.9rem; font-weight: 700; padding: 10px 22px; border-radius: 25px; background: #1c1c1e; white-space: nowrap; transition: 0.3s; }
        .cat.active { color: #fff; background: linear-gradient(135deg, var(--blue), var(--purple)); box-shadow: 0 4px 15px rgba(0, 210, 255, 0.3); }

        .container { width: 92%; max-width: 650px; margin: auto; padding: 20px 0; }
        .card { background: #151517; border-radius: 28px; overflow: hidden; margin-bottom: 30px; border: 1px solid #222; transition: 0.3s; }
        .card-img { width: 100%; height: 280px; object-fit: cover; }
        .card-body { padding: 25px; }
        .card-tag { color: var(--blue); font-size: 12px; font-weight: 800; text-transform: uppercase; margin-bottom: 8px; }
        .card-title { margin: 8px 0; font-size: 24px; font-weight: 700; line-height: 1.2; }
        .btn { display: block; background: linear-gradient(135deg, var(--blue), var(--purple)); color: #fff; padding: 18px; text-align: center; border-radius: 20px; text-decoration: none; font-weight: 700; margin-top: 15px; border:none; cursor:pointer; }

        /* Lecture Article */
        .article-body .hero { min-height: 65vh; display: flex; flex-direction: column; justify-content: flex-end; padding: 5rem 6%; position: relative; background-size: cover; background-position: center; }
        .article-body .hero::after { content: ''; position: absolute; inset: 0; background: linear-gradient(to top, var(--dark) 8%, transparent 92%); }
        .hero-content { position: relative; z-index: 2; max-width: 950px; margin: 0 auto; width: 100%; }
        .hero-title { font-family: 'Bebas Neue', sans-serif; font-size: clamp(2.8rem, 9vw, 5.5rem); line-height: 0.95; margin: 0; text-transform: uppercase; }
        .article-content { max-width: 950px; margin: 0 auto; padding: 3rem 22px; font-size: 1.2rem; color: #d1d1d6; }
    </style>
</head>
<body>
    <div class="overlay" id="overlay" onclick="toggleMenu()"></div>
    
    <div class="sidebar" id="sidebar">
        <div class="sidebar-close" onclick="toggleMenu()">×</div>
        <div class="sidebar-nav">
            <a href="/" class="sidebar-link" onclick="toggleMenu()">ACCUEIL</a>
            <a href="mailto:{{ email }}" class="sidebar-link">NOUS CONTACTER</a>
            <a href="/article/POLITIQUE_ID" class="sidebar-link">CONFIDENTIALITÉ</a>
            <p style="margin-top:60px; font-size: 11px; color: #444; letter-spacing: 1px;">METTABYTE DIGITAL MEDIA © 2026</p>
        </div>
    </div>

    <header>
        <button class="menu-btn" onclick="toggleMenu()">☰</button>
        <a href="/" class="logo">METTA<span>BYTE</span></a>
        <div class="placeholder-right"></div>
    </header>

    {% block content %}{% endblock %}

    <script>
        function toggleMenu() {
            document.getElementById('sidebar').classList.toggle('active');
            document.getElementById('overlay').classList.toggle('active');
        }
    </script>
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
    <div class="nav-container"><nav class="nav-cats">
        {% for c in cats %}<a href="/?cat={{c}}" class="cat {% if c == active_cat %}active{% endif %}">{{c}}</a>{% endfor %}
    </nav></div>
    <div class="container">
        {% for a in articles %}
        <div class="card">
            <img src="{{ a.get('img_url') or logo }}" class="card-img" onerror="this.src='{{ logo }}'">
            <div class="card-body">
                <div class="card-tag">{{ (a.get('categorie') or 'INFO')|upper }}</div>
                <h2 class="card-title">{{ a.get('titre') }}</h2>
                <a href="/article/{{ a.get('id') }}" class="btn">LIRE L'ÉDITION</a>
            </div>
        </div>
        {% endfor %}
    </div>
    """
    # Note : Remplace POLITIQUE_ID par l'ID réel de ton article de confidentialité si tu le connais
    return render_template_string(BASE_HTML.replace('{% block content %}{% endblock %}', content), 
                                title="METTABYTE | Future Tech", logo=LOGO_URL, cats=cats, active_cat=cat_filter, articles=articles, email=MY_EMAIL)

@app.route('/article/<id>')
def read_article(id):
    try:
        r = requests.get(f"{SUPABASE_URL}?id=eq.{id}", headers=HEADERS)
        art = r.json()[0]
    except: return redirect('/')
    
    content = """
    <div class="article-body">
        <section class="hero" style="background-image: url('{{ art.get('img_url') or logo }}')">
            <div class="hero-content">
                <h1 class="hero-title">{{ art.get('titre') }}</h1>
            </div>
        </section>
        <div class="article-content">
            <div class="ad-slot">PUBLICITÉ NATIVE</div>
            {{ art.get('texte')|safe }}
            <div class="ad-slot">PUBLICITÉ NATIVE</div>
            <div style="margin-top: 60px; border-top: 1px solid #222; padding-top: 30px;">
                <a href="/" class="btn" style="background:#2c2c2e; width: fit-content; padding: 12px 40px; display: inline-block;">RETOUR À L'ACCUEIL</a>
            </div>
        </div>
    </div>
    """
    return render_template_string(BASE_HTML.replace('{% block content %}{% endblock %}', content), 
                                title=art.get('titre'), logo=LOGO_URL, art=art, email=MY_EMAIL)

@app.route('/ads.txt')
def ads_txt():
    return "google.com, pub-2847151888169934, DIRECT, f08c47fec0942fa0", 200, {'Content-Type': 'text/plain'}

# --- ADMIN SIMPLIFIÉ ---
@app.route(f'/{ADMIN_PATH}', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST' and 'password' in request.form:
        if request.form['password'] == ADMIN_PASS_ENV:
            session['logged_in'] = True
            return redirect(f'/{ADMIN_PATH}')
    if not session.get('logged_in'):
        return render_template_string(BASE_HTML.replace('{% block content %}{% endblock %}', '<div class="container"><form method="post"><input type="password" name="password" placeholder="Dashboard Pass"><button type="submit" class="btn">ACCÉDER</button></form></div>'), email=MY_EMAIL)

    if request.method == 'POST' and 'titre' in request.form:
        data = {"titre": request.form['titre'], "texte": request.form['texte'], "img_url": request.form['img_url'], "categorie": request.form['categorie'], "ts": int(time.time())}
        requests.post(SUPABASE_URL, headers=HEADERS, json=data)
        return redirect(f'/{ADMIN_PATH}')

    return render_template_string(BASE_HTML.replace('{% block content %}{% endblock %}', '<div class="container"><h3>STUDIO ÉDITORIAL</h3><form method="post"><input name="titre" placeholder="Titre de l\'article"><input name="img_url" placeholder="URL de l\'image Hero"><select name="categorie"><option>Tech</option><option>Science</option><option>IA</option><option>Espace</option></select><textarea name="texte" rows="15" placeholder="Contenu HTML..."></textarea><button type="submit" class="btn">PUBLIER</button></form></div>'), email=MY_EMAIL)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

