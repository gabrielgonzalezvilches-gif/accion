"""preparar_ia.py — deja lista la IA del 🤖 Profesor Claqueta (el Asesor) (Ollama y un modelo) para
el instalador «con IA» (lo llama compilar_instalador.bat).

1. Ollama para Windows (ollama-windows-amd64.zip, licencia MIT): lo toma de
   la carpeta del programa o lo descarga una vez de GitHub (unos 1,6 GB).
   Sin --nvidia le saca las bibliotecas CUDA de NVIDIA (pesan más de 1 GB):
   la IA funciona igual, con el procesador. Vulkan sale siempre: con él,
   Ollama usa la tarjeta de video, y con algunos controladores (NVIDIA, por
   ejemplo) se cae al cargar el modelo (error 0xc0000005).
2. El modelo (por ejemplo qwen3.5:2b): lo descarga una vez con ese mismo
   Ollama; queda en compilacion\\ia_cache\\modelos para las próximas veces.
3. Lo prueba: le pide una respuesta corta, con el Ollama que irá en el
   instalador.
4. Deja todo en compilacion\\ia_paquete: ollama\\, modelos\\ (solo los
   elegidos), licencias\\ e ia.ini.

Uso:  python preparar_ia.py --modelo qwen3.5:2b [--nvidia] [--zip ruta.zip]
      (varios modelos: --modelo "qwen3.5:2b qwen3.5:0.8b")
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
COMP = AQUI / "compilacion"
CACHE = COMP / "ia_cache"
PAQ = COMP / "ia_paquete"
URL_ZIP = "https://github.com/ollama/ollama/releases/latest/download/ollama-windows-amd64.zip"
PUERTO = 11439                      # (uno propio, para no chocar con otro Ollama abierto)
PUERTO_PROGRAMA = 11435             # (el que usa ¡Acción! con la IA incluida)
WIN = sys.platform.startswith("win")
EXE = "ollama.exe" if WIN else "ollama"
ALTERNATIVAS = {"qwen3.5:0.8b": "qwen3:0.6b", "qwen3.5:2b": "qwen3:1.7b",
                "qwen3.5:4b": "qwen3:4b", "qwen3.5:9b": "qwen3:8b"}
_RE_CUDA = re.compile(r"^(cublas|cublaslt|cudart|nvrtc|cufft|curand|cusparse|cudnn)\w*\.(dll|so[.\d]*)$", re.I)

MIT_OLLAMA = """MIT License

Copyright (c) Ollama

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


def gb(n: float) -> str:
    return f"{n / 1024 ** 3:.1f} GB"


def tamano(p: Path) -> int:
    if p.is_file():
        return p.stat().st_size
    return sum(f.stat().st_size for f in p.rglob("*") if f.is_file())


def _sin_proxy():
    return urllib.request.build_opener(urllib.request.ProxyHandler({}))


def bajar(url: str, destino: Path) -> None:
    """Descarga con su avance (por el proxy del sistema, si hay)."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    tmp = destino.with_name(destino.name + ".parcial")
    with urllib.request.urlopen(url, timeout=60) as r, open(tmp, "wb") as f:
        total = int(r.headers.get("Content-Length") or 0)
        hecho, ultimo = 0, 0.0
        while True:
            b = r.read(1 << 20)
            if not b:
                break
            f.write(b)
            hecho += len(b)
            if time.time() - ultimo > 3:
                print(f"        {gb(hecho)}" + (f" de {gb(total)}" if total else ""), flush=True)
                ultimo = time.time()
    tmp.replace(destino)


def zip_ollama(arg: str) -> Path:
    for c in ([Path(arg)] if arg else []) + [AQUI / "ollama-windows-amd64.zip", CACHE / "ollama-windows-amd64.zip"]:
        if c.is_file():
            return c
    print("        Descargando Ollama para Windows (una sola vez, unos 1,6 GB)...", flush=True)
    destino = CACHE / "ollama-windows-amd64.zip"
    bajar(URL_ZIP, destino)
    return destino


def extraer(zp: Path) -> Path:
    """Extrae el zip (si no cambió desde la última vez, usa lo ya extraído)."""
    dest = CACHE / "ollama"
    marca_f = CACHE / "ollama.marca"
    marca = f"{zp.stat().st_size}-{int(zp.stat().st_mtime)}"
    if marca_f.is_file() and marca_f.read_text() == marca and any(dest.rglob(EXE)):
        return next(dest.rglob(EXE)).parent
    shutil.rmtree(dest, ignore_errors=True)
    dest.mkdir(parents=True)
    print(f"        Extrayendo {zp.name}...", flush=True)
    with zipfile.ZipFile(zp) as z:
        z.extractall(dest)
    exes = sorted(dest.rglob(EXE), key=lambda p: len(p.parts))
    if not exes:
        raise SystemExit(f"  El zip no trae {EXE}: ¿es ollama-windows-amd64.zip?")
    if not WIN:
        exes[0].chmod(0o755)
    marca_f.write_text(marca)
    return exes[0].parent


def copiar_runtime(origen: Path, nvidia: bool) -> tuple:
    """Copia Ollama al paquete: sin Vulkan y, sin NVIDIA, sin sus bibliotecas CUDA."""
    dst = PAQ / "ollama"
    shutil.rmtree(dst, ignore_errors=True)
    fuera = []

    def ignorar(carpeta, nombres):
        carpetas_fuera = ("vulkan",) if nvidia else ("cuda", "rocm", "mlx", "vulkan")
        out = []
        for n in nombres:
            p = Path(carpeta, n)
            if (p.is_dir() and n.lower().startswith(carpetas_fuera)) or (not nvidia and p.is_file() and _RE_CUDA.match(n)):
                out.append(n)
                fuera.append(str(p.relative_to(origen)))
        return out
    shutil.copytree(origen, dst, ignore=ignorar)
    if not WIN:
        (dst / EXE).chmod(0o755)
    return dst, fuera


def _get(ruta: str, timeout: float = 2.0) -> dict:
    with _sin_proxy().open(f"http://127.0.0.1:{PUERTO}{ruta}", timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8") or "{}")


def _post(ruta: str, cuerpo: dict, timeout: float):
    req = urllib.request.Request(f"http://127.0.0.1:{PUERTO}{ruta}", data=json.dumps(cuerpo).encode("utf-8"),
                                 headers={"Content-Type": "application/json"}, method="POST")
    return _sin_proxy().open(req, timeout=timeout)


def iniciar_servidor(exe: Path, modelos: Path):
    modelos.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, OLLAMA_HOST=f"127.0.0.1:{PUERTO}", OLLAMA_MODELS=str(modelos), OLLAMA_NO_CLOUD="1",
               OLLAMA_VULKAN="0")              # (igual que ¡Acción!: la prueba es con lo mismo que se instala)
    log = open(CACHE / "ollama_serve.log", "ab")
    p = subprocess.Popen([str(exe), "serve"], env=env, stdin=subprocess.DEVNULL, stdout=log, stderr=log,
                         creationflags=0x08000000 if WIN else 0)
    for _ in range(120):
        if p.poll() is not None:
            raise SystemExit(f"  Ollama se cerró al partir (mira {CACHE / 'ollama_serve.log'}).")
        try:
            v = _get("/api/version", 1.0).get("version", "")
            return p, v
        except Exception:
            time.sleep(0.5)
    p.terminate()
    raise SystemExit("  Ollama no respondió en 60 segundos.")


def detener(p) -> None:
    if p is None or p.poll() is not None:
        return
    p.terminate()
    try:
        p.wait(10)
    except subprocess.TimeoutExpired:
        p.kill()


def cola_log(n: int = 14) -> None:
    """Las últimas líneas del registro de Ollama: dicen por qué falló."""
    log = CACHE / "ollama_serve.log"
    try:
        lineas = log.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return
    print(f"  Lo último que anotó Ollama ({log}):", flush=True)
    for li in lineas[-n:]:
        print("    " + li[:220], flush=True)


def _ruta_manifiesto(modelos: Path, tag: str) -> Path:
    nombre, _, etiqueta = tag.partition(":")
    partes = nombre.split("/")
    if len(partes) == 1:
        partes = ["library"] + partes
    return modelos / "manifests" / "registry.ollama.ai" / Path(*partes) / (etiqueta or "latest")


def descargar_modelo(tag: str, modelos: Path) -> str:
    """Descarga el modelo (o su alternativa, si este Ollama no lo tiene)."""
    for t in [tag] + ([ALTERNATIVAS[tag]] if tag in ALTERNATIVAS else []):
        if _ruta_manifiesto(modelos, t).is_file():
            print(f"        Modelo {t}: ya estaba descargado", flush=True)
            return t
        print(f"        Descargando el modelo {t} (una sola vez)...", flush=True)
        error, ultimo = "", 0.0
        try:
            with _post("/api/pull", {"model": t, "stream": True}, 600) as r:
                for linea in r:
                    linea = linea.strip()
                    if not linea:
                        continue
                    d = json.loads(linea.decode("utf-8"))
                    if d.get("error"):
                        error = str(d["error"])
                        break
                    if d.get("total") and time.time() - ultimo > 3:
                        print(f"        {gb(float(d.get('completed') or 0))} de {gb(float(d['total']))}", flush=True)
                        ultimo = time.time()
                    if d.get("status") == "success":
                        return t
        except urllib.error.HTTPError as ex:
            error = ex.read().decode("utf-8", "replace")
        print(f"        [aviso] {t}: {error or 'la descarga se cortó'}", flush=True)
    raise SystemExit(f"  No se pudo descargar el modelo {tag}.")


def probar(tag: str) -> str:
    """Una respuesta corta: así se sabe que el Ollama del paquete y el modelo funcionan."""
    cuerpo = {"model": tag, "stream": False, "think": False, "keep_alive": 0,
              "messages": [{"role": "user", "content": "Responde solo con la palabra: listo"}],
              "options": {"num_predict": 40, "num_ctx": 2048}}
    for intento in (0, 1):
        try:
            with _post("/api/chat", cuerpo, 900) as r:
                d = json.loads(r.read().decode("utf-8") or "{}")
            t = str((d.get("message") or {}).get("content") or "")
            return re.sub(r"<think>.*?</think>", "", t, flags=re.S).strip()
        except urllib.error.HTTPError as ex:
            detalle = ex.read().decode("utf-8", "replace")
            if intento == 0 and "think" in detalle.lower():
                cuerpo.pop("think", None)
                continue
            print(f"  El modelo {tag} no respondió: {detalle}", flush=True)
            cola_log()
            raise SystemExit(1)
    return ""


def copiar_modelos(tags: list, origen: Path) -> tuple:
    """Solo los modelos elegidos (su manifiesto y sus capas). Devuelve
    (bytes, {tag: texto de su licencia})."""
    dst = PAQ / "modelos"
    shutil.rmtree(dst, ignore_errors=True)
    total, licencias = 0, {}
    for t in tags:
        man = _ruta_manifiesto(origen, t)
        datos = json.loads(man.read_text(encoding="utf-8"))
        destino_man = _ruta_manifiesto(dst, t)
        destino_man.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(man, destino_man)
        for capa in [datos.get("config") or {}] + list(datos.get("layers") or []):
            dig = str(capa.get("digest") or "")
            if not dig:
                continue
            blob = origen / "blobs" / dig.replace(":", "-")
            if not blob.is_file():
                raise SystemExit(f"  Falta una parte del modelo {t} ({dig[:19]}…): bórralo de {origen} y vuelve a intentar.")
            (dst / "blobs").mkdir(parents=True, exist_ok=True)
            final = dst / "blobs" / blob.name
            if not final.exists():
                shutil.copy2(blob, final)
                total += final.stat().st_size
            if str(capa.get("mediaType", "")).endswith(".license"):
                licencias[t] = licencias.get(t, "") + blob.read_text(encoding="utf-8", errors="replace") + "\n"
    return total, licencias


def escribir_licencias(origen_runtime: Path, licencias_modelos: dict, nvidia: bool, version: str) -> None:
    lic = PAQ / "licencias"
    shutil.rmtree(lic, ignore_errors=True)
    (lic / "Ollama").mkdir(parents=True)
    (lic / "Ollama" / "LICENSE.txt").write_text(MIT_OLLAMA, encoding="utf-8")
    for f in origen_runtime.rglob("*"):
        if f.is_file() and re.match(r"(licen[cs]e|copying|notice|third.?party)", f.name, re.I):
            shutil.copy2(f, lic / "Ollama" / f"{f.parent.name}_{f.name}" if f.parent != origen_runtime else lic / "Ollama" / f.name)
    for tag, texto in licencias_modelos.items():
        carpeta = lic / f"Modelo {tag.replace(':', ' ')}"
        carpeta.mkdir(parents=True, exist_ok=True)
        (carpeta / "LICENSE.txt").write_text(texto.strip() + "\n", encoding="utf-8")
    lineas = ["IA DEL ASESOR (incluida en este instalador)", "=" * 60, "",
              f"Ollama {version} — licencia MIT (Ollama/LICENSE.txt). https://github.com/ollama/ollama",
              "  Incluye llama.cpp / ggml (licencia MIT, © The ggml authors) y otras bibliotecas con",
              "  licencias permisivas; su código fuente está en el mismo repositorio.",
              ]
    if nvidia:
        lineas += ["  Incluye bibliotecas de NVIDIA CUDA (cuBLAS, cudart…), redistribuibles según el",
                   "  acuerdo de licencia del CUDA Toolkit de NVIDIA (https://docs.nvidia.com/cuda/eula/)."]
    else:
        lineas += ["  (Sin las bibliotecas CUDA de NVIDIA: funciona con el procesador.)"]
    for tag in licencias_modelos or {}:
        lineas.append(f"Modelo {tag} — su licencia en «Modelo {tag.replace(':', ' ')}/LICENSE.txt».")
    lineas += ["Los modelos Qwen (Alibaba Cloud) se distribuyen bajo la licencia Apache 2.0.", "",
               "El Profesor Claqueta (el asesor con IA de ¡Acción!) funciona solo en este computador: habla con "
               "Ollama en 127.0.0.1."]
    (lic / "LEEME_IA.txt").write_text("﻿" + "\r\n".join(lineas) + "\r\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelo", default="qwen3.5:2b")
    ap.add_argument("--nvidia", default="no")
    ap.add_argument("--zip", default="")
    a = ap.parse_args()
    nvidia = str(a.nvidia).lower() in ("si", "sí", "1", "true", "yes")
    tags = [t for t in re.split(r"[\s,;]+", a.modelo) if t]
    CACHE.mkdir(parents=True, exist_ok=True)
    PAQ.mkdir(parents=True, exist_ok=True)
    zp = zip_ollama(a.zip)
    raiz = extraer(zp)
    runtime, fuera = copiar_runtime(raiz, nvidia)
    if fuera:
        print(f"        {'Sin Vulkan' if nvidia else 'Sin NVIDIA CUDA ni Vulkan'}: {len(fuera)} carpetas/archivos fuera "
              f"({gb(tamano(raiz) - tamano(runtime))} menos)", flush=True)
    modelos_cache = CACHE / "modelos"
    p = None
    try:
        p, version = iniciar_servidor(runtime / EXE, modelos_cache)
        print(f"        Ollama {version} funcionando (puerto {PUERTO})", flush=True)
        usados = [descargar_modelo(t, modelos_cache) for t in tags]
        for t in usados:
            print(f"        Probando {t}...", flush=True)
            r = probar(t)
            print(f"        Respondió: «{r[:60]}»", flush=True)
            if not r:
                raise SystemExit(f"  El modelo {t} respondió vacío.")
    finally:
        detener(p)
    bytes_mod, lic_mod = copiar_modelos(usados, modelos_cache)
    escribir_licencias(raiz, lic_mod, nvidia, version)
    (PAQ / "ia.ini").write_text(f"[ia]\nmodelos = modelos\nmodelo = {usados[0]}\npuerto = {PUERTO_PROGRAMA}\n",
                                encoding="utf-8")
    (PAQ / "modelo.txt").write_text(" ".join(usados), encoding="utf-8")
    t_run = tamano(runtime)
    print(f"        Listo: Ollama {gb(t_run)} + modelo(s) {', '.join(usados)} {gb(bytes_mod)} "
          f"= {gb(t_run + bytes_mod)} (sin comprimir)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
