# Parcial 2 (Realimentación N°2) — Síntesis y segmentación, paso a paso
### Out = (y² + eˣ) / 4, con 1 sumador, 1 multiplicador y 1 desplazador >>1

> Se resuelve con **los mismos métodos de tus apuntes**: agrupación de variables (lado izquierdo), agrupación de operadores (partición de grafos), agrupación de conexiones (buses, partición de grafos) y las dos segmentaciones (unidad funcional y camino de datos). Sin código, solo diseño.

---

## Índice

0. Recordatorio del ASM y notación
1. Grafo de flujo de datos (DFG) — la base de todo
2. Agrupación de variables → registros mínimos (lado izquierdo)
3. Agrupación de operadores → unidades funcionales (grafos)
4. Camino de datos con variables y operadores agrupados
5. Agrupación de conexiones → buses (grafos)
6. Camino de datos final con buses
7. Modelo de retardos (para medir las segmentaciones)
8. Segmentación de la unidad funcional (el multiplicador en 2 etapas)
9. Segmentación del camino de datos (pipeline completo)
10. Resultado final y comparación

---

## 0. Recordatorio del ASM y notación

El algoritmo del enunciado (serie de Taylor de eˣ con a = coef. de x², b = coef. de x³):

```
 S0: a=in1, b=in2, x=in3, y=in4, Final=0   (espera Inicio)
 S1: t1 = x·x          t2 = 1 + x
 S2: t3 = t1·x
 S3: t4 = a·t1
 S4: t5 = b·t3         t6 = t2 + t4
 S5: t8 = y·y          t7 = t6 + t5
 S6: t9 = t8 + t7
 S7: t9 = t9 >> 1
 S8: out = t9 >> 1, Final = 1
```

9 estados (S0–S8), Moore, sin señales de estado. La "÷4" son dos `>>1` seguidos porque el desplazador es de una posición. Esta planificación respeta el recurso: **1 multiplicación, 1 suma y 1 desplazamiento como máximo por estado**.

Operaciones del algoritmo:

| Multiplicaciones (×) | Sumas (+) | Desplazamientos (>>1) |
|---|---|---|
| t1=x·x (S1), t3=t1·x (S2), t4=a·t1 (S3), t5=b·t3 (S4), t8=y·y (S5) | t2=1+x (S1), t6=t2+t4 (S4), t7=t6+t5 (S5), t9=t8+t7 (S6) | S7, S8 |
| **5 multiplicaciones** | **4 sumas** | **2 desplazamientos** |

---

## 1. Grafo de flujo de datos (DFG)

```
    x ──┬──►[× t1]──┬──►[× t3]──►[× t5]──┐
        │  (x·x)    │  (t1·x)   (b·t3)   │
        │           └──►[× t4]──┐        ▼
        │               (a·t1)  ▼      [+ t7]──┐
   "1"──┴──►[+ t2]──────────►[+ t6]──►(t6+t5)  ▼
            (1+x)            (t2+t4)         [+ t9]──►[>>1]──►[>>1]──► out
    y ──────►[× t8]───────────────────────►(t8+t7)
            (y·y)
```

El camino más largo (crítico) es: x·x → t1·x → b·t3 → t7 → t9 → >>1 → >>1. Esto fija el mínimo de estados.

---

## 2. Agrupación de variables → registros mínimos (lado izquierdo)

### 2.1 Definiciones (tus apuntes)

- Estado de **escritura** de una variable = el estado **siguiente** a aquel en que se calcula.
- Estado de **lectura** = donde se usa.
- **Tiempo de vida** = desde el primer estado de escritura hasta el último de lectura, **sin huecos**.

### 2.2 Tabla de tiempos de vida (estados S1–S8)

| Variable | escrita en | leída en | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 |
|---|---|---|---|---|---|---|---|---|---|---|
| y | S0 | S5 | X | X | X | X | X | | | |
| b | S0 | S4 | X | X | X | X | | | | |
| a | S0 | S3 | X | X | X | | | | | |
| x | S0 | S1,S2 | X | X | | | | | | |
| t1 | S1 | S2,S3 | | X | X | | | | | |
| t2 | S1 | S4 | | X | X | X | | | | |
| t3 | S2 | S4 | | | X | X | | | | |
| t4 | S3 | S4 | | | | X | | | | |
| t5 | S4 | S5 | | | | | X | | | |
| t6 | S4 | S5 | | | | | X | | | |
| t7 | S5 | S6 | | | | | | X | | |
| t8 | S5 | S6 | | | | | | X | | |
| t9 | S6 | S7,S8 | | | | | | | X | X |
| **Vivas** | | | **4** | **6** | **6** | **5** | **3** | **2** | **1** | **1** |

**Máximo = 6 → 6 registros.** (Es la "corrección buena" de tu parcial.)

### 2.3 Lado izquierdo

Orden por estado de inicio: y(1–5), b(1–4), a(1–3), x(1–2), t1(2–3), t2(2–4), t3(3–4), t4(4), t5(5), t6(5), t7(6), t8(6), t9(7–8).

| Registro | Se construye así | Variables |
|---|---|---|
| R1 | y(1–5) → t7(6) → t9(7–8) | **{y, t7, t9}** |
| R2 | b(1–4) → t5(5) → t8(6) | **{b, t5, t8}** |
| R3 | a(1–3) → t4(4) → t6(5) | **{a, t4, t6}** |
| R4 | x(1–2) → t3(3–4) | **{x, t3}** |
| R5 | t2(2–4) | **{t2}** |
| R6 | t1(2–3) | **{t1}** |

**6 registros = densidad máxima → óptimo.**

### 2.4 Transferencias por estado (sustituyendo variable → registro)

| Estado | Operación | Transferencia RTL |
|---|---|---|
| S0 | carga | R1←in4, R2←in2, R3←in1, R4←in3 |
| S1 | t1=x·x ; t2=1+x | R6←R4×R4 ; R5←1+R4 |
| S2 | t3=t1·x | R4←R4×R6 |
| S3 | t4=a·t1 | R3←R3×R6 |
| S4 | t5=b·t3 ; t6=t2+t4 | R2←R2×R4 ; R3←R3+R5 |
| S5 | t8=y·y ; t7=t6+t5 | R2←R1×R1 ; R1←R3+R2 |
| S6 | t9=t8+t7 | R1←R1+R2 |
| S7 | t9=t9>>1 | R1←R1>>1 |
| S8 | out=t9>>1,Final=1 | OUT=R1>>1 |

---

## 3. Agrupación de operadores → unidades funcionales (grafos)

Aquí los recursos ya están dados por el enunciado: **1 sumador, 1 multiplicador, 1 desplazador**. Pero el ejercicio sirve para ver el método completo, porque hay que comprobar que con **una sola unidad de cada tipo basta** y asignar cada operación a su unidad.

### 3.1 Paso 1: nodos (una operación por nodo)

```
 Multiplicaciones:  M1=x·x   M2=t1·x   M3=a·t1   M4=b·t3   M5=y·y
 Sumas:             A1=1+x   A2=t2+t4  A3=t6+t5  A4=t8+t7
 Desplazamientos:   D1=(>>1 en S7)   D2=(>>1 en S8)
```

### 3.2 Paso 2: arcos de incompatibilidad (mismo estado)

Dos operaciones del mismo tipo son **incompatibles** (no comparten unidad) si están en el mismo estado:

| Par | Estado común | ¿Incompatible? |
|---|---|---|
| M1 y A1 | S1 | distinto tipo (× vs +), no compiten |
| M4 y A2 | S4 | distinto tipo, no compiten |
| M5 y A3 | S5 | distinto tipo, no compiten |
| cualquier M con cualquier M | — | **nunca coinciden** (1 × por estado) |
| cualquier A con cualquier A | — | **nunca coinciden** (1 + por estado) |
| D1 y D2 | S7, S8 | están en estados distintos → compatibles |

**Resultado del grafo:** las 5 multiplicaciones son todas compatibles entre sí (ninguna comparte estado) → caben en **1 multiplicador**. Las 4 sumas son todas compatibles → **1 sumador**. Los 2 desplazamientos son compatibles → **1 desplazador**.

```
 GRAFO DE MULTIPLICACIONES (todos compatibles → 1 clique → 1 unidad)

     M1 ───── M2
      │  \  /  │
      │   \/   │        no hay ningún arco de incompatibilidad
      │   /\   │        (ninguna comparte estado)
     M5 ───── M3
        \     /
          M4

 → Supernodo {M1,M2,M3,M4,M5} = MULTIPLICADOR

 GRAFO DE SUMAS:  {A1,A2,A3,A4} → 1 clique → SUMADOR
 GRAFO DE DESPL.: {D1,D2}       → 1 clique → DESPLAZADOR
```

Esto **confirma** que los recursos del enunciado (1 ×, 1 +, 1 >>) son suficientes. El mínimo coincide con "máximo de operaciones del mismo tipo en un estado" = 1 para cada tipo.

### 3.3 Paso 3: pesos fuente/destino (para decidir operandos y reducir MUX)

Aunque solo haya una unidad de cada tipo, los pesos sirven para elegir **qué operando va a cada entrada** y así reducir los multiplexores. Para cada entrada de cada unidad, listamos de qué registro lee en cada estado:

**Multiplicador** (se elige el orden de operandos aprovechando que a·b = b·a):

| Entrada | Lee en cada estado | Fuentes distintas | MUX |
|---|---|---|---|
| × izq (ML) | R4(S1), R4(S2), R3(S3), R2(S4), R1(S5) | R4, R3, R2, R1 = 4 | 4:1 |
| × der (MR) | R4(S1), R6(S2), R6(S3), R4(S4), R1(S5) | R4, R6, R1 = 3 | 3:1 |

**Sumador:**

| Entrada | Lee en cada estado | Fuentes distintas | MUX |
|---|---|---|---|
| + izq (AL) | R4(S1), R3(S4), R3(S5), R1(S6) | R4, R3, R1 = 3 | 3:1 |
| + der (AR) | "1"(S1), R5(S4), R2(S5), R2(S6) | "1", R5, R2 = 3 | 3:1 |

**Desplazador:** siempre lee R1 → cable directo, sin MUX.

### 3.4 Destinos (MUX a la entrada de cada registro)

| Registro | Recibe de (estado) | Fuentes | MUX |
|---|---|---|---|
| R1 | in4(S0), ADD(S5), ADD(S6), SHR(S7) | in4, ADD, SHR = 3 | 3:1 |
| R2 | in2(S0), MUL(S4), MUL(S5) | in2, MUL = 2 | 2:1 |
| R3 | in1(S0), MUL(S3), ADD(S4) | in1, MUL, ADD = 3 | 3:1 |
| R4 | in3(S0), MUL(S2) | in3, MUL = 2 | 2:1 |
| R5 | ADD(S1) | ADD = 1 | directo |
| R6 | MUL(S1) | MUL = 1 | directo |

---

## 4. Camino de datos con variables y operadores agrupados

```
   in4 ADD SHR     in2 MUL      in1 MUL ADD      in3 MUL      ADD       MUL
    │   │   │       │   │        │   │   │        │   │        │         │
   ┌┴───┴───┴┐     ┌┴───┴┐      ┌┴───┴───┴┐      ┌┴───┴┐    ┌──┴─┐   ┌───┴┐
 s1│ MUX R1  │  s2 │MUXR2│   s3 │ MUX R3  │  s4  │MUXR4│    │ R5 │   │ R6 │
   │00 01 10 │     │0  1 │      │00 01 10 │      │0  1 │    │(t2)│   │(t1)│
   └────┬────┘     └──┬──┘      └────┬────┘      └──┬──┘    └──┬─┘   └──┬─┘
     ┌──┴─┐        ┌──┴─┐        ┌───┴┐          ┌──┴─┐       │        │
     │ R1 │        │ R2 │        │ R3 │          │ R4 │       │        │
     │y,t7│        │b,t5│        │a,t4│          │x,t3│       │        │
     │ t9 │        │ t8 │        │ t6 │          │    │       │        │
     └──┬─┘        └──┬─┘        └──┬─┘          └──┬─┘       │        │
        └─────┬───────┴──────┬──────┴───────┬───────┴─────────┴────────┘
              ▼              ▼               ▼          (buses de lectura R1..R6, "1")
        ┌───────────┐   ┌───────────┐
    ml► │  MUX ML   │   │  MUX AL   │ ◄al    (entradas del + )
    mr► │  MUX MR   │   │  MUX AR   │ ◄ar
        └─────┬─────┘   └─────┬─────┘
           ┌──┴──┐         ┌──┴──┐
           │  ×  │──►MUL    │  +  │──►ADD
           └─────┘         └─────┘
              (R1)──►┌──────┐──►SHR
                     │ >>1  │──►──┤▷├──► OUT
                     └──────┘      ▲ h
```

- MUX de registros: R1 (3:1), R2 (2:1), R3 (3:1), R4 (2:1), R5 y R6 directos.
- MUX de unidades: ML (4:1), MR (3:1), AL (3:1), AR (3:1 con la constante "1").
- Desplazador directo desde R1; three-state a la salida.
- **0 señales de estado** (no hay decisiones sobre datos).

Hasta aquí es el diseño que te pedían en el parcial (puntos 1–3). Lo que sigue es la **síntesis extra**: buses y segmentación.

---

## 5. Agrupación de conexiones → buses (grafos)

### 5.1 Qué son los nodos

Cada **lectura de un registro** es una conexión. Agrupamos conexiones que **nunca se usan en el mismo estado** en un mismo bus (acceso por three-state).

### 5.2 Tabla de conexiones de lectura (estados S1–S6; el desplazador lee R1 por cable aparte)

| Fuente (lee) | S1 | S2 | S3 | S4 | S5 | S6 |
|---|---|---|---|---|---|---|
| R1 (y, t7) | | | | | X | X |
| R2 (b, t5) | | | | X | X | X |
| R3 (a, t4) | | | X | X | X | |
| R4 (x, t3) | X | X | | X | | |
| R5 (t2) | | | | X | | |
| R6 (t1) | | X | X | | | |
| "1" | X | | | | | |
| **Fuentes activas** | 2 | 2 | 2 | **4** | 3 | 2 |

**Mínimo de buses de lectura = 4** (estado S4 lee R2, R3, R4, R5 a la vez).

### 5.3 Arcos de incompatibilidad (misma columna)

| Estado | Fuentes que coinciden → incompatibles entre sí |
|---|---|
| S1 | R4, "1" |
| S2 | R4, R6 |
| S3 | R3, R6 |
| S4 | R2, R3, R4, R5 (todos entre sí) |
| S5 | R1, R2, R3 (todos entre sí) |
| S6 | R1, R2 |

### 5.4 Grafo de conflicto y asignación

R2, R3, R4, R5 forman un grupo mutuamente incompatible (S4) → cada uno necesita su propio bus → 4 buses como mínimo, ya lo sabíamos. Repartimos R1, R6 y "1" en esos 4 buses buscando compatibilidad:

```
 Grafo de conflicto (línea = incompatibles):

        "1"───R4───R6
               │ \  │
              R5  R2─R3
                   │  │
                  R1──┘

 Asignación (colorear con 4 colores):
   BUS A = { R4, R1 }      (R4 y R1 nunca coinciden: R4 en S1,S2,S4; R1 en S5,S6)
   BUS B = { R2, R6, "1" } (no coinciden: "1" en S1, R6 en S2–S3, R2 en S4–S6)
   BUS C = { R3 }
   BUS D = { R5 }
```

Comprobación del bus A: R4 activa en S1, S2, S4; R1 activa en S5, S6 → no se pisan ✓.
Comprobación del bus B: "1" en S1, R6 en S2–S3, R2 en S4–S6 → no se pisan ✓.

### 5.5 Buses de escritura

Resultados por estado: S1 (×,+), S2 (×), S3 (×), S4 (×,+), S5 (×,+), S6 (+), S7 (>>), S8 (>>).
Máximo 2 a la vez (×y+) → **2 buses de escritura**:
- **BUS W1** = salida del multiplicador.
- **BUS W2** = salida del sumador **o** del desplazador (nunca escriben el mismo estado), cada uno con su three-state.

### 5.6 Resultado

**4 buses de lectura + 2 de escritura = 6 buses**, en lugar de las ~13 conexiones punto a punto. Cada registro y cada unidad accede con three-state.

---

## 6. Camino de datos final con buses

```
   in4          in2          in1          in3
    │            │            │            │
  ┌─▼──┐       ┌─▼──┐       ┌─▼──┐       ┌─▼──┐
  │ R1 │       │ R2 │       │ R3 │       │ R4 │   R5(t2)   R6(t1)
  └─┬┬─┘       └─┬┬─┘       └─┬┬─┘       └─┬┬─┘    │ │       │ │
    ││           ││           ││           ││      │ │       │ │
 ═══╪╪═══════════╪╪═══════════╪╪═══════════╪╪══════╪═╪═══════╪═╪═ BUS A {R4,R1}
 ═══╪╪═══════════╪╪═══════════╪╪═══════════╪╪══════╪═╪═══════╪═╪═ BUS B {R2,R6,"1"}
 ═══╪╪═══════════╪╪═══════════╪╪═══════════╪╪══════╪═╪═══════╪═╪═ BUS C {R3}
 ═══╪╪═══════════╪╪═══════════╪╪═══════════╪╪══════╪═╪═══════╪═╪═ BUS D {R5}
    ▷▷ (three-states de lectura de cada registro hacia su bus)
    │            │            │
  ┌─▼────────────▼─┐        ┌─▼──────┐
  │  MULTIPLICADOR │        │ SUMADOR│      ┌────────┐
  │  (ML←A/C, MR←  │        │(AL←A/C,│      │  >>1   │◄─ R1 (cable)
  │   A/B)         │        │ AR←B/D)│      └───┬────┘
  └───────┬────────┘        └───┬────┘          │
 ═════════╪═════════════════════╪═══════════════╪══ BUS W1 (resultado ×)
 ═════════╪═════════════════════╪═══════════════╪══ BUS W2 (resultado + / >>)
          ▷ (three-states de escritura)         ▷
          └──────────► a los MUX de R1..R6       └──► OUT (three-state h)
```

Palabra de control: selectores de los buses de lectura de cada registro, selectores de entrada de cada unidad (qué bus), habilitadores de escritura de cada bus, LD de cada registro, `h`. Una fila por estado (misma lógica que ya hiciste en el parcial).

---

## 7. Modelo de retardos (para medir las segmentaciones)

En el examen te dan los números; aquí uso estos para poder calcular (proporciones realistas):

| Elemento | Retardo |
|---|---|
| Registro (clk→Q + setup) | 2 ns |
| ROM de salida de la UC | 3 ns |
| MUX / three-state (un nivel) | 1 ns |
| Multiplicador | 16 ns |
| Sumador | 8 ns |
| Desplazador >>1 | 1 ns |

**Periodo base.** Camino de un estado Moore = clk→Q(1) + ROM(3) + MUX(1) + unidad + MUX(1) + setup(1) = **7 + t_unidad**.
- Multiplicador: 7 + 16 = **23 ns** ← camino crítico.
- Sumador: 7 + 8 = 15 ns. Desplazador: 7 + 1 = 8 ns.

**Tiempo por resultado (base):** 9 estados × 23 ns = **207 ns**.

---

## 8. Segmentación de la unidad funcional (el multiplicador en 2 etapas)

### 8.1 Por qué el multiplicador

El multiplicador es la unidad lenta (16 ns) y fija el reloj. Lo partimos en **2 etapas** con un registro interno:

```
       ML   MR
        │   │
     ┌──▼───▼──┐
     │ Etapa 1 │  8 ns     ← primera mitad del producto
     └────┬────┘
        ║reg║              ← registro de segmentación (interno)
     ┌────▼────┐
     │ Etapa 2 │  8 ns     ← segunda mitad
     └────┬────┘
          ▼
         MUL
```

### 8.2 Nuevo reloj

- Etapa 1 del ×: clk→Q(1) + ROM(3) + MUX(1) + 8 + setup(1) = 14 ns
- Etapa 2 del ×: clk→Q(1) + 8 + MUX(1) + setup(1) = 11 ns
- Sumador (completo, sin segmentar): 7 + 8 = **15 ns** ← ahora manda el sumador

**T = 15 ns** (antes 23).

### 8.3 Regla de temporización

> Una multiplicación **lanzada** en Sk entrega su resultado al final de Sk+1; se puede **usar a partir de Sk+2**.

Por eso en cada estado hay que mirar **dos cosas**: qué multiplicación se lanza (entradas del ×) y qué multiplicación termina (su resultado va a un registro).

### 8.4 Replanificación (rellenar las 2 etapas con multiplicaciones independientes)

La única multiplicación independiente de la cadena es **y·y**. La lanzamos temprano para que la etapa 2 no quede vacía:

| Estado | Lanza en × | Termina (se guarda) | Sumador | Desplazador |
|---|---|---|---|---|
| S1 | t1 = x·x | — | t2 = 1+x | — |
| S2 | t8 = y·y | t1 | — | — |
| S3 | t3 = t1·x | t8 | — | — |
| S4 | t4 = a·t1 | t3 | — | — |
| S5 | t5 = b·t3 | t4 | — | — |
| S6 | — | t5 | t6 = t2+t4 | — |
| S7 | — | — | t7 = t6+t5 | — |
| S8 | — | — | t9 = t8+t7 | — |
| S9 | — | — | — | t9 = t9>>1 |
| S10 | — | — | — | out = t9>>1 |

Comprobación de dependencias (lanzada en Sk → disponible en Sk+2):
- t3 (S3) usa t1, lanzado en S1 → disponible S3 ✓
- t4 (S4) usa t1 (S1) → ✓
- t5 (S5) usa t3, lanzado en S3 → disponible S5 ✓
- t6 (S6) usa t4 (lanzado S4 → disp. S6) ✓
- t7 (S7) usa t5 (lanzado S5 → disp. S7) ✓
- t9 (S8) usa t8 (lanzado S2 → disp. S4, de sobra) ✓

### 8.5 Diagrama de tiempos (reservas de cada unidad)

```
 Ciclo:        S1   S2   S3   S4   S5   S6   S7   S8   S9  S10
 × etapa 1:    t1   t8   t3   t4   t5    ·    ·    ·    ·   ·
 × etapa 2:    ·    t1   t8   t3   t4   t5    ·    ·    ·   ·
 Sumador:      t2   ·    ·    ·    ·    t6   t7   t9    ·   ·
 Desplazador:  ·    ·    ·    ·    ·    ·    ·    ·   >>1  >>1→out
```

Una multiplicación avanza en diagonal (etapa 1 → etapa 2). El multiplicador acepta una nueva cada ciclo.

### 8.6 Resultado de segmentar la UF

- Estados: S0 + 10 = **11 ciclos**.
- Tiempo: 11 × 15 ns = **165 ns** (base 207 ns). **Ganancia 1,25×.**
- Registros: al replanificar, el máximo de variables vivas baja a **5** (el registro interno del × guarda un valor "en vuelo"). Un registro menos en el CD.

> Conclusión honesta (como en tus apuntes): la ganancia es modesta porque el algoritmo es muy **encadenado** (una multiplicación depende de la anterior). Solo y·y es independiente y rellena un hueco. Segmentar la UF ayuda poco cuando casi todo está en serie.

---

## 9. Segmentación del camino de datos (pipeline completo)

Esto tiene sentido si hay que calcular la ecuación para **muchos juegos de datos** (a,b,x,y) seguidos y se busca productividad (un resultado por ciclo), no un cálculo rápido aislado.

### 9.1 Niveles del DFG (planificación ASAP, sin límite de recursos)

| Nivel | Operaciones | Retardo |
|---|---|---|
| N1 | t1=x·x, t2=1+x, t8=y·y | 16 (×) |
| N2 | t3=t1·x, t4=a·t1 | 16 |
| N3 | t5=b·t3, t6=t2+t4 | 16 |
| N4 | t7=t6+t5 | 8 |
| N5 | t9=t8+t7 | 8 |
| N6 | >>1, >>1 | 2 |

### 9.2 Balanceo

Cada etapa de pipeline cuesta: retardo lógico + 2 ns de registro (sin ROM ni MUX, porque cada unidad tiene conexión fija).

| Opción | Etapas | Etapa más lenta | T |
|---|---|---|---|
| 5 etapas: {N1}{N2}{N3}{N4}{N5,N6} | 5 | 16+2 = 18 | **18 ns** |

Las etapas de multiplicación (16 ns) mandan; partir más no ayuda sin segmentar el propio multiplicador.

### 9.3 Esquema del CD segmentado

```
         ┌──── E1 ────┐   ┌─ E2 ─┐   ┌─ E3 ─┐   ┌─ E4 ─┐   ┌──── E5 ────┐
 a ─►║   │ t1 = x·x   │ ║ │t3=t1·x│ ║│t5=b·t3│ ║│t7=   │ ║ │ t9=t8+t7   │ ║─► out
 b ─►║   │ t2 = 1+x   │ ║ │t4=a·t1│ ║│t6=t2+t4│║│t6+t5 │ ║ │ >>1  >>1   │ ║
 x ─►║   │ t8 = y·y   │ ║ │       │ ║│       │ ║│      │ ║ │            │ ║
 y ─►║   │ (2×, 1+)   │ ║ │(2×)   │ ║│(1×,1+)│ ║│(1+)  │ ║ │ (1+, 2>>)  │ ║
     reg entrada     reg E1/E2   reg E2/E3  reg E3/E4  reg E4/E5    reg salida
```

### 9.4 Registros de segmentación (lo que cruza cada frontera, incluidos los que solo "pasan")

| Registro | Guarda | Comentario |
|---|---|---|
| Entrada | a, b, x, y | 4 |
| E1/E2 | t1, t2, t8, x, a, b | t2, t8, b solo pasan |
| E2/E3 | t3, t4, t2, t8 | t8 solo pasa |
| E3/E4 | t5, t6, t8 | t8 solo pasa |
| E4/E5 | t7, t8 | |
| Salida | out | |

El dato t8 viaja por 3 fronteras hasta que se usa en E5: ése es el **costo oculto** de segmentar (hay que retrasar los datos para que lleguen junto con su mismo juego).

### 9.5 Hardware y métricas

- Hardware: **5 multiplicadores, 4 sumadores, 2 desplazadores** y ~20 registros de segmentación. Ya **no se comparte**: cada operación tiene su unidad.
- Latencia (un resultado): 5 × 18 = **90 ns**.
- Productividad: **1 resultado cada 18 ns** (una vez lleno el pipeline).
- Para N juegos de datos: (5 + N − 1) × 18 ns.
  - N = 1000 → 1004 × 18 = 18 072 ns, frente a 1000 × 207 = 207 000 ns del diseño base → ~11× más rápido para flujos largos.
- Ganancia de **la segmentación en sí** (contra el mismo hardware sin registros, que tardaría 16+16+16+8+2 ≈ 58 ns + 2 = 60 ns por resultado): 60 / 18 ≈ **3,3×** (la ideal con 5 etapas sería 5; se pierde por el desbalance, las etapas de suma usan 8 de 16 ns).

---

## 10. Resultado final y comparación

| Diseño | Periodo T | Ciclos | Tiempo / resultado | Hardware | Registros |
|---|---|---|---|---|---|
| **Base (parcial)** | 23 ns | 9 | **207 ns** | 1×, 1+, 1>> | 6 |
| **+ buses** | 23 ns | 9 | 207 ns (igual tiempo, menos cables) | 1×, 1+, 1>> | 6 |
| **UF segmentada** (× en 2 etapas) | 15 ns | 11 | **165 ns** | × con reg. interno | 5 |
| **CD segmentado** (5 etapas) | 18 ns | 1 por resultado | **18 ns/dato** (flujo) | 5×, 4+, 2>> | ~20 |

### Lo que hay que saber responder

1. **Agrupar variables** (lado izquierdo) → 6 registros. Es lo que pedía el parcial.
2. **Agrupar operadores** (grafos) → confirma que 1 ×, 1 + y 1 >> bastan; los pesos fuente/destino dicen cómo elegir operandos para achicar los MUX.
3. **Agrupar conexiones** (grafos) → 4 buses de lectura + 2 de escritura.
4. **Segmentar la UF**: partir el multiplicador en 2 etapas, replanificar lanzando y·y en el hueco → 165 ns, 5 registros. Ganancia modesta por ser un algoritmo encadenado.
5. **Segmentar el CD**: 5 etapas por niveles, un resultado por ciclo → ideal para procesar muchos datos; ganancia ≈ número de etapas.

### Reglas que se repiten (las tres agrupaciones son el mismo método)

- Registros mínimos = **máx. variables vivas en un estado**.
- Unidades mínimas de un tipo = **máx. operaciones de ese tipo en un estado**.
- Buses mínimos = **máx. conexiones activas en un estado**.
- Segmentar = cambiar latencia por productividad; la ganancia la limita la **etapa más lenta** y las **dependencias**.

---

> Los retardos de las secciones 7–9 son de ejemplo para poder dar números; en tu examen usa los que te den. Si quieres, puedo añadir la **palabra de control completa** (tabla por estado) de cualquiera de las versiones segmentadas, o el **grafo de operadores/conexiones dibujado con los pesos f/d** si me confirmas los valores que usa tu profesor.
