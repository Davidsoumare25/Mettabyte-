import os
import re
import json
import time
import hashlib
import requests
from flask import Flask, request, redirect, session, Response

app = Flask(__name__)

# --- SÉCURISATION STRICTE DE LA CLÉ DE SESSION ---
if not os.environ.get("SESSION_KEY"):
    raise RuntimeError("ERREUR CRITIQUE : La variable d'environnement SESSION_KEY n'est pas configurée !")

app.secret_key = os.environ.get("SESSION_KEY")

# --- CONFIGURATION ---
SUPABASE_URL     = os.environ.get("SUPABASE_URL")        # table articles
SUPABASE_URL_USR = os.environ.get("SUPABASE_URL_USERS")  # table users

# Déduction ou configuration automatique de la table 'jeux'
if SUPABASE_URL and "/rest/v1/" in SUPABASE_URL:
    SUPABASE_BASE = SUPABASE_URL.split("/rest/v1/")[0]
    SUPABASE_URL_JEU = f"{SUPABASE_BASE}/rest/v1/jeux"
else:
    SUPABASE_URL_JEU = os.environ.get("SUPABASE_URL_JEUX")

SUPABASE_KEY     = os.environ.get("SUPABASE_KEY")
ADMIN_PASS_ENV   = os.environ.get("ADMIN_PASSWORD")
ADMIN_PATH       = "moncode123"
LOGO_URL         = "https://i.ibb.co/GfZxNrFq/img-1778540891.png"
ADSENSE_ID       = "pub-2847151888169934"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": "Bearer " + str(SUPABASE_KEY),
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# ─────────────────────────────────────────────
# PAYDUNYA — CONFIGURATION
# ─────────────────────────────────────────────
PAYDUNYA_MASTER_KEY  = os.environ.get("PAYDUNYA_MASTER_KEY")
PAYDUNYA_PRIVATE_KEY = os.environ.get("PAYDUNYA_PRIVATE_KEY")
PAYDUNYA_PUBLIC_KEY  = os.environ.get("PAYDUNYA_PUBLIC_KEY")
PAYDUNYA_TOKEN       = os.environ.get("PAYDUNYA_TOKEN")
PAYDUNYA_MODE        = os.environ.get("PAYDUNYA_MODE", "test")

def paydunya_headers():
    return {
        "PAYDUNYA-MASTER-KEY":  PAYDUNYA_MASTER_KEY,
        "PAYDUNYA-PRIVATE-KEY": PAYDUNYA_PRIVATE_KEY,
        "PAYDUNYA-PUBLIC-KEY":  PAYDUNYA_PUBLIC_KEY,
        "PAYDUNYA-TOKEN":       PAYDUNYA_TOKEN,
        "Content-Type": "application/json"
    }

def paydunya_base_url():
    prefix = "sandbox-" if PAYDUNYA_MODE == "test" else ""
    return f"https://app.paydunya.com/{prefix}api/v1"


# ─────────────────────────────────────────────
# UTILITAIRES / HELPERS
# ─────────────────────────────────────────────
def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def reading_time(html_text):
    clean = re.sub(r'<[^>]+>', '', html_text)
    return max(1, round(len(clean.split()) / 200))

def get_user():
    uid = session.get('user_id')
    if not uid:
        return None
    try:
        r = requests.get(SUPABASE_URL_USR + "?id=eq." + str(uid), headers=HEADERS)
        data = r.json()
        return data[0] if data else None
    except:
        return None

def render_page(content, title, meta_desc="METTABYTE — Tech, IA, Science, Espace"):
    user = get_user()
    user_name  = user['email'].split('@')[0] if user else ""
    is_premium = user.get('premium', False) if user else False
    is_logged  = user is not None

    if is_logged:
        menu_user_html = f"""
        <div class="menu-user-info">
            <div class="menu-avatar">{user_name[0].upper()}</div>
            <div>
                <div style="font-weight:700; color:#fff;">{user_name}</div>
                <div style="font-size:0.75rem; color:{'#f5c518' if is_premium else '#888'};">
                    {'👑 Premium' if is_premium else 'Gratuit'}
                </div>
            </div>
        </div>
        {'<div class="menu-premium-badge">👑 Membre Premium actif</div>' if is_premium else '<a href="/premium" class="menu-upgrade-btn">✨ Passer Premium — 655 F</a>'}
        <hr style="border:0.5px solid #222; margin:20px 0;">
        <a href="/compte" class="menu-link">👤 Mon compte</a>
        <a href="/deconnexion" class="menu-link" style="color:var(--red);">🚪 Déconnexion</a>
        """
    else:
        menu_user_html = """
        <p style="color:#888; font-size:0.85rem; margin-bottom:20px;">
            Crée un compte pour accéder aux articles Premium et à l'Arcade Arcade.
        </p>
        <a href="/inscription" class="menu-cta-btn">✉️ Créer un compte</a>
        <a href="/connexion" class="menu-link" style="margin-top:10px;">🔑 Se connecter</a>
        <hr style="border:0.5px solid #222; margin:20px 0;">
        <a href="/premium" class="menu-link" style="color:#f5c518;">👑 Découvrir Premium</a>
        """

    html = BASE_HTML
    html = html.replace("%PAGE_TITLE%", title)
    html = html.replace("%LOGO%", LOGO_URL)
    html = html.replace("%RAW_CONTENT%", content)
    html = html.replace("%META_DESC%", meta_desc)
    html = html.replace("%ADSENSE_ID%", ADSENSE_ID)
    html = html.replace("%MENU_USER_HTML%", menu_user_html)
    return html

# ─────────────────────────────────────────────
# GABARIT HTML DE BASE (BASE_HTML)
# ─────────────────────────────────────────────
BASE_HTML = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>%PAGE_TITLE%</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="description" content="%META_DESC%">
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-%ADSENSE_ID%" crossorigin="anonymous"></script>
    <link rel="icon" href="%LOGO%">
    <link rel="manifest" href="/manifest.json">
    <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:ital,wght@0,300;0,400;0,700;1,300&display=swap" rel="stylesheet">
    <style>
        :root { --blue:#00d2ff; --purple:#9d50bb; --dark:#050505; --gray:#1c1c1e; --white:#f5f0eb; --red:#e63022; --gold:#f5c518; }
        *, *::before, *::after { box-sizing: border-box; }
        body { font-family:'DM Sans',-apple-system,sans-serif; margin:0; background:var(--dark); color:#fff; line-height:1.6; -webkit-font-smoothing:antialiased; overflow-x:hidden; padding-bottom:80px; }

        /* HEADER */
        header { background:rgba(0,0,0,0.9); backdrop-filter:blur(20px); padding:15px 20px; display:flex; align-items:center; justify-content:space-between; border-bottom:0.5px solid #333; position:sticky; top:0; z-index:1000; }
        .logo { font-size:1.6rem; font-weight:800; color:#fff; text-decoration:none; font-family:'Bebas Neue',sans-serif; }
        .logo span { color:var(--blue); }
        .header-menu-btn { background:none; border:none; color:#fff; font-size:1.4rem; cursor:pointer; padding:5px; line-height:1; }

        /* TIROIR DE NAVIGATION (MENU GAUCHE) */
        .sidebar-overlay { position:fixed; inset:0; background:rgba(0,0,0,0.6); z-index:2000; opacity:0; pointer-events:none; transition:opacity 0.3s; backdrop-filter:blur(4px); }
        .sidebar-overlay.open { opacity:1; pointer-events:all; }
        .sidebar { position:fixed; top:0; left:0; height:100%; width:min(320px,85vw); background:#0e0e10; border-right:1px solid #222; z-index:2001; transform:translateX(-100%); transition:transform 0.35s cubic-bezier(.4,0,.2,1); display:flex; flex-direction:column; overflow-y:auto; }
        .sidebar.open { transform:translateX(0); }
        .sidebar-header { display:flex; align-items:center; justify-content:space-between; padding:20px; border-bottom:1px solid #222; }
        .sidebar-logo { font-family:'Bebas Neue',sans-serif; font-size:1.4rem; color:#fff; }
        .sidebar-logo span { color:var(--blue); }
        .sidebar-close { background:none; border:none; color:#888; font-size:1.5rem; cursor:pointer; line-height:1; }
        .sidebar-body { padding:24px 20px; flex:1; }
        .sidebar-section-title { font-size:0.65rem; letter-spacing:0.15em; text-transform:uppercase; color:#555; margin-bottom:12px; }
        .menu-link { display:block; padding:12px 16px; color:#ccc; text-decoration:none; border-radius:10px; font-size:0.95rem; font-weight:500; transition:background 0.2s; margin-bottom:4px; }
        .menu-link:hover { background:#1a1a1e; color:#fff; }
        .menu-cta-btn { display:block; background:linear-gradient(135deg,var(--blue),var(--purple)); color:#fff; text-align:center; padding:14px; border-radius:14px; font-weight:700; text-decoration:none; font-size:0.95rem; margin-bottom:8px; }
        .menu-upgrade-btn { display:block; background:linear-gradient(135deg,#f5c518,#e6a800); color:#000; text-align:center; padding:14px; border-radius:14px; font-weight:700; text-decoration:none; font-size:0.95rem; margin-bottom:8px; }
        .menu-premium-badge { background:rgba(245,197,24,0.1); border:1px solid rgba(245,197,24,0.3); color:var(--gold); text-align:center; padding:10px; border-radius:10px; font-size:0.85rem; font-weight:700; margin-bottom:8px; }
        .menu-user-info { display:flex; align-items:center; gap:12px; margin-bottom:20px; padding:14px; background:#1a1a1e; border-radius:12px; }
        .menu-avatar { width:42px; height:42px; background:linear-gradient(135deg,var(--blue),var(--purple)); border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:1.1rem; flex-shrink:0; }

        /* ÉLÉMENTS DU SITE */
        .nav-container { background:#000; border-bottom:0.5px solid #222; padding:12px 0; }
        .nav-cats { display:flex; gap:12px; overflow-x:auto; padding:0 20px; }
        .nav-cats::-webkit-scrollbar { display:none; }
        .cat { color:#8e8e93; text-decoration:none; font-size:0.9rem; font-weight:600; padding:8px 18px; white-space:nowrap; border-radius:20px; background:var(--gray); }
        .cat.active { color:#fff; background:linear-gradient(135deg,var(--blue),var(--purple)); }
        .container { width:92%; max-width:800px; margin:auto; padding:20px 0; }

        /* CARDS ARTICLES */
        .card { background:var(--gray); border-radius:24px; overflow:hidden; margin-bottom:30px; border:0.5px solid #333; text-decoration:none; display:block; color:inherit; transition:transform 0.2s; position:relative; }
        .card:active { transform:scale(0.98); }
        .card-img { width:100%; height:280px; object-fit:cover; }
        .card-body { padding:25px; }
        .card-tag { color:var(--blue); font-size:11px; font-weight:700; text-transform:uppercase; margin-bottom:8px; letter-spacing:1px; }
        .card-title { margin:5px 0; font-size:24px; font-weight:700; line-height:1.2; color:#fff; }
        .premium-badge { position:absolute; top:14px; right:14px; background:linear-gradient(135deg,var(--gold),#e6a800); color:#000; font-size:0.7rem; font-weight:800; padding:5px 10px; border-radius:20px; letter-spacing:0.05em; text-transform:uppercase; display:flex; align-items:center; gap:4px; }

        /* ARCADE GRID */
        .arcade-grid { display:grid; grid-template-columns:repeat(auto-fill, minmax(280px, 1fr)); gap:20px; margin-top:20px; }
        .game-card { background:var(--gray); border:1px solid #333; border-radius:20px; overflow:hidden; text-decoration:none; color:inherit; transition:transform 0.2s; position:relative; display:flex; flex-direction:column; }
        .game-card:active { transform:scale(0.97); }
        .game-img { width:100%; height:180px; object-fit:cover; }
        .game-body { padding:18px; flex:1; display:flex; flex-direction:column; justify-content:space-between; }
        .game-title { font-size:1.3rem; font-weight:700; margin:0 0 6px 0; color:#fff; }
        .game-desc { font-size:0.85rem; color:#aaa; margin:0 0 14px 0; line-height:1.4; }

        /* ARTICLE STRUCTURE */
        .article-hero { min-height:60vh; display:flex; flex-direction:column; justify-content:flex-end; padding:4rem 2rem; position:relative; background-size:cover; background-position:center; }
        .article-hero::after { content:''; position:absolute; inset:0; background:linear-gradient(to top,var(--dark) 15%,transparent 100%); }
        .hero-content { position:relative; z-index:2; max-width:800px; margin:0 auto; width:100%; }
        .hero-title { font-family:'Bebas Neue',sans-serif; font-size:clamp(2.5rem,8vw,5.5rem); line-height:0.9; margin:0; color:#fff; }
        .hero-meta { margin-top:1rem; color:#aaa; font-size:0.85rem; display:flex; gap:1rem; flex-wrap:wrap; align-items:center; }
        .hero-premium-tag { background:linear-gradient(135deg,var(--gold),#e6a800); color:#000; font-size:0.7rem; font-weight:800; padding:4px 10px; border-radius:20px; }
        .article-content { max-width:740px; margin:0 auto; padding:3rem 2rem; color:#c8c0b8; font-size:1.15rem; line-height:1.8; }
        .article-content h2 { font-family:'Bebas Neue',sans-serif; font-size:2.5rem; color:var(--white); margin:3rem 0 1rem; border-left:4px solid var(--blue); padding-left:15px; }

        /* FORMULAIRES & INPUTS */
        input, textarea, select { width:100%; padding:15px; margin:10px 0; background:#1c1c1e; border:1px solid #333; color:#fff; border-radius:12px; font-size:16px; box-sizing:border-box; }
        input:focus, textarea:focus { outline:none; border-color:var(--blue); }
        label { color:#888; font-size:0.8rem; display:block; margin-top:10px; }
        .btn { display:block; background:linear-gradient(135deg,var(--blue),var(--purple)); color:#fff; padding:18px; text-align:center; border-radius:20px; text-decoration:none; font-weight:700; border:none; font-size:1rem; cursor:pointer; width:100%; box-sizing:border-box; }
        
        /* AUTH CARDS */
        .auth-wrap { max-width:420px; margin:60px auto; padding:0 20px 40px; }
        .auth-title { font-family:'Bebas Neue',sans-serif; font-size:2.8rem; color:#fff; margin-bottom:0.25rem; }
        .auth-sub { color:#888; margin-bottom:2rem; font-size:0.9rem; }
        .auth-card { background:#111; border:1px solid #222; border-radius:20px; padding:28px; }
        .auth-input { width:100%; padding:14px 16px; background:#1c1c1e; border:1px solid #333; color:#fff; border-radius:12px; font-size:1rem; margin-bottom:14px; }
        .auth-btn { width:100%; padding:16px; background:linear-gradient(135deg,var(--blue),var(--purple)); color:#fff; font-weight:700; font-size:1rem; border:none; border-radius:14px; cursor:pointer; }
        .auth-link { display:block; text-align:center; margin-top:16px; color:#888; font-size:0.85rem; text-decoration:none; }
        .auth-error { background:rgba(230,48,34,0.1); border:1px solid rgba(230,48,34,0.3); color:#ff6b6b; padding:12px 16px; border-radius:10px; margin-bottom:16px; font-size:0.85rem; }

        /* PREMIUM PRICING */
        .premium-hero { text-align:center; padding:4rem 2rem 2rem; }
        .premium-crown { font-size:4rem; margin-bottom:1rem; }
        .premium-title { font-family:'Bebas Neue',sans-serif; font-size:clamp(3rem,8vw,5rem); color:var(--gold); line-height:1; }
        .premium-sub { color:#aaa; font-size:1.05rem; max-width:500px; margin:1rem auto 0; }
        .pricing-card { background:#111; border:2px solid var(--gold); border-radius:24px; padding:32px; max-width:380px; margin:2rem auto; text-align:center; }
        .pricing-price { font-family:'Bebas Neue',sans-serif; font-size:4rem; color:var(--gold); line-height:1; }
        .pricing-period { color:#888; font-size:0.85rem; margin-bottom:1.5rem; }
        .pricing-features { list-style:none; padding:0; margin:0 0 1.5rem; text-align:left; }
        .pricing-features li { padding:8px 0; border-bottom:0.5px solid #222; color:#ccc; font-size:0.9rem; }
        .pricing-features li::before { content:'✓ '; color:var(--gold); font-weight:700; }

        /* FOOTER STRAP */
        .footer-nav { position:fixed; bottom:0; left:0; width:100%; background:rgba(0,0,0,0.9); backdrop-filter:blur(15px); border-top:0.5px solid #333; display:flex; justify-content:space-around; padding:15px 0; z-index:1000; }
        .footer-nav a { color:#888; text-decoration:none; font-size:0.75rem; font-weight:700; text-transform:uppercase; }
        
        /* SEARCH BOX */
        .search-wrap { background:#000; padding:12px 20px; border-bottom:0.5px solid #222; }
        .search-box { display:flex; align-items:center; background:#1c1c1e; border-radius:50px; padding:0 16px; gap:10px; max-width:600px; margin:0 auto; border:1px solid #333; }
        .search-box input { background:none; border:none; color:#fff; font-size:0.95rem; padding:12px 0; margin:0; width:100%; outline:none; }
        .search-box span { color:#666; font-size:1.1rem; }
        .search-results { max-width:800px; margin:0 auto; padding:0 20px 10px; display:none; }
        .search-item { display:flex; align-items:center; gap:12px; padding:12px; background:#111; border-radius:12px; margin-bottom:8px; text-decoration:none; color:#fff; border:0.5px solid #333; }
        .search-item img { width:60px; height:60px; object-fit:cover; border-radius:8px; }
        .search-item-title { font-size:0.9rem; font-weight:700; }

        /* COMPTE */
        .compte-wrap { max-width:600px; margin:0 auto; padding:30px 20px; }
        .compte-header { display:flex; align-items:center; gap:16px; margin-bottom:30px; }
        .compte-avatar { width:64px; height:64px; background:linear-gradient(135deg,var(--blue),var(--purple)); border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:1.8rem; font-weight:700; }
        .compte-info h2 { margin:0; font-size:1.3rem; }
        .compte-info p { margin:4px 0 0; color:#888; font-size:0.85rem; }

        /* SCROLL TOP */
        .scroll-top { position:fixed; bottom:90px; right:20px; width:44px; height:44px; background:linear-gradient(135deg,var(--blue),var(--purple)); border-radius:50%; display:flex; align-items:center; justify-content:center; cursor:pointer; border:none; color:#fff; font-size:1.1rem; z-index:999; opacity:0; pointer-events:none; transition:opacity 0.3s; }
        .scroll-top.visible { opacity:1; pointer-events:all; }

        .admin-list-item { background:#111; padding:12px 15px; margin-bottom:6px; border-radius:10px; display:flex; justify-content:space-between; align-items:center; gap:10px; flex-wrap:wrap; }
        .btn-edit { color:var(--blue); font-size:0.8rem; font-weight:700; text-decoration:none; }
        .btn-delete { background:none; border:none; color:var(--red); font-size:0.8rem; font-weight:700; cursor:pointer; padding:0; }
    </style>
</head>
<body>
    <header>
        <button class="header-menu-btn" id="openMenuBtn">☰</button>
        <a href="/" class="logo">METTA<span>BYTE</span></a>
        <div style="width:34px;"></div>
    </header>

    <div class="sidebar-overlay" id="sidebarOverlay"></div>
    <div class="sidebar" id="sidebar">
        <div class="sidebar-header">
            <span class="sidebar-logo">METTA<span>BYTE</span></span>
            <button class="sidebar-close" id="closeMenuBtn">×</button>
        </div>
        <div class="sidebar-body">
            %MENU_USER_HTML%
            <hr style="border:0.5px solid #222; margin:16px 0;">
            <div class="sidebar-section-title">Navigation</div>
            <a href="/" class="menu-link">🏠 Accueil</a>
            <a href="/arcade" class="menu-link" style="color:var(--blue); font-weight:700; background:rgba(0,210,255,0.05);">🎮 METTABYTE ARCADE</a>
            <a href="/?cat=IA" class="menu-link">🤖 Intelligence Artificielle</a>
            <a href="/?cat=Tech" class="menu-link">💻 Tech</a>
            <a href="/?cat=Science" class="menu-link">🔬 Science</a>
            <a href="/?cat=Espace" class="menu-link">🚀 Espace</a>
            <hr style="border:0.5px solid #222; margin:16px 0;">
            <a href="mailto:mettabytesite@gmail.com" class="menu-link">✉️ Contact</a>
            <a href="/privacy" class="menu-link">🔒 Confidentialité</a>
        </div>
    </div>

    %RAW_CONTENT%

    <div class="footer-nav">
        <a href="/">Accueil</a>
        <a href="/arcade">🎮 Arcade</a>
        <a href="mailto:mettabytesite@gmail.com">Contact</a>
    </div>

    <button class="scroll-top" id="scrollTopBtn">↑</button>

    <script>
    document.addEventListener('DOMContentLoaded', function() {
        var sidebar = document.getElementById('sidebar');
        var overlay = document.getElementById('sidebarOverlay');
        var openBtn = document.getElementById('openMenuBtn');
        var closeBtn = document.getElementById('closeMenuBtn');

        if (openBtn && sidebar && overlay) {
            openBtn.addEventListener('click', function() {
                sidebar.classList.add('open');
                overlay.classList.add('open');
            });
        }
        if (closeBtn && sidebar && overlay) {
            closeBtn.addEventListener('click', function() {
                sidebar.classList.remove('open');
                overlay.classList.remove('open');
            });
            overlay.addEventListener('click', function() {
                sidebar.classList.remove('open');
                overlay.classList.remove('open');
            });
        }

        var scrollBtn = document.getElementById('scrollTopBtn');
        if (scrollBtn) {
            window.addEventListener('scroll', function() {
                if (window.scrollY > 400) scrollBtn.classList.add('visible');
                else scrollBtn.classList.remove('visible');
            });
            scrollBtn.addEventListener('click', function() {
                window.scrollTo({top:0, behavior:'smooth'});
            });
        }

        // Système de recherche dynamique
        var sIn = document.getElementById('searchInput');
        var sRes = document.getElementById('searchResults');
        if (sIn && sRes) {
            var timer;
            sIn.addEventListener('input', function() {
                clearTimeout(timer);
                var q = this.value.trim();
                if (q.length < 2) { sRes.style.display = 'none'; return; }
                timer = setTimeout(function() {
                    fetch('/search?q=' + encodeURIComponent(q))
                    .then(r => r.json())
                    .then(data => {
                        if(!data.length) { sRes.innerHTML = '<div style="padding:15px;color:#666;">Aucun résultat</div>'; }
                        else {
                            sRes.innerHTML = data.map(a => `<a href="/article/${a.id}" class="search-item">
                                <img src="${a.img_url || '/static/logo.png'}" style="width:50px;height:50px;object-fit:cover;border-radius:6px;">
                                <div><div style="font-size:11px;color:var(--blue);">${a.categorie}</div><div class="search-item-title">${a.titre}</div></div>
                            </a>`).join('');
                        }
                        sRes.style.display = 'block';
                    });
                }, 300);
            });
        }
    });
    </script>
</body>
</html>"""


# ─────────────────────────────────────────────
# ROUTES DES ARTICLES (ACCUEIL & AFFICHAGE)
# ─────────────────────────────────────────────

@app.route('/')
def home():
    cat = request.args.get('cat', 'Tous')
    params = {"order": "ts.desc"}
    if cat != 'Tous':
        params["categorie"] = "eq." + cat
    try:
        r = requests.get(SUPABASE_URL, headers=HEADERS, params=params)
        articles = r.json() if isinstance(r.json(), list) else []
    except:
        articles = []

    cats_list = ["Tous", "Tech", "Science", "IA", "Espace", "Santé"]
    nav = '<div class="nav-container"><nav class="nav-cats">' + "".join([
        f'<a href="/?cat={c}" class="cat {"active" if c == cat else ""}">{c}</a>' for c in cats_list
    ]) + '</nav></div>'
    nav += """
    <div class="search-wrap">
        <div class="search-box"><span>🔍</span><input type="text" id="searchInput" placeholder="Rechercher un article..."></div>
        <div class="search-results" id="searchResults"></div>
    </div>"""

    cards = "".join([
        f'<a href="/article/{a["id"]}" class="card">'
        + ('<div class="premium-badge">👑 Premium</div>' if a.get("premium") else '')
        + f'<img src="{a.get("img_url", LOGO_URL)}" class="card-img" loading="lazy">'
        f'<div class="card-body">'
        f'<div class="card-tag">{a.get("categorie","TECH")} · {reading_time(a.get("texte",""))} min</div>'
        f'<h2 class="card-title">{a["titre"]}</h2>'
        f'</div></a>' for a in articles
    ])

    return render_page(nav + '<div class="container">' + cards + '</div>', "METTABYTE")


@app.route('/article/<id>')
def read_article(id):
    try:
        r = requests.get(SUPABASE_URL + "?id=eq." + str(id), headers=HEADERS)
        art = r.json()[0]
    except:
        return redirect('/')

    user = get_user()
    is_premium_user = user.get('premium', False) if user else False
    is_premium_art  = art.get('premium', False)

    if is_premium_art and not is_premium_user:
        extrait = art["texte"][:150] + "... [Contenu Premium Masqué]"
        texte_html = f"""
        <div class="paywall-blur">{extrait}</div>
        <div class="paywall-box">
            <div class="paywall-icon">👑</div>
            <div class="paywall-title">Article Premium</div>
            <p class="paywall-sub">Rejoins l'élite METTABYTE pour débloquer cet article.</p>
            <div class="paywall-btns"><a href="/premium" class="paywall-btn-premium">✨ Devenir Premium</a></div>
        </div>"""
    else:
        texte_html = art["texte"]

    content = f"""
    <div class="article-hero" style="background-image:url('{art.get('img_url', LOGO_URL)}')">
        <div class="hero-content">
            <h1 class="hero-title">{art["titre"]}</h1>
            <div class="hero-meta"><span>⏱️ {reading_time(art.get('texte',''))} min</span></div>
        </div>
    </div>
    <div class="article-content">{texte_html}</div>"""
    return render_page(content, art['titre'])


# ─────────────────────────────────────────────
# 🎮 ARCADE MATRIX — ZONE MULTI-FICHIERS (HTML, CSS, JS, JSON)
# ─────────────────────────────────────────────

@app.route('/arcade')
def arcade():
    try:
        r = requests.get(SUPABASE_URL_JEU, headers=HEADERS, params={"order": "ts.desc"})
        jeux = r.json() if isinstance(r.json(), list) else []
    except:
        jeux = []

    game_cards = ""
    for j in jeux:
        premium_badge = '<div class="premium-badge">👑 Premium</div>' if j.get("premium") else ''
        game_cards += f"""
        <a href="/arcade/jouer/{j['id']}" class="game-card">
            {premium_badge}
            <img src="{j.get('img_url', LOGO_URL)}" class="game-img" loading="lazy">
            <div class="game-body">
                <div>
                    <h3 class="game-title">{j['titre']}</h3>
                    <p class="game-desc">{j.get('description', '')}</p>
                </div>
                <span style="color:var(--blue);font-size:0.85rem;font-weight:700;">Lancer l'expérience →</span>
            </div>
        </a>"""

    if not game_cards:
        game_cards = '<p style="color:#555;text-align:center;grid-column:1/-1;">Aucun jeu disponible.</p>'

    content = f"""
    <div class="container">
        <h1 style="font-family:'Bebas Neue';font-size:3.5rem;margin-bottom:0;text-align:center;">METTABYTE <span style="color:var(--blue);">ARCADE</span></h1>
        <p style="color:#666;text-align:center;margin-top:0;margin-bottom:40px;">Mini-jeux web autonomes de type Quiz, Arcade & Réflexion</p>
        <div class="arcade-grid">{game_cards}</div>
    </div>"""
    return render_page(content, "Mettabyte Arcade")


@app.route('/arcade/jouer/<id>')
def jouer_jeu(id):
    try:
        r = requests.get(SUPABASE_URL_JEU + "?id=eq." + str(id), headers=HEADERS)
        jeu = r.json()[0]
    except:
        return redirect('/arcade')

    user = get_user()
    if jeu.get('premium') and (not user or not user.get('premium')):
        content = f"""
        <div class="container" style="text-align:center;padding:80px 20px;">
            <h1 style="font-family:'Bebas Neue';font-size:3rem;color:var(--gold);">👑 Expérience Restreinte</h1>
            <p style="color:#aaa;">Le jeu <strong>{jeu['titre']}</strong> requiert l'accès Premium.</p>
            <a href="/premium" class="paywall-btn-premium" style="display:inline-block;margin-top:20px;">S'abonner (655 F)</a>
        </div>"""
        return render_page(content, "Accès Restreint")

    content = f"""
    <div class="container" style="text-align:center;">
        <h1 style="font-family:'Bebas Neue';font-size:2rem;margin-bottom:20px;">{jeu['titre']}</h1>
        <div style="width:100%;max-width:550px;margin:0 auto;background:#000;border:2px solid #222;border-radius:24px;overflow:hidden;aspect-ratio:9/16;max-height:80vh;">
            <iframe src="/arcade/render-game/{jeu['id']}" style="width:100%;height:100%;border:none;" allow="autoplay; gamepad"></iframe>
        </div>
        <br><a href="/arcade" style="color:#555;text-decoration:none;font-size:0.9rem;">← Retour à la liste</a>
    </div>"""
    return render_page(content, jeu['titre'])


@app.route('/arcade/render-game/<id>')
def render_game_code(id):
    try:
        r = requests.get(SUPABASE_URL_JEU + "?id=eq." + str(id), headers=HEADERS)
        jeu = r.json()[0]
        
        # Sécurité d'Iframe Premium
        if jeu.get('premium'):
            user = get_user()
            if not user or not user.get('premium'):
                return "Interdit — Premium Exigé", 403
        
        gdata = jeu.get('game_data', {})
        if isinstance(gdata, str):
            gdata = json.loads(gdata)
            
        html_code = gdata.get('html', '<body></body>')
        css_code  = gdata.get('css', '')
        js_code   = gdata.get('js', '')
        json_data = gdata.get('json', '{}')

        injection_css = f"<style>{css_code}</style>"
        
        # INJECTION INTELLIGENTE ET INTERCEPTION DU FETCH EXTERNE
        injection_js  = f"""
        <script>
            // Injection de tes questions et réponses JSON
            const DATA_JSON = {json_data};
            
            // Redirection magique de fetch('questions.json') pour éviter les blocages CORS
            const originalFetch = window.fetch;
            window.fetch = function(url) {{
                if (url.endsWith('.json') || url === 'questions.json') {{
                    return Promise.resolve({{
                        json: () => Promise.resolve(DATA_JSON),
                        ok: true,
                        status: 200
                    }});
                }}
                return originalFetch.apply(this, arguments);
            }};
            
            // Injection du script.js original
            {js_code}
        </script>"""

        complete_html = html_code
        if "</head>" in complete_html:
            complete_html = complete_html.replace("</head>", f"{injection_css}</head>")
        else:
            complete_html = injection_css + complete_html

        if "</body>" in complete_html:
            complete_html = complete_html.replace("</body>", f"{injection_js}</body>")
        else:
            complete_html = complete_html + injection_js

        return Response(complete_html, mimetype='text/html')
    except Exception as e:
        return f"Erreur de rendu de la matrice : {str(e)}", 404


# ─────────────────────────────────────────────
# COMPTE / SESSIONS / AUTHENTIFICATION
# ─────────────────────────────────────────────

@app.route('/inscription', methods=['GET', 'POST'])
def inscription():
    error = ""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        pw    = request.form.get('password', '')
        if len(pw) < 6: error = "Mot de passe trop court (6 caract. min)."
        else:
            chk = requests.get(SUPABASE_URL_USR + "?email=eq." + email, headers=HEADERS)
            if chk.json(): error = "Compte déjà existant."
            else:
                data = {"email": email, "password": hash_pw(pw), "premium": False, "ts": int(time.time())}
                r = requests.post(SUPABASE_URL_USR, headers=HEADERS, json=data)
                if r.json():
                    session['user_id'] = r.json()[0]['id']
                    return redirect('/')
    
    content = f"""<div class="auth-wrap"><div class="auth-card">
        <h2 class="auth-title">Créer un compte</h2>
        {f'<div class="auth-error">{error}</div>' if error else ''}
        <form method="post">
            <input class="auth-input" type="email" name="email" placeholder="Email" required>
            <input class="auth-input" type="password" name="password" placeholder="Mot de passe" required>
            <button type="submit" class="auth-btn">Rejoindre</button>
        </form>
    </div></div>"""
    return render_page(content, "Inscription")


@app.route('/connexion', methods=['GET', 'POST'])
def connexion():
    error = ""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        pw    = request.form.get('password', '')
        r = requests.get(SUPABASE_URL_USR + "?email=eq." + email, headers=HEADERS)
        users = r.json()
        if users and users[0]['password'] == hash_pw(pw):
            session['user_id'] = users[0]['id']
            return redirect('/')
        else: error = "Identifiants invalides."

    content = f"""<div class="auth-wrap"><div class="auth-card">
        <h2 class="auth-title">Connexion</h2>
        {f'<div class="auth-error">{error}</div>' if error else ''}
        <form method="post">
            <input class="auth-input" type="email" name="email" placeholder="Email" required>
            <input class="auth-input" type="password" name="password" placeholder="Mot de passe" required>
            <button type="submit" class="auth-btn">Entrer</button>
        </form>
    </div></div>"""
    return render_page(content, "Connexion")


@app.route('/deconnexion')
def deconnexion():
    session.clear()
    return redirect('/')


@app.route('/premium')
def premium():
    user = get_user()
    if user and user.get('premium'):
        return render_page("<div class='container'><h2>Tu es Premium ! 👑</h2></div>", "Premium")
    
    pay_btn = """<a href="/checkout-paydunya" class="btn">💳 Activer l'accès par PayDunya (655 F)</a>""" if user else "<p><a href='/connexion'>Connecte-toi</a> pour payer.</p>"
    content = f"<div class='container'><div class='pricing-card'><div class='pricing-price'>655 F</div>{pay_btn}</div></div>"
    return render_page(content, "Passer Premium")


@app.route('/checkout-paydunya')
def checkout_paydunya():
    user = get_user()
    if not user: return redirect('/connexion')
    base_url = request.url_root.rstrip('/')
    payload = {
        "invoice": {"items": {"item_0": {"name": "Premium 1 Mois", "quantity": 1, "unit_price": "655", "total_price": "655"}}, "total_amount": 655},
        "store": {"name": "METTABYTE", "website_url": base_url},
        "custom_data": {"user_id": str(user['id'])},
        "actions": {"cancel_url": base_url+"/premium", "return_url": base_url+"/paydunya/succes", "callback_url": base_url+"/paydunya/callback"}
    }
    r = requests.post(paydunya_base_url() + "/checkout-invoice/create", headers=paydunya_headers(), json=payload)
    if r.json().get("response_code") == "00": return redirect(r.json()["response_text"])
    return "Erreur PayDunya", 400


@app.route('/paydunya/succes')
def paydunya_succes():
    user = get_user()
    if user: requests.patch(SUPABASE_URL_USR + "?id=eq." + str(user['id']), headers=HEADERS, json={"premium": True})
    return redirect('/')


@app.route('/compte')
def compte():
    user = get_user()
    if not user: return redirect('/connexion')
    return render_page(f"<div class='container'><h2>Mon Profil</h2><p>Email: {user['email']}</p></div>", "Mon Compte")


# ─────────────────────────────────────────────
# API / METRICS / SYSTEM
# ─────────────────────────────────────────────

@app.route('/search')
def search():
    q = request.args.get('q', '').strip().lower()
    try:
        r = requests.get(SUPABASE_URL, headers=HEADERS)
        arts = [{"id": a["id"], "titre": a["titre"], "categorie": a.get("categorie",""), "img_url": a.get("img_url","")} for a in r.json() if q in a["titre"].lower()]
    except: arts = []
    return Response(json.dumps(arts), mimetype='application/json')

@app.route('/manifest.json')
def manifest():
    return Response(json.dumps({"name":"METTABYTE","start_url":"/","display":"standalone"}), mimetype='application/json')

@app.route('/privacy')
def privacy(): return render_page("<h2>Confidentialité</h2>", "Confidentialité")


# ─────────────────────────────────────────────
# 🛠️ STUDIO ADMINISTRATEUR AVANCÉ (4-FILES ARCADE)
# ─────────────────────────────────────────────

@app.route('/' + ADMIN_PATH, methods=['GET', 'POST'])
def admin():
    if request.method == 'POST' and request.form.get('password') == ADMIN_PASS_ENV:
        session['logged_in'] = True
    if not session.get('logged_in'):
        return render_page("""<div class="container" style="text-align:center;"><form method="post"><h2>Console Admin</h2><input type="password" name="password"><button class="btn">Authentification</button></form></div>""", "Admin")

    # Suppression Jeu
    if request.method == 'POST' and request.form.get('action') == 'delete_game':
        gid = request.form.get('del_game_id')
        requests.delete(SUPABASE_URL_JEU + "?id=eq." + gid, headers=HEADERS)
        return redirect('/' + ADMIN_PATH)

    # Sauvegarde/Ajout Jeu Multi-Fichiers (HTML, CSS, JS, JSON)
    if request.method == 'POST' and request.form.get('action_type') == 'save_game':
        structured = {
            "html": request.form['game_html'],
            "css":  request.form['game_css'],
            "js":   request.form['game_js'],
            "json": request.form['game_json']
        }
        game_payload = {
            "titre": request.form['game_titre'],
            "description": request.form['game_description'],
            "img_url": request.form['game_img_url'],
            "game_data": structured,
            "premium": request.form.get('game_premium') == 'on',
            "ts": int(time.time())
        }
        gid = request.form.get('game_id')
        if gid: requests.patch(SUPABASE_URL_JEU + "?id=eq." + gid, headers=HEADERS, json=game_payload)
        else: requests.post(SUPABASE_URL_JEU, headers=HEADERS, json=game_payload)
        return redirect('/' + ADMIN_PATH)

    # Récupération de la liste des jeux installés
    try: r_games = requests.get(SUPABASE_URL_JEU, headers=HEADERS, params={"order": "ts.desc"}).json()
    except: r_games = []

    list_games_html = "<h3>Jeux installés sur l'Arcade</h3>"
    for g in r_games:
        list_games_html += f"""
        <div class="admin-list-item">
            <span>🎮 {g['titre']}</span>
            <form method="post" style="margin:0;">
                <input type="hidden" name="action" value="delete_game">
                <input type="hidden" name="del_game_id" value="{g['id']}">
                <button type="submit" class="btn-delete">🗑️ Supprimer</button>
            </form>
        </div>"""

    # Formulaire de déploiement multi-fichiers
    form_jeu_html = f"""
    <div style="background:#111; padding:20px; border-radius:20px; margin-top:40px;">
        <h2 style="font-family:'Bebas Neue'; color:var(--blue);">🎮 DÉPLOIEMENT ARCADE STUDIO (4-FICHIERS)</h2>
        <form method="post">
            <input type="hidden" name="action_type" value="save_game">
            
            <label>Nom de l'expérience (Titre)</label>
            <input name="game_titre" placeholder="Ex: Quiz de l'Espace" required>
            
            <label>Description (Règles ou sous-titre)</label>
            <input name="game_description" placeholder="Ex: Réponds aux questions avant la fin du chronomètre.">
            
            <label>Vignette d'illustration (URL Image)</label>
            <input name="game_img_url" placeholder="https://...">

            <label style="color:#ff5e00; font-weight:bold; margin-top:15px;">📄 1. INDEX.HTML</label>
            <textarea name="game_html" rows="10" placeholder="Le code HTML brut" required></textarea>

            <label style="color:#007acc; font-weight:bold;">🎨 2. STYLE.CSS</label>
            <textarea name="game_css" rows="8" placeholder="Le style CSS"></textarea>

            <label style="color:#f1c40f; font-weight:bold;">⚡ 3. SCRIPT.JS</label>
            <textarea name="game_js" rows="10" placeholder="La logique JavaScript"></textarea>

            <label style="color:#2ecc71; font-weight:bold;">⚙️ 4. QUESTIONS.JSON (Données Structurées)</label>
            <textarea name="game_json" rows="8" placeholder='[ {{"question": "En quelle année... ?"}} ]' required></textarea>

            <label style="display:flex; align-items:center; gap:10px; margin-top:15px;">
                <input type="checkbox" name="game_premium" style="width:auto; margin:0;">
                <span>👑 Limiter ce jeu aux utilisateurs Premium</span>
            </label>
            <br>
            <button type="submit" class="btn">🚀 PROPULSER LE JEU SUR L'ARCADE</button>
        </form>
    </div>"""

    return render_page('<div class="container">' + form_jeu_html + '<hr>' + list_games_html + '</div>', "Studio Admin")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

