import os
import requests
import time
from flask import Flask, render_template_string, request, redirect, url_for, Response

app = Flask(__name__)

# --- CONFIGURATION (CORRIGÉE AVEC TA CLÉ) ---
SUPABASE_URL = "https://xwzjlddgqwlrxgetahvp.supabase.co/rest/v1/articles"
# Voici ta clé corrigée intégrée ici :
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh3empsZGRncXdscnhnZXRhaHZwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk3MzY1NTQsImV4cCI6MjA4NTMxMjU1NH0.MsCgDKBz3jXrJ_dOcJ35koaLi-uBpNXoAoaFLAWDbkg"
LOGO_URL = "https://i.ibb.co/GfZxNrFq/img-1778540891.png"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

ADMIN_PATH = "moncode123"
SITE_URL = "https://mettabyte.onrender.com"

BASE_HTML = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>{{ title }}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="{{ logo }}">
    <link rel="apple-touch-icon" href="{{ logo }}">
    <style>
        :root { --blue: #00d2ff; --purple: #9d50bb; --dark: #050505; --red: #ff4b2b; }
        body { font-family: 'Segoe UI', sans-serif; margin: 0; background: var(--dark); color: #eee; line-height: 1.6; }
        header { background: #000; padding: 20px; text-align: center; border-bottom: 1px solid #111; position: sticky; top:0; z-index:100; }
        .logo { font-size: 1.8rem; font-weight: 900; color: #fff; text-decoration: none; letter-spacing: 2px; }
        .logo span { color: var(--blue); }
        .nav-cats { display: flex; gap: 15px; overflow-x: auto; padding: 15px; justify-content: center; background: #080808; border-bottom: 1px solid #111; }
        .cat { color: #888; text-decoration: none; font-size: 0.9rem; font-weight: bold; padding: 5px 10px; white-space: nowrap; }
        .cat.active { color: var(--blue); border-bottom: 2px solid var(--blue); }
        .container { width: 92%; max-width: 700px; margin: auto; padding: 20px 0; }
        .card { background: #111; border-radius: 15px; overflow: hidden; margin-bottom: 30px; border: 1px solid #222; }
        .card-img { width: 100%; height: 230px; object-fit: cover; background: #1a1a1a; }
        .card-body { padding: 20px; }
        .btn { display: block; background: linear-gradient(135deg, var(--blue), var(--purple)); color: #fff; padding: 14px; text-align: center; border-radius: 12px; text-decoration: none; font-weight: bold; margin-top: 10px; border:none; width:100%; box-sizing:border-box; cursor:pointer; }
        input, textarea, select { width: 100%; padding: 12px; margin: 8px 0; background: #000; border: 1px solid #333; color: #fff; border-radius: 8px; box-sizing: border-box; }
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
        articles = r.json()
    except: articles = []
    
    cats = ["Tous", "Science", "Tech", "Espace", "IA"]
    content = """
    <nav class="nav-cats">
        {% for c in cats %}
        <a href="/?cat={{c}}" class="cat {% if c == active_cat %}active{% endif %}">{{c}}</a>
        {% endfor %}
    </nav>
    <div class="container">
        {% for a in articles %}
        <div class="card">
            <img src="{{ a.get('img_url') or logo }}" class="card-img">
            <div class="card-body">
                <span style="color:var(--blue); font-size:12px; font-weight:bold;">{{ (a.get('categorie') or 'NEWS')|upper }}</span>
                <h2 style="margin: 10px 0; font-size: 22px;">{{ a.get('titre') }}</h2>
                <p style="color:#aaa; font-size:14px;">{{ a.get('resume') }}...</p>
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
        <img src="{{ art.get('img_url') or logo }}" style="width:100%; border-radius:15px; border:1px solid #222;">
        <h1 style="margin:20px 0;">{{ art.get('titre') }}</h1>
        <div style="white-space:pre-wrap; font-size:18px;">{{ art.get('texte') }}</div>
        <br><a href="/" class="btn" style="background:#222;">RETOUR</a>
    </div>
    """
    return render_template_string(BASE_HTML.replace('{% block content %}{% endblock %}', content), 
                                title=art.get('titre'), logo=LOGO_URL, art=art)

@app.route(f'/{ADMIN_PATH}/', methods=['GET', 'POST'])
def admin():
    edit_id = request.args.get('edit')
    article_to_edit = None
    if edit_id:
        r = requests.get(f"{SUPABASE_URL}?id=eq.{edit_id}", headers=HEADERS)
        if r.json(): article_to_edit = r.json()[0]
    
    if request.method == 'POST':
        action = request.form.get('action')
        art_id = request.form.get('id')
        if action == 'delete':
            requests.delete(f"{SUPABASE_URL}?id=eq.{art_id}", headers=HEADERS)
            return redirect(f'/{ADMIN_PATH}/')
        
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
        return redirect('/')

    r = requests.get(SUPABASE_URL, headers=HEADERS, params={"order": "ts.desc"})
    all_articles = r.json() if r.status_code == 200 else []
    
    admin_ui = """
    <div class="container">
        <form method="post">
            <input type="hidden" name="id" value="{{ art_edit.get('id') if art_edit else '' }}">
            <input name="titre" placeholder="Titre" value="{{ art_edit.get('titre') if art_edit else '' }}" required>
            <select name="categorie">
                {% for cat in ["Tech", "Science", "IA", "Espace"] %}
                <option value="{{cat}}" {% if art_edit and art_edit.get('categorie') == cat %}selected{% endif %}>{{cat}}</option>
                {% endfor %}
            </select>
            <input name="img_url" placeholder="URL Image" value="{{ art_edit.get('img_url') if art_edit else '' }}" required>
            <textarea name="texte" rows="10" placeholder="Contenu" required>{{ art_edit.get('texte') if art_edit else '' }}</textarea>
            <button type="submit" class="btn">ENREGISTRER</button>
        </form>
        <hr style="margin:30px 0; border:1px solid #222;">
        {% for a in all_arts %}
        <div style="background:#111; padding:15px; border-radius:10px; margin-bottom:10px; border:1px solid #222;">
            <b>{{ a.get('titre') }}</b>
            <a href="/{{ admin_path }}/?edit={{ a.get('id') }}" style="color:var(--blue); margin-left:10px;">Modifier</a>
        </div>
        {% endfor %}
    </div>
    """
    return render_template_string(BASE_HTML.replace('{% block content %}{% endblock %}', admin_ui), 
                                title="Admin", logo=LOGO_URL, art_edit=article_to_edit, all_arts=all_articles, admin_path=ADMIN_PATH)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

