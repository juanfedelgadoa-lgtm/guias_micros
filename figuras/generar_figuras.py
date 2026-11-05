# -*- coding: utf-8 -*-
"""Genera las figuras SVG de la guia 'parcial2_tecnicas_sintesis.md'.
Uso:  python3 generar_figuras.py   (escribe los .svg en esta misma carpeta)
"""
import math, os

AQUI = os.path.dirname(os.path.abspath(__file__))

# Colores
AZUL = "#2b6cb0"; AZUL_C = "#e3f0fb"; ROJO = "#d62828"; AMAR = "#f2b134"
VERDE = "#2f855a"; NARANJA = "#dd6b20"; GRIS = "#555"; GRIS_C = "#f2f2f2"
CIAN = "#8ee6e0"; ROSA = "#f49ac8"; LILA = "#a8c7fa"
FONT = "font-family='Segoe UI,Arial,Helvetica,sans-serif'"


class SVG:
    def __init__(self, w, h):
        self.w, self.h, self.p = w, h, []

    def add(self, s):
        self.p.append(s)

    def rect(self, x, y, w, h, fill="white", stroke="#333", sw=1.5, rx=0, dash=None):
        d = f" stroke-dasharray='{dash}'" if dash else ""
        self.add(f"<rect x='{x}' y='{y}' width='{w}' height='{h}' rx='{rx}' fill='{fill}' stroke='{stroke}' stroke-width='{sw}'{d}/>")

    def line(self, x1, y1, x2, y2, stroke="#333", sw=1.5, dash=None, arrow=False):
        d = f" stroke-dasharray='{dash}'" if dash else ""
        a = " marker-end='url(#fl)'" if arrow else ""
        self.add(f"<line x1='{x1}' y1='{y1}' x2='{x2}' y2='{y2}' stroke='{stroke}' stroke-width='{sw}'{d}{a}/>")

    def poly(self, pts, stroke="#333", sw=1.5, fill="none", arrow=False, dash=None):
        d = f" stroke-dasharray='{dash}'" if dash else ""
        a = " marker-end='url(#fl)'" if arrow else ""
        s = " ".join(f"{x},{y}" for x, y in pts)
        self.add(f"<polyline points='{s}' fill='{fill}' stroke='{stroke}' stroke-width='{sw}'{d}{a}/>")

    def circle(self, x, y, r, fill="white", stroke=AZUL, sw=2):
        self.add(f"<circle cx='{x}' cy='{y}' r='{r}' fill='{fill}' stroke='{stroke}' stroke-width='{sw}'/>")

    def ellipse(self, x, y, rx, ry, fill="white", stroke=AZUL, sw=2):
        self.add(f"<ellipse cx='{x}' cy='{y}' rx='{rx}' ry='{ry}' fill='{fill}' stroke='{stroke}' stroke-width='{sw}'/>")

    def text(self, x, y, t, size=14, color="#222", anchor="middle", bold=False, italic=False):
        b = " font-weight='bold'" if bold else ""
        i = " font-style='italic'" if italic else ""
        t = t.replace("→", "->").replace("←", "<-").replace("≥", ">=").replace("≈", "~").replace("≤", "<=")
        t = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        self.add(f"<text x='{x}' y='{y}' {FONT} font-size='{size}' fill='{color}' text-anchor='{anchor}' dominant-baseline='middle'{b}{i}>{t}</text>")

    def label_box(self, x, y, t, size=12, color="#222", bg="white"):
        w = 7.2 * len(t) * size / 12 + 8
        self.rect(x - w / 2, y - size * 0.75, w, size * 1.5, fill=bg, stroke="none", sw=0, rx=3)
        self.text(x, y, t, size=size, color=color, bold=True)

    def save(self, nombre):
        cab = (f"<svg xmlns='http://www.w3.org/2000/svg' width='{self.w}' height='{self.h}' viewBox='0 0 {self.w} {self.h}'>"
               "<defs><marker id='fl' markerWidth='10' markerHeight='8' refX='9' refY='4' orient='auto'>"
               "<path d='M0,0 L10,4 L0,8 z' fill='#333'/></marker></defs>"
               f"<rect width='{self.w}' height='{self.h}' fill='white'/>")
        with open(os.path.join(AQUI, nombre), "w", encoding="utf-8") as f:
            f.write(cab + "".join(self.p) + "</svg>")


# ------------------------------------------------------------------ grafos
def arista(s, a, b, peso=None, tipo="comp", t=0.5, off=(0, 0), r=28):
    """tipo: comp (amarilla) | inc (roja punteada) | grupo (verde gruesa)"""
    (x1, y1), (x2, y2) = a, b
    if tipo == "comp":
        s.line(x1, y1, x2, y2, stroke=AMAR, sw=3)
    elif tipo == "inc":
        s.line(x1, y1, x2, y2, stroke=ROJO, sw=2.5, dash="9,6")
    else:
        s.line(x1, y1, x2, y2, stroke=VERDE, sw=4)
    if peso and peso != "0/0":
        mx, my = x1 + (x2 - x1) * t + off[0], y1 + (y2 - y1) * t + off[1]
        s.label_box(mx, my, peso, size=13, color="#222")


def nodo(s, x, y, t, r=28, fill="white", stroke=AZUL, sub=None, size=14):
    s.circle(x, y, r, fill=fill, stroke=stroke)
    if sub:
        s.text(x, y - 7, t, size=size, color=AZUL, bold=True)
        s.text(x, y + 10, sub, size=10, color=GRIS)
    else:
        s.text(x, y, t, size=size, color=AZUL, bold=True)


def leyenda_grafo(s, x, y):
    s.line(x, y, x + 40, y, stroke=AMAR, sw=3); s.text(x + 48, y, "compatibles (pueden compartir)", 12, anchor="start")
    s.line(x, y + 22, x + 40, y + 22, stroke=ROJO, sw=2.5, dash="9,6"); s.text(x + 48, y + 22, "incompatibles (mismo estado o distinto tipo)", 12, anchor="start")
    s.rect(x, y + 36, 40, 14, fill="white", stroke="none"); s.text(x + 20, y + 44, "f/d", 12, bold=True)
    s.text(x + 48, y + 44, "fuentes comunes / destinos comunes (sin número = 0/0)", 12, anchor="start")


# ------------------------------------------------------------------ figura: ASM del parcial
def fig_asm():
    s = SVG(760, 740)
    s.text(380, 22, "ASM del parcial (9 estados) y posibles líneas de corte", 17, bold=True)
    cajas = [
        ("S0", "a=in1, b=in2, x=in3, y=in4, Final=0"),
        ("S1", "t1 = x·x ;  t2 = 1 + x"),
        ("S2", "t3 = t1·x"),
        ("S3", "t4 = a·t1"),
        ("S4", "t5 = b·t3 ;  t6 = t2 + t4"),
        ("S5", "t8 = y·y ;  t7 = t6 + t5"),
        ("S6", "t9 = t8 + t7"),
        ("S7", "t9 = t9 >> 1"),
        ("S8", "out = t9 >> 1 ;  Final = 1"),
    ]
    x0, w, h = 150, 330, 46
    y = 50
    ys = []
    for i, (e, t) in enumerate(cajas):
        s.rect(x0, y, w, h, fill=AZUL_C, stroke=AZUL, sw=2)
        s.text(x0 + 10, y + 12, e, 12, color=AZUL, anchor="start", bold=True)
        s.text(x0 + w / 2 + 8, y + h / 2 + 3, t, 14)
        ys.append(y)
        if i == 0:
            # rombo inicio
            cy = y + h + 38
            s.line(x0 + w / 2, y + h, x0 + w / 2, cy - 20)
            s.poly([(x0 + w / 2, cy - 20), (x0 + w / 2 + 50, cy), (x0 + w / 2, cy + 20), (x0 + w / 2 - 50, cy), (x0 + w / 2, cy - 20)], stroke=AZUL, sw=2, fill="white")
            s.text(x0 + w / 2, cy, "Inicio", 13)
            s.poly([(x0 + w / 2 - 50, cy), (x0 - 30, cy), (x0 - 30, y + h / 2), (x0, y + h / 2)], arrow=True)
            s.text(x0 - 40, cy - 10, "0", 12)
            s.text(x0 + w / 2 + 12, cy + 30, "1", 12)
            s.line(x0 + w / 2, cy + 20, x0 + w / 2, cy + 46, arrow=True)
            y = cy + 46
        else:
            if i < len(cajas) - 1:
                s.line(x0 + w / 2, y + h, x0 + w / 2, y + h + 24, arrow=True)
            y += h + 24
    # retorno
    yl = ys[-1] + h / 2
    s.poly([(x0 + w, yl), (x0 + w + 30, yl), (x0 + w + 30, ys[0] + 10), (x0 + w, ys[0] + 10)], arrow=True)
    # lineas de corte
    def corte(i, color, txt, dash=None):
        yc = ys[i] + h + 12
        s.line(70, yc, 560, yc, stroke=color, sw=3, dash=dash)
        s.text(570, yc, txt, 12, color=color, anchor="start", bold=True)
    corte(4, "#999", "corte S4|S5 (2 ×, 2 +)", dash="6,4")
    corte(5, ROJO, "corte S5|S6 (el elegido)", None)
    corte(6, "#999", "corte S6|S7 (sin hardware extra)", dash="6,4")
    s.text(40, (ys[1] + ys[5]) / 2 + 20, "NIVEL", 13, color=VERDE, bold=True)
    s.text(40, (ys[1] + ys[5]) / 2 + 38, "SUPERIOR", 13, color=VERDE, bold=True)
    s.text(40, (ys[6] + ys[8]) / 2 + 20, "NIVEL", 13, color=NARANJA, bold=True)
    s.text(40, (ys[6] + ys[8]) / 2 + 38, "INFERIOR", 13, color=NARANJA, bold=True)
    s.save("01_asm_parcial.svg")


# ------------------------------------------------------------------ figura: grafo del profesor (raiz) decodificado
def fig_grafo_raiz():
    s = SVG(780, 640)
    s.text(390, 22, "Ejemplo de clase (raíz): grafo original con los pesos f/d", 16, bold=True)
    orden = ["|a|", "|b|", "máx1", "−", "máx2", "+", "mín"]
    cx, cy, R = 390, 330, 250
    P = {}
    for i, n in enumerate(orden):
        ang = -math.pi / 2 - math.pi / 7 + i * 2 * math.pi / 7
        P[n] = (cx + R * math.cos(ang), cy + R * math.sin(ang))
    E = [("|a|", "|b|", "inc", None), ("mín", "máx1", "inc", None),
         ("|a|", "máx1", "comp", "1/1"), ("|a|", "máx2", "comp", "1/1"), ("|a|", "mín", "comp", "1/0"),
         ("|a|", "−", "comp", "1/0"), ("|a|", "+", "comp", "0/0"), ("|b|", "mín", "comp", "1/1"), ("|b|", "+", "comp", "1/1"),
         ("|b|", "máx1", "comp", "1/0"), ("|b|", "máx2", "comp", "1/0"), ("|b|", "−", "comp", "0/0"), ("mín", "+", "comp", "1/1"),
         ("mín", "−", "comp", "1/0"), ("mín", "máx2", "comp", "2/0"), ("máx1", "máx2", "comp", "2/1"),
         ("máx1", "+", "comp", "1/0"), ("máx1", "−", "comp", "1/0"), ("+", "−", "comp", "1/0"),
         ("+", "máx2", "comp", "1/0"), ("−", "máx2", "comp", "1/0")]
    idx = {n: i for i, n in enumerate(orden)}
    for a, b, t, p in E:
        d = (idx[b] - idx[a]) % 7
        d = min(d, 7 - d)
        tt = 0.5 if d == 1 else (0.27 if d == 2 else 0.36)
        arista(s, P[a], P[b], p, t, t=tt)
    for k, (x, y) in P.items():
        nodo(s, x, y, k, r=30)
    s.text(390, 610, "Registros del ejemplo: R1={a,t1,x,t7}  R2={b,t2,y,t4,t6}  R3={t3,t5}.  Arcos sin número: 0/0", 12, color=GRIS)
    s.save("02_grafo_raiz_pesos.svg")


# ------------------------------------------------------------------ figura: grafo de operadores del parcial
def fig_grafo_ops():
    s = SVG(900, 560)
    s.text(450, 22, "Parcial: grafo de operadores (paso 1 y 2: nodos + arcos de incompatibilidad + pesos)", 15, bold=True)
    # familia x en pentagono
    cx, cy, R = 220, 250, 140
    M = {}
    nombres = [("M1", "x·x  S1"), ("M2", "t1·x  S2"), ("M3", "a·t1  S3"), ("M4", "b·t3  S4"), ("M5", "y·y  S5")]
    for i, (n, sub) in enumerate(nombres):
        ang = -math.pi / 2 + i * 2 * math.pi / 5
        M[n] = (cx + R * math.cos(ang), cy + R * math.sin(ang))
    pesos_m = {("M1", "M2"): "1/0", ("M1", "M3"): "0/0", ("M1", "M4"): "1/0", ("M1", "M5"): "0/0",
               ("M2", "M3"): "1/0", ("M2", "M4"): "1/0", ("M2", "M5"): "0/0", ("M3", "M4"): "0/0",
               ("M3", "M5"): "0/0", ("M4", "M5"): "0/1"}
    for (a, b), p in pesos_m.items():
        arista(s, M[a], M[b], p, "comp", t=0.5 if (a, b) not in [("M1", "M3"), ("M1", "M4"), ("M2", "M4"), ("M2", "M5"), ("M3", "M5")] else 0.33)
    # familia +
    A = {"A1": (560, 120), "A2": (760, 120), "A3": (560, 330), "A4": (760, 330)}
    pesos_a = {("A1", "A2"): "0/0", ("A1", "A3"): "0/0", ("A1", "A4"): "0/0", ("A2", "A3"): "1/0",
               ("A2", "A4"): "0/0", ("A3", "A4"): "1/1"}
    for (a, b), p in pesos_a.items():
        arista(s, A[a], A[b], p, "comp", t=0.5 if (a, b) not in [("A1", "A4"), ("A2", "A3")] else 0.3)
    D = {"D1": (560, 460), "D2": (760, 460)}
    arista(s, D["D1"], D["D2"], "1/0", "comp")
    # incompatibilidades de mismo estado (ademas de tipo)
    arista(s, M["M1"], A["A1"], None, "inc")
    arista(s, M["M4"], A["A2"], None, "inc")
    arista(s, M["M5"], A["A3"], None, "inc")
    for n, sub in nombres:
        nodo(s, *M[n], n, sub=sub.split()[0] + " " + sub.split()[1])
    subs_a = {"A1": "1+x S1", "A2": "t2+t4 S4", "A3": "t6+t5 S5", "A4": "t8+t7 S6"}
    for n in A:
        nodo(s, *A[n], n, sub=subs_a[n], fill="#fffbea", stroke=NARANJA)
    subs_d = {"D1": ">>1 S7", "D2": ">>1 S8"}
    for n in D:
        nodo(s, *D[n], n, sub=subs_d[n], fill="#eefaf1", stroke=VERDE)
    s.text(220, 420, "familia ×", 14, color=AZUL, bold=True)
    s.text(660, 395, "familia +", 14, color=NARANJA, bold=True)
    s.text(660, 515, "familia >>", 14, color=VERDE, bold=True)
    leyenda_grafo(s, 40, 480)
    s.save("03_grafo_operadores_parcial.svg")


def fig_fusion_mult():
    """Paneles con la fusion de la familia x (el arco verde es el que se une en ese paso)."""
    W = 225
    s = SVG(5 * W + 20, 350)
    s.text((5 * W + 20) / 2, 20, "Pasos 4 a 7 en la familia ×: se une el arco de mayor peso (verde) y los pesos hacia el supernodo se suman", 14, bold=True)
    paneles = [
        ("Inicio: empate en 1/0", "se elige M1–M2", [("M1", (55, 110)), ("M2", (170, 110)), ("M3", (170, 230)), ("M4", (55, 230)), ("M5", (112, 300))],
         [(0, 1, "1/0"), (0, 3, "1/0"), (1, 2, "1/0"), (1, 3, "1/0"), (3, 4, "0/1")], 0),
        ("Tras unir M1 y M2", "SN–M4 = 1/0+1/0 = 2/0", [("SN{M1,M2}", (80, 110)), ("M3", (180, 210)), ("M4", (80, 230)), ("M5", (180, 300))],
         [(0, 1, "1/0"), (0, 2, "2/0"), (2, 3, "0/1")], 1),
        ("Tras unir M4", "SN–M3 = 1/0+0/0 = 1/0", [("SN{M1,M2,M4}", (95, 120)), ("M3", (95, 230)), ("M5", (185, 300))],
         [(0, 1, "1/0"), (0, 2, "0/1")], 0),
        ("Tras unir M3", "SN–M5 = 0/1", [("SN{M1..M4}", (95, 130)), ("M5", (95, 260))],
         [(0, 1, "0/1")], 0),
        ("Resultado", "1 sola unidad", [("UF× = {M1..M5}", (112, 190))], [], None),
    ]
    for k, (tit, sub, nodos, arcos, mejor) in enumerate(paneles):
        ox = 10 + k * W
        s.rect(ox, 35, W - 8, 305, fill="#fafafa", stroke="#ccc", sw=1, rx=6)
        s.text(ox + (W - 8) / 2, 52, tit, 12.5, bold=True)
        s.text(ox + (W - 8) / 2, 70, sub, 11.5, color=VERDE, bold=True)
        for i, (a, b, p) in enumerate(arcos):
            pa = (ox + nodos[a][1][0], nodos[a][1][1]); pb = (ox + nodos[b][1][0], nodos[b][1][1])
            arista(s, pa, pb, p, "grupo" if i == mejor else "comp", t=0.5)
        for n, (x, y) in nodos:
            if n.startswith("SN") or n.startswith("UF"):
                s.ellipse(ox + x, y, 58 if not n.startswith("UF") else 95, 26, fill=AZUL_C)
                s.text(ox + x, y, n, 11.5, color=AZUL, bold=True)
            else:
                nodo(s, ox + x, y, n, r=22)
    s.save("04_fusion_familia_mult.svg")


# ------------------------------------------------------------------ conexiones (datos compartidos por varias figuras)
# lectura: letra -> (fuente, puerto, estados)
LECT = {"A": ("R1", "ML", [5]), "B": ("R2", "ML", [4]), "C": ("R3", "ML", [3]), "D": ("R4", "ML", [1, 2]),
        "E": ("R1", "MR", [5]), "F": ("R4", "MR", [1, 4]), "G": ("R6", "MR", [2, 3]),
        "H": ("R1", "AL", [6]), "I": ("R3", "AL", [4, 5]), "J": ("R4", "AL", [1]),
        "K": ("'1'", "AR", [1]), "L": ("R2", "AR", [5, 6]), "M": ("R5", "AR", [4]), "N": ("R1", "SH", [7, 8])}
# escritura: letra -> (fuente, destino, estados)
ESCR = {"O": ("ADD", "R1", [5, 6]), "P": ("SH", "R1", [7]), "Q": ("MUL", "R2", [4, 5]), "R": ("MUL", "R3", [3]),
        "T": ("ADD", "R3", [4]), "U": ("MUL", "R4", [2]), "V": ("ADD", "R5", [1]), "W": ("MUL", "R6", [1]),
        "Y": ("SH", "SAL", [8])}
BUSC = {"A": "#7b3fbf", "B": "#2f855a", "C": "#2b6cb0", "D": "#dd6b20", "W1": "#b7791f", "W2": "#c53030"}


def fig_conexiones():
    s = SVG(1100, 520)
    s.text(550, 20, "Camino de datos sin buses: cada conexión (letra) es un cable punto a punto", 16, bold=True)
    # panel lectura
    s.text(280, 50, "Parte superior: registro → entrada de unidad", 13, color=AZUL, bold=True)
    izq = ["R1", "R2", "R3", "R4", "R5", "R6", "'1'"]
    der = ["ML", "MR", "AL", "AR", "SH"]
    PI = {n: (110, 90 + i * 52) for i, n in enumerate(izq)}
    PD = {n: (450, 100 + i * 90) for i, n in enumerate(der)}
    tpuerto = {"ML": 0.55, "MR": 0.7, "AL": 0.4, "AR": 0.8, "SH": 0.25}
    for k, (f, d, est) in LECT.items():
        (x1, y1), (x2, y2) = PI[f], PD[d]
        s.line(x1 + 30, y1, x2 - 34, y2, stroke="#888", sw=1.6)
        t = tpuerto[d]
        s.label_box(x1 + 30 + (x2 - x1 - 64) * t, y1 + (y2 - y1) * t, k, size=12, color=ROJO)
    for n, (x, y) in PI.items():
        s.rect(x - 30, y - 15, 60, 30, fill=AZUL_C, stroke=AZUL, rx=4); s.text(x, y, n, 13, color=AZUL, bold=True)
    nombres = {"ML": "× izq", "MR": "× der", "AL": "+ izq", "AR": "+ der", "SH": ">>1"}
    for n, (x, y) in PD.items():
        s.rect(x - 34, y - 15, 68, 30, fill="#fffbea", stroke=NARANJA, rx=4); s.text(x, y, nombres[n], 12.5, bold=True)
    # panel escritura
    s.text(830, 50, "Parte inferior: unidad → registro", 13, color=AZUL, bold=True)
    izq2 = ["MUL", "ADD", "SH"]
    der2 = ["R1", "R2", "R3", "R4", "R5", "R6", "SAL"]
    PI2 = {n: (690, 140 + i * 110) for i, n in enumerate(izq2)}
    PD2 = {n: (1010, 90 + i * 52) for i, n in enumerate(der2)}
    for k, (f, d, est) in ESCR.items():
        (x1, y1), (x2, y2) = PI2[f], PD2[d]
        s.line(x1 + 34, y1, x2 - 30, y2, stroke="#888", sw=1.6)
        t = {"MUL": 0.75, "ADD": 0.5, "SH": 0.35}[f]
        s.label_box(x1 + 34 + (x2 - x1 - 64) * t, y1 + (y2 - y1) * t, k, size=12, color=ROJO)
    nombres2 = {"MUL": "× (MUL)", "ADD": "+ (ADD)", "SH": ">>1 (SH)"}
    for n, (x, y) in PI2.items():
        s.rect(x - 38, y - 15, 76, 30, fill="#fffbea", stroke=NARANJA, rx=4); s.text(x, y, nombres2[n], 12, bold=True)
    for n, (x, y) in PD2.items():
        s.rect(x - 30, y - 15, 60, 30, fill=AZUL_C, stroke=AZUL, rx=4); s.text(x, y, n, 13, color=AZUL, bold=True)
    s.text(550, 505, "Las cargas in1..in4 → R3, R2, R4, R1 (estado S0) se dejan como cables directos (ver sección 5.5).", 12, color=GRIS)
    s.save("05_conexiones_sin_buses.svg")


def _pos_circulo(n, cx, cy, R, i, fase=-math.pi / 2):
    a = fase + i * 2 * math.pi / n
    return cx + R * math.cos(a), cy + R * math.sin(a)


def fig_grafo_buses_lectura():
    s = SVG(1100, 560)
    s.text(550, 20, "Buses de lectura: (1) se unen las conexiones que salen del mismo registro, (2) grafo de supernodos", 15, bold=True)
    # panel 1: 14 conexiones agrupadas por fuente
    grupos = [("R1", ["A", "E", "H", "N"]), ("R2", ["B", "L"]), ("R3", ["C", "I"]), ("R4", ["D", "F", "J"]),
              ("R5", ["M"]), ("R6", ["G"]), ("'1'", ["K"])]
    s.text(270, 50, "Paso 1: misma fuente = mismo dato → nunca chocan", 13, color=AZUL, bold=True)
    y = 80
    for g, letras in grupos:
        w = 60 + 46 * len(letras)
        s.rect(40, y, w, 50, fill="#f7fbff", stroke=AZUL, sw=1.5, rx=25)
        s.text(70, y + 25, g, 13, color=AZUL, bold=True)
        for i, l in enumerate(letras):
            f, d, est = LECT[l]
            nodo(s, 120 + i * 46, y + 25, l, r=19, size=13)
            s.text(120 + i * 46, y + 53, d + " " + ",".join("S%d" % e for e in est), 9, color=GRIS)
        y += 66
    # panel 2: grafo de supernodos
    s.text(790, 50, "Paso 2: supernodos por registro, pesos d = puertos en común", 13, color=AZUL, bold=True)
    orden = ["R1", "R4", "R6", "R2", "R3", "R5", "'1'"]
    P = {n: _pos_circulo(7, 790, 300, 190, i) for i, n in enumerate(orden)}
    comp = {("R1", "R4"): "3", ("R1", "R5"): "0", ("R1", "R6"): "1", ("R1", "'1'"): "0", ("R2", "R6"): "0",
            ("R2", "'1'"): "1", ("R3", "'1'"): "0", ("R5", "R6"): "0", ("R5", "'1'"): "1", ("R6", "'1'"): "0"}
    inc = [("R1", "R2"), ("R1", "R3"), ("R2", "R3"), ("R2", "R4"), ("R2", "R5"), ("R3", "R4"), ("R3", "R5"),
           ("R3", "R6"), ("R4", "R5"), ("R4", "R6"), ("R4", "'1'")]
    for a, b in inc:
        arista(s, P[a], P[b], None, "inc")
    for (a, b), w in comp.items():
        arista(s, P[a], P[b], "d=" + w if w != "0" else None, "grupo" if (a, b) == ("R1", "R4") else "comp", t=0.5)
    for n, (x, y) in P.items():
        nodo(s, x, y, n, r=26, fill="#f7fbff")
    s.text(790, 525, "rojo punteado: los dos registros se leen en un mismo estado (S1, S2, S3, S4, S5 o S6)", 11.5, color=ROJO)
    s.text(790, 545, "verde: primer arco elegido (R1–R4, comparten las entradas ML, MR y AL)", 11.5, color=VERDE)
    s.save("06_grafo_buses_lectura.svg")


def fig_buses_resultado():
    s = SVG(1100, 330)
    s.text(550, 20, "Resultado de la partición: 4 buses de lectura y 2 de escritura", 16, bold=True)
    lect = [("Bus A", ["R2: B, L", "R6: G"]), ("Bus B", ["R3: C, I"]), ("Bus C", ["R1: A, E, H, N", "R4: D, F, J"]), ("Bus D", ["R5: M", "'1': K"])]
    for i, (b, items) in enumerate(lect):
        x = 30 + i * 200
        col = BUSC[b[-1]]
        s.rect(x, 50, 185, 120, fill="white", stroke=col, sw=3, rx=12)
        s.text(x + 92, 70, b, 14, color=col, bold=True)
        for j, it in enumerate(items):
            s.text(x + 92, 100 + j * 24, it, 12.5)
    esc = [("Bus W1", ["MUL: Q, R, U, W"]), ("Bus W2", ["ADD: O, T, V", "SH: P, Y"])]
    for i, (b, items) in enumerate(esc):
        x = 30 + 800 + i * 0
        y = 50 + i * 130
        col = BUSC[b[-2:]]
        s.rect(830, y, 240, 110, fill="white", stroke=col, sw=3, rx=12)
        s.text(950, y + 20, b, 14, color=col, bold=True)
        for j, it in enumerate(items):
            s.text(950, y + 50 + j * 24, it, 12.5)
    s.text(420, 200, "Entradas de cada unidad (MUX):", 13, bold=True)
    filas = ["× izq (ML) ← Bus A, B, C   → MUX 3:1",
             "× der (MR) ← Bus C, A      → MUX 2:1",
             "+ izq (AL) ← Bus C, B      → MUX 2:1",
             "+ der (AR) ← Bus D, A      → MUX 2:1",
             ">>1 (SH)   ← Bus C         → directo"]
    for j, f in enumerate(filas):
        s.text(60, 225 + j * 20, f, 12.5, anchor="start")
    s.text(500, 225, "Sin buses: 4 + 3 + 3 + 3 + 1 = 14 entradas de MUX", 12.5, anchor="start", color=GRIS)
    s.text(500, 247, "Con buses: 3 + 2 + 2 + 2 + 1 = 10 entradas de MUX", 12.5, anchor="start", color=VERDE, bold=True)
    s.save("07_buses_resultado.svg")


def fig_grafo_buses_escritura():
    s = SVG(900, 330)
    s.text(450, 20, "Buses de escritura: grafo de las 9 conexiones unidad → registro", 15, bold=True)
    P = {"Q": (90, 110), "R": (90, 190), "U": (90, 270), "W": (200, 290),
         "O": (430, 110), "T": (430, 190), "V": (430, 270),
         "P": (690, 150), "Y": (690, 250)}
    for a, b in [("V", "W"), ("Q", "T"), ("O", "Q")]:
        arista(s, P[a], P[b], None, "inc")
    s.ellipse(130, 195, 115, 125, fill="none", stroke=BUSC["W1"], sw=3)
    s.text(130, 55, "W1 = salida del ×", 13, color=BUSC["W1"], bold=True)
    s.add(f"<rect x='370' y='60' width='390' height='260' rx='40' fill='none' stroke='{BUSC['W2']}' stroke-width='3'/>")
    s.text(565, 50, "W2 = salida del + y del >>1", 13, color=BUSC["W2"], bold=True)
    arista(s, P["O"], P["P"], "mismo destino R1 (d=1)", "grupo", t=0.5)
    for k, (x, y) in P.items():
        f, d, est = ESCR[k]
        nodo(s, x, y, k, r=22, size=13)
        s.text(x, y + 32, f + "→" + d + " " + ",".join("S%d" % e for e in est), 9.5, color=GRIS)
    s.save("08_grafo_buses_escritura.svg")


def _mux(s, x, y, w, h, txt, n_in=2):
    s.add(f"<polygon points='{x - w / 2},{y} {x + w / 2},{y} {x + w / 2 - 10},{y + h} {x - w / 2 + 10},{y + h}' fill='#fff' stroke='#333' stroke-width='1.5'/>")
    s.text(x, y + h / 2, txt, 10.5, bold=True)


def _tri(s, x, y, color="#333", lab=None, down=True):
    """buffer three-state apuntando hacia abajo, vertice en (x, y+14)"""
    s.add(f"<polygon points='{x - 8},{y} {x + 8},{y} {x},{y + 14}' fill='white' stroke='{color}' stroke-width='1.5'/>")
    if lab:
        s.text(x + 12, y + 6, lab, 9.5, color=GRIS, anchor="start")


def _dot(s, x, y, c="#333"):
    s.add(f"<circle cx='{x}' cy='{y}' r='3.5' fill='{c}'/>")


def fig_cd_buses():
    s = SVG(1120, 700)
    s.text(560, 18, "Camino de datos final con buses (parcial 2)", 16, bold=True)
    # buses de escritura (arriba y abajo, unidos por la derecha)
    yW1t, yW2t, yW1b, yW2b = 48, 66, 640, 660
    s.line(60, yW1t, 1080, yW1t, stroke=BUSC["W1"], sw=4); s.text(40, yW1t, "W1", 12, color=BUSC["W1"], bold=True)
    s.line(60, yW2t, 1100, yW2t, stroke=BUSC["W2"], sw=4); s.text(40, yW2t, "W2", 12, color=BUSC["W2"], bold=True)
    s.line(200, yW1b, 1080, yW1b, stroke=BUSC["W1"], sw=4)
    s.line(600, yW2b, 1100, yW2b, stroke=BUSC["W2"], sw=4)
    s.line(1080, yW1t, 1080, yW1b, stroke=BUSC["W1"], sw=4)
    s.line(1100, yW2t, 1100, yW2b, stroke=BUSC["W2"], sw=4)
    # registros
    RX = {"R1": 120, "R2": 290, "R3": 460, "R4": 630, "R5": 800, "R6": 950}
    cont = {"R1": "y, t7, t9", "R2": "b, t5, t8", "R3": "a, t4, t6", "R4": "x, t3", "R5": "t2", "R6": "t1"}
    entradas = {"R1": ("in4", ["W2"]), "R2": ("in2", ["W1"]), "R3": ("in1", ["W1", "W2"]), "R4": ("in3", ["W1"])}
    yR = 160
    for r, x in RX.items():
        if r in entradas:
            inp, buses = entradas[r]
            n = 1 + len(buses)
            _mux(s, x, 112, 34 + 18 * n, 20, "s" + r[1])
            xs = [x - 8 * (n - 1) + 16 * i for i in range(n)]
            s.line(xs[0], 85, xs[0], 112); s.text(xs[0] - 4, 80, inp, 10.5, anchor="end", color=GRIS)
            for xi, b in zip(xs[1:], buses):
                yb = yW1t if b == "W1" else yW2t
                s.line(xi, yb, xi, 112, stroke=BUSC[b], sw=2); _dot(s, xi, yb, BUSC[b])
            s.line(x, 132, x, yR, arrow=True)
        else:
            b = "W2" if r == "R5" else "W1"
            yb = yW1t if b == "W1" else yW2t
            s.line(x, yb, x, yR, stroke=BUSC[b], sw=2, arrow=True); _dot(s, x, yb, BUSC[b])
        s.rect(x - 48, yR, 96, 40, fill=AZUL_C, stroke=AZUL, sw=2, rx=3)
        s.text(x, yR + 13, r, 13, color=AZUL, bold=True); s.text(x, yR + 29, cont[r], 10.5)
        s.text(x - 54, yR + 20, "LD" + r[1], 9.5, color=GRIS, anchor="end")
    # buses de lectura
    yb = {"A": 260, "B": 285, "C": 310, "D": 335}
    for b, yy in yb.items():
        s.line(60, yy, 1040, yy, stroke=BUSC[b], sw=4); s.text(46, yy, b, 12, color=BUSC[b], bold=True)
    bus_de = {"R1": "C", "R2": "A", "R3": "B", "R4": "C", "R5": "D", "R6": "A"}
    for r, x in RX.items():
        b = bus_de[r]
        s.line(x, yR + 40, x, 222)
        if r == "R3":
            s.line(x, 222, x, yb[b], stroke=BUSC[b], sw=2); s.text(x + 6, 230, "(único en B: sin 3-state)", 9, color=GRIS, anchor="start")
        else:
            _tri(s, x, 222, lab="t" + r[1] + b)
            s.line(x, 236, x, yb[b], stroke=BUSC[b], sw=2)
        _dot(s, x, yb[b], BUSC[b])
    # constante 1
    s.rect(1000, 180, 40, 26, fill="#fff", stroke="#333", rx=3); s.text(1020, 193, "'1'", 12, bold=True)
    s.line(1020, 206, 1020, 222); _tri(s, 1020, 222, lab="t1D"); s.line(1020, 236, 1020, yb["D"], stroke=BUSC["D"], sw=2); _dot(s, 1020, yb["D"], BUSC["D"])
    # muxes de puertos
    yM = 400
    puertos = {"ML": (200, ["A", "B", "C"]), "MR": (380, ["C", "A"]), "AL": (600, ["C", "B"]), "AR": (780, ["D", "A"])}
    for p, (x, bs) in puertos.items():
        n = len(bs)
        _mux(s, x, yM, 30 + 20 * n, 22, p.lower())
        xs = [x - 10 * (n - 1) + 20 * i for i in range(n)]
        for xi, b in zip(xs, bs):
            s.line(xi, yb[b], xi, yM, stroke=BUSC[b], sw=2); _dot(s, xi, yb[b], BUSC[b])
    # unidades
    yU = 470
    s.line(200, yM + 22, 200, yU); s.line(380, yM + 22, 380, yU)
    s.add(f"<polygon points='170,{yU} 410,{yU} 340,{yU + 50} 240,{yU + 50}' fill='#fffbea' stroke='{NARANJA}' stroke-width='2'/>")
    s.text(290, yU + 22, "MULTIPLICADOR ×", 13, bold=True)
    s.line(600, yM + 22, 600, yU); s.line(780, yM + 22, 780, yU)
    s.add(f"<polygon points='570,{yU} 810,{yU} 740,{yU + 50} 640,{yU + 50}' fill='#fffbea' stroke='{NARANJA}' stroke-width='2'/>")
    s.text(690, yU + 22, "SUMADOR +", 13, bold=True)
    # desplazador desde bus C
    s.line(930, yb["C"], 930, yU, stroke=BUSC["C"], sw=2); _dot(s, 930, yb["C"], BUSC["C"])
    s.rect(895, yU, 70, 40, fill="#eefaf1", stroke=VERDE, sw=2, rx=3); s.text(930, yU + 20, ">> 1", 13, bold=True)
    # salidas a buses de escritura
    s.line(290, yU + 50, 290, yW1b, stroke=BUSC["W1"], sw=2); _dot(s, 290, yW1b, BUSC["W1"])
    s.text(296, yU + 75, "MUL (único en W1: sin 3-state)", 9.5, color=GRIS, anchor="start")
    s.line(690, yU + 50, 690, 585); _tri(s, 690, 585, lab="tADD"); s.line(690, 599, 690, yW2b, stroke=BUSC["W2"], sw=2); _dot(s, 690, yW2b, BUSC["W2"])
    s.line(930, yU + 40, 930, 585); _tri(s, 930, 585, lab="tSH"); s.line(930, 599, 930, yW2b, stroke=BUSC["W2"], sw=2); _dot(s, 930, yW2b, BUSC["W2"])
    # salida OUT desde W2
    s.line(1010, yW2b, 1010, 610); _dot(s, 1010, yW2b, BUSC["W2"])
    s.add("<polygon points='1002,610 1018,610 1010,596' fill='white' stroke='#333' stroke-width='1.5'/>")
    s.line(1010, 596, 1010, 560, arrow=True); s.text(1010, 548, "OUT", 12, bold=True); s.text(1024, 604, "h", 10, color=GRIS, anchor="start")
    s.text(560, 690, "Buses de lectura A, B, C, D (registro → unidad) · Buses de escritura W1, W2 (unidad → registro) · triángulos = three-state", 11.5, color=GRIS)
    s.save("09_cd_con_buses.svg")


# ------------------------------------------------------------------ segmentacion
CONJ = [CIAN, ROSA, LILA]


def tabla_tiempos(nombre, titulo, filas, ncols, celdas, sep_despues, colores_fila, nota=None, cw=46):
    """celdas: {(fila, col): (texto, conjunto)}"""
    fw, rh = 120, 24
    W = fw + cw * ncols + 20
    H = 70 + rh * (len(filas) + 1) + (60 if nota else 30)
    s = SVG(W, H)
    s.text(W / 2, 20, titulo, 15, bold=True)
    y0 = 40
    s.rect(10, y0, fw, rh, fill="#ddd", stroke="#999", sw=1)
    s.text(10 + fw / 2, y0 + rh / 2, "Elemento del CD", 11.5, bold=True)
    for c in range(ncols):
        s.rect(10 + fw + c * cw, y0, cw, rh, fill="#ddd", stroke="#999", sw=1)
        s.text(10 + fw + c * cw + cw / 2, y0 + rh / 2, "s%d" % c, 11.5, bold=True)
    for i, f in enumerate(filas):
        y = y0 + rh * (i + 1)
        s.rect(10, y, fw, rh, fill=colores_fila[i], stroke="#999", sw=1)
        s.text(18, y + rh / 2, f, 11.5, anchor="start", bold=True)
        for c in range(ncols):
            t = celdas.get((f, c))
            fill = CONJ[t[1]] if t else "white"
            s.rect(10 + fw + c * cw, y, cw, rh, fill=fill, stroke="#999", sw=1)
            if t:
                s.text(10 + fw + c * cw + cw / 2, y + rh / 2, t[0], 10.5)
    ys = y0 + rh * (sep_despues + 2)
    s.line(10, ys, 10 + fw + cw * ncols, ys, stroke="#000", sw=2.5, dash="6,4")
    yl = y0 + rh * (len(filas) + 1) + 18
    for k, txt in enumerate(["1er conjunto", "2do conjunto", "3er conjunto"]):
        s.rect(20 + k * 150, yl - 8, 18, 16, fill=CONJ[k], stroke="#999", sw=1)
        s.text(44 + k * 150, yl, txt, 11.5, anchor="start")
    if nota:
        s.text(10, yl + 26, nota, 11.5, anchor="start", color=GRIS)
    s.save(nombre)


def fig_tabla_clase():
    filas = ["Leer R1", "Leer R2", "UF-NS", ">>1", ">>3", "Esc R1", "Esc R2",
             "Leer R3", "Leer R4", "Leer R5", "UF-NI", "Esc R3", "Esc R4", "Esc R5", "Salida"]
    col = ["#7fd17f"] * 7 + ["#f6c76b"] * 8
    c = {}
    for k in range(3):
        o = 4 * k
        def put(f, t, txt):
            c[(f, t + o)] = (txt, k)
        put("Leer R1", 2, "b"); put("Leer R1", 3, "t2"); put("Leer R1", 4, "t2")
        put("Leer R2", 1, "a"); put("Leer R2", 3, "t1"); put("Leer R2", 4, "t1")
        put("UF-NS", 1, "|a|"); put("UF-NS", 2, "|b|"); put("UF-NS", 3, "máx"); put("UF-NS", 4, "mín")
        put(">>1", 4, "X"); put(">>3", 3, "X")
        put("Esc R1", 0, "b"); put("Esc R1", 2, "t2"); put("Esc R2", 0, "a"); put("Esc R2", 1, "t1")
        put("Leer R3", 4, "x"); put("Leer R3", 6, "x"); put("Leer R3", 7, "t7")
        put("Leer R4", 4, "t3"); put("Leer R4", 5, "t5"); put("Leer R4", 6, "t6")
        put("Leer R5", 5, "t4")
        put("UF-NI", 4, "−"); put("UF-NI", 5, "+"); put("UF-NI", 6, "máx")
        put("Esc R3", 3, "x"); put("Esc R3", 6, "t7")
        put("Esc R4", 3, "t3"); put("Esc R4", 4, "t5"); put("Esc R4", 5, "t6")
        put("Esc R5", 4, "t4"); put("Salida", 7, "X")
    tabla_tiempos("10_tabla_tiempos_clase.svg", "Tabla de la clase (raíz) completada: 3 conjuntos, uno nuevo cada 4 estados",
                  filas, 16, c, 6, col, nota="Termina en s7, s11 y s15  →  8, 12 y 16 estados (tu hoja: 8 / 12 / 16 frente a 9 / 18 / 27).")


def fig_tabla_parcial():
    filas = ["Leer R1", "Leer R2", "Leer R3", "Leer R4", "Leer R5", "Leer R6", "UF-NS ×", "UF-NS +",
             "Esc R1", "Esc R2", "Esc R3", "Esc R4", "Esc R5", "Esc R6",
             "Leer R7", "Leer R8", "UF-NI +", ">>1", "Esc R7", "Esc R8", "Salida"]
    col = ["#7fd17f"] * 14 + ["#f6c76b"] * 7
    c = {}
    for k in range(3):
        o = 5 * k
        def put(f, t, txt):
            c[(f, t + o)] = (txt, k)
        put("Esc R1", 0, "y"); put("Esc R2", 0, "b"); put("Esc R3", 0, "a"); put("Esc R4", 0, "x")
        put("Leer R4", 1, "x"); put("UF-NS ×", 1, "x·x"); put("Esc R6", 1, "t1")
        put("UF-NS +", 1, "1+x"); put("Esc R5", 1, "t2")
        put("Leer R4", 2, "x"); put("Leer R6", 2, "t1"); put("UF-NS ×", 2, "t1·x"); put("Esc R4", 2, "t3")
        put("Leer R3", 3, "a"); put("Leer R6", 3, "t1"); put("UF-NS ×", 3, "a·t1"); put("Esc R3", 3, "t4")
        put("Leer R2", 4, "b"); put("Leer R4", 4, "t3"); put("UF-NS ×", 4, "b·t3"); put("Esc R2", 4, "t5")
        put("Leer R5", 4, "t2"); put("Leer R3", 4, "t4"); put("UF-NS +", 4, "t2+t4"); put("Esc R3", 4, "t6")
        put("Leer R1", 5, "y"); put("UF-NS ×", 5, "y·y"); put("Esc R8", 5, "t8")
        put("Leer R3", 5, "t6"); put("Leer R2", 5, "t5"); put("UF-NS +", 5, "t6+t5"); put("Esc R7", 5, "t7")
        put("Leer R7", 6, "t7"); put("Leer R8", 6, "t8"); put("UF-NI +", 6, "t8+t7"); put("Esc R7", 6, "t9")
        put("Leer R7", 7, "t9"); put(">>1", 7, "X"); put("Esc R7", 7, "t9")
        put("Leer R7", 8, "t9"); put(">>1", 8, "X"); put("Salida", 8, "out")
    tabla_tiempos("13_tabla_tiempos_parcial.svg", "Parcial 2: análisis de tiempos del CD segmentado (corte S5|S6), 3 conjuntos",
                  filas, 19, c, 13, col, cw=44,
                  nota="Termina en s8, s13 y s18  →  9, 14 y 19 estados (sin segmentar: 9, 18 y 27). Un conjunto nuevo cada 5 estados.")


def fig_mult_segmentado():
    s = SVG(1100, 400)
    s.text(550, 20, "Segmentación de la unidad funcional: el multiplicador en dos etapas", 16, bold=True)
    # antes
    s.text(170, 44, "Antes (1 etapa)", 13, bold=True)
    s.line(140, 70, 140, 110, arrow=True); s.line(200, 70, 200, 110, arrow=True)
    s.text(140, 64, "ML", 11); s.text(200, 64, "MR", 11)
    s.rect(100, 110, 140, 150, fill="#fffbea", stroke=NARANJA, sw=2, rx=4)
    s.text(170, 175, "MULTIPLICADOR", 12.5, bold=True); s.text(170, 195, "retardo t×", 12, color=GRIS)
    s.line(170, 260, 170, 300, arrow=True); s.text(170, 312, "MUL (listo al final del estado)", 11)
    s.text(170, 345, "reloj T ≥ t×", 13, color=ROJO, bold=True)
    # despues
    x0 = 470
    s.text(x0 + 200, 44, "Después (2 etapas)", 13, bold=True)
    s.line(x0 + 130, 70, x0 + 130, 100, arrow=True); s.line(x0 + 270, 70, x0 + 270, 100, arrow=True)
    s.text(x0 + 130, 64, "ML (A)", 11); s.text(x0 + 270, 64, "MR (B)", 11)
    s.rect(x0 + 60, 100, 280, 70, fill="#fffbea", stroke=NARANJA, sw=2, rx=4)
    s.text(x0 + 200, 125, "ETAPA 1: productos parciales de la", 12, bold=True)
    s.text(x0 + 200, 145, "mitad baja de B y su suma  (≈ t×/2)", 12, bold=True)
    regs = [("A", x0 + 100), ("B alta", x0 + 200), ("suma parcial", x0 + 300)]
    for t, x in regs:
        s.line(x, 170, x, 190)
        s.rect(x - 42, 190, 84, 26, fill=CIAN, stroke="#333", sw=1.5)
        s.text(x, 203, t, 11, bold=True)
        s.line(x, 216, x, 236, arrow=True)
    s.text(x0 + 350, 203, "<- registros de segmentación", 11.5, color=AZUL, anchor="start")
    s.rect(x0 + 60, 236, 280, 70, fill="#fffbea", stroke=NARANJA, sw=2, rx=4)
    s.text(x0 + 200, 261, "ETAPA 2: productos parciales de la", 12, bold=True)
    s.text(x0 + 200, 281, "mitad alta y suma final  (≈ t×/2)", 12, bold=True)
    s.line(x0 + 200, 306, x0 + 200, 336, arrow=True); s.text(x0 + 200, 348, "MUL (listo 2 ciclos después de lanzar)", 11)
    s.text(x0 + 200, 378, "reloj T' ≈ T/2 · acepta una multiplicación nueva cada ciclo", 13, color=VERDE, bold=True)
    s.save("11_multiplicador_segmentado.svg")


def fig_reserva_uf():
    s = SVG(1000, 330)
    s.text(500, 18, "Tabla de reserva: multiplicador segmentado (reloj T/2) frente al diseño original (reloj T)", 14.5, bold=True)
    u = 46
    x0 = 130
    # original: 9 estados de 2 unidades
    s.text(20, 60, "Sin segmentar", 12, anchor="start", bold=True)
    orig = ["S0 carga", "S1 x·x, 1+x", "S2 t1·x", "S3 a·t1", "S4 b·t3, t2+t4", "S5 y·y, t6+t5", "S6 t8+t7", "S7 >>1", "S8 >>1, out"]
    for i, t in enumerate(orig):
        s.rect(x0 + i * 2 * u, 46, 2 * u, 30, fill=AZUL_C, stroke=AZUL, sw=1.2)
        s.text(x0 + i * 2 * u + u, 61, t, 9.5)
    s.text(x0 + 18 * u + 8, 61, "= 9 T", 12, anchor="start", bold=True, color=ROJO)
    # segmentado
    filas = ["× etapa 1", "× etapa 2", "sumador +", ">>1"]
    ops = {("× etapa 1", 1): "x·x", ("× etapa 1", 2): "y·y", ("× etapa 1", 3): "t1·x", ("× etapa 1", 4): "a·t1", ("× etapa 1", 5): "b·t3",
           ("× etapa 2", 2): "x·x", ("× etapa 2", 3): "y·y", ("× etapa 2", 4): "t1·x", ("× etapa 2", 5): "a·t1", ("× etapa 2", 6): "b·t3",
           ("sumador +", 1): "1+x", ("sumador +", 6): "t2+t4", ("sumador +", 7): "t6+t5", ("sumador +", 8): "t8+t7",
           (">>1", 9): ">>1", (">>1", 10): "out"}
    colm = {"x·x": "#ffd6a5", "y·y": "#caffbf", "t1·x": "#9bf6ff", "a·t1": "#bdb2ff", "b·t3": "#ffc6ff"}
    yt = 110
    for c in range(11):
        s.rect(x0 + c * u, yt, u, 22, fill="#ddd", stroke="#999", sw=1)
        s.text(x0 + c * u + u / 2, yt + 11, "c%d" % c, 11, bold=True)
    for i, f in enumerate(filas):
        y = yt + 22 + i * 30
        s.text(20, y + 15, f, 12, anchor="start", bold=True)
        for c in range(11):
            t = ops.get((f, c))
            if c == 0 and i == 0:
                t = "carga"
            fill = colm.get(t, "#fff6d6") if t else "white"
            s.rect(x0 + c * u, y, u, 30, fill=fill, stroke="#999", sw=1)
            if t:
                s.text(x0 + c * u + u / 2, y + 15, t, 10.5)
    s.text(x0 + 11 * u + 8, yt + 22 + 60, "= 11 × T/2 = 5,5 T", 12, anchor="start", bold=True, color=VERDE)
    s.text(500, 290, "Cada multiplicación baja en diagonal (etapa 1 en ck, etapa 2 en ck+1); su resultado se puede leer en ck+2.", 12, color=GRIS)
    s.text(500, 310, "y·y (independiente) se lanza en c1+1 = c2 para tapar el hueco mientras se espera t1.", 12, color=GRIS)
    s.save("12_reserva_uf_segmentada.svg")


def fig_cd_segmentado():
    s = SVG(1060, 340)
    s.text(530, 20, "Camino de datos segmentado en dos niveles (corte S5|S6)", 16, bold=True)
    s.rect(40, 50, 540, 230, fill="#effaf0", stroke=VERDE, sw=2.5, rx=10)
    s.text(310, 70, "NIVEL SUPERIOR (S1–S5): un conjunto cada 5 estados", 13, color=VERDE, bold=True)
    regs = ["R1 y", "R2 b,t5", "R3 a,t4,t6", "R4 x,t3", "R5 t2", "R6 t1"]
    for i, r in enumerate(regs):
        s.rect(60 + i * 84, 95, 78, 36, fill=AZUL_C, stroke=AZUL, rx=3); s.text(99 + i * 84, 113, r, 10.5, bold=True)
    s.text(310, 88, "carga: in4 -> R1, in2 -> R2, in1 -> R3, in3 -> R4", 10.5, color=GRIS)
    s.add(f"<polygon points='110,165 270,165 225,205 155,205' fill='#fffbea' stroke='{NARANJA}' stroke-width='2'/>"); s.text(190, 182, "UF-NS ×", 12.5, bold=True)
    s.add(f"<polygon points='330,165 490,165 445,205 375,205' fill='#fffbea' stroke='{NARANJA}' stroke-width='2'/>"); s.text(410, 182, "UF-NS +", 12.5, bold=True)
    s.text(310, 225, "igual que el CD del parcial (MUX en registros y en entradas)", 10.5, color=GRIS)
    # salidas del NS hacia el NI
    s.poly([(190, 205), (190, 265), (625, 265), (625, 66), (865, 66), (865, 90)], stroke=ROJO, sw=2, arrow=True)
    s.poly([(410, 205), (410, 252), (612, 252), (612, 120), (690, 120)], stroke=ROJO, sw=2, arrow=True)
    s.text(470, 245, "t7 (sumador)", 11, color=ROJO, bold=True)
    s.text(300, 276, "t8 (multiplicador)", 11, color=ROJO, bold=True)
    # NI
    s.rect(640, 50, 360, 230, fill="#fff5e6", stroke=NARANJA, sw=2.5, rx=10)
    s.text(820, 40, "NIVEL INFERIOR (S6–S8)", 13, color=NARANJA, bold=True)
    s.rect(690, 90, 100, 40, fill=CIAN, stroke=AZUL, rx=3); s.text(740, 102, "R7 (MUX 3:1)", 11, bold=True); s.text(740, 119, "t7, t9", 10.5)
    s.rect(815, 90, 100, 40, fill=CIAN, stroke=AZUL, rx=3); s.text(865, 102, "R8", 12, bold=True); s.text(865, 119, "t8", 10.5)
    s.add(f"<polygon points='700,175 860,175 815,215 745,215' fill='#fffbea' stroke='{NARANJA}' stroke-width='2'/>"); s.text(780, 192, "UF-NI +", 12.5, bold=True)
    s.rect(890, 175, 70, 40, fill="#eefaf1", stroke=VERDE, sw=2, rx=3); s.text(925, 195, ">>1", 12.5, bold=True)
    s.line(735, 130, 735, 175, arrow=True); s.line(845, 130, 845, 175, arrow=True)
    s.poly([(775, 130), (775, 150), (925, 150), (925, 175)], arrow=True)
    s.poly([(780, 215), (780, 235), (668, 235), (668, 110), (690, 110)], arrow=True)
    s.poly([(925, 215), (925, 248), (656, 248), (656, 100), (690, 100)], arrow=True)
    s.line(960, 195, 1040, 195, arrow=True); s.text(1010, 182, "OUT (h)", 11, bold=True)
    s.text(530, 315, "Hardware: 1 ×, 2 +, 1 >>1 y 8 registros (6 + 2). El nivel inferior no comparte nada con el superior.", 12, color=GRIS)
    s.save("14_cd_segmentado_niveles.svg")


def fig_ganancia():
    s = SVG(900, 360)
    s.text(450, 20, "Ciclos totales para N conjuntos de datos", 16, bold=True)
    datos = [("Sin segmentar", [9, 18, 27], "#a0aec0"), ("Corte S6|S7 (sin HW extra)", [9, 15, 21], "#90cdf4"),
             ("Corte S5|S6 (+1 sumador)", [9, 14, 19], "#68d391"), ("Corte S4|S5 (+1 ×, +1 +)", [9, 13, 17], "#f6ad55")]
    x0, y0, hmax = 90, 300, 240
    s.line(x0, y0, 860, y0); s.line(x0, y0, x0, 40)
    for v in range(0, 31, 5):
        y = y0 - v * hmax / 30
        s.line(x0 - 4, y, x0, y); s.text(x0 - 10, y, str(v), 11, anchor="end")
        s.line(x0, y, 860, y, stroke="#eee", sw=1)
    bw = 36
    for g in range(3):
        gx = x0 + 40 + g * 250
        for k, (nom, vals, col) in enumerate(datos):
            h = vals[g] * hmax / 30
            s.rect(gx + k * (bw + 6), y0 - h, bw, h, fill=col, stroke="#555", sw=1)
            s.text(gx + k * (bw + 6) + bw / 2, y0 - h - 10, str(vals[g]), 11, bold=True)
        s.text(gx + 2 * (bw + 6) - 3, y0 + 18, "N = %d" % (g + 1), 12.5, bold=True)
    for k, (nom, vals, col) in enumerate(datos):
        s.rect(110, 45 + k * 22, 16, 14, fill=col, stroke="#555", sw=1)
        s.text(132, 52 + k * 22, nom, 11.5, anchor="start")
    s.save("15_ganancia_segmentacion.svg")


if __name__ == "__main__":
    fig_asm()
    fig_grafo_raiz()
    fig_grafo_ops()
    fig_fusion_mult()
    fig_conexiones()
    fig_grafo_buses_lectura()
    fig_buses_resultado()
    fig_grafo_buses_escritura()
    fig_cd_buses()
    fig_tabla_clase()
    fig_tabla_parcial()
    fig_mult_segmentado()
    fig_reserva_uf()
    fig_cd_segmentado()
    fig_ganancia()
    print("ok")
