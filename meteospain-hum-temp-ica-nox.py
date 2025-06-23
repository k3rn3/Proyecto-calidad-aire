#!/usr/bin/env python3
import requests
import subprocess
import sys

# URLs de los servicios de Meteogalicia
url_ica = "https://servizos.meteogalicia.gal/mgrss/caire/jsonICAActual.action"
url_meteo = "https://servizos.meteogalicia.gal/mgrss/observacion/ultimos10minEstacionsMeteo.action"
url_nox = "https://servizos.meteogalicia.gal/mgrss/caire/jsonDatosActualesEstacion.action?idEstacion=17"

# Configuración para Zabbix
zabbix_server = "172.25.2.239"
zabbix_host = "tgmsrv02"

def send_to_zabbix(key, value):
    """
    Envía un valor utilizando zabbix_sender.
    """
    cmd = [
        "zabbix_sender",
        "-z", zabbix_server,
        "-s", zabbix_host,
        "-k", key,
        "-o", str(value)
    ]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
        print(f"Enviado {key} = {value} -> {result.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        print(f"Error enviando {key}: {e.stderr.strip()}")

# --- Obtener valor PM desde ICA ---
pm_value = None
try:
    response_ica = requests.get(url_ica)
    response_ica.raise_for_status()
    data_ica = response_ica.json()
except Exception as e:
    print("Error obteniendo datos ICA:", e)
    sys.exit(1)

for estacion in data_ica.get("icas", []):
    if estacion.get("idEstacion") == 17:
        pm_value = estacion.get("valor")
        print(f"PM obtenido para la estación 17: {pm_value}")
        break

# --- Obtener datos meteorológicos ---
humidity = None
temperature = None
try:
    response_meteo = requests.get(url_meteo)
    response_meteo.raise_for_status()
    data_meteo = response_meteo.json()
except Exception as e:
    print("Error obteniendo datos meteorológicos:", e)
    sys.exit(1)

for estacion in data_meteo.get("listUltimos10min", []):
    if estacion.get("idEstacion") == 10156:
        medidas = estacion.get("listaMedidas", [])
        for medida in medidas:
            if medida.get("codigoParametro") == "HR_AVG_1.5m":
                humidity = medida.get("valor")
            elif medida.get("codigoParametro") == "TA_AVG_1.5m":
                temperature = medida.get("valor")
        print(f"Datos meteorológicos obtenidos para la estación 10156: Humedad={humidity}, Temperatura={temperature}")
        break

# --- Obtener NOX ---
nox_value = None
try:
    response_nox = requests.get(url_nox)
    response_nox.raise_for_status()
    data_nox = response_nox.json()

    estaciones = data_nox.get("datosEstacion", [])
    for estacion in estaciones:
        if estacion.get("idEstacion") == 17:
            parametros = estacion.get("parametros", [])
            for param in parametros:
                if param.get("parametro") == "NOX":
                    nox_value = param.get("valor")
                    print(f"NOX obtenido: {nox_value}")
                    break
            break  # Ya encontramos la estación, no seguir buscando
    else:
        print("NOX no encontrado en datos.")

except Exception as e:
    print("Error obteniendo datos NOX:", e)
    sys.exit(1)

# --- Verificar que se hayan obtenido todos los datos requeridos ---
if pm_value is None or humidity is None or temperature is None or nox_value is None:
    print("Error: No se pudieron obtener todos los datos necesarios.")
    sys.exit(1)

# --- Enviar los valores obtenidos a Zabbix ---
send_to_zabbix("pm.meteogalicia", pm_value)
send_to_zabbix("humedad.meteogalicia", humidity)
send_to_zabbix("temperatura.meteogalicia", temperature)
send_to_zabbix("nox.meteogalicia", nox_value)
