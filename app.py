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
    <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:ital,wght@0,300;0,400;0,700;1,300&family=Playfair+Display:ital@1&display=swap" rel="stylesheet">
    <style>
        :root { --blue: #00d2ff; --purple: #9d50bb; --dark: #050505; --gray: #1c1c1e; --white: #f5f0eb; --red: #e63022; }
        
        body { 
            font-family: 'DM Sans', sans-serif; 
            margin: 0; background: var(--dark); color: #fff; line-height: 1.6; 
            -webkit-font-smoothing: antialiased; overflow-x: hidden; 
        }

        header { 
            background: rgba(0, 0, 0, 0.85); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); 
            padding: 15px; text-align: center; border-bottom: 0.5px solid #333; position: sticky; top:0; z-index:1000; 
        }

        .logo { font-size: 1.6rem; font-weight: 800; color: #fff; text-decoration: none; letter-spacing: -0.5px; font-family: 'Bebas Neue', sans-serif; }
        .logo span { color: var(--blue); }

        /* Navigation Style iPhone */
        .nav-container { background: rgba(0,0,0,0.3); border-bottom: 0.5px solid #222; padding: 12px 0; }
        .nav-cats { display: flex; gap: 12px; overflow-x: auto; padding: 0 20px; scroll-behavior: smooth; -webkit-overflow-scrolling: touch; }
        .nav-cats::-webkit-scrollbar { display: none; }
        .cat { color: #8e8e93; text-decoration: none; font-size: 0.9rem; font-weight: 600; padding: 8px 18px; white-space: nowrap; border-radius: 20px; background: var(--gray); transition: all 0.2s ease; }
        .cat.active { color: #fff; background: linear-gradient(135deg, var(--blue), var(--purple)); }

        /* LECTURE ARTICLE - LARGEUR OPTIMISÉE */
        .article-body .hero { 
            min-height: 65vh; display: flex; flex-direction: column; justify-content: flex-end; 
            padding: 4rem 5%; position: relative; 
            background-size: cover; background-position: center 20%; background-repeat: no-repeat;
        }
        .article-body .hero::after { content: ''; position: absolute; inset: 0; background: linear-gradient(to top, var(--dark) 5%, transparent 95%); }
        
        .hero-content { position: relative; z-index: 2; max-width: 1000px; margin: 0 auto; width: 100%; }
        .hero-tag { color: var(--red); font-size: 0.85rem; text-transform: uppercase; letter-spacing: 3px; margin-bottom: 1rem; font-weight: 700; }
        .hero-title { font-family: 'Bebas Neue', sans-serif; font-size: clamp(3rem, 10vw, 7rem); line-height: 0.85; margin: 0; }
        
        .article-content { 
            max-width: 950px; /* Élargi pour éviter l'étroitesse */
            margin: 0 auto; 
            padding: 3rem 20px; 
            font-size: 1.15rem;
        }

        /* Images dans l'article */
        .article-content img {
            max-width: 100%; height: auto; border-radius: 16px; margin: 2.5rem 0; display: block;
        }

        .article-content h2 { font-family: 'Bebas Neue', sans-serif; font-size: 3rem; color: var(--white); margin: 4rem 0 1.5rem; display: flex; align-items: center; gap: 1rem; }
        .article-content h2::before { content: ''; width: 40px; height: 4px; background: var(--red); }
        .article-content p { color: #c8c0b8; margin-bottom: 1.8rem; font-weight: 300; }

        /* Composants Magazine */
        .big-quote { font-family: 'Bebas Neue', sans-serif; font-size: clamp(2.5rem, 7vw, 4.5rem); border-left: 6px solid var(--red); padding-left: 2rem; margin: 4rem 0; line-height: 1; }
        .highlight { background: rgba(230, 48, 34, 0.05); border-left: 4px solid var(--red); padding: 2.5rem; margin: 3rem 0; font-family: 'Playfair Display', serif; font-style: italic; font-size: 1.3rem; border-radius: 0 12px 12px 0; }
        
        .diff-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin: 3rem 0; }
        .diff-card { padding: 2rem; border-radius: 12px; border: 1px solid #333; }
        .diff-card.bad { background: rgba(230, 48, 34, 0.08); border-color: var(--red); }
        .diff-card.good { background: rgba(80, 200, 120, 0.08); border-color: #50c878; }
        
        .stat-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1px; background: #333; margin: 4rem 0; border: 1px solid #333; border-radius: 12px; overflow: hidden; }
        .stat-item { background: var(--dark); padding: 2.5rem 1rem; text-align: center; }
        .stat-number { font-family: 'Bebas Neue', sans-serif; font-size: 3.5rem; color: var(--red); line-height: 1; }
        .stat-label { font-size: 0.75rem; text-transform: uppercase; color: #888; margin-top: 8px; letter-spacing: 1px; }

        /* Style Accueil Cards */
        .container { width: 92%; max-width: 600px; margin: auto; padding: 20px 0; }
        .card { background: var(--gray); border-radius: 24px; overflow: hidden; margin-bottom: 25px; border: 0.5px solid #333; transition: transform 0.2s ease; }
        .card:active { transform: scale(0.97); }
        .card-img { width: 100%; height: 260px; object-fit: cover; }
        .card-body { padding: 22px; }
        .card-tag { color: var(--blue); font-size: 11px; font-weight: 700; text-transform: uppercase; margin-bottom: 6px; letter-spacing: 1px; }
        .card-title { margin: 6px 0; font-size: 22px; font-weight: 700; line-height: 1.2; }
        .btn { display: block; background: linear-gradient(135deg, var(--blue), var(--purple)); color: #fff; padding: 16px; text-align: center; border-radius: 18px; text-decoration: none; font-weight: 700; margin-top: 15px; border:none; width:100%; box-sizing:border-box; cursor:pointer; }
        
        @media (max-width: 768px) { 
            .diff-grid, .stat-row { grid-template-columns: 1fr; } 
            .article-content { padding: 2rem 15px; }
            .hero-title { font-size: 3.5rem; }
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
    <div class="article-body">
        <section class="hero" style="background-image: url('{{ art.get('img_url') or logo }}')">
            <div class="hero-content">
                <div class="hero-tag">{{ art.get('categorie') }}</div>
                <h1 class="hero-title">{{ art.get('titre') }}</h1>
            </div>
        </section>
        <div class="article-content">
            {{ art.get('texte')|safe }}
            <div style="margin-top: 50px; border-top: 1px solid #222; padding-top: 30px;">
                <a href="/" class="btn" style="background:#3a3a3c; width: fit-content; padding: 12px 40px; display: inline-block;">RETOUR À L'ACCUEIL</a>
            </div>
        </div>
    </div>
    """
    return render_template_string(BASE_HTML.replace('{% block content %}{% endblock %}', content), 
                                title=art.get('titre'), logo=LOGO_URL, art=art)

@app.route(f'/{ADMIN_PATH}', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST' and 'password' in request.form:
        if request.form['password'] == ADMIN_PASS_ENV:
            session['logged_in'] = True
            return redirect(f'/{ADMIN_PATH}')
        return "Accès refusé."

    if not session.get('logged_in'):
        login_ui = '<div class="container" style="padding-top:100px; text-align:center;"><form method="post"><input type="password" name="password" placeholder="Mot de passe" required><button type="submit" class="btn">ENTRER</button></form></div>'
        return render_template_string(BASE_HTML.replace('{% block content %}{% endblock %}', login_ui), title="Connexion", logo=LOGO_URL)

    edit_id = request.args.get('edit')
    art_edit = None
    if edit_id:
        r = requests.get(f"{SUPABASE_URL}?id=eq.{edit_id}", headers=HEADERS)
        if r.json(): art_edit = r.json()[0]

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
        <h3 style="font-family: 'Bebas Neue'; font-size: 2rem;">DESIGN STUDIO</h3>
        <form method="post">
            <input type="hidden" name="id" value="{{ art_edit.get('id') if art_edit else '' }}">
            <input name="titre" placeholder="Titre de l'article" value="{{ art_edit.get('titre') if art_edit else '' }}" required>
            <select name="categorie">
                {% for cat in ["Tech", "Science", "IA", "Espace", "Santé", "Sport"] %}
                <option value="{{cat}}" {% if art_edit and art_edit.get('categorie') == cat %}selected{% endif %}>{{cat}}</option>
                {% endfor %}
            </select>
            <input name="img_url" placeholder="URL Image (Fond Hero)" value="{{ art_edit.get('img_url') if art_edit else '' }}" required>
            <textarea name="texte" rows="20" placeholder="Insérez votre code HTML Magazine ici...">{{ art_edit.get('texte') if art_edit else '' }}</textarea>
            <button type="submit" class="btn">PUBLIER L'ÉDITION</button>
        </form>
        <div style="margin-top:30px;">
            {% for a in all_arts %}
            <div style="background:#1c1c1e; padding:12px; border-radius:12px; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center; border:0.5px solid #333;">
                <span style="font-size:13px; opacity: 0.8;">{{ a.get('titre')[:35] }}...</span>
                <a href="/{{ admin_path }}?edit={{ a.get('id') }}" style="color:var(--blue); font-weight:700; text-decoration:none; font-size:12px;">ÉDITER</a>
            </div>
            {% endfor %}
        </div>
    </div>
    """
    return render_template_string(BASE_HTML.replace('{% block content %}{% endblock %}', admin_ui), 
                                title="Admin", logo=LOGO_URL, art_edit=art_edit, all_arts=all_arts, admin_path=ADMIN_PATH)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

