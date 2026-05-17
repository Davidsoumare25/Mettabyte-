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

# \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
# PAYDUNYA \u2014 CONFIGURATION
# \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
PAYDUNYA_MASTER_KEY  = os.environ.get("PAYDUNYA_MASTER_KEY")
PAYDUNYA_PRIVATE_KEY = os.environ.get("PAYDUNYA_PRIVATE_KEY")
PAYDUNYA_PUBLIC_KEY  = os.environ.get("PAYDUNYA_PUBLIC_KEY")
PAYDUNYA_TOKEN       = os.environ.get("PAYDUNYA_TOKEN")
PAYDUNYA_MODE        = os.environ.get("PAYDUNYA_MODE", "test")  # "test" ou "live"

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


# \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
# HELPERS
# \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def reading_time(html_text):
    clean = re.sub(r'<[^>]+>', '', html_text)
    return max(1, round(len(clean.split()) / 200))

def get_user():
    """Retourne l'utilisateur connect\u00e9 depuis la session, ou None."""
    uid = session.get('user_id')
    if not uid:
        return None
    try:
        r = requests.get(SUPABASE_URL_USR + "?id=eq." + str(uid), headers=HEADERS)
        data = r.json()
        return data[0] if data else None
    except:
        return None

def render_page(content, title, meta_desc="METTABYTE \u2014 Tech, IA, Science, Espace"):
    user = get_user()
    user_name   = user['email'].split('@')[0] if user else ""
    is_premium  = user.get('premium', False) if user else False
    is_logged   = user is not None

    if is_logged:
        menu_user_html = f"""
        <div class="menu-user-info">
            <div class="menu-avatar">{user_name[0].upper()}</div>
            <div>
                <div style="font-weight:700; color:#fff;">{user_name}</div>
                <div style="font-size:0.75rem; color:{'#f5c518' if is_premium else '#888'};">
                    {'\ud83d\udc51 Premium' if is_premium else 'Gratuit'}
                </div>
            </div>
        </div>
        {'<div class="menu-premium-badge">\ud83d\udc51 Membre Premium actif</div>' if is_premium else '<a href="/premium" class="menu-upgrade-btn">\u2728 Passer Premium \u2014 655 F</a>'}
        <hr style="border:0.5px solid #222; margin:20px 0;">
        <a href="/compte" class="menu-link">\ud83d\udc64 Mon compte</a>
        <a href="/deconnexion" class="menu-link" style="color:var(--red);">\ud83d\udeaa D\u00e9connexion</a>
        """
    else:
        menu_user_html = """
        <p style="color:#888; font-size:0.85rem; margin-bottom:20px;">
            Cr\u00e9e un compte pour acc\u00e9der aux articles Premium et soutenir METTABYTE.
        </p>
        <a href="/inscription" class="menu-cta-btn">\u2709\ufe0f Cr\u00e9er un compte</a>
        <a href="/connexion" class="menu-link" style="margin-top:10px;">\ud83d\udd11 Se connecter</a>
        <hr style="border:0.5px solid #222; margin:20px 0;">
        <a href="/premium" class="menu-link" style="color:#f5c518;">\ud83d\udc51 D\u00e9couvrir Premium</a>
        """

    html = BASE_HTML
    html = html.replace("%PAGE_TITLE%", title)
    html = html.replace("%LOGO%", LOGO_URL)
    html = html.replace("%RAW_CONTENT%", content)
    html = html.replace("%META_DESC%", meta_desc)
    html = html.replace("%ADSENSE_ID%", ADSENSE_ID)
    html = html.replace("%MENU_USER_HTML%", menu_user_html)
    return html

# \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
# BASE HTML
# \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
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

        /* MENU LAT\u00c9RAL */
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
