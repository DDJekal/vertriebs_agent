#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wettbewerbsanalyse – Talent Report Layout (CI: Limonengrün)
==========================================================
- CI: Helles Limonengrün #e0edc8 (Hintergrund), Dunkelgrün #1a2e0d (Zweitfarbe/Footer/Akzente)
- Logo: Skill templates/logo.png oder Projektordner logo.png/logo.svg
- Folie 2: Wettbewerber-Karten mit Logo (logo_url/domain, Clearbit-Fallback) wie v2.5

Usage:
  python3 generate_presentation.py <input.json> --html-dir <ordner> [--project-dir <projektordner>]
"""

import json
import sys
import re
import os
import base64
import tempfile
from pathlib import Path

# ── Talent Report CI (Helles Limonengrün + Dunkel als Zweitfarbe) ──────────
BG = "#e0edc8"      # Helles Limonengrün (Hauptfarbe der Präsentation)
DARK = "#1a2e0d"    # Dunkelgrün (Zweitfarbe: Linien, Footer, Akzente)
ACCENT = "#1a2e0d"  # = DARK für Konsistenz (Titel-Linie, Hervorhebungen)
CARD_TEXT = "#1a1a1a"
SWOT_STRENGTH = "#27AE60"
SWOT_WEAKNESS = "#E74C3C"
SWOT_RISK = "#f9a825"
CHANCE_DEFAULT = "#81c784"

LOGO_B64 = ""

def load_logo(path: Path, as_svg: bool) -> str:
    if not path or not path.exists():
        return ""
    try:
        with open(path, "rb") as f:
            raw = f.read()
        b64 = base64.b64encode(raw).decode()
        return ("data:image/svg+xml;base64," if as_svg else "data:image/png;base64,") + b64
    except Exception:
        return ""

def load_logo_from_project(project_dir: str) -> str:
    if not project_dir:
        return ""
    for name, svg in [("logo.png", False), ("logo.svg", True)]:
        out = load_logo(Path(project_dir) / name, svg)
        if out:
            return out
    return ""

def load_logo_from_skill() -> str:
    path = Path(__file__).resolve().parent.parent / "templates" / "logo.png"
    return load_logo(path, False)

def fetch_image_b64(url: str) -> str:
    if not url:
        return ""
    try:
        import urllib.request
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = resp.read()
            ct = resp.headers.get_content_type() or "image/jpeg"
            return f"data:{ct};base64," + base64.b64encode(data).decode()
    except Exception:
        return ""

def parse_salary(salary_str: str) -> float:
    s = re.sub(r'[^0-9,.]', '', str(salary_str))
    if ',' in s and '.' in s:
        s = s.replace('.', '').replace(',', '.')
    elif ',' in s:
        s = s.replace(',', '.')
    else:
        s = s.replace('.', '')
    try:
        return float(s)
    except ValueError:
        return 0.0

FONT_IMPORT = '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">'

def footer_html() -> str:
    logo_img = f'<img src="{LOGO_B64}" style="height:26px;" />' if LOGO_B64 else ''
    return f'''<div style="position:absolute;bottom:0;left:0;right:0;height:44px;background:{DARK};display:flex;align-items:center;justify-content:space-between;padding:0 40px;border-top:2px solid {DARK};">
    <span style="color:#e0edc8;font-size:12px;">Talent Report 2026</span>
    {logo_img}
  </div>'''

def slide_wrapper(content: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="de"><head>
<meta charset="UTF-8">
{FONT_IMPORT}
<style>
  @page {{ size: 1280px 720px; margin: 0; }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  html, body {{ width:1280px; height:720px; overflow:hidden; background:{BG};
                font-family:'Inter',sans-serif; }}
</style>
</head><body>
<div style="width:1280px;height:720px;position:relative;background:{BG};overflow:hidden;">
  <div style="position:absolute;top:0;left:0;right:0;bottom:44px;padding:28px 36px 0 36px;display:flex;flex-direction:column;overflow:hidden;">
    {content}
  </div>
  {footer_html()}
</div>
</body></html>"""

def title_bar(text: str) -> str:
    return f'''<div style="text-align:center;flex-shrink:0;margin-bottom:14px;">
    <div style="color:{DARK};font-size:24px;font-weight:800;letter-spacing:6px;text-transform:uppercase;">{text}</div>
    <div style="width:56px;height:3px;background:{DARK};margin:8px auto 0 auto;border-radius:2px;"></div>
  </div>'''


# ── Folie 1 – Titelfolie ─────────────────────────────────────────────────────

def slide_1(d: dict, images: dict) -> str:
    company  = d.get('company_name', 'Unternehmen')
    position = d.get('position', 'Position')
    location = d.get('location', 'Standort')
    bg_b64   = images.get('background', '')

    bg_layer = f'<img src="{bg_b64}" style="position:absolute;top:0;left:0;width:100%;height:100%;object-fit:cover;opacity:0.22;" />' if bg_b64 else ''

    return f"""<!DOCTYPE html>
<html lang="de"><head>
<meta charset="UTF-8">
{FONT_IMPORT}
<style>
  @page {{ size: 1280px 720px; margin: 0; }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  html, body {{ width:1280px; height:720px; overflow:hidden; background:{BG}; font-family:'Inter',sans-serif; }}
</style>
</head><body>
<div style="width:1280px;height:720px;position:relative;background:{BG};overflow:hidden;">
  {bg_layer}
  <div style="position:absolute;inset:0;background:linear-gradient(160deg,rgba(224,237,200,0.4) 0%,rgba(224,237,200,0.85) 100%);"></div>
  <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-52%);text-align:center;border:2px solid {DARK};border-radius:4px;padding:44px 68px;min-width:560px;max-width:760px;background:rgba(255,255,255,0.6);">
    <div style="color:{DARK};font-size:12px;letter-spacing:6px;text-transform:uppercase;margin-bottom:18px;">W E T T B E W E R B S - A N A L Y S E</div>
    <h1 style="color:{DARK};font-size:42px;font-weight:800;line-height:1.2;margin-bottom:16px;">{company}</h1>
    <div style="width:56px;height:3px;background:{DARK};margin:0 auto 18px auto;border-radius:2px;"></div>
    <div style="color:{DARK};font-size:17px;">{position} | {location}</div>
  </div>
  <div style="position:absolute;bottom:0;left:0;right:0;height:44px;background:{DARK};display:flex;align-items:center;justify-content:space-between;padding:0 40px;">
    <span style="color:#e0edc8;font-size:12px;">Talent Report 2026</span>
    {'<img src="' + LOGO_B64 + '" style="height:26px;" />' if LOGO_B64 else ''}
  </div>
</div>
</body></html>"""


# ── Folie 2 – Lokaler Wettbewerb (wie v2.5: Karten mit Logo/Bild) ───────────

def competitor_card(c: dict, img_b64: str) -> str:
    name     = c.get('name', '')
    ctype    = c.get('type', '')
    distance = c.get('distance', '')
    employees= c.get('employees', '')
    salary   = c.get('salary', '')
    strength = c.get('strength', '')
    weakness = c.get('weakness', '')

    if img_b64:
        img_html = f'<div style="width:100%;height:120px;background:#f5f5f5;display:flex;align-items:center;justify-content:center;overflow:hidden;flex-shrink:0;"><img src="{img_b64}" style="width:100%;height:100%;object-fit:cover;" /></div>'
    else:
        initials = ''.join(w[0] for w in name.split()[:2]).upper()
        img_html = f'<div style="width:100%;height:120px;background:white;display:flex;align-items:center;justify-content:center;flex-shrink:0;"><span style="color:{DARK};font-size:42px;font-weight:800;letter-spacing:2px;">{initials}</span></div>'

    return f'''<div style="background:white;border-radius:8px;overflow:hidden;flex:1;display:flex;flex-direction:column;">
    {img_html}
    <div style="padding:14px 16px;flex:1;display:flex;flex-direction:column;">
      <h3 style="color:{CARD_TEXT};font-size:15px;font-weight:700;margin:0 0 6px 0;line-height:1.3;">{name}</h3>
      <div style="height:2px;background:{DARK};margin-bottom:10px;"></div>
      <div style="display:flex;justify-content:space-between;margin-bottom:5px;font-size:12.5px;"><span style="color:#888;">Typ</span><span style="font-weight:600;color:{CARD_TEXT};max-width:58%;text-align:right;">{ctype}</span></div>
      <div style="display:flex;justify-content:space-between;margin-bottom:5px;font-size:12.5px;"><span style="color:#888;">Entfernung</span><span style="font-weight:700;color:{DARK};">{distance}</span></div>
      <div style="display:flex;justify-content:space-between;margin-bottom:5px;font-size:12.5px;"><span style="color:#888;">Mitarbeiter</span><span style="font-weight:600;color:{CARD_TEXT};">{employees}</span></div>
      <div style="display:flex;justify-content:space-between;margin-bottom:10px;font-size:12.5px;"><span style="color:#888;">Gehalt</span><span style="font-weight:700;color:{DARK};">{salary}</span></div>
      <div style="background:#e8f8ee;border-left:3px solid #27AE60;padding:7px 10px;font-size:12px;color:#1a7a40;margin-top:auto;">
        <div style="font-weight:700;font-size:10px;letter-spacing:0.5px;text-transform:uppercase;margin-bottom:2px;">+ STÄRKE</div>
        <div style="line-height:1.35;">{strength}</div>
      </div>
      <div style="background:#fdf0f0;border-left:3px solid #E74C3C;padding:7px 10px;font-size:12px;color:#a93226;margin-top:6px;">
        <div style="font-weight:700;font-size:10px;letter-spacing:0.5px;text-transform:uppercase;margin-bottom:2px;">- SCHWÄCHE</div>
        <div style="line-height:1.35;">{weakness}</div>
      </div>
    </div>
  </div>'''

def slide_2(d: dict, images: dict) -> str:
    competitors = d.get('competitors', [])[:3]
    cards = '\n'.join(
        competitor_card(c, images.get(f'competitor_building_{i}', '') or images.get(f'competitor_{i}', ''))
        for i, c in enumerate(competitors)
    )
    content = f'''{title_bar("LOKALER WETTBEWERB")}
    <div style="display:flex;gap:18px;flex:1;overflow:hidden;">
      {cards}
    </div>'''
    return slide_wrapper(content)


# ── Folie 3 – Regionale Analyse ─────────────────────────────────────────────

STAT_ICONS = ['▲', '■', '►', '▲']

def stat_card(stat: dict, index: int = 0) -> str:
    value = stat.get('value', '')
    label = stat.get('label', '')
    icon  = STAT_ICONS[index % len(STAT_ICONS)]
    return f'''<div style="background:rgba(255,255,255,0.85);border-radius:8px;padding:16px 20px;border-left:4px solid {DARK};display:flex;align-items:center;gap:14px;">
    <span style="color:{DARK};font-size:16px;flex-shrink:0;">{icon}</span>
    <div>
      <div style="color:{DARK};font-size:28px;font-weight:800;line-height:1.1;">{value}</div>
      <div style="color:rgba(26,46,13,0.8);font-size:12px;margin-top:3px;">{label}</div>
    </div>
  </div>'''

def radar_svg(location_short: str, competitors: list) -> str:
    cx, cy, r_outer, r_mid, r_inner = 160, 160, 148, 105, 62
    dots = ""
    positions = [(cx + 85, cy - 70), (cx + 55, cy + 80), (cx - 90, cy + 50)]
    dot_colors = ["#81c784", "#27AE60", DARK]
    for i, comp in enumerate(competitors[:3]):
        px, py = positions[i]
        name = comp.get('name', '').split()[0]
        dots += f'<circle cx="{px}" cy="{py}" r="7" fill="{dot_colors[i]}" opacity="0.9"/>'
        dots += f'<text x="{px + 10}" y="{py + 4}" fill="{DARK}" font-size="11" font-family="Inter,sans-serif">{name}</text>'

    return f'''<svg width="320" height="320" viewBox="0 0 320 320" xmlns="http://www.w3.org/2000/svg">
    <circle cx="{cx}" cy="{cy}" r="{r_outer}" fill="none" stroke="rgba(26,46,13,0.25)" stroke-width="1.5" stroke-dasharray="6,4"/>
    <text x="{cx}" y="{cy - r_outer - 6}" fill="{DARK}" font-size="11" text-anchor="middle" font-family="Inter,sans-serif">40 km</text>
    <circle cx="{cx}" cy="{cy}" r="{r_mid}" fill="none" stroke="rgba(26,46,13,0.3)" stroke-width="1.5" stroke-dasharray="6,4"/>
    <text x="{cx}" y="{cy - r_mid - 6}" fill="{DARK}" font-size="11" text-anchor="middle" font-family="Inter,sans-serif">20 km</text>
    <circle cx="{cx}" cy="{cy}" r="{r_inner}" fill="none" stroke="rgba(26,46,13,0.35)" stroke-width="1.5" stroke-dasharray="6,4"/>
    {dots}
    <circle cx="{cx}" cy="{cy}" r="42" fill="rgba(26,46,13,0.15)"/>
    <circle cx="{cx}" cy="{cy}" r="32" fill="{DARK}"/>
    <text x="{cx}" y="{cy + 5}" fill="#e0edc8" font-size="15" font-weight="bold" text-anchor="middle" font-family="Inter,sans-serif">{location_short}</text>
  </svg>'''

def slide_3(d: dict, images: dict) -> str:
    stats          = d.get('regional_stats', [])
    insight        = d.get('regional_insight', '')
    location_short = d.get('location_short', '')
    competitors    = d.get('competitors', [])

    left_html  = '\n'.join(stat_card(s, i)     for i, s in enumerate(stats[:2]))
    right_html = '\n'.join(stat_card(s, i + 2) for i, s in enumerate(stats[2:4]))

    content = f'''{title_bar("REGIONALE ANALYSE")}
    <div style="display:flex;gap:16px;flex:1;align-items:center;">
      <div style="flex:1;display:flex;flex-direction:column;gap:14px;">{left_html}</div>
      <div style="flex:0 0 320px;display:flex;align-items:center;justify-content:center;">{radar_svg(location_short, competitors)}</div>
      <div style="flex:1;display:flex;flex-direction:column;gap:14px;">{right_html}</div>
    </div>
    <div style="background:rgba(255,255,255,0.9);color:#333;border-radius:8px;padding:13px 18px;display:flex;align-items:flex-start;gap:10px;margin-top:12px;flex-shrink:0;">
      <span style="color:{DARK};font-size:16px;font-weight:700;flex-shrink:0;margin-top:1px;">i</span>
      <div style="font-size:13px;line-height:1.55;"><strong>Regionaler Insight:</strong> {insight}</div>
    </div>'''
    return slide_wrapper(content)


# ── Folie 4 – Gehaltsvergleich ──────────────────────────────────────────────

def slide_4(d: dict, images: dict) -> str:
    salaries = d.get('salaries', [])
    position = d.get('position', 'Position')

    values  = [parse_salary(s.get('salary', '0')) for s in salaries]
    max_val = max(values) if values else 1

    left_cards = []
    for s in salaries:
        is_target = s.get('bar_color', '') in (DARK, ACCENT, '#EF5800')
        is_avg    = s.get('is_average', False)
        name_str  = s.get('name', '')
        sal_str   = s.get('salary', '')
        if is_avg:
            left_cards.append(f'<div style="background:rgba(26,46,13,0.08);border:2px dashed rgba(26,46,13,0.4);border-radius:8px;padding:13px 16px;display:flex;justify-content:space-between;align-items:center;"><span style="color:{DARK};font-size:13.5px;">{name_str}</span><span style="color:{DARK};font-size:15px;font-weight:700;">{sal_str}</span></div>')
        elif is_target:
            left_cards.append(f'<div style="background:{DARK};border-radius:8px;padding:13px 16px;display:flex;justify-content:space-between;align-items:center;"><span style="color:#e0edc8;font-size:14px;font-weight:700;">{name_str}</span><span style="color:#e0edc8;font-size:17px;font-weight:800;">{sal_str}</span></div>')
        else:
            left_cards.append(f'<div style="background:white;border-radius:8px;padding:13px 16px;display:flex;justify-content:space-between;align-items:center;"><span style="color:{CARD_TEXT};font-size:13.5px;">{name_str}</span><span style="color:{CARD_TEXT};font-size:15px;font-weight:700;">{sal_str}</span></div>')

    right_bars = []
    bar_colors_fallback = [DARK, '#81c784', '#27AE60', '#9B59B6', '#95A5A6']
    for i, s in enumerate(salaries):
        val      = values[i]
        is_avg   = s.get('is_average', False)
        bar_col  = '#aaa' if is_avg else s.get('bar_color', bar_colors_fallback[i % len(bar_colors_fallback)])
        pct      = round((val / max_val) * 90) if max_val > 0 else 0
        lbl_col  = '#888' if is_avg else CARD_TEXT
        sep      = '<div style="border-top:2px dashed #ddd;margin:4px 0 10px 0;"></div>' if is_avg else ''
        right_bars.append(f'''{sep}<div style="display:flex;align-items:center;margin-bottom:12px;">
          <span style="width:155px;color:{lbl_col};font-size:12px;font-weight:600;flex-shrink:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{s.get('name','')}</span>
          <div style="flex:1;background:#f0f0f0;border-radius:4px;height:32px;margin:0 10px;">
            <div style="width:{pct}%;height:100%;background:{bar_col};border-radius:4px;"></div>
          </div>
          <span style="color:{lbl_col};font-size:13px;font-weight:700;width:68px;text-align:right;flex-shrink:0;">{s.get('salary','')}</span>
        </div>''')

    pos_short = position.split('(')[0].strip()
    content = f'''{title_bar("GEHALTSVERGLEICH")}
    <div style="display:flex;gap:22px;flex:1;align-items:center;">
      <div style="flex:0 0 42%;display:flex;flex-direction:column;gap:9px;">{''.join(left_cards)}</div>
      <div style="flex:1;background:white;border-radius:8px;padding:22px 20px 16px 20px;display:flex;flex-direction:column;justify-content:center;">
        <h3 style="color:{CARD_TEXT};font-size:12px;font-weight:700;margin-bottom:16px;text-align:center;text-transform:uppercase;letter-spacing:2px;">Monatsgehalt Brutto – {pos_short}</h3>
        {''.join(right_bars)}
      </div>
    </div>'''
    return slide_wrapper(content)


# ── Folie 5 – SWOT-Analyse ───────────────────────────────────────────────────

SWOT_SYMBOLS = {'STÄRKEN': '✅', 'SCHWÄCHEN': '⚠', 'RISIKEN': '⚡'}

def swot_card(swot: dict) -> str:
    color  = swot.get('color', '#ccc')
    title  = swot.get('title', '')
    points = swot.get('points', [])

    items_html = ''
    for p in points[:4]:
        t    = p.get('title', '')
        desc = p.get('text', '')
        items_html += f'''<div style="border-bottom:1px solid #f0f0f0;padding:9px 0;display:flex;align-items:flex-start;gap:8px;flex-shrink:0;">
          <span style="color:{color};font-size:13px;margin-top:2px;flex-shrink:0;font-weight:700;">&#9654;</span>
          <div>
            <div style="font-size:13px;font-weight:700;color:{CARD_TEXT};">{t}</div>
            <div style="font-size:11.5px;color:#555;margin-top:3px;line-height:1.4;">{desc}</div>
          </div>
        </div>'''

    symbol = swot.get('icon', SWOT_SYMBOLS.get(title, '●'))
    return f'''<div style="background:white;border-radius:8px;overflow:hidden;flex:1;display:flex;flex-direction:column;">
    <div style="background:{color};padding:14px 16px;display:flex;align-items:center;gap:10px;flex-shrink:0;">
      <span style="color:white;font-size:17px;flex-shrink:0;">{symbol}</span>
      <span style="color:white;font-size:16px;font-weight:700;letter-spacing:1.5px;">{title}</span>
    </div>
    <div style="padding:10px 14px;flex:1;display:flex;flex-direction:column;overflow:hidden;">
      {items_html}
    </div>
  </div>'''

def slide_5(d: dict, images: dict) -> str:
    swot_list = d.get('swot', [])
    cards = '\n'.join(swot_card(s) for s in swot_list[:3])
    content = f'''{title_bar("SWOT ANALYSE")}
    <div style="display:flex;gap:18px;flex:1;overflow:hidden;">
      {cards}
    </div>'''
    return slide_wrapper(content)


# ── Folie 6 – Recruiting-Chancen ────────────────────────────────────────────

CHANCE_SYMBOLS = ['&#10148;', '&#9733;', '&#9670;']

def chance_card(opp: dict, index: int = 0) -> str:
    color   = opp.get('color', CHANCE_DEFAULT)
    title   = opp.get('title', '')
    bullets = opp.get('bullets', [])
    symbol  = CHANCE_SYMBOLS[index % len(CHANCE_SYMBOLS)]

    bullets_html = ''
    for b in bullets[:4]:
        if ' – ' in b:
            kw, rest = b.split(' – ', 1)
            b_html = f'<strong>{kw}</strong> – {rest}'
        elif ': ' in b:
            kw, rest = b.split(': ', 1)
            b_html = f'<strong>{kw}</strong>: {rest}'
        else:
            b_html = b
        bullets_html += f'''<div style="border-bottom:1px solid #f0f0f0;padding:9px 0;display:flex;gap:8px;align-items:flex-start;flex-shrink:0;">
          <span style="color:{color};font-weight:bold;flex-shrink:0;font-size:13px;">&#9654;</span>
          <span style="font-size:13px;color:#333;line-height:1.4;">{b_html}</span>
        </div>'''

    return f'''<div style="background:white;border-radius:8px;overflow:hidden;flex:1;display:flex;flex-direction:column;">
    <div style="background:{color};padding:16px 18px;display:flex;align-items:center;gap:14px;flex-shrink:0;">
      <div style="width:42px;height:42px;background:rgba(255,255,255,0.2);border-radius:50%;display:flex;align-items:center;justify-content:center;flex-shrink:0;color:white;font-size:20px;">{symbol}</div>
      <div style="color:white;font-size:15px;font-weight:700;letter-spacing:1px;text-transform:uppercase;">{title}</div>
    </div>
    <div style="padding:12px 16px;flex:1;display:flex;flex-direction:column;overflow:hidden;">
      {bullets_html}
    </div>
  </div>'''

def slide_6(d: dict, images: dict) -> str:
    opps  = d.get('opportunities', [])
    cards = '\n'.join(chance_card(o, i) for i, o in enumerate(opps[:3]))
    content = f'''{title_bar("RECRUITING-CHANCEN")}
    <div style="display:flex;gap:18px;flex:1;overflow:hidden;">
      {cards}
    </div>'''
    return slide_wrapper(content)


# ── Folie 7 – Bewerber-Personas ──────────────────────────────────────────────

def persona_card(p: dict) -> str:
    color      = p.get('color', DARK)
    name       = p.get('name', '')
    archetype  = p.get('archetype', '')
    pain_pts   = p.get('pain_points', [])
    values_lst = p.get('values', [])
    initial    = name[0].upper() if name else 'P'

    def bullet(text: str, dot_color: str) -> str:
        if ' – ' in text:
            kw, rest = text.split(' – ', 1)
            b_html = f'<strong>{kw}</strong> – {rest}'
        elif ': ' in text:
            kw, rest = text.split(': ', 1)
            b_html = f'<strong>{kw}</strong>: {rest}'
        else:
            b_html = text
        return f'<div style="font-size:12px;color:#333;display:flex;gap:6px;align-items:flex-start;padding:5px 0;border-bottom:1px solid rgba(0,0,0,0.06);"><span style="color:{dot_color};flex-shrink:0;font-size:11px;margin-top:2px;font-weight:700;">&#9654;</span><span style="line-height:1.4;">{b_html}</span></div>'

    pain_html = ''.join(bullet(pp, '#c0392b') for pp in pain_pts[:3])
    val_html  = ''.join(bullet(v,  '#1a7a40') for v  in values_lst[:3])

    return f'''<div style="background:white;border-radius:8px;overflow:hidden;flex:1;display:flex;flex-direction:column;">
    <div style="background:{color};padding:14px 16px;display:flex;align-items:center;gap:12px;flex-shrink:0;">
      <div style="width:44px;height:44px;border-radius:50%;background:rgba(255,255,255,0.25);display:flex;align-items:center;justify-content:center;flex-shrink:0;color:white;font-size:22px;font-weight:700;">{initial}</div>
      <div>
        <div style="color:white;font-size:18px;font-weight:700;">{name}</div>
        <div style="color:rgba(255,255,255,0.82);font-size:12px;margin-top:2px;">{archetype}</div>
      </div>
    </div>
    <div style="padding:10px 14px;flex:1;display:flex;flex-direction:column;gap:8px;overflow:hidden;">
      <div style="background:#fdf0f0;border-radius:6px;padding:10px 12px;flex:1;overflow:hidden;">
        <div style="font-size:10px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#c0392b;margin-bottom:6px;">SCHMERZPUNKTE</div>
        {pain_html}
      </div>
      <div style="background:#e8f8ee;border-radius:6px;padding:10px 12px;flex:1;overflow:hidden;">
        <div style="font-size:10px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#1a7a40;margin-bottom:6px;">WERTE &amp; ZIELE</div>
        {val_html}
      </div>
    </div>
  </div>'''

def slide_7(d: dict, images: dict) -> str:
    personas = d.get('personas', [])
    cards    = '\n'.join(persona_card(p) for p in personas[:3])
    content  = f'''{title_bar("BEWERBER-PERSONAS")}
    <div style="display:flex;gap:18px;flex:1;overflow:hidden;">
      {cards}
    </div>'''
    return slide_wrapper(content)


# ── Bilder vorladen (Titelfolie + Wettbewerber-Logos, wie v2.5) ─────────────

def preload_images(d: dict) -> dict:
    images = {}
    location = d.get('location', 'city')
    bg_url = (d.get('background_image_url') or '').strip()
    if bg_url:
        images['background'] = fetch_image_b64(bg_url)
    if not images.get('background'):
        fallback = f"https://source.unsplash.com/1280x720/?{location},city,panorama"
        images['background'] = fetch_image_b64(fallback)

    for i, comp in enumerate(d.get('competitors', [])[:3]):
        build_url = comp.get('building_image_url', '')
        if build_url:
            images[f'competitor_building_{i}'] = fetch_image_b64(build_url)

        url = comp.get('logo_url', '') or comp.get('image_url', '')
        if url:
            images[f'competitor_{i}'] = fetch_image_b64(url)
        if not images.get(f'competitor_{i}'):
            domain = comp.get('domain', '')
            if domain:
                images[f'competitor_{i}'] = fetch_image_b64(f"https://logo.clearbit.com/{domain}")

    return images


# ── Hauptprogramm ─────────────────────────────────────────────────────────────

def main():
    global LOGO_B64

    if len(sys.argv) < 3:
        print("Usage: python generate_presentation.py <input.json> --html-dir <ordner> [--project-dir <projektordner>]")
        sys.exit(1)

    json_path = sys.argv[1]
    if '--html-dir' not in sys.argv:
        print("Dieses Skript unterstützt nur --html-dir Modus.")
        sys.exit(1)

    idx = sys.argv.index('--html-dir')
    if idx + 1 >= len(sys.argv):
        print("Fehler: --html-dir braucht einen Zielordner.")
        sys.exit(1)
    html_dir = sys.argv[idx + 1]

    project_dir = ""
    if '--project-dir' in sys.argv:
        pidx = sys.argv.index('--project-dir')
        if pidx + 1 < len(sys.argv):
            project_dir = sys.argv[pidx + 1]
    LOGO_B64 = load_logo_from_project(project_dir) if project_dir else ""
    if not LOGO_B64:
        LOGO_B64 = load_logo_from_skill()
        if LOGO_B64:
            print("  Logo aus Skill templates/logo.png geladen.")
    elif LOGO_B64:
        print("  Logo aus Projektordner geladen (logo.png/logo.svg).")

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Fehler: JSON nicht gefunden: {json_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Fehler: Ungültiges JSON: {e}")
        sys.exit(1)

    images = preload_images(data)

    generators = [slide_1, slide_2, slide_3, slide_4, slide_5, slide_6, slide_7]

    os.makedirs(html_dir, exist_ok=True)
    print(f"  Generiere HTML-Folien nach {html_dir} ...")
    for i, gen in enumerate(generators, 1):
        html = gen(data, images)
        html_path = os.path.join(html_dir, f"slide_{i:02d}.html")
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"    Folie {i}/7 ✓")
    print(f"\n✓ {len(generators)} HTML-Dateien gespeichert in: {html_dir}")

if __name__ == '__main__':
    main()
