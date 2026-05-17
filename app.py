import os
import re
import json
import time
import hashlib
import requests
from flask import Flask, request, redirect, session, Response

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_KEY") or "mettabyte_ultra_secret_2026"

# --- CONFIGURATION ---
SUPABASE_URL     = os.environ.get("SUPABASE_URL")        # table articles
SUPABASE_URL_USR = os.environ.get("SUPABASE_URL_USERS")  # table users
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
# HELPERS
# ─────────────────────────────────────────────
def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def reading_time(html_text):
    clean = re.sub(r'<[^>]+>', '', html_text)
    return max(1, round(len(clean.split()) / 200))

def get_user():
    """Retourne l'utilisateur connecté depuis la session, ou None."""
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
    user_name   = user['email'].split('@')[0] if user else ""
    is_premium  = user.get('premium', False) if user else False
    is_logged   = user is not None

    # Boutons menu latéral selon état connexion
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
        {'<div class="menu-premium-badge">👑 Membre Premium actif</div>' if is_premium else '<a href="/premium" class="menu-upgrade-btn">✨ Passer Premium — 1€</a>'}
        <hr style="border:0.5px solid #222; margin:20px 0;">
        <a href="/compte" class="menu-link">👤 Mon compte</a>
        <a href="/deconnexion" class="menu-link" style="color:var(--red);">🚪 Déconnexion</a>
        """
    else:
        menu_user_html = """
        <p style="color:#888; font-size:0.85rem; margin-bottom:20px;">
            Crée un compte pour accéder aux articles Premium et soutenir METTABYTE.
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
# BASE HTML
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

        /* MENU LATÉRAL */
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

        /* NAVIGATION */
        .nav-container { background:#000; border-bottom:0.5px solid #222; padding:12px 0; }
        .nav-cats { display:flex; gap:12px; overflow-x:auto; padding:0 20px; }
        .nav-cats::-webkit-scrollbar { display:none; }
        .cat { color:#8e8e93; text-decoration:none; font-size:0.9rem; font-weight:600; padding:8px 18px; white-space:nowrap; border-radius:20px; background:var(--gray); }
        .cat.active { color:#fff; background:linear-gradient(135deg,var(--blue),var(--purple)); }

        .container { width:92%; max-width:800px; margin:auto; padding:20px 0; }

        /* CARDS */
        .card { background:var(--gray); border-radius:24px; overflow:hidden; margin-bottom:30px; border:0.5px solid #333; text-decoration:none; display:block; color:inherit; transition:transform 0.2s; position:relative; }
        .card:active { transform:scale(0.98); }
        .card-img { width:100%; height:280px; object-fit:cover; }
        .card-body { padding:25px; }
        .card-tag { color:var(--blue); font-size:11px; font-weight:700; text-transform:uppercase; margin-bottom:8px; letter-spacing:1px; }
        .card-title { margin:5px 0; font-size:24px; font-weight:700; line-height:1.2; color:#fff; }
        /* Badge cadenas Premium sur la card */
        .premium-badge { position:absolute; top:14px; right:14px; background:linear-gradient(135deg,var(--gold),#e6a800); color:#000; font-size:0.7rem; font-weight:800; padding:5px 10px; border-radius:20px; letter-spacing:0.05em; text-transform:uppercase; display:flex; align-items:center; gap:4px; }

        /* ARTICLE */
        .article-hero { min-height:70vh; display:flex; flex-direction:column; justify-content:flex-end; padding:4rem 2rem; position:relative; background-size:cover; background-position:center; }
        .article-hero::after { content:''; position:absolute; inset:0; background:linear-gradient(to top,var(--dark) 15%,transparent 100%); }
        .hero-content { position:relative; z-index:2; max-width:800px; margin:0 auto; width:100%; }
        .hero-title { font-family:'Bebas Neue',sans-serif; font-size:clamp(3rem,10vw,6rem); line-height:0.9; margin:0; color:#fff; }
        .hero-meta { margin-top:1rem; color:#aaa; font-size:0.85rem; display:flex; gap:1rem; flex-wrap:wrap; align-items:center; }
        .hero-premium-tag { background:linear-gradient(135deg,var(--gold),#e6a800); color:#000; font-size:0.7rem; font-weight:800; padding:4px 10px; border-radius:20px; }

        .article-content { max-width:740px; margin:0 auto; padding:3rem 2rem; color:#c8c0b8; font-size:1.15rem; line-height:1.8; }
        .article-content h2 { font-family:'Bebas Neue',sans-serif; font-size:2.5rem; color:var(--white); margin:3rem 0 1rem; border-left:4px solid var(--blue); padding-left:15px; }
        .article-content h3 { font-family:'Bebas Neue',sans-serif; font-size:1.8rem; color:#ddd; margin:2rem 0 0.75rem; }
        .article-content p { margin-bottom:1.8rem; }
        .article-content img { max-width:100%; border-radius:15px; margin:2rem 0; }
        .article-content blockquote { border-left:3px solid var(--blue); padding:1rem 1.5rem; background:#111; margin:2rem 0; border-radius:0 10px 10px 0; color:#aaa; font-style:italic; }
        .article-content ul,.article-content ol { padding-left:1.5rem; margin-bottom:1.5rem; }
        .article-content li { margin-bottom:0.5rem; }
        .article-content a { color:var(--blue); }
        .article-content strong { color:#fff; }
        .article-content table { width:100%; border-collapse:collapse; margin:1.5rem 0; }
        .article-content th,.article-content td { border:1px solid #333; padding:10px; text-align:left; }
        .article-content th { background:#111; color:var(--blue); }
        .article-content pre { background:#111; padding:1rem; border-radius:8px; overflow-x:auto; font-family:monospace; color:#0f0; }

        /* PAYWALL */
        .paywall-blur { position:relative; max-height:260px; overflow:hidden; }
        .paywall-blur::after { content:''; position:absolute; bottom:0; left:0; right:0; height:200px; background:linear-gradient(to bottom,transparent,var(--dark) 85%); }
        .paywall-box { max-width:740px; margin:0 auto; padding:0 2rem 3rem; text-align:center; }
        .paywall-icon { font-size:3rem; margin-bottom:1rem; }
        .paywall-title { font-family:'Bebas Neue',sans-serif; font-size:2.2rem; color:#fff; margin-bottom:0.5rem; }
        .paywall-sub { color:#888; margin-bottom:2rem; font-size:0.95rem; }
        .paywall-btns { display:flex; gap:12px; justify-content:center; flex-wrap:wrap; }
        .paywall-btn-premium { background:linear-gradient(135deg,var(--gold),#e6a800); color:#000; font-weight:800; padding:14px 28px; border-radius:14px; text-decoration:none; font-size:0.95rem; }
        .paywall-btn-login { background:#1c1c1e; color:#fff; font-weight:700; padding:14px 28px; border-radius:14px; text-decoration:none; font-size:0.95rem; border:1px solid #333; }

        /* PARTAGE */
        .share-bar { max-width:740px; margin:0 auto; padding:0 2rem 2rem; display:flex; gap:12px; flex-wrap:wrap; }
        .share-btn { display:inline-flex; align-items:center; gap:8px; padding:12px 20px; border-radius:50px; font-size:0.85rem; font-weight:700; text-decoration:none; color:#fff; border:none; cursor:pointer; }
        .share-wa { background:#25D366; }
        .share-tw { background:#1DA1F2; }
        .share-copy { background:#333; }

        /* ARTICLES SIMILAIRES */
        .similaires { max-width:740px; margin:0 auto; padding:0 2rem 3rem; }
        .similaires-title { font-family:'Bebas Neue',sans-serif; font-size:2rem; color:var(--blue); border-left:4px solid var(--blue); padding-left:15px; margin-bottom:1.5rem; }
        .sim-grid { display:grid; grid-template-columns:repeat(2,1fr); gap:15px; }
        .sim-card { background:var(--gray); border-radius:16px; overflow:hidden; text-decoration:none; display:block; color:inherit; border:0.5px solid #333; transition:transform 0.2s; }
        .sim-card:active { transform:scale(0.97); }
        .sim-img { width:100%; height:130px; object-fit:cover; }
        .sim-body { padding:12px; }
        .sim-tag { color:var(--blue); font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:1px; }
        .sim-title { font-size:14px; font-weight:700; color:#fff; margin:4px 0 0; line-height:1.3; }

        /* FORMULAIRES AUTH */
        .auth-wrap { max-width:420px; margin:60px auto; padding:0 20px 40px; }
        .auth-title { font-family:'Bebas Neue',sans-serif; font-size:2.8rem; color:#fff; margin-bottom:0.25rem; }
        .auth-sub { color:#888; margin-bottom:2rem; font-size:0.9rem; }
        .auth-card { background:#111; border:1px solid #222; border-radius:20px; padding:28px; }
        .auth-input { width:100%; padding:14px 16px; background:#1c1c1e; border:1px solid #333; color:#fff; border-radius:12px; font-size:1rem; margin-bottom:14px; box-sizing:border-box; }
        .auth-input:focus { outline:none; border-color:var(--blue); }
        .auth-btn { width:100%; padding:16px; background:linear-gradient(135deg,var(--blue),var(--purple)); color:#fff; font-weight:700; font-size:1rem; border:none; border-radius:14px; cursor:pointer; margin-top:4px; }
        .auth-link { display:block; text-align:center; margin-top:16px; color:#888; font-size:0.85rem; }
        .auth-link a { color:var(--blue); text-decoration:none; }
        .auth-error { background:rgba(230,48,34,0.1); border:1px solid rgba(230,48,34,0.3); color:#ff6b6b; padding:12px 16px; border-radius:10px; margin-bottom:16px; font-size:0.85rem; }
        .auth-success { background:rgba(34,197,94,0.1); border:1px solid rgba(34,197,94,0.3); color:#4ade80; padding:12px 16px; border-radius:10px; margin-bottom:16px; font-size:0.85rem; }

        /* PAGE PREMIUM */
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
        .pay-methods { display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-top:16px; }
        .pay-btn { padding:14px; border-radius:14px; font-weight:700; font-size:0.9rem; text-align:center; text-decoration:none; color:#fff; border:none; cursor:pointer; }
        .pay-wave { background:linear-gradient(135deg,#1a73e8,#0d47a1); }
        .pay-card { background:linear-gradient(135deg,#2d2d2d,#1a1a1a); border:1px solid #444; }

        /* COMPTE */
        .compte-wrap { max-width:600px; margin:0 auto; padding:30px 20px; }
        .compte-header { display:flex; align-items:center; gap:16px; margin-bottom:30px; }
        .compte-avatar { width:64px; height:64px; background:linear-gradient(135deg,var(--blue),var(--purple)); border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:1.8rem; font-weight:700; }
        .compte-info h2 { margin:0; font-size:1.3rem; }
        .compte-info p { margin:4px 0 0; color:#888; font-size:0.85rem; }
        .compte-stat-grid { display:grid; grid-template-columns:repeat(2,1fr); gap:12px; margin-bottom:24px; }
        .compte-stat { background:#111; border:1px solid #222; border-radius:14px; padding:18px; text-align:center; }
        .compte-stat-val { font-family:'Bebas Neue',sans-serif; font-size:2rem; color:var(--blue); }
        .compte-stat-lbl { font-size:0.75rem; color:#888; margin-top:4px; }

        /* ADMIN */
        .admin-list-item { background:#111; padding:12px 15px; margin-bottom:6px; border-radius:10px; display:flex; justify-content:space-between; align-items:center; gap:10px; flex-wrap:wrap; }
        .btn-edit { color:var(--blue); font-size:0.8rem; font-weight:700; text-decoration:none; }
        .btn-delete { background:none; border:none; color:var(--red); font-size:0.8rem; font-weight:700; cursor:pointer; padding:0; }

        .btn { display:block; background:linear-gradient(135deg,var(--blue),var(--purple)); color:#fff; padding:18px; text-align:center; border-radius:20px; text-decoration:none; font-weight:700; border:none; font-size:1rem; cursor:pointer; width:100%; box-sizing:border-box; }

        .footer-nav { position:fixed; bottom:0; left:0; width:100%; background:rgba(0,0,0,0.9); backdrop-filter:blur(15px); border-top:0.5px solid #333; display:flex; justify-content:space-around; padding:15px 0; z-index:1000; }
        .footer-nav a { color:#888; text-decoration:none; font-size:0.75rem; font-weight:700; text-transform:uppercase; }

        input,textarea,select { width:100%; padding:15px; margin:10px 0; background:#1c1c1e; border:1px solid #333; color:#fff; border-radius:12px; font-size:16px; box-sizing:border-box; }
        label { color:#888; font-size:0.8rem; display:block; margin-top:10px; }

        /* SEARCH */
        .search-wrap { background:#000; padding:12px 20px; border-bottom:0.5px solid #222; }
        .search-box { display:flex; align-items:center; background:#1c1c1e; border-radius:50px; padding:0 16px; gap:10px; max-width:600px; margin:0 auto; border:1px solid #333; }
        .search-box input { background:none; border:none; color:#fff; font-size:0.95rem; padding:12px 0; margin:0; width:100%; outline:none; }
        .search-box input::placeholder { color:#666; }
        .search-box span { color:#666; font-size:1.1rem; }
        .search-results { max-width:800px; margin:0 auto; padding:0 20px 10px; display:none; }
        .search-results.visible { display:block; }
        .search-item { display:flex; align-items:center; gap:12px; padding:12px; background:#111; border-radius:12px; margin-bottom:8px; text-decoration:none; color:#fff; border:0.5px solid #333; }
        .search-item img { width:60px; height:60px; object-fit:cover; border-radius:8px; flex-shrink:0; }
        .search-item-tag { color:var(--blue); font-size:10px; font-weight:700; text-transform:uppercase; }
        .search-item-title { font-size:0.9rem; font-weight:700; margin-top:2px; }
        .search-empty { text-align:center; color:#666; padding:20px; font-size:0.9rem; }

        /* SCROLL TOP */
        .scroll-top { position:fixed; bottom:90px; right:20px; width:44px; height:44px; background:linear-gradient(135deg,var(--blue),var(--purple)); border-radius:50%; display:flex; align-items:center; justify-content:center; cursor:pointer; border:none; color:#fff; font-size:1.1rem; z-index:999; opacity:0; pointer-events:none; transition:opacity 0.3s; box-shadow:0 4px 15px rgba(0,210,255,0.3); }
        .scroll-top.visible { opacity:1; pointer-events:all; }

        /* 404 */
        .page-404 { text-align:center; padding:5rem 2rem; }
        .page-404 .big { font-family:'Bebas Neue',sans-serif; font-size:clamp(6rem,20vw,12rem); color:var(--blue); line-height:1; margin:0; opacity:0.15; }
        .page-404 h2 { font-family:'Bebas Neue',sans-serif; font-size:2rem; margin:-2rem 0 1rem; color:#fff; }
        .page-404 p { color:#888; margin-bottom:2rem; }

        /* VUES */
        .views-badge { display:inline-flex; align-items:center; gap:5px; color:#888; font-size:0.82rem; }

        /* PWA */
        .pwa-banner { display:none; position:fixed; bottom:75px; left:0; right:0; margin:0 15px; background:#1c1c1e; border:1px solid #333; border-radius:16px; padding:14px 18px; z-index:998; align-items:center; gap:12px; box-shadow:0 8px 30px rgba(0,0,0,0.5); }
        .pwa-banner.show { display:flex; }
        .pwa-banner-text { flex:1; font-size:0.85rem; color:#ccc; }
        .pwa-banner-text strong { color:#fff; display:block; margin-bottom:2px; }
        .pwa-btn-install { background:linear-gradient(135deg,var(--blue),var(--purple)); color:#fff; border:none; padding:8px 16px; border-radius:20px; font-weight:700; font-size:0.8rem; cursor:pointer; white-space:nowrap; }
        .pwa-btn-close { background:none; border:none; color:#666; font-size:1.3rem; cursor:pointer; padding:0; line-height:1; }

        @media (max-width:500px) { .sim-grid { grid-template-columns:1fr; } .pay-methods { grid-template-columns:1fr; } }
    </style>
</head>
<body>
    <!-- HEADER -->
    <header>
        <button class="header-menu-btn" onclick="openSidebar()">☰</button>
        <a href="/" class="logo">METTA<span>BYTE</span></a>
        <div style="width:34px;"></div>
    </header>

    <!-- MENU LATÉRAL -->
    <div class="sidebar-overlay" id="sidebarOverlay" onclick="closeSidebar()"></div>
    <div class="sidebar" id="sidebar">
        <div class="sidebar-header">
            <span class="sidebar-logo">METTA<span>BYTE</span></span>
            <button class="sidebar-close" onclick="closeSidebar()">×</button>
        </div>
        <div class="sidebar-body">
            %MENU_USER_HTML%
            <hr style="border:0.5px solid #222; margin:16px 0;">
            <div class="sidebar-section-title">Navigation</div>
            <a href="/" class="menu-link">🏠 Accueil</a>
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
        <a href="mailto:mettabytesite@gmail.com">Contact</a>
        <a href="/privacy">Privacy</a>
    </div>

    <button class="scroll-top" id="scrollTopBtn" onclick="window.scrollTo({top:0,behavior:'smooth'})">↑</button>

    <div class="pwa-banner" id="pwaBanner">
        <span style="font-size:1.5rem;">📱</span>
        <div class="pwa-banner-text">
            <strong>Installer METTABYTE</strong>
            Accès rapide depuis ton écran d'accueil
        </div>
        <button class="pwa-btn-install" id="pwaInstallBtn">Installer</button>
        <button class="pwa-btn-close" onclick="document.getElementById('pwaBanner').classList.remove('show');localStorage.setItem('pwa_dismissed','1')">×</button>
    </div>

    <script>
    // ── SIDEBAR ──
    // Attendre que le DOM soit chargé avant d'attacher les events
    document.addEventListener('DOMContentLoaded', function() {

        // SIDEBAR
        var sidebar        = document.getElementById('sidebar');
        var sidebarOverlay = document.getElementById('sidebarOverlay');
        var menuBtn        = document.querySelector('.header-menu-btn');
        var closeBtn       = document.querySelector('.sidebar-close');

        function openSidebar() {
            if (!sidebar) return;
            sidebar.classList.add('open');
            sidebarOverlay.classList.add('open');
            document.body.style.overflow = 'hidden';
        }
        function closeSidebar() {
            if (!sidebar) return;
            sidebar.classList.remove('open');
            sidebarOverlay.classList.remove('open');
            document.body.style.overflow = '';
        }

        if (menuBtn)        menuBtn.addEventListener('click', openSidebar);
        if (closeBtn)       closeBtn.addEventListener('click', closeSidebar);
        if (sidebarOverlay) sidebarOverlay.addEventListener('click', closeSidebar);

        // SCROLL TOP
        var scrollBtn = document.getElementById('scrollTopBtn');
        if (scrollBtn) {
            window.addEventListener('scroll', function() {
                scrollBtn.classList.toggle('visible', window.scrollY > 400);
            });
            scrollBtn.addEventListener('click', function() {
                window.scrollTo({top: 0, behavior: 'smooth'});
            });
        }

        // ── RECHERCHE ──
        var searchInput   = document.getElementById('searchInput');
        var searchResults = document.getElementById('searchResults');
        if (searchInput && searchResults) {
            var timer;
            searchInput.addEventListener('input', function() {
                clearTimeout(timer);
                var q = this.value.trim();
                if (q.length < 2) {
                    searchResults.style.display = 'none';
                    searchResults.innerHTML = '';
                    return;
                }
                timer = setTimeout(function() {
                    fetch('/search?q=' + encodeURIComponent(q))
                        .then(function(r) { return r.json(); })
                        .then(function(data) {
                            if (!data.length) {
                                searchResults.innerHTML = '<div class="search-empty">Aucun résultat pour "' + q + '"</div>';
                            } else {
                                searchResults.innerHTML = data.map(function(a) {
                                    var badge = a.premium ? ' 👑' : '';
                                    var img   = a.img_url ? '<img src="' + a.img_url + '" style="width:56px;height:56px;object-fit:cover;border-radius:8px;flex-shrink:0;">' : '';
                                    return '<a href="/article/' + a.id + '" class="search-item">'
                                         + img
                                         + '<div><div class="search-item-tag">' + (a.categorie || '') + badge + '</div>'
                                         + '<div class="search-item-title">' + a.titre + '</div></div></a>';
                                }).join('');
                            }
                            searchResults.style.display = 'block';
                        })
                        .catch(function() {
                            searchResults.innerHTML = '<div class="search-empty">Erreur de recherche.</div>';
                            searchResults.style.display = 'block';
                        });
                }, 350);
            });

            document.addEventListener('click', function(e) {
                if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
                    searchResults.style.display = 'none';
                }
            });
        }

        // ── AUTO-REFRESH (mise à jour automatique) ──
        // Vérifie toutes les 30 secondes si de nouveaux articles ont été publiés
        // Si oui, recharge la page silencieusement (seulement sur l'accueil)
        if (window.location.pathname === '/') {
            var lastCheck = Date.now();
            setInterval(function() {
                fetch('/api/last-article')
                    .then(function(r) { return r.json(); })
                    .then(function(data) {
                        if (data.ts && data.ts * 1000 > lastCheck) {
                            // Nouveau contenu détecté — recharge sans scroller
                            var scrollY = window.scrollY;
                            location.reload();
                        }
                    })
                    .catch(function() {});
            }, 30000); // toutes les 30 secondes
        }

        // PWA
        var deferredPrompt;
        window.addEventListener('beforeinstallprompt', function(e) {
            e.preventDefault();
            deferredPrompt = e;
            if (!localStorage.getItem('pwa_dismissed')) {
                setTimeout(function() {
                    var banner = document.getElementById('pwaBanner');
                    if (banner) banner.classList.add('show');
                }, 3000);
            }
        });
        var pwaBtn = document.getElementById('pwaInstallBtn');
        if (pwaBtn) {
            pwaBtn.addEventListener('click', function() {
                if (deferredPrompt) {
                    deferredPrompt.prompt();
                    deferredPrompt.userChoice.then(function() {
                        var banner = document.getElementById('pwaBanner');
                        if (banner) banner.classList.remove('show');
                        deferredPrompt = null;
                    });
                }
            });
        }

    }); // fin DOMContentLoaded
    </script>
</body>
</html>"""


# ─────────────────────────────────────────────
# ROUTES PRINCIPALES
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

    cats_list = ["Tous", "Tech", "Science", "IA", "Espace", "Santé", "Sport"]
    nav = '<div class="nav-container"><nav class="nav-cats">' + "".join([
        f'<a href="/?cat={c}" class="cat {"active" if c == cat else ""}">{c}</a>'
        for c in cats_list
    ]) + '</nav></div>'
    nav += """
    <div class="search-wrap">
        <div class="search-box">
            <span>🔍</span>
            <input type="text" id="searchInput" placeholder="Rechercher un article...">
        </div>
        <div class="search-results" id="searchResults"></div>
    </div>
    """

    cards = "".join([
        f'<a href="/article/{a["id"]}" class="card">'
        + ('<div class="premium-badge">👑 Premium</div>' if a.get("premium") else '')
        + f'<img src="{a.get("img_url", LOGO_URL)}" class="card-img" loading="lazy">'
        f'<div class="card-body">'
        f'<div class="card-tag">{a.get("categorie","TECH")} · {reading_time(a.get("texte",""))} min</div>'
        f'<h2 class="card-title">{a["titre"]}</h2>'
        f'</div></a>'
        for a in articles
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

    # Articles similaires
    try:
        cat = art.get("categorie", "Tech")
        rs = requests.get(SUPABASE_URL, headers=HEADERS, params={"categorie": "eq." + cat, "order": "ts.desc", "limit": "5"})
        similaires = [a for a in rs.json() if str(a["id"]) != str(id)][:4]
    except:
        similaires = []

    sim_cards = "".join([
        f'<a href="/article/{s["id"]}" class="sim-card">'
        f'<img src="{s.get("img_url", LOGO_URL)}" class="sim-img" loading="lazy">'
        f'<div class="sim-body">'
        f'<div class="sim-tag">{s.get("categorie","")} {"👑" if s.get("premium") else ""}</div>'
        f'<div class="sim-title">{s["titre"]}</div>'
        f'</div></a>'
        for s in similaires
    ])
    sim_section = f'<div class="similaires"><div class="similaires-title">À lire aussi</div><div class="sim-grid">{sim_cards}</div></div>' if sim_cards else ""

    read_min   = reading_time(art.get("texte", ""))
    article_url = request.url
    vues       = art.get("vues", 0)

    premium_tag = '<span class="hero-premium-tag">👑 Premium</span>' if is_premium_art else ""

    share_section = f"""
    <div class="share-bar">
        <a href="https://wa.me/?text={art['titre']}%20{article_url}" target="_blank" class="share-btn share-wa">📲 WhatsApp</a>
        <a href="https://twitter.com/intent/tweet?text={art['titre']}&url={article_url}" target="_blank" class="share-btn share-tw">🐦 Twitter / X</a>
        <button onclick="navigator.clipboard.writeText('{article_url}');this.innerText='✅ Copié !'" class="share-btn share-copy">🔗 Copier le lien</button>
    </div>
    """

    # Contenu ou paywall
    if is_premium_art and not is_premium_user:
        texte_html = f"""
        <div class="paywall-blur">{art["texte"]}</div>
        <div class="paywall-box">
            <div class="paywall-icon">👑</div>
            <div class="paywall-title">Article Premium</div>
            <p class="paywall-sub">Cet article est réservé aux membres Premium. Débloquez l'accès pour seulement <strong>1€ / mois</strong>.</p>
            <div class="paywall-btns">
                <a href="/premium" class="paywall-btn-premium">✨ Passer Premium</a>
                <a href="/connexion?next=/article/{id}" class="paywall-btn-login">🔑 Se connecter</a>
            </div>
        </div>
        """
    else:
        texte_html = art["texte"]

    content = f"""
    <div class="article-hero" style="background-image:url('{art.get('img_url', LOGO_URL)}')">
        <div class="hero-content">
            <h1 class="hero-title">{art["titre"]}</h1>
            <div class="hero-meta">
                <span>🏷️ {art.get("categorie","Tech")}</span>
                <span>⏱️ {read_min} min de lecture</span>
                {premium_tag}
            </div>
        </div>
    </div>
    <script>
        // Comptage silencieux — non affiché au lecteur
        fetch('/vue/{art["id"]}', {{method:'POST'}});
    </script>
    <div class="article-content">
        {texte_html}
        <br>
        <a href="/" class="btn" style="background:#222;width:fit-content;padding:12px 30px;display:inline-block;border-radius:15px;">← RETOUR</a>
    </div>
    {share_section}
    {sim_section}
    """
    return render_page(content, art['titre'], meta_desc=art['titre'] + " — METTABYTE")


# ─────────────────────────────────────────────
# AUTH — INSCRIPTION / CONNEXION
# ─────────────────────────────────────────────

@app.route('/inscription', methods=['GET', 'POST'])
def inscription():
    error = ""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        pw    = request.form.get('password', '')
        pw2   = request.form.get('password2', '')
        if not email or not pw:
            error = "Email et mot de passe requis."
        elif pw != pw2:
            error = "Les mots de passe ne correspondent pas."
        elif len(pw) < 6:
            error = "Le mot de passe doit faire au moins 6 caractères."
        else:
            # Vérif doublon
            try:
                chk = requests.get(SUPABASE_URL_USR + "?email=eq." + email, headers=HEADERS)
                if chk.json():
                    error = "Cet email est déjà utilisé."
                else:
                    data = {"email": email, "password": hash_pw(pw), "premium": False, "ts": int(time.time())}
                    res  = requests.post(SUPABASE_URL_USR, headers=HEADERS, json=data)
                    new_user = res.json()[0] if res.json() else None
                    if new_user:
                        session['user_id'] = new_user['id']
                        return redirect('/')
                    else:
                        error = "Erreur lors de la création du compte."
            except Exception as e:
                error = f"Erreur détaillée : {str(e)}"

    error_html   = f'<div class="auth-error">{error}</div>' if error else ""
    content = f"""
    <div class="auth-wrap">
        <div class="auth-title">Créer un compte</div>
        <p class="auth-sub">Gratuit · Sans engagement · Accès aux articles Premium possible</p>
        <div class="auth-card">
            {error_html}
            <form method="post">
                <input class="auth-input" type="email" name="email" placeholder="Ton adresse email" required>
                <input class="auth-input" type="password" name="password" placeholder="Mot de passe (6 caractères min)" required>
                <input class="auth-input" type="password" name="password2" placeholder="Confirmer le mot de passe" required>
                <button type="submit" class="auth-btn">✉️ Créer mon compte</button>
            </form>
            <a href="/connexion" class="auth-link">Déjà un compte ? <a href="/connexion" style="color:var(--blue)">Se connecter</a></a>
        </div>
    </div>
    """
    return render_page(content, "Inscription — METTABYTE")


@app.route('/connexion', methods=['GET', 'POST'])
def connexion():
    error  = ""
    next_url = request.args.get('next', '/')
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        pw    = request.form.get('password', '')
        try:
            r = requests.get(SUPABASE_URL_USR + "?email=eq." + email, headers=HEADERS)
            users = r.json()
            if users and users[0]['password'] == hash_pw(pw):
                session['user_id'] = users[0]['id']
                return redirect(request.form.get('next', '/'))
            else:
                error = "Email ou mot de passe incorrect."
        except:
            error = "Erreur serveur."

    error_html = f'<div class="auth-error">{error}</div>' if error else ""
    content = f"""
    <div class="auth-wrap">
        <div class="auth-title">Connexion</div>
        <p class="auth-sub">Bon retour sur METTABYTE</p>
        <div class="auth-card">
            {error_html}
            <form method="post">
                <input type="hidden" name="next" value="{next_url}">
                <input class="auth-input" type="email" name="email" placeholder="Ton adresse email" required>
                <input class="auth-input" type="password" name="password" placeholder="Mot de passe" required>
                <button type="submit" class="auth-btn">🔑 Se connecter</button>
            </form>
            <a href="/inscription" class="auth-link">Pas encore de compte ? <a href="/inscription" style="color:var(--blue)">S'inscrire gratuitement</a></a>
        </div>
    </div>
    """
    return render_page(content, "Connexion — METTABYTE")


@app.route('/deconnexion')
def deconnexion():
    session.clear()
    return redirect('/')


# ─────────────────────────────────────────────
# PAGE PREMIUM & PAIEMENT STRIPE
# ─────────────────────────────────────────────

# Clés Stripe — à renseigner dans les variables d'environnement Render
STRIPE_SECRET_KEY      = os.environ.get("STRIPE_SECRET_KEY")       # sk_live_...
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY")  # pk_live_...
STRIPE_WEBHOOK_SECRET  = os.environ.get("STRIPE_WEBHOOK_SECRET")   # whsec_...
STRIPE_PRICE_ID        = os.environ.get("STRIPE_PRICE_ID")         # price_... (1€/mois)


@app.route('/premium')
def premium():
    user = get_user()
    if user and user.get('premium'):
        content = """
        <div class="premium-hero">
            <div class="premium-crown">👑</div>
            <div class="premium-title">Tu es déjà Premium !</div>
            <p class="premium-sub">Merci de soutenir METTABYTE. Tu as accès à tous les articles exclusifs.</p>
            <a href="/" style="display:inline-block;margin-top:2rem;background:#1c1c1e;color:#fff;padding:14px 28px;border-radius:14px;text-decoration:none;font-weight:700;">← Retour aux articles</a>
        </div>
        """
        return render_page(content, "Premium — METTABYTE")

    not_logged_html = """
        <p style="color:#888;font-size:0.85rem;margin-bottom:1rem;">Connecte-toi pour continuer.</p>
        <a href="/connexion?next=/premium" class="paywall-btn-premium" style="display:block;text-align:center;margin-bottom:10px;">🔑 Se connecter</a>
        <a href="/inscription" class="paywall-btn-login" style="display:block;text-align:center;">✉️ Créer un compte</a>
    """
    stripe_btn_html = f"""
        <p style="color:#888;font-size:0.85rem;margin-bottom:1rem;">Paiement sécurisé par Stripe 🔒</p>
        <a href="/checkout" class="paywall-btn-premium" style="display:block;text-align:center;font-size:1rem;padding:16px;">
            💳 Payer 1€ / mois par carte
        </a>
        <p style="color:#555;font-size:0.72rem;text-align:center;margin-top:10px;">Visa · Mastercard · American Express · Annulable à tout moment</p>
    """

    content = f"""
    <div class="premium-hero">
        <div class="premium-crown">👑</div>
        <div class="premium-title">Passe Premium</div>
        <p class="premium-sub">Accède à tous les articles exclusifs pour seulement <strong>1€ / mois</strong>.</p>
    </div>
    <div class="container" style="padding-bottom:40px;">
        <div class="pricing-card">
            <div class="pricing-price">1€</div>
            <div class="pricing-period">par mois · paiement sécurisé Stripe</div>
            <ul class="pricing-features">
                <li>Accès illimité aux articles Premium 👑</li>
                <li>Contenu exclusif chaque semaine</li>
                <li>Badge Premium sur ton profil</li>
                <li>Annulable à tout moment</li>
            </ul>
            {not_logged_html if not user else stripe_btn_html}
        </div>
    </div>
    """
    return render_page(content, "Premium — METTABYTE")


@app.route('/checkout')
def checkout():
    """Crée une session Stripe Checkout et redirige l'utilisateur."""
    user = get_user()
    if not user:
        return redirect('/connexion?next=/premium')
    if user.get('premium'):
        return redirect('/premium')

    try:
        import stripe
        stripe.api_key = STRIPE_SECRET_KEY
        base_url = request.url_root.rstrip('/')

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            mode='subscription',
            line_items=[{'price': STRIPE_PRICE_ID, 'quantity': 1}],
            customer_email=user['email'],
            metadata={'user_id': str(user['id'])},
            success_url=base_url + '/premium/succes?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=base_url + '/premium',
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        content = f"""
        <div class="auth-wrap" style="text-align:center;">
            <div class="auth-title" style="color:var(--red);">Erreur</div>
            <p class="auth-sub">Impossible d'initialiser le paiement : {str(e)}</p>
            <a href="/premium" class="btn" style="max-width:200px;margin:0 auto;">← Retour</a>
        </div>
        """
        return render_page(content, "Erreur — METTABYTE")


@app.route('/premium/succes')
def premium_succes():
    """Page de succès après paiement Stripe — activation Premium."""
    user = get_user()
    session_id = request.args.get('session_id', '')

    if user and session_id:
        try:
            import stripe
            stripe.api_key = STRIPE_SECRET_KEY
            checkout_session = stripe.checkout.Session.retrieve(session_id)
            # Vérif que le paiement appartient bien à cet utilisateur
            if checkout_session.customer_email == user['email'] and checkout_session.payment_status == 'paid':
                requests.patch(
                    SUPABASE_URL_USR + "?id=eq." + str(user['id']),
                    headers=HEADERS,
                    json={"premium": True, "stripe_customer": checkout_session.customer}
                )
        except:
            pass

    content = """
    <div style="text-align:center; padding:5rem 2rem;">
        <div style="font-size:4rem; margin-bottom:1rem;">🎉</div>
        <h1 style="font-family:'Bebas Neue',sans-serif; font-size:3rem; color:var(--gold);">Bienvenue dans Premium !</h1>
        <p style="color:#aaa; margin-bottom:0.5rem;">Ton accès a été activé avec succès.</p>
        <p style="color:#666; font-size:0.85rem; margin-bottom:2rem;">Tu peux maintenant lire tous les articles exclusifs 👑</p>
        <a href="/" class="btn" style="max-width:260px; margin:0 auto; display:block;">← Découvrir les articles</a>
    </div>
    """
    return render_page(content, "Premium activé — METTABYTE")


@app.route('/stripe/webhook', methods=['POST'])
def stripe_webhook():
    """
    Webhook Stripe pour activer Premium automatiquement
    même si l'utilisateur ferme le navigateur après paiement.
    À configurer dans ton dashboard Stripe :
    https://dashboard.stripe.com/webhooks → Endpoint URL : https://ton-site.com/stripe/webhook
    Événements à écouter : checkout.session.completed
    """
    try:
        import stripe
        stripe.api_key = STRIPE_SECRET_KEY
        payload    = request.get_data()
        sig_header = request.headers.get('Stripe-Signature', '')
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)

        if event['type'] == 'checkout.session.completed':
            sess    = event['data']['object']
            uid     = sess.get('metadata', {}).get('user_id')
            if uid and sess.get('payment_status') == 'paid':
                requests.patch(
                    SUPABASE_URL_USR + "?id=eq." + str(uid),
                    headers=HEADERS,
                    json={"premium": True, "stripe_customer": sess.get('customer')}
                )
    except Exception as e:
        return Response(str(e), status=400)
    return Response("ok", status=200)


# ─────────────────────────────────────────────
# PAGE COMPTE UTILISATEUR
# ─────────────────────────────────────────────

@app.route('/compte')
def compte():
    user = get_user()
    if not user:
        return redirect('/connexion?next=/compte')
    name = user['email'].split('@')[0]
    is_premium = user.get('premium', False)
    content = f"""
    <div class="compte-wrap">
        <div class="compte-header">
            <div class="compte-avatar">{name[0].upper()}</div>
            <div class="compte-info">
                <h2>{name}</h2>
                <p>{user['email']}</p>
            </div>
        </div>
        <div class="compte-stat-grid">
            <div class="compte-stat">
                <div class="compte-stat-val">{'👑' if is_premium else '🆓'}</div>
                <div class="compte-stat-lbl">{'Premium actif' if is_premium else 'Compte gratuit'}</div>
            </div>
            <div class="compte-stat">
                <div class="compte-stat-val" style="font-size:1rem;">{'Illimité' if is_premium else 'Limité'}</div>
                <div class="compte-stat-lbl">Accès articles</div>
            </div>
        </div>
        {'<div class="menu-premium-badge" style="margin-bottom:16px;">👑 Membre Premium actif — Merci !</div>' if is_premium else '<a href="/premium" class="menu-upgrade-btn" style="display:block;text-align:center;margin-bottom:16px;">✨ Passer Premium — 1€/mois</a>'}
        <a href="/deconnexion" class="btn" style="background:#1c1c1e; border:1px solid #333; margin-top:20px;">🚪 Se déconnecter</a>
    </div>
    """
    return render_page(content, "Mon compte — METTABYTE")


# ─────────────────────────────────────────────
# RECHERCHE / VUES / UTILITAIRES
# ─────────────────────────────────────────────

@app.route('/api/last-article')
def api_last_article():
    """Retourne le timestamp du dernier article publié — utilisé pour l'auto-refresh."""
    try:
        r = requests.get(SUPABASE_URL, headers=HEADERS, params={"order": "ts.desc", "limit": "1", "select": "ts"})
        data = r.json()
        ts = data[0]['ts'] if data else 0
    except:
        ts = 0
    return Response(json.dumps({"ts": ts}), mimetype='application/json')


@app.route('/search')
def search():
    q = request.args.get('q', '').strip().lower()
    if not q or len(q) < 2:
        return Response("[]", mimetype='application/json')
    try:
        r = requests.get(SUPABASE_URL, headers=HEADERS, params={"order": "ts.desc"})
        all_arts = r.json() if isinstance(r.json(), list) else []
        results = [
            {"id": a["id"], "titre": a["titre"], "categorie": a.get("categorie",""), "img_url": a.get("img_url",""), "premium": a.get("premium", False)}
            for a in all_arts
            if q in a.get("titre","").lower() or q in a.get("categorie","").lower()
        ][:6]
    except:
        results = []
    return Response(json.dumps(results, ensure_ascii=False), mimetype='application/json')


@app.route('/vue/<id>', methods=['POST'])
def count_vue(id):
    try:
        r = requests.get(SUPABASE_URL + "?id=eq." + str(id), headers=HEADERS)
        art = r.json()[0]
        vues = int(art.get("vues", 0)) + 1
        requests.patch(SUPABASE_URL + "?id=eq." + str(id), headers=HEADERS, json={"vues": vues})
        return Response(str(vues), mimetype='text/plain')
    except:
        return Response("0", mimetype='text/plain')


@app.errorhandler(404)
def page_404(e):
    content = """
    <div class="page-404">
        <div class="big">404</div>
        <h2>Page introuvable</h2>
        <p>Cette page n'existe pas ou a été supprimée.</p>
        <a href="/" class="btn" style="max-width:250px;margin:0 auto;display:block;">← RETOUR À L'ACCUEIL</a>
    </div>
    """
    return render_page(content, "404 — METTABYTE"), 404


@app.route('/manifest.json')
def manifest():
    data = {"name":"METTABYTE","short_name":"METTABYTE","description":"Tech, IA, Science, Espace","start_url":"/","display":"standalone","background_color":"#050505","theme_color":"#00d2ff","icons":[{"src":LOGO_URL,"sizes":"192x192","type":"image/png"}]}
    return Response(json.dumps(data), mimetype='application/json')


@app.route('/ads.txt')
def ads_txt():
    return Response(f"google.com, {ADSENSE_ID}, DIRECT, f08c47fec0942fa0", mimetype='text/plain')


@app.route('/sitemap.xml')
def sitemap():
    base_url = request.url_root.rstrip('/')
    try:
        r = requests.get(SUPABASE_URL, headers=HEADERS, params={"select": "id"})
        articles = r.json() if isinstance(r.json(), list) else []
    except:
        articles = []
    xml = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    xml += f'<url><loc>{base_url}/</loc><priority>1.0</priority></url>'
    for a in articles:
        xml += f'<url><loc>{base_url}/article/{a["id"]}</loc><priority>0.8</priority></url>'
    xml += '</urlset>'
    return Response(xml, mimetype='text/xml')


@app.route('/privacy')
def privacy():
    content = """
    <div class="container">
        <h1 style="font-family:'Bebas Neue';font-size:3rem;color:var(--blue);">Confidentialité</h1>
        <h2 style="color:var(--blue);font-size:1.6rem;margin-top:30px;">Introduction</h2>
        <p style="color:#ccc;">Chez <strong>METTABYTE</strong>, la protection de la vie privée de nos visiteurs est l'une de nos priorités.</p>
        <h2 style="color:var(--blue);font-size:1.6rem;margin-top:30px;">Fichiers journaux</h2>
        <p style="color:#ccc;">Nous collectons les adresses IP, le type de navigateur, le FAI et l'horodatage à des fins d'analyse uniquement.</p>
        <h2 style="color:var(--blue);font-size:1.6rem;margin-top:30px;">Publicités (Google AdSense)</h2>
        <p style="color:#ccc;">METTABYTE utilise Google AdSense. Google peut utiliser des cookies pour personnaliser les annonces.</p>
        <a href="/" style="background:#222;margin-top:30px;width:fit-content;padding:12px 30px;display:inline-block;border-radius:15px;text-decoration:none;color:#fff;font-weight:700;">← RETOUR</a>
    </div>
    """
    return render_page(content, "Confidentialité — METTABYTE")


# ─────────────────────────────────────────────
# ADMIN
# ─────────────────────────────────────────────

@app.route('/' + ADMIN_PATH, methods=['GET', 'POST'])
def admin():
    if request.method == 'POST' and request.form.get('password') == ADMIN_PASS_ENV:
        session['logged_in'] = True
    if not session.get('logged_in'):
        return render_page("""
        <div class="container" style="text-align:center;padding-top:100px;">
            <form method="post">
                <h1 style="font-family:'Bebas Neue';font-size:3rem;">Studio Admin</h1>
                <input type="password" name="password" placeholder="Mot de passe" style="max-width:300px;margin:20px auto;">
                <button type="submit" class="btn" style="max-width:300px;margin:10px auto;">ENTRER</button>
            </form>
        </div>
        """, "Admin — METTABYTE")

    # Suppression
    if request.method == 'POST' and request.form.get('action') == 'delete':
        del_id = request.form.get('del_id')
        if del_id:
            requests.delete(SUPABASE_URL + "?id=eq." + del_id, headers=HEADERS)
        return redirect('/' + ADMIN_PATH)

    # Activer/désactiver Premium d'un user
    if request.method == 'POST' and request.form.get('action') == 'toggle_premium':
        uid  = request.form.get('uid')
        val  = request.form.get('val') == 'true'
        if uid:
            requests.patch(SUPABASE_URL_USR + "?id=eq." + uid, headers=HEADERS, json={"premium": val})
        return redirect('/' + ADMIN_PATH + '#users')

    edit_id = request.args.get('edit')
    art = None
    if edit_id:
        res = requests.get(SUPABASE_URL + "?id=eq." + str(edit_id), headers=HEADERS)
        if res.json():
            art = res.json()[0]

    if request.method == 'POST' and 'titre' in request.form:
        data = {
            "titre":     request.form['titre'],
            "texte":     request.form['texte'],
            "img_url":   request.form['img_url'],
            "categorie": request.form['categorie'],
            "premium":   request.form.get('premium') == 'on',
            "ts":        int(time.time())
        }
        tid = request.form.get('id')
        if tid:
            requests.patch(SUPABASE_URL + "?id=eq." + tid, headers=HEADERS, json=data)
        else:
            requests.post(SUPABASE_URL, headers=HEADERS, json=data)
        return redirect('/' + ADMIN_PATH)

    r_list   = requests.get(SUPABASE_URL, headers=HEADERS, params={"order": "ts.desc"})
    all_arts = r_list.json() if isinstance(r_list.json(), list) else []

    # Liste utilisateurs
    try:
        ru = requests.get(SUPABASE_URL_USR, headers=HEADERS, params={"order": "ts.desc"})
        all_users = ru.json() if isinstance(ru.json(), list) else []
    except:
        all_users = []

    def build_art_item(a):
        premium_span = '<span style="background:rgba(245,197,24,0.1);border:1px solid rgba(245,197,24,0.3);color:#f5c518;font-size:0.7rem;font-weight:700;padding:3px 9px;border-radius:20px;">👑 Premium</span>' if a.get("premium") else ''
        crown = "👑 " if a.get("premium") else ""
        vues = a.get("vues", 0)
        vue_label = f"👁️ {vues} vue{'s' if vues > 1 else ''}"
        return (
            '<div class="admin-list-item">'
            '<div style="flex:1;min-width:0;">'
            f'<div style="color:#ccc;font-size:0.9rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{crown}{a["titre"][:50]}...</div>'
            '<div style="margin-top:5px;display:flex;gap:8px;align-items:center;flex-wrap:wrap;">'
            f'<span style="background:#1a1a1e;border:1px solid #333;color:#00d2ff;font-size:0.7rem;font-weight:700;padding:3px 9px;border-radius:20px;">{a.get("categorie","")}</span>'
            f'<span style="background:#1a1a1e;border:1px solid #333;color:#aaa;font-size:0.7rem;padding:3px 9px;border-radius:20px;">{vue_label}</span>'
            f'{premium_span}'
            '</div></div>'
            '<div style="display:flex;gap:10px;align-items:center;flex-shrink:0;">'
            f'<a href="/{ADMIN_PATH}?edit={a["id"]}" class="btn-edit">✏️ Modifier</a>'
            '<form method="post" style="margin:0;" onsubmit="return confirm(\'Supprimer cet article ?\')">'
            f'<input type="hidden" name="action" value="delete"><input type="hidden" name="del_id" value="{a["id"]}">'
            '<button type="submit" class="btn-delete">🗑️</button>'
            '</form></div></div>'
        )

    list_html = "<h2 style='font-family:Bebas Neue;color:var(--blue);margin-top:40px;'>Articles publiés</h2>" + "".join([
        build_art_item(a) for a in all_arts
    ])

    users_html = '<h2 id="users" style="font-family:Bebas Neue;color:var(--blue);margin-top:40px;">Utilisateurs</h2>' + "".join([
        f'<div class="admin-list-item">'
        f'<span style="color:#ccc;font-size:0.85rem;">{"👑 " if u.get("premium") else ""}{u["email"]}</span>'
        f'<form method="post" style="margin:0;">'
        f'<input type="hidden" name="action" value="toggle_premium">'
        f'<input type="hidden" name="uid" value="{u["id"]}">'
        f'<input type="hidden" name="val" value="{"false" if u.get("premium") else "true"}">'
        f'<button type="submit" style="background:{"rgba(245,197,24,0.15)" if u.get("premium") else "#1a1a1e"};border:1px solid {"var(--gold)" if u.get("premium") else "#333"};color:{"var(--gold)" if u.get("premium") else "#888"};padding:6px 12px;border-radius:8px;cursor:pointer;font-size:0.75rem;font-weight:700;">'
        f'{"Retirer Premium" if u.get("premium") else "Activer Premium"}</button>'
        f'</form></div>'
        for u in all_users
    ]) if all_users else '<p style="color:#555;">Aucun utilisateur inscrit.</p>'

    cats_options = "".join([
        f'<option {"selected" if art and art.get("categorie") == c else ""}>{c}</option>'
        for c in ["Tech", "Science", "IA", "Espace", "Santé", "Sport"]
    ])
    texte_val  = art['texte'].replace('</textarea>', '&lt;/textarea&gt;') if art else ''
    is_premium = art.get('premium', False) if art else False

    form = f"""
    <div class="container">
        <h1 style="font-family:'Bebas Neue';font-size:2.5rem;">{"✏️ MODIFIER" if edit_id else "✍️ NOUVEL ARTICLE"}</h1>
        <form method="post">
            <input type="hidden" name="id" value="{art['id'] if art else ''}">
            <label>Titre</label>
            <input name="titre" placeholder="Titre de l'article" value="{art['titre'] if art else ''}" required>
            <label>URL image de couverture</label>
            <input name="img_url" placeholder="https://..." value="{art.get('img_url','') if art else ''}">
            <label>Catégorie</label>
            <select name="categorie">{cats_options}</select>
            <label style="display:flex;align-items:center;gap:10px;margin-top:16px;">
                <input type="checkbox" name="premium" style="width:auto;margin:0;" {"checked" if is_premium else ""}>
                <span>👑 Article Premium (réservé aux abonnés)</span>
            </label>
            <label>Contenu HTML de l'article</label>
            <textarea name="texte" rows="20" placeholder="Colle ici le HTML...">{texte_val}</textarea>
            <button type="submit" class="btn">{"💾 ENREGISTRER" if edit_id else "🚀 PUBLIER"}</button>
        </form>
        <hr style="border:0.5px solid #333;margin:40px 0;">
        {list_html}
        <hr style="border:0.5px solid #333;margin:40px 0;">
        {users_html}
    </div>
    """
    return render_page(form, "Studio Admin — METTABYTE")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
