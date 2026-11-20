"""datos_ejemplo.py — deja con datos ficticios los guiones de ejemplo que
van en el instalador (lo llama compilar_instalador.bat antes de Inno Setup).

Los guiones de la carpeta «guiones de ejemplo» traen fichas de actores y
técnicos inventados, pero con correos en dominios que podrían ser de
alguien (ejemplo.cl, correo.cl, gmail.com…) y teléfonos con formato real.
Este script los cambia por datos que no pueden pertenecer a nadie:
  • correos  → nombre@correo.example  (dominio reservado para ejemplos)
  • teléfonos → +56 9 0000 0001, +56 9 0000 0002…

Antes de cambiar un guion guarda el original en «guiones de ejemplo\\
originales» (esa carpeta no va en el instalador). Si ya están en orden,
no toca nada.

Uso:  python datos_ejemplo.py   (en la carpeta de accion.py)
"""
import json
import re
import shutil
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
CARPETA = AQUI / "guiones de ejemplo"
RESERVADOS = (".example", ".invalid", ".test", "example.com", "example.org", "example.net")
_CORREO = re.compile(r"(?<![A-Za-z0-9._%+-])([A-Za-z0-9._%+-]+)@([A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,})\b")
_FONO = re.compile(r"(?<![A-Za-z0-9+/])\+56[ ]?9[ ]?\d{4}[ -]?\d{4}(?![A-Za-z0-9+/=])")
_FICTICIO = re.compile(r"\+56 9 0000 \d{4}")


def limpiar_texto(texto: str) -> tuple:
    """Devuelve (texto nuevo, cuántos correos, cuántos teléfonos cambió)."""
    n_correos = 0

    def correo(m):
        nonlocal n_correos
        dominio = m.group(2).lower()
        if dominio.endswith(RESERVADOS):
            return m.group(0)
        n_correos += 1
        return f"{m.group(1)}@correo.example"

    nuevo = _CORREO.sub(correo, texto)
    usados = {int(x[-4:]) for x in _FICTICIO.findall(nuevo)}
    asignados: dict = {}

    def fono(m):
        k = m.group(0)
        if _FICTICIO.fullmatch(k):
            return k
        if k not in asignados:
            n = 1
            while n in usados:
                n += 1
            usados.add(n)
            asignados[k] = f"+56 9 0000 {n:04d}"
        return asignados[k]

    nuevo = _FONO.sub(fono, nuevo)
    return nuevo, n_correos, len(asignados)


def main() -> int:
    if not CARPETA.is_dir():
        print("  (sin carpeta «guiones de ejemplo»: el instalador va sin guiones de ejemplo)")
        return 0
    cambiados = 0
    for f in sorted(CARPETA.glob("*.accion")):
        crudo = f.read_bytes()
        try:
            texto = crudo.decode("utf-8")
            json.loads(texto)
        except (UnicodeDecodeError, ValueError):
            print(f"  [aviso] {f.name}: no es un guion .accion legible; no lo toco")
            continue
        nuevo, n_c, n_f = limpiar_texto(texto)
        if nuevo == texto:
            continue
        json.loads(nuevo)                           # (sigue siendo un .accion válido)
        respaldo = CARPETA / "originales"
        respaldo.mkdir(exist_ok=True)
        if not (respaldo / f.name).exists():
            shutil.copy2(f, respaldo / f.name)
        f.write_bytes(nuevo.encode("utf-8"))
        cambiados += 1
        print(f"  {f.name}: {n_c} correo(s) y {n_f} teléfono(s) cambiados por datos ficticios")
    if cambiados:
        print("  (los originales quedaron en «guiones de ejemplo\\originales», que no va en el instalador)")
    else:
        print("  Guiones de ejemplo: datos ficticios, en orden")
    return 0


if __name__ == "__main__":
    sys.exit(main())
