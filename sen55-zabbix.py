# SPDX-License-Identifier: MIT

import time
import subprocess
from sensirion_i2c_driver import I2cConnection, LinuxI2cTransceiver
from sensirion_i2c_sen5x import Sen5xI2cDevice

# Configuración de Zabbix
ZABBIX_SERVER = "172.25.2.239"
ZABBIX_HOST = "tgmsrv02"

def send_to_zabbix(key, value):
    try:
        result = subprocess.run([
            "zabbix_sender",
            "-z", ZABBIX_SERVER,
            "-s", ZABBIX_HOST,
            "-k", key,
            "-o", str(value)
        ], check=True, capture_output=True)

        # Revisar la salida de zabbix_sender (ignorar código 2)
        if result.returncode == 2:
            print("[Zabbix info] Ignorando código de salida 2, dato enviado correctamente.")
        elif result.returncode != 0:
            print(f"[Zabbix error] Error al enviar a Zabbix: {result.stderr.decode()}")

    except subprocess.CalledProcessError as e:
        print(f"[Zabbix error] Error al enviar a Zabbix: {e}")

# Inicializar I2C y sensor
i2c = LinuxI2cTransceiver('/dev/i2c-1')
device = Sen5xI2cDevice(I2cConnection(i2c))

# Información del dispositivo
print(f"Version: {device.get_version()}")
print(f"Product Name: {device.get_product_name()}")
print(f"Serial Number: {device.get_serial_number()}")

# Reiniciar y comenzar medición
device.device_reset()
device.start_measurement()
time.sleep(1)

def read_data():
    try:
        print("Esperando nuevos datos...")
        while not device.read_data_ready():
            time.sleep(0.1)

        values = device.read_measured_values()
        print(values)

        # Enviar a Zabbix
        send_to_zabbix("sensor.pm1_0", values.mass_concentration_1p0.physical)
        send_to_zabbix("sensor.pm2_5", values.mass_concentration_2p5.physical)
        send_to_zabbix("sensor.pm4_0", values.mass_concentration_4p0.physical)
        send_to_zabbix("sensor.pm10_0", values.mass_concentration_10p0.physical)
        send_to_zabbix("sensor.temperatura", values.ambient_temperature.degrees_celsius)
        send_to_zabbix("sensor.humedad", values.ambient_humidity.percent_rh)
        send_to_zabbix("sensor.voc_index", values.voc_index)
        send_to_zabbix("sensor.nox_index", values.nox_index)

        status = device.read_device_status()
        print(f"Estado del dispositivo: {status}\n")

    except Exception as e:
        print(f"[Error de lectura] {e}")

while True:
    read_data()
    time.sleep(60)  # leer y enviar cada 60 segundos
