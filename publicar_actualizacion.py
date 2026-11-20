"""publicar_actualizacion.py — arma lo que hay que subir al servidor para
que ¡Acción! se actualice solo.

Uso (en la carpeta donde está accion.py):

    python publicar_actualizacion.py "Qué trae esta versión"

Crea la carpeta «publicar» con:
  • accion.py      (la versión nueva)
  • version.json   (qué versión es, su huella SHA-256 y las notas)
  • Instalar_Accion_<versión>.exe  (si ya lo armaste con compilar_instalador.bat:
                   el programa instalado baja este instalador)

Después se suben esos archivos tal cual:
  • GitHub (recomendado: gratis y aguanta muchas descargas): en tu
    repositorio → Releases → «Draft a new release» → etiqueta v<versión> →
    arrastra los archivos de la carpeta «publicar» → «Publish release».
    La dirección del version.json no cambia nunca:
      https://github.com/<usuario>/<repositorio>/releases/latest/download/version.json
  • Netlify: arrastrar la carpeta «publicar» a «Deploys».
  • Una carpeta compartida de la red del colegio: file://servidor/carpeta/version.json
Esa dirección va en accion.py (URL_ACTUALIZAR_DEFECTO): así viene puesta en
todos los programas que se instalen. Cada uno puede cambiarla en
⚙ Configuración → Versión.

Antes de publicar, sube el número de versión en accion.py
(la línea  __version__ = "1.9.3"): el programa solo se actualiza si la
versión publicada es más nueva que la que tiene.

No necesita instalar nada (solo Python).
"""
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path


def main() -> int:
    aqui = Path(__file__).resolve().parent
    programa = aqui / "accion.py"
    if not programa.exists():
        print("No encuentro accion.py en esta carpeta.")
        return 1
    fuente = programa.read_text(encoding="utf-8")
    m = re.search(r'^__version__\s*=\s*"([^"]+)"', fuente, re.M)
    if not m:
        print("No encuentro la línea __version__ = \"…\" en accion.py.")
        return 1
    try:
        compile(fuente, "accion.py", "exec")
    except SyntaxError as ex:
        print(f"accion.py tiene un error y no se puede publicar: {ex}")
        return 1
    version = m.group(1)
    notas = " ".join(sys.argv[1:]).strip()
    if not notas:
        try:
            notas = input("¿Qué trae esta versión? (una línea, Enter para dejarlo en blanco): ").strip()
        except EOFError:
            notas = ""
    destino = aqui / "publicar"
    destino.mkdir(exist_ok=True)
    shutil.copy2(programa, destino / "accion.py")
    huella = hashlib.sha256((destino / "accion.py").read_bytes()).hexdigest()
    info = {"version": version, "archivo": "accion.py", "sha256": huella, "notas": notas,
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")}
    # El instalador de esta versión (lo arma compilar_instalador.bat en la carpeta «instalador»)
    instalador = aqui / "instalador" / f"Instalar_Accion_{version}.exe"
    if instalador.exists():
        shutil.copy2(instalador, destino / instalador.name)
        info["instalador"] = instalador.name
        info["sha256_instalador"] = hashlib.sha256(instalador.read_bytes()).hexdigest()
    (destino / "version.json").write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Listo: versión {version} en la carpeta «{destino.name}».")
    if "instalador" in info:
        print(f"Con el instalador: {info['instalador']}.")
        print("Sube los tres archivos (version.json, el instalador y accion.py): en GitHub, una release")
        print(f"nueva con la etiqueta v{version}.")
    else:
        print("(Sin instalador: si quieres que el programa instalado se actualice, corre antes "
              "compilar_instalador.bat.)")
        print("Sube esa carpeta (accion.py y version.json) a tu servidor.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
