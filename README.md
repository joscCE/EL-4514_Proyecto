# Simulación de transmisión inalámbrica de energía (WPT)

Proyecto Integrador · Teoría Electromagnética II · TEC

Este proyecto simula un sistema de transmisión inalámbrica de energía a **433,92 MHz**:

```text
Transmisor → Cable → Antena TX )))) espacio libre (((( Antena RX → Rectificador → Carga
```

El programa permite estudiar cómo cambia la potencia recibida y el voltaje DC en función de la distancia, considerando pérdidas del cable, ROE, ganancia de las antenas, polarización y, opcionalmente, una reflexión en el piso.

---
Densidad de potencia y Teorema de Poynting.
El teorema de Poynting establece que la potencia electromagnética que fluye a través de una superficie se puede calcular mediante el vector de Poynting , definido como:
S=E×H

La magnitud de este vector representa la potencia por unidad de área, usualmente expresada en W/m².
En el caso de una antena transmisora que irradia en el espacio libre, la densidad de potencia a una distancia d se obtiene a partir de la potencia radiada P_rady la ganancia de la antena G_TX:
S(d)=(P_rad " " G_TX)/(4πd^2 )
De esta ecuación podemos notar que comienza a disminuir con d^2.
Ecuación de Friis.
La ecuación de Friis permite calcular la potencia recibida por una antena a partir de la potencia radiada, las ganancias de ambas antenas y la distancia que las separa:
P_r=P_rad " " G_TX " " G_RX (λ/4πd)^2

Donde:
	P_res la potencia recibida,
	G_TX y G_RXson las ganancias de las antenas transmisora y receptora,
	λ es la longitud de onda,
	d es la distancia entre las antenas.
Ecuación importante para entender como la potencia recibida varia con la distancia

Polarización y factor de pérdida de polarización (PLF).
La polarización describe la orientación del campo eléctrico de la onda electromagnética. Puede ser lineal o circular,derecha o izquierda.
Cuando la polarización de la onda incidente no coincide con la polarización de la antena receptora, se produce una pérdida de potencia. Esta pérdida se cuantifica mediante el PLF:
PLF=∣e ̂_onda⋅e ̂_antena ∣^2

	e ̂_onda vector unitario que describe la dirección del campo eléctrico en la onda incidente
	e ̂_antena vector unitario que describe la polarización de la antena receptora
Algunos casos importantes:
	Polarizaciones lineales perfectamente alineadas → PLF = 1 (sin pérdida)
	Polarizaciones lineales a 45° → PLF = 0.5
	Polarizaciones lineales ortogonales (90°) → PLF = 0 (pérdida total)
	Polarización lineal con circular → PLF = 0.5
	Circulares del mismo sentido → PLF = 1
	Circulares de sentido opuesto → PLF = 0
La orientación de las antenas es muy importante de tenerlo en cuenta.

Razón de onda estacionaria (ROE) y el coeficiente de reflexión.
Cuando existe un desacople de impedancias entre una línea de transmisión y una antena (o entre la antena receptora y el rectificador), parte de la potencia se refleja. Esta reflexión se caracteriza mediante el coeficiente de reflexión  Γ:
∣Γ∣=(ROE-1)/(ROE+1)

La ROE (Razón de Onda Estacionaria) es un parámetro que indica qué tan bien adaptado está el sistema:
	ROE = 1 → adaptación perfecta (no hay reflexión)
	ROE > 1 → existe potencia reflejada
La potencia que realmente se entrega o se recibe se reduce por el factor (1-∣Γ∣^2 ). Por lo tanto, controlar la ROE es fundamental para maximizar la transferencia de energía.
________________________________________
Rectenna y eficiencia RF → DC
Una rectenna (rectifying antenna) es el conjunto formado por la antena receptora y un circuito rectificador de onda que convierte la señal de radiofrecuencia (RF) en corriente continua (DC).
La eficiencia de esta conversión se define como:
η=P_DC/P_in 

Donde P_ines la potencia de RF que llega al rectificador y P_DCes la potencia continua entregada a la carga.
En la práctica, la eficiencia no es constante: depende de la potencia de entrada. A potencias muy bajas, la eficiencia disminuye porque los diodos del rectificador no conducen de manera óptima. Por esta razón, en el modelo se utiliza una expresión aproximada de la forma:
η(P_in )=η_max⋅P_in/(P_in+P_0 )

Esta relación permite estimar el voltaje que se obtiene sobre la carga resistiva a partir de la potencia DC:
V_o=√(P_DC " " R_L )



Alternativas consideradas
Durante la etapa inicial del proyecto se evaluaron distintas formas de modelar el enlace de transmisión inalámbrica de energía. Las principales alternativas consideradas fueron las siguientes:
a) Modelo de propagación
Se analizaron dos enfoques:
	Modelo de espacio libre (ecuación de Friis), que considera únicamente el rayo directo entre las antenas.
	Modelo de dos rayos, que incluye el rayo directo y el rayo reflejado en el piso.
Se decidió implementar ambos. Por defecto la simulación utiliza el modelo de espacio libre, y se dejó la posibilidad de activar la reflexión en el piso mediante un parámetro, con el fin de estudiar el efecto de la interferencia entre ambos rayos.

b) Tratamiento de la polarización
Se consideró la opción de asumir polarización perfectamente alineada (PLF = 1) frente a incluir el cálculo del factor de pérdida de polarización.
Se optó por implementar el cálculo completo del PLF, permitiendo seleccionar polarización lineal o circular y el ángulo de desalineación entre las antenas, ya que este factor puede reducir significativamente la potencia recibida.

c) Pérdidas por desacople (ROE)
Se evaluó ignorar las pérdidas por desadaptación o incluirlas.
Se decidió incorporar el efecto de la ROE tanto en la antena transmisora como en la entrada del rectificador, mediante el coeficiente de reflexión, para obtener una estimación más realista de la potencia entregada y recibida.

d) Modelo de eficiencia del rectificador
Se consideraron dos posibilidades: asumir una eficiencia constante o utilizar un modelo que dependa de la potencia de entrada.
Se eligió un modelo aproximado de la forma
η(P_in )=η_max⋅P_in/(P_in+P_0 )

porque representa mejor el comportamiento de los rectificadores a bajas potencias. Se reconoce que este modelo deberá actualizarse cuando se disponga de datos experimentales del rectificador real.

## 1. Archivos

| Archivo | Descripción |
|---|---|
| `simulacion_wpt.py` | Programa principal de simulación |
| `requirements.txt` | Librerías de Python necesarias |
| `README.md` | Documentación y explicación del modelo |
| `resultados/` | Carpeta creada automáticamente con los resultados |

Al ejecutar el programa se generan:

- `resultados/simulacion_wpt.png`: gráficas de la simulación.
- `resultados/resultados.csv`: resultados numéricos para análisis posterior.

---

## 2. Instalación

Se necesita **Python 3**.

Instalar las dependencias:

```bash
pip install -r requirements.txt
```

o directamente:

```bash
pip install numpy matplotlib
```

---

## 3. Cómo ejecutar la simulación

Desde la carpeta del proyecto:

```bash
python simulacion_wpt.py
```

No es necesario modificar ninguna función para utilizar el programa.

**Los únicos valores que normalmente deben modificarse están al inicio de `simulacion_wpt.py`, en la sección `PARÁMETROS DE ENTRADA`.**

---

# 4. Parámetros de entrada

Esta es la sección que debe modificar una persona que quiera utilizar la simulación.

Cada parámetro tiene:

- un nombre descriptivo;
- su unidad indicada en el nombre;
- un comentario explicando qué representa;
- cuando corresponde, el rango o las opciones permitidas.

## 4.1 Transmisor

```python
FRECUENCIA_HZ = 433.92e6
POTENCIA_TX_W = 2.0
```

| Variable | Unidad | Significado |
|---|---|---|
| `FRECUENCIA_HZ` | Hz | Frecuencia de operación del sistema |
| `POTENCIA_TX_W` | W | Potencia directa entregada por el transmisor |

---

## 4.2 Cable entre el transmisor y la antena TX

```python
LONGITUD_CABLE_M = 1.0
ATENUACION_CABLE_DB_POR_M = 0.5
```

| Variable | Unidad | Significado |
|---|---|---|
| `LONGITUD_CABLE_M` | m | Longitud del cable entre el transmisor y la antena |
| `ATENUACION_CABLE_DB_POR_M` | dB/m | Pérdida del cable por cada metro |

La atenuación debe obtenerse, idealmente, de la hoja de datos del cable utilizado.

---

## 4.3 Antenas

```python
ROE_ANTENA_TX = 1.5
GANANCIA_ANTENA_TX_DBI = 2.15
GANANCIA_ANTENA_RX_DBI = 2.15
ROE_ENTRADA_RECTIFICADOR = 1.5
```

| Variable | Unidad | Significado |
|---|---|---|
| `ROE_ANTENA_TX` | adimensional | ROE de la antena transmisora |
| `GANANCIA_ANTENA_TX_DBI` | dBi | Ganancia de la antena TX |
| `GANANCIA_ANTENA_RX_DBI` | dBi | Ganancia de la antena RX |
| `ROE_ENTRADA_RECTIFICADOR` | adimensional | ROE entre la antena RX y la entrada del rectificador |

Para una antena perfectamente adaptada:

```text
ROE = 1
```

Una ROE mayor significa mayor potencia reflejada.

---

## 4.4 Polarización

```python
TIPO_POLARIZACION_TX = "lineal"
TIPO_POLARIZACION_RX = "lineal"
GIRO_ANTENA_RX_GRADOS = 0.0
```

`TIPO_POLARIZACION_TX` y `TIPO_POLARIZACION_RX` aceptan:

```text
"lineal"
"circular_derecha"
"circular_izquierda"
```

`GIRO_ANTENA_RX_GRADOS` representa el ángulo entre la polarización lineal de TX y RX.

Ejemplo:

```python
TIPO_POLARIZACION_TX = "lineal"
TIPO_POLARIZACION_RX = "lineal"
GIRO_ANTENA_RX_GRADOS = 45
```

produce una pérdida de polarización de:

```text
PLF = cos²(45°) = 0.5
```

---

## 4.5 Reflexión en el piso

La reflexión en el piso está desactivada por defecto:

```python
INCLUIR_REFLEXION_PISO = False
```

Para activarla:

```python
INCLUIR_REFLEXION_PISO = True
```

Los parámetros asociados son:

```python
ALTURA_ANTENA_TX_M = 1.0
ALTURA_ANTENA_RX_M = 1.0
PERMITIVIDAD_RELATIVA_PISO = 5.0
POLARIZACION_RESPECTO_PISO = "TE"
```

| Variable | Unidad | Significado |
|---|---|---|
| `ALTURA_ANTENA_TX_M` | m | Altura de TX sobre el piso |
| `ALTURA_ANTENA_RX_M` | m | Altura de RX sobre el piso |
| `PERMITIVIDAD_RELATIVA_PISO` | adimensional | Permitividad relativa del material del piso |
| `POLARIZACION_RESPECTO_PISO` | — | Polarización respecto al plano de incidencia: `"TE"` o `"TM"` |

---

## 4.6 Rectificador y carga

```python
RESISTENCIA_CARGA_OHM = 2000.0
EFICIENCIA_MAX_RECTIFICADOR = 0.85
POTENCIA_MEDIA_EFICIENCIA_W = 0.15e-3
VOLTAJE_ENCENDIDO_LED_V = 1.8
```

| Variable | Unidad | Significado |
|---|---|---|
| `RESISTENCIA_CARGA_OHM` | Ω | Resistencia conectada a la salida DC |
| `EFICIENCIA_MAX_RECTIFICADOR` | 0–1 | Eficiencia máxima RF → DC |
| `POTENCIA_MEDIA_EFICIENCIA_W` | W | Potencia de entrada donde la eficiencia alcanza la mitad de su valor máximo |
| `VOLTAJE_ENCENDIDO_LED_V` | V | Umbral utilizado como referencia para un LED |

**Importante:** la eficiencia del rectificador utilizada actualmente es un modelo aproximado. Para obtener resultados experimentales, debe sustituirse por datos medidos del rectificador real.

---

## 4.7 Rango de distancias

```python
DISTANCIA_MIN_M = 0.3
DISTANCIA_MAX_M = 5.0
```

Estos valores determinan el intervalo de distancias utilizado para el barrido.

---

## 4.8 Carpeta de resultados

```python
CARPETA_RESULTADOS = "resultados"
```

Indica dónde se guardarán la gráfica y el archivo CSV.

---

# 5. ¿Qué calcula el programa?

El modelo sigue la cadena física:

```text
Potencia del transmisor
        ↓
Pérdidas del cable
        ↓
Reflexión de la antena TX
        ↓
Potencia radiada
        ↓
Densidad de potencia
        ↓
Potencia recibida por RX
        ↓
Pérdidas por polarización
        ↓
Desacople con el rectificador
        ↓
Eficiencia RF → DC
        ↓
Potencia DC
        ↓
Voltaje sobre la carga
```

## 5.1 Cable y antena TX

Se calcula el coeficiente de reflexión a partir de la ROE:
$$|\Gamma| = \frac{\mathrm{ROE}-1}{\mathrm{ROE}+1}$$
La potencia entregada a la antena se calcula considerando las pérdidas del cable y la potencia reflejada.

## 5.2 Densidad de potencia

Para una antena en espacio libre:
$$\overline{S}(d) = \frac{P_{\mathrm{rad}} \, G_{\mathrm{TX}}}{4\pi d^{2}}$$
donde:

$P_{\mathrm{rad}}$: potencia entregada a la antena TX.
$G_{\mathrm{TX}}$: ganancia lineal de la antena TX.
$d$: distancia entre las antenas.
$\overline{S}$: densidad de potencia en W/m².

El campo eléctrico se obtiene mediante:
$$E_{0} = \sqrt{2\eta_{0}\overline{S}}$$
con:
$$\eta_{0} \approx 377\,\Omega$$

## 5.3 Potencia recibida

Se utiliza el área efectiva de la antena RX:

$$
A_e=\frac{G_\mathrm{RX}\lambda^2}{4\pi}
$$

y:

$$
P_r=\overline{S}\,A_e\,PLF
$$

Esto es equivalente a la ecuación de Friis:

$$
P_r = P_\mathrm{rad}\,G_\mathrm{TX}\,G_\mathrm{RX}\left(\frac{\lambda}{4\pi d}\right)^2 PLF
$$

---

## 5.4 Pérdida por polarización

El factor de pérdida de polarización se calcula como:

$$
PLF = \left| \hat{e}_\mathrm{onda}^{*} \cdot \hat{e}_\mathrm{antena} \right|^2
$$

Algunos casos:

| TX | RX | PLF |
|---|---|---:|
| Lineal | Lineal alineada | 1 |
| Lineal | Lineal a 45° | 0.5 |
| Lineal | Lineal a 90° | 0 |
| Lineal | Circular | 0.5 |
| Circular derecha | Circular derecha | 1 |
| Circular derecha | Circular izquierda | 0 |

---

## 5.5 Reflexión en el piso

Si `INCLUIR_REFLEXION_PISO = True`, el programa suma el campo de:

1. rayo directo;
2. rayo reflejado.

La diferencia de fase entre ambos produce máximos y mínimos de potencia al cambiar la distancia.

Este modelo no incluye paredes, mobiliario ni otros objetos.

---

## 5.6 Rectificador y carga

Primero se calcula la potencia que realmente entra al rectificador:

$$
P_\mathrm{in} = P_r\left(1-|\Gamma_r|^2\right)
$$

La eficiencia se modela mediante:

$$
\eta(P_\mathrm{in}) = \eta_\mathrm{max}\,\frac{P_\mathrm{in}}{P_\mathrm{in}+P_0}
$$

Después:

$$
P_\mathrm{DC} = \eta\,P_\mathrm{in}
$$

y para una carga resistiva:

$$
V_o = \sqrt{P_\mathrm{DC}\,R_L}
$$

---

# 6. Resultados generados

Al ejecutar:

```bash
python simulacion_wpt.py
```

se crea:

```text
resultados/
├── simulacion_wpt.png
└── resultados.csv
```

### Gráfica

La figura contiene:

1. densidad de potencia vs. distancia;
2. potencia recibida vs. distancia;
3. pérdida por polarización;
4. voltaje DC vs. distancia.

### CSV

El archivo contiene:

```text
distancia_m
S_W_m2
E0_V_m
P_rx_dBm
P_DC_mW
Vo_V
```

Esto permite abrir los resultados en Excel, LibreOffice Calc, MATLAB, Octave o Python.

---

# 7. Caso base

Con los valores predeterminados:

- \(f=433.92\) MHz
- \(P_{TX}=2\) W
- cable de 1 m
- atenuación de 0.5 dB/m
- ROE TX = 1.5
- ROE RX/rectificador = 1.5
- antenas de 2.15 dBi
- polarización lineal alineada
- espacio libre
- \(R_L=2\) kΩ

la longitud de onda es aproximadamente:

\[
\lambda\approx0.691\ \mathrm{m}
\]

El modelo predice aproximadamente:

| Distancia | S | E₀ | P_RX | P_DC | V₀ |
|---:|---:|---:|---:|---:|---:|
| 0.5 m | 0.893 W/m² | 25.9 V/m | 17.5 dBm | 45.3 mW | 9.52 V |
| 1.0 m | 0.226 W/m² | 13.0 V/m | 11.5 dBm | 11.3 mW | 4.76 V |
| 1.5 m | 0.099 W/m² | 8.6 V/m | 7.9 dBm | 4.9 mW | 3.14 V |
| 2.0 m | 0.056 W/m² | 6.5 V/m | 5.4 dBm | 2.7 mW | 2.34 V |
| 3.0 m | 0.025 W/m² | 4.3 V/m | 1.9 dBm | 1.1 mW | 1.52 V |
| 5.0 m | 0.009 W/m² | 2.6 V/m | −2.5 dBm | 0.36 mW | 0.84 V |

Estos resultados son **teóricos y dependen fuertemente de los parámetros utilizados**. En particular, la eficiencia del rectificador es actualmente un modelo aproximado.

---

# 8. Limitaciones del modelo

El programa actualmente supone:

- antenas ideales con ganancia fija;
- propagación en espacio libre;
- opcionalmente, un único rebote en el piso;
- ausencia de paredes y mobiliario;
- cable con atenuación uniforme;
- carga puramente resistiva;
- eficiencia del rectificador aproximada mediante una función matemática;
- sin modelar la ruptura de diodos;
- sin modelar detalladamente la red de adaptación.

Por lo tanto, los resultados deben interpretarse como **predicciones del modelo**, no como garantía del comportamiento del prototipo.

---

# 9. Datos que deberían actualizarse con mediciones

Cuando estén disponibles datos experimentales, conviene actualizar:

### Equipo de transmisión

- potencia real del transmisor;
- longitud del cable;
- atenuación del cable;
- ROE de la antena TX.

### Antena TX/RX

- ganancia real;
- patrón de radiación;
- polarización;
- ROE;
- orientación.

### Rectificador

- impedancia de entrada;
- eficiencia RF → DC;
- curva de eficiencia vs. potencia;
- comportamiento con diferentes cargas.

### Medición

- distancia;
- orientación;
- potencia recibida;
- voltaje DC.

Con estos datos, el modelo puede utilizarse para comparar directamente teoría y experimento.

---

# 10. Estructura del código

El archivo `simulacion_wpt.py` está dividido en bloques:

```text
1. Parámetros de entrada
2. Constantes físicas y valores derivados
3. Funciones auxiliares
4. Modelo físico
5. Validación y generación de resultados
6. Programa principal
```

La idea es que una persona nueva en el proyecto **solo tenga que modificar la sección 1**.

No es necesario modificar las funciones internas para cambiar la frecuencia, potencia, antenas, cable, polarización, carga o distancia.

---

# 11. Referencias

- W. H. Hayt y J. A. Buck, *Teoría Electromagnética*, 8.ª ed.
- R. Neri Vela, *Líneas de Transmisión*.
- C. A. Balanis, *Antenna Theory: Analysis and Design*, 4.ª ed.
- ICNIRP, *Guidelines for Limiting Exposure to Electromagnetic Fields*, 2020.
