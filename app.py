import os
import requests
import time
from flask import Flask, render_template_string, request, redirect

app = Flask(__name__)

# --- CONFIGURATION (Vérifie bien tes clés Mettabyte) ---
SUPABASE_URL = "https://xwzjlddgqwlrxgetahvp.supabase.co/rest/v1/articles"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh3empsZGRncXdscnhnZXRhaHZwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk3MzY1NTQsImV4cCI6MjA4NTMxMjU1NH0.MsCgDKBz3jXrJ_dOcJ35koaLi-uBpNXoAoaFLAWDbkg"
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

ADMIN_PATH = "moncode123"

# --- DESIGN ---
CSS = ":root { --blue: #00d2ff; } body { background:#000; color:#fff; font-family:sans-serif; text-align:center; padding:20px; } .card { border:1px solid #222; padding:15px; margin:10px; border-radius:10px; } .btn { background:var(--blue); color:#000; padding:10px; text-decoration:none; border-radius:5px; font-weight:bold; display:block; margin:10px auto; width:200px; border:none; }"

# --- ROUTES ---
@app.route('/')
def home():
    try:
        r = requests.get(SUPABASE_URL, headers=HEADERS, params={"order": "ts.desc"})
        articles = r.json() if r.status_code == 200 else []
    except:
        articles = []
    
    content = ""
    for a in articles:
        content += f'<div class="card"><h2>{a.get("titre")}</h2><p>{a.get("resume")}</p></div>'
    
    return render_template_string(f'<html><head><style>{CSS}</style></head><body><h1>METTABYTE</h1>{content if content else "<p>Aucun article. Allez sur /moncode123/ pour publier.</p>"}</body></html>')

@app.route(f'/{ADMIN_PATH}/', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        new_art = {
            "titre": request.form['titre'],
            "resume": request.form['texte'][:100],
            "texte": request.form['texte'],
            "ts": int(time.time()),
            "img_url": request.form['img_url']
        }
        requests.post(SUPABASE_URL, headers=HEADERS, json=new_art)
        return redirect('/')
    
    return render_template_string(f'''
        <html><head><style>{CSS}</style></head><body>
            <h1>PUBLIER</h1>
            <form method="post">
                <input name="titre" placeholder="Titre" style="width:300px;padding:10px;"><br><br>
                <input name="img_url" placeholder="Lien image" style="width:300px;padding:10px;"><br><br>
                <textarea name="texte" placeholder="Contenu" style="width:300px;height:100px;padding:10px;"></textarea><br><br>
                <button type="submit" class="btn">ENVOYER</button>
            </form>
        </body></html>
    ''')

@app.route('/googleaa97466e31055bc3.html')
def google():
    return "google-site-verification: googleaa97466e31055bc3.html"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
