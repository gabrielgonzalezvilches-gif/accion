"""generar_eula.py — arma EULA_Accion.rtf (la licencia que muestra el
instalador) a partir del texto de abajo. Si cambias el texto, vuelve a
correr:  python generar_eula.py
"""
import re
from pathlib import Path

VERSION = "1.9.3"
FECHA = "20 de noviembre de 2026"
AUTOR = "Gabriel González Vilches"
INSTAGRAM = "@accionsoftware (instagram.com/accionsoftware)"

# (estilo, texto) — estilos: titulo, sub, h, p, li, nota, mit; **negrita**
TEXTO = [
    ("titulo", "CONTRATO DE LICENCIA DE USO (EULA)"),
    ("sub", f"¡Acción! Software Audiovisual · versión {VERSION}"),
    ("nota", f"Titular: {AUTOR} (en adelante, «el autor»), Chile · Instagram: {INSTAGRAM} · "
             f"Última actualización: {FECHA}"),
    ("p", "Lee esta licencia antes de instalar. Al elegir «Acepto el acuerdo» e instalar o usar ¡Acción!, "
          "aceptas estas condiciones. Si no las aceptas, no instales el programa."),

    ("h", "1. Qué es ¡Acción!"),
    ("p", "¡Acción! es un programa gratuito para escribir guiones y preparar una producción audiovisual: "
          "escaleta, storyboard en 3D, animatic, planta de cámaras y de luces, desglose, plan de rodaje, "
          "citaciones, presupuesto e informes. Está pensado especialmente para estudiantes y docentes de "
          "colegios, liceos, institutos y universidades, y para realizadores independientes."),

    ("h", "2. Una licencia gratuita y libre"),
    ("p", "¡Acción! se distribuye bajo la **licencia MIT** (su texto original está en el Anexo). En palabras "
          "simples, sin pagar nada puedes:"),
    ("li", "instalarlo y usarlo en todos los computadores que quieras: en tu casa, en tu trabajo, en colegios, "
           "liceos, universidades e instituciones públicas o privadas;"),
    ("li", "copiarlo y compartirlo, entregarlo a estudiantes y colegas, y publicarlo en plataformas educativas;"),
    ("li", "estudiar cómo funciona y modificarlo (su código fuente es el archivo accion.py);"),
    ("li", "usarlo en tus proyectos y producciones, también en las comerciales."),
    ("p", "La única condición es que **conserves el aviso de derechos de autor y esta licencia** en todas las "
          "copias o partes importantes del programa. Si hubiera alguna diferencia entre este resumen y el texto "
          "original de la licencia MIT, para los permisos que otorga prevalece el texto original."),

    ("h", "3. El nombre y las versiones modificadas"),
    ("p", "El nombre «¡Acción!» y su logo identifican al proyecto original; la licencia MIT no entrega derechos "
          "sobre ellos. Si distribuyes una versión modificada, indica claramente que es una versión modificada y "
          "quién la modificó, para no confundir a los usuarios ni atribuirle al autor cambios que no hizo."),

    ("h", "4. Tus obras son tuyas"),
    ("p", "Los guiones, storyboards, planos, imágenes, proyectos (.accion) y demás obras que crees con ¡Acción! "
          "son de quien los crea, de acuerdo con la Ley N° 17.336 sobre Propiedad Intelectual. El autor no "
          "adquiere ningún derecho sobre ellos ni los recibe. Los guiones de ejemplo que trae el programa "
          "(terror, comedia, ciencia ficción, drama y suspenso) se pueden usar libremente para aprender y para "
          "enseñar, y también cambiarlos y grabarlos. Sus nombres, teléfonos, correos y direcciones son "
          "inventados."),

    ("h", "5. Privacidad: tus datos se quedan en tu computador"),
    ("li", "¡Acción! **no tiene cuentas de usuario, publicidad ni telemetría**, y no envía tus guiones ni tus "
           "proyectos a ningún servidor."),
    ("li", "Tus proyectos se guardan donde tú elijas; las copias automáticas, en tu carpeta de usuario; y la "
           "configuración, en tu usuario de Windows. **Desinstalar el programa no borra tus proyectos.**"),
    ("li", "Si algo falla, el programa anota el detalle técnico (la versión, el sistema y el error) en un "
           "archivo de texto en tu computador (registro_de_errores.txt, en tu carpeta de datos de ¡Acción!). "
           "**No se envía a ninguna parte**: sirve para encontrar la causa si tú decides compartirlo, y lo "
           "puedes borrar cuando quieras."),
    ("li", "Solo se conecta a internet cuando usas una función que lo necesita: la consulta del clima "
           "(Open-Meteo recibe la ubicación y las fechas de la jornada) y los enlaces que abres en tu navegador (por ejemplo, Google Maps, Gmail o WhatsApp Web), "
           "que se rigen por las condiciones de esos servicios."),
    ("li", "La colaboración en tiempo real funciona dentro de tu red local y solo cuando tú abres una sesión o "
           "te unes a una. Mientras dura, el proyecto (también las fichas con datos de contacto) viaja directo "
           "entre los computadores de la sesión, sin pasar por internet; si el guion tiene PIN, hay que escribirlo "
           "para entrar y los datos personales viajan cifrados. Mientras tienes una sesión abierta como host, los "
           "computadores de tu red que usen «Buscar sesiones» ven tu nombre y el título del guion."),
    ("li", "El **Profesor Claqueta** (el asesor con IA) conversa con Ollama **en tu mismo computador** (dirección 127.0.0.1): tu guion no "
           "sale de él. Para tenerlo, si al instalar dejaste marcado «Preparar al Profesor Claqueta en segundo plano», "
           "¡Acción! descarga una sola vez Ollama (desde GitHub) y un modelo de IA (desde el registro de Ollama), "
           "unos 3 GB, de a poco y sin ocupar toda tu conexión; si usas datos móviles, puedes pausarlo o "
           "apagarlo en su ventana. Si el computador tiene una tarjeta gráfica, descarga además (desde GitHub) la "
           "parte de Ollama para ella, para que responda más rápido: con una NVIDIA, entre 650 y 950 MB; con una "
           "AMD o una Intel (también las integradas), la parte Vulkan, unos 12 MB, y antes de usarla prueba en "
           "tu computador si de verdad acelera. Se puede pausar o apagar en Configuración → Prof. Claqueta. Esas "
           "descargas no envían nada de tus proyectos."),
    ("li", "El **dictado por voz** (F2) graba el micrófono **solo mientras dictas** y lo convierte en texto con "
           "Whisper **en tu mismo computador**: tu voz no sale de él, no se guarda (se borra apenas se escribe el "
           "texto) y no se usa para nada más. Para tenerlo, si al instalar dejaste marcado «Preparar el dictado por "
           "voz», ¡Acción! descarga una sola vez whisper.cpp (desde GitHub) y un modelo Whisper (desde Hugging Face): "
           "el «small», unos 250 MB, en un computador sin tarjeta gráfica, o el «large-v3-turbo», unos 1,6 GB, con "
           "una tarjeta NVIDIA (más la versión de whisper.cpp para ella). Baja de a poco, sin ocupar toda tu "
           "conexión; se puede pausar, apagar, cambiar de calidad o de carpeta en Configuración → Dictado por voz. Esas "
           "descargas no envían nada tuyo."),

    ("h", "6. Datos de otras personas: actores, equipo y estudiantes"),
    ("p", "Si registras datos personales de otras personas (nombres, teléfonos, correos, alergias, dietas, fotos "
          "u otros), eres responsable de contar con su autorización y de tratarlos conforme a la Ley N° 19.628 "
          "sobre Protección de la Vida Privada y sus modificaciones. Si son **estudiantes menores de edad**, pide "
          "la autorización de sus madres, padres o apoderados, en especial para fotos, videos y datos de "
          "contacto. Para los datos más delicados, usa la protección con PIN del programa con un PIN largo (8 o "
          "más caracteres, con letras y números): uno corto evita que los datos se vean a simple vista, pero "
          "se puede adivinar probando."),

    ("h", "7. Componentes de terceros"),
    ("p", "¡Acción! usa software y datos de terceros, cada uno con su propia licencia, que se respeta. Los "
          "textos completos de esas licencias están en la carpeta **«Licencias de terceros»** del programa "
          "(también en el menú Inicio y en Configuración → Versión):"),
    ("li", "**Qt y Qt for Python (PySide6 y Shiboken6)**, © The Qt Company Ltd., bajo la licencia GNU LGPL "
           "versión 3 (https://www.gnu.org/licenses/lgpl-3.0.html). Las bibliotecas de Qt se instalan como "
           "archivos separados en la carpeta del programa y se pueden reemplazar por otras versiones "
           "compatibles. Su código fuente está en https://download.qt.io/official_releases/QtForPython/ y "
           "https://download.qt.io/official_releases/qt/. El programa no incluye los módulos de Qt que solo "
           "tienen licencia GPL o comercial (como Qt Virtual Keyboard), ni FFmpeg."),
    ("li", "**Python**, © Python Software Foundation, bajo la licencia PSF, con las bibliotecas que trae "
           "(OpenSSL, libffi, zlib, bzip2, xz y otras), cada una con su licencia."),
    ("li", "**PyInstaller** (el lanzador del programa), bajo la licencia GPL versión 2 o posterior con su "
           "excepción para el lanzador, que permite distribuirlo junto a cualquier programa."),
    ("li", "**python-docx**, **openpyxl** y **et_xmlfile** (licencia MIT); **lxml** (licencia BSD; incluye "
           "libxml2 y libxslt, con licencia MIT, zlib, e iconv, con licencia GNU LGPL 2.1, cuyo código fuente "
           "está en https://ftp.gnu.org/pub/gnu/libiconv/); **pypdf** (licencia BSD); y **pycrdt** (licencia "
           "MIT) con anyio (MIT), idna (BSD) y typing_extensions (PSF), cuando están incluidos."),
    ("li", "Las bibliotecas de **Microsoft Visual C++** que necesita Windows para ejecutar el programa, "
           "incluidas según las condiciones de redistribución de Microsoft."),
    ("li", "El diccionario del corrector ortográfico es **RLA-ES 2.9** (Recursos Lingüísticos Abiertos del "
           "Español, variante de Chile; https://github.com/sbosio/rla-es), el mismo de LibreOffice, que se "
           "usa bajo la licencia GNU LGPL versión 3. Sus créditos, su licencia completa y el diccionario en su "
           "forma original están en la carpeta «sistema» del programa."),
    ("li", "Los datos del clima son de **Open-Meteo.com** (https://open-meteo.com), bajo la licencia CC BY 4.0; "
           "el programa muestra esa atribución donde aparece el clima. El servicio gratuito de Open-Meteo es "
           "para uso no comercial: si usas ¡Acción! en una actividad comercial, la consulta del clima queda "
           "sujeta a las condiciones de Open-Meteo (que para ese uso piden una suscripción), o puedes no usarla."),
    ("li", "El **Profesor Claqueta** usa **Ollama** (https://ollama.com, licencia MIT) y un modelo de IA de la familia "
           "**Qwen** (licencia Apache 2.0). El instalador «con IA» los trae; con el instalador normal, ¡Acción! "
           "los descarga en segundo plano (si lo dejaste marcado) o los instalas tú. Sus licencias quedan en la "
           "carpeta «ia\\licencias» (del programa, o de tus datos de usuario si se descargaron). Si eliges otro "
           "modelo, revisa su licencia. Si el computador tiene una tarjeta gráfica que sirve, ¡Acción! descarga "
           "aparte la parte de Ollama para ella, tal como viene en su paquete oficial, y la deja en «ollama_gpu», en "
           "tus datos de usuario: para una **NVIDIA**, bibliotecas de **NVIDIA CUDA** que se rigen por la licencia "
           "de NVIDIA (https://docs.nvidia.com/cuda/eula/), con su aviso en «LEEME_NVIDIA.txt»; para una **AMD** o "
           "una **Intel**, la parte **Vulkan** (ggml-vulkan, de llama.cpp / ggml, licencia MIT, con bibliotecas de "
           "Microsoft Visual C++ redistribuibles según las condiciones de Microsoft), con su aviso en "
           "«LEEME_VULKAN.txt». Se puede apagar en Configuración → Prof. Claqueta."),
    ("li", "El **dictado por voz** usa **whisper.cpp** (https://github.com/ggml-org/whisper.cpp, © The ggml "
           "authors, licencia MIT) y un modelo **Whisper** (small, medium o large-v3-turbo, según el computador; "
           "© OpenAI, licencia MIT), en el formato de whisper.cpp. La versión para tarjetas NVIDIA incluye bibliotecas de **NVIDIA CUDA**, que se rigen "
           "por la licencia de NVIDIA. Se descargan aparte (no vienen en el instalador) y sus licencias quedan en "
           "«voz\\licencias», en tus datos de usuario."),

    ("h", "8. Marcas"),
    ("p", "Final Draft, Celtx, Blender, Photoshop, Premiere, Excel, Word, Gmail, Outlook, WhatsApp, Zoom, Google Meet, "
          "TikTok, YouTube, Windows, Qt y las demás marcas que se nombran en el programa o en su documentación "
          "pertenecen a sus dueños. Se mencionan solo para describir compatibilidad (por ejemplo, abrir o "
          "guardar un formato) o como referencia. ¡Acción! no está asociado con esas empresas ni cuenta con su "
          "patrocinio o respaldo. Los nombres de los modelos del Profesor Claqueta (Méliès, Eisenstein, "
          "Hitchcock y Tarantino) son un homenaje a esos cineastas: ni ellos ni sus herederos o representantes "
          "tienen relación con ¡Acción! ni lo patrocinan o respaldan."),

    ("h", "9. Sin garantía"),
    ("p", "¡Acción! se entrega gratis y «tal cual», **sin garantías de ningún tipo**, ni expresas ni implícitas, "
          "incluidas las de comerciabilidad, idoneidad para un propósito determinado y no infracción. Haz "
          "respaldos de tus proyectos. Lo que calcula el programa (duraciones, posición del sol, clima, "
          "distancias, presupuestos y planes de rodaje) es una estimación de apoyo: la seguridad del rodaje y "
          "las decisiones de producción son responsabilidad de quien las toma. El IVA del presupuesto se calcula "
          "con la tasa y las exenciones que elige quien usa el programa (la tasa sugerida por país es solo una "
          "referencia): no es asesoría contable ni tributaria. Las sugerencias del Profesor Claqueta las "
          "genera una IA: pueden equivocarse o parecerse a otras obras, y la decisión de usarlas, y lo que "
          "resulte de ello, es de quien escribe. Lo mismo vale para lo que escribe la IA: los guiones de la "
          "opción «Escribir un guion» (se abren marcados como escritos con IA) y lo que escribe dentro de tu "
          "guion cuando se lo pides (según la «injerencia» que elijas: solo aconsejar, proponer y esperar tu «sí», "
          "o escribir directo), y también los cambios que hace en tu proyecto (las fichas de personajes, "
          "locaciones, crew, equipamiento y escenas, las jornadas de la Carta Gantt, el presupuesto, los "
          "contratos y seguros y la lista de planos) cuando se lo pides: por defecto te los muestra y espera tu "
          "confirmación; si "
          "eliges que avance solo, los hace sin mostrártelos antes, y revisarlos es responsabilidad de quien lo "
          "eligió. Es un borrador generado automáticamente y quien lo usa debe revisarlo y "
          "asegurarse de no infringir derechos de terceros."),

    ("h", "10. Los guiones de la IA"),
    ("p", "El autor del programa **no se hace responsable por los guiones que la IA pueda generar**, ni por el "
          "uso que se les dé."),
    ("p", "**Cada guion debe ser revisado y visado por adultos (profesores o apoderados) antes de ser "
          "grabado.**"),
    ("p", "La IA no es del autor. Los modelos que usa el Profesor Claqueta (Méliès, Eisenstein, Hitchcock y "
          "Tarantino) son de la familia **Qwen**, que pertenece a **Alibaba Cloud (Grupo Alibaba)** y se entrega "
          "con licencia Apache 2.0. Funcionan con **Ollama**, que pertenece a sus autores (https://ollama.com) y "
          "se entrega con licencia MIT. Si eliges otro modelo, pertenece a quien lo creó."),

    ("h", "11. Limitación de responsabilidad"),
    ("p", "En la máxima medida que permita la ley, el autor no será responsable de ningún reclamo, daño u otra "
          "responsabilidad, sea contractual, extracontractual o de otro tipo, que surja del programa, de su uso o "
          "de cualquier otra gestión relacionada con él, incluida la pérdida de datos o de información."),

    ("h", "12. Actualizaciones"),
    ("p", "Esta versión no busca ni instala actualizaciones por su cuenta. Las versiones nuevas se instalan con "
          "su instalador, encima de la anterior y sin tocar tus proyectos. Cada versión puede traer una versión "
          "actualizada de esta licencia."),

    ("h", "13. Ley aplicable"),
    ("p", "Esta licencia se rige por las leyes de la República de Chile. Cualquier controversia se someterá a "
          "los tribunales ordinarios de justicia competentes de Chile."),

    ("h", "14. Contacto"),
    ("p", f"Para dudas, sugerencias o para reportar errores: {AUTOR}, en Instagram: {INSTAGRAM}."),

    ("h", "Anexo — Licencia MIT (texto original)"),
    ("mit", "MIT License"),
    ("mit", f"Copyright (c) 2026 {AUTOR}"),
    ("mit", "Permission is hereby granted, free of charge, to any person obtaining a copy of this software and "
            "associated documentation files (the \"Software\"), to deal in the Software without restriction, "
            "including without limitation the rights to use, copy, modify, merge, publish, distribute, "
            "sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is "
            "furnished to do so, subject to the following conditions:"),
    ("mit", "The above copyright notice and this permission notice shall be included in all copies or "
            "substantial portions of the Software."),
    ("mit", "THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT "
            "NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND "
            "NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES "
            "OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN "
            "CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."),
]


def _rtf(texto: str) -> str:
    """Escapa para RTF (los acentos como \\uN?) y convierte **negrita**."""
    out = []
    for ch in texto:
        o = ord(ch)
        if ch in "\\{}":
            out.append("\\" + ch)
        elif o < 128:
            out.append(ch)
        elif o < 0x10000:
            out.append(f"\\u{o if o < 32768 else o - 65536}?")
    s = "".join(out)
    return re.sub(r"\*\*(.+?)\*\*", r"{\\b \1}", s)


def armar() -> str:
    # (1.8.8: el texto va en el color «automático» del RTF (\cf0), no en gris
    #  oscuro: el instalador con los estilos de cine es oscuro y ahí Inno Setup
    #  deja los colores fijos tal cual; el automático se vuelve claro sobre
    #  fondo oscuro y negro sobre blanco. Los títulos naranjos se leen en los dos.)
    partes = [r"{\rtf1\ansi\ansicpg1252\deff0\deflang13322"
              r"{\fonttbl{\f0\fswiss\fcharset0 Segoe UI;}{\f1\fmodern\fcharset0 Consolas;}}"
              r"{\colortbl ;\red200\green96\blue0;\red90\green100\blue115;\red40\green40\blue40;}"
              r"\viewkind4\uc1"]
    for estilo, texto in TEXTO:
        t = _rtf(texto)
        if estilo == "titulo":
            partes.append(r"\pard\qc\sb60\sa60\f0\fs30\cf1{\b " + t + r"}\par")
        elif estilo == "sub":
            partes.append(r"\pard\qc\sa60\f0\fs22\cf0{\b " + t + r"}\par")
        elif estilo == "nota":
            partes.append(r"\pard\qc\sa200\f0\fs16\cf0 " + t + r"\par")
        elif estilo == "h":
            partes.append(r"\pard\sb200\sa80\keepn\f0\fs21\cf1{\b " + t + r"}\par")
        elif estilo == "p":
            partes.append(r"\pard\sa100\sl264\slmult1\f0\fs18\cf0 " + t + r"\par")
        elif estilo == "li":
            partes.append(r"\pard\fi-220\li440\tx440\sa60\sl264\slmult1\f0\fs18\cf0 \u8226?\tab " + t + r"\par")
        elif estilo == "mit":
            partes.append(r"\pard\sa100\f1\fs16\cf0 " + t + r"\par")
    partes.append("}")
    return "\r\n".join(partes)


if __name__ == "__main__":
    destino = Path(__file__).resolve().parent / "EULA_Accion.rtf"
    destino.write_text(armar(), encoding="ascii")
    print(f"Listo: {destino.name}")
