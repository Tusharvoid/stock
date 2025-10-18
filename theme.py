"""Shared theme CSS for the Streamlit app and embedded chat HTML.

Provide THEME_CSS (string) and a small helper to retrieve it. This centralizes
colors, variables and common classes so `app.py` and `chat_interface.py` can reuse
the same palette and avoid duplicated inline styles.
"""

THEME_CSS = """
<style>
    :root{
        --bg: #0b0b0b;
        --panel: linear-gradient(180deg, #0f1724, #0b1220);
        --muted: #9aa0a6;
        --accent: #e6eefc;
        --soft: #cdd6e0;
        --card-shadow: 0 10px 30px rgba(2,6,23,0.6);
        --card-border: 1px solid rgba(255,255,255,0.03);
        --accent-blue: linear-gradient(180deg,#3b82f6,#7c3aed);
        --accent-green: linear-gradient(180deg,#10b981,#06b6d4);
        --accent-purple: linear-gradient(180deg,#8b5cf6,#7c3aed);
    }

    html, body { background: linear-gradient(180deg, var(--bg) 0%, #111 100%); color: var(--soft); }

    .main-header { color: var(--soft); font-weight: 700; font-size: 28px; }
    .tab-header { color: var(--soft); font-size: 18px; font-weight: 600; }

    .card, .stock-card, .portfolio-card, .metric-card { position: relative; background: var(--panel); color: var(--soft); border-radius: 12px; padding: 18px; box-shadow: var(--card-shadow); border: var(--card-border); overflow: hidden; margin-bottom: 1.25rem; }

    .stock-card::before, .portfolio-card::before, .metric-card::before {
        content: ''; position: absolute; left: 8px; top: 18px; bottom: 18px; width: 6px; border-radius: 6px; background: linear-gradient(180deg, rgba(0,0,0,0.08), rgba(0,0,0,0.06)); opacity: 0.9;
    }

    .no-accent::before { display: none !important; }
    .stock-card .card-content, .portfolio-card .card-content, .metric-card .card-content { padding-left: 28px; }
    .stock-card::before { background: var(--accent-blue); box-shadow: 0 6px 20px rgba(59,130,246,0.12); }
    .portfolio-card::before { background: var(--accent-green); box-shadow: 0 6px 20px rgba(16,185,129,0.12); }
    .metric-card::before { background: var(--accent-purple); box-shadow: 0 6px 20px rgba(139,92,246,0.12); }

    .stat-tile { background: var(--panel); padding: 16px; border-radius: 10px; box-shadow: 0 14px 34px rgba(2,6,23,0.5); border: var(--card-border); margin-bottom: 1rem; }

    .ai-tab { background: linear-gradient(180deg,#17162a,#0f1220); color: var(--soft); padding: 6px 10px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.03); }

    /* Buttons and links */
    .stButton>button { background: linear-gradient(180deg,#0f1724,#0b1220) !important; color: var(--soft) !important; border: none !important; padding: 8px 12px; border-radius:10px; box-shadow: none !important; }
    .stButton>button:hover { filter: brightness(1.08); box-shadow: 0 8px 20px rgba(2,6,23,0.6); }

    a, .link { color: #8b5cf6; }
    
    /* Hero header and intro */
    .header-hero { text-align: center; margin-bottom: 3rem; }
    .header-hero p { color: var(--muted); font-size: 1.1rem; margin-top: 1rem; font-weight: 400; }

    /* Sidebar intro card */
    .sidebar-intro { text-align: center; margin-bottom: 2rem; padding: 1rem; background: rgba(255,255,255,0.03); border-radius: 12px; border: 1px solid rgba(255,255,255,0.08); }

    /* Stat labels and values */
    .stat-label { font-size: 0.9rem; color: var(--muted); margin-bottom: 0.5rem; }
    .stat-value { font-size: 1.8rem; font-weight: 700; color: var(--accent-blue); }

    /* Small inline pill/badge */
    .small-pill { display: inline-block; padding: 0.25rem 0.5rem; border-radius: 6px; font-size: 0.8rem; margin-top: 0.5rem; }

    /* Alert card (replaces inline border-left) */
    .alert-card { padding: 12px; border-radius: 10px; margin-bottom: 0.75rem; border: var(--card-border); background: rgba(255,255,255,0.02); }

    /* Generic info panel used for small two-column panels */
    .info-panel { background: rgba(255,255,255,0.03); padding: 1rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); }

    /* Alert accent via data attribute. Example: <div class="alert-card" data-accent-color="#667eea"> */
    .alert-card { position: relative; overflow: visible; }
    .alert-card::before { content: ''; position: absolute; left: 0; top: 8px; bottom: 8px; width: 6px; border-radius: 6px; background: transparent; }
    .alert-card[data-accent-color]::before { background: var(--accent-blue); }

    /* Pill accent helpers */
    .small-pill.blue { background: rgba(102, 126, 234, 0.1); color: #667eea; }
    .small-pill.purple { background: rgba(118, 75, 162, 0.1); color: #764ba2; }
    
    /* Allocation summary row */
    .allocation-row { display: flex; justify-content: space-between; align-items: center; padding: 0.5rem; margin: 0.25rem 0; background: rgba(255,255,255,0.03); border-radius: 8px; }
    .accent-strip { width: 6px; height: 36px; display: inline-block; border-radius: 6px; margin-right: 0.75rem; vertical-align: middle; }

    /* Accent color helpers for small strip used in allocation rows */
    .accent-strip.blue { background: #667eea; }
    .accent-strip.purple { background: #764ba2; }

    /* Alert title and meta */
    .alert-title { font-weight: 600; font-size: 1.1rem; }
    .alert-meta { color: var(--muted); font-size: 0.9rem; }
    .alert-card.alert-buy::before { background: var(--accent-green); box-shadow: 0 6px 20px rgba(16,185,129,0.12); }
    .alert-card.alert-sell::before { background: linear-gradient(180deg,#ef4444,#f97316); box-shadow: 0 6px 20px rgba(239,68,68,0.12); }

    /* Card title/subtitle/price */
    .card-title { margin: 0; color: var(--soft); font-size: 1.3rem; }
    .card-subtitle { margin: 0.25rem 0; color: var(--muted); font-size: 0.9rem; }
    .card-price { font-size: 1.8rem; font-weight: 700; color: var(--accent-blue); margin-bottom: 0.25rem; }
    .card-change { font-size: 1rem; font-weight: 600; }
    
    /* Utility variables and helpers */
    :root { --accent-text: #e2e8f0; }
    .row-between { display:flex; justify-content: space-between; margin-bottom: 0.5rem; }
    .row-between-center { display:flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }
    .row-between-start { display:flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem; }

    .muted-label { color: var(--muted); }
    .grid-label { color: var(--muted); font-size: 0.8rem; margin-bottom: 0.25rem; }
    .grid-value { color: var(--accent-text); font-weight: 600; }

    .section-title.blue { color: #667eea; margin-bottom: 1rem; }
    .section-title.purple { color: #764ba2; margin-bottom: 1rem; }
    .text-right { text-align: right; }
    .value-blue { color: #667eea; font-weight: 600; }
    .value-purple { color: #764ba2; font-weight: 600; }
    .positive-change { color: #10b981; }
    .negative-change { color: #ef4444; }
    .flex-center { display:flex; align-items:center; }
    .two-col-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.75rem; margin-top: 1rem; padding-top: 1rem; }
    .card-price-blue { color: #667eea; }
    .card-price-purple { color: #764ba2; }

    /* Clean look: remove left accent bars and small accent strips for overview cards */
    .stock-card::before, .portfolio-card::before, .metric-card::before, .alert-card::before { display: none !important; }
    .accent-strip { display: none !important; }

    /* Optional: remove subtle outer border for a cleaner flat card look */
    .card, .stock-card, .portfolio-card, .metric-card, .stat-tile { border: none; }
</style>
"""

def get_theme_css() -> str:
    """Return THEME_CSS for injection into Streamlit or embedding in HTML."""
    return THEME_CSS
