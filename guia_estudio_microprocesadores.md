# Guía de estudio: Análisis y Diseño de Microprocesadores
### Diseño basado en Unidad de Control + Camino de Datos (UC + CD / FSMD)

> Material base: diapositivas del Prof. Andrés Gaona ("Diseño basado en UC y CD"), apuntes de ASM, Talleres 5 y 6, problemas del capítulo 8 de *Principios de Diseño Digital* (Gajski) y la Realimentación N°2 del semestre anterior.
> No se incluye nada de VHDL: solo diseño (algoritmo, ASM, camino de datos, unidad de control, optimización).

---

## Índice

**Parte I: Teoría**
1. El modelo UC + CD
2. Reglas de temporización (la idea más importante del curso)
3. Caja negra y caja gris
4. Diagramas ASM
5. Moore vs Mealy en ASM
6. Metodología completa de diseño (los pasos que piden en el parcial)
7. Componentes del camino de datos
8. La palabra de control
9. La unidad de control: implementación canónica con ROMs
10. Optimización del camino de datos: tiempos de vida, *left-edge* y grafos
11. Planificación (scheduling): ASAP, ALAP, movilidad, TC y RC
12. Encadenamiento y multiciclo
13. Segmentación (pipelining)
14. Periodo de reloj y camino crítico
15. Técnicas algorítmicas de los talleres (sumas/restas sucesivas, signo, decimales, overflow)

**Parte II: Ejercicios resueltos**
- E1. Ejemplo 1 del profesor: Σ xᵢ con CD preestablecido
- E2. Ejemplo 2 del profesor: contador de unos con banco de registros
- E3. Contador de unos de los apuntes: versión Moore vs versión Mealy
- E4. Dimensionamiento de la UC en los Talleres 5 y 6
- **E5. EL PARCIAL (Realimentación N°2) resuelto completo + análisis de tus errores**
- E6. Problema 8.10: asignación de registros con *left-edge*
- E7. Problemas 8.20–8.22: planificación ASAP/ALAP/TC/RC (ecuación diferencial)
- E8. Algoritmo SRA: planificación y camino de datos segmentado (8.15)
- E9. Problemas 8.4, 8.5 y 8.8: diagramas ASM
- E10. Problema 8.11: partición de grafos de compatibilidad
- E11. Problema 8.16: control segmentado

**Parte III: Práctica y repaso**
- Ejercicios propuestos con respuesta
- Errores frecuentes
- Hoja de fórmulas

---

# PARTE I: TEORÍA

## 1. El modelo UC + CD

Un microprocesador **dedicado** (de propósito específico) se divide en dos bloques que trabajan juntos:

```
              Entradas de control (Inicio)          Puertos de entrada (datos)
                        │                                    │
                        ▼                                    ▼
              ┌───────────────────┐  Señales de control ┌───────────────────┐
              │  UNIDAD DE        │ ───────────────────►│  CAMINO DE        │
              │  CONTROL (UC)     │   (palabra de       │  DATOS (CD)       │
              │  = una FSM        │    control, PC)     │                   │
              │                   │◄─────────────────── │                   │
              └───────────────────┘  Señales de estado  └───────────────────┘
                        │             (α, β, OV, ...)                │
                        ▼                                            ▼
              Salidas de control (Final)                 Puertos de salida (resultado)
```

**Unidad de Control (UC).** Es una máquina de estados finitos (FSM). No calcula nada. Decide *qué* se hace en cada ciclo de reloj:
- qué operación hace cada unidad funcional (sumar, restar, AND…),
- de dónde vienen los operandos (selectores de multiplexores, direcciones de lectura del banco),
- dónde se guarda el resultado (habilitación de escritura de registros, dirección de escritura).

**Camino de Datos (CD).** Es el circuito que sí calcula: registros, ALU, sumadores, multiplicadores, desplazadores, comparadores, multiplexores, buffers *three-state*. Los datos pueden llegar desde puertos externos o estar guardados en registros/memorias internas (por ejemplo, las ROM de los talleres).

**Las dos señales que los conectan:**

| Señal | Dirección | Qué es | Ejemplos |
|---|---|---|---|
| Señales de control (palabra de control, PC) | UC → CD | Bits que configuran el CD en el estado actual | `s` del MUX, `wr`, `dirA`, `M s1 s0` de la ALU, `h` del three-state |
| Señales de estado | CD → UC | Bits de 1 bit que resumen una condición de los datos | α = (i = 10), β = (Dato = 0), OV, signo |

Las señales de estado existen **solo** porque el ASM tiene cajas de decisión que preguntan por datos. Si el algoritmo no tiene decisiones sobre datos (como en el parcial), el CD no genera señales de estado y la UC solo depende de `Inicio`.

En el libro de Gajski a este conjunto se le llama **FSMD** (*Finite State Machine with Datapath*).

---

## 2. Reglas de temporización (la idea más importante del curso)

Estas cuatro frases de las diapositivas explican casi todos los errores típicos:

1. Las constantes y variables se guardan en memorias, registros o flip-flops.
2. Los datos se guardan **de forma síncrona** (en el flanco de reloj).
3. El CD transforma los datos **durante** un estado (entre dos flancos).
4. El resultado se guarda **al final del estado actual** y está disponible **en el estado siguiente**.

Consecuencias prácticas:

- **Dentro de un mismo estado, todas las asignaciones son simultáneas.** Si en un estado escribes `t1 = x·x` y `t3 = t1·x`, el `t1` que usa la segunda operación es el **viejo**, no el que acabas de calcular. Por eso una operación que depende de otra debe ir en un estado **posterior** (o usar encadenamiento, sección 12).
- **Un registro se puede leer y escribir en el mismo estado.** Se lee el valor viejo y al final del estado queda el nuevo. Por eso `suma = suma + x` o `t9 = t9 >> 1` caben en un estado.
- **Una variable que se calcula en el estado Sk "nace" en Sk+1.** Esto es la base de los tiempos de vida (sección 10).
- **Una decisión que pregunta por un registro ve el valor que tenía al entrar al estado**, no el que se está escribiendo en ese estado. Este detalle aparece en el ejemplo del contador de unos (E2).

```
  reloj:   ─┐  ┌──┐  ┌──┐  ┌──┐  ┌──
            └──┘  └──┘  └──┘  └──┘
  estado:  |  S1  |  S2  |  S3  |
           |t1←x·x|t3←t1·x|
                  ▲
                  └── t1 ya está guardado: se puede usar en S2
```

---

## 3. Caja negra y caja gris

**Caja negra.** Es la vista externa del sistema completo: solo entradas y salidas, con su número de bits. No muestra nada interno.

```
            Inicio ──►┌──────────────┐──► Final
     in1..in4 ──/n──►│  Ecuación    │──/n──► Out
               CLK ──►│              │
               RST ──►└──────────────┘
```

**Caja gris.** Abre la caja negra en dos bloques (UC y CD) y muestra **las señales entre ellos con su número de bits**: el ancho de la palabra de control y cuántas señales de estado hay.

```
   Inicio                         in1..in4
     │                               │
     ▼        PC (k bits)            ▼
  ┌──────┐ ───────/k────────►  ┌──────┐
  │  UC  │                     │  CD  │──/n──► Out
  │      │ ◄──────/m────────── │      │
  └──────┘   señales estado    └──────┘
     │        (m bits)          ▲    ▲
     ▼                         CLK  RST
   Final       (CLK y RST llegan a ambos)
```

Para dibujar la caja gris completa necesitas conocer **k** (bits de la palabra de control) y **m** (señales de estado). Por eso la caja gris se termina después de diseñar el CD.

Reglas para repartir las señales:
- `Inicio` entra a la **UC** (es una entrada de control, se usa en una caja de decisión).
- `Final` sale de la **UC** (es una salida que depende solo del estado).
- Los datos de entrada y el resultado entran y salen del **CD**.
- CLK y RST llegan a los dos bloques.

---

## 4. Diagramas ASM (Algorithmic State Machine)

Un ASM es un diagrama de flujo con significado temporal: describe a la vez la UC y lo que hace el CD en cada estado.

### 4.1 Los tres tipos de caja

| Caja | Forma | Qué contiene | Qué implica para la UC | Qué implica para el CD |
|---|---|---|---|---|
| **De estado** | Rectángulo | Asignaciones incondicionales: `d = b + c`, `h = h >> 2`, `Final = 1` | Cada caja de estado es **un estado** de la FSM | Define las unidades funcionales y los registros necesarios |
| **De decisión** | Rombo, salidas 1/0 | Una pregunta: `Inicio`, `d = 0`, `b ≥ c` | Las preguntas son **entradas** de la UC (condiciones de transición) | Hay que crear un bloque combinacional (comparador) que genere la señal de estado |
| **De asignación condicional** | Óvalo / rectángulo redondeado | Asignaciones que solo ocurren si se tomó ese camino: `a = INPORT` | **No** genera estado nuevo. Su presencia hace la máquina **Mealy** | Igual que la caja de estado: pide operadores y registros |

### 4.2 El bloque ASM

Un **bloque ASM** es una caja de estado más todas las cajas de decisión y de asignación condicional que cuelgan de ella hasta llegar a la siguiente caja de estado. **Todo lo que hay dentro de un bloque ocurre en un solo ciclo de reloj.**

```
   ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐  ← bloque ASM del estado S2
     ┌──────────────┐
   │ │ S2:  cuenta  │              │   (caja de estado)
     └──────┬───────┘
   │        ▼                      │
         ◇ α ◇ ── 0 ──┐                (caja de decisión)
   │        │1        │            │
            ▼         │
   │  (cuenta=cuenta+1)│           │   (asignación condicional)
            │         │
   └ ─ ─ ─ ─┼─ ─ ─ ─ ─┼─ ─ ─ ─ ─ ─ ┘
            ▼         ▼
          S3 ...     S4 ...
```

### 4.3 Reglas del ASM (de tus apuntes)

1. **Para un estado presente y un conjunto de valores de las decisiones solo debe haber un estado siguiente.** No pueden salir dos caminos válidos a la vez para las mismas condiciones.
2. **Todo camino a través de cajas de decisión debe llegar a una caja de estado.** No se puede volver de una decisión a otra decisión sin pasar por un estado (eso sería un lazo combinacional infinito). Si necesitas "esperar", el lazo debe regresar a la caja de estado, no al rombo.

```
  MAL (regla 2):               BIEN:
     ┌───────┐                    ┌──────────┐◄──┐
     │  S0   │                    │ S0       │   │
     └───┬───┘                    └────┬─────┘   │
    ┌───►◇ Inicio ◇                   ◇ Inicio ◇─0┘
    └─0──┘   │1                        │1
             ▼                         ▼
```

### 4.4 Equivalencia ASM ↔ diagrama de estados

- Cada caja de estado = un círculo del diagrama de estados.
- Cada camino de decisiones entre dos estados = una flecha etiquetada con la condición (`Inicio=1`, `α=0`).
- En Moore, dentro del círculo se escribe la salida: `PC1 & Final=0`.
- En Mealy, la salida va en la flecha: `β=1 / PC4`.

---

## 5. Moore vs Mealy en ASM

| | Moore ("basado en estados") | Mealy ("basado en entradas") |
|---|---|---|
| Salidas (palabra de control, Final) dependen de | Solo el estado actual | Estado actual **y** entradas/señales de estado |
| En el ASM | Solo cajas de estado y decisión | Hay cajas de asignación condicional |
| Número de estados | Mayor | Menor (varias acciones se "comprimen" en un estado) |
| ROM de salida | Direccionada solo por el estado: 2^(bits estado) | Direccionada por estado + condiciones que afectan la salida |
| Periodo de reloj | Más corto (la salida no espera a las condiciones) | Puede ser más largo: el camino crítico pasa por comparador → UC → CD |
| Ejemplo | Contador de unos: 6 estados | Contador de unos: 3 estados |

El libro llama a Moore **FSMD basado en estados** y a Mealy **FSMD basado en entradas**.

---

## 6. Metodología completa de diseño (lo que piden en el parcial)

Ésta es la secuencia que siguen el profesor, los talleres y el parcial. Apréndela en orden:

1. **Caja negra**: entradas, salidas y número de bits.
2. **Pseudoalgoritmo**: el cálculo paso a paso, con `Final = 0`, espera de `Inicio`, cálculo, salida y `Final = 1`.
3. **Diagrama ASM**: repartir las operaciones en estados **respetando**:
   - las dependencias de datos (una operación va después de las que producen sus operandos),
   - los **recursos disponibles** (si solo hay 1 multiplicador, máximo 1 multiplicación por estado),
   - las reglas del ASM.
4. **Tabla de tiempos de vida** de las variables y **asignación de registros** (mínimo número de registros: *left-edge*).
5. **Camino de datos**: registros + unidades funcionales + multiplexores en cada entrada que tenga más de una fuente + comparadores para las señales de estado + buffer de salida.
6. **Palabra de control**: listar todos los bits de control del CD y su valor en cada estado.
7. **Caja gris** (UC + CD con los anchos de bus).
8. **Unidad de control**: número de estados → bits de registro → tamaño de ROM de entrada y ROM de salida → **contenido** de ambas ROM (tabla de transiciones y tabla de palabras de control).

En el parcial te bajaron puntos justamente en los pasos 5 y 8: el CD quedó incompleto y no estaban descritos los contenidos de las ROM. En E5 está todo resuelto.

---

## 7. Componentes del camino de datos

### 7.1 Registro
Guarda n bits en el flanco de reloj. Señales típicas:
- **LD / we (write enable)**: si vale 1, en el flanco carga la entrada; si vale 0, conserva su valor.
- **clr**: lo pone en 0.

Si un registro se carga desde varias fuentes (un puerto, el sumador, el multiplicador…), necesita un **MUX a su entrada**.

En el Ejemplo 1 del profesor el registro es además de desplazamiento, con control `p q`: 00 = nada, 01 = desplazar a la derecha con `r` como bit de entrada, 10 = desplazar a la izquierda, 11 = guardar (cargar).

### 7.2 Multiplexor (MUX)
Selecciona una de N entradas. Necesita ⌈log₂ N⌉ bits de selección.
- 2 fuentes → MUX 2:1 → 1 bit
- 3 o 4 fuentes → MUX 4:1 → 2 bits
- 5 a 8 fuentes → MUX 8:1 → 3 bits

**Regla de diseño: cada entrada de registro y cada entrada de unidad funcional que reciba datos de más de una fuente lleva un MUX.** Si recibe de una sola fuente, va un cable directo.

### 7.3 ALU
Unidad que hace varias operaciones seleccionadas por bits de control. La ALU de las diapositivas usa `M s1 s0`:

| M s1 s0 | Operación | Truco de uso |
|---|---|---|
| 000 | NOT B | |
| 001 | A AND B | `0 AND B = 0` → sirve para **poner un registro en 0** |
| 010 | A OR B | `A OR 0 = A` → sirve para **pasar A sin cambios** |
| 011 | A XNOR B | |
| 100 | A + 1 | Incremento; con A=0 da la constante **1** |
| 101 | A + B | |
| 110 | A − B | También sirve para **comparar** (mirar signo o cero) |
| 111 | A − 1 | |

Estos trucos aparecen mucho: con una ALU no hace falta un MUX de "constante 0" o "constante 1" si se juega con las operaciones y con `enA = 0` / `enB = 0` (salidas del banco en cero).

### 7.4 Banco de registros
Un conjunto de 2^k registros con:
- **un puerto de escritura**: `dirw` (k bits) + `wr` (1 bit),
- **dos puertos de lectura**: `dirA` + `enA` y `dirB` + `enB`. Si `en = 0` la salida vale 0.

Ventaja: ahorra multiplexores (el direccionamiento hace de MUX). Restricción: **solo se escribe un registro por ciclo** y solo se leen dos. Esto limita cuántas operaciones caben en un estado.

Bits de control de un banco de 8 registros: `wr`(1) + `dirw`(3) + `enA`(1) + `dirA`(3) + `enB`(1) + `dirB`(3) = 12 bits.

### 7.5 Desplazador
`>> 1` (derecha) divide entre 2 (enteros sin signo). `<< 1` multiplica por 2. Un desplazador de "una posición" (como en el parcial) obliga a hacer `>> 2` en **dos estados**, o a usar dos desplazadores en cascada.

### 7.6 Buffer three-state
Conecta el resultado al puerto de salida solo cuando `h = 1`. Con `h = 0` la salida queda en alta impedancia. Se activa normalmente en el estado final, junto con `Final = 1`.

### 7.7 Comparadores (generan las señales de estado)
Bloques combinacionales: `= 0`, `= 10`, `≥`, `>`, bit menos significativo, bit de signo, overflow de la ALU. Cada pregunta de una caja de decisión que dependa de datos se convierte en un comparador y en **una señal de estado** de 1 bit hacia la UC.

### 7.8 Contadores/índices dedicados
Un registro con un sumador `+1` y un comparador (`i = 10`, `i ≥ n`). Los talleres los añadieron al CD como registros dedicados (`i`, `n`, `CONT`).

---

## 8. La palabra de control (PC)

La palabra de control es **el conjunto de todos los bits que la UC envía al CD**. Para construirla:

1. Recorre el CD y anota **cada** entrada de control: selectores de MUX, LD de cada registro, operación de la ALU, `wr`/direcciones del banco, control del desplazador, `h` del three-state.
2. Ordénalas en una tabla con un campo por señal. El número de bits total es la suma.
3. Para cada estado del ASM, llena una fila con los valores que hacen que el CD ejecute las asignaciones de ese estado.
4. Usa **X (no importa)** cuando el valor no afecta el resultado. Ojo: los **habilitadores de escritura nunca son X**. Si un registro no debe cambiar, su LD (o `wr`) tiene que valer **0**; si fuera X, podría sobrescribirse.
5. La señal `Final` normalmente se agrega a la salida de la ROM de salida junto con la PC (por eso en el Ejemplo 1: 8 bits de PC + Final = 9).

Ejemplo, el Ejemplo 1 del profesor (8 bits: `s | M s1 s0 | r p q | h`):

| Estado | s | M s1 s0 | r p q | h | Operación |
|---|---|---|---|---|---|
| PC0 | 0 | 001 (AND) | X 1 1 (guardar) | 0 | suma = 0 (0 AND R = 0) |
| PC1 | 1 | 101 (A+B) | X 1 1 (guardar) | 0 | suma = suma + x |
| PC2 | X | XXX | X 0 0 (nada) | 1 | resultado = suma |

En PC2 la diapositiva escribe "XXX" en el registro. Lo más seguro es `p q = 00` (nada) para que no cambie mientras se muestra el resultado.

---

## 9. La unidad de control: implementación canónica con ROMs

### 9.1 Estructura

```
  Inicio ─┐
  señales ┤
  estado  │     ┌───────────┐  próximo   ┌──────────┐  estado    ┌───────────┐
  (α,β..) └────►│ ROM DE    │──estado───►│ REGISTRO │──actual───►│ ROM DE    │──► PC (k bits)
           ┌───►│ ENTRADA   │  (n bits)  │ (n FF-D) │  (n bits)  │ SALIDA    │──► Final
           │    └───────────┘            └──────────┘     │      └───────────┘
           │                                 ▲   ▲        │
           │                                CLK RST       │
           └───────────── realimentación del estado ──────┘
```

- **Registro de estado**: n flip-flops D, con n = ⌈log₂(número de estados)⌉. RST lo lleva al estado inicial S0.
- **ROM de entrada** (lógica de próximo estado): dirección = estado actual + entradas de la UC; contenido = próximo estado.
- **ROM de salida** (lógica de salida): dirección = estado actual (Moore); contenido = PC + Final.

### 9.2 Fórmulas de dimensionamiento

Sea:
- E = número de estados → **n = ⌈log₂ E⌉** bits de estado
- c = número de entradas de la UC (Inicio + señales de estado + otras entradas externas)
- k = bits de la palabra de control, f = salidas externas de control (normalmente 1: Final)

| Bloque | Tamaño (palabras × bits) |
|---|---|
| Registro | n bits |
| ROM de entrada | **2^(n + c) × n** |
| ROM de salida (Moore) | **2^n × (k + f)** |
| ROM de salida (Mealy) | **2^(n + c') × (k + f)**, donde c' = condiciones que influyen en las salidas |

Comprobación con los ejemplos de clase:

| Diseño | E | n | c | ROM entrada | k+f | ROM salida |
|---|---|---|---|---|---|---|
| Σxᵢ (Ej. 1) | 3 | 2 | 2 (Inicio, α) | 2⁴ × 2 = **16 × 2** | 8+1 | 2² × 9 = **4 × 9** |
| Contador de unos (Ej. 2) | 8 | 3 | 2 (Inicio, α) | 2⁵ × 3 = **32 × 3** | 19+1 | 2³ × 20 = **8 × 20** |
| Contador de unos Moore (apuntes) | 6 | 3 | 3 (Inicio, α, β) | 2⁶ × 3 = **64 × 3** | 5+1 | 2³ × 6 = **8 × 6** |
| Contador de unos Mealy (apuntes) | 3 | 2 | 2 (Inicio, β) | 2⁴ × 2 = **16 × 2** | 5+1 | 2^(2+3) × 6 = **32 × 6** |
| Taller 6 (MSE) | 15 | 4 | 7 | 2¹¹ × 4 = **2048 × 4** | 18+1 | 2⁴ × 19 = **16 × 19** |
| Taller 5 (media ponderada) | 36 | 6 | 8 | 2¹⁴ × 6 = **16384 × 6** | 30+2 | 2⁶ × 32 = **64 × 32** |

En la versión Mealy de los apuntes, la ROM de salida recibe el estado (2 bits) más Inicio, α y β (3 bits) = 5 bits de dirección.

### 9.3 Cómo llenar las ROM (lo que te faltó en el parcial)

**ROM de entrada = tabla de transiciones.** Una fila por cada combinación (estado actual, entradas). Para no escribir 2^(n+c) filas, se agrupan con X las entradas que no importan en ese estado:

| Estado actual (Q) | Inicio | α | Próximo estado (D) |
|---|---|---|---|
| S0 = 00 | 0 | X | 00 |
| S0 = 00 | 1 | X | 01 |
| S1 = 01 | X | 0 | 01 |
| S1 = 01 | X | 1 | 10 |
| S2 = 10 | X | X | 00 |
| 11 (no usado) | X | X | 00 (o X) |

Llevar los códigos no usados a S0 es una buena práctica: si el circuito cae en un estado inválido, vuelve al inicio.

**ROM de salida = tabla de palabras de control.** Una fila por estado con todos los bits de la PC y Final (como la tabla de la sección 8).

### 9.4 Otras implementaciones de la UC (Gajski, problema 8.18)

- **Registro de estado + decodificador**: el estado se codifica en binario, un decodificador n→2ⁿ produce una línea por estado y las señales de control se forman con compuertas OR de esas líneas.
- **Contador + decodificador**: si la mayoría de transiciones son "pasar al siguiente estado", el registro de estado se cambia por un contador. Avanza con `+1` y solo carga una dirección nueva cuando hay un salto (decisión).
- **Microprogramada**: una ROM guarda **microinstrucciones**. Cada microinstrucción tiene la palabra de control + un campo de condición + una dirección de salto. Un contador de microprograma (μPC) indica la microinstrucción actual. La implementación con ROMs de clase es una forma de UC "cableada en ROM".
- **One-hot**: un flip-flop por estado. Usa más FF y menos lógica. Las herramientas de síntesis lo eligen a veces automáticamente; el Taller 5 reporta que ISE usó codificación Gray.


---

## 10. Optimización del camino de datos: tiempos de vida, *left-edge* y grafos

El objetivo es usar **el mínimo hardware**: pocos registros, pocas unidades funcionales y pocos multiplexores. Hay tres problemas de "compartir":

| Qué se comparte | Condición para compartir | Técnica |
|---|---|---|
| **Registros** entre variables | Sus tiempos de vida no se solapan | Tabla de tiempos de vida + *left-edge* |
| **Unidades funcionales** entre operaciones | Las operaciones están en estados distintos | Grafo de compatibilidad + partición en cliques |
| **Conexiones/buses** entre transferencias | Las transferencias ocurren en estados distintos | Grafo de compatibilidad de conexiones |

### 10.1 Tiempo de vida de una variable

Una variable está **viva** desde el estado siguiente a aquel en que se escribe hasta el último estado en que se lee.

- Se escribe en Sk → empieza a vivir en **Sk+1** (por la regla de la sección 2).
- Se lee por última vez en Sj → su vida termina en **Sj**.
- **Está viva en todos los estados intermedios, aunque no se use en ellos.** Debe "mantenerse viva" porque su valor tiene que seguir guardado hasta que se lea. Ésta es la anotación del profesor en tu primera tabla: *"las variables deben mantenerse vivas"*.

Se construye una tabla con las variables en filas, los estados en columnas y una X donde la variable está viva. Al pie se cuenta cuántas X hay por columna.

> **Número mínimo de registros = máximo número de variables vivas en un mismo estado** (la columna con más X, también llamada *densidad máxima*).

Dos variables pueden compartir registro si **no tienen ninguna columna en común**. Si una muere en Sj (se lee en Sj) y otra se escribe en Sj (nace en Sj+1), **sí** pueden compartir: en Sj se lee la vieja y al final de Sj se guarda la nueva.

Variables de salida: si el resultado se muestra en el último estado desde un registro, ese registro está vivo hasta ese estado.

### 10.2 Algoritmo *left-edge* (del lado izquierdo)

Asigna variables a registros con el número mínimo (igual a la densidad máxima) cuando los tiempos de vida son intervalos continuos:

1. Ordena las variables por **estado de inicio** (borde izquierdo) de menor a mayor.
2. Abre un registro nuevo. Recorre la lista en orden: mete la primera variable libre; luego mete cada variable siguiente cuyo inicio sea **mayor** que el final de la última variable metida en ese registro.
3. Quita de la lista las variables asignadas. Si quedan variables, vuelve al paso 2 con otro registro.

Ejemplo pequeño (estados 1 a 5):

| Var | Vida | | Orden por inicio: v1(1-2), v2(1-3), v3(3-4), v5(3-5), v4(4-5) |
|---|---|---|---|
| v1 | 1–2 | | R1: v1(1-2) → v3(3-4) → (v4 empieza en 4, choca) → fin. R1 = {v1, v3} |
| v2 | 1–3 | | R2: v2(1-3) → v4(4-5). R2 = {v2, v4} |
| v3 | 3–4 | | R3: v5(3-5). R3 = {v5} |
| v4 | 4–5 | | Densidad máxima (estado 3: v2, v3, v5) = 3 = registros usados ✓ |
| v5 | 3–5 | | |

### 10.3 Grafos de compatibilidad y de conflicto

- **Grafo de compatibilidad**: un nodo por variable (u operación, o conexión). Hay una arista entre dos nodos si **pueden compartir** recurso.
- **Grafo de conflicto**: lo contrario (complemento). Hay arista si **no pueden** compartir. Minimizar recursos = **colorear** el grafo de conflicto con el mínimo de colores (cada color es un registro o unidad).
- Para variables con vidas en intervalos, el grafo de conflicto es un *grafo de intervalos*, y *left-edge* da el óptimo.

**Pesos (prioridad).** A una arista de compatibilidad se le pone un peso que mide cuánto conviene juntar esos dos nodos: por ejemplo, el número de fuentes o destinos que comparten (si dos variables vienen siempre del mismo sumador, ponerlas en el mismo registro ahorra entradas de MUX). En el libro las aristas llevan pesos como `2/1` (dos números de prioridad); el procedimiento es el mismo sumando ambos o usando el primero como prioridad principal.

**Partición en cliques (agrupamiento)** – algoritmo voraz del libro:
1. Elige la arista de **mayor peso**.
2. Une sus dos nodos en un **supernodo**.
3. El supernodo solo conserva aristas hacia nodos que eran compatibles con **todos** sus miembros. El peso de la nueva arista es la **suma** de los pesos de las aristas hacia cada miembro.
4. Repite hasta que no queden aristas. Cada supernodo final es un registro (o una unidad funcional, o un bus).

Ejemplo con las variables de 10.2 (compatibles: v1–v3, v1–v4, v1–v5, v2–v4; pesos supuestos v1–v3 = 2, v2–v4 = 2, v1–v4 = 1, v1–v5 = 1):
- Mayor peso: v1–v3 (2) → supernodo {v1,v3}. ¿Compatible con v4? v3–v4 no → se pierde. ¿Con v5? v3–v5 no → se pierde.
- Siguiente: v2–v4 (2) → {v2,v4}.
- Queda v5 sola. Resultado: {v1,v3}, {v2,v4}, {v5} → 3 registros.

### 10.4 Compartir unidades funcionales

- Dos operaciones son compatibles si están en **estados distintos** y una misma unidad puede hacer ambas (por ejemplo, una ALU hace + y −).
- **Número mínimo de unidades de un tipo = máximo número de operaciones de ese tipo en un mismo estado.**
- Al asignar operaciones a una unidad, aprovecha la **conmutatividad** (a·b = b·a) para que cada entrada de la unidad reciba el menor número de fuentes distintas: así los MUX de entrada son más pequeños.

### 10.5 Compartir conexiones (buses)

Si dos transferencias ocurren en estados diferentes, pueden usar el mismo bus. Se arma el grafo de compatibilidad de conexiones y se particiona igual. Menos buses implican menos cables pero más MUX/three-states.

---

## 11. Planificación (*scheduling*)

Planificar es decidir **en qué estado (paso de control) va cada operación**. Se parte del **grafo de flujo de datos (DFG)**: un nodo por operación y una flecha de cada operación a las que usan su resultado.

### 11.1 ASAP (*As Soon As Possible*)
Cada operación va en el **primer** estado posible: un paso después de su última operación predecesora. Sin límite de recursos.
- Da el **mínimo número de estados** (la longitud del camino crítico).
- Suele concentrar muchas operaciones en los primeros estados (muchos recursos).

### 11.2 ALAP (*As Late As Possible*)
Fijado un número total de estados (normalmente el de ASAP), cada operación va en el **último** estado posible, de atrás hacia adelante.

### 11.3 Movilidad
**Movilidad = estado ALAP − estado ASAP.**
- Movilidad 0 → la operación está en el **camino crítico**: no se puede mover sin alargar el diseño.
- Movilidad > 0 → la operación tiene holgura y se puede mover para repartir recursos.

### 11.4 Planificación con restricción de tiempo (TC, *time-constrained*)
Se fija el número de estados y se busca el **mínimo de recursos**. Cada operación se coloca dentro de su ventana [ASAP, ALAP] intentando que en ningún estado se acumulen muchas del mismo tipo.

### 11.5 Planificación con restricción de recursos (RC, *resource-constrained*) – *list scheduling*
Se fija el número de unidades de cada tipo y se busca el **mínimo de estados**:
1. Estado actual = 1.
2. Lista de operaciones **listas** (todos sus predecesores ya terminaron en estados anteriores).
3. Ordénalas por **prioridad**: menor movilidad primero (o mayor longitud de camino hasta el final).
4. Asigna al estado actual tantas como unidades de cada tipo haya.
5. Pasa al siguiente estado y repite.

Esto es exactamente lo que tienes que hacer en el parcial cuando te dicen "dispone de una unidad de suma y otra de multiplicación": es un problema RC.

---

## 12. Encadenamiento y multiciclo

**Encadenamiento (*chaining*).** Poner dos operaciones **dependientes** en el mismo estado, conectando la salida de una unidad directamente a la entrada de la otra sin registro intermedio.
- Ventaja: menos estados.
- Costo: el periodo de reloj debe cubrir la suma de los dos retardos.
- Ejemplo: `t = (a + b) >> 1` en un estado si el desplazador está a la salida del sumador (como el desplazador después de la ALU en el Ejemplo 2 del profesor: ALU + desplazador se encadenan en un ciclo).

**Multiciclo.** Una operación lenta (multiplicación, por ejemplo) ocupa **dos o más** ciclos de reloj.
- Ventaja: el reloj se ajusta a las operaciones rápidas y es más corto.
- Costo: la unidad queda ocupada varios ciclos y sus entradas deben permanecer estables. En el ASM la operación se reparte en dos estados seguidos (en el primero se lanza, en el segundo se guarda el resultado).

Los dos son la misma idea vista al revés: decidir cuánto trabajo combinacional cabe en un periodo de reloj.

---

## 13. Segmentación (*pipelining*)

Segmentar es dividir un trabajo en **etapas** separadas por **registros de segmentación**, para que varias datos se procesen a la vez, cada uno en una etapa distinta. Funciona como una cadena de montaje.

### 13.1 Métricas

Para k etapas, retardo de la etapa más lenta t_max y retardo de registro t_reg:

- **Periodo de reloj**: T = t_max + t_reg (manda la etapa más lenta).
- **Latencia** (tiempo de un dato de entrada a salida): k · T.
- **Productividad (*throughput*)**: un resultado por ciclo, 1/T, una vez lleno el pipeline.
- **Tiempo para N datos**: (k + N − 1) · T.
- **Ganancia (*speedup*)** frente a la versión sin segmentar (que tarda t_total por dato):

  S = (N · t_total) / ((k + N − 1) · T)  → para N grande, S ≈ t_total / T ≤ k

Conclusiones que suelen preguntar:
- La ganancia ideal es **k** (el número de etapas) si todas las etapas duran igual y el registro no cuesta nada.
- **Las etapas desbalanceadas reducen la ganancia**: manda la más lenta.
- La segmentación **no reduce la latencia** (normalmente la aumenta un poco). Mejora la productividad.
- Más etapas no siempre ayudan: si el trabajo no se puede dividir más finamente, la etapa más lenta no baja.

### 13.2 Tres tipos de segmentación (Gajski)

1. **Unidades funcionales segmentadas.** Una unidad (por ejemplo, el multiplicador) se parte en etapas internas. Puede aceptar una operación nueva cada ciclo, pero el resultado sale **varios ciclos después**. En el ASM, una operación lanzada en Si tiene su resultado disponible en Si+etapas.
2. **Camino de datos segmentado.** Todo el algoritmo se divide en etapas, cada una con su propio hardware, y entre ellas hay registros. Entra un dato nuevo cada ciclo.
3. **Control segmentado.** Se ponen registros en la propia comunicación UC↔CD:
   - **Registro de estado** (entre las señales de estado del CD y la UC): la UC ve la condición **un ciclo tarde**. La decisión se toma con información atrasada; hay que añadir un estado de espera o reordenar operaciones.
   - **Registro de control** (entre la ROM de salida y el CD): el CD ejecuta la palabra de control **un ciclo después** de que la UC entra al estado.
   - Con ambos registros, la UC y el CD trabajan desfasados dos ciclos en las decisiones.
   - Ventaja: se corta el camino crítico UC → CD → UC y el reloj es más rápido.

---

## 14. Periodo de reloj y camino crítico

El periodo mínimo de reloj es el **retardo de registro a registro más largo** (*camino crítico*). En un FSMD hay tres tipos de caminos:

1. **Camino del CD**: registro → (lectura banco / MUX) → unidad funcional → MUX → entrada del registro.
2. **Camino de próximo estado**: registro de estado → ROM de entrada → registro de estado.
3. **Camino de estado** (cuando hay decisiones): registro del CD → comparador → ROM de entrada → registro de estado.

- **Moore (basado en estados):** las señales de control salen del registro de estado a través de la ROM de salida, así que el camino 1 empieza con el retardo de la ROM de salida:
  T ≥ máx( t_ROMsal + t_CD , t_comparador + t_ROMent ) + t_setup + t_clk→Q
- **Mealy (basado en entradas):** las señales de control dependen además de las señales de estado. El camino peor es: registro del CD → comparador → ROM de salida → MUX/unidad funcional del CD → registro. Por eso **Mealy suele tener periodo más largo**.

Los talleres reportan esto en ISE: Taller 6, periodo mínimo 7,952 ns (125,75 MHz), y el camino crítico estaba en el registro RESIDUO por la comparación `RESIDUO ≥ N` + resta. Es un camino tipo 1 + 3.

---

## 15. Técnicas algorítmicas de los talleres

Estas técnicas sirven cuando el enunciado **prohíbe** multiplicadores o divisores, o cuando solo hay un sumador/ALU.

**Multiplicación por sumas sucesivas** (A · B con B ≥ 0):
```
 P = 0 ; C = B
 mientras C > 0:  P = P + A ; C = C − 1
```
En el ASM es un estado que se repite en lazo con una decisión `C > 0` (señal de estado: comparador "C = 0").

**División por restas sucesivas** (cociente Q y residuo R de A / B):
```
 R = A ; Q = 0
 mientras R ≥ B:  R = R − B ; Q = Q + 1
```
Señal de estado: `R ≥ B` (comparador o bit de signo de R − B).

**Decimales** (Taller 5): tras la parte entera, multiplicar el residuo por 10 y volver a dividir: el cociente es el primer decimal. Repetir para el segundo.
**Punto fijo escalado** (Taller 6): multiplicar el numerador por 100 antes de dividir. El resultado entero representa el valor × 100 (400 → 4,00).

**Signo** (Taller 5): con datos en complemento a 2, revisar el bit más significativo. Si es 1, guardar `SIGNO = 1` y trabajar con el valor absoluto (complemento a 2: NOT + 1). Al final se muestra el signo aparte.

**Overflow**: cada suma que pueda desbordar se sigue de una decisión `OV`. Si OV = 1, saltar a un estado de error (salida = 0, LED de overflow). El Taller 6 compara además con 65535 (máximo de 16 bits).

**Cuadrado de un número** (Taller 6): |d| sumado |d| veces (sumas sucesivas sobre el valor absoluto).

**Coste**: estas técnicas cambian hardware por tiempo. Un estado de lazo se ejecuta muchas veces, así que el número de **estados** del ASM es pequeño pero el número de **ciclos** depende de los datos.


---

# PARTE II: EJERCICIOS RESUELTOS

## E1. Ejemplo 1 del profesor: f = Σ xᵢ (i = 1..10), CD preestablecido

**Enunciado.** Diseñar con UC+CD el cálculo de la suma de 10 datos de 16 bits que llegan por `Inport`. Empieza con `Inicio = 1`; el resultado se muestra solo al terminar (`Final = 1`).

**CD dado:** MUX (s: 1 = Inport, 0 = constante 0) → entrada A de la ALU; entrada B de la ALU ← salida del Registro R; ALU → Registro R (control r, p, q); contador i con +1 y comparador con 10 → α; three-state `h` → Outport.

**Paso 1 – Pseudoalgoritmo**
```
Final = 0
si Inicio = 1:
   suma = 0                      ← estado 0
   ciclo i = 1..10:
      suma = suma + x            ← estado 1 (se repite)
   resultado = suma; Final = 1   ← estado 2
```

**Paso 2 – Entradas y salidas de cada bloque**
- UC: entradas Inicio, α (i = 10); salidas Final, PC de 8 bits.
- CD: entradas Inport (16), PC (8); salidas Outport (16), α.

**Paso 3 – Palabra de control** (8 bits = s + M s1 s0 + r p q + h):

| PC | s | M s1 s0 | r p q | h | Qué hace el CD |
|---|---|---|---|---|---|
| PC0 | 0 | 001 (AND) | X 1 1 | 0 | A = 0 → 0 AND R = 0 → R = 0 (suma = 0) |
| PC1 | 1 | 101 (A+B) | X 1 1 | 0 | A = x, B = R → R = R + x |
| PC2 | X | XXX | X 0 0 | 1 | R se conserva y sale por Outport |

Por qué AND para poner a cero: el MUX con s = 0 entrega 0 a la entrada A, y `0 AND B = 0` sin importar lo que tenga R.

**Paso 4 – Diagrama de estados (Moore)**
```
         Inicio=0
          ┌──┐
          ▼  │
        ┌──────┐  Inicio=1   ┌──────┐  α=1   ┌──────┐
 RST──► │  s0  │ ──────────► │  s1  │ ─────► │  s2  │
        │PC0   │             │PC1   │        │PC2   │
        │Final=0│            │Final=0│       │Final=1│
        └──────┘             └──────┘        └──────┘
            ▲                  │  ▲              │
            │                  └──┘ α=0          │
            └────────────────────────────────────┘
```

Detalle que conviene comentar en un examen: en el CD de la diapositiva el contador `i` no tiene señales de control. En un diseño completo `i` debería ponerse a 1 (o 0) en s0 y avanzar solo en s1; si no, α no indicaría el dato 10 correcto. Si te preguntan cómo completarlo: agrega a `i` un MUX de "carga 1 / i+1" y un LD controlados por la UC (2 bits más en la PC).

**Paso 5 – Unidad de control**
- 3 estados → **n = 2 bits** de registro.
- ROM de entrada: entradas Inicio, α + 2 bits de estado = 4 → **2⁴ × 2 = 16 × 2**.
- ROM de salida: 2 bits de estado → 4 palabras de 8 + 1 (Final) → **4 × 9**.

Contenido de la ROM de entrada (dirección = Inicio α q1 q0):

| Inicio | α | q1 q0 (actual) | D1 D0 (próximo) |
|---|---|---|---|
| 0 | X | 00 (s0) | 00 |
| 1 | X | 00 (s0) | 01 |
| X | 0 | 01 (s1) | 01 |
| X | 1 | 01 (s1) | 10 |
| X | X | 10 (s2) | 00 |
| X | X | 11 | 00 (no usado) |

Contenido de la ROM de salida:

| q1 q0 | PC | Final |
|---|---|---|
| 00 | PC0 | 0 |
| 01 | PC1 | 0 |
| 10 | PC2 | 1 |
| 11 | X | X |

---

## E2. Ejemplo 2 del profesor: contador de unos con banco de registros

**Enunciado.** Contar cuántos 1 tiene una palabra de 16 bits que entra por Inport, y sacar el resultado por Outport con `Final = 1`.

**CD dado:** MUX (s: Inport / realimentación) → banco de 8 registros (dirw, wr, dirA, enA, dirB, enB) → salidas A y B → ALU (M s1 s0) → desplazador (p q: 00 pasar, 01 derecha, 10 izquierda, 11 nada) → realimentación al MUX y three-state h → Outport. Comparador `= 0` sobre la salida A → α.

**Pseudoalgoritmo** (registros: Dato = R2, cuenta = R1, aux = R3, Bls = R4)
```
Final = 0
si Inicio = 1:
 1  Dato = Inport
 2  cuenta = 0
 3  aux = 1
    mientras Dato ≠ 0:
 4     Bls = Dato AND aux        (aísla el bit menos significativo)
 5     cuenta = cuenta + Bls
 6     Dato = Dato >> 1
 7  Outport = cuenta ; Final = 1
```

**Traza con Dato = 100010:**

| Iteración | Dato | Dato AND aux | cuenta | Dato >> 1 |
|---|---|---|---|---|
| 1 | 100010 | 000000 | 0 | 010001 |
| 2 | 010001 | 000001 | 1 | 001000 |
| 3 | 001000 | 000000 | 1 | 000100 |
| 4 | 000100 | 000000 | 1 | 000010 |
| 5 | 000010 | 000000 | 1 | 000001 |
| 6 | 000001 | 000001 | 2 | 000000 |

Resultado: 2 ✓.

**Palabra de control** (19 bits: s 1, enA 1, dirA 3, enB 1, dirB 3, wr 1, dirw 3, M s1 s0 3, p q 2, h 1):

| Estado | s | enA | dirA | enB | dirB | wr | dirw | ALU | pq | h | Operación |
|---|---|---|---|---|---|---|---|---|---|---|---|
| s1 | 0 | X | XXX | X | XXX | 1 | 010 | XXX | XX | 0 | R2 ← Inport |
| s2 | 1 | 0 | XXX | 0 | XXX | 1 | 001 | OR 010 | 00 | 0 | R1 ← 0 OR 0 = 0 |
| s3 | 1 | 0 | XXX | X | XXX | 1 | 011 | INC 100 | 00 | 0 | R3 ← 0 + 1 = 1 |
| s4 | 1 | 1 | 010 | 1 | 011 | 1 | 100 | AND 001 | 00 | 0 | R4 ← R2 AND R3 |
| s5 | 1 | 1 | 001 | 1 | 100 | 1 | 001 | ADD 101 | 00 | 0 | R1 ← R1 + R4 |
| s6 | 1 | 1 | 010 | 0 | XXX | 1 | 010 | OR 010 | 01 | 0 | R2 ← (R2 OR 0) >> 1 |
| s7 | X | 1 | 001 | 0 | XXX | 0 | XXX | OR 010 | 00 | 1 | Outport ← R1 |

Trucos que usa el profesor:
- `enA = 0` y `enB = 0` hacen A = B = 0. Con OR da 0 (s2) y con INC da 1 (s3): **constantes sin MUX extra**.
- `A OR 0 = A` sirve para **pasar** un registro por la ALU (s6, s7).
- El desplazador está **encadenado** a la ALU: en s6 se lee, se pasa por la ALU y se desplaza en un solo ciclo.
- En s7 `wr = 0` (no se escribe nada). En s0 (PC0 = X) también debe ser `wr = 0` y `h = 0` para no dañar datos.

**Diagrama de estados:**
```
 s0 ─Inicio=1─► s1 ─► s2 ─► s3 ─► s4 ─► s5 ─► s6 ─α=1─► s7 ─► s0
 ▲└Inicio=0┘                      ▲             │
                                  └────α=0──────┘
```

**Detalle fino (sirve para una pregunta de análisis).** α se calcula sobre la **salida A** del banco. En s6 la salida A es R2 = Dato **antes** de desplazar. Por tanto la pregunta "¿Dato = 0?" se responde con el valor viejo y el lazo hace **una iteración de más** (con Dato = 0, Bls = 0 y cuenta no cambia). El resultado es correcto pero se gasta una vuelta extra. Si te piden optimizar, mira la pista del problema 8.2: el bit menos significativo de Dato está disponible a la salida de la ALU/desplazador, así que se puede ahorrar `aux` y `Bls`.

**UC:** 8 estados → 3 bits. ROM de entrada: Inicio + α + 3 = 5 bits → **32 × 3**. ROM de salida: **8 × 20** (19 PC + Final).

Filas de la ROM de entrada (Q2 Q1 Q0 = número de estado):

| Actual | Condición | Próximo |
|---|---|---|
| 000 (s0) | Inicio = 0 | 000 |
| 000 (s0) | Inicio = 1 | 001 |
| 001 → 010 → 011 → 100 → 101 → 110 | incondicional | siguiente |
| 110 (s6) | α = 0 | 100 (s4) |
| 110 (s6) | α = 1 | 111 (s7) |
| 111 (s7) | incondicional | 000 |

---

## E3. Contador de unos de los apuntes: Moore vs Mealy

Aquí el CD es **a la medida** (no preestablecido): registro Dato (16 bits) con MUX Inport/realimentación y desplazador `>>1`; registro Cuenta (5 bits) con MUX 0/realimentación y sumador +1; three-state a Salida. Señales de estado: **α = Dato_LSB** (bit menos significativo) y **β = (Dato = 0)**.

Palabra de control de 5 bits: ① sel MUX Dato, ② sel MUX Cuenta, ③ LD Dato, ④ LD Cuenta, ⑤ h.

¿Por qué Cuenta tiene 5 bits? El máximo de unos en 16 bits es 16 = 10000₂, que necesita 5 bits.

### Versión Moore (6 estados)
```
 S0: Final=0 ──Inicio=0──► S0
             ──Inicio=1──► S1
 S1: Dato=Inport, Cuenta=0 ─► S2
 S2: (evaluar α) ──α=1──► S3
                 ──α=0──► S4
 S3: Cuenta=Cuenta+1 ─► S4
 S4: Dato=Dato>>1 ──β=0 (Dato≠0)──► S2
                  ──β=1 (Dato=0)──► S5
 S5: Salida=Cuenta, Final=1 ─► S0
```
(En los apuntes β se dibuja como la pregunta "Dato = 0". Recuerda que en S4 la decisión ve el Dato **viejo**; como el lazo vuelve a S2 y vuelve a preguntar, el resultado es correcto y como mucho hay una vuelta extra.)

ROM de salida Moore:

| Estado | ① | ② | ③ | ④ | ⑤ | Final | Operación |
|---|---|---|---|---|---|---|---|
| 0 | X | X | 0 | 0 | 0 | 0 | nada |
| 1 | 0 | 0 | 1 | 1 | 0 | 0 | Dato = Inport, Cuenta = 0 |
| 2 | X | X | 0 | 0 | 0 | 0 | evaluar α |
| 3 | X | 1 | 0 | 1 | 0 | 0 | Cuenta = Cuenta + 1 |
| 4 | 1 | X | 1 | 0 | 0 | 0 | Dato = Dato >> 1 |
| 5 | X | X | 0 | 0 | 1 | 1 | Salida = Cuenta |

En la fila 1 fíjate en los selectores: en este CD la entrada 0 de cada MUX es Inport (para Dato) y la constante 0 (para Cuenta). Por eso sel Dato = 0 y sel Cuenta = 0, con ambos LD en 1. En tus apuntes esa casilla tiene un tachón; si lees un 1 en la primera columna, corrígelo a 0.

UC Moore: 6 estados → 3 bits; ROM entrada 2^(3+3) = **64 × 3** (Inicio, α, β); ROM salida 2³ × 6 = **8 × 6**.

### Versión Mealy (3 estados)
```
 S0: Final=0
     Inicio=0 → S0
     Inicio=1 → (Dato=Inport, Cuenta=0) → S1          [asignación condicional]
 S1: α=1 → (Cuenta=Cuenta+1)                         [asignación condicional]
     β=0 → (Dato=Dato>>1) → S1                        [asignación condicional]
     β=1 → S2
 S2: Salida=Cuenta, Final=1 → S0
```
Ahora la palabra de control depende del estado **y** de Inicio, α, β. Por eso hay 7 palabras distintas (PC0…PC6) con solo 3 estados:

| PC | Cuándo | Operación |
|---|---|---|
| PC0 | S0, Inicio = 0 | nada |
| PC1 | S0, Inicio = 1 | Dato = Inport, Cuenta = 0 |
| PC2 | S1, α = 0, β = 0 | Dato = Dato >> 1 |
| PC3 | S1, α = 1, β = 0 | Cuenta + 1 y Dato >> 1 (a la vez) |
| PC4 | S1, α = 0, β = 1 | nada |
| PC5 | S1, α = 1, β = 1 | Cuenta = Cuenta + 1 |
| PC6 | S2 | Salida = Cuenta, Final = 1 |

UC Mealy: 3 estados → 2 bits; ROM entrada: 2 + Inicio + β = 4 → **16 × 2**; ROM salida: 2 + Inicio + α + β = 5 → **32 × 6**. Observa que en el circuito de los apuntes α **solo** entra a la ROM de salida (no afecta el próximo estado) e Inicio y β entran a las dos.

**Conclusión para el examen:** Mealy reduce estados (y ciclos: hace dos operaciones por vuelta en S1) pero agranda la ROM de salida y alarga el camino crítico.

---

## E4. Lo que enseñan los Talleres 5 y 6 sobre dimensionamiento

**Taller 5 (media ponderada, CD preestablecido + bloques añadidos).**
- 36 estados (S0–S35, incluido el estado de error por overflow) → **6 bits**.
- Entradas de la UC: INICIO, ENTER, π, α, β, φ, OV_ALU, SIGNO = 8 → ROM de entrada **2¹⁴ × 6 = 16384 × 6**.
- PC de 30 bits + FINAL + OV_OUT = 32 → ROM de salida **2⁶ × 32 = 64 × 32**.
- La tabla de PC muestra el método: cada campo (S_MUX_IN 2 bits, wr, en_A, en_B, sel_dir, DIR_W/A/B 4 bits cada una, ALU_OP 3 bits, h, clr, we…) con un valor por estado. Mira cómo **los `wr`/`we` nunca son X**, mientras que direcciones y operaciones que no se usan sí lo son.
- Técnica destacada: el estado `S8: PRODUCTO ← PRODUCTO + X[i]` lee A con dirección de la UC y B con el índice `i` (`s_dA = 1`, `s_dB = 0`). Es decir, el banco se direcciona a veces por la UC y a veces por un registro índice, con un MUX de dirección.

**Taller 6 (error cuadrático medio, CD de alto nivel).**
- 15 estados → **4 bits**.
- 6 señales de estado + INICIO = 7 → ROM de entrada **2¹¹ × 4 = 2048 × 4**.
- ISE sintetizó una PC de 18 bits + FINAL → ROM de salida **16 × 19**. (En el informe aparece "2⁴ × 39" y luego "16 × XX"; el valor que corresponde a lo sintetizado es 16 × 19.)
- Técnica destacada: **un mismo estado se repite muchos ciclos** (lazos de sumas/restas sucesivas), así que pocos estados no significan pocos ciclos.

**Por qué la ROM de entrada crece tanto:** cada señal de estado duplica su tamaño. En la práctica muchas direcciones son "no importa"; por eso en el papel se escribe la tabla compacta con X, como en E1.


---

## E5. EL PARCIAL: Realimentación N°2 resuelta completa

### Enunciado

El ASM parcial de la Figura 1 aproxima

  **Out = (y² + eˣ) / 4**

con el algoritmo:

```
 a = in1, b = in2, x = in3, y = in4, Final = 0   (espera Inicio)
 t1 = x·x          (x²)
 t2 = 1 + x
 t3 = t1·x         (x³)
 t4 = a·t1         (a·x²)
 t5 = b·t3         (b·x³)
 t6 = t2 + t4      (1 + x + a·x²)
 t7 = t6 + t5      (1 + x + a·x² + b·x³)  ≈ eˣ
 t8 = y·y          (y²)
 t9 = t8 + t7      (y² + eˣ)
 out = t9 >> 2, Final = 1                    (÷ 4)
```

Es la serie de Taylor eˣ ≈ 1 + x + x²/2 + x³/6, con **a = 1/2** y **b = 1/6** como coeficientes de entrada (en hardware se representan en punto fijo).

**Recursos del CD:** 1 sumador, 1 multiplicador, 1 desplazador de **una** posición a la derecha.

**Piden:** (1) el ASM respetando los recursos, (2) el CD con registros mínimos, (3) el diseño y especificación de la UC.

### Qué pasó en tu solución (nota 3,4)

| Punto | Marca del profesor | Qué significa |
|---|---|---|
| 1. ASM | −0,2, "Hay opciones mejores a la planteada" | El ASM funciona pero usa más estados de los necesarios (ver abajo) |
| Tabla de vida (1ª versión) | "Las variables deben mantenerse vivas" | En el primer intento las variables tenían huecos o terminaban antes de su último uso |
| Tabla de vida (2ª versión) | "Corrección buena" | La segunda tabla es correcta: 6 registros |
| 2. CD | −0,8, "Incompleto" | Faltaban conexiones de las unidades, el desplazador, la salida y los selectores |
| 3. UC | "Falta describir transiciones y ROMs" | Diste tamaños, pero no el contenido de la ROM de entrada ni la de salida (ni la PC) |

### Paso 1: el DFG (dependencias) y el análisis de recursos

```
   x ──┬──► [×] t1 ──┬──► [×] t3 ──► [×] t5 ──┐
       │   (x·x)     │   (t1·x)    (b·t3)     │
       │             └──► [×] t4 ──┐          ▼
       │                 (a·t1)    ▼        [+] t7 ──┐
       └──► [+] t2 ───────────► [+] t6 ──►  (t6+t5)  ▼
           (1+x)                (t2+t4)            [+] t9 ─► [>>1] ─► [>>1] ─► out
   y ─────► [×] t8 ────────────────────────────────►(t8+t7)
           (y·y)
```

- Multiplicaciones: t1, t3, t4, t5, t8 = **5** → con 1 multiplicador hacen falta **al menos 5 estados de cálculo**.
- Sumas: t2, t6, t7, t9 = 4.
- Desplazamientos: 2 (÷4 con un desplazador de una posición = dos `>>1` seguidos, porque dependen uno del otro).

**¿Cuántos estados de cálculo como mínimo?** Después de la última multiplicación todavía hay que hacer cosas:
- Si la última es t5: faltan t7, t9, >>1, >>1 → 4 estados más → 9 en total.
- Si la última es t4: faltan t6, t7, t9, >>1, >>1 → 5 más → 10.
- Si la última es **t8**: faltan t9, >>1, >>1 → 3 más → **8 en total**.

Así que el mínimo con estos recursos es **8 estados de cálculo**, con t8 como última multiplicación. Planificación RC (list scheduling):

| Paso | Multiplicador | Sumador | Desplazador |
|---|---|---|---|
| 1 | t1 = x·x | t2 = 1 + x | – |
| 2 | t3 = t1·x | – | – |
| 3 | t4 = a·t1 | – | – |
| 4 | t5 = b·t3 | t6 = t2 + t4 | – |
| 5 | t8 = y·y | t7 = t6 + t5 | – |
| 6 | – | t9 = t8 + t7 | – |
| 7 | – | – | t9 = t9 >> 1 |
| 8 | – | – | out = t9 >> 1 |

Tu planificación de cálculo era exactamente ésta: S2…S9 con las mismas operaciones. **La parte de cálculo estaba bien.** El −0,2 viene de los estados que sobran alrededor.

### Paso 2: por qué "hay opciones mejores"

Tu ASM tenía 11 estados: S0 (Final=0, espera), S1 (carga a, b, x, y), S2–S9 (cálculo), S10 (out = t9, Final = 1). Dos mejoras:

1. **Cargar las entradas en el estado de espera.** Mira la Figura 1 del enunciado: la carga `a = in1 … y = in4, Final = 0` está **en la misma caja** que espera a Inicio. Mientras Inicio = 0, los registros se recargan en cada ciclo, y cuando llega Inicio = 1 ya tienen los datos. Te ahorras S1.
2. **Sacar el resultado en el último desplazamiento.** En vez de `S9: t9 = t9 >> 1` y `S10: out = t9`, el último estado lleva la salida del desplazador directamente al three-state: `out = t9 >> 1, Final = 1`. Es encadenar un desplazamiento con la salida (no hay que guardar nada). Te ahorras otro estado.

Resultado: **9 estados (S0–S8)** en vez de 11.

> Alternativa si tu profesor prefiere que `out` salga de un registro: deja `S8: t9 = t9 >> 1` y `S9: out = t9, Final = 1`. Son 10 estados y sigue siendo mejor que 11.

> Observación extra (para defender en un examen): si el enunciado garantiza que in1…in4 se mantienen estables durante todo el cálculo, a, b, x, y podrían leerse **directamente de los puertos** sin registros. Entonces el máximo de variables vivas baja a 3. Con el enunciado tal cual (los datos se cargan en registros), se usan registros.

### Paso 3: ASM corregido

```
              ┌────────────────────────────────────┐
     ┌───────►│ S0   Final = 0                     │◄──────────────────┐
     │        │      a←in1  b←in2  x←in3  y←in4    │                   │
     │        └─────────────────┬──────────────────┘                   │
     │                          ▼                                      │
     │      0              ◇  Inicio  ◇                                │
     └─────────────────────────┤                                       │
                               │ 1                                     │
                               ▼                                       │
                 ┌───────────────────────────┐                         │
                 │ S1   t1 ← x·x ; t2 ← 1+x  │                         │
                 └─────────────┬─────────────┘                         │
                 ┌─────────────▼─────────────┐                         │
                 │ S2   t3 ← t1·x            │                         │
                 └─────────────┬─────────────┘                         │
                 ┌─────────────▼─────────────┐                         │
                 │ S3   t4 ← a·t1            │                         │
                 └─────────────┬─────────────┘                         │
                 ┌─────────────▼─────────────┐                         │
                 │ S4   t5 ← b·t3 ; t6 ← t2+t4│                        │
                 └─────────────┬─────────────┘                         │
                 ┌─────────────▼─────────────┐                         │
                 │ S5   t8 ← y·y ; t7 ← t6+t5│                         │
                 └─────────────┬─────────────┘                         │
                 ┌─────────────▼─────────────┐                         │
                 │ S6   t9 ← t8 + t7         │                         │
                 └─────────────┬─────────────┘                         │
                 ┌─────────────▼─────────────┐                         │
                 │ S7   t9 ← t9 >> 1         │                         │
                 └─────────────┬─────────────┘                         │
                 ┌─────────────▼─────────────┐                         │
                 │ S8   out = t9 >> 1        │                         │
                 │      Final = 1            │─────────────────────────┘
                 └───────────────────────────┘
```

Especificaciones del ASM:
- Máquina **Moore** (no hay cajas de asignación condicional): 9 estados.
- Única decisión: Inicio (entrada externa). **No hay señales de estado del CD.**
- En cada estado: como máximo 1 multiplicación, 1 suma y 1 desplazamiento ✓ (respeta los recursos).

### Paso 4: tiempos de vida (estados S1…S8)

Regla: escrita en Sk → viva desde Sk+1 hasta su último uso, sin huecos.

| Variable | Se escribe en | Se lee en | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 |
|---|---|---|---|---|---|---|---|---|---|---|
| y | S0 | S5 | X | X | X | X | X | | | |
| b | S0 | S4 | X | X | X | X | | | | |
| a | S0 | S3 | X | X | X | | | | | |
| x | S0 | S1, S2 | X | X | | | | | | |
| t1 | S1 | S2, S3 | | X | X | | | | | |
| t2 | S1 | S4 | | X | X | X | | | | |
| t3 | S2 | S4 | | | X | X | | | | |
| t4 | S3 | S4 | | | | X | | | | |
| t5 | S4 | S5 | | | | | X | | | |
| t6 | S4 | S5 | | | | | X | | | |
| t7 | S5 | S6 | | | | | | X | | |
| t8 | S5 | S6 | | | | | | X | | |
| t9 | S6 | S7, S8 | | | | | | | X | X |
| **Vivas** | | | **4** | **6** | **6** | **5** | **3** | **2** | **1** | **1** |

**Máximo = 6 → 6 registros mínimos.** Es tu "Corrección buena" (tus columnas 2…10 son estas mismas desplazadas un estado, porque tu ASM tenía el estado de carga aparte).

Error típico de la primera versión: poner X solo en los estados donde la variable **se usa** (por ejemplo, y solo en S1 y S5). Así parece que caben en menos registros, pero y se perdería en S2–S4.

### Paso 5: asignación de registros con *left-edge*

Orden por inicio: y(1–5), b(1–4), a(1–3), x(1–2), t1(2–3), t2(2–4), t3(3–4), t4(4), t5(5), t6(5), t7(6), t8(6), t9(7–8).

| Registro | Construcción | Variables |
|---|---|---|
| R1 | y(1–5) → primera con inicio > 5: t7(6) → inicio > 6: t9(7–8) | **{y, t7, t9}** |
| R2 | b(1–4) → inicio > 4: t5(5) → inicio > 5: t8(6) | **{b, t5, t8}** |
| R3 | a(1–3) → inicio > 3: t4(4) → inicio > 4: t6(5) | **{a, t4, t6}** |
| R4 | x(1–2) → inicio > 2: t3(3–4) → ya no quedan con inicio > 4 | **{x, t3}** |
| R5 | t2(2–4) | **{t2}** |
| R6 | t1(2–3) | **{t1}** |

Coincide con tu asignación del parcial (R1 = {y, t7, t9}, R2 = {b, t5, t8}, R3 = {a, t4, t6}, R4 = {x, t3}, R5 = {t2}, R6 = {t1}). Fíjate en los casos "justos": en S3 se lee a (último uso) y se escribe t4 en el mismo R3; en S5 se lee t5 de R2 y se escribe t8 en R2. Ambos son válidos.

### Paso 6: transferencias entre registros (RTL) por estado

Sustituye cada variable por su registro:

| Estado | Operación | Transferencia |
|---|---|---|
| S0 | carga | R1 ← in4, R2 ← in2, R3 ← in1, R4 ← in3 |
| S1 | t1 = x·x ; t2 = 1 + x | R6 ← R4 × R4 ; R5 ← 1 + R4 |
| S2 | t3 = t1·x | R4 ← R4 × R6 |
| S3 | t4 = a·t1 | R3 ← R3 × R6 |
| S4 | t5 = b·t3 ; t6 = t2 + t4 | R2 ← R2 × R4 ; R3 ← R3 + R5 |
| S5 | t8 = y·y ; t7 = t6 + t5 | R2 ← R1 × R1 ; R1 ← R3 + R2 |
| S6 | t9 = t8 + t7 | R1 ← R1 + R2 |
| S7 | t9 = t9 >> 1 | R1 ← R1 >> 1 |
| S8 | out = t9 >> 1 | OUT = R1 >> 1 (three-state), Final = 1 |

Esta tabla es la que **te permite dibujar el CD sin olvidar conexiones**: cada flecha del CD corresponde a una celda de aquí.

### Paso 7: fuentes de cada entrada (para dimensionar los MUX)

Se usa la conmutatividad para elegir qué operando va a cada entrada y minimizar las fuentes:

| Entrada | Fuentes (estado) | Fuentes distintas | MUX |
|---|---|---|---|
| Multiplicador, entrada izquierda (ML) | R4 (S1, S2), R3 (S3), R2 (S4), R1 (S5) | 4 | 4:1 (2 bits) |
| Multiplicador, entrada derecha (MR) | R4 (S1, S4), R6 (S2, S3), R1 (S5) | 3 | 4:1 o 3:1 (2 bits) |
| Sumador, entrada izquierda (AL) | R4 (S1), R3 (S4, S5), R1 (S6) | 3 | 3:1 (2 bits) |
| Sumador, entrada derecha (AR) | constante 1 (S1), R5 (S4), R2 (S5, S6) | 3 | 3:1 (2 bits) |
| Desplazador | R1 (S7, S8) | 1 | cable directo |
| R1 | in4 (S0), ADD (S5, S6), SHR (S7) | 3 | 3:1 (2 bits) |
| R2 | in2 (S0), MUL (S4, S5) | 2 | 2:1 (1 bit) |
| R3 | in1 (S0), MUL (S3), ADD (S4) | 3 | 3:1 (2 bits) |
| R4 | in3 (S0), MUL (S2) | 2 | 2:1 (1 bit) |
| R5 | ADD (S1) | 1 | cable directo |
| R6 | MUL (S1) | 1 | cable directo |
| OUT | SHR (S8) | 1 | three-state con `h` |

Elección de operandos usada: S1 ML=R4, MR=R4 · S2 ML=R4, MR=R6 · S3 ML=R3, MR=R6 · S4 ML=R2, MR=R4 · S5 ML=R1, MR=R1. Sumador: S1 AL=R4, AR=1 · S4 AL=R3, AR=R5 · S5 AL=R3, AR=R2 · S6 AL=R1, AR=R2.

### Paso 8: camino de datos completo

```
 ── REGISTROS ───────────────────────────────────────────────────────────────────────

    in4  ADD  SHR      in2  MUL      in1  MUL  ADD      in3  MUL       ADD      MUL
     │    │    │        │    │        │    │    │        │    │         │        │
    ┌┴────┴────┴┐      ┌┴────┴┐      ┌┴────┴────┴┐      ┌┴────┴┐        │        │
 s1►│ MUX_R1    │  s2►│MUX_R2│   s3►│ MUX_R3    │  s4►│MUX_R4│        │        │
    │ 00 01 10  │      │ 0  1 │      │ 00 01 10  │      │ 0  1 │        │        │
    └─────┬─────┘      └──┬───┘      └─────┬─────┘      └──┬───┘        │        │
       ┌──┴──┐         ┌──┴──┐          ┌──┴──┐         ┌──┴──┐     ┌──┴──┐  ┌──┴──┐
 LD1──►│ R1  │  LD2───►│ R2  │   LD3───►│ R3  │  LD4───►│ R4  │LD5─►│ R5  │LD6►│ R6 │
       │y t7 │         │b t5 │          │a t4 │         │x t3 │     │ t2  │  │ t1  │
       │ t9  │         │ t8  │          │ t6  │         │     │     │     │  │     │
       └──┬──┘         └──┬──┘          └──┬──┘         └──┬──┘     └──┬──┘  └──┬──┘
          │R1             │R2              │R3             │R4          │R5      │R6
          ▼               ▼                ▼               ▼            ▼        ▼
      (todas las salidas van a los buses que alimentan los MUX de abajo)

 ── UNIDADES FUNCIONALES ────────────────────────────────────────────────────────────

    R1  R2  R3  R4        R1  R4  R6            R1  R3  R4       "1" R2  R5
    │   │   │   │         │   │   │             │   │   │         │   │   │
   ┌┴───┴───┴───┴┐       ┌┴───┴───┴┐           ┌┴───┴───┴┐       ┌┴───┴───┴┐
ml►│   MUX_ML    │   mr►│ MUX_MR  │        al►│ MUX_AL  │   ar►│ MUX_AR  │
   │ 00 01 10 11 │       │ 00 01 10│           │ 00 01 10│       │ 00 01 10│
   └──────┬──────┘       └────┬────┘           └────┬────┘       └────┬────┘
          └────────┐   ┌──────┘                     └───────┐  ┌──────┘
                 ┌─┴───┴─┐                                ┌─┴──┴─┐
                 │   ×   │──────► MUL                     │  +   │──────► ADD
                 └───────┘  (a R2, R3, R4, R6)            └──────┘  (a R1, R3, R5)

          R1 ──►┌───────┐──────► SHR (a R1)
                │  >>1  │
                └───────┘──────►──┤▷├──────► OUT
                                    ▲
                                    h
```

Lista de componentes (lo que faltaba en tu CD):
- 6 registros de n bits con carga (LD1…LD6).
- 1 multiplicador, 1 sumador, 1 desplazador >>1.
- MUX: R1 (3:1), R2 (2:1), R3 (3:1), R4 (2:1), ML (4:1), MR (3:1), AL (3:1), AR (3:1 con la constante 1).
- 1 buffer three-state en la salida (h).
- 0 señales de estado (no hay decisiones sobre datos).

Ancho de palabra: n bits según el enunciado. Como a = 1/2 y b = 1/6, los datos van en **punto fijo**; el producto de dos números de n bits ocupa 2n bits y hay que reescalarlo (tomar los bits correctos). Basta con mencionarlo como especificación.

### Paso 9: palabra de control

Campos (21 bits):

| Campo | Bits | Codificación |
|---|---|---|
| s1 (MUX_R1) | 2 | 00 = in4, 01 = ADD, 10 = SHR |
| LD1 | 1 | carga R1 |
| s2 (MUX_R2) | 1 | 0 = in2, 1 = MUL |
| LD2 | 1 | |
| s3 (MUX_R3) | 2 | 00 = in1, 01 = MUL, 10 = ADD |
| LD3 | 1 | |
| s4 (MUX_R4) | 1 | 0 = in3, 1 = MUL |
| LD4 | 1 | |
| LD5 | 1 | |
| LD6 | 1 | |
| ml (MUX_ML) | 2 | 00 = R1, 01 = R2, 10 = R3, 11 = R4 |
| mr (MUX_MR) | 2 | 00 = R1, 01 = R4, 10 = R6 |
| al (MUX_AL) | 2 | 00 = R1, 01 = R3, 10 = R4 |
| ar (MUX_AR) | 2 | 00 = "1", 01 = R2, 10 = R5 |
| h | 1 | habilita OUT |
| **Total** | **21** | + Final = 22 bits en la ROM de salida |

Valores por estado:

| Estado | s1 | LD1 | s2 | LD2 | s3 | LD3 | s4 | LD4 | LD5 | LD6 | ml | mr | al | ar | h | Final |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S0 | 00 | 1 | 0 | 1 | 00 | 1 | 0 | 1 | 0 | 0 | XX | XX | XX | XX | 0 | 0 |
| S1 | XX | 0 | X | 0 | XX | 0 | X | 0 | 1 | 1 | 11 | 01 | 10 | 00 | 0 | 0 |
| S2 | XX | 0 | X | 0 | XX | 0 | 1 | 1 | 0 | 0 | 11 | 10 | XX | XX | 0 | 0 |
| S3 | XX | 0 | X | 0 | 01 | 1 | X | 0 | 0 | 0 | 10 | 10 | XX | XX | 0 | 0 |
| S4 | XX | 0 | 1 | 1 | 10 | 1 | X | 0 | 0 | 0 | 01 | 01 | 01 | 10 | 0 | 0 |
| S5 | 01 | 1 | 1 | 1 | XX | 0 | X | 0 | 0 | 0 | 00 | 00 | 01 | 01 | 0 | 0 |
| S6 | 01 | 1 | X | 0 | XX | 0 | X | 0 | 0 | 0 | XX | XX | 00 | 01 | 0 | 0 |
| S7 | 10 | 1 | X | 0 | XX | 0 | X | 0 | 0 | 0 | XX | XX | XX | XX | 0 | 0 |
| S8 | XX | 0 | X | 0 | XX | 0 | X | 0 | 0 | 0 | XX | XX | XX | XX | 1 | 1 |

Comprobación de un estado, S4: `t5 = b·t3` → ml = 01 (R2 = b), mr = 01 (R4 = t3), resultado MUL → R2 (s2 = 1, LD2 = 1). `t6 = t2 + t4` → al = 01 (R3 = t4), ar = 10 (R5 = t2), resultado ADD → R3 (s3 = 10, LD3 = 1). Los demás LD en 0 ✓.

### Paso 10: caja negra y caja gris

```
 Caja negra:                                Caja gris:
                                              Inicio                in1 in2 in3 in4
 Inicio ─►┌────────────┐                        │                     │   │   │   │
  in1 ─/n►│            │──► Final               ▼        PC           ▼   ▼   ▼   ▼
  in2 ─/n►│  Ecuación  │                     ┌──────┐ ────/21────►  ┌──────────────┐
  in3 ─/n►│            │──/n─► Out           │  UC  │               │      CD      │──/n─► Out
  in4 ─/n►│            │                     └──────┘  (0 señales   └──────────────┘
  CLK ───►│            │                       │  ▲ ▲   de estado)        ▲   ▲
  RST ───►└────────────┘                     Final CLK RST               CLK RST
```

### Paso 11: unidad de control (lo que te faltó)

**Dimensionamiento:**
- 9 estados → **n = 4 bits** (registro de 4 flip-flops D). Códigos S0 = 0000 … S8 = 1000; 1001–1111 no usados.
- Entradas de la UC: solo Inicio (c = 1). ROM de entrada: 2^(4+1) × 4 = **32 × 4**.
- ROM de salida (Moore): 2⁴ × (21 + 1) = **16 × 22**.

```
            ┌──────────────┐   D3..D0  ┌────────────┐  Q3..Q0   ┌──────────────┐
 Inicio ───►│ ROM ENTRADA  │──────────►│ REGISTRO   │──────────►│ ROM SALIDA   │──/21─► PC
        ┌──►│   32 × 4     │   4 bits  │  4 bits    │  4 bits   │   16 × 22    │──────► Final
        │   └──────────────┘           └────────────┘    │      └──────────────┘
        │                                 ▲     ▲        │
        │                                CLK   RST       │
        └──────────── Q3..Q0 (realimentación) ───────────┘
```

**Contenido de la ROM de entrada (tabla de transiciones):**

| Q3 Q2 Q1 Q0 (actual) | Inicio | D3 D2 D1 D0 (próximo) |
|---|---|---|
| 0000 (S0) | 0 | 0000 (S0) |
| 0000 (S0) | 1 | 0001 (S1) |
| 0001 (S1) | X | 0010 (S2) |
| 0010 (S2) | X | 0011 (S3) |
| 0011 (S3) | X | 0100 (S4) |
| 0100 (S4) | X | 0101 (S5) |
| 0101 (S5) | X | 0110 (S6) |
| 0110 (S6) | X | 0111 (S7) |
| 0111 (S7) | X | 1000 (S8) |
| 1000 (S8) | X | 0000 (S0) |
| 1001 … 1111 | X | 0000 (vuelta segura a S0) |

Como la dirección tiene 5 bits, la ROM tiene 32 posiciones. Cada fila con "X" en Inicio ocupa dos posiciones con el mismo contenido.

**Contenido de la ROM de salida:** es la tabla del Paso 9 (una fila de 22 bits por estado). Las direcciones 1001–1111 se llenan con todos los LD = 0, h = 0, Final = 0 (no hacer nada).

**Diagrama de estados equivalente:**
```
         Inicio=0
          ┌──┐
          ▼  │
 RST ──► (S0) ──Inicio=1──► (S1) ─► (S2) ─► (S3) ─► (S4) ─► (S5) ─► (S6) ─► (S7) ─► (S8)
          ▲                                                                           │
          └───────────────────────────────────────────────────────────────────────────┘
   Moore: en cada círculo va su PC; Final = 1 solo en S8.
```

Como casi todas las transiciones son "pasar al siguiente", otra UC válida (y más barata) es **un contador de 4 bits + decodificador**: el contador se queda en 0 mientras Inicio = 0, cuenta en S1…S7 y se reinicia en S8. Puedes mencionarlo como alternativa.

### Resumen de cómo debiste responder (lista de chequeo del parcial)

1. ASM con recursos: 1 multiplicación, 1 suma y 1 desplazamiento máximo por estado; carga en el estado de espera; ÷4 = dos `>>1`.
2. Tabla de tiempos de vida **sin huecos** → máximo 6 → 6 registros.
3. *Left-edge* → R1…R6.
4. Tabla RTL por estado (registro ← unidad(registro, registro)).
5. Tabla de fuentes → MUX de cada entrada.
6. CD dibujado con **todas** las unidades (incluido el desplazador y el three-state) y los nombres de las señales de control.
7. Palabra de control: campos, bits y tabla por estado.
8. UC: bits de estado, tamaños de ROM y **contenido** de las dos ROM.


---

## E6. Problema 8.10: asignar t1…t8 al mínimo de registros con *left-edge*

Tiempos de vida leídos de la Figura P8.10 (estados s0…s7):

| Var | s0 | s1 | s2 | s3 | s4 | s5 | s6 | s7 | Intervalo |
|---|---|---|---|---|---|---|---|---|---|
| t1 | X | X | X | X | | | | | 0–3 |
| t2 | X | X | X | | | | | | 0–2 |
| t3 | | X | X | X | X | | | | 1–4 |
| t4 | | | | X | X | | | | 3–4 |
| t5 | | | | | X | X | X | | 4–6 |
| t6 | | | | | X | X | | | 4–5 |
| t7 | | | | | | X | X | | 5–6 |
| t8 | | | | | | | X | X | 6–7 |
| **Vivas** | 2 | 3 | 3 | 3 | **4** | 3 | 3 | 1 | |

(Si en tu copia del libro t3 empieza en otra columna, el procedimiento es el mismo; solo cambia la tabla.)

**Mínimo teórico: 4 registros** (columna s4: t3, t4, t5, t6).

*Left-edge* con el orden t1(0–3), t2(0–2), t3(1–4), t4(3–4), t5(4–6), t6(4–5), t7(5–6), t8(6–7):

| Registro | Construcción | Resultado |
|---|---|---|
| R1 | t1(0–3) → inicio > 3: t5(4–6) → inicio > 6: ninguna (t8 empieza en 6 y choca) | {t1, t5} |
| R2 | t2(0–2) → inicio > 2: t4(3–4) → inicio > 4: t7(5–6) → inicio > 6: ninguna | {t2, t4, t7} |
| R3 | t3(1–4) → inicio > 4: t8(6–7) | {t3, t8} |
| R4 | t6(4–5) | {t6} |

4 registros = densidad máxima → **óptimo** ✓.

---

## E7. Problemas 8.20–8.22: planificación del lazo de la ecuación diferencial (8.7)

Cuerpo del lazo:
```
 x1 = x + dx
 u1 = u − 3·x·u·dx − 3·y·dx
 y1 = y + u·dx
 condición: x1 < a
```

**Operaciones** (reutilizando u·dx, que aparece dos veces):

| Op | Cálculo | Tipo | Depende de |
|---|---|---|---|
| m1 | 3·x | × | – |
| m2 | u·dx | × | – |
| m3 | m1·m2 (3x·u·dx) | × | m1, m2 |
| m4 | 3·y | × | – |
| m5 | m4·dx (3y·dx) | × | m4 |
| s1 | u − m3 | − | m3 |
| s2 | s1 − m5 (= u1) | − | s1, m5 |
| a1 | x + dx (= x1) | + | – |
| a2 | y + m2 (= y1) | + | m2 |
| c | x1 < a | comparación (resta) | a1 |

(El ejemplo clásico de la literatura cuenta u·dx dos veces y tiene 6 multiplicaciones; si tu profesor lo plantea así, añade m6 = u·dx con las mismas ventanas que m2.)

**8.20 (a) ASAP:**

| Paso | Operaciones |
|---|---|
| 1 | m1, m2, m4, a1 |
| 2 | m3, m5, a2, c |
| 3 | s1 |
| 4 | s2 |

Camino crítico: m1/m2 → m3 → s1 → s2 = **4 pasos**.

**8.20 (b) ALAP (con 4 pasos):**

| Paso | Operaciones |
|---|---|
| 1 | m1, m2 |
| 2 | m3, m4 |
| 3 | s1, m5, a1 |
| 4 | s2, a2, c |

**Movilidad (ALAP − ASAP):** m1 = 0, m2 = 0, m3 = 0, s1 = 0, s2 = 0 (camino crítico); m4 = 1, m5 = 1; a1 = 2, a2 = 2, c = 2.

**8.21 Planificación TC (mínimos recursos para un número de estados dado)** (ALU = sumador/restador que también compara):

| Estados | Planificación | Recursos |
|---|---|---|
| 4 | 1: m1, m2, a1 · 2: m3, m4, c · 3: m5, s1 · 4: s2, a2 | 2 ×, 2 ALU |
| 5 | 1: m1, m2, a1 · 2: m3, m4, c · 3: m5, s1 · 4: s2 · 5: a2 | 2 ×, 1 ALU |
| 6 | 1: m1, a1 · 2: m2, c · 3: m3, a2 · 4: m4, s1 · 5: m5 · 6: s2 | 1 ×, 1 ALU |

Por qué 4 estados necesitan 2 ALU: hay 5 operaciones de ALU (a1, a2, c, s1, s2) y solo 4 pasos, así que algún paso lleva dos.
Por qué 5 estados no alcanzan con 1 multiplicador: las 5 multiplicaciones ocuparían los pasos 1–5, y después de la última (m3 o m5) aún falta al menos una resta → 6 pasos.

**8.22 Planificación RC (mínimos estados con recursos dados)** con *list scheduling* por movilidad:

| Recursos | Planificación | Estados |
|---|---|---|
| (a) 3 ×, 2 ALU | 1: m1, m2, m4, a1 · 2: m3, m5, a2, c · 3: s1 · 4: s2 | 4 |
| (b) 2 ×, 2 ALU | 1: m1, m2, a1 · 2: m3, m4, c, a2 · 3: m5, s1 · 4: s2 | 4 |
| (c) 2 ×, 1 ALU | 1: m1, m2, a1 · 2: m3, m4, c · 3: m5, s1 · 4: s2 · 5: a2 | 5 |

En (c), en el paso 2 compiten c y a2 por la única ALU; se elige cualquiera (misma movilidad) y en el paso 3 gana s1 por tener movilidad 0. Con (a) sobra un multiplicador: (b) consigue lo mismo con menos hardware.

---

## E8. Algoritmo SRA (aproximación de raíz cuadrada) y segmentación (8.15)

El ejemplo del libro aproxima √(a² + b²) ≈ máx(0,875·x + 0,5·y, x), con x = máx(|a|, |b|) e y = mín(|a|, |b|). Como 0,875·x = x − x/8:

| Op | Cálculo |
|---|---|
| o1 | t1 = \|a\| |
| o2 | t2 = \|b\| |
| o3 | x = máx(t1, t2) |
| o4 | y = mín(t1, t2) |
| o5 | t3 = x >> 3 |
| o6 | t4 = y >> 1 |
| o7 | t5 = x − t3 |
| o8 | t6 = t4 + t5 |
| o9 | t7 = máx(t6, x) |

**ASAP:** 1: o1, o2 · 2: o3, o4 · 3: o5, o6 · 4: o7 · 5: o8 · 6: o9 → 6 pasos.
**ALAP (6 pasos):** 1: o1, o2 · 2: o3 · 3: o4, o5 · 4: o6, o7 · 5: o8 · 6: o9.
Movilidad 1 para o4 y o6; las demás están en el camino crítico.

**8.15 (a) Camino de datos segmentado en 3 etapas** (dos pasos encadenados por etapa):

```
  a,b ─► [ |a| |b| ] ─► [máx][mín] ─║─► [>>3][>>1] ─► [ − ] ─║─► [ + ] ─► [máx] ─► SRA
         └──────── Etapa 1 ────────┘ └─────── Etapa 2 ──────┘ └───── Etapa 3 ─────┘
                                   reg: x, y              reg: x, t4, t5
```

- Cada etapa encadena 2 operaciones → retardo ≈ 2τ (τ = retardo de una operación).
- Sin segmentar (FSMD de 6 estados, reloj τ): 6τ por resultado.
- Segmentado: un resultado cada 2τ (más el retardo del registro).
- **Ganancia para muchos datos ≈ 6τ / 2τ = 3.** Latencia: 3 · 2τ = 6τ (igual o un poco peor).
- Para N datos: tiempo = (3 + N − 1) · 2τ. Con N = 100: 204τ frente a 600τ → 2,94.

**8.15 (b) 4 etapas:** el camino crítico tiene 6 operaciones en serie; repartidas en 4 etapas quedan, por ejemplo, 2-2-1-1. La etapa más lenta sigue durando 2τ, así que **la ganancia sigue siendo ≈ 3** y se gastan más registros y más latencia (4 · 2τ = 8τ). Solo mejoraría si las operaciones tuvieran retardos distintos y se pudiera balancear mejor. Ésta es la idea clave: **la ganancia la fija la etapa más lenta.**

**8.14 (unidades segmentadas), idea general:** si la unidad [abs/mín/máx] tiene 2 etapas, el resultado de una operación lanzada en el paso i está listo en i + 2. En el ASM, las operaciones que dependen de ella se corren un paso, pero la unidad puede aceptar otra operación en i + 1. Se dibuja un diagrama de tiempos con una fila por etapa de cada unidad y se van colocando las operaciones.

---

## E9. Problemas 8.4, 8.5 y 8.8: diagramas ASM

### 8.4 Contador de décadas con salidas L5, E5, G5

Cuenta 0…9 cíclicamente. L5 = 1 si cuenta < 5, E5 = 1 si cuenta = 5, G5 = 1 si cuenta > 5.

Versión basada en entradas (Mealy, 2 estados):
```
 S0: cuenta ← 0 ─────────────────────────────► S1
 S1: (caja vacía)
       ◇ cuenta < 5 ◇ ─1─► (L5 = 1)
             │0
       ◇ cuenta = 5 ◇ ─1─► (E5 = 1)
             │0
           (G5 = 1)
       ── luego, en el mismo bloque ──
       ◇ cuenta = 9 ◇ ─1─► (cuenta ← 0) ──► S1
             │0
       (cuenta ← cuenta + 1) ─────────────► S1
```
CD: registro de 4 bits, sumador +1, MUX (0 / cuenta+1), comparadores <5, =5, =9.
Versión Moore: 10 estados (uno por valor), con L5/E5/G5 escritos dentro de cada caja de estado. Es el ejemplo clásico de "Moore: más estados, salidas solo del estado".

### 8.5 Contador módulo 4 (rango = 0) o módulo 7 (rango = 1)
```
 S0: cuenta ← 0 ──► S1
 S1: salida = cuenta
     ◇ rango ◇
       0 │                       1 │
     ◇ cuenta ≥ 3 ◇            ◇ cuenta ≥ 6 ◇
      1│      │0                1│      │0
  (cuenta←0) (cuenta←cuenta+1) (cuenta←0) (cuenta←cuenta+1)
      └──────┴──────── ► S1 ◄──┴──────┘
```
Se usa **≥** en vez de = para que, si rango cambia de 1 a 0 con cuenta = 5, el contador vuelva a 0 y no se salga del rango.

### 8.8 Multiplicador de desplazamiento y suma

Multiplica MD × MR (n bits). PP es el producto parcial (parte alta), y MR se va desplazando y termina guardando la parte baja.

```
 S0: Final = 0 ; MD ← inport1 ; MR ← inport2        ◇Inicio◇ ─0─► S0
                                                         │1
 S1: PP ← 0 ; cont ← n
 S2: ◇ MR₀ ◇ ─1─► (PP ← PP + MD)                    [asignación condicional]
          │0
 S3: {C, PP, MR} ← {C, PP, MR} >> 1 ; cont ← cont − 1
     ◇ cont = 0 ◇ ─0─► S2
          │1
 S4: salida = {PP, MR} ; Final = 1 ──► S0
```
Señales de estado: MR₀ (LSB del multiplicador) y (cont = 0).

Traza 5 × 3 con 4 bits (MD = 0101, MR = 0011):

| Iteración | MR₀ | PP después de sumar | Tras desplazar: PP, MR |
|---|---|---|---|
| inicio | | 0000 | 0000, 0011 |
| 1 | 1 | 0101 | 0010, 1001 |
| 2 | 1 | 0111 | 0011, 1100 |
| 3 | 0 | 0011 | 0001, 0110 |
| 4 | 0 | 0001 | 0000, 1011 |

Resultado {PP, MR} = 0000 1111 = 15 ✓.

---

## E10. Problema 8.11: partición del grafo de compatibilidad

No se puede resolver número por número sin leer bien los pesos de la Figura P8.11, pero el procedimiento que se evalúa es siempre el mismo:

1. Lista todas las aristas con su peso. Si la arista tiene dos números (por ejemplo, 2/1), usa la regla que dé tu profesor; lo habitual es usar el primero como prioridad y el segundo para desempatar, o sumar ambos.
2. Toma la arista de **mayor peso** y une sus nodos en un supernodo.
3. Borra las aristas del supernodo hacia nodos que no sean compatibles con **todos** sus miembros (en la figura, las aristas punteadas suelen indicar incompatibilidad).
4. Para los nodos que sí son compatibles con todos, la nueva arista pesa la **suma** de las aristas hacia cada miembro (lo dice el enunciado: "el peso de un arco prioritario a un supernodo es igual a los pesos de los arcos a cada uno de los nodos del supernodo").
5. Repite hasta que no queden aristas. Número de supernodos = número de recursos.

Ejemplo resuelto con 4 nodos A, B, C, D y aristas de compatibilidad A–B (3), A–C (1), B–C (2), C–D (2), B–D (1). A y D son incompatibles (no hay arista A–D):
- Mayor peso A–B (3) → {A,B}. C es compatible con A y con B → arista {A,B}–C con peso 1 + 2 = 3. D no es compatible con A → se elimina la arista hacia D.
- Mayor peso {A,B}–C (3) → {A,B,C}. D no es compatible con A → no hay más aristas con D.
- Resultado: {A, B, C} y {D} → 2 recursos.

---

## E11. Problema 8.16: control segmentado (diagrama de tiempos)

Con el contador de unos (estado del lazo: `Dato ← Dato >> 1` y decisión β = (Dato = 0)):

**Sin registros de segmentación:** en el ciclo k la UC está en el estado, el CD calcula y β llega a la UC en el mismo ciclo. La decisión se toma al final del ciclo k.

**(a) Con registro de estado** (β pasa por un flip-flop antes de llegar a la UC):

| Ciclo | k | k+1 | k+2 |
|---|---|---|---|
| UC | S4 (Dato>>1) | estado de espera | decide con β |
| CD | calcula, β → registro | β disponible | – |

La decisión llega un ciclo tarde: hay que meter un estado de espera o adelantar la operación que produce β.

**(b) Con registro de control** (la PC pasa por un registro antes de llegar al CD): la palabra de control de un estado se ejecuta en el ciclo **siguiente**. El CD va un ciclo detrás de la UC, y las decisiones que dependen de un resultado se retrasan también un ciclo.

**(c) Con ambos:** el lazo UC → CD → UC tarda dos ciclos más. El reloj puede ser más rápido (cada camino es más corto), pero cada decisión cuesta ciclos extra. Es el mismo compromiso de cualquier segmentación: más frecuencia a cambio de latencia.

---

# PARTE III: PRÁCTICA Y REPASO

## Ejercicios propuestos (con respuesta)

**P1.** Out = (a·b + c·d) >> 1 con 1 multiplicador, 1 sumador y 1 desplazador.
<details><summary>Respuesta</summary>

S0: Final = 0, carga a, b, c, d, espera Inicio · S1: t1 = a·b · S2: t2 = c·d · S3: t3 = t1 + t2 · S4: out = t3 >> 1, Final = 1. Vidas (S1–S4): a, b: S1; c, d: S1–S2; t1: S2–S3; t2: S3; t3: S4. Máximo = 4 (en S1: a, b, c, d) → 4 registros. *Left-edge*: R1 = {a, t1, t3}, R2 = {b, t2}, R3 = {c}, R4 = {d}. UC: 5 estados → 3 bits; ROM de entrada 2⁴ × 3 = 16 × 3.
</details>

**P2.** Una UC tiene 13 estados, 3 señales de estado + Inicio, una PC de 17 bits y Final. Dimensiona la UC en versión Moore y en una versión Mealy donde la salida depende de 1 señal de estado.
<details><summary>Respuesta</summary>

n = 4 bits. ROM de entrada: 2^(4+4) × 4 = 256 × 4. ROM de salida Moore: 2⁴ × 18 = 16 × 18. ROM de salida Mealy: 2^(4+1) × 18 = 32 × 18.
</details>

**P3.** Pipeline de 5 etapas con retardos 10, 8, 12, 9 y 11 ns y registros de 1 ns. Calcula periodo, latencia, ganancia para 100 datos y ganancia asintótica.
<details><summary>Respuesta</summary>

Sin segmentar: 50 + 1 = 51 ns por dato. Periodo segmentado: 12 + 1 = 13 ns. Latencia: 5 · 13 = 65 ns. 100 datos: (5 + 99) · 13 = 1352 ns frente a 5100 ns → ganancia 3,77. Asintótica: 51 / 13 ≈ 3,92 (menor que 5 por el desbalance de etapas).
</details>

**P4.** f = Σ xᵢ² para 8 datos usando solo un sumador (cuadrado por sumas sucesivas). Plantea el pseudoalgoritmo y las señales de estado.
<details><summary>Respuesta</summary>

```
Final = 0 ; espera Inicio
suma = 0 ; i = 0
mientras i < 8:
   d = X[i] ; acc = 0 ; cont = d
   mientras cont > 0:  acc = acc + d ; cont = cont − 1
   suma = suma + acc ; i = i + 1
out = suma ; Final = 1
```
Señales de estado: (cont = 0) y (i = 8). Si los datos son con signo, primero d = |X[i]| (como en el Taller 6).
</details>

**P5.** Con estos tiempos de vida en S1–S5, ¿cuántos registros hacen falta y cuál es la asignación? p: 1–2, q: 1–4, r: 2–3, s: 3–5, t: 4–5, u: 5.
<details><summary>Respuesta</summary>

Vivas por estado: S1 = 2, S2 = 3, S3 = 3, S4 = 3, S5 = 3 → 3 registros. *Left-edge* (orden p, q, r, s, t, u): R1 = {p, s} (s empieza en 3 > 2), R2 = {q, u} (u empieza en 5 > 4), R3 = {r, t} (t empieza en 4 > 3).
</details>

**P6.** ¿Por qué en un ASM no se puede escribir `t1 = x·x ; t3 = t1·x` en el mismo estado sin encadenamiento?
<details><summary>Respuesta</summary>

Porque t1 se guarda al final del estado; durante el estado, t3 leería el t1 viejo. Para hacerlo en un estado haría falta encadenar dos multiplicadores (y en el parcial solo hay uno).
</details>

## Errores frecuentes (y cómo evitarlos)

1. **Huecos en los tiempos de vida.** Una variable ocupa registro desde que nace hasta su último uso, aunque no se use en medio.
2. **Usar más unidades por estado de las disponibles.** Revisa cada caja de estado: cuenta multiplicaciones, sumas y desplazamientos.
3. **Dividir entre 4 con un desplazador de una posición en un solo estado.** Son dos `>>1` dependientes → dos estados (o dos desplazadores en cascada).
4. **CD sin entradas de las unidades.** Cada unidad funcional necesita sus dos entradas conectadas, con MUX si hay varias fuentes. Haz siempre la tabla RTL y la tabla de fuentes antes de dibujar.
5. **Olvidar el buffer de salida, el desplazador o las constantes** (el "1" de `1 + x`).
6. **Poner X en un habilitador de escritura.** LD y wr van en 0 cuando el registro no debe cambiar.
7. **Dar solo el tamaño de las ROM.** Hay que dar la tabla de transiciones (ROM de entrada) y la tabla de palabras de control (ROM de salida).
8. **Contar mal la dirección de la ROM de entrada.** Bits de estado + todas las entradas de la UC (Inicio, señales de estado, otras entradas externas).
9. **Confundir Moore y Mealy.** Si hay cajas de asignación condicional, es Mealy y la ROM de salida también recibe las condiciones.
10. **Estados de más.** Cargar los datos en el estado de espera y sacar el resultado en el último estado de cálculo, cuando el enunciado lo permite.
11. **Bucles de decisión a decisión.** Toda espera vuelve a una caja de estado.

## Hoja de fórmulas

| Concepto | Fórmula |
|---|---|
| Bits de estado | n = ⌈log₂ E⌉ |
| ROM de entrada | 2^(n + c) × n |
| ROM de salida Moore | 2ⁿ × (k + f) |
| ROM de salida Mealy | 2^(n + c') × (k + f) |
| Bits de selección de un MUX de N entradas | ⌈log₂ N⌉ |
| Bits de un banco de 2^r registros | wr + dirw(r) + enA + dirA(r) + enB + dirB(r) = 3 + 3r |
| Registros mínimos | máx. variables vivas en un estado |
| Unidades mínimas de un tipo | máx. operaciones de ese tipo en un estado |
| Estados mínimos (sin límite de recursos) | longitud del camino crítico (ASAP) |
| Cota inferior con R unidades y M operaciones de un tipo | ⌈M / R⌉ estados |
| Movilidad | ALAP − ASAP |
| Periodo segmentado | T = t_etapa_máx + t_reg |
| Tiempo para N datos en k etapas | (k + N − 1) · T |
| Ganancia | N · t_total / ((k + N − 1) · T) → t_total / T |
| Frecuencia máxima | f = 1 / T_crítico |

---

*Fin de la guía. Orden recomendado de estudio: secciones 1–9 → E1, E2, E3 → secciones 10–11 → **E5 (parcial)** → E6, E7 → secciones 12–14 → E8, E11 → Parte III.*
