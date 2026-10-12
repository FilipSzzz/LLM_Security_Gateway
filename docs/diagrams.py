"""Draw README diagrams: light background, dark text, no orange/yellow."""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)

TEXT = "#1A1A1A"
MUTED = "#555555"
STYLE = {
    "done": {"fc": "#DDF0E4", "ec": "#2E7D4F", "ls": "-"},
    "wip": {"fc": "#DCE8F7", "ec": "#2B5C9E", "ls": "-"},
    "planned": {"fc": "#F4F4F4", "ec": "#8A8A8A", "ls": "--"},
}
LABEL = {"done": "Done", "wip": "In progress", "planned": "Planned"}


def box(ax, x, y, w, h, title, sub="", status="done", title_size=11):
    s = STYLE[status]
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.02,rounding_size=0.08",
            fc=s["fc"],
            ec=s["ec"],
            ls=s["ls"],
            lw=1.6,
        )
    )
    if sub:
        ax.text(
            x + w / 2,
            y + h * 0.66,
            title,
            ha="center",
            va="center",
            fontsize=title_size,
            weight="bold",
            color=TEXT,
        )
        ax.text(
            x + w / 2,
            y + h * 0.30,
            sub,
            ha="center",
            va="center",
            fontsize=8.8,
            color=MUTED,
            linespacing=1.3,
        )
    else:
        ax.text(
            x + w / 2,
            y + h / 2,
            title,
            ha="center",
            va="center",
            fontsize=title_size,
            weight="bold",
            color=TEXT,
        )


def arrow(ax, p1, p2, color=TEXT, style="-|>", ls="-"):
    ax.add_patch(
        FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=14, color=color, lw=1.4, ls=ls)
    )


def legend(ax, x, y):
    for i, key in enumerate(["done", "wip", "planned"]):
        s = STYLE[key]
        ax.add_patch(
            FancyBboxPatch(
                (x + i * 1.9, y),
                0.35,
                0.22,
                boxstyle="round,pad=0.01,rounding_size=0.04",
                fc=s["fc"],
                ec=s["ec"],
                ls=s["ls"],
                lw=1.4,
            )
        )
        ax.text(x + i * 1.9 + 0.5, y + 0.11, LABEL[key], va="center", fontsize=10, color=TEXT)


def canvas(w, h):
    fig, ax = plt.subplots(figsize=(w, h), dpi=160)
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.axis("off")
    return fig, ax


def architecture():
    fig, ax = canvas(15, 6.6)
    ax.text(0.3, 6.25, "Request flow through the gateway", fontsize=15, weight="bold", color=TEXT)
    legend(ax, 9.3, 6.2)

    # outer actors
    box(ax, 0.3, 3.0, 1.7, 1.2, "Client app", "has a gateway\nAPI key only", "done")
    box(ax, 13.0, 3.0, 1.7, 1.2, "LLM provider", "OpenRouter\n(swappable)", "done")

    # gateway frame
    ax.add_patch(
        FancyBboxPatch(
            (2.5, 0.9),
            10.0,
            4.9,
            boxstyle="round,pad=0.02,rounding_size=0.15",
            fc="white",
            ec="#3A3A3A",
            lw=1.4,
        )
    )
    ax.text(2.7, 5.5, "LLM Security Gateway (FastAPI)", fontsize=12, weight="bold", color=TEXT)
    ax.text(
        2.7,
        5.2,
        "holds the real provider key - inspects every prompt and every answer",
        fontsize=9.5,
        color=MUTED,
    )

    w, h, gap = 1.75, 1.15, 0.22
    xs = [2.75 + i * (w + gap) for i in range(5)]
    top = 3.55
    req = [
        ("1. Auth +\nrate limit", "per API key\n(Redis)", "planned"),
        ("2. Validation", "Pydantic: type,\nlength 1-8000", "done"),
        ("3. Injection\ndetectors", "regex rules (TOML),\nblock = 400", "done"),
        ("4. PII masking", "PESEL, e-mail,\ncard numbers", "planned"),
        ("5. Forward", "httpx AsyncClient,\ntimeouts, errors", "done"),
    ]
    for x, (t, s, st) in zip(xs, req, strict=True):
        box(ax, x, top, w, h, t, s, st, title_size=9.5)
    for a, b in zip(xs, xs[1:], strict=False):
        arrow(ax, (a + w, top + h / 2), (b, top + h / 2))

    bottom = 1.25
    resp = [
        (xs[4], "6. Output checks", "leaked secrets,\nsystem prompt", "planned"),
        (xs[2], "7. Response", "only the `reply`\nfield + request ID", "done"),
    ]
    for x, t, s, st in resp:
        box(ax, x, bottom, w, h, t, s, st, title_size=9.5)
    arrow(ax, (xs[4], bottom + h / 2), (xs[2] + w, bottom + h / 2))

    # side services
    box(
        ax,
        xs[0],
        bottom,
        w,
        h,
        "Incident log",
        "PostgreSQL\n(decision, reason)",
        "planned",
        title_size=9.5,
    )
    arrow(ax, (xs[2], bottom + h / 2), (xs[0] + w, bottom + h / 2), color="#8A8A8A", ls="--")

    # client <-> gateway, gateway <-> provider
    arrow(ax, (2.0, 3.85), (xs[0], top + h / 2))
    ax.text(0.35, 4.35, "POST /v1/chat", fontsize=9, color=MUTED)
    arrow(ax, (xs[2] + w / 2, bottom), (xs[2] + w / 2, 0.55), style="-")
    arrow(ax, (xs[2] + w / 2, 0.55), (1.15, 0.55), style="-")
    arrow(ax, (1.15, 0.55), (1.15, 3.0))
    ax.text(1.3, 0.68, "200 + reply, or an error status (4xx / 5xx)", fontsize=8.5, color=MUTED)

    arrow(ax, (xs[4] + w, top + h / 2), (13.0, 3.95))
    arrow(ax, (13.0, 3.25), (xs[4] + w, bottom + h / 2))
    ax.text(13.85, 2.7, "model answer", fontsize=9, color=MUTED, ha="center")

    ax.text(
        2.7,
        0.15,
        "Each detector returns one decision: allow, allow after modification "
        "(masking), or block - with a reason.",
        fontsize=9.5,
        color=MUTED,
    )
    fig.savefig(OUT / "architecture.png", bbox_inches="tight", facecolor="white")


def roadmap():
    fig, ax = canvas(15, 6.4)
    ax.text(0.3, 6.0, "Roadmap", fontsize=15, weight="bold", color=TEXT)
    legend(ax, 9.3, 5.95)
    items = [
        ("0. Transparent proxy", "FastAPI, httpx, settings,\nerror mapping, respx tests", "done"),
        ("1. First detector", "regex rules, detector\ninterface, block response", "done"),
        ("2. Benchmark", "~200 labeled prompts,\nprecision, recall, p95;\nvs LLM Guard", "wip"),
        ("3. Monitoring", "Prometheus metrics,\nGrafana RED dashboard", "planned"),
        ("4. PII masking", "PESEL checksum,\ne-mail, card numbers", "planned"),
        ("5. Rate limiting", "Redis, per API key", "planned"),
        ("6. Access mgmt", "hashed keys, roles,\nPostgreSQL, 401 vs 403", "planned"),
        ("7. LLM-as-judge", "second model for\nsuspicious prompts", "planned"),
        ("8. Detector registry", "plug-in detectors,\nper-tenant config", "planned"),
        ("9. Workflows", "Celery, async review,\nsigned webhooks", "planned"),
        ("10. Demo + deploy", "dashboard, README,\none-command start", "planned"),
    ]
    w, h, gx = 2.1, 1.75, 0.3
    rows = [(items[:6], 3.55), (items[6:], 1.0)]
    for row, y in rows:
        xs = [0.4 + i * (w + gx) for i in range(len(row))]
        for x, (t, s, st) in zip(xs, row, strict=True):
            box(ax, x, y, w, h, t, s, st, title_size=9.5)
        for a, b in zip(xs, xs[1:], strict=False):
            arrow(ax, (a + w, y + h / 2), (b, y + h / 2))
    # wrap from row 1 end to row 2 start
    last_x = 0.4 + 5 * (w + gx) + w / 2
    arrow(ax, (last_x, 3.55), (last_x, 3.15), style="-")
    arrow(ax, (last_x, 3.15), (0.4 + w / 2, 3.15), style="-")
    arrow(ax, (0.4 + w / 2, 3.15), (0.4 + w / 2, 1.0 + h))
    ax.text(
        0.4,
        0.45,
        "Each stage ends with working code, tests and a written design decision.",
        fontsize=9.5,
        color=MUTED,
    )
    fig.savefig(OUT / "roadmap.png", bbox_inches="tight", facecolor="white")


architecture()
roadmap()
print("ok")
