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

# --- DESIGN GLOBAL CORRIGÉ ---
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
        :root { --blue: #00d2ff; --purple: #9d50bb; --dark: #050505; --gray: #1c1c1e; }
        body { font-family: 'DM Sans', sans-serif; margin: 0; background: var(--dark); color: #fff; overflow-x: hidden; }
        
        /* HEADER */
        header { 
            background: rgba(0, 0, 0, 0.95); backdrop-filter: blur(10px);
            padding: 15px 20px; display: flex; align-items: center; justify-content: space-between;
            border-bottom: 0.5px solid #333; position: sticky; top:0; z-index: 1000; 
        }
        .menu-btn { background: none; border: none; color: white; font-size: 30px; cursor: pointer; }
        .logo { font-size: 1.5rem; font-weight: 800; color: #fff; text-decoration: none; font-family: 'Bebas Neue', sans-serif; }
        .logo span { color: var(--blue); }

        /* SIDEBAR CACHÉE PAR DÉFAUT */
        .sidebar {
            position: fixed; top: 0; left: -100%; width: 280px; height: 100%;
            background: #111; z-index: 3000; transition: 0.4s ease;
            padding: 60px 25px; box-shadow: 10px 0 50px rgba(0,0,0,0.9);
        }
        .sidebar.active { left: 0; }
        .sidebar-close { position: absolute; top: 15px; right: 20px; font-size: 40px; cursor: pointer; color: #666; }
        .sidebar-link { 
            display: block; color: white; text-decoration: none; font-size: 1.6rem; 
            padding: 20px 0; border-bottom: 1px solid #222; font-family: 'Bebas Neue', sans-serif;
        }

        /* OVERLAY */
        .overlay { 
            position: fixed; inset: 0; background: rgba(0,0,0,0.85); 
            display: none; z-index: 2500; backdrop-filter: blur(4px);
        }
        .overlay.active { display: block; }

        /* CARTES ET CONTENU */
        .container { width: 92%; max-width: 600px; margin: auto; padding: 20px 0; }
        .card { background: var(--gray); border-radius: 24px; overflow: hidden; margin-bottom: 25px; border: 0.5px solid #333; }
        .card-img { width: 100%; height: 250px; object-fit: cover; }
        .card-body { padding: 20px; }
        .btn { display: block; background: linear-gradient(135deg, var(--blue), var(--purple)); color: #fff; padding: 16px; text-align: center; border-radius: 18px; text-decoration: none; font-weight: 700; margin-top: 15px; }
        
        /* Nav catégories */
        .nav-container { background: #000; padding: 10px 0; border-bottom: 0.5px solid #222; }
        .nav-cats { display: flex; gap: 10px; overflow-x: auto; padding: 0 15px; }
        .cat { color: #888; text-decoration: none; font-size: 0.8rem; padding: 8px 15px; border-radius: 20px; background: #1c1c1e; white-space: nowrap; }
        .cat.active { color: #fff; background: var(--blue); }
    </style>
</head>
<body>
    <div class="overlay" id="overlay" onclick="toggleMenu()"></div>
    
    <div class="sidebar" id="sidebar">
        <div class="sidebar-close" onclick="toggleMenu()">×</div>
        <div class="sidebar-nav">
            <a href="/" class="sidebar-link" onclick="toggleMenu()">ACCUEIL</a>
            <a href="mailto:{{ email }}" class="sidebar-link">NOUS CONTACTER</a>
            <a href="/?cat=Tech" class="sidebar-link" onclick="toggleMenu()">TECH & IA</a>
            <p style="margin-top:50px; color:#444; font-size:10px;">METTABYTE © 2026</p>
        </div>
    </div>

    <header>
        <button class="menu-btn" onclick="toggleMenu()">☰</button>
        <a href="/" class="logo">METTA<span>BYTE</span></a>
        <div style="width:30px;"></div>
    </header>

    {% block content %}{% endblock %}

    <script>
        function toggleMenu() {
            const sb = document.getElementById('sidebar');
            const ov = document.getElementById('overlay');
            sb.classList.toggle('active');
            ov.classList.toggle('active');
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
    
    cats = ["Tous", "Science", "Tech", "IA", "Espace"]
    content = """
    <div class="nav-container"><nav class="nav-cats">
        {% for c in cats %}<a href="/?cat={{c}}" class="cat {% if c == active_cat %}active{% endif %}">{{c}}</a>{% endfor %}
    </nav></div>
    <div class="container">
        {% for a in articles %}
        <div class="card">
            <img src="{{ a.get('img_url') or logo }}" class="card-img" onerror="this.src='{{ logo }}'">
            <div class="card-body">
                <h2 style="margin:0; font-size:20px;">{{ a.get('titre') }}</h2>
                <a href="/article/{{ a.get('id') }}" class="btn">LIRE L'ARTICLE</a>
            </div>
        </div>
        {% endfor %}
    </div>
    """
    return render_template_string(BASE_HTML.replace('{% block content %}{% endblock %}', content), 
                                title="METTABYTE", logo=LOGO_URL, cats=cats, active_cat=cat_filter, articles=articles, email=MY_EMAIL)

@app.route('/article/<id>')
def read_article(id):
    try:
        r = requests.get(f"{SUPABASE_URL}?id=eq.{id}", headers=HEADERS)
        art = r.json()[0]
    except: return redirect('/')
    
    content = """
    <div class="container">
        <img src="{{ art.get('img_url') }}" style="width:100%; border-radius:20px; margin-bottom:20px;">
        <h1 style="font-family:'Bebas Neue'; font-size:3rem; line-height:1;">{{ art.get('titre') }}</h1>
        <div style="font-size:1.1rem; color:#ccc; margin-top:20px;">
            {{ art.get('texte')|safe }}
        </div>
        <a href="/" class="btn" style="background:#333; margin-top:40px;">RETOUR</a>
    </div>
    """
    return render_template_string(BASE_HTML.replace('{% block content %}{% endblock %}', content), 
                                title=art.get('titre'), logo=LOGO_URL, art=art, email=MY_EMAIL)

@app.route('/ads.txt')
def ads_txt():
    return "google.com, pub-2847151888169934, DIRECT, f08c47fec0942fa0", 200, {'Content-Type': 'text/plain'}

@app.route(f'/{ADMIN_PATH}', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST' and 'password' in request.form:
        if request.form['password'] == ADMIN_PASS_ENV:
            session['logged_in'] = True
            return redirect(f'/{ADMIN_PATH}')
    if not session.get('logged_in'):
        return render_template_string(BASE_HTML.replace('{% block content %}{% endblock %}', '<div class="container"><form method="post"><input type="password" name="password" placeholder="Pass"><button type="submit" class="btn">ENTRER</button></form></div>'), email=MY_EMAIL)
    # Formulaire simplifié pour test
    return "Espace Admin Connecté"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

