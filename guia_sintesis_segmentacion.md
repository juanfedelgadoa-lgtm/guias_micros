# Técnicas de síntesis y segmentación (según los apuntes del profesor)
### Agrupación de variables, de operadores y de conexiones · Segmentación de la UF y del camino de datos

> Esta guía sigue **el mismo ejercicio y los mismos métodos de tus apuntes** (el del cálculo aproximado de la raíz). Reemplaza la versión anterior, que usaba otro ejercicio y un modelo de retardos inventado.
> Ejercicio base:
>
>   **√(a² + b²) ≈ máx( 0,875·x + 0,5·y , x )**,  con  x = máx(|a|, |b|),  y = mín(|a|, |b|)
>
> y como 0,875·x = x − x/8 y 0,5·y = y/2, todo se hace con restas, sumas, máx, mín y desplazamientos (sin multiplicador). Nada de código, solo diseño.

---

## Índice

1. Qué es la síntesis de un ASM (el mapa completo)
2. El ejercicio base: pseudoalgoritmo, ASM y caja negra
3. Agrupación de **variables** (lado izquierdo) → reduce registros
4. Agrupación de **operadores** (partición de grafos) → reduce unidades funcionales
5. El camino de datos con variables y operadores agrupados
6. Agrupación de **conexiones** (buses, otra vez grafos) → reduce cables
7. El camino de datos con buses
8. Segmentación: idea y métrica
9. Segmentación de la **unidad funcional**
10. Segmentación del **camino de datos**
11. Encadenamiento y multiciclo
12. Resumen y método de examen

---

## 1. Qué es la síntesis de un ASM (el mapa completo)

De tus apuntes (hoja "Síntesis de ASM"):

> **Síntesis** = procedimientos que buscan **optimizar la implementación hardware** del camino de datos y de la unidad de control.

Se divide en dos familias:

```
                         SÍNTESIS DE ASM
          ┌──────────────────────┴───────────────────────┐
   OPTIMIZAR RECURSOS (hardware)              OPTIMIZAR TIEMPO (procesamiento)
   ┌──────────┼───────────────┐              ┌───────────┼────────────┐
 Elementos   Unidades      Conexiones     Pipeline    Encadena-    Multiciclo
   de almac.  funcionales   (buses)       (segmen-     miento
 (registros) (operadores)                  tación)
   │             │              │
 Lado        Partición      Partición
 izquierdo   de grafos      de grafos
```

| Familia | Qué reduce | Técnica | Herramienta |
|---|---|---|---|
| Recursos: almacenamiento | número de **registros** | agrupación de variables | tabla de tiempos de vida + **lado izquierdo** |
| Recursos: operadores | número de **unidades funcionales** | agrupación de operadores | **partición de grafos** |
| Recursos: conexiones | número de **cables / buses** | agrupación de conexiones | **partición de grafos** (tabla de conexiones) |
| Tiempo | periodo de reloj / ciclos | **pipeline**, encadenamiento, multiciclo | planificación por etapas |

Las tres técnicas de recursos usan la misma idea: **dos cosas pueden compartir un recurso si nunca se usan en el mismo estado**. Los registros se agrupan con el lado izquierdo (porque sus "vidas" son intervalos); los operadores y las conexiones se agrupan con grafos (porque sus incompatibilidades no son intervalos limpios).

---

## 2. El ejercicio base: pseudoalgoritmo, ASM y caja negra

### 2.1 Enunciado

Implementar **√(a² + b²) ≈ máx( 0,875·x + 0,5·y , x )** con a, b enteros, donde x = máx(|a|, |b|), y = mín(|a|, |b|).

### 2.2 Pseudoalgoritmo (de tus apuntes)

```
 a = in1, b = in2, FINAL = 0
 si INICIO = 1:
    t1 = |a|            t2 = |b|
    x  = máx(t1, t2)    y  = mín(t1, t2)
    t3 = x >> 3         t4 = y >> 1       (x/8 y y/2)
    t5 = x − t3         (0,875·x)
    t6 = t5 + t4        (0,875·x + 0,5·y)
    t7 = máx(t6, x)
    SAL = t7,  FINAL = 1
```

### 2.3 Diagrama ASM (un estado por línea)

```
        ┌────────────────────┐
   ┌───►│ S0  FINAL=0         │◄──────────┐
   │    │     a=in1 ; b=in2   │           │
   │    └─────────┬───────────┘           │
   │       0  ◇ INICIO ◇ 1                │
   └───────────┤       └──────┐           │
                             ▼            │
                 ┌───────────────────┐    │
                 │ S1  t1=|a| ; t2=|b|│   │
                 └─────────┬─────────┘    │
                 ┌─────────▼─────────┐    │
                 │ S2  x=máx(t1,t2)  │    │
                 │     y=mín(t1,t2)  │    │
                 └─────────┬─────────┘    │
                 ┌─────────▼─────────┐    │
                 │ S3  t3=x>>3       │    │
                 │     t4=y>>1       │    │
                 └─────────┬─────────┘    │
                 ┌─────────▼─────────┐    │
                 │ S4  t5=x−t3       │    │
                 └─────────┬─────────┘    │
                 ┌─────────▼─────────┐    │
                 │ S5  t6=t5+t4      │    │
                 └─────────┬─────────┘    │
                 ┌─────────▼─────────┐    │
                 │ S6  t7=máx(t6,x)  │    │
                 └─────────┬─────────┘    │
                 ┌─────────▼─────────┐    │
                 │ S7  SAL=t7 ;FINAL=1│───┘
                 └────────────────────┘
```

Moore, 8 estados (S0–S7), sin señales de estado (la única decisión es INICIO).

### 2.4 Caja negra

```
   in1 ─/8─►┌──────────┐
   in2 ─/8─►│          │──/8─► SALIDA
  INICIO ──►│  RAÍZ    │─────► FINAL
   CLK ────►│          │
   RST ────►└──────────┘
```

---

## 3. Agrupación de variables (lado izquierdo) → reduce registros

Esto ya lo dominas; lo repito corto porque es el primero de los tres "agrupamientos" y sirve de modelo para los otros dos.

### 3.1 Definiciones de tus apuntes

- **Estado de escritura**: el estado **siguiente** a aquel en que la variable se asigna (porque el resultado se guarda al final del estado y está disponible en el siguiente).
- **Estado de lectura**: el estado donde la variable se usa.
- **Tiempo de vida**: todos los estados entre el **primer estado de escritura** y el **último de lectura**.

### 3.2 Tabla de tiempos de vida (tu hoja "Ejemplo")

| Var | S1 | S2 | S3 | S4 | S5 | S6 | S7 | Vida |
|---|---|---|---|---|---|---|---|---|
| a (→t1) | X | | | | | | | 1 |
| b (→t2) | X | | | | | | | 1 |
| t1 | | X | | | | | | 1 |
| t2 | | X | | | | | | 1 |
| x | | | X | X | X | X | | 4 |
| y | | | X | | | | | 1 |
| t4 | | | | X | X | | | 2 |
| t3 | | | | X | | | | 1 |
| t5 | | | | | X | | | 1 |
| t6 | | | | | | X | | 1 |
| t7 | | | | | | | X | 1 |
| **Registros vivos** | 2 | 2 | 2 | **3** | **3** | 2 | 1 | |

**Máximo = 3 → 3 registros.** Es el resultado de tu hoja.

### 3.3 Lado izquierdo → asignación

Igual que en tu hoja:

```
 R1 = { a, t1, x, t7 }
 R2 = { b, t2, y, t4, t6 }
 R3 = { t3, t5 }
```

---

## 4. Agrupación de operadores (partición de grafos) → reduce unidades funcionales

Aquí está lo nuevo. En vez de intervalos, se usa un **grafo** porque las operaciones "compatibles" no forman intervalos limpios.

### 4.1 Idea (tu hoja "Agrupación de operadores")

> Reducir el número de unidades funcionales agrupando las operaciones **similares** (aritméticas, lógicas, de desplazamiento), siempre que no coincidan en el mismo estado.

### 4.2 Las operaciones del ejercicio

| Operador | Estado | Tipo |
|---|---|---|
| \|a\| (abs₁) | S1 | valor absoluto |
| \|b\| (abs₂) | S1 | valor absoluto |
| máx₁ = máx(t1,t2) | S2 | máximo |
| mín = mín(t1,t2) | S2 | mínimo |
| >>3 | S3 | desplazamiento |
| >>1 | S3 | desplazamiento |
| − (t5=x−t3) | S4 | resta |
| + (t6=t5+t4) | S5 | suma |
| máx₂ = máx(t6,x) | S6 | máximo |

Son 9 nodos: abs₁, abs₂, máx₁, mín, >>3, >>1, −, +, máx₂.

### 4.3 El algoritmo de partición de grafos (tu hoja, 7 pasos)

1. Genera los **nodos** = las unidades/operaciones.
2. Identifica los **arcos de incompatibilidad**: dos operaciones son incompatibles (NO pueden compartir unidad) si están en el **mismo estado**, o si son de tipos que ninguna unidad común puede hacer.
3. Evalúa los **arcos priorizados** con pesos **fuente/destino**: a dos operaciones compatibles les pones un peso `f/d` donde `f` = cuántas **fuentes** (registros de entrada) comparten y `d` = cuántos **destinos** (registros de salida) comparten. Juntarlas así ahorra multiplexores.
4. Toma el arco de **mayor peso** → crea un **supernodo** uniendo esos dos nodos.
5. Al agrupar: no destruir otros arcos (el supernodo solo conserva arcos hacia nodos compatibles con **todos** sus miembros), el peso del arco nuevo es la **suma**, y se busca el supernodo con **más elementos**.
6. **Actualiza el grafo**.
7. Vuelve al paso 4 mientras se puedan agrupar nodos.

### 4.4 Paso 1–2: nodos y arcos de incompatibilidad

Arco punteado (rojo en tus apuntes) = **incompatibles**. Incompatibles por estar en el mismo estado:
- abs₁ – abs₂ (los dos en S1)
- máx₁ – mín (los dos en S2)
- >>3 – >>1 (los dos en S3)

Todo lo demás es, en principio, compatible (está en estados distintos). Pero además hay que poder hacerlas con **una misma unidad**. Tu solución agrupa por "familias" que una ALU/comparador puede cubrir:

- Una unidad que hace **+ y −** (ALU).
- Una unidad que hace **máx y mín** (un restador + un MUX: compara A−B y escoge).
- **abs** se puede hacer con la misma idea (resta y escoge).
- Los **desplazamientos** >>1 y >>3 pueden ser una unidad o cableado.

### 4.5 Paso 3: pesos fuente/destino

Mira tu "Grafo original" (hoja 11): cada arco lleva una etiqueta tipo `1/0`, `1/1`, `2/1`. Ése es el peso **fuente/destino**:
- `1/1` entre máx₁ y mín: comparten **1 fuente** (ambos leen t1 y t2) y **1 destino** no... (en realidad comparten las dos fuentes; el número exacto depende de cómo cuentes, y por eso en tus apuntes hay varios `1/1`, `1/0`, `2/1`).
- La regla práctica: **más peso = más conviene juntarlas** porque comparten entradas o salidas y ahorran MUX.

### 4.6 Pasos 4–7: agrupar (siguiendo tu secuencia de hojas 11→14)

Tu desarrollo agrupa en este orden y llega a **dos supernodos** (dos unidades funcionales):

```
 Paso 1 (grafo original):   9 nodos con todos sus arcos y pesos.
 Paso 2:  se unen máx₁ y máx₂ → supernodo {máx₁, máx₂}   (misma operación, distinto estado)
 Paso 3:  se une  mín con {|b|, +}  → supernodo {mín, |b|, +}
 Paso 4 (resultado):
      U.F.1 = { máx₁, máx₂, |a| }
      U.F.2 = { mín, |b|, +, − }
```

Es decir, de 9 operaciones se pasa a **2 unidades funcionales**:

| Unidad | Operaciones que hace |
|---|---|
| **U.F.1** | máx₁, máx₂, \|a\| |
| **U.F.2** | mín, \|b\|, +, − |

Más los **desplazadores** >>1 y >>3, que en tu dimensionamiento quedan como unidades aparte (2 desplazadores).

> Cómo se construye cada "unidad multifunción": tu hoja 9 lo dibuja. Un **máx/mín** es un restador A−B cuyo bit de signo controla un MUX que escoge A o B. Un **valor absoluto** es A−B con A=0 y un MUX que escoge el positivo. Una **ALU +/−** es un sumador con un XOR de control en B. Y una unidad que hace `+, −, |·|, máx, mín` es un sumador/restador seguido de dos MUX controlados por bits `c1…c4` (tu último dibujo de la hoja 9).

### 4.7 Dimensionamiento final (tu hoja "Dimensionamiento")

- **Unidades funcionales:** 2 de valor absoluto, 1 máximo, 1 mínimo, 2 desplazadores (>>1 y >>3), 1 restador, 1 sumador — y al agruparlas quedan **U.F.1** y **U.F.2** multifunción + los desplazadores.
- **Almacenamiento:** 3 registros (del paso 3).
- **Multiplexores:** 3 (uno por registro).
- **UC:** ROM entrada 16×3, registro 3 bits, ROM salida 8×11 (u 8×13 según cuántos bits de control salgan).

---

## 5. El camino de datos con variables y operadores agrupados

Éste es tu dibujo "Camino de datos (variables agrupadas)" (hoja 7). Lo transcribo como esquema:

```
          in1                 in2
           │                   │
      ┌────▼────┐         ┌─────▼────┐         ┌─────────┐
  4,5►│ MUX R1  │     1,2►│ MUX R2   │       6►│ MUX R3  │◄─ realim.
    1►│         │       2►│          │       3►│         │
      └────┬────┘         └────┬─────┘         └────┬────┘
        ┌──▼──┐            ┌───▼──┐             ┌───▼──┐
        │ R1  │            │ R2   │             │ R3   │
        │a,t1,│            │b,t2, │             │t3,t5 │
        │x,t7 │            │y,t4, │             │      │
        │     │            │t6    │             │      │
        └──┬──┘            └───┬──┘             └───┬──┘
           └─────────┬─────────┴─────────┬──────────┘
                     ▼ (buses de lectura hacia todas las unidades)
   ┌────┬────┬─────┬─────┬─────┬─────┬─────┬────┬────┐
   │|a| │|b| │ máx │ mín │ >>3 │ >>1 │ máx │ +  │ −  │
   └──┬─┴──┬─┴──┬──┴──┬──┴──┬──┴──┬──┴──┬──┴──┬─┴──┬─┘
      └────┴────┴─────┴─────┴─────┴─────┴─────┴────┘
                     ▼ (resultados de vuelta a los MUX de R1, R2, R3)
               SAL (three-state desde R1)
```

Lo importante: **cada registro tiene un MUX a la entrada** (porque recibe de in, de realimentación y de varias unidades), y **las salidas de las unidades vuelven a los registros**. Todavía NO hay buses; cada conexión es un cable. Eso es lo que optimiza el paso siguiente.

---

## 6. Agrupación de conexiones (buses, otra vez grafos) → reduce cables

### 6.1 Idea (tu hoja "Agrupación de conexiones")

> Reducir el número de **cables** que interconectan las unidades funcionales con los registros:
> - usar **buses** para tener conexiones comunes,
> - el acceso al bus se hace con **three-state**,
> - se resuelve con el **algoritmo de grafos** (el mismo del paso 4).

### 6.2 Qué son los nodos ahora

Cada **conexión** del camino de datos se etiqueta con una letra (A, B, C, …, P en tus apuntes). Una conexión es "un cable que lleva un dato de un sitio a otro en algún estado". Dos conexiones pueden compartir bus si **nunca se usan en el mismo estado**.

Tu hoja "Camino de datos" (15) pone letras a cada tramo:
- A, B, C, … = salidas de registros hacia las unidades (lecturas),
- J, K, L, M, N, O, P = entradas a los registros (escrituras).

### 6.3 Tabla de conexiones (tu hoja 17)

Es igual que la tabla de tiempos de vida, pero con **conexiones** en las filas y **estados** en las columnas. Una X marca que esa conexión se usa en ese estado:

```
        S0  S1  S2  S3  S4  S5  S6  S7
   A                              X        (grupo registros → U.F.)
   B          X   X           X
   C          X   X   X
   D                  X
   E              X
   ...
```

(La tabla completa es la de tu hoja; lo que importa es el método.)

### 6.4 Arcos de incompatibilidad

Dos conexiones son **incompatibles** (no comparten bus) si tienen una X en la **misma columna**. De tu hoja 17:

```
 Incompatibles:  B–C,  F–G,  J–L,  E–H,  C–G,  D–I
```

### 6.5 Partición en buses (tus hojas 18)

Se dibuja el grafo (arcos punteados = incompatibles) y se agrupan los compatibles. Tu resultado:

```
 Parte superior (lecturas):   Bus 1 = {A, C, F, I, E}
                              Bus 2 = {B, D, G, H}
 Parte inferior (escrituras): Bus 3 = {J, K, P}
                              Bus 4 = {L, M, N, O}
```

→ **4 buses** en total (2 de lectura + 2 de escritura). En vez de ~16 cables separados, 4 buses compartidos por three-states.

### 6.6 Regla para el examen

> **Número mínimo de buses = máximo número de conexiones distintas activas en un mismo estado** (la columna con más X de la tabla de conexiones). Es la misma regla que "registros mínimos = máximo de variables vivas", pero aplicada a cables.

---

## 7. El camino de datos con buses

Éste es tu "Camino de datos final" (hoja 19): los mismos registros y unidades, pero conectados por **4 buses** (las 4 líneas horizontales de colores) a los que todo accede con three-state:

```
          in1              in2
           │                │
      ┌────▼───┐       ┌─────▼──┐       ┌────────┐
    J►│ MUX R1 │     L►│ MUX R2 │     O►│ MUX R3 │◄─ P
    K►│        │     M►│        │       │        │
      └───┬────┘     N►└───┬────┘       └───┬────┘
       ┌──▼─┐          ┌───▼┐           ┌───▼┐
       │ R1 │          │ R2 │           │ R3 │
       └─┬──┘          └─┬──┘           └─┬──┘
   ══════╪═══════════════╪═══════════════╪══════  BUS 1 (lecturas)  {A,C,F,I,E}
   ══════╪═══════════════╪═══════════════╪══════  BUS 2 (lecturas)  {B,D,G,H}
         │ ▷ (three-states de acceso)    │
   ┌─────▼──┐   ┌────┐   ┌──────┐   ┌────▼┐   ┌────┐
   │ U.F.1  │   │>>1 │   │ U.F.2│   │ >>3 │   │ ...│
   │máx,|a| │   │    │   │mín,+,│   │     │   │    │
   └───┬────┘   └─┬──┘   │−,|b| │   └──┬──┘   └────┘
       │          │      └───┬──┘      │
   ════╪══════════╪══════════╪═════════╪══════  BUS 3 (escrituras) {J,K,P}
   ════╪══════════╪══════════╪═════════╪══════  BUS 4 (escrituras) {L,M,N,O}
       ▼
      SAL (three-state)
```

- Las unidades **leen** de los buses 1 y 2 por three-state.
- Los resultados se **escriben** en los buses 3 y 4, y de ahí a los MUX de los registros.
- La U.F.2 tiene una tablita de control (tu hoja 15): `c12 c13` = 00 |·|, 01 +, 10 −, 11 mín.

Ventaja: muchos menos cables. Precio: three-states por todos lados y la restricción de "una sola fuente por bus en cada estado", que ya se garantizó con la tabla de conexiones.

---

## 8. Segmentación: idea y métrica

### 8.1 Definición (tu hoja "Segmentación (Pipeline)")

> Técnica para mejorar las prestaciones de un circuito dividiéndolo en **etapas**, donde cada etapa funciona de manera casi independiente de las otras.

```
          ┌─────────┐              ┌──────┐
   IN ───►│         │        IN ──►│ E1   │
          │ Circuito│   ═══►       ╞══════╡ ║reg║
          │  comb.  │              │ E2   │
          │         │              ╞══════╡ ║reg║
          └────┬────┘              │ ...  │
               │ t_R               ╞══════╡
               ▼                   │ En   │
              OUT                  └──┬───┘
                                      ▼ OUT
```

- El retardo de cada etapa segmentada es **menor** que el del circuito entero: t_R(E1), t_R(E2)… < t_R.
- Cada etapa procesa una parte del cálculo.
- **Idealmente, con N etapas el tiempo de procesamiento se reduce a 1/N** del retardo original (tu nota al pie).

### 8.2 Las dos segmentaciones que pide el ejercicio

1. **Segmentar la unidad funcional** (una UF se parte en 2 etapas) → tu hoja 21.
2. **Segmentar el camino de datos** (todo el algoritmo se parte en etapas por niveles).

---

## 9. Segmentación de la unidad funcional

### 9.1 Qué se hace (tu hoja 21)

Se toma **una** unidad funcional (por ejemplo la que hace `+, −, máx, mín, |·|`) y se le mete un **registro interno** que la parte en dos etapas:

```
        A   B
        │   │
     ┌──▼───▼──┐
     │  + / −  │   ← Etapa 1 (sumador/restador)
     └────┬────┘
        ║reg║      ← registro de segmentación
     ┌────▼────┐
     │  MUX    │   ← Etapa 2 (selección máx/mín/abs)
     │  MUX    │
     └────┬────┘
          ▼
         SAL
```

Los cuadritos que tu dibujo marca entre las dos etapas son **los registros necesarios para la segmentación**.

### 9.2 Diagrama de bloques resultante (tu hoja 21, derecha)

```
          A        B
          │        │
      ┌───▼────────▼───┐
      │  UF SEGMENTADA │   (2 etapas internas)
      └───┬────────┬───┘
     ┌────▼─┐   ┌──▼───┐
     │ >>1  │   │ >>3  │
     └──┬───┘   └──┬───┘
        ▼          ▼
```

### 9.3 La pregunta clave de tu hoja: ¿cuál es la ganancia?

> "¿Cuál es la ganancia al segmentar la unidad funcional en una parte (dos etapas)?"

Respuesta con la regla de la sección 8: si la UF tardaba t_UF y se parte en 2 etapas iguales de t_UF/2, el **periodo de reloj** baja de (algo + t_UF) a (algo + t_UF/2). Pero una operación ahora tarda **2 ciclos** en salir (latencia), aunque la UF puede **empezar una operación nueva cada ciclo**.

- **Si las operaciones son dependientes** (como casi todo este algoritmo: t5 necesita x, t6 necesita t5…), segmentar la UF **no acelera**, porque hay que esperar el resultado antes de lanzar la siguiente. La latencia de 2 ciclos incluso puede hacerlo más lento.
- **Si hay operaciones independientes** que se pueden solapar, sí se gana: mientras una está en la etapa 2, otra entra en la etapa 1.

En este ejercicio, el camino es muy encadenado, así que la ganancia de segmentar **una** UF es pequeña; el ASM de tu hoja 21 marca con flechas rojas que t3 y t4 (estados S3–S4) podrían solaparse porque son independientes. Ahí sí ayuda.

### 9.4 Cómo cambia el ASM

Una operación lanzada en Sk da su resultado en Sk+1. En el ASM, las operaciones que dependen de ella se corren un estado; las independientes se lanzan en estados seguidos para llenar las dos etapas. Se dibuja el **diagrama de tiempos** con una fila por etapa.

---

## 10. Segmentación del camino de datos

### 10.1 Método

Se parte **todo el algoritmo** en etapas por **niveles de dependencia** (como el ASAP), con un registro de segmentación entre niveles. Cada etapa tiene su propio hardware y procesa un dato distinto a la vez.

### 10.2 Niveles del ejercicio

| Etapa | Operaciones | Depende de |
|---|---|---|
| E1 | t1=\|a\|, t2=\|b\| | entradas |
| E2 | x=máx(t1,t2), y=mín(t1,t2) | E1 |
| E3 | t3=x>>3, t4=y>>1 | E2 |
| E4 | t5=x−t3 | E3 (y x de E2) |
| E5 | t6=t5+t4 | E4 (y t4 de E3) |
| E6 | t7=máx(t6,x) | E5 (y x de E2) |

6 etapas. Entre cada par va un registro que guarda **todo lo que cruza la frontera**, incluidas las variables que solo "pasan" (x viaja desde E2 hasta E4 y E6).

### 10.3 Esquema

```
 a,b ─►║  E1   ║─►║  E2   ║─►║  E3   ║─►║ E4 ║─►║ E5 ║─►║ E6 ║─► SAL
       ║ |a|   ║  ║ máx   ║  ║ >>3   ║  ║ −  ║  ║ +  ║  ║máx ║
       ║ |b|   ║  ║ mín   ║  ║ >>1   ║  ║    ║  ║    ║  ║    ║
       reg       reg(x,y)   reg(x,    reg(x,  reg(x,  reg
                            t3,t4,y)  t5,t4)  t6)
```

Cada etapa tiene su propio hardware (ya no se comparte): 2 abs, 1 máx + 1 mín, 2 desplazadores, 1 restador, 1 sumador, 1 máx. Un dato nuevo (a, b) puede entrar **cada ciclo**.

### 10.4 Ganancia

- **Latencia** (un resultado): 6 etapas × T.
- **Productividad**: un resultado **por ciclo** una vez lleno el pipeline.
- Para N pares de datos: (6 + N − 1) × T, frente a 6·N·T del diseño secuencial → para N grande, **ganancia ≈ 6** (el número de etapas), como dice tu nota "1/N del retardo".
- Se pierde algo porque las etapas no duran exactamente igual (la del restador/sumador es más lenta que la del desplazador).

### 10.5 Diferencia con segmentar la UF

| | Segmentar la UF | Segmentar el CD |
|---|---|---|
| Qué se parte | una unidad | todo el algoritmo |
| Registros nuevos | 1 (interno) | uno por frontera de etapa |
| Hardware | el mismo | se multiplica (una unidad por operación) |
| Para qué sirve | subir el reloj de esa unidad | procesar un flujo de muchos datos |

---

## 11. Encadenamiento y multiciclo

Las otras dos técnicas de "tiempo" de tu primera hoja.

**Encadenamiento.** Dos operaciones **dependientes** en el mismo estado, conectando la salida de una unidad a la entrada de otra sin registro. Ejemplo en este ejercicio: `t5 = x − t3` seguido de `t6 = t5 + t4` podrían ir en un estado si el restador y el sumador están en cascada. Ahorra un estado, pero el periodo de reloj debe cubrir **resta + suma**.

**Multiciclo.** Una operación lenta ocupa **varios ciclos** de un reloj más corto. Útil cuando una unidad (por ejemplo un multiplicador, si lo hubiera) es mucho más lenta que las demás. Sus entradas deben mantenerse estables todos los ciclos y el resultado se guarda al final.

Las dos responden la misma pregunta: **cuánto trabajo cabe en un periodo de reloj.** Encadenar mete más (reloj más lento, menos estados); multiciclo mete menos (reloj más rápido, más estados).

---

## 12. Resumen y método de examen

### 12.1 Tabla de las tres agrupaciones (son el mismo método)

| Agrupar | Nodos del problema | Incompatibles si… | Mínimo | Herramienta |
|---|---|---|---|---|
| **Variables** | variables | sus vidas se solapan (misma columna) | máx. variables vivas | lado izquierdo |
| **Operadores** | operaciones | mismo estado o tipos sin unidad común | máx. operaciones del mismo tipo por estado | grafos |
| **Conexiones** | cables/tramos | activos en el mismo estado | máx. conexiones activas por estado | grafos |

### 12.2 Pasos del algoritmo de grafos (operadores y conexiones)

1. Nodos = unidades / conexiones.
2. Arcos de **incompatibilidad** (mismo estado).
3. Pesos **fuente/destino** en los arcos compatibles.
4. Une el arco de mayor peso → supernodo.
5. Al unir: conserva solo arcos compatibles con todos, suma pesos, busca el supernodo más grande.
6. Actualiza el grafo.
7. Repite hasta que no se pueda agrupar más.

### 12.3 Las dos segmentaciones

- **UF segmentada:** registro interno → la unidad se parte en 2 etapas, acepta una operación por ciclo, resultado en 2 ciclos. Gana solo si hay operaciones independientes que solapar.
- **CD segmentado:** una etapa por nivel del algoritmo, con registros entre etapas y hardware propio en cada una. Un resultado por ciclo; ganancia ≈ número de etapas para flujos largos.

### 12.4 Orden recomendado al resolver un ejercicio de síntesis

1. Pseudoalgoritmo → ASM → caja negra (ya lo sabes hacer).
2. **Variables** con lado izquierdo → número de registros.
3. **Operadores** con grafos → número de unidades funcionales.
4. Dibuja el CD con variables y operadores agrupados.
5. **Conexiones** con grafos → número de buses.
6. Dibuja el CD final con buses.
7. Si piden tiempo: **segmenta** (UF o CD) o **encadena/multiciclo**, y calcula la ganancia.

---

## Nota sobre esta guía

Reescribí todo para que siguiera el ejercicio de la raíz y los tres métodos de agrupación (variables = lado izquierdo, operadores y conexiones = partición de grafos) tal como aparecen en tus apuntes, más las dos segmentaciones. Si alguno de los grafos de tus hojas (los pesos `f/d` exactos, o la tabla de conexiones A–P completa) lo quieres resuelto celda por celda, dime y lo desarrollo entero: necesitaría que me confirmes los valores que se alcanzan a leer, porque algunas etiquetas de las fotos quedan borrosas.
