# guias_micros

Guías de estudio de Análisis y Diseño de Microprocesadores (diseño UC + CD con ASM). Cada guía está en Markdown (se lee en GitHub) y en HTML (se descarga y se abre en el navegador).

| Guía | Contenido |
|---|---|
| [parcial2_sintesis_resuelto.md](parcial2_sintesis_resuelto.md) | **Parcial 2 con todas las técnicas de síntesis**: agrupación de variables, operadores (grafos) y conexiones (buses), segmentación de la unidad funcional y del camino de datos (método de la clase), con figuras |
| [guia_estudio_microprocesadores.md](guia_estudio_microprocesadores.md) | Teoría completa + ejercicios resueltos (incluye el parcial 2 sin síntesis: ASM, CD, palabra de control, UC) |
| [guia_sintesis_segmentacion.md](guia_sintesis_segmentacion.md) | Técnicas de síntesis con el ejemplo de la raíz |
| [segmentacion_paso_a_paso.md](segmentacion_paso_a_paso.md) | Segmentación del CD con el ejemplo de la raíz (ver la corrección al inicio) |

Las figuras están en [`figuras/`](figuras/). Para regenerarlas: `python3 figuras/generar_figuras.py`; para regenerar el HTML del parcial: `python3 figuras/construir_html.py` (requiere el paquete `markdown`).
