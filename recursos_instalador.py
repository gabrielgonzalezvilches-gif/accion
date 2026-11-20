"""recursos_instalador.py — prepara lo que necesitan PyInstaller e Inno Setup
para armar el instalador de ¡Acción! (lo llama compilar_instalador.bat).

Crea la carpeta «compilacion» (junto a accion.py) con:
  • version.txt              la versión (la línea  __version__ = "…"  de accion.py)
  • version_info.txt         los datos del .exe (Propiedades → Detalles)
  • accion.ico               el ícono: la claqueta (dibujo propio), la misma de la ventana
  • asistente_grande*.bmp    la imagen del costado del instalador
  • asistente_chico*.bmp     la imagen chica de arriba a la derecha

Uso:  python recursos_instalador.py   (en la carpeta de accion.py)
"""
import io
import re
import struct
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PROGRAMA = AQUI / "accion.py"
SALIDA = AQUI / "compilacion"
AUTOR = "Gabriel González Vilches"
NOMBRE = "¡Acción!"
DESCRIPCION = "¡Acción! Software Audiovisual"


def leer_version() -> str:
    fuente = PROGRAMA.read_text(encoding="utf-8")
    m = re.search(r'^__version__\s*=\s*"([^"]+)"', fuente, re.M)
    if not m:
        raise SystemExit('No encuentro la línea __version__ = "…" en accion.py.')
    return m.group(1)


def numeros_version(v: str) -> tuple:
    nums = [int(x) for x in re.findall(r"\d+", v)][:4]
    return tuple(nums + [0] * (4 - len(nums)))


def escribir_version_info(v: str) -> None:
    """El archivo de versión que PyInstaller pone dentro del .exe."""
    n = numeros_version(v)
    texto = f"""# Datos del ejecutable (los arma recursos_instalador.py)
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={n},
    prodvers={n},
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable('340A04B0', [
        StringStruct('CompanyName', '{AUTOR}'),
        StringStruct('FileDescription', '{DESCRIPCION}'),
        StringStruct('FileVersion', '{v}'),
        StringStruct('InternalName', 'Accion'),
        StringStruct('LegalCopyright', '© 2026 {AUTOR} · Licencia MIT'),
        StringStruct('OriginalFilename', 'Accion.exe'),
        StringStruct('ProductName', '{NOMBRE}'),
        StringStruct('ProductVersion', '{v}')
      ])
    ]),
    VarFileInfo([VarStruct('Translation', [0x340A, 1200])])
  ]
)
"""
    (SALIDA / "version_info.txt").write_text(texto, encoding="utf-8")


# ── Dibujos (con Qt, que ya está instalado para ¡Acción!) ──
def _app():
    from PySide6.QtGui import QGuiApplication
    return QGuiApplication.instance() or QGuiApplication(sys.argv[:1])


def pintar_claqueta(p, x, y, lado) -> None:
    """La claqueta de ¡Acción!: un dibujo propio, hecho con trazos (sin
    fuentes ni emojis), de lado×lado px a partir de (x, y)."""
    from PySide6.QtCore import QPointF, QRectF, Qt
    from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen, QPolygonF
    p.save()
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.translate(x, y)
    p.scale(lado / 64.0, lado / 64.0)
    p.setPen(Qt.PenStyle.NoPen)
    naranjo, blanco, cuerpo = QColor("#ff8c1a"), QColor("#f4f6f8"), QColor("#1f2b38")

    def franjas(caja: QRectF, forma: QPainterPath, inclinacion: float) -> None:
        p.save()
        p.setClipPath(forma)
        p.fillRect(caja, blanco)
        p.setBrush(naranjo)
        h, ancho = caja.height(), 7.5
        xi = caja.left() - h - ancho
        while xi < caja.right() + h:
            d = h * inclinacion
            p.drawPolygon(QPolygonF([QPointF(xi, caja.bottom()), QPointF(xi + d, caja.top()),
                                     QPointF(xi + d + ancho, caja.top()), QPointF(xi + ancho, caja.bottom())]))
            xi += 2 * ancho
        p.restore()

    # el cuerpo (la pizarra)
    p.setBrush(cuerpo)
    p.drawRoundedRect(QRectF(5, 27, 54, 32), 5, 5)
    # la franja fija, arriba del cuerpo
    caja = QRectF(5, 27, 54, 8.5)
    forma = QPainterPath()
    forma.addRoundedRect(QRectF(5, 27, 54, 32), 5, 5)
    banda = QPainterPath()
    banda.addRect(caja)
    franjas(caja, forma.intersected(banda), 0.75)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(QColor("#3b4a5c") if lado >= 30 else cuerpo, max(1.2, 0.9 * 64.0 / lado)))
    p.drawRoundedRect(QRectF(5, 27, 54, 32), 5, 5)
    p.setPen(Qt.PenStyle.NoPen)
    # el brazo, entreabierto (gira en la bisagra de la izquierda)
    p.save()
    p.translate(7, 25.5)
    p.rotate(-17)
    p.translate(-7, -25.5)
    brazo = QRectF(5, 16.5, 54, 8.5)
    forma_b = QPainterPath()
    forma_b.addRoundedRect(brazo, 2.2, 2.2)
    franjas(brazo, forma_b, -0.75)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(cuerpo, max(1.2, 0.9 * 64.0 / lado)))     # (borde: que se vea sobre fondo blanco)
    p.drawRoundedRect(brazo, 2.2, 2.2)
    p.setPen(Qt.PenStyle.NoPen)
    p.restore()
    # la bisagra
    p.setBrush(QColor("#9aa8b6"))
    p.drawEllipse(QPointF(7.6, 26.2), 2.9, 2.9)
    # «¡Acción!»: el triángulo de reproducir
    p.setBrush(naranjo)
    p.drawPolygon(QPolygonF([QPointF(42.5, 40.5), QPointF(42.5, 54.5), QPointF(54, 47.5)]))
    if lado >= 30:                                   # (los renglones de la pizarra, si se alcanzan a ver)
        p.setBrush(QColor("#4c5d71"))
        p.drawRoundedRect(QRectF(11, 41, 25, 3), 1.5, 1.5)
        p.drawRoundedRect(QRectF(11, 48.5, 17, 3), 1.5, 1.5)
    p.restore()


def dibujar_claqueta(lado: int):
    """La claqueta de ¡Acción! (la misma de la ventana del programa: un
    dibujo propio, no un emoji ni una fuente), de lado×lado px."""
    from PySide6.QtGui import QColor, QImage, QPainter
    _app()
    img = QImage(lado, lado, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(QColor(0, 0, 0, 0))
    p = QPainter(img)
    pintar_claqueta(p, 0, 0, lado)
    p.end()
    return img


def _png(img) -> bytes:
    from PySide6.QtCore import QBuffer, QByteArray, QIODevice
    ba = QByteArray()
    buf = QBuffer(ba)
    buf.open(QIODevice.OpenModeFlag.WriteOnly)
    img.save(buf, "PNG")
    buf.close()
    return bytes(ba)


def escribir_icono() -> None:
    """accion.ico con todos los tamaños de Windows (cada uno dibujado a su tamaño)."""
    lados = (16, 20, 24, 32, 40, 48, 64, 96, 128, 256)
    datos = [_png(dibujar_claqueta(l)) for l in lados]
    cab = struct.pack("<HHH", 0, 1, len(lados))
    desplazamiento = 6 + 16 * len(lados)
    entradas = b""
    for l, d in zip(lados, datos):
        entradas += struct.pack("<BBBBHHII", l % 256, l % 256, 0, 0, 1, 32, len(d), desplazamiento)
        desplazamiento += len(d)
    (SALIDA / "accion.ico").write_bytes(cab + entradas + b"".join(datos))


def _imagen_asistente(w: int, h: int, v: str, chica: bool):
    from PySide6.QtCore import QPointF, QRect, QRectF, Qt
    from PySide6.QtGui import QColor, QFont, QImage, QLinearGradient, QPainter, QPen
    _app()
    img = QImage(w, h, QImage.Format.Format_RGB32)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
    g = QLinearGradient(0, 0, 0, h)
    g.setColorAt(0.0, QColor("#16233a"))
    g.setColorAt(1.0, QColor("#0a0f18"))
    p.fillRect(QRectF(0, 0, w, h), g)
    if chica:
        lado = int(min(w, h) * 0.86)
        p.drawImage(QPointF((w - lado) / 2, (h - lado) / 2), dibujar_claqueta(lado))
    else:
        u = w / 164.0
        # un brillo cálido, como la luz de un set
        from PySide6.QtGui import QRadialGradient
        rg = QRadialGradient(QPointF(w * 0.5, h * 0.3), w * 0.75)
        rg.setColorAt(0.0, QColor(255, 140, 26, 70))
        rg.setColorAt(1.0, QColor(255, 140, 26, 0))
        p.fillRect(QRectF(0, 0, w, h), rg)
        lado = int(92 * u)
        p.drawImage(QPointF((w - lado) / 2, 46 * u), dibujar_claqueta(lado))
        f = QFont("Segoe UI")
        f.setBold(True)
        f.setPixelSize(int(27 * u))
        p.setFont(f)
        p.setPen(QColor("#ff8c1a"))
        p.drawText(QRect(0, int(150 * u), w, int(36 * u)), Qt.AlignmentFlag.AlignCenter, NOMBRE)
        f2 = QFont("Segoe UI")
        f2.setPixelSize(int(11.5 * u))
        p.setFont(f2)
        p.setPen(QColor("#e8edf4"))
        p.drawText(QRect(0, int(188 * u), w, int(18 * u)), Qt.AlignmentFlag.AlignCenter, "Software Audiovisual")
        p.setPen(QPen(QColor(255, 140, 26, 150), max(1.0, u)))
        p.drawLine(QPointF(w * 0.3, 214 * u), QPointF(w * 0.7, 214 * u))
        f3 = QFont("Segoe UI")
        f3.setPixelSize(int(10 * u))
        p.setFont(f3)
        p.setPen(QColor("#9fb0c6"))
        p.drawText(QRect(int(8 * u), int(222 * u), w - int(16 * u), int(48 * u)),
                   Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop | Qt.TextFlag.TextWordWrap,
                   f"Versión {v}\nGuion · Storyboard · Producción")
        f4 = QFont("Segoe UI")
        f4.setPixelSize(int(8.5 * u))
        p.setFont(f4)
        p.setPen(QColor("#64748b"))
        p.drawText(QRect(0, h - int(24 * u), w, int(16 * u)), Qt.AlignmentFlag.AlignCenter,
                   "Gratis y de uso libre (MIT)")
    p.end()
    return img.convertToFormat(QImage.Format.Format_RGB888)


def escribir_imagenes_asistente(v: str) -> None:
    # (Inno Setup elige la que mejor calza con la escala de la pantalla)
    for nombre, (w, h), chica in (("asistente_grande.bmp", (164, 314), False),
                                  ("asistente_grande_2x.bmp", (410, 797), False),
                                  ("asistente_chico.bmp", (55, 55), True),
                                  ("asistente_chico_2x.bmp", (138, 140), True)):
        _imagen_asistente(w, h, v, chica).save(str(SALIDA / nombre), "BMP")


def main() -> int:
    if not PROGRAMA.exists():
        print(f"No encuentro accion.py en {AQUI}")
        return 1
    SALIDA.mkdir(exist_ok=True)
    v = leer_version()
    (SALIDA / "version.txt").write_text(v, encoding="ascii")
    escribir_version_info(v)
    try:
        escribir_icono()
        escribir_imagenes_asistente(v)
    except Exception as ex:                     # (sin ícono igual se puede compilar)
        print(f"  (aviso) no se pudieron dibujar el icono y las imagenes: {ex}")
    print(f"  Version {v}: recursos listos en la carpeta compilacion")
    m = re.search(r'^URL_ACTUALIZAR_DEFECTO\s*=\s*"([^"]*)"', PROGRAMA.read_text(encoding="utf-8"), re.M)
    if m and m.group(1).strip():
        print(f"  Actualizaciones: {m.group(1).strip()}")
    else:
        print("  [aviso] accion.py no trae la direccion de las actualizaciones (URL_ACTUALIZAR_DEFECTO):")
        print("          los programas que se instalen con este instalador no van a buscar versiones nuevas")
        print("          solos (cada uno tendria que ponerla en Configuracion - Version).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
