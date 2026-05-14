import os
import requests
import time
from flask import Flask, render_template_string, request, redirect, url_for, Response

app = Flask(__name__)

# --- CONFIGURATION ---
# On garde les clés via Render car elles fonctionnent pour l'affichage
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# TEST : On écrit le chemin directement ici pour être sûr
ADMIN_PATH = "monadmin77" 

LOGO_URL = "https://i.ibb.co/GfZxNrFq/img-1778540891.png"
SITE_URL = "https://mettabyte.onrender.com"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# --- DESIGN HTML ---
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
        body { font-family: 'Segoe UI', sans-serif; margin: 0; background: var(--dark); color: #eee; }
        header { background: #000; padding: 20px; text-align: center; border-bottom: 1px solid #111; }
        .logo { font-size: 1.8rem; font-weight: 900; color: #fff; text-decoration: none; }
        .logo span { color: var(--blue); }
        .container { width: 92%; max-width: 700px; margin: auto; padding: 20px 0; }
        .btn { display: block; background: linear-gradient(135deg, var(--blue), var(--purple)); color: #fff; padding: 14px; text-align: center; border-radius: 12px; text-decoration: none; font-weight: bold; border:none; width:100%; cursor:pointer; }
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
    try:
        r = requests.get(SUPABASE_URL, headers=HEADERS, params={"order": "ts.desc"})
        articles = r.json()
    except: articles = []
    
    content = """
    <div class="container">
        {% for a in articles %}
        <div style="background:#111; border-radius:15px; margin-bottom:20px; border:1px solid #222; overflow:hidden;">
            <img src="{{ a.get('img_url') or logo }}" style="width:100%; height:200px; object-fit:cover;">
            <div style="padding:15px;">
                <h2 style="margin:0 0 10px 0;">{{ a.get('titre') }}</h2>
                <a href="/article/{{ a.get('id') }}" class="btn">LIRE</a>
            </div>
        </div>
        {% endfor %}
    </div>
    """
    return render_template_string(BASE_HTML.replace('{% block content %}{% endblock %}', content), 
                                title="METTABYTE", logo=LOGO_URL, articles=articles)

@app.route('/article/<id>')
def read_article(id):
    try:
        r = requests.get(f"{SUPABASE_URL}?id=eq.{id}", headers=HEADERS)
        art = r.json()[0]
    except: return redirect('/')
    content = f'<div class="container"><h1>{art.get("titre")}</h1><div style="white-space:pre-wrap;">{art.get("texte")}</div><br><a href="/" class="btn">RETOUR</a></div>'
    return render_template_string(BASE_HTML.replace('{% block content %}{% endblock %}', content), title=art.get('titre'), logo=LOGO_URL)

# --- ROUTE ADMIN FIXÉE ---
@app.route('/monadmin77', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        data = {
            "titre": request.form['titre'],
            "resume": request.form['texte'][:100],
            "texte": request.form['texte'],
            "img_url": request.form['img_url'],
            "categorie": request.form['categorie'],
            "mots_cles": request.form.get('mots_cles', ''),
            "ts": int(time.time())
        }
        requests.post(SUPABASE_URL, headers=HEADERS, json=data)
        return redirect('/')

    r = requests.get(SUPABASE_URL, headers=HEADERS, params={"order": "ts.desc"})
    all_arts = r.json() if r.status_code == 200 else []
    
    admin_ui = """
    <div class="container">
        <h3>NOUVEL ARTICLE</h3>
        <form method="post">
            <input name="titre" placeholder="Titre" required>
            <input name="mots_cles" placeholder="Mots-clés">
            <select name="categorie">
                <option value="Tech">Tech</option>
                <option value="Science">Science</option>
            </select>
            <input name="img_url" placeholder="URL Image" required>
            <textarea name="texte" rows="10" placeholder="Contenu" required></textarea>
            <button type="submit" class="btn">PUBLIER</button>
        </form>
    </div>
    """
    return render_template_string(BASE_HTML.replace('{% block content %}{% endblock %}', admin_ui), title="Admin", logo=LOGO_URL)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

