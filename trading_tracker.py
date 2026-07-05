import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
from datetime import date, datetime, timedelta
import calendar

# ─── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Trading Tracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;700&family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600;700&display=swap');

:root {
    --bg:       #05070d;
    --bg2:      #0d1117;
    --bg3:      #161b27;
    --bg4:      #1e2535;
    --border:   #1e2d45;
    --accent:   #00d4ff;
    --accent2:  #7c3aed;
    --green:    #00e676;
    --red:      #ff1744;
    --amber:    #ffc400;
    --text:     #e2e8f5;
    --muted:    #4a5878;
    --muted2:   #8899bb;
}

html, body, [class*="css"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif;
}

/* Scanline overlay */
body::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        rgba(0,212,255,0.008) 2px,
        rgba(0,212,255,0.008) 4px
    );
    pointer-events: none;
    z-index: 9999;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1117 0%, #0a0e19 100%) !important;
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] * { color: var(--text) !important; }

h1, h2, h3 {
    font-family: 'Bebas Neue', sans-serif !important;
    letter-spacing: 0.08em !important;
    color: var(--text) !important;
}
h1 { font-size: 2.6rem !important; }
h2 { font-size: 1.9rem !important; }
h3 { font-size: 1.4rem !important; color: var(--accent) !important; }

[data-testid="metric-container"] {
    background: linear-gradient(135deg, var(--bg2) 0%, var(--bg3) 100%);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 1rem !important;
    position: relative;
    overflow: hidden;
}
[data-testid="metric-container"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
}
[data-testid="stMetricValue"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 1.5rem !important;
    font-weight: 700 !important;
}
[data-testid="stMetricLabel"] {
    color: var(--muted2) !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    font-weight: 600 !important;
}
[data-testid="stMetricDelta"] svg { display: none; }
[data-testid="stMetricDelta"] { font-family: 'IBM Plex Mono', monospace !important; font-size: 0.85rem !important; }

button[data-baseweb="tab"] {
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    color: var(--muted2) !important;
    background: transparent !important;
    border-bottom: 2px solid transparent !important;
    letter-spacing: 0.03em;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
}

input, textarea, [data-baseweb="input"] input {
    background: var(--bg3) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 4px !important;
    font-family: 'IBM Plex Mono', monospace !important;
}
[data-baseweb="select"] > div {
    background: var(--bg3) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
}
[data-testid="stNumberInput"] input { font-family: 'IBM Plex Mono', monospace !important; }

[data-testid="stButton"] > button {
    background: linear-gradient(135deg, var(--accent), #0099cc) !important;
    color: #000 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 4px !important;
    letter-spacing: 0.05em;
    transition: all 0.2s;
}
[data-testid="stButton"] > button:hover { opacity: 0.85 !important; transform: translateY(-1px); }

[data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: 4px;
    overflow: hidden;
}

hr { border-color: var(--border) !important; }

.kpi-card {
    background: linear-gradient(135deg, var(--bg2), var(--bg3));
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 1.2rem 1.5rem;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
}
.kpi-card.green::before { background: var(--green); }
.kpi-card.red::before { background: var(--red); }
.kpi-card.blue::before { background: var(--accent); }
.kpi-card.purple::before { background: var(--accent2); }
.kpi-card.amber::before { background: var(--amber); }

.kpi-label {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--muted2);
    margin-bottom: 0.4rem;
}
.kpi-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text);
    line-height: 1;
}
.kpi-sub {
    font-size: 0.75rem;
    color: var(--muted2);
    margin-top: 0.3rem;
    font-family: 'IBM Plex Mono', monospace;
}
.green-val { color: var(--green) !important; }
.red-val   { color: var(--red)   !important; }
.amber-val { color: var(--amber) !important; }
.blue-val  { color: var(--accent) !important; }

.insight-chip {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 2px;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    font-family: 'IBM Plex Mono', monospace;
}
.chip-green { background: rgba(0,230,118,0.12); color: #00e676; border: 1px solid rgba(0,230,118,0.3); }
.chip-red   { background: rgba(255,23,68,0.12);  color: #ff5252; border: 1px solid rgba(255,23,68,0.3); }
.chip-amber { background: rgba(255,196,0,0.12);  color: #ffc400; border: 1px solid rgba(255,196,0,0.3); }
.chip-blue  { background: rgba(0,212,255,0.1);   color: #00d4ff; border: 1px solid rgba(0,212,255,0.3); }
.chip-gray  { background: rgba(74,88,120,0.2);   color: #8899bb; border: 1px solid rgba(74,88,120,0.4); }

.section-hdr {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 0.85rem;
    letter-spacing: 0.2em;
    color: var(--muted2);
    text-transform: uppercase;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.section-hdr::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}

.day-row {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 0.8rem 1rem;
    margin-bottom: 0.5rem;
    display: flex;
    gap: 1rem;
    align-items: center;
}
.stAlert { border-radius: 4px !important; }
.stSuccess { border-color: var(--green) !important; }
.stWarning { border-color: var(--amber) !important; }
.stError   { border-color: var(--red) !important; }

.logo-text {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.6rem;
    letter-spacing: 0.1em;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
</style>
""", unsafe_allow_html=True)

PLOTLY_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="IBM Plex Mono, monospace", color="#8899bb", size=11),
    margin=dict(l=10, r=10, t=40, b=10),
    xaxis=dict(gridcolor="#1e2535", showline=False, zeroline=False, tickcolor="#4a5878"),
    yaxis=dict(gridcolor="#1e2535", showline=False, zeroline=False, tickcolor="#4a5878"),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#1e2535", borderwidth=1),
)
GREEN  = "#00e676"
RED    = "#ff1744"
BLUE   = "#00d4ff"
PURPLE = "#7c3aed"
AMBER  = "#ffc400"

MONTHS = ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
          "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
MONTH_EN = ["January","February","March","April","May","June",
            "July","August","September","October","November","December"]
DIAS = ["Lu","Ma","Mi","Ju","Vi"]

# =====================================================================
# 🛡️ COMPUERTA DE SEGURIDAD (SISTEMA DE LOGIN)
# =====================================================================
from login import requerir_autenticacion, boton_cerrar_sesion

# Si el estudiante no se ha autenticado, se pausa la carga de toda la app aquí:
if not requerir_autenticacion():
    st.stop()

# Si ya inició sesión correctamente, mostramos el botón de salir en la barra lateral:
boton_cerrar_sesion()
# =====================================================================

# ─── Data persistence helpers ─────────────────────────────────────────────────
def get_data_key(): return "trading_data_v2"

def init_data():
    """Initialize empty data structure for 12 months."""
    data = {}
    for m in range(1, 13):
        data[m] = {
            "config": {"balance_inicial": 1000.0, "contratos": 1, "comision": 5.0},
            "trades": {}  # key: "YYYY-MM-DD", val: {ops, ganadoras, perdedoras, pts_pos, pts_neg}
        }
    return data

def load_data():
    if get_data_key() not in st.session_state:
        st.session_state[get_data_key()] = init_data()
    return st.session_state[get_data_key()]

def save_data(data):
    st.session_state[get_data_key()] = data

# ─── Calculation helpers ──────────────────────────────────────────────────────
def calc_day(row: dict):
    ops = row.get("ops", 0)
    gan = row.get("ganadoras", 0)
    per = row.get("perdedoras", 0)
    pts_pos = row.get("pts_pos", 0.0)
    pts_neg = row.get("pts_neg", 0.0)
    balance = pts_pos - pts_neg
    tasa = (gan / ops * 100) if ops > 0 else 0
    avg_win = (pts_pos / gan) if gan > 0 else 0
    avg_loss = (pts_neg / per) if per > 0 else 0
    rr = (avg_win / avg_loss) if avg_loss > 0 else (avg_win if gan > 0 else 0)
    insight = get_insight(tasa, rr, ops)
    return dict(ops=ops, ganadoras=gan, perdedoras=per,
                pts_pos=pts_pos, pts_neg=pts_neg, balance=balance,
                tasa=tasa, avg_win=avg_win, avg_loss=avg_loss, rr=rr, insight=insight)

def get_insight(tasa, rr, ops):
    if ops == 0: return "Sin operaciones"
    if tasa == 100: return "Día perfecto 🎯"
    if tasa >= 80 and rr >= 2: return "Operativa eficiente ✅"
    if tasa >= 50 and rr >= 1.5: return "Buen desempeño 👍"
    if tasa >= 40 and rr >= 1: return "Resultado aceptable ⚖️"
    if tasa < 40 or rr < 0.5: return "Revisar errores ⚠️"
    if tasa < 0: return "Día negativo ❌"
    return "En desarrollo 📈"

def get_month_stats(data, month):
    trades = data[month]["trades"]
    if not trades:
        return None
    rows = [calc_day(v) for v in trades.values()]
    total_ops = sum(r["ops"] for r in rows)
    total_gan = sum(r["ganadoras"] for r in rows)
    total_per = sum(r["perdedoras"] for r in rows)
    total_pts_pos = sum(r["pts_pos"] for r in rows)
    total_pts_neg = sum(r["pts_neg"] for r in rows)
    total_bal = total_pts_pos - total_pts_neg
    tasa_mes = (total_gan / total_ops * 100) if total_ops > 0 else 0
    avg_win = (total_pts_pos / total_gan) if total_gan > 0 else 0
    avg_loss = (total_pts_neg / total_per) if total_per > 0 else 0
    rr_mes = (avg_win / avg_loss) if avg_loss > 0 else avg_win
    cfg = data[month]["config"]
    bal_ini = cfg["balance_inicial"]
    contratos = cfg["contratos"]
    comision = cfg["comision"]
    resultado_pts = total_bal
    comisiones_total = total_ops * comision
    resultado_usd = ((resultado_pts * contratos)*50) - comisiones_total
    retorno_pct = ((resultado_usd / bal_ini) * 100) if bal_ini > 0 else 0
    return dict(
        total_ops=total_ops, total_gan=total_gan, total_per=total_per,
        total_pts_pos=total_pts_pos, total_pts_neg=total_pts_neg, total_bal=total_bal,
        tasa=tasa_mes, avg_win=avg_win, avg_loss=avg_loss, rr=rr_mes,
        resultado_usd=resultado_usd, comisiones=comisiones_total,
        bal_ini=bal_ini, contratos=contratos, retorno_pct=retorno_pct,
        dias_activos=len([r for r in rows if r["ops"] > 0]),
        total_dias=len(rows),
    )

def get_week_dates(year, month, week_num):
    """Return list of (date, day_label) for a trading week (Mon-Fri)."""
    first = date(year, month, 1)
    weeks = []
    cur = first
    week_start = None
    wk = 0
    while cur.month == month:
        if cur.weekday() == 0:  # Monday
            wk += 1
            week_start = cur
        if wk == week_num and cur.weekday() < 5:
            weeks.append(cur)
        cur += timedelta(days=1)
    return weeks

def get_all_weeks(year, month):
    """Return dict of week_num -> list of dates."""
    first = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    last = date(year, month, last_day)
    weeks = {}
    cur = first
    wk = None
    for day in range(1, last_day + 1):
        d = date(year, month, day)
        if d.weekday() == 0:
            wk = len(weeks) + 1
            weeks[wk] = []
        if wk and d.weekday() < 5:
            weeks.setdefault(wk, []).append(d)
    return weeks

# ─── Sidebar ──────────────────────────────────────────────────────────────────
data = load_data()

with st.sidebar:
    st.markdown('<div class="logo-text">📊 TRADING TRACKER</div>', unsafe_allow_html=True)
    st.caption("Backtesting & Seguimiento 2026")
    st.divider()

    st.markdown('<div class="section-hdr">Navegación</div>', unsafe_allow_html=True)
    page = st.radio("", ["📥 Registro de Trades", "📈 Dashboard Mensual",
                         "🗓️ Resumen Anual", "⚙️ Configuración"],
                    label_visibility="collapsed")

    st.divider()
    st.markdown('<div class="section-hdr">Mes Activo</div>', unsafe_allow_html=True)
    current_month = st.selectbox("", MONTHS, index=date.today().month - 1,
                                 label_visibility="collapsed")
    month_idx = MONTHS.index(current_month) + 1

    st.divider()
    cfg = data[month_idx]["config"]
    st.markdown('<div class="section-hdr">Config del Mes</div>', unsafe_allow_html=True)
    cfg["balance_inicial"] = st.number_input("Balance Inicial ($)", value=float(cfg["balance_inicial"]),
                                              min_value=0.0, step=100.0)
    cfg["contratos"] = st.number_input("N° Contratos", value=int(cfg["contratos"]),
                                        min_value=1, max_value=100, step=1)
    cfg["comision"] = st.number_input("Comisión / trade ($)", value=float(cfg["comision"]),
                                       min_value=0.0, step=0.5)
    save_data(data)

YEAR = 2026

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — REGISTRO DE TRADES
# ══════════════════════════════════════════════════════════════════════════════
if page == "📥 Registro de Trades":
    st.markdown(f"# REGISTRO — {current_month.upper()} {YEAR}")
    st.markdown(f'<div style="color:var(--muted2);font-family:\'IBM Plex Mono\',monospace;font-size:0.8rem;margin-bottom:1.5rem">Ingresa operaciones día a día · Solo completa días con actividad</div>', unsafe_allow_html=True)

    weeks = get_all_weeks(YEAR, month_idx)

    for wk_num, dates_list in weeks.items():
        if not dates_list:
            continue
        st.markdown(f'<div class="section-hdr">Semana {wk_num}</div>', unsafe_allow_html=True)

        # Table header
        hcols = st.columns([1, 1, 1.5, 1.5, 1.5, 1.5, 1.5, 2])
        hcols[0].markdown('<div style="font-size:0.65rem;color:var(--muted2);font-weight:700;letter-spacing:0.1em">DÍA</div>', unsafe_allow_html=True)
        hcols[1].markdown('<div style="font-size:0.65rem;color:var(--muted2);font-weight:700;letter-spacing:0.1em">FECHA</div>', unsafe_allow_html=True)
        hcols[2].markdown('<div style="font-size:0.65rem;color:var(--muted2);font-weight:700;letter-spacing:0.1em">OPS TOTAL</div>', unsafe_allow_html=True)
        hcols[3].markdown('<div style="font-size:0.65rem;color:var(--green);font-weight:700;letter-spacing:0.1em">GANADORAS</div>', unsafe_allow_html=True)
        hcols[4].markdown('<div style="font-size:0.65rem;color:var(--red);font-weight:700;letter-spacing:0.1em">PERDEDORAS</div>', unsafe_allow_html=True)
        hcols[5].markdown('<div style="font-size:0.65rem;color:var(--green);font-weight:700;letter-spacing:0.1em">PTS +</div>', unsafe_allow_html=True)
        hcols[6].markdown('<div style="font-size:0.65rem;color:var(--red);font-weight:700;letter-spacing:0.1em">PTS −</div>', unsafe_allow_html=True)
        hcols[7].markdown('<div style="font-size:0.65rem;color:var(--muted2);font-weight:700;letter-spacing:0.1em">INSIGHT</div>', unsafe_allow_html=True)

        week_ops = week_gan = week_per = 0
        week_pp = week_pm = 0.0

        for d in dates_list:
            day_key = d.strftime("%Y-%m-%d")
            day_data = data[month_idx]["trades"].get(day_key, {})
            dia_label = DIAS[d.weekday()]

            cols = st.columns([1, 1, 1.5, 1.5, 1.5, 1.5, 1.5, 2])
            cols[0].markdown(f'<div style="font-family:\'IBM Plex Mono\',monospace;font-weight:700;padding-top:0.5rem">{dia_label}</div>', unsafe_allow_html=True)
            cols[1].markdown(f'<div style="font-family:\'IBM Plex Mono\',monospace;color:var(--muted2);font-size:0.8rem;padding-top:0.5rem">{d.strftime("%d/%m")}</div>', unsafe_allow_html=True)

            with cols[2]:
                ops = st.number_input("", min_value=0, max_value=50, value=int(day_data.get("ops", 0)),
                                       key=f"ops_{day_key}", label_visibility="collapsed")
            with cols[3]:
                gan = st.number_input("", min_value=0, max_value=50, value=int(day_data.get("ganadoras", 0)),
                                       key=f"gan_{day_key}", label_visibility="collapsed")
            with cols[4]:
                per = st.number_input("", min_value=0, max_value=50, value=int(day_data.get("perdedoras", 0)),
                                       key=f"per_{day_key}", label_visibility="collapsed")
            with cols[5]:
                pp = st.number_input("", min_value=0.0, value=float(day_data.get("pts_pos", 0.0)),
                                      key=f"pp_{day_key}", format="%.2f", step=0.25, label_visibility="collapsed")
            with cols[6]:
                pm = st.number_input("", min_value=0.0, value=float(day_data.get("pts_neg", 0.0)),
                                      key=f"pm_{day_key}", format="%.2f", step=0.25, label_visibility="collapsed")

            # Auto-calc insight
            calc = calc_day({"ops": ops, "ganadoras": gan, "perdedoras": per, "pts_pos": pp, "pts_neg": pm})
            ins = calc["insight"]
            if ops == 0:
                chip_class = "chip-gray"
            elif "eficiente" in ins or "perfecto" in ins:
                chip_class = "chip-green"
            elif "emocional" in ins or "negativo" in ins or "errores" in ins:
                chip_class = "chip-red"
            elif "Buen" in ins or "aceptable" in ins:
                chip_class = "chip-blue"
            else:
                chip_class = "chip-amber"
            cols[7].markdown(f'<div style="padding-top:0.35rem"><span class="insight-chip {chip_class}">{ins}</span></div>', unsafe_allow_html=True)

            # Save to data
            data[month_idx]["trades"][day_key] = {
                "ops": ops, "ganadoras": gan, "perdedoras": per, "pts_pos": pp, "pts_neg": pm
            }
            week_ops += ops; week_gan += gan; week_per += per
            week_pp += pp; week_pm += pm

        # Week summary bar
        w_bal = week_pp - week_pm
        w_color = "green-val" if w_bal >= 0 else "red-val"
        w_tasa = (week_gan / week_ops * 100) if week_ops > 0 else 0
        st.markdown(
            f'<div style="background:var(--bg3);border:1px solid var(--border);border-left:3px solid var(--accent);'
            f'border-radius:4px;padding:0.6rem 1rem;margin:0.3rem 0 1rem 0;display:flex;gap:2rem;font-family:\'IBM Plex Mono\',monospace;font-size:0.78rem">'
            f'<span style="color:var(--muted2)">SEMANA {wk_num}</span>'
            f'<span>Ops: <b>{week_ops}</b></span>'
            f'<span style="color:var(--green)">✓ {week_gan}</span>'
            f'<span style="color:var(--red)">✗ {week_per}</span>'
            f'<span>Tasa: <b style="color:{"var(--green)" if w_tasa>=50 else ("var(--amber)" if w_tasa>=40 else "var(--red)")}">{w_tasa:.0f}%</b></span>'
            f'<span>Pts +{week_pp:.2f} / −{week_pm:.2f}</span>'
            f'<span class="{w_color}">Balance: <b>{"+" if w_bal>=0 else ""}{w_bal:.2f}</b></span>'
            f'</div>',
            unsafe_allow_html=True
        )

    save_data(data)

    # Month quick summary at bottom
    stats = get_month_stats(data, month_idx)
    if stats and stats["total_ops"] > 0:
        st.divider()
        st.markdown("### RESUMEN DEL MES")
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Operaciones", stats["total_ops"])
        m2.metric("Tasa de Éxito", f"{stats['tasa']:.1f}%",
                  f"+{stats['total_gan']} ganadoras")
        m3.metric("Balance Puntos", f"{'+' if stats['total_bal']>=0 else ''}{stats['total_bal']:.2f}",
                  f"R/B: {stats['rr']:.2f}")
        m4.metric("Prom Ganancia", f"{stats['avg_win']:.2f} pts")
        m5.metric("Prom Pérdida", f"{stats['avg_loss']:.2f} pts")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — DASHBOARD MENSUAL
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📈 Dashboard Mensual":
    st.markdown(f"# DASHBOARD — {current_month.upper()} {YEAR}")

    stats = get_month_stats(data, month_idx)
    if not stats or stats["total_ops"] == 0:
        st.info(f"📭 Aún no hay operaciones registradas para {current_month}. Ve a **Registro de Trades** para comenzar.")
        st.stop()

    # ── KPI Cards ──────────────────────────────────────────────────────────────
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    bal_color = "green" if stats["total_bal"] >= 0 else "red"
    res_color = "green" if stats["resultado_usd"] >= 0 else "red"

    k1.markdown(f'''
    <div class="kpi-card blue">
        <div class="kpi-label">Operaciones Totales</div>
        <div class="kpi-value">{stats["total_ops"]}</div>
        <div class="kpi-sub">{stats["dias_activos"]} días activos</div>
    </div>''', unsafe_allow_html=True)

    tasa_col = "green" if stats["tasa"] >= 50 else ("amber" if stats["tasa"] >= 40 else "red")
    k2.markdown(f'''
    <div class="kpi-card {tasa_col}">
        <div class="kpi-label">Tasa de Éxito</div>
        <div class="kpi-value {tasa_col}-val">{stats["tasa"]:.1f}%</div>
        <div class="kpi-sub">{stats["total_gan"]} ✓ · {stats["total_per"]} ✗</div>
    </div>''', unsafe_allow_html=True)

    k3.markdown(f'''
    <div class="kpi-card {bal_color}">
        <div class="kpi-label">Balance de Puntos</div>
        <div class="kpi-value {bal_color}-val">{"+" if stats["total_bal"]>=0 else ""}{stats["total_bal"]:.2f}</div>
        <div class="kpi-sub">+{stats["total_pts_pos"]:.2f} / −{stats["total_pts_neg"]:.2f}</div>
    </div>''', unsafe_allow_html=True)

    rr_col = "green" if stats["rr"] >= 1.5 else ("amber" if stats["rr"] >= 1 else "red")
    k4.markdown(f'''
    <div class="kpi-card {rr_col}">
        <div class="kpi-label">Riesgo / Beneficio</div>
        <div class="kpi-value {rr_col}-val">{stats["rr"]:.2f}</div>
        <div class="kpi-sub">Prom win: {stats["avg_win"]:.2f} · loss: {stats["avg_loss"]:.2f}</div>
    </div>''', unsafe_allow_html=True)

    k5.markdown(f'''
    <div class="kpi-card {res_color}">
        <div class="kpi-label">Resultado (USD)</div>
        <div class="kpi-value {res_color}-val">{"+" if stats["resultado_usd"]>=0 else ""}${stats["resultado_usd"]:,.2f}</div>
        <div class="kpi-sub">Comisiones: −${stats["comisiones"]:.2f}</div>
    </div>''', unsafe_allow_html=True)

    ret_color = "green" if stats["retorno_pct"] >= 0 else "red"
    ret_color = "green" if stats["retorno_pct"] >= 0 else "red"
    k6.markdown(f'''
    <div class="kpi-card {ret_color}">
        <div class="kpi-label">Retorno Mensual</div>
        <div class="kpi-value {ret_color}-val">{"+" if stats["retorno_pct"]>=0 else ""}{stats["retorno_pct"]:.2f}%</div>
        <div class="kpi-sub">Sobre ${stats["bal_ini"]:,.0f} inicial</div>
    </div>''', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Build daily dataframe ──────────────────────────────────────────────────
    rows = []
    for day_key, vals in sorted(data[month_idx]["trades"].items()):
        if vals.get("ops", 0) == 0: continue
        d = datetime.strptime(day_key, "%Y-%m-%d").date()
        calc = calc_day(vals)
        rows.append({"fecha": d, "dia": DIAS[d.weekday()], **calc})
    df = pd.DataFrame(rows)

    if df.empty:
        st.info("No hay días con operaciones para graficar.")
        st.stop()

    df["cumbal"] = df["balance"].cumsum()

    # ── Equity Curve ───────────────────────────────────────────────────────────
    st.markdown('<div class="section-hdr">Curva de Equidad (Puntos)</div>', unsafe_allow_html=True)
    fig_eq = go.Figure()
    # Fill area
    fig_eq.add_trace(go.Scatter(
        x=df["fecha"].astype(str), y=df["cumbal"],
        fill="tozeroy",
        fillcolor="rgba(0,212,255,0.07)",
        line=dict(color=BLUE, width=2.5),
        mode="lines+markers",
        marker=dict(size=7, color=BLUE, line=dict(width=1, color="#000")),
        name="Balance acumulado",
        hovertemplate="<b>%{x}</b><br>Balance: %{y:.2f} pts<extra></extra>",
    ))
    # Zero line
    fig_eq.add_hline(y=0, line_dash="dash", line_color="#1e2535", line_width=1)
    fig_eq.update_layout(**PLOTLY_THEME, height=280,
                          yaxis_title="Puntos", xaxis_title="")
    st.plotly_chart(fig_eq, use_container_width=True)

    # ── Two charts side by side ────────────────────────────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<div class="section-hdr">Operaciones por Día</div>', unsafe_allow_html=True)
        fig_ops = go.Figure()
        fig_ops.add_trace(go.Bar(x=df["fecha"].astype(str), y=df["ganadoras"],
                                  name="Ganadoras", marker_color=GREEN, opacity=0.85))
        fig_ops.add_trace(go.Bar(x=df["fecha"].astype(str), y=-df["perdedoras"],
                                  name="Perdedoras", marker_color=RED, opacity=0.85))
        fig_ops.add_hline(y=0, line_color="#1e2535", line_width=1)
        fig_ops.update_layout(**{**PLOTLY_THEME, "legend": dict(orientation="h", y=1.1)},
                               height=250, barmode="overlay")
        st.plotly_chart(fig_ops, use_container_width=True)

    with col_b:
        st.markdown('<div class="section-hdr">Tasa de Éxito por Día (%)</div>', unsafe_allow_html=True)
        colors_tasa = [GREEN if t >= 50 else (AMBER if t >= 40 else RED) for t in df["tasa"]]
        fig_tasa = go.Figure()
        fig_tasa.add_trace(go.Bar(
            x=df["fecha"].astype(str), y=df["tasa"],
            marker_color=colors_tasa, opacity=0.9,
            hovertemplate="<b>%{x}</b><br>Tasa: %{y:.1f}%<extra></extra>",
            name="Tasa de éxito",
        ))
        fig_tasa.add_hline(y=50, line_dash="dot", line_color=GREEN, line_width=1,
                            annotation_text="50%", annotation_position="right")
        fig_tasa.add_hline(y=40, line_dash="dot", line_color=AMBER, line_width=1,
                            annotation_text="40%", annotation_position="right")
        fig_tasa.update_layout(**{**PLOTLY_THEME, "yaxis": dict(**PLOTLY_THEME["yaxis"], range=[0, 110])},
                                height=250)
        st.plotly_chart(fig_tasa, use_container_width=True)

    # ── R/B Ratio and Puntos chart ─────────────────────────────────────────────
    col_c, col_d = st.columns(2)

    with col_c:
        st.markdown('<div class="section-hdr">Ratio Riesgo / Beneficio</div>', unsafe_allow_html=True)
        colors_rr = [GREEN if r >= 1.5 else (AMBER if r >= 1 else RED) for r in df["rr"]]
        fig_rr = go.Figure()
        fig_rr.add_trace(go.Scatter(
            x=df["fecha"].astype(str), y=df["rr"],
            mode="lines+markers",
            line=dict(color=PURPLE, width=2),
            marker=dict(size=8, color=colors_rr, line=dict(width=1.5, color="#000")),
            hovertemplate="<b>%{x}</b><br>R/B: %{y:.2f}<extra></extra>",
        ))
        fig_rr.add_hline(y=1.5, line_dash="dot", line_color=GREEN, line_width=1,
                          annotation_text="1.5 objetivo", annotation_position="right")
        fig_rr.add_hline(y=1, line_dash="dot", line_color=AMBER, line_width=1)
        fig_rr.update_layout(**PLOTLY_THEME, height=250)
        st.plotly_chart(fig_rr, use_container_width=True)

    with col_d:
        st.markdown('<div class="section-hdr">Distribución Pts + / Pts −</div>', unsafe_allow_html=True)
        fig_pts = go.Figure()
        fig_pts.add_trace(go.Bar(x=df["fecha"].astype(str), y=df["pts_pos"],
                                  name="Pts +", marker_color=GREEN, opacity=0.8))
        fig_pts.add_trace(go.Bar(x=df["fecha"].astype(str), y=-df["pts_neg"],
                                  name="Pts −", marker_color=RED, opacity=0.8))
        fig_pts.add_hline(y=0, line_color="#1e2535", line_width=1)
        fig_pts.update_layout(**{**PLOTLY_THEME, "legend": dict(orientation="h", y=1.1)},
                               height=250, barmode="stack")
        st.plotly_chart(fig_pts, use_container_width=True)

    # ── Tabla detallada ────────────────────────────────────────────────────────
    st.markdown('<div class="section-hdr">Detalle Diario</div>', unsafe_allow_html=True)
    disp = df[["fecha","dia","ops","ganadoras","perdedoras","pts_pos","pts_neg","balance","tasa","rr","insight"]].copy()
    disp.columns = ["Fecha","Día","Ops","Ganadoras","Perdedoras","Pts +","Pts −","Balance","Tasa %","R/B","Insight"]
    disp["Fecha"] = disp["Fecha"].astype(str)
    disp["Tasa %"] = disp["Tasa %"].map(lambda x: f"{x:.1f}%")
    disp["R/B"] = disp["R/B"].map(lambda x: f"{x:.2f}")
    disp["Balance"] = disp["Balance"].map(lambda x: f"+{x:.2f}" if x >= 0 else f"{x:.2f}")
    st.dataframe(disp, hide_index=True, use_container_width=True)

    # ── Gauge Tasa de éxito ────────────────────────────────────────────────────
    st.divider()
    g1, g2, g3 = st.columns(3)

    with g1:
        st.markdown('<div class="section-hdr">Tasa de Éxito Global</div>', unsafe_allow_html=True)
        fig_g1 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=stats["tasa"],
            number={"suffix": "%", "valueformat": ".1f", "font": {"family": "IBM Plex Mono", "size": 28,
                    "color": GREEN if stats["tasa"]>=50 else (AMBER if stats["tasa"]>=40 else RED)}},
            gauge={"axis": {"range": [0, 100]},
                   "bar": {"color": GREEN if stats["tasa"]>=50 else (AMBER if stats["tasa"]>=40 else RED)},
                   "bgcolor": "#161b27", "bordercolor": "#1e2535",
                   "steps": [{"range":[0,40],"color":"rgba(255,23,68,0.1)"},
                              {"range":[40,50],"color":"rgba(255,196,0,0.08)"},
                              {"range":[50,100],"color":"rgba(0,230,118,0.1)"}],
                   "threshold":{"line":{"color":"white","width":2},"thickness":0.8,"value":60}},
        ))
        fig_g1.update_layout(paper_bgcolor="rgba(0,0,0,0)", height=200,
                              margin=dict(l=20,r=20,t=20,b=10), font=dict(color="#e2e8f5"))
        st.plotly_chart(fig_g1, use_container_width=True)

    with g2:
        st.markdown('<div class="section-hdr">Ratio R/B</div>', unsafe_allow_html=True)
        fig_g2 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=stats["rr"],
            number={"valueformat": ".2f", "font": {"family": "IBM Plex Mono", "size": 28,
                    "color": GREEN if stats["rr"]>=1.5 else (AMBER if stats["rr"]>=1 else RED)}},
            gauge={"axis": {"range": [0, 5]},
                   "bar": {"color": GREEN if stats["rr"]>=1.5 else (AMBER if stats["rr"]>=1 else RED)},
                   "bgcolor": "#161b27", "bordercolor": "#1e2535",
                   "steps": [{"range":[0,1],"color":"rgba(255,23,68,0.1)"},
                              {"range":[1,1.5],"color":"rgba(255,196,0,0.08)"},
                              {"range":[1.5,5],"color":"rgba(0,230,118,0.1)"}],
                   "threshold":{"line":{"color":"white","width":2},"thickness":0.8,"value":1.5}},
        ))
        fig_g2.update_layout(paper_bgcolor="rgba(0,0,0,0)", height=200,
                              margin=dict(l=20,r=20,t=20,b=10), font=dict(color="#e2e8f5"))
        st.plotly_chart(fig_g2, use_container_width=True)

    with g3:
        st.markdown('<div class="section-hdr">Distribución de Resultados</div>', unsafe_allow_html=True)
        fig_pie = go.Figure(go.Pie(
            labels=["Ganadoras", "Perdedoras"],
            values=[stats["total_gan"], stats["total_per"]],
            hole=0.6,
            marker=dict(colors=[GREEN, RED]),
            textfont=dict(family="IBM Plex Mono", size=11),
        ))
        fig_pie.update_layout(**{**PLOTLY_THEME, "margin": dict(l=20,r=20,t=20,b=10)},
                               height=200)
        st.plotly_chart(fig_pie, use_container_width=True)

    # ── Insights del mes ──────────────────────────────────────────────────────
    st.divider()
    st.markdown('<div class="section-hdr">Análisis de Insights</div>', unsafe_allow_html=True)
    insight_counts = df["insight"].value_counts()
    ic1, ic2 = st.columns(2)
    with ic1:
        for ins, cnt in insight_counts.items():
            chip = "chip-gray"
            if "eficiente" in ins or "perfecto" in ins: chip = "chip-green"
            elif "emocional" in ins or "negativo" in ins or "errores" in ins: chip = "chip-red"
            elif "Buen" in ins or "aceptable" in ins: chip = "chip-blue"
            elif "desarrollo" in ins: chip = "chip-amber"
            st.markdown(f'<span class="insight-chip {chip}">{ins}</span> &nbsp; <span style="font-family:\'IBM Plex Mono\',monospace;color:var(--muted2)">{cnt} días</span><br>', unsafe_allow_html=True)
    with ic2:
        dias_ef = len(df[df["insight"].str.contains("eficiente|perfecto", na=False)])
        dias_em = len(df[df["insight"].str.contains("emocional|negativo|errores", na=False)])
        dias_ok = len(df) - dias_ef - dias_em
        st.markdown(f"""
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.85rem;line-height:2">
        <span style="color:var(--green)">● Días eficientes:</span> {dias_ef} / {len(df)}<br>
        <span style="color:var(--amber)">● Días aceptables:</span> {dias_ok} / {len(df)}<br>
        <span style="color:var(--red)">● Días con errores:</span> {dias_em} / {len(df)}<br>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — RESUMEN ANUAL
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🗓️ Resumen Anual":
    st.markdown(f"# RESUMEN ANUAL {YEAR}")
    st.markdown('<div style="color:var(--muted2);font-family:\'IBM Plex Mono\',monospace;font-size:0.8rem;margin-bottom:1.5rem">Consolidado de todos los meses con actividad</div>', unsafe_allow_html=True)

    # Build annual dataframe
    ann_rows = []
    for m in range(1, 13):
        s = get_month_stats(data, m)
        if s and s["total_ops"] > 0:
            ann_rows.append({"mes": MONTHS[m-1], "mes_idx": m, **s})
    ann_df = pd.DataFrame(ann_rows)

    if ann_df.empty:
        st.info("📭 No hay datos registrados aún. Comienza en **Registro de Trades**.")
        st.stop()

    # Annual KPIs
    total_ops = ann_df["total_ops"].sum()
    total_gan = ann_df["total_gan"].sum()
    total_per = ann_df["total_per"].sum()
    total_bal = ann_df["total_bal"].sum()
    total_usd = ann_df["resultado_usd"].sum()
    tasa_anual = (total_gan / total_ops * 100) if total_ops > 0 else 0
    avg_rr = ann_df["rr"].mean()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Operaciones Totales", f"{total_ops:,}", f"{len(ann_df)} meses activos")
    k2.metric("Tasa de Éxito Anual", f"{tasa_anual:.1f}%", f"{total_gan} ganadoras")
    k3.metric("Balance de Puntos", f"{'+'if total_bal>=0 else ''}{total_bal:.2f}",
              f"{'+'if total_usd>=0 else ''}${total_usd:,.2f} USD")
    k4.metric("Ratio R/B Promedio", f"{avg_rr:.2f}")

    st.divider()

    # ── Monthly performance bars ───────────────────────────────────────────────
    st.markdown('<div class="section-hdr">Balance de Puntos por Mes</div>', unsafe_allow_html=True)
    colors_ann = [GREEN if v >= 0 else RED for v in ann_df["total_bal"]]
    fig_ann = go.Figure()
    fig_ann.add_trace(go.Bar(
        x=ann_df["mes"], y=ann_df["total_bal"],
        marker_color=colors_ann, opacity=0.85,
        hovertemplate="<b>%{x}</b><br>Balance: %{y:.2f} pts<extra></extra>",
    ))
    fig_ann.add_hline(y=0, line_color="#1e2535", line_width=1)
    fig_ann.update_layout(**PLOTLY_THEME, height=280, yaxis_title="Puntos")
    st.plotly_chart(fig_ann, use_container_width=True)

    # ── Cumulative equity ──────────────────────────────────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<div class="section-hdr">Curva de Equidad Acumulada</div>', unsafe_allow_html=True)
        ann_df_sorted = ann_df.sort_values("mes_idx")
        cum_bal = ann_df_sorted["total_bal"].cumsum()
        fig_cum = go.Figure()
        fig_cum.add_trace(go.Scatter(
            x=ann_df_sorted["mes"], y=cum_bal,
            fill="tozeroy", fillcolor="rgba(0,212,255,0.06)",
            line=dict(color=BLUE, width=2.5),
            mode="lines+markers",
            marker=dict(size=8, color=BLUE),
            hovertemplate="<b>%{x}</b><br>Acumulado: %{y:.2f} pts<extra></extra>",
        ))
        fig_cum.add_hline(y=0, line_dash="dash", line_color="#1e2535", line_width=1)
        fig_cum.update_layout(**PLOTLY_THEME, height=260, yaxis_title="Puntos acumulados")
        st.plotly_chart(fig_cum, use_container_width=True)

    with col_b:
        st.markdown('<div class="section-hdr">Tasa de Éxito por Mes</div>', unsafe_allow_html=True)
        tasa_colors = [GREEN if t >= 50 else (AMBER if t >= 40 else RED) for t in ann_df_sorted["tasa"]]
        fig_tasa_ann = go.Figure()
        fig_tasa_ann.add_trace(go.Bar(
            x=ann_df_sorted["mes"], y=ann_df_sorted["tasa"],
            marker_color=tasa_colors, opacity=0.85,
            hovertemplate="<b>%{x}</b><br>Tasa: %{y:.1f}%<extra></extra>",
        ))
        fig_tasa_ann.add_hline(y=50, line_dash="dot", line_color=GREEN, line_width=1,
                                annotation_text="50% meta", annotation_position="right")
        fig_tasa_ann.update_layout(**{**PLOTLY_THEME, "yaxis": dict(**PLOTLY_THEME["yaxis"], range=[0, 110])},
                                    height=260)
        st.plotly_chart(fig_tasa_ann, use_container_width=True)

    # ── Monthly table ──────────────────────────────────────────────────────────
    st.markdown('<div class="section-hdr">Tabla Comparativa Mensual</div>', unsafe_allow_html=True)
    tbl = ann_df[["mes","total_ops","total_gan","total_per","tasa","total_bal","rr","resultado_usd"]].copy()
    tbl.columns = ["Mes","Ops","Ganadoras","Perdedoras","Tasa %","Balance Pts","R/B","Resultado USD"]
    tbl["Tasa %"] = tbl["Tasa %"].map(lambda x: f"{x:.1f}%")
    tbl["Balance Pts"] = tbl["Balance Pts"].map(lambda x: f"+{x:.2f}" if x >= 0 else f"{x:.2f}")
    tbl["R/B"] = tbl["R/B"].map(lambda x: f"{x:.2f}")
    tbl["Resultado USD"] = tbl["Resultado USD"].map(lambda x: f"+${x:,.2f}" if x >= 0 else f"-${abs(x):,.2f}")
    st.dataframe(tbl, hide_index=True, use_container_width=True)

    # ── R/B scatter ─────────────────────────────────────────────────────────────
    st.markdown('<div class="section-hdr">Tasa de Éxito vs Ratio R/B</div>', unsafe_allow_html=True)
    fig_sc = go.Figure()
    fig_sc.add_trace(go.Scatter(
        x=ann_df["tasa"], y=ann_df["rr"],
        mode="markers+text",
        text=ann_df["mes"],
        textposition="top center",
        textfont=dict(family="IBM Plex Mono", size=10, color="#8899bb"),
        marker=dict(size=14, color=ann_df["total_bal"],
                    colorscale=[[0, RED], [0.5, AMBER], [1, GREEN]],
                    showscale=True,
                    colorbar=dict(title="Balance pts", tickfont=dict(family="IBM Plex Mono"))),
        hovertemplate="<b>%{text}</b><br>Tasa: %{x:.1f}%<br>R/B: %{y:.2f}<extra></extra>",
    ))
    fig_sc.add_vline(x=50, line_dash="dot", line_color=GREEN, line_width=1)
    fig_sc.add_hline(y=1.5, line_dash="dot", line_color=PURPLE, line_width=1)
    fig_sc.update_layout(**PLOTLY_THEME, height=320,
                          xaxis_title="Tasa de Éxito (%)", yaxis_title="Ratio R/B")
    st.plotly_chart(fig_sc, use_container_width=True)
    st.caption("🟢 Zona ideal: Tasa > 50% y R/B > 1.5 · Tamaño/color del punto = balance de puntos")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — CONFIGURACIÓN
# ══════════════════════════════════════════════════════════════════════════════
elif page == "⚙️ Configuración":
    st.markdown("# CONFIGURACIÓN")
    st.markdown('<div style="color:var(--muted2);margin-bottom:1.5rem">Gestión de datos, exportación y parámetros globales.</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Exportar Datos")
        st.write("Descarga todos tus registros como JSON para respaldo.")
        export_json = json.dumps(
            {str(k): v for k, v in data.items()}, default=str, indent=2
        )
        st.download_button(
            label="⬇️ Descargar JSON",
            data=export_json,
            file_name=f"trading_tracker_{YEAR}.json",
            mime="application/json",
            use_container_width=True,
        )

        st.markdown("### Cargar Datos")
        st.write("Restaura un respaldo previo.")
        uploaded = st.file_uploader("Subir JSON", type=["json"])
        if uploaded:
            try:
                loaded = json.load(uploaded)
                new_data = {int(k): v for k, v in loaded.items()}
                save_data(new_data)
                st.success("✅ Datos cargados correctamente. Recarga la página.")
            except Exception as e:
                st.error(f"Error al cargar: {e}")

    with col2:
        st.markdown("### Reiniciar Datos")
        st.warning("⚠️ Esta acción borrará **todos** los registros del año. No hay vuelta atrás.")
        confirm = st.checkbox("Confirmo que quiero borrar todos los datos")
        if st.button("🗑️ Reiniciar", disabled=not confirm):
            save_data(init_data())
            st.success("Datos reiniciados. Recarga la página.")

        st.markdown("### Guía de Métricas")
        metrics_guide = {
            "Tasa de Éxito": "% de operaciones ganadoras. Meta: ≥ 60%",
            "Ratio R/B": "Ganancia promedio / Pérdida promedio. Meta: ≥ 1.5",
            "Balance Puntos": "Suma de Pts+ menos Pts− del período",
            "Op. Eficiente": "Tasa ≥ 80% y R/B ≥ 2",
            "Error Emocional": "Tasa < 40% o R/B < 0.5",
            "Buen Desempeño": "Tasa ≥ 60% y R/B ≥ 1.5",
        }
        for k, v in metrics_guide.items():
            st.markdown(f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.78rem;margin:0.4rem 0"><span style="color:var(--accent)">{k}:</span> <span style="color:var(--muted2)">{v}</span></div>', unsafe_allow_html=True)
