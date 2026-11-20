"""licencias_terceros.py — deja el programa compilado en regla con las
licencias de lo que lleva dentro (lo llama compilar_instalador.bat después
de PyInstaller).

1. Saca lo que el programa no usa y no se debe repartir:
   • Qt Virtual Keyboard (teclado en pantalla): su licencia es GPL 3 o
     comercial (no LGPL). PyInstaller lo mete por un complemento de Qt.
   • FFmpeg y el complemento multimedia de Qt que lo usa: el programa no
     reproduce ni graba video (la lectura en voz alta no lo necesita).
2. Arma la carpeta «Licencias de terceros» con los textos de licencia de
   cada componente empaquetado (Python, Qt/PySide6, python-docx, lxml,
   openpyxl, pypdf, pycrdt…), dónde obtener el código fuente de Qt, y un
   índice (LEEME.txt).
3. Deja LICENSE.txt (la licencia MIT de ¡Acción!) junto a Accion.exe.

Uso:  python licencias_terceros.py   (en la carpeta de accion.py)
"""
import importlib.metadata as md
import re
import shutil
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DIST = AQUI / "compilacion" / "dist" / "Accion"
BUILD = AQUI / "compilacion" / "build" / "Accion"
TEXTOS = AQUI / "licencias"
CARPETA = DIST / "Licencias de terceros"
AUTOR = "Gabriel González Vilches"

# ── 1. Lo que no se reparte ──
_FUERA = [
    (re.compile(r"virtualkeyboard", re.I), "Qt Virtual Keyboard (GPL 3): no se usa"),
    (re.compile(r"ffmpegmediaplugin|qt6ffmpegstub", re.I), "complemento FFmpeg de Qt Multimedia: no se usa"),
    (re.compile(r"^(lib)?(avcodec|avformat|avutil|avdevice|avfilter|swresample|swscale|postproc)([-.]\d|\.dll$|\.so)", re.I),
     "FFmpeg: no se usa"),
]


def limpiar() -> list:
    sacados = []
    for p in sorted(DIST.rglob("*"), key=lambda x: len(x.parts), reverse=True):
        if not (p.is_file() or p.is_symlink()):
            continue
        for rx, motivo in _FUERA:
            if rx.search(p.name):
                try:
                    p.unlink()
                    sacados.append((p.relative_to(DIST), motivo))
                except OSError as ex:
                    print(f"  [aviso] no pude borrar {p.name}: {ex}")
                break
    return sacados


# ── 2. Qué paquetes de Python quedaron dentro ──
def modulos_empaquetados() -> set:
    nombres = set()
    for toc in ("PYZ-00.toc", "Analysis-00.toc"):
        f = BUILD / toc
        if f.exists():
            texto = f.read_text(encoding="utf-8", errors="replace")
            for m in re.finditer(r"\('([A-Za-z_][\w.]*)',\s*'[^']*',\s*'(PYMODULE|EXTENSION)'\)", texto):
                nombres.add(m.group(1).split(".")[0])
    if not nombres:                                  # (sin la carpeta build: lo que hay en _internal)
        interno = DIST / "_internal"
        if interno.exists():
            nombres = {p.name.split(".")[0] for p in interno.iterdir()}
    return nombres


def distribuciones(modulos: set) -> list:
    por_modulo = md.packages_distributions()
    nombres = set()
    for mod in modulos:
        for d in por_modulo.get(mod, []):
            nombres.add(d)
    if "PySide6" in modulos or any(n.lower().startswith("pyside6") for n in nombres):
        nombres |= {"PySide6", "PySide6_Essentials", "PySide6_Addons", "shiboken6"}
    nombres.add("pyinstaller")                        # (su lanzador va dentro del .exe)
    presentes = {p.name.lower() for p in DIST.rglob("*") if p.is_file()}
    salida = []
    for n in sorted(nombres, key=str.lower):
        try:
            d = md.distribution(n)
        except md.PackageNotFoundError:
            continue
        if n.lower().startswith("pyside6_"):
            # (los paquetes en que se divide PySide6: solo si algo suyo quedó dentro)
            binarios = {Path(str(f)).name.lower() for f in (d.files or [])
                        if str(f).lower().endswith((".dll", ".so", ".pyd", ".dylib")) or ".so." in str(f).lower()}
            if not (binarios & presentes):
                continue
        salida.append(d)
    return salida


_ES_LICENCIA = re.compile(r"(licen[cs]e|copying|notice|authors)", re.I)


def licencia_de(d) -> str:
    m = d.metadata
    lic = (m.get("License-Expression") or "").strip()
    if not lic:
        lic = (m.get("License") or "").strip().splitlines()[0] if m.get("License") else ""
    if not lic or len(lic) > 80:
        clas = [c.split("::")[-1].strip() for c in (m.get_all("Classifier") or []) if c.startswith("License")]
        lic = ", ".join(clas) or lic[:80] or "ver archivos"
    return lic


def copiar_licencias(d, destino: Path) -> int:
    """Los archivos de licencia que trae la ficha del paquete (su .dist-info)."""
    n = 0
    for f in d.files or []:
        ruta = str(f).replace("\\", "/")
        nombre = ruta.rsplit("/", 1)[-1]
        if ".dist-info/" not in ruta or not _ES_LICENCIA.search(nombre):
            continue
        origen = Path(d.locate_file(f))
        if not origen.is_file():
            continue
        destino.mkdir(parents=True, exist_ok=True)
        final = destino / nombre
        if final.exists():                              # (dos con el mismo nombre)
            final = destino / (ruta.split(".dist-info/", 1)[-1].replace("/", "_"))
        shutil.copy2(origen, final)
        n += 1
    return n


def licencia_python(destino: Path) -> bool:
    base = Path(sys.base_prefix)
    for c in (base / "LICENSE.txt", base / "LICENSE",
              base / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "LICENSE.txt"):
        if c.is_file():
            destino.mkdir(parents=True, exist_ok=True)
            shutil.copy2(c, destino / "LICENSE.txt")
            return True
    return False


MIT = """MIT License

Copyright (c) 2026 {autor}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


def main() -> int:
    if not DIST.is_dir():
        print("  No encuentro compilacion\\dist\\Accion: primero hay que compilar.")
        return 1
    sacados = limpiar()
    print(f"  Fuera del programa: {len(sacados)} archivos (teclado virtual GPL y FFmpeg, que no se usan)")
    if CARPETA.exists():
        shutil.rmtree(CARPETA)
    CARPETA.mkdir(parents=True)
    filas = []
    version_qt = ""
    for d in distribuciones(modulos_empaquetados()):
        nombre, version = d.metadata["Name"], d.version
        sub = CARPETA / f"{nombre}-{version}"
        n = copiar_licencias(d, sub)
        lic = licencia_de(d)
        if nombre.lower().startswith("pyside6") or nombre.lower() == "shiboken6":
            version_qt = version_qt or version
            sub.mkdir(parents=True, exist_ok=True)
            for t in ("LGPL-3.0.txt", "GPL-3.0.txt"):
                if (TEXTOS / t).is_file():
                    shutil.copy2(TEXTOS / t, sub / t)
                    n += 1
        if nombre.lower() == "lxml" and (TEXTOS / "LGPL-2.1.txt").is_file():
            sub.mkdir(parents=True, exist_ok=True)
            shutil.copy2(TEXTOS / "LGPL-2.1.txt", sub / "LGPL-2.1 (iconv).txt")
            n += 1
        filas.append((nombre, version, lic, sub.name if n else "(ver su sitio)"))
    py_ok = licencia_python(CARPETA / f"Python-{sys.version.split()[0]}")
    filas.insert(0, (f"Python", sys.version.split()[0], "PSF License (y las de sus bibliotecas: OpenSSL, libffi, "
                     "zlib, bzip2, xz…)", f"Python-{sys.version.split()[0]}" if py_ok else "(ver python.org)"))
    vc = sorted({p.name for p in DIST.rglob("*") if re.match(r"(vcruntime|msvcp|concrt|ucrtbase)\d*.*\.dll$", p.name, re.I)})
    (DIST / "LICENSE.txt").write_text(MIT.format(autor=AUTOR), encoding="utf-8")

    mm = ".".join(version_qt.split(".")[:2]) if version_qt else "6"
    lineas = [
        "LICENCIAS DE TERCEROS — ¡Acción! Software Audiovisual",
        "=" * 60,
        "",
        "¡Acción! es software libre bajo la licencia MIT (LICENSE.txt, junto a Accion.exe).",
        "Para funcionar usa los componentes de terceros de esta lista; cada uno conserva su",
        "propia licencia, cuyo texto está en la carpeta indicada.",
        "",
        f"{'Componente':28} {'Versión':12} Licencia  →  carpeta",
        "-" * 60,
    ]
    for nombre, version, lic, sub in filas:
        lineas.append(f"{nombre:28} {version:12} {lic}  →  {sub}")
    lineas += [
        "Diccionario RLA-ES 2.9 (es_CL)        GNU LGPL 3  →  ..\\sistema\\LICENCIA_diccionario.txt",
        "",
        "QT Y PYSIDE6 (LGPL 3)",
        "  Las bibliotecas de Qt van como archivos separados dentro de la carpeta _internal y",
        "  se pueden reemplazar por otras versiones compatibles. Código fuente de esta versión:",
        "    https://download.qt.io/official_releases/QtForPython/pyside6/",
        f"    https://download.qt.io/official_releases/qt/{mm}/",
        "  Componentes de terceros dentro de Qt (FreeType, libpng, HarfBuzz, PDFium…):",
        "    https://doc.qt.io/qt-6/licenses-used-in-qt.html",
        "  Qt es marca de The Qt Company Ltd.",
        "",
        "LXML",
        "  Incluye libxml2 y libxslt (MIT), zlib (licencia zlib) e iconv (GNU LGPL 2.1).",
        "  Código fuente de iconv: https://ftp.gnu.org/pub/gnu/libiconv/",
        "",
        "PYINSTALLER",
        "  El lanzador de Accion.exe es de PyInstaller (GPL 2 o posterior con una excepción",
        "  que permite distribuirlo junto a cualquier programa).",
    ]
    if vc:
        lineas += ["", "MICROSOFT VISUAL C++",
                   "  " + ", ".join(vc) + ": componentes redistribuibles de Microsoft, incluidos según",
                   "  sus condiciones de redistribución."]
    if sacados:
        lineas += ["", "NO INCLUIDOS (el programa no los usa)",
                   "  Qt Virtual Keyboard (GPL 3) y FFmpeg se sacaron de esta copia del programa."]
    lineas += ["", "EL PROFESOR CLAQUETA (🤖, EL ASESOR CON IA)",
               "  Usa Ollama (https://ollama.com, licencia MIT) y un modelo de IA con su propia licencia",
               "  (los sugeridos, Qwen: Apache 2.0). El instalador normal no los trae: ¡Acción! los descarga",
               "  en segundo plano (si se dejó marcado al instalar; quedan en %LOCALAPPDATA%\\Accion\\ia,",
               "  con sus licencias en ia\\licencias) o se instalan aparte.",
               "  El instalador «con IA» sí los trae; sus licencias quedan en la carpeta ia\\licencias",
               "  del programa (LEEME_IA.txt).",
               "  Con una tarjeta gráfica que sirve, ¡Acción! descarga aparte la parte de Ollama para ella",
               "  (tal como viene en su paquete oficial) a %LOCALAPPDATA%\\Accion\\ollama_gpu:",
               "  - con una NVIDIA, bibliotecas de NVIDIA CUDA (cuBLAS, cudart…), que se rigen por la licencia",
               "    de NVIDIA (https://docs.nvidia.com/cuda/eula/); el aviso queda en ollama_gpu\\LEEME_NVIDIA.txt;",
               "  - con una AMD o una Intel (también las integradas), la parte Vulkan: ggml-vulkan (llama.cpp /",
               "    ggml, licencia MIT) y bibliotecas de Microsoft Visual C++ redistribuibles; el aviso queda",
               "    en ollama_gpu\\LEEME_VULKAN.txt."]
    lineas += ["", "EL DICTADO POR VOZ (🎙, F2)",
               "  Usa whisper.cpp (https://github.com/ggml-org/whisper.cpp, © The ggml authors, licencia MIT)",
               "  y un modelo Whisper (small, medium o large-v3-turbo, según el computador; © OpenAI,",
               "  licencia MIT). No vienen en el instalador:",
               "  ¡Acción! los descarga en segundo plano (si se dejó marcado al instalar) a",
               "  %LOCALAPPDATA%\\Accion\\voz, con sus licencias en voz\\licencias. Con una tarjeta NVIDIA",
               "  también baja la versión de whisper.cpp para ella, que incluye bibliotecas de NVIDIA CUDA",
               "  (bajo la licencia de NVIDIA)."]
    lineas += ["", "Las marcas mencionadas pertenecen a sus dueños. Los nombres de los modelos del Profesor",
               "Claqueta (Méliès, Eisenstein, Hitchcock y Tarantino) son un homenaje a esos cineastas: ni",
               "ellos ni sus herederos o representantes tienen relación con ¡Acción! ni lo respaldan."]
    (CARPETA / "LEEME.txt").write_text("﻿" + "\r\n".join(lineas) + "\r\n", encoding="utf-8")
    print(f"  Licencias de terceros: {len(filas)} componentes (carpeta 'Licencias de terceros')")
    return 0


if __name__ == "__main__":
    sys.exit(main())
