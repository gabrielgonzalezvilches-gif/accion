"""guiones_ejemplo.py — arma los cinco guiones de ejemplo de ¡Acción! (los
que van en el instalador, en la carpeta «guiones de ejemplo»).

Son cortometrajes para grabar en un liceo, con adolescentes o niños:
  🕯 Terror · La sala 13
  😂 Comedia · Doña Pepa se escapó
  🛸 Ciencia ficción · Señal del futuro
  🎭 Drama · La voz de Rocío
  🔍 Suspenso · Último recreo
Cada uno trae TODO el programa usado: el guion (escenas, acción, diálogos,
paréntesis, diálogo doble, planos, transiciones y actos), los tags con
valor, las notas, la portada, la premisa, la escaleta, la Pizarra de beats,
el análisis por escena, la versión corta, las fichas (elenco, locaciones,
crew y equipamiento, con lo de la Call Sheet), la lista de planos, el
storyboard en 3D (paredes, muebles, personas, una cámara por plano, el sol
en los exteriores y un recorrido), la Carta Gantt, el presupuesto (fondos,
gastos, pagos y, en algunos, IVA y grupos de categorías) y los contratos y
seguros.

Las fechas se escriben desde hoy (`ejemplo_fecha_base`); ¡Acción! las corre
al presente cada vez que se abre un ejemplo, así que la Carta Gantt nunca
queda en una fecha que ya pasó.

Todos los datos son inventados: los teléfonos son +56 9 0000 xxxx y los
correos, @correo.example (dominios que no pueden ser de nadie).

Uso:  python guiones_ejemplo.py [carpeta]   (por defecto, «guiones de ejemplo»
      junto a accion.py)
"""
import importlib.util
import os
import re
import sys
from datetime import date, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent


def _modulo_accion():
    if "accion" in sys.modules:
        return sys.modules["accion"]
    spec = importlib.util.spec_from_file_location("accion", AQUI / "accion.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["accion"] = m
    spec.loader.exec_module(m)
    return m


# ═══════════════════════════════════════════════════════════════════════
#  El guion, escrito con un marcado corto (una línea por bloque):
#    ACTO: …  FINACTO: …   E: encabezado   A: acción   PL: plano
#    P: PERSONAJE   P2: PERSONAJE (diálogo doble, a la vez que el anterior)
#    (…) paréntesis   D: diálogo   T: transición   N: nota del bloque anterior
#  Dentro de una acción o diálogo, un tag con valor:
#    [[texto|categoría|valor|tipo|cantidad]]  (tipo: unica, cantidad o diaria)
#  y **negrita**.
# ═══════════════════════════════════════════════════════════════════════

_TAG = re.compile(r"\[\[([^\]|]+)(?:\|([a-z_]+))?(?:\|(\d*))?(?:\|(unica|cantidad|diaria))?(?:\|(\d+))?\]\]")


def bloques_desde_marcado(m, texto: str, autor: str, fecha_nota: str) -> list:
    E = m.Elem
    tipos = {"ACTO": E.ACTO_INICIO, "FINACTO": E.ACTO_FIN, "E": E.ESCENA, "A": E.ACCION,
             "PL": E.PLANO, "P": E.PERSONAJE, "P2": E.PERSONAJE, "D": E.DIALOGO, "T": E.TRANSICION}
    out = []
    for linea in texto.strip().splitlines():
        linea = linea.strip()
        if not linea:
            continue
        if linea.startswith("("):
            out.append(m.Bloque(E.PARENTESIS, m.aplicar_caso_a_texto(E.PARENTESIS, linea)))
            continue
        clave, _, resto = linea.partition(":")
        resto = resto.strip()
        if clave == "N":
            out[-1].tags.append({"categoria": "nota", "contenido": resto, "autor": autor,
                                 "fecha": fecha_nota})
            continue
        elem = tipos[clave]
        tags, formatos, visible, pos = [], [], "", 0
        for t in _TAG.finditer(resto):
            visible += resto[pos:t.start()]
            ini = len(visible)
            visible += t.group(1)
            if t.group(2):
                tag = {"categoria": t.group(2), "contenido": t.group(1), "desde": ini,
                       "hasta": len(visible), "autor": autor, "fecha": fecha_nota}
                if t.group(3):
                    tag["valor"] = t.group(3)
                tag["tipo_compra"] = t.group(4) or "unica"
                if t.group(5):
                    tag["cantidad"] = int(t.group(5))
                tags.append(tag)
            pos = t.end()
        visible += resto[pos:]
        while "**" in visible:                           # **negrita**
            a = visible.index("**")
            b = visible.index("**", a + 2)
            for tg in tags:                              # (lo que va después se corre)
                for k in ("desde", "hasta"):
                    if tg[k] > b:
                        tg[k] -= 4
                    elif tg[k] > a:
                        tg[k] -= 2
            visible = visible[:a] + visible[a + 2:b] + visible[b + 2:]
            formatos.append({"desde": a, "hasta": b - 2, "negrita": True})
        visible = m.aplicar_caso_a_texto(elem, visible)
        b_ = m.Bloque(elem, visible, tags=tags, formatos=formatos)
        if clave == "P2":
            b_.doble = True
        out.append(b_)
    return out


# ═══════════════════════════════════════════════════════════════════════
#  Los cinco guiones
# ═══════════════════════════════════════════════════════════════════════

TERROR = """
E: INT. LICEO - SALA DE AUDIOVISUALES - NOCHE
A: La feria científica terminó hace una hora. Sillas dadas vuelta, un [[proyector|camara|0]] apagado y carteles a medio despegar.
A: ISIDORA (15) graba todo con su celular. MAXI (14) enrolla cables como si fueran serpientes. CONSTANZA (15) ordena una caja con etiquetas.
P: CONSTANZA
D: Esta caja dice «no abrir».
P: MAXI
D: Entonces no la abramos.
A: Isidora ya la abrió. Adentro hay una [[cámara de video antigua|utileria|0]] y una [[cinta marcada «SALA 13 - 1975»|utileria|2000]].
P: ISIDORA
D: ¿Sala 13? El liceo llega hasta la doce.
A: La puerta se abre de golpe. Los tres saltan. Es DON HUGO (68), el auxiliar, con su [[manojo de llaves|utileria|0]].
P: DON HUGO
(sonriendo)
D: En diez minutos cierro el portón. El que se quede adentro, duerme con los fantasmas.
A: Sale. Maxi mira a Isidora.
P: MAXI
D: Dijo «los fantasmas» como si los conociera.
T: CORTE A:
E: INT. LICEO - PASILLO - NOCHE
A: Los tres avanzan con una [[linterna|utileria|3000|cantidad|2]]. Los [[tubos fluorescentes parpadean|iluminacion|0]]. Al fondo hay una puerta sin número.
A: Se escucha un [[piano lejano|sfx_sonido|0]]: tres notas, siempre las mismas.
N: El piano se graba aparte y se pone en la edición. En el set, alguien da la señal con la mano.
P: MAXI
D: ¿Escucharon eso?
P2: CONSTANZA
D: No escuché nada.
A: Isidora alumbra la puerta. Alguien pintó un 13 con [[tiza|utileria|500]].
P: ISIDORA
(susurrando)
D: Es aquí.
E: INT. LICEO - SALA 13 - NOCHE
A: Una bodega. [[Sillas apiladas|set_dressing|0]], un [[piano cubierto con una sábana|set_dressing|5000]] y **polvo** en el aire.
A: Constanza conecta la cámara antigua a un [[televisor viejo|utileria|0]]. Aparece la imagen, con rayas.
PL: INSERTO - EL TELEVISOR
A: Una niña, ELENA (12), con [[uniforme de los años setenta|vestuario|8000]], ensaya una obra. Deja de actuar y mira a la cámara.
P: ELENA
(en la cinta)
D: No apaguen la luz.
A: [[Se corta la luz|sfx_especiales|0]]. Oscuridad total. El piano suena otra vez, más cerca.
P: MAXI
D: ¡Yo no fui!
T: CORTE A:
E: EXT. LICEO - PATIO - NOCHE
A: Corren por el patio. El portón tiene un [[candado|utileria|2500]]. Una luz se acerca desde la oscuridad, moviéndose de lado a lado.
P: CONSTANZA
D: Tiene que haber una explicación lógica.
P: ISIDORA
D: Dímela rápido.
A: La luz los alcanza. Es Don Hugo, con su linterna y una [[taza de té|comida|0]].
P: DON HUGO
D: ¿Encontraron la sala 13?
A: Los tres asienten, sin aire.
E: INT. LICEO - PORTERÍA - NOCHE
A: Una portería chica: un [[calendario de 1999|set_dressing|0]], una radio y fotos de cursos antiguos. Don Hugo les sirve té.
P: DON HUGO
D: La niña del video es mi hermana, Elena. En el setenta y cinco hicieron la última obra en esa sala. Después la cerraron por una gotera y la usaron de bodega.
P: CONSTANZA
D: ¿Y el piano? Lo escuchamos.
P: DON HUGO
(serio)
D: Ese piano no tiene cuerdas hace treinta años.
A: Silencio. Isidora mira su celular: el piano quedó grabado.
E: INT. LICEO - SALA DE AUDIOVISUALES - NOCHE
A: Isidora guarda la cámara antigua en la caja. Maxi y Constanza la esperan en la puerta.
A: La pantalla de la cámara se enciende sola. Muestra la sala... y a los tres, de espaldas, desde el fondo.
A: Isidora se da vuelta muy despacio. Al fondo de la sala no hay nadie.
P: MAXI
D: Isi... ¿quién está grabando?
T: CORTE A NEGRO.
"""

COMEDIA = """
E: INT. COLEGIO - SALA DEL SÉPTIMO - DÍA
A: Una sala llena de dibujos. En un rincón, en su [[jaula|utileria|12000]], DOÑA PEPA, la [[gallina del curso|animales|5000|diaria]], picotea con dignidad.
A: FLORENCIA (12) lee el horario en voz alta. BENJA (12) le da [[maíz|comida|1500]] a la gallina. TOMÁS (11) dibuja a la gallina con corona.
P: FLORENCIA
D: Diez en punto: llega el alcalde. Diez y cuarto: acto en el gimnasio. Diez y media: todos felices.
P: BENJA
D: Doña Pepa también quiere ver al alcalde.
A: Benja abre la jaula «solo un poquito». Doña Pepa sale disparada por la puerta.
P: FLORENCIA
D: ¡Benjamín!
P2: TOMÁS
D: ¡Pepa, vuelve!
T: CORTE A:
E: INT. COLEGIO - CASINO - DÍA
A: El TÍO JUAN (50) revuelve una [[olla de porotos|comida|3000]] con un [[cucharón gigante|utileria|0]]. Doña Pepa aterriza en el mesón.
P: TÍO JUAN
D: Hoy el menú es porotos. Porotos. No pollo.
A: Tomás entra a gatas y le habla a la gallina, muy serio.
P: TÍO JUAN
D: ¿Le estás hablando?
P: TOMÁS
(ofendido)
D: Ella me entiende. Usted no.
A: Doña Pepa escapa por la ventana de la cocina. Una lluvia de [[servilletas|utileria|1000]] cae sobre el Tío Juan.
E: INT. COLEGIO - OFICINA DE LA DIRECTORA - DÍA
A: La DIRECTORA MARGARITA (55) ensaya su discurso frente a un espejo, con una [[banda tricolor|vestuario|4000]] cruzada en el pecho.
P: DIRECTORA MARGARITA
D: Señor alcalde: en este colegio todo, absolutamente todo, está bajo control.
A: Bajo su escritorio, Doña Pepa. Por la puerta, a gatas, Benja y Florencia. La directora se da vuelta. Los niños se quedan inmóviles, como estatuas.
P: DIRECTORA MARGARITA
D: ¿Qué hacen en el suelo?
P: FLORENCIA
D: Buscamos... un aro.
P: BENJA
D: Un arito. De oro.
A: Doña Pepa sale caminando entre los pies de la directora, que no la ve.
E: EXT. PLAZA FRENTE AL COLEGIO - DÍA
A: Llega el [[auto del alcalde|vehiculos|0]]. Un grupo de [[apoderados con banderitas|extras|0|cantidad|10]] aplaude.
A: Doña Pepa cruza la plaza. Los tres niños la persiguen alrededor de la pileta, disimulando, como si fuera parte del acto.
P: EL ALCALDE
D: Qué bonita bienvenida. ¿Y esa gallina?
P: FLORENCIA
(sin pensarlo)
D: ¡Es la mascota oficial!
E: INT. COLEGIO - GIMNASIO - DÍA
A: El acto. Suena la [[banda del colegio|musica|0]]. El alcalde sube al [[escenario con cortina|set_dressing|10000]] y abre su discurso sobre el [[atril|utileria|0]].
A: Doña Pepa salta al atril. Silencio total. La gallina se acomoda... y deja un [[huevo|utileria|200]] sobre el discurso.
P: EL ALCALDE
D: Es la primera vez que uno de mis discursos produce algo.
A: El gimnasio entero estalla en aplausos. La directora sonríe con los dientes apretados.
E: INT. COLEGIO - SALA DEL SÉPTIMO - DÍA
A: Doña Pepa, de vuelta en su jaula, luce una [[medalla de cartón|utileria|500]] que dice «Mascota oficial».
A: La directora entra.
P: DIRECTORA MARGARITA
D: Una sola pregunta: ¿quién abrió la jaula?
A: Todo el curso apunta a Benja. Benja apunta a la gallina.
T: FUNDIDO A NEGRO.
"""

CIENCIA_FICCION = """
E: INT. CASA DE CATALINA - DORMITORIO - NOCHE
A: Cables, tornillos y una [[radio antigua del abuelo|utileria|0]] abierta sobre el escritorio. CATALINA (16) trabaja con un [[soldador|utileria|8000]].
A: El ABUELO RAMÓN (75) se asoma con dos tazas.
P: ABUELO RAMÓN
D: Esa radio no suena desde el terremoto, Cata.
P: CATALINA
D: Hoy va a sonar.
A: Conecta el último cable. Una [[estática de radio|sfx_sonido|0]] llena la pieza. En el dial se enciende una [[luz azul que no debería existir|vfx|0]].
P: CATALINA ADULTA (V.O.)
D: Cata... ¿me escuchas? Soy tú.
A: Catalina suelta el soldador.
T: CORTE A:
E: INT. LICEO - TALLER DE CIENCIAS - DÍA
A: Mesas con [[maquetas de volcanes|set_dressing|0|cantidad|3]] y un esqueleto con lentes de sol. MATEO (16) escucha a Catalina sin pestañear.
P: MATEO
D: Una voz del futuro. Que eres tú. En una radio del año del terremoto.
P: CATALINA
D: Dicho así, suena raro.
A: El PROFESOR SALINAS (50) deja un [[electroimán que no funciona|utileria|4000]] sobre la mesa de Catalina.
P: PROFESOR SALINAS
D: La feria es el viernes. Si tu electroimán no levanta ni un clip, presenta otra cosa.
E: INT. CASA DE CATALINA - DORMITORIO - NOCHE
A: Catalina enciende la radio. Estática. Luz azul.
P: CATALINA ADULTA (V.O.)
D: El viernes no te rindas. Lo que vas a presentar no es el electroimán: es la radio.
P: CATALINA
D: ¿Y cómo sé que eres yo?
P: CATALINA ADULTA (V.O.)
D: Tienes un lunar con forma de estrella en la rodilla. Nadie lo sabe.
A: Catalina se tapa la rodilla, como si alguien la estuviera mirando.
E: EXT. MIRADOR DEL CERRO - NOCHE
A: Un cielo lleno de estrellas. Catalina y Mateo instalan la radio con una [[antena de alambre|utileria|3000]].
A: Un punto de luz cruza el cielo: un [[satélite|vfx|0]]. La radio se enciende sola al mismo tiempo.
P: MATEO
D: Cada vez que pasa el satélite.
P: CATALINA
D: No es magia. Es una señal que rebota.
P: MATEO
(sonriendo)
D: Es un poco magia.
E: INT. LICEO - GIMNASIO - DÍA
A: La feria científica: [[stands con carteles|set_dressing|15000]], [[público de la feria|extras|0|cantidad|15]] y un jurado con tablas.
A: Catalina enciende la radio frente al jurado. Nada. Ni estática. Mateo traga saliva.
PL: PRIMER PLANO DE CATALINA
A: Catalina respira, deja la radio de lado y explica cómo funciona una señal que rebota en un satélite. Habla claro, sin nervios.
A: El jurado escribe. Cuando se dan vuelta, la luz azul parpadea una vez. Solo Mateo la ve.
E: INT. CASA DE CATALINA - DORMITORIO - NOCHE
A: Sobre el escritorio, un [[diploma de mención honrosa|utileria|1000]]. Catalina enciende la radio: estática.
P: CATALINA
(a la radio)
D: Si me escuchas... no te rindas tú tampoco.
A: Silencio. La luz azul parpadea dos veces.
T: FUNDIDO A NEGRO.
"""

DRAMA = """
ACTO: PRIMER ACTO
E: INT. LICEO - SALA DE CLASES - DÍA
A: Primer día de ROCÍO (13) en el liceo, en pleno junio. Lleva un [[abrigo de lana enorme|vestuario|0]] que no se saca.
P: PROFESORA ANDREA
D: Ella es Rocío. Viene de Punta Arenas. ¿Quieres contarnos algo?
A: Rocío niega con la cabeza. Algunos se ríen bajito. LUCAS (13), el del puesto de al lado, le presta un [[lápiz|utileria|300]] sin decir nada.
P: PROFESORA ANDREA
D: Otro día, entonces.
E: INT. CASA DE ROCÍO - COCINA - NOCHE
A: [[Cajas de mudanza|set_dressing|500|cantidad|6]] por todos lados. RODRIGO (40), el papá, revuelve una olla.
A: En un [[notebook|utileria|0]], la ABUELA TERE (70) aparece en videollamada. Rocío habla sin parar, se ríe, le muestra la cocina.
P: ROCÍO
D: ¡Aquí no hay viento, abuela! Una se peina y queda peinada.
P: ABUELA TERE
D: ¿Y ya hiciste amigos?
A: Rocío deja de sonreír. Rodrigo la escucha desde la puerta.
FINACTO: FIN DEL PRIMER ACTO
ACTO: SEGUNDO ACTO
E: INT. LICEO - SALA DE TEATRO - DÍA
A: Un círculo de sillas. La Profesora Andrea reparte [[hojas en blanco|utileria|0]].
P: PROFESORA ANDREA
D: Cada uno va a escribir una carta a alguien que extraña. Y la va a leer en voz alta en la muestra.
A: Rocío se para y sale de la sala.
E: EXT. LICEO - ESCALERA - DÍA
A: Rocío está sentada en la escalera del cerro, frente al mar. Lucas se sienta dos escalones más arriba.
P: LUCAS
D: Yo t-t-tartamudeo cuando me pongo nervioso. Por eso no hablo en clases.
A: Rocío lo mira por primera vez.
P: ROCÍO
D: En Punta Arenas el viento no te deja hablar. Aquí es el silencio.
P: LUCAS
D: Entonces escribe la carta. Que la lea el papel.
FINACTO: FIN DEL SEGUNDO ACTO
ACTO: TERCER ACTO
E: INT. LICEO - SALA DE TEATRO - NOCHE
A: La muestra. [[Apoderados|extras|0|cantidad|20]] en las sillas. Un [[foco cenital|iluminacion|0]] sobre el centro.
A: En la última fila, Rodrigo sostiene su celular en alto: la Abuela Tere mira por videollamada.
A: Rocío pasa al centro con su carta. Le tiemblan las manos. Lucas le hace un gesto: respira.
P: ROCÍO
D: Querida abuela: aquí el mar es más tibio y las casas suben por los cerros. Todavía no tengo amigos, pero tengo uno que tartamudea y que me prestó un lápiz.
P: ROCÍO
(levanta la vista)
D: Te extraño. Pero creo que me voy a quedar.
A: Silencio. Después, un [[aplauso que llena la sala|sfx_sonido|0]].
E: EXT. LICEO - ESCALERA - NOCHE
A: Rocío, Rodrigo y Lucas bajan la escalera iluminada por [[faroles|set_dressing|0]]. En el celular, la abuela llora de risa.
P: ABUELA TERE
D: Te escuché fuerte y claro, mijita.
A: Rocío se saca el abrigo de lana por primera vez y se lo pone a Lucas, que tiene frío.
T: FUNDIDO A NEGRO.
FINACTO: FIN DEL TERCER ACTO
"""

SUSPENSO = """
E: INT. LICEO - SALA DE PROFESORES - DÍA
A: El PROFESOR VALDÉS (45) da vuelta su escritorio buscando algo. El INSPECTOR PATRICIO (50) lo mira desde la puerta.
P: PROFESOR VALDÉS
D: El sobre con las respuestas de la prueba estaba aquí. Mañana es la prueba.
P: INSPECTOR PATRICIO
D: En el primer recreo el único alumno que entró fue Diego Soto. A dejar una guía.
PL: INSERTO - RELOJ DE LA PARED: 10:15
T: CORTE A:
E: INT. LICEO - PASILLO - DÍA
A: DIEGO (15) camina como si lo persiguiera alguien. ANTONIA (15) lo alcanza con su [[libreta de detective|utileria|1000]].
P: DIEGO
D: Me van a suspender. Y yo no saqué nada.
P: ANTONIA
D: Entonces tenemos hasta el último recreo para saber quién fue.
A: Antonia anota: «sala de profesores - 10:15 - sobre café».
N: Ensayar este diálogo caminando. La cámara va delante de ellos, retrocediendo.
E: INT. LICEO - FOTOCOPIADORA - DÍA
A: Una [[fotocopiadora vieja|set_dressing|0]] que suena como un tractor. Antonia abre la bandeja: hay una [[hoja atascada|utileria|0]] con la primera respuesta de la prueba.
PL: INSERTO - PANTALLA DE LA FOTOCOPIADORA: ÚLTIMO CÓDIGO 214
P: DIEGO
D: El 214 es el código del segundo B.
P: ANTONIA
D: El curso de Joaquín. El delegado.
A: Se escucha el [[timbre|sfx_sonido|0]]. Fin del tercer recreo. Queda uno.
E: INT. LICEO - BIBLIOTECA - DÍA
A: [[Estudiantes estudiando|extras|0|cantidad|6]] en silencio. JOAQUÍN (15) mira a todos lados y mete un [[sobre café|utileria|300|cantidad|2]] dentro de una [[enciclopedia|utileria|0]].
A: Desde atrás de un estante, Antonia y Diego lo ven. Antonia le saca una foto con el celular. El flash se dispara.
PL: INSERTO - RELOJ DE LA BIBLIOTECA: 12:55
A: Joaquín se da vuelta. Antonia y Diego se agachan justo a tiempo.
E: EXT. LICEO - PATIO - DÍA
A: El último recreo. Diego y Antonia encuentran a Joaquín solo, en una de las [[bancas|set_dressing|0]].
P: ANTONIA
D: Sabemos lo del sobre.
P: JOAQUÍN
(bajando la vista)
D: Lo saqué para ver si era fácil. Después lo quise devolver, pero ya culpaban a Diego. Me dio miedo.
P: DIEGO
D: Miedo tenía yo.
A: Joaquín les pasa el sobre. Lo tiene doblado en cuatro.
E: INT. LICEO - SALA DE PROFESORES - DÍA
A: Joaquín deja el sobre en el escritorio del Profesor Valdés. Diego y Antonia esperan en la puerta.
P: PROFESOR VALDÉS
D: Gracias por decir la verdad. La prueba se hace igual, mañana. Con otras preguntas.
A: Diego respira por primera vez en todo el día. Antonia cierra su libreta.
P: ANTONIA
D: Caso cerrado.
T: FUNDIDO A NEGRO.
"""

# ═══════════════════════════════════════════════════════════════════════
#  La producción de cada uno
# ═══════════════════════════════════════════════════════════════════════

def _sab(base: date, semana: int) -> date:
    """El sábado de la semana «semana» desde la base (1: el próximo sábado
    después de una semana)."""
    primero = base + timedelta(days=7 + (5 - base.weekday()) % 7)
    return primero + timedelta(days=7 * (semana - 1))


CIUDADES = {
    "Viña del Mar": ("Viña del Mar (Valparaíso)", -33.0245, -71.5518, "Valparaíso"),
    "Rancagua": ("Rancagua (O'Higgins)", -34.1708, -70.7444, "O'Higgins"),
    "La Serena": ("La Serena (Coquimbo)", -29.9027, -71.2519, "Coquimbo"),
    "Valparaíso": ("Valparaíso (Valparaíso)", -33.0472, -71.6127, "Valparaíso"),
    "Santiago": ("Santiago (Metropolitana)", -33.4489, -70.6693, "Metropolitana"),
}


def _tel(serie: int, k: int) -> str:
    return f"+56 9 0000 {serie:02d}{k:02d}"


PROYECTOS = [
    {
        "genero": "Terror", "titulo": "La sala 13", "guion": TERROR, "ciudad": "Viña del Mar", "serie": 11,
        "en_escena": {1: ["ISIDORA", "MAXI", "CONSTANZA", "DON HUGO"], 2: ["ISIDORA", "MAXI", "CONSTANZA"], 3: ["ISIDORA", "MAXI", "CONSTANZA"], 4: ["ISIDORA", "CONSTANZA", "MAXI", "DON HUGO"], 5: ["DON HUGO", "CONSTANZA", "ISIDORA", "MAXI"], 6: ["ISIDORA", "MAXI", "CONSTANZA"]},
        "voces": ["ELENA"],
        "premisa": ("Tres estudiantes que se quedan guardando equipos después de la feria científica "
                    "encuentran una cinta de 1975 grabada en una sala del liceo que ya no existe."),
        "escaleta": ["Después de la feria, Isidora, Maxi y Constanza encuentran una cámara antigua y una cinta de la «sala 13».",
                     "En el pasillo escuchan un piano y encuentran una puerta con un 13 pintado.",
                     "En la sala 13 ven la cinta: una niña les pide que no apaguen la luz. Se corta la luz.",
                     "Huyen al patio: el portón está cerrado y una luz se acerca. Es Don Hugo.",
                     "Don Hugo explica que la niña era su hermana. Pero el piano no tiene cuerdas.",
                     "La cámara se enciende sola y los muestra de espaldas, desde el fondo de la sala."],
        "elenco": [
            ("ISIDORA", dict(genero="Femenino", edad="15", profesion="Estudiante de 1° medio",
                             biografia="Valiente y curiosa. Graba todo con su celular porque quiere ser documentalista.",
                             actor_nombre="Fernanda Quiroz", descripcion_fisica="Pelo largo tomado, mochila con parches.",
                             vestuario="Polerón del liceo, jeans y zapatillas blancas (igual en todas las escenas).")),
            ("MAXI", dict(genero="Masculino", edad="14", profesion="Estudiante de 1° medio",
                          biografia="Miedoso y chistoso: hace bromas cuando está nervioso.",
                          actor_nombre="Maximiliano Rojas", alergias=True, alergias_detalle="Polvo (en la sala 13 usar polvo falso de talco)",
                          vestuario="Chaqueta de mezclilla y gorro.")),
            ("CONSTANZA", dict(genero="Femenino", edad="15", profesion="Estudiante de 1° medio",
                               biografia="Lógica y ordenada. Busca una explicación para todo.",
                               actor_nombre="Constanza Vidal", vestuario="Uniforme del liceo y lentes.")),
            ("DON HUGO", dict(genero="Masculino", edad="68", profesion="Auxiliar del liceo",
                              biografia="Lleva cuarenta años en el liceo. Conoce cada llave y cada historia.",
                              actor_nombre="Jorge Saavedra (apoderado)", actor_valor_dia="15000",
                              vestuario="Cotona azul de auxiliar y un manojo de llaves al cinturón.")),
            ("ELENA", dict(genero="Femenino", edad="12", profesion="Estudiante (en 1975)",
                           biografia="La hermana de Don Hugo, en la cinta del último ensayo de la sala 13.",
                           actor_nombre="Josefa Saavedra",
                           descripcion_fisica="Maquillaje pálido; peinado con dos trenzas.",
                           vestuario="Jumper azul y blusa blanca de los años setenta.")),
        ],
        "locaciones": [("Liceo", dict(ubicacion="Calle de Ejemplo 123, Viña del Mar", precio_dia="0",
                                      detalles="Rodaje de noche, después de clases. Pedir las llaves en portería.",
                                      hospital="CESFAM de ejemplo · Av. Ejemplo 100 · urgencias " + "+56 9 0000 1199"))],
        "crew": [("Valentina Muñoz", "Dirección"), ("Tomás Herrera", "Asistente de dirección"),
                 ("Profesora Carolina Díaz", "Producción"), ("Ignacio Pérez", "Cámara (DP)"),
                 ("Martina Soto", "Sonido directo"), ("Agustín Lagos", "Arte y utilería"),
                 ("Daniela Fuentes", "Vestuario y maquillaje"), ("Sofía Navarro", "Script y continuidad")],
        "equipos": [("Cámara réflex del liceo", "Con lente 18-55 mm", "Liceo (préstamo)", "1", "0"),
                    ("Trípode", "", "Liceo (préstamo)", "1", "0"),
                    ("Grabadora de sonido", "Con pértiga (boom)", "Arriendo audiovisual (ejemplo)", "1", "6000"),
                    ("Panel LED", "Con filtro azul para la noche", "Arriendo audiovisual (ejemplo)", "2", "4000"),
                    ("Máquina de humo chica", "Para el polvo de la sala 13", "Arriendo audiovisual (ejemplo)", "1", "8000")],
        "jornadas": [(1, "Liceo", [1, 2, 3], "18:30", "Interiores de noche",
                      "Colación a las 20:00 en el casino", "Permiso de la dirección para grabar después de clases"),
                     (2, "Liceo", [4, 5, 6], "18:30", "Patio, portería y final",
                      "Colación a las 20:00 en el casino", "Permiso de la dirección para grabar después de clases")],
        "planos": {
            1: [("PG", "Normal", "Fijo", "24 mm", "La sala después de la feria: los tres guardan equipos."),
                ("PD", "Picado", "Fijo", "50 mm", "La caja abierta: la cámara y la cinta."),
                ("PM", "Contrapicado", "Fijo", "35 mm", "Don Hugo en la puerta con las llaves.")],
            2: [("PA", "Normal", "Travelling", "24 mm", "Los tres avanzan con la linterna (cámara delante, retrocediendo)."),
                ("PMC", "Normal", "Fijo", "35 mm", "Maxi y Constanza: «¿Escucharon eso?»")],
            3: [("PG", "Normal", "Fijo", "18 mm", "La bodega con el piano tapado."),
                ("PP", "Normal", "Zoom", "50 mm", "Elena en el televisor: «No apaguen la luz»."),
                ("PM", "Holandés", "Cámara en mano", "24 mm", "Se corta la luz: solo las linternas.")],
            4: [("GPG", "Picado", "Fijo", "18 mm", "El patio oscuro y la luz que se acerca."),
                ("PM", "Normal", "Fijo", "35 mm", "Don Hugo con la taza de té.")],
            5: [("PM", "Normal", "Fijo", "35 mm", "Don Hugo cuenta la historia."),
                ("PP", "Normal", "Fijo", "50 mm", "Isidora mira su celular.")],
            6: [("PE", "Normal", "Fijo", "24 mm", "Isidora guarda la cámara; los otros en la puerta."),
                ("PD", "Normal", "Fijo", "50 mm", "La pantalla de la cámara los muestra de espaldas."),
                ("PP", "Normal", "Dolly", "35 mm", "Isidora se da vuelta muy despacio.")]},
        "objetos": {1: [("mesa", 0.0, -0.6, 0), ("computador", -1.8, -1.8, 0), ("silla", 1.5, -1.6, 30), ("caja", 0.3, -0.6, 0)],
                    2: [("puerta", 0.0, -2.5, 0), ("linterna", -0.4, 0.4, 0)],
                    3: [("piano", -1.2, -1.8, 0), ("silla", 1.6, -1.9, 10), ("silla", 2.0, -1.9, 0), ("televisor", 1.0, -0.4, 180)],
                    4: [("reja", 0.0, -3.0, 0), ("arbol", -3.0, -1.5, 0), ("banca", 2.5, -1.2, 90)],
                    5: [("escritorio", 0.0, -0.8, 0), ("taza", 0.2, -0.8, 0), ("cuadro", -1.5, -2.4, 0)],
                    6: [("mesa", 0.0, -0.6, 0), ("caja", 0.0, -0.6, 0), ("puerta", 1.6, -2.5, 0)]},
        "recorrido": (2, "ISIDORA", [(0.0, 2.0), (0.0, 0.5), (0.2, -1.5)]),
        "sol": {4: "21:30"},
        "fichas_escenas": {
            1: dict(proposito="Presentar a los tres y el misterio de la cinta.", objetivo_protagonista="Isidora quiere grabar algo que valga la pena.",
                    obstaculo="Don Hugo está por cerrar el liceo.", tono="Cotidiano que se vuelve raro",
                    notas_direccion="Que la caja se vea desde lejos antes de que la abran."),
            3: dict(proposito="El susto principal.", objetivo_protagonista="Saber qué hay en la cinta.",
                    obstaculo="La oscuridad y el miedo.", subtexto="Elena no los asusta: les pide ayuda.",
                    tono="Terror suave, sin sangre", referencias="Luz de linterna y sombras largas.",
                    notas_direccion="El corte de luz se hace apagando el panel LED: probarlo antes."),
            6: dict(proposito="Un final abierto.", tono="Escalofrío", notas_direccion="No mostrar a nadie al fondo: el miedo lo pone el público.")},
        "gastos": [("Catering", "Colación para el equipo", "Casino del liceo", 14, "2500", "jornadas"),
                   ("Arte y vestuario", "Talco y tela para el polvo falso", "Librería (ejemplo)", 1, "3500", None),
                   ("Imprevistos", "Pilas para linternas y micrófonos", "", 1, "6000", None)],
        "pagos": [("equipamiento:Máquina de humo chica", -2, "Reserva pagada al arrendar")],
        "documentos": [("Autorización de menores", "Autorizaciones de los apoderados (elenco y crew menores de edad)",
                        "Apoderados del curso", "Recibido", -6, 120, "", "Faltan 2: recordar en la reunión de apoderados."),
                       ("Permiso municipal", "Permiso de la dirección para grabar de noche", "Dirección del liceo",
                        "Firmado", -4, 30, "", ""),
                       ("Seguro", "Seguro escolar (cubre las actividades del liceo)", "Seguro escolar", "Vigente",
                        -30, 300, "0", "Avisar a la dirección los horarios de rodaje."),
                       ("Cesión de derechos / imagen", "Cesión de imagen del elenco", "Elenco", "Enviado", -2, 365, "", "")],
        "fondos": "150000", "fondos_de": "Aporte del centro de padres",
        "iva": ("", ""), "grupos": None, "version_corta": [1, 3, 5, 6],
    },
    {
        "genero": "Comedia", "titulo": "Doña Pepa se escapó", "guion": COMEDIA, "ciudad": "Rancagua", "serie": 12,
        "en_escena": {1: ["BENJA", "FLORENCIA", "TOMÁS"], 2: ["TÍO JUAN", "TOMÁS"], 3: ["DIRECTORA MARGARITA", "FLORENCIA", "BENJA"], 4: ["EL ALCALDE", "FLORENCIA", "BENJA", "TOMÁS"], 5: ["EL ALCALDE", "DIRECTORA MARGARITA", "BENJA", "FLORENCIA", "TOMÁS"], 6: ["DIRECTORA MARGARITA", "BENJA", "FLORENCIA", "TOMÁS"]},
        "voces": [],
        "premisa": ("El día que llega el alcalde, la gallina del séptimo básico se escapa de su jaula y tres "
                    "niños tienen una hora para encontrarla sin que la directora se entere."),
        "escaleta": ["Benja abre la jaula de Doña Pepa justo antes de la visita del alcalde.",
                     "La gallina aparece en el casino; Tomás le habla y el Tío Juan no lo puede creer.",
                     "En la oficina de la directora, los niños se hacen las estatuas mientras ella ensaya.",
                     "En la plaza llega el alcalde: Florencia dice que la gallina es la mascota oficial.",
                     "En el acto, Doña Pepa pone un huevo sobre el discurso del alcalde.",
                     "La directora pregunta quién abrió la jaula: todos apuntan a Benja, Benja a la gallina."],
        "elenco": [
            ("BENJA", dict(genero="Masculino", edad="12", profesion="Estudiante de 7° básico",
                           biografia="Tiene ideas geniales que casi siempre salen mal.", actor_nombre="Benjamín Araya",
                           vestuario="Buzo del colegio con una rodilla rota (siempre la misma).")),
            ("FLORENCIA", dict(genero="Femenino", edad="12", profesion="Estudiante de 7° básico",
                               biografia="La más ordenada del curso: anda con una libreta de horarios.",
                               actor_nombre="Florencia Bustos", alimentacion="Vegetariano/a",
                               vestuario="Uniforme impecable, cintillo amarillo.")),
            ("TOMÁS", dict(genero="Masculino", edad="11", profesion="Estudiante de 7° básico",
                           biografia="Dice que entiende a los animales. Nadie le cree.", actor_nombre="Tomás Gaete",
                           alergias=True, alergias_detalle="Maní", vestuario="Delantal con dibujos de animales.")),
            ("DIRECTORA MARGARITA", dict(genero="Femenino", edad="55", profesion="Directora del colegio",
                                         biografia="Quiere que la visita del alcalde salga perfecta.",
                                         actor_nombre="Profesora Marcela Tapia", vestuario="Traje gris y banda tricolor.")),
            ("TÍO JUAN", dict(genero="Masculino", edad="50", profesion="Cocinero del casino",
                              biografia="Cocina para trescientos niños y no deja entrar ni una mosca a su cocina.",
                              actor_nombre="Juan Castro (apoderado)", vestuario="Delantal blanco y gorro de cocina.")),
            ("EL ALCALDE", dict(genero="Masculino", edad="60", profesion="Alcalde",
                                biografia="Viene a inaugurar el gimnasio y no tiene nada de sentido del humor... hasta hoy.",
                                actor_nombre="Profesor Luis Molina", vestuario="Terno azul y corbata roja.")),
        ],
        "locaciones": [("Colegio", dict(ubicacion="Pasaje de Ejemplo 45, Rancagua", precio_dia="0",
                                        detalles="Rodar el sábado: el colegio está vacío. El casino se pide al Tío Juan.",
                                        hospital="Hospital de ejemplo · Calle Ejemplo 500 · urgencias +56 9 0000 1299")),
                       ("Plaza Frente Al Colegio", dict(ubicacion="Plaza de Ejemplo, Rancagua", precio_dia="0",
                                                        detalles="Lugar público: permiso municipal. Hay una pileta.",
                                                        hospital="Hospital de ejemplo · Calle Ejemplo 500 · urgencias +56 9 0000 1299"))],
        "crew": [("Amanda Reyes", "Dirección"), ("Lucas Sepúlveda", "Asistente de dirección"),
                 ("Profesor Rodrigo Vera", "Producción"), ("Catalina Ibáñez", "Cámara (DP)"),
                 ("Vicente Morales", "Sonido directo"), ("Javiera Ortiz", "Arte y utilería"),
                 ("Don Pedro Leiva", "Cuidador de animales")],
        "equipos": [("Celular con estabilizador", "Estabilizador de mano (gimbal)", "Propio", "1", "0"),
                    ("Trípode", "", "Colegio (préstamo)", "1", "0"),
                    ("Micrófono de corbata (lavalier)", "", "Arriendo audiovisual (ejemplo)", "2", "3000"),
                    ("Reflector plegable", "Para la plaza", "Colegio (préstamo)", "1", "0")],
        "jornadas": [(1, "Colegio", [1, 2, 3, 6], "09:00", "Interiores del colegio",
                      "Colación en el casino (13:00)", ""),
                     (2, "Plaza Frente Al Colegio", [4, 5], "09:30", "La plaza y el acto en el gimnasio",
                      "Colación en el casino (13:00)", "Permiso municipal para la plaza", "Colegio")],
        "planos": {
            1: [("PG", "Normal", "Fijo", "24 mm", "La sala y la jaula de Doña Pepa."),
                ("PP", "Normal", "Fijo", "50 mm", "Benja abre la jaula «solo un poquito»."),
                ("PD", "Picado", "Paneo", "35 mm", "La gallina sale disparada por la puerta.")],
            2: [("PM", "Normal", "Fijo", "35 mm", "El Tío Juan con el cucharón."),
                ("PP", "Picado", "Fijo", "50 mm", "Tomás le habla a la gallina.")],
            3: [("PA", "Normal", "Fijo", "24 mm", "La directora ensaya frente al espejo."),
                ("PG", "Picado", "Fijo", "18 mm", "Los niños, inmóviles como estatuas.")],
            4: [("GPG", "Normal", "Paneo", "18 mm", "Llega el auto del alcalde a la plaza."),
                ("PE", "Normal", "Travelling", "24 mm", "La persecución alrededor de la pileta.")],
            5: [("PG", "Normal", "Fijo", "24 mm", "El acto en el gimnasio."),
                ("PD", "Picado", "Fijo", "50 mm", "El huevo sobre el discurso."),
                ("PMC", "Contrapicado", "Fijo", "35 mm", "El alcalde: «produce algo».")],
            6: [("PM", "Normal", "Fijo", "35 mm", "La directora pregunta."),
                ("PG", "Normal", "Paneo", "24 mm", "Todos apuntan a Benja; Benja a la gallina.")]},
        "objetos": {1: [("pupitre", -1.5, -1.0, 0), ("pupitre", 1.5, -1.0, 0), ("gallina", 0.6, -1.6, 0), ("caja", 0.6, -1.6, 0)],
                    2: [("cocina", -1.2, -2.0, 0), ("olla", -1.2, -2.0, 0), ("mostrador", 1.0, -1.2, 0), ("gallina", 1.0, -1.2, 0)],
                    3: [("escritorio", 0.0, -1.5, 0), ("espejo", -2.0, -2.4, 0), ("gallina", 0.0, -1.2, 0)],
                    4: [("pileta", 0.0, -1.0, 0), ("auto", -3.0, -2.5, 0), ("arbol", 3.0, -2.0, 0), ("banca", 2.0, 1.2, 0), ("gallina", 0.8, -0.2, 0)],
                    5: [("atril", 0.0, -1.0, 180), ("telon", 0.0, -2.4, 0), ("butacas", 0.0, 2.0, 180), ("gallina", 0.2, -1.0, 0)],
                    6: [("pupitre", -1.5, -1.0, 0), ("pupitre", 1.5, -1.0, 0), ("caja", 0.6, -1.6, 0)]},
        "recorrido": (4, "FLORENCIA", [(-1.5, 1.0), (-1.6, -1.4), (0.0, -2.4), (1.6, -1.2)]),
        "sol": {4: "10:30"},
        "fichas_escenas": {
            1: dict(proposito="El problema: la gallina se escapa.", objetivo_protagonista="Benja quiere que Doña Pepa vea al alcalde.",
                    obstaculo="La visita del alcalde es en una hora.", tono="Comedia de enredos"),
            3: dict(proposito="Casi los pillan.", subtexto="La directora no está tan segura de que todo esté «bajo control».",
                    tono="Comedia física", notas_direccion="Las estatuas: probar la pose y contar hasta tres antes de cortar."),
            5: dict(proposito="El clímax: el huevo.", tono="Comedia", notas_direccion="El huevo se pone en el atril entre tomas.")},
        "gastos": [("Catering", "Colación para el equipo", "Casino del colegio", 13, "2000", "jornadas"),
                   ("Transporte", "Traslado de la jaula y Doña Pepa", "Don Pedro Leiva", 1, "5000", "jornadas"),
                   ("Mascota", "Alimento y paja para Doña Pepa", "Forrajería (ejemplo)", 1, "4000", None),
                   ("Imprevistos", "Imprevistos (10 %)", "", 1, "10000", None)],
        "pagos": [("gasto:Mascota", -3, "Comprado en la forrajería"),
                  ("tag:animales:gallina del curso", -1, "Pagado a Don Pedro por cuidar a la gallina")],
        "documentos": [("Autorización de menores", "Autorizaciones de los apoderados del 7° básico", "Apoderados",
                        "Recibido", -7, 120, "", ""),
                       ("Permiso municipal", "Permiso para grabar en la plaza", "Municipalidad (ejemplo)", "Enviado",
                        -3, 20, "5000", "Llamar para confirmar."),
                       ("Otro", "Cuidado de la gallina durante el rodaje", "Don Pedro Leiva", "Firmado", -5, 30, "",
                        "La gallina descansa cada 30 minutos, con agua y sombra.")],
        "fondos": "150000", "fondos_de": "Fondo del curso", "iva": ("incluido", "19"),
        "categorias_propias": [("Mascota", "🐔")], "grupos": "etapas",
        "lineas_movidas": {"tag:animales:gallina del curso": "Mascota"},
        "version_corta": [1, 3, 5, 6],
    },
    {
        "genero": "Ciencia ficción", "titulo": "Señal del futuro", "guion": CIENCIA_FICCION, "ciudad": "La Serena", "serie": 13,
        "en_escena": {1: ["CATALINA", "ABUELO RAMÓN"], 2: ["MATEO", "CATALINA", "PROFESOR SALINAS"], 3: ["CATALINA"], 4: ["CATALINA", "MATEO"], 5: ["CATALINA", "MATEO", "PROFESOR SALINAS"], 6: ["CATALINA"]},
        "voces": ["CATALINA ADULTA"],
        "premisa": ("Una estudiante arregla la radio antigua de su abuelo para la feria científica y empieza a "
                    "recibir mensajes de ella misma, veinte años en el futuro."),
        "escaleta": ["Catalina arregla la radio del abuelo y escucha su propia voz, del futuro.",
                     "En el taller de ciencias, Mateo no le cree y el profesor le pide otro proyecto.",
                     "La voz le da una prueba que solo ella conoce y le dice que presente la radio.",
                     "En el mirador descubren que la señal llega cuando pasa un satélite.",
                     "En la feria la radio no suena, pero Catalina explica la ciencia y lo logra.",
                     "Catalina le responde a la radio. La luz azul parpadea dos veces."],
        "elenco": [
            ("CATALINA", dict(genero="Femenino", edad="16", profesion="Estudiante de 2° medio",
                              biografia="Desarma todo para entender cómo funciona.", actor_nombre="Catalina Molina",
                              vestuario="Overol de mezclilla con parches de la NASA dibujados a mano.")),
            ("CATALINA ADULTA", dict(genero="Femenino", edad="36", profesion="Ingeniera (en el futuro)",
                                     biografia="Solo se escucha su voz, por la radio.", actor_nombre="Profesora Paula Zamora",
                                     voz_tts="femenina", actor_notas="Grabar su voz en la sala de música, sin eco.")),
            ("MATEO", dict(genero="Masculino", edad="16", profesion="Estudiante de 2° medio",
                           biografia="El mejor amigo de Catalina. No cree en nada que no pueda medir.", actor_nombre="Mateo Carrasco",
                           vestuario="Polera de un videojuego y anteojos.")),
            ("PROFESOR SALINAS", dict(genero="Masculino", edad="50", profesion="Profesor de física",
                                      biografia="Exigente, pero el primero en emocionarse con un buen experimento.",
                                      actor_nombre="Profesor Andrés Pino", vestuario="Delantal blanco y corbata de humita.")),
            ("ABUELO RAMÓN", dict(genero="Masculino", edad="75", profesion="Radioaficionado jubilado",
                                  biografia="Le enseñó a Catalina a usar un soldador.", actor_nombre="Ramón Pizarro (abuelo de una alumna)",
                                  actor_valor_dia="10000", movilidad_reducida=True,
                                  movilidad_detalle="Usa bastón: dejarle una silla cerca del set.",
                                  vestuario="Chaleco de lana café.")),
        ],
        "locaciones": [("Casa De Catalina", dict(ubicacion="Calle de Ejemplo 77, La Serena", precio_dia="15000",
                                                 detalles="Casa de una apoderada. El dormitorio es chico: máximo 4 personas del equipo adentro.",
                                                 hospital="Hospital de ejemplo · Av. Ejemplo 300 · urgencias +56 9 0000 1399")),
                       ("Liceo", dict(ubicacion="Calle de Ejemplo 10, La Serena", precio_dia="0",
                                      detalles="El taller de ciencias y el gimnasio.",
                                      hospital="Hospital de ejemplo · Av. Ejemplo 300 · urgencias +56 9 0000 1399")),
                       ("Mirador Del Cerro", dict(ubicacion="Mirador de ejemplo, La Serena", precio_dia="0",
                                                  detalles="De noche hace frío: llevar parkas y termos. Sin luz: llevar focos.",
                                                  hospital="Hospital de ejemplo · Av. Ejemplo 300 · urgencias +56 9 0000 1399"))],
        "crew": [("Renata Álvarez", "Dirección"), ("Simón Cortés", "Asistente de dirección"),
                 ("Profesora Isabel Rojas", "Producción"), ("Benjamín Tapia", "Cámara (DP)"),
                 ("Antonia Vega", "Sonido directo"), ("Gaspar Núñez", "Efectos visuales (postproducción)"),
                 ("Trinidad Salas", "Arte y utilería")],
        "equipos": [("Cámara réflex del liceo", "Con lente 50 mm luminoso para el cielo", "Liceo (préstamo)", "1", "0"),
                    ("Trípode", "", "Liceo (préstamo)", "1", "0"),
                    ("Panel LED azul", "Para la luz de la radio", "Arriendo audiovisual (ejemplo)", "1", "5000"),
                    ("Grabadora de sonido", "Para la voz del futuro", "Arriendo audiovisual (ejemplo)", "1", "6000")],
        "jornadas": [(1, "Casa De Catalina", [1, 3, 6], "17:00", "El dormitorio de Catalina",
                      "Once en la casa (aporte de la familia)", ""),
                     (2, "Liceo", [2, 5], "09:00", "El liceo y la feria",
                      "Colación en el casino (13:00)", ""),
                     (3, "Mirador Del Cerro", [4], "20:00", "El mirador, de noche",
                      "Sopaipillas y té en termos", "Aviso a la municipalidad (lugar público)")],
        "planos": {
            1: [("PM", "Normal", "Fijo", "35 mm", "Catalina con el soldador."),
                ("PD", "Normal", "Fijo", "50 mm", "Se enciende la luz azul del dial."),
                ("PP", "Normal", "Zoom", "50 mm", "Catalina escucha su voz.")],
            2: [("PA", "Normal", "Fijo", "24 mm", "Catalina y Mateo en el taller."),
                ("PM", "Contrapicado", "Fijo", "35 mm", "El profesor deja el electroimán.")],
            3: [("PMC", "Normal", "Fijo", "35 mm", "Catalina frente a la radio."),
                ("PD", "Picado", "Fijo", "50 mm", "Se tapa la rodilla.")],
            4: [("GPG", "Contrapicado", "Fijo", "18 mm", "El cielo estrellado y el satélite."),
                ("PE", "Normal", "Fijo", "24 mm", "Los dos con la radio y la antena.")],
            5: [("PG", "Normal", "Paneo", "24 mm", "La feria y el público."),
                ("PP", "Normal", "Fijo", "50 mm", "Catalina explica, sin nervios."),
                ("PD", "Normal", "Fijo", "50 mm", "La luz azul parpadea una vez.")],
            6: [("PM", "Normal", "Fijo", "35 mm", "Catalina le habla a la radio."),
                ("PD", "Normal", "Dolly", "50 mm", "La luz parpadea dos veces.")]},
        "objetos": {1: [("escritorio", 0.0, -1.5, 0), ("parlante", 0.0, -1.5, 0), ("cama", 2.0, 0.5, 90), ("lampara_escritorio", -0.5, -1.6, 0)],
                    2: [("mesa", 0.0, -0.8, 0), ("computador", -1.0, -2.0, 0), ("pizarra", 0.0, -2.4, 0)],
                    3: [("escritorio", 0.0, -1.5, 0), ("parlante", 0.0, -1.5, 0), ("cama", 2.0, 0.5, 90)],
                    4: [("roca", -2.0, -1.0, 0), ("arbusto", 2.5, -2.0, 0), ("parlante", 0.0, -0.5, 0)],
                    5: [("mesa", 0.0, -1.0, 0), ("parlante", 0.0, -1.0, 0), ("letrero", -2.5, -2.0, 0), ("mesa", -2.5, -1.0, 0)],
                    6: [("escritorio", 0.0, -1.5, 0), ("parlante", 0.0, -1.5, 0), ("cama", 2.0, 0.5, 90)]},
        "recorrido": (5, "CATALINA", [(-1.2, 1.2), (-0.6, 0.2), (0.0, -0.4)]),
        "sol": {4: "21:00"},
        "fichas_escenas": {
            1: dict(proposito="El detonante: la voz del futuro.", objetivo_protagonista="Que la radio vuelva a sonar.",
                    obstaculo="Nadie cree que funcione.", tono="Misterio luminoso", referencias="Luces azules, cables, el cuarto en penumbra."),
            4: dict(proposito="La explicación científica.", subtexto="Mateo empieza a creer en Catalina.",
                    tono="Asombro", notas_direccion="El satélite se agrega en la edición: grabar el cielo fijo 20 segundos."),
            6: dict(proposito="El cierre: Catalina se responde a sí misma.", tono="Emotivo")},
        "gastos": [("Locaciones", "Aporte por la luz y el agua de la casa", "Familia Molina", 1, "10000", None),
                   ("Catering", "Colación para el equipo", "Casino del liceo", 12, "2000", "jornadas"),
                   ("Postproducción", "Disco externo para respaldar el material", "Tienda de ejemplo", 1, "15000", None),
                   ("Transporte", "Furgón al mirador (ida y vuelta)", "Transportes de ejemplo", 1, "25000", None)],
        "pagos": [("locacion:Casa De Catalina", -2, "Abono del 50 %")],
        "documentos": [("Contrato de locación", "Uso de la casa de la familia Molina", "Familia Molina", "Firmado",
                        -4, 60, "", ""),
                       ("Autorización de menores", "Autorizaciones de los apoderados", "Apoderados", "Recibido",
                        -6, 120, "", ""),
                       ("Transporte", "Furgón al mirador", "Transportes de ejemplo", "Pendiente", 0, 30, "",
                        "Confirmar la hora de vuelta.")],
        "fondos": "200000", "fondos_de": "Proyecto de la feria científica", "iva": ("", ""), "grupos": None,
        "version_corta": [1, 3, 4, 6],
    },
    {
        "genero": "Drama", "titulo": "La voz de Rocío", "guion": DRAMA, "ciudad": "Valparaíso", "serie": 14,
        "en_escena": {1: ["PROFESORA ANDREA", "ROCÍO", "LUCAS"], 2: ["ROCÍO", "RODRIGO"], 3: ["PROFESORA ANDREA", "ROCÍO", "LUCAS"], 4: ["LUCAS", "ROCÍO"], 5: ["ROCÍO", "LUCAS", "RODRIGO", "PROFESORA ANDREA"], 6: ["ROCÍO", "LUCAS", "RODRIGO"]},
        "voces": ["ABUELA TERE"],
        "premisa": ("Una niña que llega a mitad de año a un liceo de Valparaíso no se atreve a hablar en clases, "
                    "hasta que el taller de teatro le pide leer en voz alta una carta a su abuela."),
        "escaleta": ["Rocío llega al liceo y no dice nada. Lucas le presta un lápiz.",
                     "En casa, Rocío habla sin parar con su abuela por videollamada. Su papá la escucha.",
                     "La profesora de teatro pide escribir una carta para leerla en voz alta. Rocío se va.",
                     "En la escalera, Lucas le cuenta que tartamudea. Rocío habla por primera vez.",
                     "En la muestra, Rocío lee su carta frente a todos y a su abuela.",
                     "Bajando la escalera, la abuela le dice que la escuchó fuerte y claro."],
        "elenco": [
            ("ROCÍO", dict(genero="Femenino", edad="13", profesion="Estudiante de 8° básico",
                           biografia="Llegó desde Punta Arenas en junio. Extraña a su abuela y el viento.",
                           actor_nombre="Rocío Aguilera", vestuario="Abrigo de lana enorme, gris (es de la abuela).",
                           emergencia_telefono="+56 9 0000 1449 (papá)")),
            ("LUCAS", dict(genero="Masculino", edad="13", profesion="Estudiante de 8° básico",
                           biografia="Tartamudea cuando se pone nervioso; por eso casi no habla en clases.",
                           actor_nombre="Lucas Henríquez", vestuario="Uniforme y una bufanda azul.")),
            ("PROFESORA ANDREA", dict(genero="Femenino", edad="35", profesion="Profesora de teatro",
                                      biografia="Cree que todos tienen algo que decir.", actor_nombre="Profesora Andrea Lillo",
                                      vestuario="Blusa de colores y un pañuelo en la cabeza.")),
            ("RODRIGO", dict(genero="Masculino", edad="40", profesion="Papá de Rocío",
                             biografia="Se cambió de ciudad por trabajo. Se siente culpable del silencio de Rocío.",
                             actor_nombre="Rodrigo Aguilera (apoderado)", vestuario="Chaleco con capucha y jeans.")),
            ("ABUELA TERE", dict(genero="Femenino", edad="70", profesion="Abuela de Rocío",
                                 biografia="Vive en Punta Arenas. Se ríe fuerte y llora fácil.",
                                 actor_nombre="Teresa Barría", actor_notas="Graba sus partes por videollamada, desde su casa.",
                                 alimentacion="Sin gluten")),
        ],
        "locaciones": [("Liceo", dict(ubicacion="Cerro de Ejemplo 12, Valparaíso", precio_dia="0",
                                      detalles="La sala de teatro se pide con una semana de anticipación. La escalera está al lado del liceo.",
                                      hospital="Hospital de ejemplo · Subida Ejemplo 20 · urgencias +56 9 0000 1499")),
                       ("Casa De Rocío", dict(ubicacion="Pasaje de Ejemplo 8, Valparaíso", precio_dia="10000",
                                              detalles="Casa en el cerro: subir el equipo por la escalera. Cocina chica.",
                                              hospital="Hospital de ejemplo · Subida Ejemplo 20 · urgencias +56 9 0000 1499"))],
        "crew": [("Ema Fuentealba", "Dirección"), ("Joaquín Lara", "Asistente de dirección"),
                 ("Profesora Andrea Lillo", "Producción"), ("Florencia Paredes", "Cámara (DP)"),
                 ("Bastián Ríos", "Sonido directo"), ("Josefina Arce", "Arte y vestuario"),
                 ("Martín Cáceres", "Iluminación")],
        "equipos": [("Cámara réflex del liceo", "Con lente 35 mm", "Liceo (préstamo)", "1", "0"),
                    ("Estabilizador de mano (gimbal)", "Para la escalera", "Arriendo audiovisual (ejemplo)", "1", "7000"),
                    ("Micrófono de corbata (lavalier)", "", "Liceo (préstamo)", "2", "0"),
                    ("Foco con difusor", "Para la muestra", "Arriendo audiovisual (ejemplo)", "1", "5000")],
        "jornadas": [(1, "Liceo", [1, 3, 4, 2], "09:00", "El liceo de día y la cocina de noche",
                      "Colación en el casino (13:00) y once en la casa (18:00)", "", "Casa De Rocío"),
                     (2, "Liceo", [5, 6], "17:30", "La muestra y la escalera de noche",
                      "Colación para el elenco y los extras (sándwich y jugo)", "")],
        "planos": {
            1: [("PG", "Normal", "Fijo", "24 mm", "La sala; Rocío de pie junto a la profesora."),
                ("PP", "Normal", "Fijo", "50 mm", "Rocío niega con la cabeza."),
                ("PD", "Normal", "Fijo", "50 mm", "Lucas le pasa el lápiz.")],
            2: [("PM", "Normal", "Fijo", "35 mm", "Rocío ríe con su abuela en el notebook."),
                ("PA", "Normal", "Fijo", "35 mm", "Rodrigo la escucha desde la puerta.")],
            3: [("PG", "Picado", "Fijo", "18 mm", "El círculo de sillas."),
                ("PM", "Normal", "Paneo", "35 mm", "Rocío se para y sale.")],
            4: [("PE", "Normal", "Fijo", "24 mm", "Los dos en la escalera, frente al mar."),
                ("PP", "Normal", "Fijo", "50 mm", "Rocío habla por primera vez.")],
            5: [("PG", "Normal", "Fijo", "24 mm", "La muestra: el público y el foco."),
                ("PP", "Normal", "Dolly", "50 mm", "Rocío lee su carta."),
                ("PM", "Normal", "Fijo", "35 mm", "Rodrigo con el celular en alto.")],
            6: [("PE", "Normal", "Travelling", "24 mm", "Los tres bajan la escalera."),
                ("PMC", "Normal", "Fijo", "35 mm", "Rocío le pone el abrigo a Lucas.")]},
        "objetos": {1: [("pupitre", -1.2, -0.8, 0), ("pupitre", 1.2, -0.8, 0), ("pizarra", 0.0, -2.4, 0), ("escritorio", -1.8, -1.8, 0)],
                    2: [("cocina", -1.5, -2.0, 0), ("mesa", 0.5, -0.8, 0), ("notebook", 0.5, -0.8, 0), ("caja", 2.0, -1.5, 0), ("caja", 2.2, -1.0, 15)],
                    3: [("silla", -1.0, -0.5, 60), ("silla", 1.0, -0.5, -60), ("silla", 0.0, -1.5, 0), ("silla", 0.0, 0.7, 180)],
                    4: [("escalera", 0.0, -1.0, 0), ("farol", 1.6, -1.5, 0), ("agua", 0.0, -4.0, 0)],
                    5: [("reflector", 0.0, -2.0, 180), ("butacas", 0.0, 1.8, 180), ("silla", -2.5, 1.8, 180)],
                    6: [("escalera", 0.0, -1.0, 0), ("farol", 1.6, -1.5, 0), ("farol", -1.6, -1.0, 0)]},
        "recorrido": (6, "ROCÍO", [(0.0, 1.4), (0.0, 0.0), (0.2, -1.6)]),
        "sol": {4: "16:30", 6: "20:30"},
        "fichas_escenas": {
            2: dict(proposito="Mostrar que Rocío sí habla, cuando se siente segura.", subtexto="El papá descubre lo que su hija extraña.",
                    tono="Íntimo", notas_direccion="El notebook se graba en directo con la abuela; probar la conexión antes."),
            4: dict(proposito="El encuentro: alguien la entiende.", objetivo_protagonista="Que la dejen sola.",
                    obstaculo="Lucas no se va.", subtexto="Los dos tienen miedo de hablar.", tono="Tierno",
                    referencias="Valparaíso: escaleras, el mar al fondo, luz de la tarde."),
            5: dict(proposito="El clímax: Rocío encuentra su voz.", tono="Emotivo",
                    notas_direccion="La carta se lee completa una vez, de corrido; después se hacen los planos cortos.")},
        "gastos": [("Catering", "Colación para el equipo", "Casino del liceo", 12, "2000", "jornadas"),
                   ("Catering", "Sándwich y jugo para los extras de la muestra", "Almacén de ejemplo", 20, "1200", None),
                   ("Arte y vestuario", "Abrigo de lana (feria de segunda mano)", "Feria de ejemplo", 1, "6000", None)],
        "pagos": [("gasto:Arte y vestuario", -5, "Comprado en la feria")],
        "documentos": [("Autorización de menores", "Autorizaciones de los apoderados", "Apoderados", "Recibido",
                        -6, 120, "", ""),
                       ("Contrato de locación", "Uso de la casa de la familia Aguilera", "Familia Aguilera", "Firmado",
                        -3, 60, "", ""),
                       ("Cesión de derechos / imagen", "Cesión de imagen de los apoderados (extras)", "Apoderados",
                        "Pendiente", 0, 365, "", "Llevar las hojas impresas a la muestra.")],
        "fondos": "100000", "fondos_de": "Fondo del taller de teatro", "iva": ("", ""), "grupos": "linea",
        "version_corta": [1, 2, 5, 6],
    },
    {
        "genero": "Suspenso", "titulo": "Último recreo", "guion": SUSPENSO, "ciudad": "Santiago", "serie": 15,
        "en_escena": {1: ["PROFESOR VALDÉS", "INSPECTOR PATRICIO"], 2: ["DIEGO", "ANTONIA"], 3: ["ANTONIA", "DIEGO"], 4: ["JOAQUÍN", "ANTONIA", "DIEGO"], 5: ["ANTONIA", "JOAQUÍN", "DIEGO"], 6: ["JOAQUÍN", "PROFESOR VALDÉS", "DIEGO", "ANTONIA"]},
        "voces": [],
        "premisa": ("Cuando desaparecen las respuestas de la prueba de matemáticas, un estudiante acusado sin "
                    "pruebas tiene hasta el último recreo para descubrir quién las sacó."),
        "escaleta": ["Desaparecen las respuestas de la prueba y el inspector sospecha de Diego.",
                     "Antonia decide investigar: tienen hasta el último recreo.",
                     "En la fotocopiadora encuentran una hoja atascada y el código del segundo B.",
                     "En la biblioteca ven a Joaquín esconder un sobre en una enciclopedia.",
                     "En el patio, Joaquín confiesa: tuvo miedo de devolverlo.",
                     "Joaquín devuelve el sobre. La prueba se hace igual, con otras preguntas."],
        "elenco": [
            ("DIEGO", dict(genero="Masculino", edad="15", profesion="Estudiante de 2° medio",
                           biografia="Tranquilo y buen compañero. Nunca se ha metido en problemas.", actor_nombre="Diego Fuentes",
                           vestuario="Uniforme con la corbata suelta.")),
            ("ANTONIA", dict(genero="Femenino", edad="15", profesion="Estudiante de 2° medio",
                             biografia="Lee novelas de detectives y anota todo en su libreta.", actor_nombre="Antonia Bravo",
                             vestuario="Uniforme, chaleco rojo y la libreta en el bolsillo.")),
            ("JOAQUÍN", dict(genero="Masculino", edad="15", profesion="Delegado del 2° B",
                             biografia="Quiere ser perfecto en todo. Esta vez se equivocó.", actor_nombre="Joaquín Medina",
                             vestuario="Uniforme impecable y una insignia de delegado.")),
            ("PROFESOR VALDÉS", dict(genero="Masculino", edad="45", profesion="Profesor de matemáticas",
                                     biografia="Justo, pero desordenado con sus papeles.", actor_nombre="Profesor Carlos Fierro",
                                     vestuario="Camisa a cuadros y lápiz en la oreja.")),
            ("INSPECTOR PATRICIO", dict(genero="Masculino", edad="50", profesion="Inspector general",
                                        biografia="Siempre sospecha del primero que encuentra.", actor_nombre="Patricio Lobos (apoderado)",
                                        actor_valor_dia="15000", vestuario="Terno gris y un silbato al cuello.")),
        ],
        "locaciones": [("Liceo", dict(ubicacion="Avenida de Ejemplo 900, Santiago", precio_dia="0",
                                      detalles="La biblioteca se ocupa en la mañana: grabarla a las 15:00. La fotocopiadora hace ruido: apagarla para el sonido.",
                                      hospital="Hospital de ejemplo · Av. Ejemplo 1200 · urgencias +56 9 0000 1599"))],
        "crew": [("Pablo Contreras", "Dirección"), ("Isidora Méndez", "Asistente de dirección"),
                 ("Profesora Ximena Ruiz", "Producción"), ("Felipe Orellana", "Cámara (DP)"),
                 ("Constanza Aravena", "Sonido directo"), ("Emilia Toro", "Script y continuidad"),
                 ("Cristóbal Vidal", "Arte y utilería")],
        "equipos": [("Cámara réflex del liceo", "Con lente 18-55 mm", "Liceo (préstamo)", "1", "0"),
                    ("Celular para la segunda cámara", "", "Propio", "1", "0"),
                    ("Trípode", "", "Liceo (préstamo)", "2", "0"),
                    ("Grabadora de sonido", "Con pértiga (boom)", "Arriendo audiovisual (ejemplo)", "1", "6000"),
                    ("Slider", "Para los planos del reloj", "Arriendo audiovisual (ejemplo)", "1", "5000")],
        "jornadas": [(1, "Liceo", [1, 2, 3, 6], "08:30", "Interiores de la mañana",
                      "Colación en el casino (13:00)", "Permiso de la dirección (sábado)"),
                     (2, "Liceo", [4, 5], "14:30", "Biblioteca y patio",
                      "Colación en el casino (14:00)", "Permiso de la dirección (sábado)")],
        "planos": {
            1: [("PM", "Normal", "Fijo", "35 mm", "Valdés da vuelta el escritorio."),
                ("PA", "Contrapicado", "Fijo", "24 mm", "El inspector en la puerta."),
                ("INS", "Normal", "Slider", "50 mm", "El reloj: 10:15.")],
            2: [("PA", "Normal", "Travelling", "24 mm", "Diego y Antonia caminan (cámara delante)."),
                ("PD", "Picado", "Fijo", "50 mm", "Antonia anota en la libreta.")],
            3: [("PM", "Normal", "Fijo", "35 mm", "Antonia abre la bandeja."),
                ("INS", "Normal", "Fijo", "50 mm", "La pantalla: código 214.")],
            4: [("PG", "Normal", "Fijo", "24 mm", "La biblioteca en silencio."),
                ("SH", "Normal", "Fijo", "50 mm", "Joaquín esconde el sobre (sobre el hombro de Antonia)."),
                ("INS", "Normal", "Slider", "50 mm", "El reloj: 12:55.")],
            5: [("PE", "Normal", "Fijo", "24 mm", "Joaquín solo en la banca."),
                ("PP", "Normal", "Fijo", "50 mm", "Joaquín confiesa.")],
            6: [("PM", "Normal", "Fijo", "35 mm", "Joaquín deja el sobre."),
                ("PP", "Normal", "Fijo", "50 mm", "Antonia: «Caso cerrado».")]},
        "objetos": {1: [("escritorio", 0.0, -1.2, 0), ("archivador", -2.0, -2.2, 0), ("reloj_pared", 0.0, -2.45, 0), ("silla_oficina", 0.0, -1.8, 0)],
                    2: [("puerta", -2.0, -2.5, 0), ("puerta", 1.5, -2.5, 0)],
                    3: [("impresora", 0.0, -1.6, 0), ("papelero", 1.0, -1.8, 0)],
                    4: [("librero", -2.0, -2.0, 0), ("librero", 0.0, -2.2, 0), ("mesa", 1.0, 0.5, 0), ("libros", 1.0, 0.5, 0), ("reloj_pared", 2.5, -2.45, 0)],
                    5: [("banca", 0.0, -0.8, 0), ("arbol", -2.5, -1.8, 0), ("basurero", 2.0, -1.0, 0)],
                    6: [("escritorio", 0.0, -1.2, 0), ("silla_oficina", 0.0, -1.8, 0), ("archivador", -2.0, -2.2, 0)]},
        "recorrido": (2, "DIEGO", [(-2.5, 1.0), (-0.5, 0.2), (1.5, -0.6)]),
        "sol": {5: "13:00"},
        "fichas_escenas": {
            1: dict(proposito="El conflicto: las respuestas desaparecen.", objetivo_protagonista="Encontrar el sobre.",
                    obstaculo="No hay pistas.", tono="Tenso", notas_direccion="El inserto del reloj en todas las escenas marca el tiempo."),
            4: dict(proposito="La pista definitiva.", subtexto="Joaquín tiene miedo, no es un villano.",
                    tono="Suspenso", referencias="Silencio de biblioteca: solo se escucha el reloj.",
                    notas_direccion="El flash del celular se hace de verdad: avisar a los extras."),
            5: dict(proposito="La confesión.", tono="Dramático y honesto")},
        "gastos": [("Catering", "Colación para el equipo", "Casino del liceo", 13, "2000", "jornadas"),
                   ("Arte y vestuario", "Sobres, insignia y libreta", "Librería (ejemplo)", 1, "4500", None),
                   ("Imprevistos", "Imprevistos", "", 1, "8000", None)],
        "pagos": [("equipamiento:Slider", -1, "Arriendo pagado por adelantado"),
                  ("gasto:Arte y vestuario", -4, "")],
        "documentos": [("Autorización de menores", "Autorizaciones de los apoderados", "Apoderados", "Recibido",
                        -5, 120, "", ""),
                       ("Permiso municipal", "Permiso de la dirección para grabar el sábado", "Dirección del liceo",
                        "Firmado", -6, 30, "", ""),
                       ("Contrato de actor", "Contrato del Inspector Patricio", "Patricio Lobos", "Firmado",
                        -3, 30, "", "Valor por día en su ficha.")],
        "fondos": "90000", "fondos_de": "Fondo del curso", "iva": ("", ""), "grupos": None,
        "version_corta": [1, 3, 4, 5, 6],
    },
]

TAMANOS = {"GPG": 1, "PG": 2, "PE": 3, "PA": 4, "PM": 5, "PMC": 6, "PP": 7, "PPP": 8, "PD": 9, "SH": 11, "INS": 12}
COLORES_BEAT = ["#5b6ef5", "#ff8c1a", "#2f9e5e", "#d94f72", "#8e5bf5", "#e8a33d"]


def armar_proyecto(m, p: dict, base: date):
    """Un Documento completo, con las fechas escritas desde «base»."""
    autor = "Taller de cine (ejemplo)"
    fecha_nota = (base - timedelta(days=3)).isoformat() + " 18:00"
    doc = m.Documento()
    doc.bloques = bloques_desde_marcado(m, p["guion"], autor, fecha_nota)
    doc.titulo = p["titulo"]
    doc.autor_id = autor
    doc.coautores = "Estudiantes del taller de cine"
    doc.borrador = "Guion de ejemplo de ¡Acción!"
    doc.fecha_portada = f"{m._MESES_LARGOS[base.month - 1].capitalize()} de {base.year}"
    doc.contacto = "taller.cine@correo.example"
    doc.premisa = p["premisa"]
    doc.escaleta = list(p["escaleta"])
    doc.comentarios = ("Guion de ejemplo de ¡Acción!: los nombres, teléfonos, correos y direcciones son "
                       "inventados. Úsalo para practicar o como base para tu propia película. "
                       f"Fondos del presupuesto: {p['fondos_de'].lower()}.")
    doc.moneda, doc.pais_default = "CLP", "CL"
    doc.version_corta = list(p.get("version_corta") or [])
    serie = p["serie"]
    lugar_sol, lat, lon, region = CIUDADES[p["ciudad"]]
    ciudad = p["ciudad"]

    # ── Pizarra de beats: una tarjeta por punto de la escaleta, conectadas ──
    for k, punto in enumerate(doc.escaleta):
        b = m.Beat(titulo=f"Escena {k + 1}", descripcion=punto, color=COLORES_BEAT[k % len(COLORES_BEAT)],
                   x=40.0 + (k % 3) * 230.0, y=40.0 + (k // 3) * 190.0, w=200.0, h=150.0)
        if k + 1 < len(doc.escaleta):
            b.conexiones_lados = [{"destino": k + 1, "lado_origen": "right" if k % 3 != 2 else "bot",
                                   "lado_destino": "left" if k % 3 != 2 else "top"}]
        doc.beats.append(b)

    # ── Elenco ──
    for k, (nombre, campos) in enumerate(p["elenco"], 1):
        campos = {c: v for c, v in campos.items() if c in {f.name for f in m.fields(m.Ficha)}}
        f = m.Ficha(personaje=nombre, nacionalidad="Chilena", **campos)
        if not f.actor_telefono:
            f.actor_telefono = _tel(serie, k)
        if not f.actor_correo:
            f.actor_correo = re.sub(r"[^a-z.]", "", m._sin_tildes(f.actor_nombre.split("(")[0].strip().lower()
                                                                  .replace(" ", "."))) + "@correo.example"
        if not f.emergencia_telefono:
            f.emergencia_telefono = f"{_tel(serie, 40 + k)} (apoderado/a)"
        if not f.actor_valor_dia:
            f.actor_valor_dia = "0"
        if f.alimentacion == "Omnívoro":
            f.alimentacion = "Omnívoro/a"
        doc.fichas[nombre] = f
    # ── Locaciones ──
    for nombre, campos in p["locaciones"]:
        doc.locaciones[nombre] = m.Locacion(nombre=nombre, gps=f"{lat:.4f},{lon:.4f}", pais="CL", region=region,
                                            ciudad=ciudad, **campos)
    # ── Crew y equipamiento ──
    for k, (nombre, rol) in enumerate(p["crew"], 1):
        precio = "20000" if "invitado" in rol.lower() else "0"
        doc.tecnicos.append(m.Tecnico(
            nombre=nombre, rol=rol, telefono=_tel(serie, 20 + k),
            correo=re.sub(r"[^a-z.]", "", m._sin_tildes(nombre.lower().replace(" ", "."))) + "@correo.example",
            emergencia_telefono=_tel(serie, 60 + k), precio_dia=precio,
            alimentacion="Vegetariano/a" if k % 4 == 0 else "Omnívoro/a"))
    for nombre, modelo, prov, cant, precio in p["equipos"]:
        doc.equipamiento.append(m.Equipamiento(nombre=nombre, modelo=modelo, proveedor=prov, cantidad=cant,
                                               precio_dia=precio, contacto=f"contacto.{serie}@correo.example"
                                               if "ejemplo" in prov else ""))
    # ── Carta Gantt: las jornadas (los sábados que vienen) ──
    crew = ", ".join(t.nombre for t in doc.tecnicos)
    equipos = ", ".join(e.nombre for e in doc.equipamiento)
    for k, (semana, lugar, escenas, hora, nombre, comida, permisos, *otra) in enumerate(p["jornadas"], 1):
        d = _sab(base, semana)
        j = m.Jornada(nombre=f"Jornada {k} — {nombre}", fecha=d.isoformat(), fecha_fin=d.isoformat(),
                      lugar=lugar, lugar_2=(otra[0] if otra else ""), hora_citacion=hora,
                      escenas=", ".join(str(x) for x in escenas),
                      tecnicos=crew, equipamiento=equipos,
                      transporte="Cada uno llega por su cuenta; el equipo pesado va en el auto de producción.",
                      alimentacion=comida, permisos=permisos,
                      notas="Ejemplo: ajusta los horarios a tu liceo.")
        m.completar_actores_de_jornada(doc, j)
        ya = [a.strip() for a in j.actores.split(",") if a.strip()]
        for n_ in escenas:
            for nombre_ in p["en_escena"].get(n_, []):
                if nombre_ not in ya:
                    ya.append(nombre_)
        j.actores = ", ".join(ya)
        doc.jornadas.append(j)
    # (una actriz no puede un domingo: se ve en su ficha y en la Carta Gantt)
    primera = next(iter(doc.fichas.values()))
    primera.disponibilidad.inhabiles = [(_sab(base, 1) + timedelta(days=1)).isoformat()]

    # ── Lista de planos y storyboard en 3D ──
    escenas = m.escenas_con_bloques(doc.bloques)
    for n, lista in p["planos"].items():
        for k, (tam, ang, mov, lente, desc) in enumerate(lista, 1):
            pl = {"escena": n, "numero": str(k), "tamano": m.TAMANOS_PLANO[TAMANOS[tam]], "angulo": ang,
                  "movimiento": mov, "lente": lente, "descripcion": desc,
                  "duracion": "4 s" if tam not in ("INS", "PD") else "2 s", "notas": "", "hecho": False}
            m.asegurar_id_plano(pl)
            doc.planos.append(pl)
    lugares = [(-0.8, 0.0, 0.0), (0.8, 0.0, 180.0), (0.0, -1.0, 90.0), (-1.6, -0.7, 45.0), (1.6, -0.7, 135.0)]
    for e in escenas:
        n = e["n"]
        enc = doc.bloques[e["desde"]].texto
        planta = m.planta_de_escena(doc, n, crear=True)
        els = planta.setdefault("elementos", [])
        presentes = [x for x in p["en_escena"].get(n, []) if x not in p["voces"]]
        for k, nombre in enumerate(presentes):
            x, y, a = lugares[k % len(lugares)]
            els.append({"id": m.nuevo_id_corto(), "tipo": "personaje", "nombre": nombre, "x": x, "y": y, "ang": a})
        pers = [el for el in els if el.get("tipo") == "personaje"]
        if len(pers) >= 2:
            planta["eje"] = [pers[0]["id"], pers[1]["id"]]
        # (las voces —por radio, en la tele o por videollamada— no van en la planta)
        planta["ignorar"] = [f"nombre:{m.clave_nombre(v)}" for v in p["voces"]]
        if enc.startswith("INT"):
            for x1, y1, x2, y2 in ((-3, -2.5, 3, -2.5), (3, -2.5, 3, 2.5), (-3, 2.5, -3, -2.5)):
                els.append({"id": m.nuevo_id_corto(), "tipo": "pared", "x1": x1, "y1": y1, "x2": x2, "y2": y2})
        for clase, x, y, ang in p["objetos"].get(n, []):
            el = {"id": m.nuevo_id_corto(), "tipo": "mueble", "sb": True, "clase": clase, "x": x, "y": y, "ang": float(ang)}
            if clase in ("puerta", "ventana", "cuadro", "espejo", "reloj_pared", "pizarra") and enc.startswith("INT"):
                m.pegar_a_pared_planta(planta, el)
                m.orientar_hacia_adentro(planta, el)
            els.append(el)
        hora = p["sol"].get(n)
        if hora:                                      # ☀ el sol, el día de su jornada
            fecha_j = next((j.fecha for j in doc.jornadas if str(n) in [s.strip() for s in j.escenas.split(",")]),
                           base.isoformat())
            planta["sol"] = {"activo": True, "lugar": lugar_sol, "lat": lat, "lon": lon, "fecha": fecha_j,
                             "hora": hora, "norte": 0.0}
            planta["cielo"] = {"modo": "sol"}
        m.completar_planta_sb(doc, n, m.cuadros_ordenados(doc, {n}), planta, respetar_borrados=True)
    rn, quien, pts = p["recorrido"]
    pl_r = m.planta_de_escena(doc, rn)
    pers = next((e for e in pl_r["elementos"] if e.get("tipo") == "personaje"
                 and m.clave_nombre(e.get("nombre")) == m.clave_nombre(quien)), None)
    if pers is not None:
        pers["x"], pers["y"] = pts[0]
        pl_r["elementos"].append({"id": m.nuevo_id_corto(), "tipo": "recorrido", "quien": pers["id"],
                                  "puntos": [list(q) for q in pts], "color": "#ff8c1a"})

    # ── Análisis por escena ──
    for n, campos in p["fichas_escenas"].items():
        e = next(x for x in escenas if x["n"] == n)
        doc.fichas_escenas[str(n)] = m.FichaEscena(numero=n, encabezado=doc.bloques[e["desde"]].texto, **campos)

    # ── Presupuesto ──
    doc.presupuesto_fondos = p["fondos"]
    for nombre, icono in p.get("categorias_propias", []):
        doc.categorias_propias.append({"nombre": nombre, "icono": icono})
    ids_gasto = {}
    for cat, concepto, prov, cant, valor, cuando in p["gastos"]:
        g = {"id": m.nuevo_id_corto(), "categoria": cat, "concepto": concepto, "proveedor": prov,
             "cantidad": cant, "valor": valor, "notas": ""}
        if cuando:
            g["cuando"] = cuando
        doc.gastos.append(g)
        ids_gasto.setdefault(cat, g["id"])
    for clave, dias, notas in p["pagos"]:
        if clave.startswith("gasto:"):
            clave = "gasto:" + ids_gasto[clave.split(":", 1)[1]]
        doc.pagos[clave] = {"pagado": True, "fecha_pago": (base + timedelta(days=dias)).isoformat(), "notas": notas}
    modo, tasa = p["iva"]
    doc.iva_modo, doc.iva_tasa = modo, tasa
    if modo:
        doc.iva_exentos = ["cat:Elenco", "cat:Catering"]
    for clave, cat in (p.get("lineas_movidas") or {}).items():
        doc.categoria_lineas[clave] = cat
    if p.get("grupos"):
        m.aplicar_grupos_de_ejemplo(doc, p["grupos"])
        if p.get("categorias_propias"):
            for g in doc.grupos_categorias:
                if g["nombre"] in ("Imprevistos y otros",):
                    g["categorias"] += [c for c, _i in p["categorias_propias"]]
    # ── Contratos y seguros ──
    for tipo, titulo, contraparte, estado, firma, vence, monto, notas in p["documentos"]:
        doc.documentos_legales.append({
            "id": m.nuevo_id_corto(), "tipo": tipo, "titulo": titulo, "contraparte": contraparte,
            "estado": estado, "firma": (base + timedelta(days=firma)).isoformat() if estado in ("Firmado", "Vigente", "Recibido") else "",
            "vence": (base + timedelta(days=vence)).isoformat(), "monto": monto,
            "archivo_nombre": "", "archivo_datos": "", "notas": notas})
    m.completar_ejemplo_call_sheet(doc)
    doc.ejemplo_fecha_base = base.isoformat()
    return doc


def armar_todos(carpeta: Path, base: date | None = None) -> list[Path]:
    m = _modulo_accion()
    from PySide6.QtWidgets import QApplication
    _app = QApplication.instance() or QApplication(sys.argv[:1])
    base = base or date.today()
    carpeta.mkdir(parents=True, exist_ok=True)
    rutas = []
    for p in PROYECTOS:
        doc = armar_proyecto(m, p, base)
        ruta = carpeta / f"{p['genero']} - {p['titulo']}.accion"
        ruta.write_text(m.documento_a_json(doc), encoding="utf-8")
        rutas.append(ruta)
    return rutas


def main() -> int:
    carpeta = Path(sys.argv[1]) if len(sys.argv) > 1 else AQUI / "guiones de ejemplo"
    if not os.environ.get("QT_QPA_PLATFORM") and sys.platform.startswith("linux") and not os.environ.get("DISPLAY"):
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
    try:
        sys.stdout.reconfigure(errors="replace")          # (la consola de Windows y las tildes)
    except Exception:
        pass
    for r in armar_todos(carpeta):
        print(f"       {r.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
