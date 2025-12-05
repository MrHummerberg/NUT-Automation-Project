import os
import sys
import subprocess
from pathlib import Path
from .configs import NutConfigPaths, backup_config_file, generar_contenido_ups_conf_virtual, generar_contenido_emulado_seq, generar_contenido_upsd_conf, generar_contenido_upsd_users, generar_linea_notifycmd, actualizar_notifycmd_en_contenido

# === Códigos ANSI para color en terminal ===
class ColoresTerm:
    INFO = '\033[96m'
    OK = '\033[92m'
    AVISO = '\033[93m'
    ERROR = '\033[91m'
    NEUTRO = '\033[0m'
    NEGRITA = '\033[1m'

def imprimir_info(msg): print(f"{ColoresTerm.INFO}[INFO]{ColoresTerm.NEUTRO} {msg}")
def imprimir_ok(msg): print(f"{ColoresTerm.OK}[OK]{ColoresTerm.NEUTRO} {msg}")
def imprimir_aviso(msg): print(f"{ColoresTerm.AVISO}[AVISO]{ColoresTerm.NEUTRO} {msg}")
def imprimir_error(msg): print(f"{ColoresTerm.ERROR}[ERROR]{ColoresTerm.NEUTRO} {msg}", file=sys.stderr)

# === Utilidades de sistema ===
def es_root():
    return os.geteuid() == 0

def ejecutar_comando(comando, mostrar_salida=True, detener_si_fallo=True):
    imprimir_info(f"Ejecutando: {' '.join(comando)}")
    try:
        resultado = subprocess.run(comando, check=detener_si_fallo, capture_output=not mostrar_salida, text=True)
        if not mostrar_salida and resultado.stdout:
            print(resultado.stdout)
        return resultado
    except subprocess.CalledProcessError as exc:
        imprimir_error(f"El comando falló con código {exc.returncode}: {' '.join(comando)}")
        if exc.stderr: print(exc.stderr)
        if detener_si_fallo: sys.exit(exc.returncode)
        return exc

def escribir_contenido(ruta: Path, contenido: str):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(contenido, encoding="utf-8")
    imprimir_ok(f"Archivo escrito: {ruta}")

# === Flujo principal de automatización ===
def instalar_paquetes():
    imprimir_info("Instalando los paquetes necesarios (nut y nut-monitor)...")
    ejecutar_comando(["apt-get", "update"])
    ejecutar_comando(["apt-get", "install", "-y", "nut", "nut-monitor"])

def config_ups_conf(rutas: NutConfigPaths):
    imprimir_info("Configurando ups.conf y el script de escenario emulado...")
    backup_config_file(rutas.ups_conf)
    escribir_contenido(rutas.ups_conf, generar_contenido_ups_conf_virtual())
    escribir_contenido(rutas.emulado_seq, generar_contenido_emulado_seq())
    imprimir_ok("Configuración de SAI virtual y script de simulación listos.")

def config_upsd_conf(rutas: NutConfigPaths):
    imprimir_info("Configurando upsd.conf para escuchar en localhost...")
    backup_config_file(rutas.upsd_conf)
    escribir_contenido(rutas.upsd_conf, generar_contenido_upsd_conf())

def config_upsd_users(rutas: NutConfigPaths):
    imprimir_info("Configurando upsd.users con usuario por defecto...")
    backup_config_file(rutas.upsd_users)
    escribir_contenido(rutas.upsd_users, generar_contenido_upsd_users())

def configuracion_notifycmd(rutas: NutConfigPaths):
    imprimir_info("Configuración de notificaciones por correo (opcional).")
    resp = input("¿Desea configurar notificaciones NOTIFYCMD en upsmon.conf? [s/N]: ").strip().lower()
    if resp not in {"s", "sí", "si"}:
        imprimir_info("NOTIFYCMD se omite.")
        return
    correo = input("Indique dirección de correo destino (usuario@example.com): ").strip()
    if not correo:
        imprimir_aviso("Correo no indicado. No se configurará NOTIFYCMD.")
        return
    asunto = "Alerta SAI: Evento de suministro eléctrico"
    # Usamos la función de configs.py para generar la línea
    linea_notifycmd = generar_linea_notifycmd(correo, asunto, "/usr/bin/mail")

    backup_config_file(rutas.upsmon_conf)
    contenido = ""
    if rutas.upsmon_conf.exists():
        contenido = rutas.upsmon_conf.read_text(encoding="utf-8")

    nuevo = actualizar_notifycmd_en_contenido(contenido, linea_notifycmd)
    escribir_contenido(rutas.upsmon_conf, nuevo)
    imprimir_ok("Configuración de notificaciones por correo aplicada.")
    imprimir_info("Recuerde que debe tener configurado un MTA (como postfix/ssmtp) para envío de correos.")

def reiniciar_nut_server():
    imprimir_info("Reiniciando el servicio nut-server...")
    resultado = ejecutar_comando(["systemctl", "restart", "nut-server"], mostrar_salida=False, detener_si_fallo=False)
    if getattr(resultado, "returncode", 1) != 0:
        imprimir_error("No se ha podido reiniciar nut-server. Revise /etc/nut/nut.conf (MODE=netserver).")
        sys.exit(resultado.returncode)
    imprimir_ok("nut-server reiniciado correctamente.")

def verificar_ups():
    imprimir_info("Comprobando estado del SAI virtual (upsc)...")
    resultado = ejecutar_comando(["upsc", "emulated_ups@localhost"], mostrar_salida=True, detener_si_fallo=False)
    imprimir_info("Si el estado del SAI aparece, la monitorización es correcta.")

def simular_corte():
    imprimir_info("Simulación de corte de suministro (opcional).")
    resp = input("¿Desea simular un corte del servicio nut-server? [s/N]: ").strip().lower()
    if resp not in {"s", "sí", "si"}:
        imprimir_info("Simulación omitida.")
        return
    imprimir_aviso("Parando nut-server para simular fallo...")
    ejecutar_comando(["systemctl", "stop", "nut-server"], mostrar_salida=True, detener_si_fallo=False)
    input("Pulsa Intro para volver a arrancar nut-server...")
    ejecutar_comando(["systemctl", "start", "nut-server"], mostrar_salida=True, detener_si_fallo=False)
    imprimir_ok("Simulación de corte completada. Puede observar sucesos en nut-monitor.")

# === Secuencia principal ===
def main():
    if not es_root():
        imprimir_error("Debes ejecutar este script como root (sudo).")
        sys.exit(1)

    rutas = NutConfigPaths()

    imprimir_info("Automatización de configuración SAI virtual NUT – Laboratorio.")
    try:
        instalar_paquetes()
        config_ups_conf(rutas)
        config_upsd_conf(rutas)
        config_upsd_users(rutas)
        configuracion_notifycmd(rutas)
        reiniciar_nut_server()
        verificar_ups()
        simular_corte()
        imprimir_ok("Automatización completada. Puedes abrir nut-monitor para observar el SAI virtual.")
    except Exception as exc:
        imprimir_error(f"Error inesperado: {exc}")
        sys.exit(1)

if __name__ == "__main__":
    main()

