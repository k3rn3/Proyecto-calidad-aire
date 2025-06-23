# Proyecto de Calidad del Aire con Sensor SEN55

Esta carpeta contiene la plantilla de Zabbix y los scripts necesarios para enviar al servidor Zabbix los datos recopilados por:

- El sensor **SEN55** conectado a una Raspberry Pi.
- La estación meteorológica **Pontevedra-Campolongo** de **Meteogalicia**.

---

## Contenido de Archivos

### `Meteogalicia-SEN55.xml`
Plantilla exportada de Zabbix que incluye:

- Grupo de plantillas: `Templates/Sensores`
- Templates incluidos:
  - **Template Sen55**
    - Items: Temperatura, Humedad, VOC, NOX, PM
  - **Template Meteogalicia**
    - Items: Temperatura, Humedad, NOX, PM

---

### `meteospain-hum-temp-ica-nox.py`
Script en Python que:

- Recoge medidas (en formato JSON) desde la web oficial de Meteogalicia para la estación de **Pontevedra-Campolongo**.
- Extrae: Temperatura, Humedad, NOX, PM.
- Envía los datos a Zabbix usando `zabbix_sender`.
- Define **triggers** que generan alertas si los valores superan ciertos umbrales.
- Recomendado ejecutarlo cada **5 minutos** mediante `cron`.

---

### `sen55-zabbix.py`
Script en Python diseñado para ejecutarse en la Raspberry Pi `tgmsrv02`. Funcionalidades:

- Se conecta al sensor SEN55 por I2C.
- Toma mediciones de calidad del aire.
- Envía los datos directamente al servidor Zabbix.

---

### `sen55.py`
Script de prueba simple que:

- Imprime en consola las medidas actuales del sensor SEN55.
- No realiza envío a Zabbix.

---

### `dashboards.sql`
Archivo SQL que:

- Contiene la exportación de la **organización del dashboard** de Zabbix desde la base de datos.
- Permite importar la visualización personalizada asociada a estos sensores.

---

## Requisitos

- Python 3.x
- Sensor SEN55 conectado correctamente vía I2C.
- Acceso al servidor Zabbix.
- Herramienta `zabbix_sender` instalada en el equipo que ejecuta los scripts.
- Permisos de escritura en Zabbix para importar plantillas y dashboards.
