"""
SIMULACIÓN DE TRANSMISIÓN INALÁMBRICA DE ENERGÍA (WPT)
======================================================

Proyecto Integrador - Teoría Electromagnética II - TEC

Descripción
-----------
Simula un sistema de transmisión inalámbrica de energía a 433,92 MHz.

El programa calcula, en función de la distancia entre las antenas:
    - densidad de potencia;
    - campo eléctrico;
    - potencia recibida por la antena RX;
    - potencia DC después del rectificador;
    - voltaje DC sobre la carga.

También permite incluir:
    - pérdidas del cable;
    - reflexión por ROE;
    - pérdida por polarización;
    - reflexión en el piso;
    - una eficiencia aproximada del rectificador.

Uso
---
1. Modificar únicamente la sección "PARÁMETROS DE ENTRADA".
2. Ejecutar:
       python simulacion_wpt.py
3. Revisar la carpeta "resultados/".

Requisitos
----------
Python 3
numpy
matplotlib

Instalación:
    pip install -r requirements.txt
"""

import csv
import os

import matplotlib.pyplot as plt
import numpy as np


# =============================================================================
# 1. PARÁMETROS DE ENTRADA
# =============================================================================
# ---------------------------------------------------------------------------
# IMPORTANTE:
# Esta es la única sección que normalmente debe modificar el usuario.
#
# Convención de nombres:
#   _HZ       -> frecuencia [Hz]
#   _W        -> potencia [W]
#   _DB       -> decibeles [dB]
#   _DBI      -> ganancia [dBi]
#   _DB_POR_M -> atenuación [dB/m]
#   _M        -> distancia/longitud/altura [m]
#   _OHM      -> resistencia/impedancia [Ω]
#   _V        -> voltaje [V]
#   _GRADOS   -> ángulo [°]
#
# ROE es adimensional.
# Las eficiencias y PLF están expresadas entre 0 y 1.
# ---------------------------------------------------------------------------

# --- Transmisor --------------------------------------------------------------
FRECUENCIA_HZ = 433.92e6

"""Frecuencia de operación del sistema [Hz]."""

POTENCIA_TX_W = 2.0
"""Potencia directa entregada por el transmisor [W]."""


# --- Cable TX -----------------------------------------------------------------
LONGITUD_CABLE_M = 1.0
"""Longitud del cable entre el transmisor y la antena TX [m]."""

ATENUACION_CABLE_DB_POR_M = 0.5

"""Pérdida del cable por unidad de longitud [dB/m]."""


# --- Antenas ------------------------------------------------------------------
ROE_ANTENA_TX = 1.5
"""ROE de la antena transmisora. ROE = 1 significa adaptación perfecta."""

GANANCIA_ANTENA_TX_DBI = 2.15
"""Ganancia de la antena TX [dBi]."""

GANANCIA_ANTENA_RX_DBI = 2.15
"""Ganancia de la antena RX [dBi]."""

ROE_ENTRADA_RECTIFICADOR = 1.5
"""
ROE entre la antena RX y la entrada del rectificador.

Este valor representa el desacople entre la antena y el rectificador.
Una red de adaptación real debería permitir reemplazar este valor por
el obtenido experimentalmente.
"""


# --- Polarización -------------------------------------------------------------
# Opciones:
#   "lineal"
#   "circular_derecha"
#   "circular_izquierda"

TIPO_POLARIZACION_TX = "lineal"
"""Tipo de polarización de la antena TX."""

TIPO_POLARIZACION_RX = "lineal"
"""Tipo de polarización de la antena RX."""

GIRO_ANTENA_RX_GRADOS = 0.0
"""
Ángulo entre las polarizaciones lineales de TX y RX [°].

Solo tiene efecto cuando la polarización correspondiente es lineal.
0°  -> antenas alineadas.
45° -> pérdida de polarización de 3 dB.
90° -> recepción nula para polarización lineal ideal.
"""


# --- Reflexión en el piso -----------------------------------------------------
INCLUIR_REFLEXION_PISO = False
"""
Activa/desactiva el modelo de reflexión en el piso.

False -> solo rayo directo.
True  -> rayo directo + rayo reflejado.
"""

ALTURA_ANTENA_TX_M = 1.0
"""Altura de la antena TX sobre el piso [m]."""

ALTURA_ANTENA_RX_M = 1.0
"""Altura de la antena RX sobre el piso [m]."""

PERMITIVIDAD_RELATIVA_PISO = 5.0
"""Permitividad relativa del material del piso εr [adimensional]."""

POLARIZACION_RESPECTO_PISO = "TE"
"""
Polarización respecto al plano de incidencia.

Opciones:
    "TE" -> campo eléctrico paralelo al piso.
    "TM" -> campo eléctrico perpendicular al piso.
"""


# --- Rectificador y carga ----------------------------------------------------
RESISTENCIA_CARGA_OHM = 2000.0
"""Resistencia conectada a la salida DC del rectificador [Ω]."""

EFICIENCIA_MAX_RECTIFICADOR = 0.85
"""
Eficiencia máxima del modelo del rectificador RF -> DC.

Debe estar entre 0 y 1.
Por ejemplo, 0.85 representa una eficiencia máxima del 85 %.
"""

POTENCIA_MEDIA_EFICIENCIA_W = 0.15e-3
"""
Potencia de entrada donde la eficiencia alcanza la mitad de su valor máximo [W].
Es un parámetro del modelo aproximado del rectificador.
"""

VOLTAJE_ENCENDIDO_LED_V = 1.8
"""Voltaje utilizado como referencia para el encendido de un LED rojo [V]."""


# --- Seguridad ---------------------------------------------------------------
# Valor de referencia usado en este proyecto.
# Confirmar con el profesor cuál norma debe utilizarse en el proyecto final.
DENSIDAD_POTENCIA_LIMITE_W_M2 = FRECUENCIA_HZ / 1e6 / 200
"""Densidad de potencia límite de referencia [W/m²]."""


# --- Barrido y resultados -----------------------------------------------------
DISTANCIA_MIN_M = 0.3
"""Distancia mínima del barrido [m]."""

DISTANCIA_MAX_M = 5.0
"""Distancia máxima del barrido [m]."""

NUMERO_PUNTOS_BARRIDO = 400
"""Cantidad de puntos utilizados en el barrido de distancia."""

CARPETA_RESULTADOS = "resultados"
"""Carpeta donde se guardan las gráficas y el CSV."""


# =============================================================================
# 2. CONSTANTES FÍSICAS Y VALORES DERIVADOS
# =============================================================================
VELOCIDAD_LUZ_M_S = 299_792_458.0
IMPEDANCIA_VACIO_OHM = 120 * np.pi

LONGITUD_ONDA_M = VELOCIDAD_LUZ_M_S / FRECUENCIA_HZ
NUMERO_ONDA_RAD_M = 2 * np.pi / LONGITUD_ONDA_M


# =============================================================================
# 3. FUNCIONES AUXILIARES
# =============================================================================
def db_a_veces(valor_db):
    """Convierte dB a una razón de potencia."""
    return 10 ** (np.asarray(valor_db) / 10)


def vatios_a_dbm(potencia_w):
    """Convierte potencia en vatios a dBm."""
    return 10 * np.log10(np.maximum(potencia_w, 1e-30) / 1e-3)


def coeficiente_reflexion(roe):
    """
    Calcula el módulo del coeficiente de reflexión a partir de la ROE.

    |Γ| = (ROE - 1) / (ROE + 1)

    ROE = 1 -> |Γ| = 0 -> adaptación perfecta.
    """
    return (roe - 1) / (roe + 1)


def fraccion_potencia_transmitida(roe):
    """
    Calcula la fracción de potencia que NO es reflejada.

    P_transmitida / P_incidente = 1 - |Γ|²
    """
    gamma = coeficiente_reflexion(roe)
    return 1 - gamma**2


# =============================================================================
# 4. MODELO FÍSICO
# =============================================================================
def calcular_potencia_radiada():
    """
    Calcula la potencia que realmente recibe la antena TX.

    Modelo:
        1. El transmisor entrega POTENCIA_TX_W.
        2. El cable introduce pérdidas.
        3. La antena TX refleja una parte de la potencia según su ROE.

    Returns
    -------
    potencia_radiada_w : float
        Potencia aceptada por la antena TX [W].

    coef_reflexion_tx : float
        |Γ| de la antena TX.

    potencia_reflejada_medida_w : float
        Potencia reflejada que mediría el transmisor [W].
    """
    # Conversión de dB/m a Np/m.
    alfa_np_m = ATENUACION_CABLE_DB_POR_M / 8.686

    # Pérdida de potencia en un recorrido por el cable.
    atenuacion_ida = np.exp(
        -2 * alfa_np_m * LONGITUD_CABLE_M
    )

    coef_reflexion_tx = coeficiente_reflexion(ROE_ANTENA_TX)

    potencia_fin_cable_w = POTENCIA_TX_W * atenuacion_ida

    potencia_radiada_w = (
        potencia_fin_cable_w
        * (1 - coef_reflexion_tx**2)
    )

    # La potencia reflejada recorre el cable dos veces.
    potencia_reflejada_medida_w = (
        POTENCIA_TX_W
        * coef_reflexion_tx**2
        * atenuacion_ida**2
    )

    return (
        potencia_radiada_w,
        coef_reflexion_tx,
        potencia_reflejada_medida_w,
    )


def densidad_potencia(distancia_m, potencia_radiada_w):
    """
    Calcula la densidad de potencia promedio en espacio libre.

    S(d) = P_rad * G_TX / (4πd²)

    Parameters
    ----------
    distancia_m : float o array
        Distancia entre TX y RX [m].

    potencia_radiada_w : float
        Potencia aceptada por la antena TX [W].

    Returns
    -------
    float o array
        Densidad de potencia [W/m²].
    """
    ganancia_tx = db_a_veces(GANANCIA_ANTENA_TX_DBI)

    return (
        potencia_radiada_w
        * ganancia_tx
        / (4 * np.pi * distancia_m**2)
    )


def campo_electrico_pico(densidad_potencia_w_m2):
    """
    Calcula la amplitud del campo eléctrico.

    S = E0² / (2η0)

    E0 = sqrt(2η0S)
    """
    return np.sqrt(
        2 * IMPEDANCIA_VACIO_OHM * densidad_potencia_w_m2
    )


def vector_polarizacion(tipo, giro_grados=0.0):
    """
    Devuelve el vector unitario de polarización.

    Polarización lineal:
        (cos(ψ), sin(ψ))

    Circular derecha:
        (1, +j) / sqrt(2)

    Circular izquierda:
        (1, -j) / sqrt(2)
    """
    if tipo == "lineal":
        giro_rad = np.radians(giro_grados)

        return np.array(
            [np.cos(giro_rad), np.sin(giro_rad)],
            dtype=complex,
        )

    if tipo == "circular_derecha":
        return np.array([1, 1j]) / np.sqrt(2)

    if tipo == "circular_izquierda":
        return np.array([1, -1j]) / np.sqrt(2)

    raise ValueError(
        f"Tipo de polarización desconocido: '{tipo}'"
    )


def factor_perdida_polarizacion(
    polarizacion_onda,
    polarizacion_antena,
):
    """
    Calcula el factor de pérdida por polarización (PLF).

    PLF = |ê_onda* · ê_antena|²

    PLF = 1 -> no hay pérdida.
    PLF = 0 -> no se recibe potencia idealmente.
    """
    return abs(
        np.vdot(
            polarizacion_onda,
            polarizacion_antena,
        )
    ) ** 2


def potencia_recibida(distancia_m, potencia_radiada_w):
    """
    Calcula la potencia disponible en la antena RX usando Friis.

    P_r = S * A_e * PLF

    donde:

        A_e = G_RX * λ² / (4π)
    """
    ganancia_rx = db_a_veces(GANANCIA_ANTENA_RX_DBI)

    area_efectiva_m2 = (
        ganancia_rx
        * LONGITUD_ONDA_M**2
        / (4 * np.pi)
    )

    polarizacion_tx = vector_polarizacion(
        TIPO_POLARIZACION_TX
    )

    polarizacion_rx = vector_polarizacion(
        TIPO_POLARIZACION_RX,
        GIRO_ANTENA_RX_GRADOS,
    )

    plf = factor_perdida_polarizacion(
        polarizacion_tx,
        polarizacion_rx,
    )

    return (
        densidad_potencia(
            distancia_m,
            potencia_radiada_w,
        )
        * area_efectiva_m2
        * plf
    )


def potencia_recibida_con_piso(
    distancia_m,
    potencia_radiada_w,
):
    """
    Calcula la potencia recibida considerando un rayo directo
    y un rayo reflejado en el piso.

    La interferencia entre ambos rayos puede producir máximos
    y mínimos de potencia al cambiar la distancia.
    """
    altura_tx_m = ALTURA_ANTENA_TX_M
    altura_rx_m = ALTURA_ANTENA_RX_M

    distancia_directa_m = np.sqrt(
        distancia_m**2
        + (altura_tx_m - altura_rx_m)**2
    )

    distancia_reflejada_m = np.sqrt(
        distancia_m**2
        + (altura_tx_m + altura_rx_m)**2
    )

    # Ángulo de incidencia respecto a la normal.
    angulo_incidencia_rad = np.arctan2(
        distancia_m,
        altura_tx_m + altura_rx_m,
    )

    cos_incidente = np.cos(angulo_incidencia_rad)

    cos_transmitido = np.sqrt(
        1
        - np.sin(angulo_incidencia_rad) ** 2
        / PERMITIVIDAD_RELATIVA_PISO
    )

    # Impedancias de los medios.
    impedancia_aire_ohm = IMPEDANCIA_VACIO_OHM

    impedancia_piso_ohm = (
        IMPEDANCIA_VACIO_OHM
        / np.sqrt(PERMITIVIDAD_RELATIVA_PISO)
    )

    if POLARIZACION_RESPECTO_PISO == "TE":
        gamma_piso = (
            impedancia_piso_ohm * cos_incidente
            - impedancia_aire_ohm * cos_transmitido
        ) / (
            impedancia_piso_ohm * cos_incidente
            + impedancia_aire_ohm * cos_transmitido
        )

    else:  # TM
        gamma_piso = (
            impedancia_aire_ohm * cos_incidente
            - impedancia_piso_ohm * cos_transmitido
        ) / (
            impedancia_aire_ohm * cos_incidente
            + impedancia_piso_ohm * cos_transmitido
        )

    # Diferencia de fase entre ambos caminos.
    diferencia_fase_rad = (
        NUMERO_ONDA_RAD_M
        * (distancia_reflejada_m - distancia_directa_m)
    )

    factor_interferencia = (
        1
        + gamma_piso
        * (distancia_directa_m / distancia_reflejada_m)
        * np.exp(-1j * diferencia_fase_rad)
    )

    return (
        potencia_recibida(
            distancia_directa_m,
            potencia_radiada_w,
        )
        * np.abs(factor_interferencia) ** 2
    )


def rectificador_y_carga(potencia_recibida_w):
    """
    Calcula potencia DC y voltaje de salida.

    1. Se considera el desacople entre RX y rectificador.
    2. Se aplica el modelo aproximado de eficiencia.
    3. Se calcula el voltaje sobre una carga resistiva.

    Returns
    -------
    potencia_dc_w : float o array
        Potencia entregada a la carga [W].

    voltaje_dc_v : float o array
        Voltaje sobre la carga [V].
    """
    potencia_entrada_w = (
        potencia_recibida_w
        * fraccion_potencia_transmitida(
            ROE_ENTRADA_RECTIFICADOR
        )
    )

    eficiencia = (
        EFICIENCIA_MAX_RECTIFICADOR
        * potencia_entrada_w
        / (
            potencia_entrada_w
            + POTENCIA_MEDIA_EFICIENCIA_W
        )
    )

    potencia_dc_w = (
        eficiencia * potencia_entrada_w
    )

    voltaje_dc_v = np.sqrt(
        potencia_dc_w
        * RESISTENCIA_CARGA_OHM
    )

    return potencia_dc_w, voltaje_dc_v


# =============================================================================
# 5. VALIDACIÓN DE PARÁMETROS
# =============================================================================
def revisar_parametros():
    """Comprueba que los parámetros principales sean físicamente válidos."""

    if POTENCIA_TX_W <= 0:
        raise ValueError(
            "POTENCIA_TX_W debe ser mayor que 0."
        )

    if LONGITUD_CABLE_M < 0:
        raise ValueError(
            "LONGITUD_CABLE_M no puede ser negativa."
        )

    if ATENUACION_CABLE_DB_POR_M < 0:
        raise ValueError(
            "ATENUACION_CABLE_DB_POR_M no puede ser negativa."
        )

    if ROE_ANTENA_TX < 1:
        raise ValueError(
            "ROE_ANTENA_TX no puede ser menor que 1."
        )

    if ROE_ENTRADA_RECTIFICADOR < 1:
        raise ValueError(
            "ROE_ENTRADA_RECTIFICADOR no puede ser menor que 1."
        )

    if not 0 < EFICIENCIA_MAX_RECTIFICADOR <= 1:
        raise ValueError(
            "EFICIENCIA_MAX_RECTIFICADOR debe estar entre 0 y 1."
        )

    if RESISTENCIA_CARGA_OHM <= 0:
        raise ValueError(
            "RESISTENCIA_CARGA_OHM debe ser mayor que 0."
        )

    polarizaciones_validas = {
        "lineal",
        "circular_derecha",
        "circular_izquierda",
    }

    if TIPO_POLARIZACION_TX not in polarizaciones_validas:
        raise ValueError(
            "TIPO_POLARIZACION_TX no es válida."
        )

    if TIPO_POLARIZACION_RX not in polarizaciones_validas:
        raise ValueError(
            "TIPO_POLARIZACION_RX no es válida."
        )

    if POLARIZACION_RESPECTO_PISO not in {"TE", "TM"}:
        raise ValueError(
            "POLARIZACION_RESPECTO_PISO debe ser 'TE' o 'TM'."
        )

    if DISTANCIA_MIN_M <= 0:
        raise ValueError(
            "DISTANCIA_MIN_M debe ser mayor que 0."
        )

    if DISTANCIA_MIN_M >= DISTANCIA_MAX_M:
        raise ValueError(
            "DISTANCIA_MIN_M debe ser menor que DISTANCIA_MAX_M."
        )

    if NUMERO_PUNTOS_BARRIDO < 2:
        raise ValueError(
            "NUMERO_PUNTOS_BARRIDO debe ser al menos 2."
        )


# =============================================================================
# 6. IMPRESIÓN DE RESULTADOS
# =============================================================================
def imprimir_resumen(
    distancias_m,
    potencia_radiada_w,
    coef_reflexion_tx,
    potencia_reflejada_w,
    densidad_w_m2,
    potencia_rx_w,
    potencia_dc_w,
    voltaje_dc_v,
):
    """Imprime en consola un resumen de los resultados."""

    perdidas_retorno_db = (
        -20 * np.log10(
            max(coef_reflexion_tx, 1e-30)
        )
    )

    print("=" * 70)
    print("SIMULACIÓN DE TRANSMISIÓN INALÁMBRICA DE ENERGÍA")
    print("=" * 70)

    print(f"Frecuencia             : {FRECUENCIA_HZ / 1e6:.2f} MHz")
    print(f"Longitud de onda       : {LONGITUD_ONDA_M:.3f} m")

    print("\n--- TRANSMISOR / CABLE / ANTENA TX ---")

    print(
        f"Potencia del transmisor: "
        f"{POTENCIA_TX_W:.2f} W"
    )

    print(
        f"Coeficiente |Γ_TX|     : "
        f"{coef_reflexion_tx:.3f}"
    )

    print(
        f"Pérdida de retorno     : "
        f"{perdidas_retorno_db:.1f} dB"
    )

    print(
        f"Potencia aceptada por TX: "
        f"{potencia_radiada_w:.3f} W"
    )

    print(
        f"Potencia reflejada medida: "
        f"{potencia_reflejada_w * 1e3:.2f} mW"
    )

    # Distancia a partir de la cual la densidad de potencia
    # queda por debajo del límite de referencia.
    ganancia_tx = db_a_veces(
        GANANCIA_ANTENA_TX_DBI
    )

    distancia_seguridad_m = np.sqrt(
        potencia_radiada_w
        * ganancia_tx
        / (
            4
            * np.pi
            * DENSIDAD_POTENCIA_LIMITE_W_M2
        )
    )

    print("\n--- REFERENCIA DE SEGURIDAD ---")

    print(
        f"Límite utilizado       : "
        f"{DENSIDAD_POTENCIA_LIMITE_W_M2:.2f} W/m²"
    )

    print(
        f"Distancia de referencia: "
        f"{distancia_seguridad_m:.2f} m"
    )

    print("\n--- PÉRDIDA POR POLARIZACIÓN ---")

    polarizacion_lineal = vector_polarizacion("lineal")

    casos_polarizacion = {
        "Lineal - lineal alineada": (
            polarizacion_lineal,
            polarizacion_lineal,
        ),
        "Lineal - lineal a 45°": (
            polarizacion_lineal,
            vector_polarizacion("lineal", 45),
        ),
        "Lineal - lineal a 90°": (
            polarizacion_lineal,
            vector_polarizacion("lineal", 90),
        ),
        "Lineal - circular": (
            polarizacion_lineal,
            vector_polarizacion("circular_derecha"),
        ),
        "Circular - circular igual": (
            vector_polarizacion("circular_derecha"),
            vector_polarizacion("circular_derecha"),
        ),
        "Circular - circular opuesta": (
            vector_polarizacion("circular_derecha"),
            vector_polarizacion("circular_izquierda"),
        ),
    }

    for nombre, (pol_a, pol_b) in casos_polarizacion.items():
        plf = factor_perdida_polarizacion(pol_a, pol_b)

        print(
            f"{nombre:32s}: PLF = {plf:.2f}"
        )

    print("\n--- RESULTADOS EN DISTANCIAS DE REFERENCIA ---")

    print(
        " d [m] | S [W/m²] | E0 [V/m] | "
        "P_RX [dBm] | P_DC [mW] | V0 [V]"
    )

    print("-" * 70)

    for distancia_consulta_m in (
        0.5,
        1.0,
        1.5,
        2.0,
        3.0,
        5.0,
    ):
        indice = np.argmin(
            np.abs(
                distancias_m
                - distancia_consulta_m
            )
        )

        campo_electrico_v_m = campo_electrico_pico(
            densidad_w_m2[indice]
        )

        potencia_rx_dbm = vatios_a_dbm(
            potencia_rx_w[indice]
        )

        print(
            f"{distancias_m[indice]:6.2f} | "
            f"{densidad_w_m2[indice]:8.3f} | "
            f"{campo_electrico_v_m:9.1f} | "
            f"{potencia_rx_dbm:10.1f} | "
            f"{potencia_dc_w[indice] * 1e3:10.3f} | "
            f"{voltaje_dc_v[indice]:6.2f}"
        )


# =============================================================================
# 7. GRÁFICAS
# =============================================================================
def graficar(
    distancias_m,
    densidad_w_m2,
    potencia_rx_w,
    voltaje_dc_v,
    ruta_png,
):
    """Genera y guarda las cuatro gráficas principales."""

    fig, ejes = plt.subplots(
        2,
        2,
        figsize=(11, 8),
    )

    # --- Densidad de potencia -----------------------------------------------
    ejes[0, 0].semilogy(
        distancias_m,
        densidad_w_m2,
        lw=2,
        label="S(d)",
    )

    ejes[0, 0].axhline(
        DENSIDAD_POTENCIA_LIMITE_W_M2,
        color="r",
        ls="--",
        label="Límite de referencia",
    )

    ejes[0, 0].set(
        xlabel="Distancia [m]",
        ylabel="Densidad de potencia [W/m²]",
        title="Densidad de potencia",
    )

    ejes[0, 0].legend()

    # --- Potencia recibida ---------------------------------------------------
    ejes[0, 1].plot(
        distancias_m,
        vatios_a_dbm(potencia_rx_w),
        lw=2,
    )

    titulo_potencia = "Potencia recibida en RX"

    if INCLUIR_REFLEXION_PISO:
        titulo_potencia += " (con reflexión en piso)"

    ejes[0, 1].set(
        xlabel="Distancia [m]",
        ylabel="Potencia recibida [dBm]",
        title=titulo_potencia,
    )

    # --- Pérdida por polarización -------------------------------------------
    giro_grados = np.linspace(0, 89, 200)

    perdida_db = 10 * np.log10(
        np.cos(np.radians(giro_grados)) ** 2
    )

    ejes[1, 0].plot(
        giro_grados,
        perdida_db,
        lw=2,
        label="Lineal - lineal: cos²(ψ)",
    )

    ejes[1, 0].axhline(
        10 * np.log10(0.5),
        color="C1",
        ls="--",
        label="Lineal - circular: −3 dB",
    )

    ejes[1, 0].set(
        xlabel="Giro de RX ψ [°]",
        ylabel="Pérdida [dB]",
        title="Pérdida por polarización",
    )

    ejes[1, 0].legend()

    # --- Voltaje DC ----------------------------------------------------------
    ejes[1, 1].plot(
        distancias_m,
        voltaje_dc_v,
        lw=2,
        label=(
            f"V₀ con R_L = "
            f"{RESISTENCIA_CARGA_OHM:g} Ω"
        ),
    )

    ejes[1, 1].axhline(
        VOLTAJE_ENCENDIDO_LED_V,
        color="r",
        ls="--",
        label=(
            f"Umbral LED ≈ "
            f"{VOLTAJE_ENCENDIDO_LED_V} V"
        ),
    )

    ejes[1, 1].set(
        xlabel="Distancia [m]",
        ylabel="Voltaje DC [V]",
        title="Voltaje sobre la carga",
    )

    ejes[1, 1].legend()

    for eje in ejes.flat:
        eje.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(
        ruta_png,
        dpi=150,
        bbox_inches="tight",
    )
    plt.close(fig)


# =============================================================================
# 8. GUARDAR RESULTADOS
# =============================================================================
def guardar_csv(
    distancias_m,
    densidad_w_m2,
    potencia_rx_w,
    potencia_dc_w,
    voltaje_dc_v,
    ruta_csv,
):
    """Guarda los resultados del barrido en formato CSV."""

    campo_electrico_v_m = campo_electrico_pico(
        densidad_w_m2
    )

    potencia_rx_dbm = vatios_a_dbm(
        potencia_rx_w
    )

    with open(
        ruta_csv,
        "w",
        newline="",
        encoding="utf-8",
    ) as archivo:

        escritor = csv.writer(archivo)

        escritor.writerow(
            [
                "distancia_m",
                "densidad_potencia_W_m2",
                "campo_electrico_V_m",
                "potencia_rx_dBm",
                "potencia_dc_mW",
                "voltaje_dc_V",
            ]
        )

        for fila in zip(
            distancias_m,
            densidad_w_m2,
            campo_electrico_v_m,
            potencia_rx_dbm,
            potencia_dc_w * 1e3,
            voltaje_dc_v,
        ):
            escritor.writerow(
                [f"{valor:.6g}" for valor in fila]
            )


# =============================================================================
# 9. PROGRAMA PRINCIPAL
# =============================================================================
def main():
    """Ejecuta toda la simulación."""

    revisar_parametros()

    os.makedirs(
        CARPETA_RESULTADOS,
        exist_ok=True,
    )

    # -------------------------------------------------------------------------
    # Paso 1: potencia radiada por la antena TX
    # -------------------------------------------------------------------------
    (
        potencia_radiada_w,
        coef_reflexion_tx,
        potencia_reflejada_w,
    ) = calcular_potencia_radiada()

    # -------------------------------------------------------------------------
    # Paso 2: crear el barrido de distancias
    # -------------------------------------------------------------------------
    distancias_m = np.linspace(
        DISTANCIA_MIN_M,
        DISTANCIA_MAX_M,
        NUMERO_PUNTOS_BARRIDO,
    )

    # -------------------------------------------------------------------------
    # Paso 3: densidad de potencia
    # -------------------------------------------------------------------------
    densidad_w_m2 = densidad_potencia(
        distancias_m,
        potencia_radiada_w,
    )

    # -------------------------------------------------------------------------
    # Paso 4: potencia recibida
    # -------------------------------------------------------------------------
    if INCLUIR_REFLEXION_PISO:
        potencia_rx_w = potencia_recibida_con_piso(
            distancias_m,
            potencia_radiada_w,
        )
    else:
        potencia_rx_w = potencia_recibida(
            distancias_m,
            potencia_radiada_w,
        )

    # -------------------------------------------------------------------------
    # Paso 5: rectificador y carga
    # -------------------------------------------------------------------------
    potencia_dc_w, voltaje_dc_v = rectificador_y_carga(
        potencia_rx_w
    )

    # -------------------------------------------------------------------------
    # Paso 6: mostrar y guardar resultados
    # -------------------------------------------------------------------------
    imprimir_resumen(
        distancias_m,
        potencia_radiada_w,
        coef_reflexion_tx,
        potencia_reflejada_w,
        densidad_w_m2,
        potencia_rx_w,
        potencia_dc_w,
        voltaje_dc_v,
    )

    ruta_png = os.path.join(
        CARPETA_RESULTADOS,
        "simulacion_wpt.png",
    )

    graficar(
        distancias_m,
        densidad_w_m2,
        potencia_rx_w,
        voltaje_dc_v,
        ruta_png,
    )

    ruta_csv = os.path.join(
        CARPETA_RESULTADOS,
        "resultados.csv",
    )

    guardar_csv(
        distancias_m,
        densidad_w_m2,
        potencia_rx_w,
        potencia_dc_w,
        voltaje_dc_v,
        ruta_csv,
    )

    print("\n" + "=" * 70)
    print("Simulación terminada correctamente.")
    print(f"Resultados guardados en: {CARPETA_RESULTADOS}/")
    print("=" * 70)


if __name__ == "__main__":
    main()
