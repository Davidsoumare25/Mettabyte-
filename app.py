import os
import requests
import time
from flask import Flask, render_template_string, request, redirect, url_for, Response

app = Flask(__name__)

# --- CONFIGURATION ---
SUPABASE_URL = "https://xwzjlddgqwlrxgetahvp.supabase.co/rest/v1/articles"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh3empsZGRncXdscnhnZXRahvpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk3MzY1NTQsImV4cCI6MjA4NTMxMjU1NH0.MsCgDKBz3jXrJ_dOcJ35koaLi-uBpNXoAoaFLAWDbkg"
LOGO_URL = "https://i.ibb.co/GfZxNrFq/img-1778540891.png"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

ADMIN_PATH = "moncode123"
SITE_URL = "https://mettabyte.onrender.com"

# --- TEMPLATE DE BASE (POUR ÉVITER LES ERREURS DE SYNTAXE) ---
BASE_HTML = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>{{ title }}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="icon" href="{{ logo }}">
    <link rel="apple-touch-icon" href="{{ logo }}">
    <style>
        :root { --blue: #00d2ff; --purple: #9d50bb; --dark: #050505; --red: #ff4b2b; }
        body { font-family: 'Segoe UI', sans-serif; margin: 0; background: var(--dark); color: #eee; line-height: 1.6; }
        header { background: #000; padding: 20px; text-align: center; border-bottom: 1px solid #111; position: sticky; top:0; z-index:100; }
        .logo { font-size: 1.8rem; font-weight: 900; color: #fff; text-decoration: none; letter-spacing: 2px; }
        .logo span { color: var(--blue); }
        .nav-cats { display: flex; gap: 15px; overflow-x: auto; padding: 15px; justify-content: center; background: #080808; border-bottom: 1px solid #111; }
        .cat { color: #888; text-decoration: none; font-size: 0.9rem; font-weight: bold; padding: 5px 10px; }
        .cat.active { color: var(--blue); border-bottom: 2px solid var(--blue); }
        .container { width: 92%; max-width: 700px; margin: auto; padding: 20px 0; }
        .card { background: #111; border-radius: 15px; overflow: hidden; margin-bottom: 30px; border: 1px solid #222; }
        .card-img { width: 100%; height: 230px; object-fit: cover; }
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
    if cat_filter != 'Tous':
        params["categorie"] = f"eq.{cat_filter}"
    
    try:
        r = requests.get(SUPABASE_URL, headers=HEADERS, params=params)
        articles = r.json()
    except:
        articles = []
    
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
            <img src="{{ a.img_url }}" class="card-img">
            <div class="card-body">
                <span style="color:var(--blue); font-size:12px; font-weight:bold;">{{ a.categorie|upper }}</span>
                <h2 style="margin: 10px 0; font-size: 22px;">{{ a.titre }}</h2>
                <p style="color:#aaa; font-size:14px;">{{ a.resume }}...</p>
                <a href="/article/{{ a.id }}" class="btn">LIRE LA SUITE</a>
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
    except:
        return redirect('/')
    
    content = """
    <div class="container">
        <img src="{{ art.img_url }}" style="width:100%; border-radius:15px;">
        <h1 style="margin:20px 0;">{{ art.titre }}</h1>
        <div style="white-space:pre-wrap; font-size:18px;">{{ art.texte }}</div>
        <br><a href="/" class="btn" style="background:#222;">RETOUR</a>
    </div>
    """
    return render_template_string(BASE_HTML.replace('{% block content %}{% endblock %}', content), 
                                title=art['titre'], logo=LOGO_URL, art=art)

@app.route('/sitemap.xml')
def sitemap():
    try:
        r = requests.get(SUPABASE_URL, headers=HEADERS)
        articles = r.json()
    except:
        articles = []
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    xml += f'<url><loc>{SITE_URL}/</loc><priority>1.0</priority></url>\n'
    for a in articles:
        xml += f'<url><loc>{SITE_URL}/article/{a["id"]}</loc><priority>0.8</priority></url>\n'
    xml += '</urlset>'
    return Response(xml, mimetype='application/xml')

@app.route('/googleaa97466e31055bc3.html')
def google_verify():
    return "google-site-verification: googleaa97466e31055bc3.html"

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
        if art_id:
            requests.patch(f"{SUPABASE_URL}?id=eq.{art_id}", headers=HEADERS, json=data)
        else:
            requests.post(SUPABASE_URL, headers=HEADERS, json=data)
        return redirect('/')

    r = requests.get(SUPABASE_URL, headers=HEADERS, params={"order": "ts.desc"})
    all_articles = r.json() if r.status_code == 200 else []
    
    admin_ui = """
    <div class="container">
        <h3>{% if art_edit %}MODIFIER ARTICLE{% else %}NOUVEL ARTICLE{% endif %}</h3>
        <form method="post">
            <input type="hidden" name="id" value="{{ art_edit.id if art_edit else '' }}">
            <input name="titre" placeholder="Titre" value="{{ art_edit.titre if art_edit else '' }}" required>
            <select name="categorie">
                {% for cat in ["Tech", "Science", "IA", "Espace"] %}
                <option value="{{cat}}" {% if art_edit and art_edit.categorie == cat %}selected{% endif %}>{{cat}}</option>
                {% endfor %}
            </select>
            <input name="img_url" placeholder="URL Image" value="{{ art_edit.img_url if art_edit else '' }}" required>
            <textarea name="texte" rows="10" placeholder="Contenu" required>{{ art_edit.texte if art_edit else '' }}</textarea>
            <button type="submit" class="btn">ENREGISTRER</button>
        </form>
        <hr style="margin:30px 0; border:1px solid #222;">
        <h3>GÉRER LES ARTICLES</h3>
        {% for a in all_arts %}
        <div style="background:#111; padding:15px; border-radius:10px; margin-bottom:10px; border:1px solid #222;">
            <b>{{ a.titre }}</b>
            <div style="display:flex; gap:10px; margin-top:10px;">
                <a href="/{{ admin_path }}/?edit={{ a.id }}" class="btn" style="background:#333; font-size:12px;">MODIFIER</a>
                <form method="post" style="flex:1;">
                    <input type="hidden" name="id" value="{{ a.id }}">
                    <input type="hidden" name="action" value="delete">
                    <button type="submit" class="btn" style="background:var(--red); font-size:12px;" onclick="return confirm('Supprimer ?')">SUPPRIMER</button>
                </form>
            </div>
        </div>
        {% endfor %}
    </div>
    """
    return render_template_string(BASE_HTML.replace('{% block content %}{% endblock %}', admin_ui), 
                                title="Admin", logo=LOGO_URL, art_edit=article_to_edit, all_arts=all_articles, admin_path=ADMIN_PATH)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

