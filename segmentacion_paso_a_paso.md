# Cómo hacer segmentación (pipeline) — método del profesor, paso a paso
### Con todas las gráficas y el ejercicio de la raíz desarrollado completo

> Reconstruido a partir de tus apuntes y de las capturas de Numbers ("Segmentación_263"). Se usa el ejercicio que el profesor desarrolla en clase:
>
>   **√(a² + b²) ≈ máx( 0,875·x + 0,5·y , x )**,  x = máx(|a|,|b|),  y = mín(|a|,|b|)
>
> Al final se muestra cómo trasladar el mismo método a otros ejercicios. Sin código, solo diseño.

---

## Índice

1. Qué es segmentar y las dos clases que hay
2. El ejercicio: ASM y de dónde salen las operaciones
3. La idea central: cortar el ASM en niveles
4. Paso 1 — Partir el ASM con la línea de corte
5. Paso 2 — Agrupar variables **dentro de cada nivel**
6. Paso 3 — El camino de datos de cada nivel
7. Paso 4 — La tabla de análisis de tiempos (lo más importante)
8. Paso 5 — Solapar conjuntos de datos (el pipeline en acción)
9. Paso 6 — Calcular la ganancia (% de mejora)
10. La otra segmentación: partir una unidad funcional
11. Receta para cualquier ejercicio
12. Resumen

---

## 1. Qué es segmentar y las dos clases que hay

**Segmentar (pipeline)** = dividir el trabajo en **etapas** separadas por **registros**, para que varios juegos de datos se procesen a la vez, cada uno en una etapa distinta. Como una cadena de montaje: mientras un auto está en pintura, otro ya entró en chasis.

```
   SIN segmentar (un dato a la vez):        CON segmentar (varios a la vez):

   ┌──────────────┐                         ┌────┐ ║ ┌────┐ ║ ┌────┐
   │   TODO el     │                        │ E1 │ ║ │ E2 │ ║ │ E3 │
   │   cálculo     │ ──► OUT                 └────┘ ║ └────┘ ║ └────┘
   └──────────────┘                          reg      reg
     tarda t_total                         cada etapa tarda t_total/3
```

En el curso hay **dos** cosas que se pueden segmentar:

| Qué se segmenta | Qué se parte | Para qué sirve | Dónde en esta guía |
|---|---|---|---|
| **El camino de datos** | todo el algoritmo, en niveles | procesar muchos juegos de datos seguidos | secciones 3–9 (lo principal) |
| **Una unidad funcional** | una sola unidad (p. ej. el sumador) en 2 etapas internas | subir el reloj de esa unidad | sección 10 |

Esta guía se centra en la **del camino de datos**, que es la de tus capturas de Numbers.

---

## 2. El ejercicio: ASM y de dónde salen las operaciones

Pseudoalgoritmo (de tus apuntes):

```
 a = in1, b = in2, FINAL = 0
 si INICIO = 1:
    t1 = |a|           t2 = |b|
    x  = máx(t1,t2)    y  = mín(t1,t2)
    t3 = x >> 3        (x/8)
    t4 = y >> 1        (y/2)
    t5 = x − t3        (0,875·x)
    t6 = t5 + t4       (0,875·x + 0,5·y)
    t7 = máx(t6, x)
    SAL = t7, FINAL = 1
```

ASM (un estado por paso):

```
        ┌─────────────────┐
   ┌───►│ S0 a=in1 b=in2  │◄──────────┐
   │    │    FINAL=0       │           │
   │    └───────┬─────────┘           │
   │     0  ◇ INICIO ◇ 1              │
   └─────────┤      └────┐            │
                        ▼             │
              ┌──────────────────┐    │
              │ S1 t1=|a| t2=|b| │    │   ← NIVEL
              └─────────┬────────┘    │     SUPERIOR
              ┌─────────▼────────┐    │
              │ S2 x=máx(t1,t2)  │    │
              │    y=mín(t1,t2)  │    │
              └─────────┬────────┘    │
              ┌─────────▼────────┐    │
              │ S3 t3=x>>3       │    │
              │    t4=y>>1       │    │
              └─────────┬────────┘    │
        ══════════════════════════════════  ← LÍNEA DE CORTE (roja)
              ┌─────────▼────────┐    │
              │ S4 t5=x−t3       │    │   ← NIVEL
              └─────────┬────────┘    │     INFERIOR
              ┌─────────▼────────┐    │
              │ S5 t6=t5+t4      │    │
              └─────────┬────────┘    │
              ┌─────────▼────────┐    │
              │ S6 t7=máx(t6,x)  │    │
              └─────────┬────────┘    │
              ┌─────────▼────────┐    │
              │ S7 SAL=t7 FINAL=1│────┘
              └──────────────────┘
```

La **línea roja** es la que dibuja el profesor en el ASM: corta el algoritmo en dos mitades.

---

## 3. La idea central: cortar el ASM en niveles

El profesor NO hace 6 etapas pequeñas (una por operación). Hace **2 niveles grandes**:

- **Nivel Superior (NS):** la primera mitad del ASM (hasta la línea roja).
- **Nivel Inferior (NI):** la segunda mitad.

Entre los dos niveles se pone un **registro de frontera** (la línea punteada de la tabla de tiempos). Mientras el nivel inferior termina el juego de datos nº 1, el nivel superior ya empieza el juego nº 2. Eso es el pipeline.

```
                 ┌──────────────┐           ┌──────────────┐
   a,b (juego k)►│ NIVEL         │  ═reg═►   │ NIVEL        │──► SALIDA (juego k)
                 │ SUPERIOR      │ frontera  │ INFERIOR     │
                 │ (S1,S2,S3)    │           │ (S4,S5,S6,S7)│
                 └──────────────┘           └──────────────┘
                   trabaja en el               trabaja en el
                   juego k+1                    juego k
```

**¿Por dónde se corta?** Por un punto donde "pase poca cosa" de un nivel al otro (pocas variables cruzan la frontera) y donde los dos lados queden parecidos de tamaño. En este ejercicio, la línea va **después de t3, t4** (fin de S3). Lo único que necesita el nivel inferior del superior es **x, t3, t4** (y x otra vez para el máx final).

---

## 4. Paso 1 — Partir el ASM con la línea de corte

Lista qué operaciones y qué estados quedan en cada nivel:

| | Estados | Operaciones | Qué recibe del nivel anterior | Qué entrega |
|---|---|---|---|---|
| **Nivel Superior** | S1, S2, S3 | t1=\|a\|, t2=\|b\|, x=máx, y=mín, t3=x>>3, t4=y>>1 | a, b (entradas) | x, t3, t4 |
| **Nivel Inferior** | S4, S5, S6, S7 | t5=x−t3, t6=t5+t4, t7=máx(t6,x), salida | x, t3, t4 | SALIDA |

---

## 5. Paso 2 — Agrupar variables **dentro de cada nivel**

Aquí está el detalle que no es obvio: la agrupación de variables (lado izquierdo) se hace **por separado en cada nivel**, no en todo el algoritmo junto. Es tu hoja de Numbers "SEGMENTACIÓN DEL CD (UNA PARTE) - Agrupación de variables".

### 5.1 Nivel Superior

Tiempos de vida solo dentro del NS (estados s1–s4 de esa hoja):

```
          s1  s2  s3  s4   vida
   b       X   X            2        → R1 (b, t2)
   a       X                1        → R2 (a, t1)
   t1          X   X   X    3
   t2              X   X    2
          ───────────────
  REG      2   2   2   2
```

Máximo = 2 → **2 registros en el nivel superior**:
```
   R1 = { b, t2 }
   R2 = { a, t1 }
```
(En la hoja aparecen más variables como x, y; el principio es el mismo, lo que manda es el máximo de la columna.)

### 5.2 Nivel Inferior

```
          s4  s5  s6  s7  s8   vida
   x       X   X   X   X        4    → R3 (x, t7)
   t3      X   X                2    → R4 (t3, t5, t6)
   t4          X   X            2    → R5 (t4)
   t5              X            1
   t6                  X        1
   t7                      X    1
          ───────────────────
  REG      2   3   3   2   1
```

Máximo = 3 → **3 registros en el nivel inferior**:
```
   R3 = { x, t7 }
   R4 = { t3, t5, t6 }
   R5 = { t4 }
```

**En total: 2 + 3 = 5 registros.** (Un diseño sin segmentar necesitaba 3; aquí hay más porque cada nivel tiene su propio banco, y porque x, t3, t4 deben cruzar la frontera.)

---

## 6. Paso 3 — El camino de datos de cada nivel

Cada nivel es un mini camino de datos con sus registros, sus unidades funcionales y sus MUX. El registro de frontera conecta los dos.

```
 ── NIVEL SUPERIOR ─────────────────────────────────
     in1(a)        in2(b)
       │             │
     ┌─▼──┐        ┌─▼──┐
     │ R2 │        │ R1 │
     │a,t1│        │b,t2│
     └─┬──┘        └─┬──┘
       └──────┬──────┘
          ┌───▼───┐  ┌───────┐
          │ |a||b|│  │máx mín│   (unidades del NS)
          └───┬───┘  └───┬───┘
              └─────┬────┘
            ┌───────▼────────┐  ┌──────┐ ┌──────┐
            │ realim. a R1,R2│  │ >>3  │ │ >>1  │
            └────────────────┘  └──┬───┘ └──┬───┘
                                   │        │
 ══════════════ REGISTRO DE FRONTERA (x, t3, t4) ══════════════
                                   │        │
 ── NIVEL INFERIOR ────────────────▼────────▼──────
     ┌─▼──┐      ┌──▼─┐      ┌──▼─┐
     │ R3 │      │ R4 │      │ R5 │
     │x,t7│      │t3, │      │ t4 │
     │    │      │t5,t6│     │    │
     └─┬──┘      └─┬──┘      └─┬──┘
       └─────┬─────┴─────┬─────┘
          ┌──▼──┐     ┌──▼──┐
          │  −  │     │  +  │   ┌──────┐
          └──┬──┘     └──┬──┘   │ máx  │
             └─────┬─────┴──────┘
                   ▼
                  SALIDA (three-state)
```

---

## 7. Paso 4 — La tabla de análisis de tiempos (lo más importante)

Ésta es tu hoja 4 de Numbers ("Análisis de tiempos - SEGMENTACIÓN el CD"). Es una tabla **ciclo por ciclo**. Cada operación necesita **tres ciclos**:

1. **Leer** el/los registros fuente (Leer Rx).
2. **Ejecutar** en la unidad funcional (UF-NS o UF-NI).
3. **Escribir** el resultado en el registro destino (Esc Rx).

Las filas de tu tabla son exactamente éstas:

```
  Leer R1 / Leer R2      (fuentes del nivel superior)
  UF-NS                  (unidades del nivel superior)
  >>1 , >>3              (desplazadores)
  Esc R1 / Esc R2        (escrituras del nivel superior)
  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─    (línea punteada = frontera entre niveles)
  Leer R3 / Leer R4 / Leer R5   (fuentes del nivel inferior)
  UF-NI                  (unidades del nivel inferior)
  Esc R3 / Esc R4 / Esc R5      (escrituras del nivel inferior)
  Salida
```

### 7.1 Un solo juego de datos (sin solapar todavía)

Columnas = ciclos s0, s1, s2, … Pongo qué hace cada fila en cada ciclo para **el primer juego** (color celeste en tus capturas):

```
 Elemento \ ciclo   s0  s1  s2  s3  s4  s5  s6  s7
 ───────────────────────────────────────────────
 Leer R1                 b   t2
 Leer R2             a   t1
 UF-NS              abs abs máx mín
                    (a) (b)
 >>1                             X
 >>3                         X
 Esc R1              b       t2
 Esc R2             a   t1
 ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
 Leer R3                         x       t7
 Leer R4                         t3  t5
 Leer R5                             t4
 UF-NI                           −   +   máx
 Esc R3                              t7
 Esc R4                          t3  t5  t6
 Esc R5                          t4
 Salida                                      X
```

Lo esencial que se ve:
- Mientras el nivel superior hace sus abs/máx/mín (ciclos s1–s4), el nivel inferior está **vacío** (todavía no tiene datos).
- Cuando el superior termina y cruza la frontera, el inferior arranca (ciclos s4–s7).
- Un juego de datos completo tarda del orden de **8 ciclos** de principio a fin.

### 7.2 Por qué 3 ciclos por operación

```
   ciclo k:     Leer R  →  el dato sale del registro al bus
   ciclo k+1:   UF      →  la unidad calcula
   ciclo k+2:   Esc R   →  el resultado se guarda en el registro destino
```

Por eso la tabla "escalona" cada operación en diagonal.

---

## 8. Paso 5 — Solapar conjuntos de datos (el pipeline en acción)

Aquí ocurre la magia. En cuanto el nivel superior **termina el juego 1 y lo pasa al inferior**, puede empezar el **juego 2**. En tus capturas esto son los colores: **celeste = 1er conjunto, rosa = 2do conjunto**.

```
 Elemento \ ciclo   s0  s1  s2  s3  s4  s5  s6  s7  s8  s9  s10 s11 s12
 ──────────────────────────────────────────────────────────────────
 Leer R1                 b   t2          b   t2             (celeste=1, rosa=2)
 Leer R2             a   t1          a   t1
 UF-NS              aA  aB  máx mín aA  aB  máx
                    (1) (1) (1) (1)(2) (2) (2)
 >>1                             X               X
 >>3                         X                   X
 Esc R1              b       t2          b       t2
 Esc R2             a   t1          a   t1
 ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
 Leer R3                         x       t7  x           x     (1 y 2 solapados)
 Leer R4                         t3  t5      t3  t5  t6
 Leer R5                             t4          t4
 UF-NI                           −   +   máx −   +   máx
 Esc R3                              t7              t7
 Esc R4                          t3  t5  t6  t3  t5  t6
 Esc R5                          t4          t4
 Salida                                      X           X
```

Clave: en el ciclo s4–s5, el nivel **superior ya está procesando el 2do conjunto (rosa)** mientras el **inferior todavía procesa el 1ro (celeste)**. Los dos niveles trabajan a la vez sobre datos distintos. Eso es lo que ahorra tiempo.

---

## 9. Paso 6 — Calcular la ganancia (% de mejora)

Ésta es la tabla final de tus capturas:

| | 1er conjunto | 2do conjunto | 3er conjunto |
|---|---|---|---|
| **Sin segmentación** | 9 | 18 | 27 |
| **Con segmentación** | 8 | 12 | 16 |
| **Diferencia (ciclos ahorrados)** | 1 | 6 | 11 |
| **% Mejora** | 0,11 | 0,33 | 0,41 |

### Cómo se obtiene cada número

**Sin segmentación** (los juegos se hacen uno tras otro, un juego = 9 ciclos):
- 1 juego: 9 · 1 = 9
- 2 juegos: 9 · 2 = 18
- 3 juegos: 9 · 3 = 27

**Con segmentación** (el primer juego cuesta 8; cada juego siguiente solo añade lo que tarda un nivel, porque se solapa con el anterior; aquí ≈ 4 ciclos extra por juego):
- 1 juego: 8
- 2 juegos: 8 + 4 = 12
- 3 juegos: 12 + 4 = 16

**% Mejora = (sin − con) / sin:**
- 1 juego: (9 − 8)/9 = 0,11 (11 %)
- 2 juegos: (18 − 12)/18 = 0,33 (33 %)
- 3 juegos: (27 − 16)/27 = 0,41 (41 %)

```
  Ciclos
   27 ┤                              ● sin segmentar
      │                         ╱
   18 ┤                    ╱●
      │               ╱   ╱         ● con segmentar (16)
   16 ┤          ╱   ╱ ╱─────────●
   12 ┤      ●─╱─╱─●
    9 ┤   ●╱
    8 ┤ ●
      └──┬──────┬──────┬───────► nº de conjuntos
         1      2      3
```

**La conclusión más importante del tema:** la ganancia **crece con el número de datos**. Para 1 solo dato casi no mejora (11 %), porque hay que "llenar" el pipeline; pero para muchos datos la mejora se acerca al ideal. Por eso segmentar sirve cuando hay que procesar **un flujo** de datos, no un cálculo aislado.

Fórmula general: con **k niveles** y **N juegos de datos**, y si cada nivel tarda c ciclos,
```
   Sin segmentar:  N · (k · c)
   Con segmentar:  k · c  +  (N − 1) · c      ← primer juego lleno + los demás uno por nivel
   Ganancia → k    cuando N es muy grande
```

---

## 10. La otra segmentación: partir una unidad funcional

Tu apunte tiene también la pregunta: **"¿cuál es la ganancia al segmentar la unidad funcional en una parte (dos etapas)?"** Esto es distinto de lo anterior: aquí se parte **una sola unidad**, no todo el algoritmo.

```
        A   B
        │   │
     ┌──▼───▼──┐
     │  + / −  │   ← Etapa 1 (la parte lenta: sumador/restador)
     └────┬────┘
        ║reg║      ← registro interno de segmentación
     ┌────▼────┐
     │ MUX máx │   ← Etapa 2 (selección máx/mín/abs)
     │ MUX mín │
     └────┬────┘
          ▼
         SAL
```

- La unidad hacía antes todo de una vez (retardo grande); ahora lo hace en 2 etapas, así que el **reloj puede ir más rápido**.
- Pero una operación tarda **2 ciclos** en salir (latencia). Puede **lanzar una nueva cada ciclo**.
- **Gana solo si hay operaciones independientes** para solapar. En este ejercicio t3 y t4 (los dos desplazamientos) son independientes y se pueden solapar; por eso tu apunte marca con flechas rojas esa zona del ASM.

Diagrama de bloques resultante (tu hoja): la UF segmentada alimenta a los dos desplazadores >>1 y >>3.

```
          A        B
          │        │
      ┌───▼────────▼───┐
      │ UF SEGMENTADA  │  (2 etapas internas)
      └───┬────────┬───┘
       ┌──▼─┐   ┌──▼──┐
       │>>1 │   │ >>3 │
       └────┘   └─────┘
```

| | Segmentar la UF | Segmentar el CD (secciones 3–9) |
|---|---|---|
| Qué se parte | una unidad en 2 etapas | todo el algoritmo en 2 niveles |
| Registros nuevos | 1 interno | un banco por nivel + frontera |
| Para qué | subir el reloj de esa unidad | procesar flujos de datos |
| Ganancia | pequeña si todo es dependiente | crece con el nº de datos |

---

## 11. Receta para cualquier ejercicio

Para segmentar **el camino de datos** de cualquier ASM:

1. **Dibuja el ASM** con un estado por paso.
2. **Traza la línea de corte** por un punto donde crucen pocas variables y los dos lados queden parecidos. Quedan Nivel Superior y Nivel Inferior.
3. **Agrupa variables en cada nivel por separado** (lado izquierdo). Anota qué variables cruzan la frontera → registro de frontera.
4. **Dibuja el mini camino de datos** de cada nivel, unidos por el registro de frontera.
5. **Arma la tabla de tiempos** con filas Leer Rx / UF / Esc Rx (3 ciclos por operación) y una línea punteada en la frontera. Rellena un juego de datos.
6. **Solapa conjuntos**: empieza el 2º juego en el nivel superior en cuanto el 1º cruzó la frontera. Colorea cada conjunto.
7. **Tabla de ganancia**: cuenta ciclos sin segmentar (N · ciclos_por_juego) y con segmentar (primer juego lleno + c por cada juego extra). Calcula % mejora = (sin − con)/sin.

Para segmentar **una unidad funcional**:

1. Elige la unidad lenta. Pártela en 2 etapas con un registro interno.
2. Nuevo reloj = etapa más lenta (de esa unidad) o el de las demás unidades, el que mande.
3. Regla: lanzada en Sk → resultado en Sk+2.
4. Replanifica el ASM lanzando operaciones **independientes** en los huecos.
5. La ganancia es alta solo si hay independencia; si todo está encadenado, es poca.

---

## 12. Resumen

- Segmentar el CD = **cortar el ASM en niveles** con un registro de frontera, agrupar variables **en cada nivel**, y solapar juegos de datos.
- La herramienta de análisis es la **tabla de tiempos ciclo a ciclo** (Leer / UF / Escribir), con colores para cada conjunto.
- Cada operación cuesta **3 ciclos** (leer, ejecutar, escribir).
- La **ganancia crece con el número de datos**: 11 % para 1 juego, 33 % para 2, 41 % para 3… tendiendo al número de niveles.
- Segmentar **una UF** es otra técnica: parte una sola unidad en 2 etapas; solo gana si hay operaciones independientes.

> Resultados numéricos (9/18/27 vs 8/12/16 y 0,11/0,33/0,41) tomados directamente de tus capturas de Numbers. Si quieres, aplico este mismo método completo al ejercicio del **parcial 2** (Out = (y²+eˣ)/4): solo dime por dónde quieres la línea de corte y armo las dos tablas de niveles y la tabla de tiempos con sus colores.
