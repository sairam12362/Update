"""Static HTML components for the Calibration Bench shell.

These are presentational only: they take already-computed values and emit
markup. Widgets (selectors, buttons, expanders) stay in the view modules.
"""
from __future__ import annotations

import html
from typing import List, Optional, Sequence

from core import results as R


def esc(value: object) -> str:
    return html.escape(str(value))


# ---------------------------------------------------------------------------
# Shell
# ---------------------------------------------------------------------------
def brand_html(title: str = "Spectrum Allocation Benchmark") -> str:
    lines = title.split(" Benchmark")
    first = esc(lines[0])
    second = "Benchmark" if len(lines) > 1 else ""
    return (
        '<div class="brand">'
        f"{first}<br>{second}"
        "</div>"
    )


def sources_html(sources: Sequence[str], artifacts: dict) -> str:
    rows = "".join(f'<div class="side-row"><span>{esc(s)}</span></div>' for s in sources)
    artifact_rows = "".join(
        f'<div class="side-row"><span>{esc(name)}</span>'
        f'<span class="muted">{"loaded" if loaded else "absent"}</span></div>'
        for name, loaded in artifacts.items()
    )
    return (
        f'<div class="side-rule"><div class="side-label">Sources</div>'
        f'<div class="side-list">{rows}</div></div>'
        f'<div class="side-rule"><div class="side-label">Model artifacts</div>'
        f'<div class="side-list">{artifact_rows}</div></div>'
    )


def page_header(title: str, fields: Sequence[tuple[str, str]]) -> str:
    chips = []
    for index, (label, value) in enumerate(fields):
        if index:
            chips.append('<span class="hdr-div"></span>')
        chips.append(
            f'<span class="hdr-field"><span class="hdr-label">{esc(label)}</span>'
            f'<span class="hdr-value">{esc(value)}</span></span>'
        )
    return (
        '<header class="bench-header">'
        f'<div class="bench-header-title">{esc(title)}</div>'
        f'<div class="bench-header-fields">{"".join(chips)}</div>'
        "</header>"
    )


def scope_fields(fields: Sequence[tuple[str, str]]) -> str:
    chips = []
    for index, (label, value) in enumerate(fields):
        if index:
            chips.append('<span class="scope-div"></span>')
        chips.append(
            f'<span class="scope-field"><span class="scope-label">{esc(label)}</span>'
            f'<span class="scope-value">{esc(value)}</span></span>'
        )
    return f'<div class="scope-fields">{"".join(chips)}</div>'


# ---------------------------------------------------------------------------
# Sections
# ---------------------------------------------------------------------------
def section_head(title: str, meta: str = "") -> str:
    meta_html = f'<div class="sec-meta">{esc(meta)}</div>' if meta else ""
    return f'<div class="sec-row"><div class="sec-title">{esc(title)}</div>{meta_html}</div>'


def framing(columns: Sequence[tuple[str, Sequence[str]]]) -> str:
    """Two unequal findings columns separated by a hairline; no card."""
    cells: List[str] = []
    for index, (label, lines) in enumerate(columns):
        if index:
            cells.append('<div class="framing-rule"></div>')
        body = "".join(f'<div class="framing-line">{line}</div>' for line in lines)
        cells.append(
            f'<div class="framing-col{" right" if index else ""}">'
            f'<div class="framing-label">{esc(label)}</div>{body}</div>'
        )
    return f'<section class="framing">{"".join(cells)}</section>'


def substitution_map(rows: Sequence[dict]) -> str:
    """Two routes of component swaps; arrows mean substitution, not causation.

    Each row is ``{"cards": [...], "steps": [...], "annotation": str|None}``
    where a card is ``{"name", "spec": [(k, v)], "strong", "width"}`` and a
    step is ``{"label", "width"}``.
    """
    html_rows: List[str] = []
    for row in rows:
        chunks: List[str] = []
        cards = row["cards"]
        steps = row.get("steps", [])
        for index, card in enumerate(cards):
            if index:
                step = steps[index - 1]
                chunks.append(
                    f'<div class="step" style="width:{step["width"]}px">'
                    f'<div class="step-label">{step["label"]}</div>'
                    '<div class="step-arrow"><span class="step-line"></span>'
                    '<span class="step-tip">\u2192</span></div></div>'
                )
            spec = "".join(
                f"<dt>{esc(k)}</dt><dd>{esc(v)}</dd>" for k, v in card["spec"]
            )
            chunks.append(
                f'<div class="cfg{" strong" if card.get("strong") else ""}" '
                f'style="width:{card["width"]}px">'
                f'<div class="cfg-name">{esc(card["name"])}</div>'
                f'<dl class="cfg-spec">{spec}</dl></div>'
            )
        if row.get("annotation"):
            chunks.append(f'<div class="strongest">{esc(row["annotation"])}</div>')
        html_rows.append(f'<div class="route">{"".join(chunks)}</div>')
    return "".join(html_rows)


def matrix_table(columns: Sequence[dict], rows: Sequence[dict]) -> str:
    """A semantic table styled as the flat bench grid.

    ``columns`` items: ``{"label", "width", "num"}``. ``rows`` items:
    ``{"cells": [...], "strong": bool, "badge": str|None}``.
    """
    colgroup = "".join(f'<col style="width:{col.get("width", "auto")}">' for col in columns)
    head = "".join(
        f'<th class="{"num" if col.get("num") else ""}">{esc(col["label"])}</th>'
        for col in columns
    )
    body: List[str] = []
    for row in rows:
        cells: List[str] = []
        for index, (col, value) in enumerate(zip(columns, row["cells"])):
            css = "num" if col.get("num") else ("name" if index == 0 else "")
            badge = ""
            if index == 0 and row.get("badge"):
                badge = f'<span class="badge">{esc(row["badge"])}</span>'
            cells.append(f'<td class="{css}">{value}{badge}</td>')
        strong = ' class="is-strong"' if row.get("strong") else ""
        body.append(f"<tr{strong}>{''.join(cells)}</tr>")
    return (
        '<table class="bench-table">'
        f"<colgroup>{colgroup}</colgroup>"
        f"<thead><tr>{head}</tr></thead>"
        f'<tbody>{"".join(body)}</tbody></table>'
    )


def kv_table(rows: Sequence[tuple[str, str]], key_width: str = "40%") -> str:
    colgroup = f'<col style="width:{key_width}"><col>'
    body = "".join(
        f'<tr><td class="name">{esc(key)}</td><td>{esc(value)}</td></tr>'
        for key, value in rows
    )
    return (
        f'<table class="bench-table" style="font-size:13px"><colgroup>{colgroup}</colgroup>'
        f'<tbody>{body}</tbody></table>'
    )


# ---------------------------------------------------------------------------
# Confidence-interval strip
# ---------------------------------------------------------------------------
def _positions(row: dict):
    """Map both intervals onto one row-local 0-100 scale."""
    proposed_ci = row.get("proposed_ci") or (row["proposed"], row["proposed"])
    classical_ci = row.get("classical_ci") or (row["classical"], row["classical"])
    low = min(proposed_ci[0], classical_ci[0], row["proposed"], row["classical"])
    high = max(proposed_ci[1], classical_ci[1], row["proposed"], row["classical"])
    span = high - low
    pad = span * 0.08 if span else 1.0

    def position(value: float) -> float:
        return 100.0 * (value - (low - pad)) / ((high + pad) - (low - pad))

    return position, proposed_ci, classical_ci


def _ci_markup(value: float, interval: tuple[float, float], position, strong: bool) -> str:
    left = position(interval[0])
    right = position(interval[1])
    dot = position(value)
    kind = "" if strong else " cls"
    return (
        '<div class="ci">'
        '<span class="ci-base"></span>'
        f'<span class="ci-bar{kind}" style="left:{left:.1f}%;right:{100 - right:.1f}%"></span>'
        f'<span class="ci-tick{kind}" style="left:{left:.1f}%"></span>'
        f'<span class="ci-tick{kind}" style="right:{100 - right:.1f}%"></span>'
        f'<span class="ci-dot{kind}" style="left:{dot:.1f}%"></span>'
        "</div>"
    )


def strip_table(rows: Sequence[dict]) -> str:
    head = (
        "<thead><tr>"
        "<th>Metric</th>"
        '<th>Proposed, mean [95% CI]</th>'
        '<th>Best classical, mean [95% CI]</th>'
        '<th class="num">\u0394, + better</th>'
        '<th class="num">p</th>'
        "</tr></thead>"
    )
    body: List[str] = []
    for row in rows:
        position, proposed_ci, classical_ci = _positions(row)
        improvement = R.fmt_p(row.get("improvement")) if row.get("improvement") is not None else "\u2014"
        improvement_value = row.get("improvement")
        delta = R.signed_pct(improvement_value)
        try:
            is_significant = float(row["p_value"]) < 0.05
        except (TypeError, ValueError):
            is_significant = False
        marker = ' <span style="font-size:10px;font-weight:600">*</span>' if is_significant else ' <span style="font-size:10px;color:var(--ink-60)">n.s.</span>'
        emphasis = ' class="value-strong"' if is_significant else ""
        body.append(
            "<tr>"
            f'<td class="metric">{esc(row["label"])}</td>'
            '<td><div class="ci-cell">'
            f'<span class="ci-value">{R.f3(row["proposed"])}</span>'
            f'{_ci_markup(row["proposed"], proposed_ci, position, True)}'
            "</div></td>"
            '<td><div class="ci-cell">'
            f'<span class="ci-name">{esc(row["comparator"])}</span>'
            f'<span class="ci-value compare">{R.f3(row["classical"])}</span>'
            f'{_ci_markup(row["classical"], classical_ci, position, False)}'
            "</div></td>"
            f'<td class="num"><span{emphasis}>{delta}</span></td>'
            f'<td class="num">{R.fmt_p(row["p_value"])}{marker}</td>'
            "</tr>"
        )
    colgroup = (
        '<colgroup><col style="width:150px"><col style="width:270px">'
        '<col style="width:326px"><col style="width:74px"><col style="width:84px"></colgroup>'
    )
    return f'<table class="strip-table">{colgroup}{head}<tbody>{"".join(body)}</tbody></table>'


# ---------------------------------------------------------------------------
# Stat plates (secondary pages)
# ---------------------------------------------------------------------------
def stat_plates(stats: Sequence[dict]) -> str:
    """``{"label", "value", "note"}`` rendered as flat typographic cells."""
    cells = []
    for stat in stats:
        cells.append(
            '<div class="stat-cell">'
            f'<div class="stat-label">{esc(stat["label"])}</div>'
            f'<div class="stat-value">{esc(stat["value"])}</div>'
            f'<div class="stat-note">{stat.get("note", "")}</div>'
            "</div>"
        )
    return f'<div class="stat-grid">{"".join(cells)}</div>'
