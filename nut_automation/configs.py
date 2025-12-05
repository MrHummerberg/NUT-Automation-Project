"""Utilidades de rutas y contenidos de configuración para NUT."""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from shutil import copy2
from typing import Optional, Union

PathLike = Union[str, Path]

@dataclass
class NutConfigPaths:
    """Rutas base de configuración de NUT."""
    base_dir: Path = Path("/etc/nut")

    @property
    def ups_conf(self) -> Path:
        """Ruta a ups.conf."""
        return self.base_dir / "ups.conf"

    @property
    def upsd_conf(self) -> Path:
        """Ruta a upsd.conf."""
        return self.base_dir / "upsd.conf"

    @property
    def upsd_users(self) -> Path:
        """Ruta a upsd.users."""
        return self.base_dir / "upsd.users"

    @property
    def upsmon_conf(self) -> Path:
        """Ruta a upsmon.conf."""
        return self.base_dir / "upsmon.conf"

    @property
    def emulado_seq(self) -> Path:
        """Ruta del fichero de simulación del SAI virtual."""
        return self.base_dir / "emulated_ups.seq"

def generar_timestamp() -> str:
    """Devuelve un timestamp compacto para nombres de copia de seguridad."""
    return datetime.now().strftime("%Y%m%d-%H%M%S")

def backup_config_file(path: PathLike) -> Optional[Path]:
    """Crea una copia de seguridad con timestamp si el fichero existe."""
    p = Path(path)
    if not p.exists():
        return None
    timestamp = generar_timestamp()
    backup_path = p.with_suffix(p.suffix + f".bak-{timestamp}")
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    copy2(p, backup_path)
    return backup_path

def generar_contenido_ups_conf_virtual() -> str:
    """Contenido de ups.conf para un SAI virtual con dummy-ups y fichero seq."""
    return (
        "[emulated_ups]\n"
        "    driver = dummy-ups\n"
        "    port = emulated_ups.seq\n"
        "    # mode=dummy-loop\n"
        "    desc = \"SAI Virtual\"\n"
    )

def generar_contenido_emulado_seq() -> str:
    """Contenido del fichero de escenario del SAI virtual emulado."""
    return (
        "battery.runtime = 1800 # Tiempo de batería simulado en segundos (30 minutos)\n"
        "battery.mfr = \"Emulated\"\n"
        "battery.model = \"Virtual UPS\"\n"
        "battery.charge: 100\n"
        "ups.status: OL\n"
        "TIMER 10\n"
        "ups.status: 0B\n"
        "TIMER 4\n"
        "battery.charge: 80\n"
        "TIMER 2\n"
        "battery.charge: 60\n"
        "TIMER 2\n"
        "battery.charge: 40\n"
        "TIMER 2\n"
        "ALARM [UPS demasiado caliente para cargar]\n"
        "TIMER 5\n"
        "ALARM [Circuito UPS sobrecalentado]\n"
        "TIMER 5\n"
        "ALARM [UPS demasiado frío para cargar]\n"
        "TIMER 4\n"
        "battery.charge: 20\n"
        "TIMER 4\n"
        "battery.charge: 5\n"
        "TIMER 4\n"
    )

def generar_contenido_upsd_conf() -> str:
    """Contenido de upsd.conf para escuchar en localhost."""
    return "LISTEN 127.0.0.1 3493\n"

def generar_contenido_upsd_users(usuario="admin", contraseña="admin_password") -> str:
    """Contenido de upsd.users con un usuario administrador por defecto."""
    return (
        f"[{usuario}]\n"
        f"password = {contraseña}\n"
        "actions = SET\n"
        "instcmds = ALL\n"
        "upsmon master\n"
    )

def generar_linea_notifycmd(correo: str, asunto: str, ruta_mail: str) -> str:
    """Genera una línea NOTIFYCMD para upsmon.conf."""
    return f'NOTIFYCMD {ruta_mail} -s "{asunto}" {correo}'

def actualizar_notifycmd_en_contenido(contenido_actual: str, nueva_linea: str) -> str:
    """Actualiza o añade NOTIFYCMD en el texto de upsmon.conf."""
    lineas = contenido_actual.splitlines()
    nueva_linea = nueva_linea.strip()
    indices_notify = [i for i, l in enumerate(lineas) if l.strip().startswith("NOTIFYCMD")]
    if indices_notify:
        primer = indices_notify[0]
        nuevas_lineas = []
        for i, l in enumerate(lineas):
            if i == primer:
                nuevas_lineas.append(nueva_linea)
            elif i in indices_notify[1:]:
                continue
            else:
                nuevas_lineas.append(l)
        resultado = "\n".join(nuevas_lineas) + "\n"
        return resultado
    nuevas_lineas = list(lineas)
    if nuevas_lineas and nuevas_lineas[-1].strip():
        nuevas_lineas.append("")
    nuevas_lineas.append(nueva_linea)
    return "\n".join(nuevas_lineas) + "\n"
