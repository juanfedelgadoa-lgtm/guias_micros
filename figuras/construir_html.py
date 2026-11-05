# -*- coding: utf-8 -*-
"""Convierte parcial2_sintesis_resuelto.md en un HTML autocontenido (figuras SVG embebidas).
Uso: python3 construir_html.py   (requiere el paquete 'markdown')
"""
import base64, os, re
import markdown

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
MD = os.path.join(RAIZ, "parcial2_sintesis_resuelto.md")
HTML = os.path.join(RAIZ, "parcial2_sintesis_resuelto.html")

ESTILO = """body{font-family:Segoe UI,Arial,sans-serif;max-width:1150px;margin:auto;padding:24px;line-height:1.55;color:#222}
pre{background:#f4f4f4;padding:12px;overflow-x:auto;font-size:12.5px;line-height:1.25;border-radius:6px}
code{font-family:Consolas,'DejaVu Sans Mono',monospace;background:#f4f4f4;padding:0 3px;border-radius:3px}
table{border-collapse:collapse;margin:10px 0;font-size:14px}th,td{border:1px solid #bbb;padding:4px 8px}th{background:#e8eef7}
h1{border-bottom:3px solid #345;padding-bottom:4px}h2{border-bottom:1px solid #aaa;margin-top:40px}
blockquote{border-left:4px solid #6a8;margin:0;padding:4px 12px;background:#f3faf5}
img{max-width:100%;height:auto;display:block;margin:14px auto;border:1px solid #e3e3e3;border-radius:6px}"""


def embeber(m):
    alt, ruta = m.group(1), m.group(2)
    with open(os.path.join(RAIZ, ruta), "rb") as f:
        datos = base64.b64encode(f.read()).decode()
    return f'<img alt="{alt}" src="data:image/svg+xml;base64,{datos}">'


def main():
    texto = open(MD, encoding="utf-8").read()
    texto = re.sub(r"!\[([^\]]*)\]\((figuras/[^)]+\.svg)\)", embeber, texto)
    cuerpo = markdown.markdown(texto, extensions=["tables", "fenced_code"])
    with open(HTML, "w", encoding="utf-8") as f:
        f.write('<!doctype html><html lang="es"><head><meta charset="utf-8">'
                "<title>Parcial 2 - Técnicas de síntesis y segmentación</title>"
                f"<style>{ESTILO}</style></head><body>{cuerpo}</body></html>")
    print("escrito", HTML)


if __name__ == "__main__":
    main()
