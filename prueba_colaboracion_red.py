"""prueba_colaboracion_red.py — la colaboración de ¡Acción! con varios
programas de verdad, conectados por TCP (en este mismo computador).

Abre un host y N invitados, cada uno en su propio proceso, con su propia
ventana (sin mostrarla). Todos escriben a la vez durante unos segundos —en
el mismo bloque, Enter, borrar, Ctrl+Z, notas, negritas, fichas, jornadas—
y al final cada uno guarda cómo le quedó el proyecto. La prueba pasa si
todos quedaron iguales.

Uso:   python prueba_colaboracion_red.py [invitados] [segundos] [semilla]
       (por defecto: 2 invitados, 12 segundos)
Lo usa pruebas_accion.py; también sirve sola.
"""
import json
import os
import random
import subprocess
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PUERTO = int(os.environ.get("ACCION_PUERTO_PRUEBA", "19977"))


def _cargar():
    import importlib.util
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    spec = importlib.util.spec_from_file_location("accion", AQUI / "accion.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["accion"] = m
    spec.loader.exec_module(m)
    return m


def participante(rol: str, nombre: str, n_invitados: int, segundos: float,
                 semilla: int, salida: str, extra: str = "") -> None:
    m = _cargar()
    from PySide6.QtCore import QSettings, Qt
    from PySide6.QtWidgets import QApplication, QMessageBox, QInputDialog
    from PySide6.QtTest import QTest
    m.PUERTO_COLAB = PUERTO
    m.settings_app = lambda: QSettings("AccionFilmtools", f"AccionPruebaRed{nombre}")
    m.settings_app().setValue("bienvenida_oculta", True)
    app = QApplication(sys.argv[:1])
    avisos = []
    QMessageBox.warning = staticmethod(lambda *a, **k: avisos.append(str(a[1:3])) or QMessageBox.StandardButton.Ok)
    QMessageBox.information = staticmethod(lambda *a, **k: avisos.append(str(a[1:3])) or QMessageBox.StandardButton.Ok)
    QMessageBox.question = staticmethod(lambda *a, **k: QMessageBox.StandardButton.Yes)
    QInputDialog.getMultiLineText = staticmethod(lambda *a, **k: (f"nota de {nombre}", True))
    r = random.Random(semilla)
    # (sin ventanas que esperan respuesta: nadie las contestaría)
    m.VentanaPrincipal._al_detectar_personaje_nuevo = lambda self, *a: None
    vp = m.VentanaPrincipal()
    rt = vp._colab_runtime
    ses = vp._colab
    E, B = m.Elem, m.Bloque

    def esperar(cond, s):
        t = time.time()
        while time.time() - t < s:
            app.processEvents()
            QTest.qWait(15)
            if cond():
                return True
        return cond()

    if rol == "host":
        doc = m.Documento()
        doc.titulo = "Prueba en red"
        doc.bloques = [B(E.ESCENA, "INT. SALA DE CLASES - DÍA"),
                       B(E.ACCION, "Rocío entra con la mochila. Ñandú la sigue."),
                       B(E.PERSONAJE, "ROCÍO"), B(E.DIALOGO, "¿Hay alguien aquí?"),
                       B(E.ESCENA, "EXT. PATIO - NOCHE"),
                       B(E.ACCION, "Silencio. 🎬 Se apaga la luz.")]
        doc.fichas["ROCÍO"] = m.Ficha(personaje="ROCÍO", actor_nombre="Actriz uno")
        vp.editor.cargar_documento(doc)
        nivel = "notas" if extra == "notas" else "editar"
        assert ses.iniciar_host("Host 🎬", nivel, 8), "no se pudo abrir el puerto"
        print("LISTO", flush=True)
        if not esperar(lambda: len(rt.participantes) >= 1 + n_invitados, 30):
            print("ERROR faltan invitados", len(rt.participantes), flush=True)
    else:
        ses.unirse("127.0.0.1", nombre, "")
        if not esperar(lambda: rt.conectado and ses.activa, 20):
            print("ERROR no entró", rt.estado, avisos, flush=True)
            sys.exit(2)
        esperar(lambda: len(rt.participantes) >= 1 + n_invitados, 30)
        print("DENTRO", flush=True)
    esperar(lambda: False, 0.5)

    ed = vp.editor
    from PySide6.QtCore import QEvent
    from PySide6.QtGui import QKeyEvent

    def teclear(texto: str) -> None:
        # (como un teclado de verdad, también con tildes, ñ y emojis)
        for ch in texto:
            for tipo in (QEvent.Type.KeyPress, QEvent.Type.KeyRelease):
                QApplication.sendEvent(ed, QKeyEvent(tipo, 0, Qt.KeyboardModifier.NoModifier, ch))

    palabras = ["hola", "ñandú", "corre", "¿qué?", "¡ya!", "café", "luz", "😀",
                "sí", "mañana", "atrás", "pizarra"]
    fin = time.time() + segundos
    acciones = 0
    cortes = 0
    mis_jornadas = []
    corte_en = -1
    while time.time() < fin:
        app.processEvents()
        if ed.isReadOnly():
            # (con permiso de notas: una nota de vez en cuando)
            if r.random() < 0.05:
                n = len(ed.documento.bloques)
                ed._mover_cursor_a(r.randrange(n), 0)
                ed._agregar_nota_desde_menu()
            QTest.qWait(r.randint(20, 90))
            continue
        n = len(ed.documento.bloques)
        k = r.random()
        try:
            if k < 0.45:
                i = r.randrange(n)
                t = ed.documento.bloques[i].texto
                ed._mover_cursor_a(i, r.randint(0, len(t)))
                teclear(" " + r.choice(palabras))
            elif k < 0.55:
                i = r.randrange(n)
                ed._mover_cursor_a(i, len(ed.documento.bloques[i].texto))
                QTest.keyClick(ed, Qt.Key.Key_Return)
                teclear(r.choice(palabras))
            elif k < 0.67:
                i = r.randrange(n)
                t = ed.documento.bloques[i].texto
                if t:
                    ed._mover_cursor_a(i, r.randint(1, len(t)))
                    for _ in range(r.randint(1, 3)):
                        QTest.keyClick(ed, Qt.Key.Key_Backspace)
            elif k < 0.72 and n > 3:
                i = r.randrange(1, n)
                ed._mover_cursor_a(i, 0)
                QTest.keyClick(ed, Qt.Key.Key_Backspace)    # juntar con el anterior
            elif k < 0.77:
                QTest.keyClick(ed, Qt.Key.Key_Z, Qt.KeyboardModifier.ControlModifier)
            elif k < 0.80:
                QTest.keyClick(ed, Qt.Key.Key_Y, Qt.KeyboardModifier.ControlModifier)
            elif k < 0.84:
                i = r.randrange(n)
                ed._mover_cursor_a(i, 0)
                ed._agregar_nota_desde_menu()
            elif k < 0.88:
                i = r.randrange(n)
                t = ed.documento.bloques[i].texto
                if len(t) > 3:
                    from PySide6.QtGui import QTextCursor
                    qb = ed.document().findBlockByNumber(i)
                    c = QTextCursor(qb)
                    a = r.randint(0, len(t) - 2)
                    c.setPosition(qb.position() + a)
                    c.setPosition(qb.position() + min(len(t), a + r.randint(1, 4)),
                                  QTextCursor.MoveMode.KeepAnchor)
                    ed.setTextCursor(c)
                    ed._aplicar_formato_generico({"negrita": True})
            elif k < 0.92:
                f = ed.documento.fichas.setdefault(
                    f"PJ {nombre}", m.Ficha(personaje=f"PJ {nombre}"))
                f.actor_nombre = f"{nombre} {acciones}"
                ses._datos_sucios = True    # (como si se hubiera usado la ventana de fichas)
            elif k < 0.95:
                d = ed.documento
                d.jornadas.append(m.Jornada(nombre=f"Jornada de {nombre} {acciones}"))
                mis_jornadas.append(f"Jornada de {nombre} {acciones}")
                vp._colab_emitir_gantt()
            else:
                ed.documento.fichas["ROCÍO"].biografia = f"según {nombre} ({acciones})"
                ses._datos_sucios = True
        except Exception as ex:
            import traceback
            traceback.print_exc()
            print("ERROR acción", ex, flush=True)
        acciones += 1
        if extra == "corte" and rol != "host" and cortes == 0 and time.time() > fin - segundos / 2:
            # (el WiFi se corta: se sigue escribiendo y vuelve sola)
            cortes += 1
            corte_en = acciones
            for s_ in list(rt._sockets):
                s_.abort()
        QTest.qWait(r.randint(15, 70))
    # que todo llegue
    ses.enviar_local()
    ses.enviar_datos_locales()
    if extra == "corte" and rol != "host":
        esperar(lambda: rt.conectado, 20)
    esperar(lambda: False, 4.0)
    ses.enviar_local()
    ses.enviar_datos_locales()
    esperar(lambda: False, 2.5)
    d = ed.documento
    claves = [list(map(lambda x: list(x) if isinstance(x, tuple) else x, m._clave_bloque(b)))
              for b in d.bloques]
    datos = ses._estado_datos() if ses.activa else {}
    estado = {"rol": rol, "nombre": nombre, "acciones": acciones,
              "claves": claves,
              "fichas": {k: [v.actor_nombre, v.biografia] for k, v in d.fichas.items()},
              "jornadas": sorted(j.nombre for j in d.jornadas),
              "datos_ok": bool(datos), "estado_red": rt.estado,
              "nivel": rt.mi_nivel(), "avisos": avisos[-3:],
              "cortes": cortes, "mis_jornadas": mis_jornadas, "corte_en": corte_en,
              "verificar": (ses.guion.verificar() if ses.guion is not None else None),
              "huella": ses.huella()}
    Path(salida).write_text(json.dumps(estado, ensure_ascii=False), encoding="utf-8")
    print("FIN", acciones, flush=True)
    if rol == "host":
        esperar(lambda: len(rt.participantes) <= 1, 15)
        rt.detener()
    else:
        vp._desconectar_colab(preguntar=False)
    esperar(lambda: False, 0.3)


def correr(n_invitados: int = 2, segundos: float = 12.0, semilla: int = 1,
           extra: str = "", carpeta: Path = None) -> dict:
    """Corre la prueba completa; devuelve {"ok", "detalle", "estados"}."""
    carpeta = Path(carpeta or (AQUI / "pruebas_resultado" / "colab_red"))
    carpeta.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, QT_QPA_PLATFORM="offscreen", PYTHONIOENCODING="utf-8")
    procesos = []

    def lanzar(rol, nombre, k):
        salida = carpeta / f"{nombre}.json"
        if salida.exists():
            salida.unlink()
        p = subprocess.Popen(
            [sys.executable, str(Path(__file__).resolve()), "--participante", rol,
             nombre, str(n_invitados), str(segundos), str(semilla * 100 + k),
             str(salida), extra],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env,
            text=True, encoding="utf-8", errors="replace")
        procesos.append((nombre, p, salida))
        return p
    host = lanzar("host", "Host", 0)
    linea = ""
    t0 = time.time()
    while time.time() - t0 < 60:
        linea = host.stdout.readline()
        if not linea or linea.startswith("LISTO") or linea.startswith("ERROR"):
            break
    if not linea.startswith("LISTO"):
        host.kill()
        return {"ok": False, "detalle": "el host no partió: " + linea, "estados": []}
    for k in range(n_invitados):
        lanzar("invitado", f"Invitado{k + 1}", k + 1)
    salidas = {}
    for nombre, p, _s in procesos:
        try:
            out, _ = p.communicate(timeout=segundos + 120)
        except subprocess.TimeoutExpired:
            p.kill()
            out = "(se colgó)"
        salidas[nombre] = out
    estados = []
    for nombre, _p, s in procesos:
        if not s.exists():
            return {"ok": False, "detalle": f"{nombre} no terminó:\n{salidas[nombre][-1500:]}",
                    "estados": estados}
        estados.append(json.loads(s.read_text(encoding="utf-8")))
    base = estados[0]
    problemas = []
    for e in estados:
        if "ERROR" in salidas[e["nombre"]]:
            problemas.append(f"{e['nombre']}: " + salidas[e["nombre"]][-800:])
        if e["verificar"] is False:
            problemas.append(f"{e['nombre']}: la copia incremental no calzaba")
    for e in estados[1:]:
        if e["claves"] != base["claves"]:
            dif = next((i for i, (a, b) in enumerate(zip(e["claves"], base["claves"])) if a != b),
                       min(len(e["claves"]), len(base["claves"])))
            problemas.append(f"guion distinto en {e['nombre']} (bloque {dif}; "
                             f"{len(e['claves'])} vs {len(base['claves'])} bloques)")
        if e["fichas"] != base["fichas"]:
            problemas.append(f"fichas distintas en {e['nombre']}")
        if e["jornadas"] != base["jornadas"]:
            problemas.append(f"jornadas distintas en {e['nombre']}")
        if e.get("huella") != base.get("huella"):
            problemas.append(f"la huella de {e['nombre']} ({e.get('huella')}) no es la del host "
                             f"({base.get('huella')})")
    for e in estados:
        perdidas = [j for j in e.get("mis_jornadas", []) if j not in base["jornadas"]]
        if perdidas:
            problemas.append(f"se perdieron {len(perdidas)} jornadas de {e['nombre']} "
                             f"({', '.join(perdidas)}; corte en la acción {e.get('corte_en')})")
    acciones = sum(e["acciones"] for e in estados)
    detalle = (f"{len(estados)} programas, {acciones} cambios a la vez, "
               f"{len(base['claves'])} bloques al final, {len(base['jornadas'])} jornadas, "
               f"huella {base.get('huella')} en todos")
    if problemas:
        return {"ok": False, "detalle": "; ".join(problemas)[:3000], "estados": estados}
    return {"ok": True, "detalle": detalle, "estados": estados}


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--participante":
        rol, nombre, n, seg, sem, salida = sys.argv[2:8]
        extra = sys.argv[8] if len(sys.argv) > 8 else ""
        participante(rol, nombre, int(n), float(seg), int(sem), salida, extra)
    else:
        n = int(sys.argv[1]) if len(sys.argv) > 1 else 2
        seg = float(sys.argv[2]) if len(sys.argv) > 2 else 12.0
        sem = int(sys.argv[3]) if len(sys.argv) > 3 else 1
        extra = sys.argv[4] if len(sys.argv) > 4 else ""
        res = correr(n, seg, sem, extra)
        print(("✓ " if res["ok"] else "✗ ") + res["detalle"])
        sys.exit(0 if res["ok"] else 1)
