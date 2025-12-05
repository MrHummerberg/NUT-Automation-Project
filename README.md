# Nut Automation Project

Automatización de configuración de NUT (Network UPS Tools) para un SAI virtual en entornos de laboratorio.

## Instalación

Este proyecto se puede instalar como un paquete de Python.

1. Clona el repositorio:
   ```bash
   git clone https://github.com/MrHummerberg/NUT-Automation-Project
   cd NUT-Automation-Project
   ```

2. Instala el paquete (recomendado):
   ```bash
   pip install .
   ```

## Uso

El script debe ejecutarse con privilegios de **root** (sudo) ya que modifica archivos de configuración en `/etc/nut` e instala paquetes del sistema.

### Opción 1: Usando el comando instalado (Recomendado)

Si instalaste el paquete, puedes usar el comando `nut-setup`:

```bash
sudo nut-setup
```

### Opción 2: Ejecución directa del módulo

Si prefieres no instalar el paquete, puedes ejecutarlo directamente desde el directorio raíz del proyecto:

```bash
sudo python3 -m nut_automation.main
```

## Características

- Instalación automática de `nut` y `nut-monitor`.
- Configuración de un SAI virtual (dummy-ups).
- Configuración de usuarios y permisos.
- (Opcional) Configuración de notificaciones por correo.
- Simulación de cortes de energía.
