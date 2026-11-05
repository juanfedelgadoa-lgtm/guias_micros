# Técnicas de síntesis y segmentación aplicadas al parcial
### Encadenamiento, multiciclo, unidades funcionales segmentadas, camino de datos segmentado, control segmentado y buses

> Complemento de `guia_estudio_microprocesadores.md`. Todo se aplica al mismo ejercicio de la Realimentación N°2:
> **Out = (y² + eˣ) / 4**, con 1 multiplicador, 1 sumador y 1 desplazador de una posición.
> Igual que en la guía principal: nada de código, solo diseño.

---

## Índice

0. Punto de partida: el diseño base y un modelo de retardos
1. La idea común a todas las técnicas
2. Encadenamiento (*chaining*)
3. Multiciclo
4. Unidad funcional segmentada (multiplicador de 2 etapas)
5. Camino de datos segmentado (procesar un flujo de datos)
6. Control segmentado (registro de control y registro de estado)
7. Buses: compartir conexiones
8. Segmentación de buses (registros en los buses)
9. Comparación final y combinaciones
10. Cómo atacar cada técnica en un examen
11. Ejercicios propuestos con respuesta

---

## 0. Punto de partida: el diseño base y un modelo de retardos

### 0.1 El diseño base (el de la guía principal, sección E5)

| Estado | Operaciones | Transferencias |
|---|---|---|
| S0 | Final = 0, carga, espera Inicio | R1 ← in4 (y), R2 ← in2 (b), R3 ← in1 (a), R4 ← in3 (x) |
| S1 | t1 = x·x ; t2 = 1 + x | R6 ← R4 × R4 ; R5 ← 1 + R4 |
| S2 | t3 = t1·x | R4 ← R4 × R6 |
| S3 | t4 = a·t1 | R3 ← R3 × R6 |
| S4 | t5 = b·t3 ; t6 = t2 + t4 | R2 ← R2 × R4 ; R3 ← R3 + R5 |
| S5 | t8 = y·y ; t7 = t6 + t5 | R2 ← R1 × R1 ; R1 ← R3 + R2 |
| S6 | t9 = t8 + t7 | R1 ← R1 + R2 |
| S7 | t9 = t9 >> 1 | R1 ← R1 >> 1 |
| S8 | out = t9 >> 1, Final = 1 | OUT = R1 >> 1 |

9 estados, 6 registros, UC Moore sin señales de estado.

### 0.2 Modelo de retardos

Para poder **comparar** las técnicas hacen falta números. En el examen te los dan; aquí uso estos (son inventados pero realistas en proporción):

| Elemento | Retardo |
|---|---|
| Registro: clk→Q + setup | 1 + 1 = 2 ns |
| ROM de salida de la UC | 3 ns |
| ROM de entrada de la UC | 3 ns |
| Un nivel de MUX (o three-state) | 1 ns |
| Multiplicador | 16 ns |
| Sumador | 8 ns |
| Desplazador >>1 | 1 ns |

**Periodo del diseño base.** En una UC Moore con ROMs, el camino más largo de un estado es:

```
 registro de estado → ROM salida → MUX entrada UF → UF → MUX entrada registro → registro
      1 ns (clk→Q)      3 ns           1 ns         t_UF        1 ns             1 ns (setup)
```

  T = 7 ns + t_UF

- Con el multiplicador: 7 + 16 = **23 ns** ← camino crítico.
- Con el sumador: 7 + 8 = 15 ns.
- Con el desplazador: 7 + 1 = 8 ns.

**Tiempo por resultado** (operación continua: Inicio se deja en 1 y después de S8 se vuelve a S0, que carga datos nuevos): 9 ciclos × 23 ns = **207 ns**.

Ésta es la referencia contra la que se mide cada técnica.

---

## 1. La idea común a todas las técnicas

Todas las técnicas responden la misma pregunta: **¿cuánto trabajo combinacional cabe entre dos flancos de reloj?**

| Técnica | Qué hace | Efecto en el periodo T | Efecto en los ciclos |
|---|---|---|---|
| Encadenamiento | Mete 2 operaciones dependientes en un ciclo | Igual o mayor | Menos ciclos |
| Multiciclo | Deja que 1 operación lenta ocupe varios ciclos | Menor | Más ciclos |
| UF segmentada | Parte una unidad en etapas con registros internos | Menor | La unidad acepta una operación nueva cada ciclo |
| CD segmentado | Parte todo el algoritmo en etapas con hardware propio | Menor | Sale un resultado por ciclo |
| Control segmentado | Pone registros entre UC y CD | Menor | Añade ciclos de latencia en las decisiones |

Tiempo total = (número de ciclos) × T. Una técnica solo mejora si el producto baja. Más adelante vas a ver un caso (multiciclo) donde baja T pero el producto **sube**.

---

## 2. Encadenamiento (*chaining*)

### 2.1 Qué es

Conectar la salida de una unidad directamente a la entrada de otra, **sin registro en medio**, para hacer dos operaciones dependientes en el mismo estado.

### 2.2 Cómo se decide qué encadenar

1. Busca pares de operaciones dependientes en estados consecutivos.
2. Necesitas **dos unidades distintas** (la misma unidad no puede hacer dos operaciones en el mismo ciclo).
3. Suma los retardos del camino encadenado y compáralo con T:
   - Si cabe en T: el encadenamiento es "gratis" (ahorra un estado sin cambiar el reloj).
   - Si no cabe: T sube, y hay que ver si compensa.

### 2.3 Aplicado al parcial

Candidatos (operaciones dependientes en estados seguidos y con unidades distintas):

| Par | Unidades | Camino | ¿Cabe en 23 ns? |
|---|---|---|---|
| t9 = t8 + t7 → t9 >> 1 | + y >>1 | 1+3+1 + 8 + **1 (MUX del desplazador)** + 1 + 1 + 1 = 17 ns | Sí ✓ |
| t4 = a·t1 → t6 = t2 + t4 | × y + | 1+3+1 + 16 + 1 + 8 + 1 + 1 = 32 ns | No (T sube a 32) |
| t7 = t6 + t5 → t9 = t8 + t7 | + y + | Necesita 2 sumadores | No hay recursos |
| t9 >> 1 → >> 1 | >>1 y >>1 | Necesita 2 desplazadores | No hay recursos |

Fíjate en el MUX extra del desplazador: al encadenar, el desplazador recibe datos de dos sitios (del sumador en S6 y de R1 en S7), así que su entrada necesita un MUX 2:1. **Encadenar casi siempre añade un MUX al camino.**

El único encadenamiento útil es **suma + desplazamiento**.

### 2.4 ASM encadenado (8 estados)

```
 S0: Final = 0 ; a←in1, b←in2, x←in3, y←in4      ◇Inicio◇ ─0─► S0
 S1: t1 ← x·x ; t2 ← 1 + x
 S2: t3 ← t1·x
 S3: t4 ← a·t1
 S4: t5 ← b·t3 ; t6 ← t2 + t4
 S5: t8 ← y·y  ; t7 ← t6 + t5
 S6: t9 ← (t8 + t7) >> 1          ← encadenado: sumador → desplazador → R1
 S7: out = t9 >> 1 ; Final = 1    ──► S0
```

### 2.5 Qué cambia en el diseño

- **Camino de datos:** nueva conexión sumador → desplazador y un MUX 2:1 a la entrada del desplazador (0 = R1, 1 = salida del sumador).
- **Palabra de control:** +1 bit (selector de ese MUX). En S6: sel = 1, R1 carga la salida del desplazador. En S7: sel = 0.
- **Tiempos de vida:** t9 ya no se escribe en S6 y S7, solo nace al final de S6 y vive en S7. El máximo sigue siendo 6 → 6 registros.
- **Unidad de control:** 8 estados → **3 bits** (antes 4). ROM de entrada 2^(3+1) × 3 = 16 × 3; ROM de salida 8 × 23.
- **Tiempo:** 8 × 23 = **184 ns** por resultado (antes 207). Ganancia 1,125.

### 2.6 Para recordar

- El encadenamiento **cambia hardware por estados**: necesita unidades distintas y añade MUX.
- Es gratis solo si el camino encadenado es más corto que el camino crítico actual.
- Aquí el multiplicador fija T = 23 ns, así que hay 23 − 15 = 8 ns de "holgura" en los estados que solo suman: ahí cabe el desplazador.

---

## 3. Multiciclo

### 3.1 Qué es

Bajar el periodo de reloj para que lo ajusten las operaciones rápidas, y dejar que la operación lenta ocupe **varios ciclos**.

### 3.2 Reglas de un operador multiciclo (no segmentado)

1. Durante todos sus ciclos, **sus entradas deben quedarse quietas**: los selectores de sus MUX de entrada se repiten en cada estado de la operación, y los registros fuente no se pueden sobrescribir.
2. El resultado se guarda solo al final del **último** ciclo.
3. La unidad está **ocupada** todos esos ciclos: no acepta otra operación.

### 3.3 Aplicado al parcial

Nuevo reloj ajustado al sumador: T = 7 + 8 = **15 ns**.
El multiplicador necesita 7 + 16 = 23 ns ≤ 2 × 15 = 30 ns → **2 ciclos**.

Planificación (el multiplicador está ocupado 5 × 2 = 10 ciclos; la última multiplicación debe seguir siendo y·y):

| Estado | Multiplicador | Sumador | Desplazador |
|---|---|---|---|
| S1 | t1 = x·x (ciclo 1) | t2 = 1 + x | |
| S2 | t1 (ciclo 2, se guarda) | | |
| S3 | t3 = t1·x (1) | | |
| S4 | t3 (2) | | |
| S5 | t4 = a·t1 (1) | | |
| S6 | t4 (2) | | |
| S7 | t5 = b·t3 (1) | t6 = t2 + t4 | |
| S8 | t5 (2) | | |
| S9 | t8 = y·y (1) | t7 = t6 + t5 | |
| S10 | t8 (2) | | |
| S11 | | t9 = t8 + t7 | |
| S12 | | | t9 = t9 >> 1 |
| S13 | | | out = t9 >> 1, Final = 1 |

S0 + 13 estados = **14 ciclos × 15 ns = 210 ns**. **¡Es peor que el diseño base (207 ns)!**

¿Por qué? El algoritmo tiene 5 multiplicaciones en serie sobre un único multiplicador. Al pasar a 2 ciclos de 15 ns, cada multiplicación tarda 30 ns en vez de 23 ns: se desperdician 7 ns por multiplicación. Lo que se gana en los estados de suma no compensa.

**Lección:** el multiciclo sirve cuando las operaciones lentas son **pocas** comparadas con las rápidas. Aquí pasa lo contrario.

¿Y encadenar suma + desplazamiento con T = 15? Camino = 7 + 8 + 1 + 1 = 17 > 15. No cabe. **Las técnicas interactúan:** al bajar el reloj se pierde la holgura que permitía encadenar.

### 3.4 Tiempos de vida con multiciclo

Con multiciclo, un operando debe estar vivo durante **todos** los ciclos de la operación que lo lee:

| Var | Vida (estados) | Comentario |
|---|---|---|
| x | 1–4 | se lee en t1 (S1–S2) y t3 (S3–S4) |
| y | 1–10 | se lee en t8 (S9–S10) |
| a | 1–6 | se lee en t4 (S5–S6) |
| b | 1–8 | se lee en t5 (S7–S8) |
| t1 | 3–6 | |
| t2 | 2–7 | |
| t3 | 5–8 | |
| t4 | 7 | |
| t6 | 8–9 | |
| t5 | 9 | |
| t7 | 10–11 | |
| t8 | 11 | |
| t9 | 12–13 | |

Máximo: 6 (estados 3 a 6) → 6 registros. Las vidas se alargan porque las operaciones duran más.

### 3.5 Palabra de control en multiciclo

En S1 y S2 los selectores del multiplicador valen lo mismo (los dos operandos son x). El LD del registro destino de t1 vale **0 en S1** y **1 en S2**. Si pusieras LD = 1 en S1 guardarías un resultado a medio calcular.

---

## 4. Unidad funcional segmentada (multiplicador de 2 etapas)

### 4.1 Qué es

Se mete un registro **dentro** del multiplicador, que queda partido en dos etapas de 8 ns:

```
 operandos ──► [ Etapa 1: 8 ns ] ──► ║reg║ ──► [ Etapa 2: 8 ns ] ──► resultado
```

Diferencia clave con multiciclo:

| | Multiciclo | Segmentada |
|---|---|---|
| Latencia de una multiplicación | 2 ciclos | 2 ciclos |
| ¿Acepta otra multiplicación en el ciclo siguiente? | **No**, está ocupada | **Sí** |
| ¿Hay que mantener los operandos los 2 ciclos? | Sí | **No**, solo en el ciclo en que se lanza |

### 4.2 Reloj

- Etapa 1: 1 (clk→Q) + 3 (ROM) + 1 (MUX) + 8 + 1 (setup del registro interno) = 14 ns
- Etapa 2: 1 + 8 + 1 (MUX del registro destino) + 1 = 11 ns
- Sumador: 7 + 8 = 15 ns ← manda

**T = 15 ns.**

### 4.3 Regla de temporización nueva

> Una multiplicación **lanzada** en el estado Sk deja su resultado guardado al final de Sk+1. Ese resultado se puede usar a partir de **Sk+2**.

Por eso en cada estado hay que pensar en dos cosas distintas para el multiplicador:
- **qué multiplicación se lanza** (selectores de las entradas del multiplicador),
- **qué multiplicación termina** (MUX y LD del registro que recibe el resultado).

### 4.4 Planificación

La idea: mientras una multiplicación está "en vuelo", se lanza otra que **no dependa** de ella. La única independiente es y·y, así que se lanza al principio para rellenar el hueco.

| Estado | Lanza en el multiplicador | Termina (se guarda) | Sumador | Desplazador |
|---|---|---|---|---|
| S1 | t1 = x·x | | t2 = 1 + x | |
| S2 | t8 = y·y | t1 | | |
| S3 | t3 = t1·x | t8 | | |
| S4 | t4 = a·t1 | t3 | | |
| S5 | t5 = b·t3 | t4 | | |
| S6 | | t5 | t6 = t2 + t4 | |
| S7 | | | t7 = t6 + t5 | |
| S8 | | | t9 = t8 + t7 | |
| S9 | | | | t9 = t9 >> 1 |
| S10 | | | | out = t9 >> 1, Final = 1 |

Comprobaciones de dependencias:
- t3 en S3 usa t1, lanzado en S1 → disponible en S3 ✓
- t5 en S5 usa t3, lanzado en S3 → disponible en S5 ✓
- t6 en S6 usa t4, lanzado en S4 → disponible en S6 ✓
- t7 en S7 usa t5, lanzado en S5 → disponible en S7 ✓

Es óptimo: el camino crítico t1 → t3 → t5 → t7 → t9 → >>1 → >>1 mide 2 + 2 + 2 + 1 + 1 + 1 + 1 = 10 ciclos.

**Diagrama de tiempos (reservas de cada unidad):**

```
 Ciclo:          S1   S2   S3   S4   S5   S6   S7   S8   S9   S10
 Mult etapa 1:   t1   t8   t3   t4   t5    .    .    .    .    .
 Mult etapa 2:    .   t1   t8   t3   t4   t5    .    .    .    .
 Sumador:        t2    .    .    .    .   t6   t7   t9    .    .
 Desplazador:     .    .    .    .    .    .    .    .   >>1  >>1→out
```

Lees cada fila como una "agenda" de la unidad. Una multiplicación avanza en diagonal de la etapa 1 a la etapa 2.

**Tiempo:** S0 + 10 = 11 ciclos × 15 ns = **165 ns** (base 207). Ganancia 1,25.

### 4.5 Tiempos de vida (cambian, y salen menos registros)

Recuerda: un resultado lanzado en Sk nace en Sk+2. Los operandos solo hacen falta en el estado de lanzamiento.

| Var | Escrita al final de | Leída en | Vida |
|---|---|---|---|
| x | S0 | S1, S3 | 1–3 |
| y | S0 | S2 | 1–2 |
| a | S0 | S4 | 1–4 |
| b | S0 | S5 | 1–5 |
| t2 | S1 | S6 | 2–6 |
| t1 | S2 | S3, S4 | 3–4 |
| t8 | S3 | S8 | 4–8 |
| t3 | S4 | S5 | 5 |
| t4 | S5 | S6 | 6 |
| t5 | S6 | S7 | 7 |
| t6 | S6 | S7 | 7 |
| t7 | S7 | S8 | 8 |
| t9 | S8, S9 | S9, S10 | 9–10 |

| Estado | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| Vivas | 4 | 5 | 5 | 5 | 4 | 3 | 3 | 2 | 1 | 1 |

**Máximo 5 → 5 registros** (antes 6). El registro interno del multiplicador guarda un valor "en vuelo", y eso libera un registro del CD.

*Left-edge* (orden por inicio: x, y, a, b, t2, t1, t8, t3, t4, t5, t6, t7, t9):

| Registro | Variables |
|---|---|
| R1 | x(1–3) → t8(4–8) → t9(9–10) |
| R2 | y(1–2) → t1(3–4) → t3(5) → t4(6) → t5(7) → t7(8) |
| R3 | a(1–4) → t6(7) |
| R4 | b(1–5) |
| R5 | t2(2–6) |

### 4.6 Transferencias (RTL)

| Estado | Lanza (entradas del ×) | Recibe (salida del ×) | Sumador / desplazador |
|---|---|---|---|
| S0 | | | R1 ← in3, R2 ← in4, R3 ← in1, R4 ← in2 |
| S1 | R1 × R1 | | R5 ← 1 + R1 |
| S2 | R2 × R2 | R2 ← MUL (t1) | |
| S3 | R2 × R1 | R1 ← MUL (t8) | |
| S4 | R3 × R2 | R2 ← MUL (t3) | |
| S5 | R4 × R2 | R2 ← MUL (t4) | |
| S6 | | R2 ← MUL (t5) | R3 ← R5 + R2 |
| S7 | | | R2 ← R3 + R2 |
| S8 | | | R1 ← R1 + R2 |
| S9 | | | R1 ← R1 >> 1 |
| S10 | | | OUT = R1 >> 1, Final = 1 |

Casos que parecen conflicto pero son válidos: en S2 se lee y de R2 (para y·y) y al final de S2 se escribe t1 en R2. En S3 se lee x de R1 y al final se escribe t8 en R1. Se lee el valor viejo y se guarda el nuevo, como siempre.

### 4.7 Qué cambia en la UC

- 11 estados → 4 bits. ROM de entrada 32 × 4.
- La palabra de control de un estado mezcla **dos multiplicaciones distintas**: los selectores de entrada son de la que se lanza y el MUX/LD destino es de la que termina. Ejemplo, S3: entradas del × = (R2, R1) para t3; LD1 = 1 con el MUX de R1 en "MUL" para guardar t8.
- Si en un estado no se lanza nada, los selectores del × son X. Lo que nunca puede ser X es el LD del registro que recibe.

---

## 5. Camino de datos segmentado (procesar un flujo de datos)

### 5.1 Cuándo tiene sentido

Cuando hay que calcular la ecuación para **muchos juegos de datos** (a, b, x, y) seguidos, por ejemplo un juego nuevo en cada ciclo. Ya no se busca hacer un cálculo rápido, sino sacar **muchos resultados por segundo** (productividad).

Precio: cada etapa necesita su propio hardware, porque todas trabajan a la vez sobre datos distintos. **Ya no se comparten unidades.**

### 5.2 Método

1. Haz la planificación **ASAP** sin límite de recursos (cada nivel del DFG es un candidato a etapa).
2. Junta niveles consecutivos hasta que las etapas tengan retardos parecidos (**balancear**).
3. Pon un registro de segmentación entre etapas. Debe guardar **todas** las variables que cruzan la frontera, incluidas las que solo "pasan" hacia una etapa posterior.
4. T = etapa más lenta + registro.

### 5.3 Paso 1: niveles ASAP

| Nivel | Operaciones | Retardo del nivel |
|---|---|---|
| 1 | t1 = x·x, t2 = 1 + x, t8 = y·y | 16 (mult) |
| 2 | t3 = t1·x, t4 = a·t1 | 16 |
| 3 | t5 = b·t3, t6 = t2 + t4 | 16 |
| 4 | t7 = t6 + t5 | 8 |
| 5 | t9 = t8 + t7 | 8 |
| 6 | >>1, >>1 | 2 |

### 5.4 Paso 2: balancear

En un CD segmentado no hay ROM ni MUX en el camino (cada unidad tiene una conexión fija), así que cada etapa cuesta: retardo lógico + 2 ns de registro.

| Opción | Etapas | Etapa más lenta | T |
|---|---|---|---|
| A (4 etapas) | {1}, {2}, {3}, {4, 5, 6} | 8 + 8 + 2 = 18 | **20 ns** |
| B (5 etapas) | {1}, {2}, {3}, {4}, {5, 6} | 16 | **18 ns** |

Más etapas no siempre dan mucho: B gana solo 2 ns porque las etapas de multiplicación (16 ns) ya mandan. Partir más allá exigiría segmentar el propio multiplicador.

Me quedo con la **opción B**.

### 5.5 Paso 3: registros de segmentación

```
        ┌────────── E1 ──────────┐   ┌──── E2 ────┐   ┌──── E3 ────┐   ┌─ E4 ─┐   ┌──── E5 ────┐
 a ─►║  │                        │ ║ │            │ ║ │            │ ║ │      │ ║ │            │ ║
 b ─►║  │ t1 = x·x   (×)         │ ║ │ t3 = t1·x  │ ║ │ t5 = b·t3  │ ║ │ t7 = │ ║ │ t9 = t8+t7 │ ║─► out
 x ─►║  │ t2 = 1+x   (+)         │ ║ │ t4 = a·t1  │ ║ │ t6 = t2+t4 │ ║ │ t6+t5│ ║ │ >>1 >>1    │ ║
 y ─►║  │ t8 = y·y   (×)         │ ║ │            │ ║ │            │ ║ │      │ ║ │            │ ║
        └────────────────────────┘   └────────────┘   └────────────┘   └──────┘   └────────────┘
     reg entrada               reg E1/E2         reg E2/E3        reg E3/E4   reg E4/E5     reg salida
```

¿Qué guarda cada registro?

| Registro | Variables | Cuáles solo "pasan" | Cantidad |
|---|---|---|---|
| Entrada | a, b, x, y | | 4 |
| E1/E2 | t1, t2, t8, x, a, b | t2, t8, b no se usan en E2 | 6 |
| E2/E3 | t3, t4, t2, t8, b | t8 no se usa en E3 | 5 |
| E3/E4 | t5, t6, t8 | t8 no se usa en E4 | 3 |
| E4/E5 | t7, t8 | | 2 |
| Salida | out | | 1 |
| **Total** | | | **21 registros** |

Las variables que pasan sin usarse (t8 cruza 3 fronteras) son el **costo oculto** de segmentar: hay que retrasarlas con registros para que lleguen junto con los datos de su mismo juego.

Hardware total: 5 multiplicadores, 4 sumadores, 2 desplazadores (o un cableado de >>2), 21 registros.

### 5.6 Control del CD segmentado

No hace falta una FSM que recorra estados: todas las etapas hacen siempre lo mismo. Basta con un **bit de validez** que viaja con los datos:

```
 Inicio ─►║v║─►║v║─►║v║─►║v║─►║v║─► Final
```

Final = 1 indica que el dato que está saliendo es válido. Esto también es "control segmentado": el control avanza con los datos.

### 5.7 Métricas

| | Base (FSMD) | CD segmentado (5 etapas) |
|---|---|---|
| Periodo | 23 ns | 18 ns |
| Latencia (un resultado) | 207 ns | 5 × 18 = 90 ns |
| Productividad | 1 resultado / 207 ns | 1 resultado / 18 ns |
| N = 1000 juegos | 207 000 ns | (5 + 999) × 18 = 18 072 ns |
| Hardware | 1×, 1+, 1>>, 6 reg | 5×, 4+, 2>>, 21 reg |

**Cuidado al hablar de ganancia.** La mejora de 207 → 18 ns mezcla dos cosas:
- **Más hardware** (paralelismo): con las mismas 5×/4+/2>> pero sin registros, el circuito combinacional tarda 16+16+16+8+8+2 + 2 = 68 ns por resultado.
- **Segmentación**: 68 / 18 = **3,8** con 5 etapas (la ideal sería 5; se pierde por el desbalance: la etapa E4 solo usa 8 de 16 ns).

Si te preguntan "ganancia de la segmentación", compara contra el combinacional con el mismo hardware (68 ns), no contra el FSMD.

### 5.8 Nota avanzada: segmentar sin multiplicar el hardware

Si solo hay 1 multiplicador, también se pueden solapar juegos de datos consecutivos (empezar el siguiente antes de terminar el actual). El límite es el **intervalo de iniciación** (cada cuántos ciclos entra un dato nuevo): como cada juego usa el multiplicador 5 veces, ningún esquema baja de **5 ciclos por resultado**. Con el multiplicador segmentado de la sección 4 (T = 15 ns) la cota es 75 ns por resultado. Esto se llama segmentación funcional o de lazos.

---

## 6. Control segmentado (registro de control y registro de estado)

### 6.1 Dónde se ponen los registros

```
              ┌─────────┐   ┌──────┐   ┌─────────┐    ║registro de║
 Inicio ─────►│ROM ENTR.│──►│ ESTADO│──►│ROM SALID│───►║  CONTROL  ║────► CD
          ┌──►└─────────┘   └──────┘   └─────────┘    ║ (PC+Final)║
          │                                                         │
          └──────────────────║registro de ESTADO║◄── señales de estado (α, β…) ◄┘
```

- **Registro de control**: entre la ROM de salida y el CD. Saca la ROM de salida del camino crítico del CD.
- **Registro de estado** (de señales de estado): entre los comparadores del CD y la ROM de entrada. Saca el comparador del camino crítico de la UC.

### 6.2 Registro de control en el parcial

**Reloj.** El camino del CD ya no incluye la ROM:

```
 registro de control → MUX → UF → MUX → registro      =  1 + 1 + t_UF + 1 + 1  =  4 + t_UF
 registro de estado → ROM salida → registro de control =  1 + 3 + 1 = 5 ns
```

Con el multiplicador: 4 + 16 = **20 ns** (antes 23).

**Temporización.** El CD ejecuta la palabra de control de un estado **un ciclo después** de que la UC pasa por ese estado:

```
 Ciclo:        k     k+1   k+2   k+3   ...   k+8   k+9
 UC en:        S0    S1    S2    S3    ...   S8    S0
 CD ejecuta:   (…)   PC0   PC1   PC2   ...   PC7   PC8 → out, Final = 1
```

Como el parcial **no tiene señales de estado**, el CD hace exactamente la misma secuencia, solo que desplazada un ciclo. No hay que cambiar el ASM ni la tabla de palabras de control. Solo hay que meter **Final en el mismo registro** que la palabra de control, para que Final y `h` (el three-state) salgan en el mismo ciclo.

**Tiempo:**
- Primer resultado: 10 ciclos × 20 = 200 ns.
- Operación continua: el ciclo extra se solapa con el cálculo siguiente, así que sale un resultado cada 9 ciclos × 20 = **180 ns** (base 207).
- Costo: un registro de 22 bits (21 de PC + Final).

### 6.3 Cuando hay decisiones: el problema real

El control segmentado solo es "gratis" si no hay señales de estado. Para verlo, una **variante** del parcial con saturación:

> Si t9 ≥ LIM, la salida es el máximo (OV = 1). Si no, out = t9 >> 2.

Diseño base (sin registros de segmentación):

```
 S6: t9 ← t8 + t7
 S7: t9 ← t9 >> 1      ◇ β = (t9 ≥ LIM) ◇   (el comparador mira R1, que en S7 ya tiene t9)
          β = 0 → S8: out = t9 >> 1, Final = 1
          β = 1 → S9: out = MAX, OV = 1, Final = 1
```

**Con registro de control.** La UC está en S7 en el ciclo k, pero el CD está ejecutando PC6 (calculando t9). El comparador ve en el ciclo k el valor **viejo** de R1. β correcto aparece en k+1. La UC tiene que decidir **un estado después**:

```
 Ciclo:        k        k+1          k+2
 UC en:        S7       S7b          S8 o S9  ← decide en S7b
 CD ejecuta:   PC6      PC7          PC7b (nada: "burbuja")
 R1:           t7       t9           t9 >> 1
 β válido:     no       sí
```

Se añade un estado S7b vacío y la decisión se mueve ahí. Costo: **1 ciclo (burbuja)** en ese camino.

**Con registro de control + registro de estado.** β pasa además por un flip-flop: llega a la UC en k+2. Hacen falta **dos** estados entre el que pide el cálculo y el que decide: 2 burbujas.

**Cómo esconder las burbujas:** rellenar los estados de espera con trabajo útil que no dependa de β. En un algoritmo largo suele haber operaciones independientes que se pueden mover ahí. En esta variante casi no queda nada: el segundo `>> 1` se podría hacer en S7b de forma especulativa, pero S8 sigue haciendo falta para sacar el resultado, así que la burbuja no desaparece. Ése es el caso típico en que segmentar el control cuesta ciclos.

### 6.4 Regla para el examen

> Con un registro de control y/o de estado, cuenta cuántos ciclos tarda una señal de estado en llegar a la UC desde que la UC pidió la operación que la genera: 0 sin registros, 1 con uno de los dos, 2 con ambos. La caja de decisión debe ir ese número de estados después. Si no hay trabajo útil para esos estados, son burbujas.

---

## 7. Buses: compartir conexiones

### 7.1 Conexión punto a punto vs bus

**Punto a punto** (como el CD de la guía principal): cada entrada de unidad tiene su MUX, con un cable desde cada registro que la alimenta.

**Bus**: un cable común al que varias fuentes se conectan con **three-state**. En cada estado solo una fuente maneja el bus, y **varios destinos** pueden leerlo a la vez.

| | Punto a punto | Buses |
|---|---|---|
| Cables | Muchos (una conexión por par fuente→destino) | Pocos |
| Lógica | MUX grandes en cada destino | Three-state por fuente + MUX pequeños |
| Restricción | Ninguna | Máximo **una fuente por bus en cada estado** |

### 7.2 Método (es otra vez un problema de compatibilidad)

1. A partir de la tabla RTL, anota en qué estados **se lee** cada fuente (cada registro y cada constante).
2. Dos fuentes son **compatibles** (pueden compartir bus) si nunca se leen en el mismo estado.
3. **Número mínimo de buses = máximo número de fuentes distintas leídas en un mismo estado.** Es el mismo razonamiento que con los registros.
4. Agrupa fuentes compatibles en buses (colorear el grafo de conflicto). Entre las opciones, prefiere juntar fuentes que van **al mismo destino**: así el MUX de ese destino es más pequeño. Ésta es la "prioridad" o peso del grafo.
5. Usa la conmutatividad para reducir más los MUX.
6. Repite para las salidas de las unidades (buses de escritura).

### 7.3 Paso 1: tabla de lecturas (base del parcial, S1–S6)

El desplazador lee siempre de R1: lo dejo como **cable dedicado** fuera de los buses.

| Fuente | S1 | S2 | S3 | S4 | S5 | S6 | Destinos |
|---|---|---|---|---|---|---|---|
| R1 (y, t7) | | | | | X | X | ×(S5), +(S6) |
| R2 (b, t5, t8) | | | | X | X | X | ×(S4), +(S5, S6) |
| R3 (a, t4, t6) | | | X | X | X | | ×(S3), +(S4, S5) |
| R4 (x, t3) | X | X | | X | | | ×(S1, S2, S4), +(S1) |
| R5 (t2) | | | | X | | | +(S4) |
| R6 (t1) | | X | X | | | | ×(S2, S3) |
| "1" | X | | | | | | +(S1) |
| **Fuentes por estado** | 2 | 2 | 2 | **4** | 3 | 2 | |

En S1, R4 alimenta a la vez las dos entradas del × y una del +: es **una sola fuente** en un solo bus, con tres destinos. Eso está permitido.

**Mínimo: 4 buses de lectura** (en S4 se leen R2, R3, R4 y R5).

### 7.4 Paso 2: grafo de conflicto y asignación

Conflictos (se leen en el mismo estado): R4–"1" (S1), R4–R6 (S2), R3–R6 (S3), R2–R3–R4–R5 entre todos (S4), R1–R2–R3 entre todos (S5), R1–R2 (S6).

Compatibilidades útiles: R1–R4, R1–R5, R1–R6, R2–R6, R2–"1", R3–"1", R5–R6, R5–"1", R6–"1".

R2, R3, R4 y R5 están en conflicto entre sí (S4), así que cada uno va en un bus distinto. Falta repartir R1, R6 y "1":

| Bus | Fuentes | Por qué |
|---|---|---|
| A | R4, R1 | R1 es compatible con R4 y con R5; va con R4 porque los dos alimentan las mismas entradas (× izquierda y + izquierda) |
| B | R2, R6, "1" | Los tres van a entradas que también lee R2 (prioridad) |
| C | R3 | |
| D | R5 | |

### 7.5 Paso 3: MUX a la entrada de cada unidad

Una entrada recibe uno de los buses. Con la asignación anterior y **cambiando el orden de los operandos en S4** (t5 = t3·b en vez de b·t3, para que la entrada izquierda del × lea R4 por el bus A):

| Entrada | Lee de (estado → bus) | Buses distintos | MUX |
|---|---|---|---|
| × izquierda | R4 (S1, S2, S4) → A ; R3 (S3) → C ; R1 (S5) → A | A, C | 2:1 |
| × derecha | R4 (S1) → A ; R6 (S2, S3) → B ; R2 (S4) → B ; R1 (S5) → A | A, B | 2:1 |
| + izquierda | R4 (S1) → A ; R3 (S4, S5) → C ; R1 (S6) → A | A, C | 2:1 |
| + derecha | "1" (S1) → B ; R5 (S4) → D ; R2 (S5, S6) → B | B, D | 2:1 |

| | Punto a punto (guía principal) | Con buses |
|---|---|---|
| Entradas de MUX en las unidades | 4 + 3 + 3 + 3 = 13 | 2 + 2 + 2 + 2 = 8 |
| Three-state | 1 (salida) | 7 (uno por fuente) + 1 (salida) |
| Cables de lectura | 13 conexiones | 4 buses |

### 7.6 Paso 4: buses de escritura

Resultados por estado: S1 (×, +), S2 (×), S3 (×), S4 (×, +), S5 (×, +), S6 (+), S7 (>>).
Máximo 2 a la vez → **2 buses de escritura**:
- **W1** = salida del multiplicador.
- **W2** = sumador **o** desplazador (nunca escriben en el mismo estado), cada uno con su three-state.

Con eso, el MUX de R1 baja de 3:1 (in4, +, >>) a 2:1 (in4, W2). Las entradas in1…in4 se dejan como conexiones directas porque en S0 se cargan las cuatro a la vez.

### 7.7 Los buses también restringen la planificación

Los buses son un **recurso** como las unidades funcionales. Si solo hubiera **3 buses de lectura**, S4 (4 fuentes) sería imposible y habría que replanificar. Por ejemplo:

```
 S4: t5 = b·t3                       (lee R2, R4)
 S5: t6 = t2 + t4 ; t8 = y·y          (lee R5, R3, R1) → 3 fuentes
 S6: t7 = t6 + t5
 S7: t9 = t8 + t7
 S8: t9 >> 1
 S9: out = t9 >> 1
```

Un estado más. Después habría que rehacer tiempos de vida y registros. Conclusión: **menos buses ⇒ menos cables pero más estados.**

---

## 8. Segmentación de buses (registros en los buses)

> Este nombre no es igual en todos los libros. Si en tu clase "segmentación de buses" significa otra cosa, dime y lo ajusto.

### 8.1 Idea

Además de segmentar una unidad o el algoritmo, se pueden poner registros **en los propios buses**:
- **registros de operandos** entre los buses de lectura y las entradas de las unidades,
- **registros de resultado** entre la salida de las unidades y los buses de escritura.

Cada operación se convierte en una pequeña cadena de 3 etapas:

```
  L (lectura):   registro fuente → three-state → bus → ║reg operando║
  E (ejecución): ║reg operando║ → unidad funcional → ║reg resultado║
  W (escritura): ║reg resultado║ → bus escritura → MUX → registro destino
```

### 8.2 Efecto en el reloj

Con los retardos del modelo:
- L: 1 + 3 (ROM) + 1 (three-state) + 1 (MUX) + 1 = 7 ns
- E: 1 + 16 + 1 = 18 ns (multiplicador) ← manda
- W: 1 + 1 (three-state) + 1 (MUX) + 1 = 4 ns

T = 18 ns (antes 23).

### 8.3 Efecto en las dependencias

Ahora **cada** operación tarda 3 ciclos desde que se leen sus operandos hasta que su resultado está en el registro. Una operación que usa ese resultado tiene que esperar:

```
 Ciclo:     1    2    3    4    5    6
 t1=x·x:    L    E    W
 t3=t1·x:             ·    L    E    W     ← no puede leer t1 hasta el ciclo 4
```

Solución típica: **adelantamiento (*bypass*)**. Se conecta el registro de resultado directamente a la entrada de la unidad (sin pasar por el banco), y t3 puede empezar en el ciclo 3. Cuesta un MUX más en la entrada de la unidad.

Para el parcial, que es casi todo una cadena de dependencias, esta técnica ayuda poco sin *bypass*. Brilla cuando hay muchas operaciones **independientes** que mantienen ocupadas las tres etapas.

---

## 9. Comparación final y combinaciones

### 9.1 Técnicas por separado (un resultado, operación continua)

| Variante | T | Ciclos | Tiempo / resultado | Unidades | Registros | Estados UC |
|---|---|---|---|---|---|---|
| Base | 23 ns | 9 | 207 ns | 1×, 1+, 1>> | 6 | 9 (4 bits) |
| Encadenamiento + y >> | 23 ns | 8 | **184 ns** | igual + 1 MUX | 6 | 8 (3 bits) |
| Multiciclo (× en 2 ciclos) | 15 ns | 14 | 210 ns ✗ | igual | 6 | 14 (4 bits) |
| × segmentado (2 etapas) | 15 ns | 11 | **165 ns** | × con reg. interno | 5 | 11 (4 bits) |
| Registro de control | 20 ns | 9 | **180 ns** | + reg. de 22 bits | 6 | 9 (4 bits) |
| CD segmentado (5 etapas) | 18 ns | 1 por resultado | **18 ns** | 5×, 4+, 2>> | 21 | sin FSM (bit de validez) |

### 9.2 Combinaciones (las técnicas se suman o se estorban)

| Combinación | T | Ciclos | Tiempo | Comentario |
|---|---|---|---|---|
| Registro de control + encadenamiento | 20 ns (camino + y >>: 1+1+8+1+1+1+1 = 14 ≤ 20 ✓) | 8 | **160 ns** | Se suman |
| Registro de control + × segmentado | máx(etapa 1 = 1+1+8+1 = 11, sumador = 4+8 = 12) = **12 ns** | 11 | **132 ns** | Se suman: el sumador pasa a mandar |
| × segmentado + encadenamiento | 15 ns, pero + y >> = 7+8+1+1 = 17 > 15 ✗ | | | Se estorban: ya no hay holgura |
| Multiciclo + encadenamiento | 15 ns, 17 > 15 ✗ | | | Se estorban |

Patrón general: **una técnica que baja T le quita holgura al encadenamiento**. Por eso, antes de combinar, recalcula siempre el camino crítico.

---

## 10. Cómo atacar cada técnica en un examen

**Siempre primero:**
1. DFG del algoritmo.
2. Planificación base con los recursos dados.
3. Retardos: T base y camino crítico.

**Encadenamiento**
1. Lista pares dependientes en estados seguidos con unidades distintas.
2. Calcula el camino encadenado (no olvides el MUX que aparece).
3. Si cabe en T, elimina el estado; si no, calcula el nuevo T y compara ciclos × T.
4. Actualiza: ASM, conexiones nuevas, MUX nuevos, bits de la PC, tiempos de vida, tamaño de la UC.

**Multiciclo**
1. Nuevo T = el de la operación rápida que quieras.
2. Ciclos de la lenta = ⌈(overhead + t_lenta) / T⌉.
3. Replanifica con la unidad ocupada todos sus ciclos.
4. En la PC: selectores repetidos en todos los ciclos; LD destino solo en el último.
5. Calcula ciclos × T y compara. Puede salir peor.

**Unidad funcional segmentada**
1. T = máx(etapas de la unidad, resto de operaciones).
2. Regla: lanzada en Sk → disponible en Sk+(número de etapas).
3. Replanifica lanzando operaciones independientes en los huecos.
4. Dibuja el diagrama de reservas (una fila por etapa de cada unidad).
5. Recalcula tiempos de vida (el resultado nace más tarde; el operando solo se necesita al lanzar).
6. En la PC: separa "qué se lanza" de "qué se recibe".

**Camino de datos segmentado**
1. ASAP sin límite de recursos.
2. Junta niveles hasta balancear; T = etapa más lenta + registro.
3. Registros de segmentación: todas las variables que cruzan cada frontera.
4. Hardware: una unidad por operación de cada etapa.
5. Métricas: latencia k·T, productividad 1/T, (k + N − 1)·T, ganancia contra el combinacional equivalente.

**Control segmentado**
1. Registro de control: quita la ROM de salida del camino del CD → nuevo T.
2. Registro de estado: quita el comparador del camino de la UC.
3. Sin señales de estado: solo +1 ciclo de latencia.
4. Con decisiones: mueve cada caja de decisión 1 (o 2) estados más tarde y rellena o deja burbujas.

**Buses**
1. Tabla de lecturas por estado desde la tabla RTL.
2. Mínimo de buses = máximo de fuentes distintas en un estado.
3. Grafo de conflicto → asignación, priorizando fuentes con destinos comunes.
4. MUX en cada entrada = buses distintos que llegan; usa conmutatividad.
5. Lo mismo para resultados (buses de escritura).
6. Si te limitan los buses, replanifica.

---

## 11. Ejercicios propuestos con respuesta

Usa los mismos retardos de la sección 0.2.

**P1.** Out = (a·b + c·d) >> 1, con 1 multiplicador **segmentado en 2 etapas**, 1 sumador y 1 desplazador. Planifica y compara con la versión no segmentada.

<details><summary>Respuesta</summary>

No segmentado (T = 23): S0 carga; S1 t1 = a·b; S2 t2 = c·d; S3 t3 = t1 + t2; S4 out = t3 >> 1. 5 ciclos × 23 = 115 ns.

Segmentado (T = 15):

| Estado | Lanza × | Recibe × | Sumador | Desplazador |
|---|---|---|---|---|
| S1 | t1 = a·b | | | |
| S2 | t2 = c·d | t1 | | |
| S3 | | t2 | | |
| S4 | | | t3 = t1 + t2 | |
| S5 | | | | out = t3 >> 1 |

6 ciclos × 15 = 90 ns. S3 queda vacío esperando a t2 (no hay nada independiente que hacer).
Bonus: ¿se puede encadenar + y >> en S4? 7 + 8 + 1 + 1 = 17 > 15, no.
</details>

**P2.** En el diseño base del parcial, ¿se puede encadenar t1 = x·x con t3 = t1·x si se añade un segundo multiplicador? ¿Conviene?

<details><summary>Respuesta</summary>

Camino: 7 + 16 + 1 (MUX) + 16 = 40 ns → T = 40. Se ahorra un estado (8 ciclos), pero 8 × 40 = 320 ns, mucho peor que 207 ns. Además hace falta otro multiplicador. No conviene: encadenar dos operaciones lentas casi nunca compensa.
</details>

**P3.** Con el CD segmentado de 5 etapas (T = 18 ns), ¿cuánto tarda en procesar 50 juegos de datos? ¿Y la versión de 4 etapas (T = 20 ns)?

<details><summary>Respuesta</summary>

5 etapas: (5 + 49) × 18 = 972 ns. 4 etapas: (4 + 49) × 20 = 1060 ns. Para pocos datos la diferencia es menor porque pesa el llenado del pipeline.
</details>

**P4.** Con la tabla de lecturas de la sección 7.3, si se elimina R5 guardando t2 en otro registro libre, ¿cuántos buses de lectura harían falta como mínimo?

<details><summary>Respuesta</summary>

Depende de dónde se guarde t2, pero t2 se sigue leyendo en S4 junto con b/t5 (R2), t4 (R3) y t3 (R4). Siguen siendo 4 fuentes distintas en S4 → 4 buses. Reducir registros no reduce buses: lo que cuenta es cuántos **valores distintos** se leen a la vez.
</details>

**P5.** En la variante con saturación (sección 6.3), con registro de control y registro de estado, ¿cuántos ciclos tarda un resultado saturado y uno normal, en operación continua?

<details><summary>Respuesta</summary>

Base con la decisión: S0–S8, o S0–S7 + S9 → 9 ciclos en ambos caminos.
- Solo registro de control: 1 estado de espera (S7b) → 10 ciclos × 20 ns = 200 ns.
- Registro de control + registro de estado: β llega 2 ciclos tarde → 2 estados de espera → 11 ciclos × 20 ns = 220 ns.

Mover el segundo `>> 1` a un estado de espera no ahorra nada, porque el estado final (sacar el resultado) sigue haciendo falta y en Moore su salida no puede depender de β en el mismo estado en que se decide.
</details>

**P6.** Explica en dos frases la diferencia entre un multiplicador multiciclo y uno segmentado, ambos con latencia de 2 ciclos.

<details><summary>Respuesta</summary>

El multiciclo queda ocupado los 2 ciclos y sus operandos deben mantenerse estables todo ese tiempo. El segmentado guarda un resultado parcial en un registro interno, así que acepta una multiplicación nueva cada ciclo y sus operandos solo se necesitan en el ciclo en que se lanza.
</details>
