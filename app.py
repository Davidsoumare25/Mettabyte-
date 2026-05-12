from flask import Flask, render_template_string, request, redirect
import os
import time
import requests

app = Flask(__name__)

# --- CONFIGURATION SUPABASE ---
SUPABASE_URL = "https://xwzjlddgqwlrxgetahvp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh3empsZGRncXdscnhnZXRhaHZwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk3MzY1NTQsImV4cCI6MjA4NTMxMjU1NH0.MsCgDKBz3jXrJ_dOcJ35koaLi-uBpNXoAoaFLAWDbkg"
DB_URL = f"{SUPABASE_URL}/rest/v1/articles"
HEADERS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}

CSS = """
:root { --blue: #00d2ff; --purple: #9d50bb; --dark: #050505; }
body { font-family: 'Segoe UI', sans-serif; margin: 0; background: var(--dark); color: #eee; }
header { background: #000; padding: 25px 10px; text-align: center; border-bottom: 1px solid #111; }
.logo-text { font-size: 2.2rem; font-weight: 900; color: #fff; text-decoration: none; letter-spacing: 3px; text-transform: uppercase; text-shadow: 0 0 15px var(--blue); }
.byte-part { color: var(--blue); }
.container { width: 92%; max-width: 600px; margin: auto; padding: 20px 0; }
.card { background: #111; border-radius: 20px; padding: 20px; margin-bottom: 30px; border: 1px solid #222; }
.btn { display: block; background: linear-gradient(135deg, var(--blue), var(--purple)); color: white; padding: 12px; border-radius: 10px; text-decoration: none; text-align: center; font-weight: bold; }
"""

@app.route('/')
def home():
    try:
        r = requests.get(f"{DB_URL}?order=ts.desc", headers=HEADERS)
        articles = r.json() if r.status_code == 200 else []
    except:
        articles = []
    
    cards = ""
    for art in articles:
        cards += f'<div class="card"><h2>{art["titre"]}</h2><p style="color:#888;">{art["resume"]}</p><a href="#" class="btn">LIRE LA SUITE</a></div>'
    
    return render_template_string(f"""
    <html><head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="google-site-verification" content="dDTFaN2k3Nh2HOiJF_R7J-8PaUw0LZ6enE0yTGFKrSA" />
    <style>{CSS}</style></head>
    <body><header><div class="logo-text">METTA<span class="byte-part">BYTE</span></div></header>
    <div class="container">{cards}</div></body></html>""")

# --- LA ROUTE POUR GOOGLE (MÉTHODE FICHIER HTML) ---
@app.route('/googleaa97466e31055bc3.html')
def google_verify():
    return "google-site-verification: googleaa97466e31055bc3.html"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

