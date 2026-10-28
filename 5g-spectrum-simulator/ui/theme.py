"""Calibration Bench design tokens and the global Streamlit stylesheet.

The palette is deliberately narrow: a speckled grey bench, white measurement
plates, one ink, and a single sandy chrome colour reserved for the two shell
bands. Nothing on the content surfaces carries a semantic hue - gains and
losses are signed numerals and printed p-values, never colour.
"""
from __future__ import annotations

import base64
from typing import Dict

import streamlit as st

#: Python-side mirror of the CSS custom properties, for matplotlib figures.
TOKENS: Dict[str, str] = {
    "bench": "#EBE9E9",
    "paper": "#FFFFFF",
    "ink": "#10171D",
    "amber": "#FCB07E",
    "ink_55": "#6E7276",
    "ink_35": "#A9A7A7",
    "hair": "#CFCDCD",
    "font": "Chivo",
}

#: 16x16 line icons for the sidebar, as inline SVG data URIs.
_ICONS: Dict[str, str] = {
    "Overview": "<path d='M2 12.6 5.6 9l3 2.2L14 4'/><path d='M10.4 4H14v3.6'/>",
    "Live Simulation": "<circle cx='8' cy='8' r='5.9'/><path d='M6.6 5.5 10.4 8 6.6 10.5Z'/>",
    "Predictor": "<path d='M1.6 8h2.1l1.6-4.3L7.5 12l1.9-6 1.3 4h2.1'/>",
    "Ablation": "<path d='M2 5.2h12M2 11h12'/><circle cx='6' cy='5.2' r='1.7'/><circle cx='10.4' cy='11' r='1.7'/>",
    "Methodology": "<path d='M8 3.3C6.4 2.2 4 1.9 2 2.3v9.9c2-.4 4.4 0 6 1.1 1.6-1.1 4-1.5 6-1.1V2.3c-2-.4-4.4 0-6 1z'/><path d='M8 3.5v10'/>",
}

_FUNNEL = "<path d='M2.2 3.2h11.6L9.4 8.6v4.1l-2.8-1.6V8.6Z'/>"


def _data_uri(path_markup: str, opacity: float) -> str:
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16' fill='none' "
        f"stroke='#10171D' stroke-opacity='{opacity}' stroke-width='1.4' "
        f"stroke-linecap='round' stroke-linejoin='round'>{path_markup}</svg>"
    )
    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"url(\"data:image/svg+xml;base64,{encoded}\")"


def _nav_icon_css() -> str:
    """One rule per sidebar row, so the active row carries the ink icon."""
    rules = []
    for index, (label, markup) in enumerate(_ICONS.items(), start=1):
        dim = _data_uri(markup, 0.45)
        solid = _data_uri(markup, 0.85)
        selector = (
            '[data-testid="stSidebar"] .st-key-nav [data-testid="stRadioGroup"] '
            f'> div:nth-child({index}) label[data-testid="stRadioOption"]'
        )
        rules.append(f"{selector}{{background-image:{dim};}}")
        rules.append(
            f'[data-testid="stSidebar"] .st-key-nav [data-testid="stRadioGroup"] '
            f'> div[data-selected="true"]:nth-child({index}) label{{background-image:{solid};}}'
        )
    return "\n".join(rules)


_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Chivo:wght@400;500;600;700&display=swap');

:root{
  --bench:#EBE9E9; --paper:#FFFFFF; --ink:#10171D; --amber:#FCB07E;
  --ink-80:rgba(16,23,29,.80); --ink-75:rgba(16,23,29,.75); --ink-70:rgba(16,23,29,.70);
  --ink-65:rgba(16,23,29,.65); --ink-60:rgba(16,23,29,.60); --ink-55:rgba(16,23,29,.55);
  --ink-50:rgba(16,23,29,.50); --ink-45:rgba(16,23,29,.45); --ink-40:rgba(16,23,29,.40);
  --ink-25:rgba(16,23,29,.25); --hair:rgba(16,23,29,.20); --hair-strong:rgba(16,23,29,.35);
  --plate:14px; --ctl:10px;
}

html, body, .stApp, [data-testid="stAppViewContainer"]{
  font-family:'Chivo', ui-sans-serif, system-ui, sans-serif;
  font-variant-numeric: tabular-nums;
  color: var(--ink);
  background: var(--bench);
}
[data-testid="stAppViewContainer"]{ background-color:var(--bench); }
[data-testid="stSidebar"], [data-testid="stMain"], [data-testid="stMarkdownContainer"],
[data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] p{ color:var(--ink); }
[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"],
#MainMenu, footer, [data-testid="stStatusWidget"], [data-testid="stAppDeployButton"]{ display:none !important; }
[data-testid="stMain"]{ background:var(--bench); }
[data-testid="stMainBlockContainer"], .block-container{ padding:0 !important; max-width:100% !important; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"]{ gap:0; }

/* ── sidebar ─────────────────────────────────────────────────────────── */
[data-testid="stSidebar"]{
  width:224px !important; min-width:224px !important; max-width:224px !important;
  background-color:var(--bench);
  background-image:radial-gradient(rgba(16,23,29,.055) .6px, transparent .7px),
                   radial-gradient(rgba(16,23,29,.035) .6px, transparent .7px);
  background-size:5px 5px, 13px 11px;
  background-position:0 0, 3px 4px;
  border-right:1px solid var(--hair);
}
[data-testid="stSidebarContent"]{ padding:16px; }
[data-testid="stSidebarUserContent"]{ padding:0; }
[data-testid="stSidebar"] [data-testid="stVerticalBlock"]{ gap:10px; }
[data-testid="stSidebarCollapseButton"], [data-testid="stSidebarCollapsedControl"]{ display:none !important; }

.brand{ padding-bottom:12px; border-bottom:1px solid var(--hair); font-size:13px; font-weight:600; line-height:1.25; letter-spacing:-.01em; color:var(--ink); }
.side-label{ font-size:11px; font-weight:500; color:var(--ink-60); }
.side-list{ margin-top:6px; display:flex; flex-direction:column; gap:4px; }
.side-row{ display:flex; align-items:center; justify-content:space-between; font-size:11px; line-height:16px; color:var(--ink-80); }
.side-row .muted{ color:var(--ink-50); }
.side-rule{ margin-top:12px; padding-top:12px; border-top:1px solid var(--hair); }

[data-testid="stSidebar"] [data-testid="stRadioGroup"]{ display:flex; flex-direction:column; gap:1px; }
[data-testid="stSidebar"] [data-testid="stWidgetLabel"]{ display:none; }
[data-testid="stSidebar"] [data-testid="stRadioGroup"] > div{ margin:0; }
[data-testid="stSidebar"] label[data-testid="stRadioOption"]{
  display:flex; align-items:center; height:34px; min-height:34px; margin:0;
  padding:0 10px 0 26px; border-radius:var(--ctl);
  background-color:transparent; background-repeat:no-repeat;
  background-position:8px center; background-size:14px 14px;
  transition:background-color .15s ease;
}
[data-testid="stSidebar"] label[data-testid="stRadioOption"]:hover{ background-color:rgba(255,255,255,.55); }
[data-testid="stSidebar"] label[data-testid="stRadioOption"] > div > div:first-child{ display:none; }
[data-testid="stSidebar"] label[data-testid="stRadioOption"] p{ margin:0; font-size:13px; color:var(--ink-70); }
[data-testid="stSidebar"] [data-selected="true"] label[data-testid="stRadioOption"]{ background-color:var(--paper); }
[data-testid="stSidebar"] [data-selected="true"] label[data-testid="stRadioOption"] p{
  color:var(--ink); font-weight:600; border-bottom:2px solid var(--amber); padding-bottom:3px;
}

/* ── header + amber scope bar ────────────────────────────────────────── */
.bench-header{
  height:52px; display:flex; align-items:center; justify-content:space-between;
  padding:0 16px; border-bottom:1px solid var(--hair); background:var(--bench);
}
.bench-header-title{ font-size:15px; font-weight:600; line-height:1; }
.bench-header-fields{ display:flex; align-items:center; gap:12px; }
.hdr-field{ display:flex; align-items:baseline; gap:6px; }
.hdr-label{ font-size:11px; color:var(--ink-60); }
.hdr-value{ font-size:12px; font-weight:500; }
.hdr-div{ width:1px; height:12px; background:var(--ink-25); }

.st-key-scope{
  background-color:var(--amber);
  background-image:radial-gradient(rgba(16,23,29,.07) .6px, transparent .7px);
  background-size:6px 6px;
  border-bottom:1px solid var(--ink-25);
  padding:0 16px; height:52px; display:flex; align-items:center;
}
.st-key-scope > div{ width:100%; }
.st-key-scope [data-testid="stVerticalBlock"]{ gap:0; }
.st-key-scope [data-testid="stHorizontalBlock"]{ align-items:center; gap:12px; }
.st-key-scope [data-testid="stRadio"]{ display:flex; align-items:center; gap:8px; min-width:0; }
.st-key-scope [data-testid="stWidgetLabel"]{ flex:0 0 auto; margin:0; padding:0; min-height:0; }
.st-key-scope [data-testid="stWidgetLabel"] p{
  font-size:11px; font-weight:600; color:var(--ink-75); display:flex; align-items:center;
  gap:5px; white-space:nowrap;
}
.st-key-scope [data-testid="stWidgetLabel"] p::before{
  content:""; width:13px; height:13px; display:inline-block;
  background:__FUNNEL__ no-repeat center/13px 13px;
}
.st-key-scope [data-testid="stRadioGroup"]{
  display:flex; align-items:center; flex-wrap:nowrap; gap:2px; min-width:0;
  background:rgba(16,23,29,.10); padding:3px; border-radius:14px;
}
.st-key-scope [data-testid="stRadioGroup"] > div{ margin:0; flex:0 0 auto; }
.st-key-scope label[data-testid="stRadioOption"]{
  height:26px; min-height:26px; margin:0; padding:0 9px; border-radius:var(--ctl);
  display:flex; align-items:center; background-color:transparent;
}
.st-key-scope label[data-testid="stRadioOption"] > div > div:first-child{ display:none; }
.st-key-scope label[data-testid="stRadioOption"] p{ margin:0; font-size:12px; color:var(--ink-75); white-space:nowrap; }
.st-key-scope [data-selected="true"] label[data-testid="stRadioOption"]{ background-color:var(--paper); }
.st-key-scope [data-selected="true"] label[data-testid="stRadioOption"] p{ color:var(--ink); font-weight:600; }

.scope-fields{ display:flex; align-items:center; gap:12px; flex-wrap:wrap; }
.scope-field{ display:flex; align-items:baseline; gap:6px; }
.scope-label{ font-size:11px; color:var(--ink-60); }
.scope-value{ font-size:12px; font-weight:500; }
.scope-div{ width:1px; height:12px; background:var(--ink-25); }

/* ── content scaffolding ─────────────────────────────────────────────── */
.st-key-content{ padding:12px 16px 16px; }
.st-key-content [data-testid="stVerticalBlock"]{ gap:12px; }
[data-testid="stMarkdownContainer"] p{ margin:0; }

/* Streamlit puts the container key on the vertical block itself, so the plate
   styles must not change its display: that is what keeps the children stacked. */
[class*="st-key-plate_"], .bench-plate{
  background:var(--paper); border:1px solid var(--hair);
  border-radius:var(--plate); padding:10px 16px; gap:4px;
}
.st-key-plate_map{
  background-image:linear-gradient(to right, rgba(16,23,29,.055) 1px, transparent 1px),
                   linear-gradient(to bottom, rgba(16,23,29,.055) 1px, transparent 1px);
  background-size:16px 16px; background-position:-1px -1px;
}
.st-key-plate_stats{ padding:12px 16px; gap:6px; }

.sec-row{ display:flex; align-items:baseline; justify-content:space-between; gap:12px; margin-bottom:4px; }
.sec-title{ font-size:13px; font-weight:600; }
.sec-meta{ font-size:11px; color:var(--ink-55); text-align:right; }

/* ── framing ─────────────────────────────────────────────────────────── */
.framing{ display:grid; grid-template-columns:1fr 1px 1fr; align-items:start; }
.framing-col{ padding-right:20px; }
.framing-col.right{ padding-right:0; padding-left:20px; }
.framing-rule{ width:1px; height:76px; background:var(--hair); }
.framing-label{ font-size:11px; font-weight:600; color:var(--ink-60); }
.framing-line{ font-size:13px; line-height:18px; margin-top:4px; }
.framing-line b{ font-weight:600; }
.framing-line i{ font-style:normal; font-weight:500; }

/* ── component substitution map ──────────────────────────────────────── */
.route{ display:flex; align-items:stretch; margin-top:0; }
.route + .route{ margin-top:8px; }
.cfg{ background:var(--paper); border:1px solid var(--ink-25); border-radius:var(--plate); padding:8px 12px; }
.cfg.strong{ border-color:rgba(16,23,29,.45); }
.cfg-name{ font-size:13px; font-weight:500; line-height:16px; white-space:nowrap; }
.cfg.strong .cfg-name{ font-weight:600; }
.cfg-spec{ display:grid; grid-template-columns:68px 1fr; gap:0 6px; margin:4px 0 0; }
.cfg-spec dt, .cfg-spec dd{ font-size:11px; line-height:13px; margin:0; }
.cfg-spec dt{ color:var(--ink-55); white-space:nowrap; }
.cfg-spec dd{ margin:0; }
.step{ display:flex; flex-direction:column; align-items:center; justify-content:center; padding:0 8px; }
.step-label{ font-size:10px; line-height:12px; text-align:center; color:var(--ink-60); }
.step-arrow{ display:flex; align-items:center; width:100%; margin-top:4px; }
.step-line{ height:1px; flex:1; background:rgba(16,23,29,.40); }
.step-tip{ font-size:12px; line-height:1; color:var(--ink-60); }
.strongest{ padding:4px 0 0 8px; font-size:10.5px; font-weight:500; color:var(--ink-70); white-space:nowrap; }

/* ── tables ──────────────────────────────────────────────────────────── */
.bench-table{ width:100%; border-collapse:collapse; table-layout:fixed; }
.bench-table th{
  font-size:10.5px; font-weight:400; color:var(--ink-65); text-align:left;
  padding:6px 0 6px; border-bottom:1px solid var(--hair-strong); vertical-align:bottom;
}
.bench-table th.num, .bench-table td.num{ text-align:right; }
.bench-table td{ height:35px; border-bottom:1px solid rgba(16,23,29,.12); font-size:14px; vertical-align:middle; }
.bench-table tr:last-child td{ border-bottom:none; }
.bench-table td.name{ font-weight:500; }
.bench-table tr.is-strong td{ font-weight:600; }
.badge{ margin-left:8px; font-size:10px; font-weight:400; color:var(--ink-60); white-space:nowrap; }

.strip-table{ width:100%; border-collapse:collapse; table-layout:fixed; }
.strip-table th{ font-size:10px; font-weight:400; color:var(--ink-65); text-align:left; padding:0 0 4px; border-bottom:1px solid var(--hair); }
.strip-table th.num, .strip-table td.num{ text-align:right; }
.strip-table td{ height:30px; border-bottom:1px solid rgba(16,23,29,.10); font-size:12px; vertical-align:middle; }
.strip-table tr:last-child td{ border-bottom:none; }
.strip-table td.metric{ font-weight:500; }
.strip-params{ font-size:11px; color:var(--ink-60); margin-left:8px; }
.value-strong{ font-weight:600; }
.compare-name{ display:block; font-size:10px; line-height:12px; color:var(--ink-60); }
.compare-value{ display:block; text-align:right; font-size:12px; }
.ci{ position:relative; height:14px; }
.ci-base{ position:absolute; left:0; right:0; top:50%; height:1px; background:var(--ink-25); }
.ci-bar{ position:absolute; top:50%; height:2px; margin-top:-1px; background:rgba(16,23,29,.55); }
.ci-bar.cls{ background:rgba(16,23,29,.35); }
.ci-tick{ position:absolute; top:50%; width:1px; height:8px; transform:translateY(-50%); background:rgba(16,23,29,.70); }
.ci-bar.cls + .ci-tick{ background:rgba(16,23,29,.50); }
.ci-dot{ position:absolute; top:50%; width:5px; height:5px; border-radius:50%; background:var(--ink); transform:translate(-50%,-50%); }
.ci-dot.cls{ background:rgba(16,23,29,.60); }
.ci-cell{ display:flex; align-items:center; gap:8px; padding-right:12px; }
.ci-cell .ci{ flex:1; }
.ci-value{ width:44px; text-align:right; }
.ci-value.compare{ width:50px; }
.ci-name{ width:104px; white-space:nowrap; font-size:10px; line-height:12px; color:var(--ink-60); }

.stat-grid{ display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); }
.stat-cell{ padding-right:24px; }
.stat-label{ font-size:11px; color:var(--ink-60); }
.stat-value{ font-size:26px; font-weight:600; letter-spacing:-.01em; margin-top:4px; }
.stat-note{ font-size:11px; color:var(--ink-60); margin-top:4px; }
.swap{ text-align:center; font-size:14px; color:var(--ink-45); padding-bottom:8px; }
.empty-state{ font-size:12px; color:var(--ink-60); padding:4px 0 2px; }

/* ── controls ────────────────────────────────────────────────────────── */
[data-testid="stBaseButton-secondary"]{
  height:32px; min-height:32px; padding:0 12px; border-radius:var(--plate);
  border:1px solid var(--ink-25); background:transparent; color:var(--ink);
  font-family:inherit; font-size:12px; font-weight:500; box-shadow:none;
}
[data-testid="stBaseButton-secondary"]:hover{
  background:var(--paper); border-color:rgba(16,23,29,.45); color:var(--ink);
}
[data-testid="stBaseButton-secondary"]:focus:not(:active){ color:var(--ink); border-color:var(--ink-25); }
[data-testid="stBaseButton-primary"]{
  height:32px; min-height:32px; padding:0 14px; border-radius:var(--plate);
  border:none; background:var(--ink); color:var(--bench);
  font-family:inherit; font-size:12px; font-weight:500; box-shadow:none;
}
[data-testid="stBaseButton-primary"]:hover{ background:#1F272D; color:var(--bench); }
[data-testid="stBaseButton-primary"]:focus:not(:active){ color:var(--bench); }
[data-testid="stBaseButton-primary"] p,
[data-testid="stBaseButton-primary"] [data-testid="stMarkdownContainer"],
[data-testid="stBaseButton-primary"] [data-testid="stMarkdownContainer"] p{ color:var(--bench) !important; font-size:12px; }
[data-testid="stBaseButton-secondary"] p,
[data-testid="stBaseButton-secondary"] [data-testid="stMarkdownContainer"] p{ color:var(--ink) !important; font-size:12px; }

[data-baseweb="select"] > div{
  background:var(--paper) !important; border:1px solid var(--ink-25) !important;
  border-radius:var(--ctl) !important; min-height:32px !important;
  font-size:12px !important; color:var(--ink) !important;
}
[data-baseweb="select"] svg{ color:var(--ink-55); }
[data-baseweb="popover"] li{ font-size:12px; }
[data-testid="stNumberInput"] input, [data-testid="stTextInput"] input{
  background:var(--paper); border:1px solid var(--ink-25); border-radius:var(--ctl);
  font-size:12px; color:var(--ink);
}
[data-testid="stWidgetLabel"] p{ font-size:11px; color:var(--ink-60); }
[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"]{ background:var(--ink); }

[data-testid="stExpander"] details{ border:none; background:transparent; }
[data-testid="stExpander"] summary{
  padding:0; font-size:11px; color:var(--ink-60); font-weight:400;
  text-decoration:underline; text-underline-offset:2px;
}
[data-testid="stExpander"] summary:hover{ color:var(--ink); }
[data-testid="stExpander"] summary svg{ display:none; }
[data-testid="stExpander"] [data-testid="stExpanderDetails"]{ padding:8px 0 0; }

[data-testid="stAlert"]{
  background:var(--paper); border:1px solid var(--hair); border-radius:12px;
  color:var(--ink-70); font-size:12px;
}
[data-testid="stAlert"] p{ font-size:12px; }

[data-testid="stTabs"] [role="tablist"]{
  display:inline-flex; gap:2px; background:rgba(16,23,29,.08);
  padding:3px; border-radius:12px; width:fit-content; align-self:flex-start;
}
[data-testid="stTab"]{
  height:30px; min-height:30px; padding:0 12px; border-radius:9px;
  display:flex; align-items:center; color:var(--ink-70); background:transparent;
}
[data-testid="stTab"] [data-testid="stMarkdownContainer"] p{ font-size:12px; color:inherit; margin:0; }
[data-testid="stTab"][aria-selected="true"]{ background:var(--paper); color:var(--ink); }
[data-testid="stTab"][aria-selected="true"] p{ font-weight:600; color:var(--ink); }
[data-testid="stTabs"] .react-aria-SelectionIndicator{ display:none !important; }
[data-testid="stTabPanel"]{ padding-top:12px; }

[data-testid="stDataFrame"]{ border:1px solid var(--hair); border-radius:12px; overflow:hidden; background:var(--paper); }

.prose{ font-size:13px; line-height:19px; color:var(--ink-80); }
.prose p{ margin:0 0 8px; }
.prose code{ font-size:12px; background:rgba(16,23,29,.06); padding:1px 4px; border-radius:4px; }
.prose strong{ font-weight:600; color:var(--ink); }
"""


def inject() -> None:
    """Install the stylesheet once per page load."""
    css = _CSS.replace("__FUNNEL__", _data_uri(_FUNNEL, 0.75))
    css = css + "\n" + _nav_icon_css()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
