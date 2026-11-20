; ════════════════════════════════════════════════════════════════════
;  ¡Acción! Software Audiovisual — instalador para Windows (Inno Setup 6)
; ════════════════════════════════════════════════════════════════════
;  Lo compila compilar_instalador.bat (después de armar el programa con
;  PyInstaller). También se puede abrir con Inno Setup y apretar F9, si
;  ya existe la carpeta «compilacion\dist\Accion».
;
;  Lo que hace:
;   • Instala sin pedir permisos de administrador (en la carpeta de
;     programas del usuario). Al empezar ofrece instalarlo «para todos
;     los usuarios» del computador (eso sí pide administrador).
;   • Accesos en el menú Inicio (el programa, los guiones de ejemplo y la
;     licencia) y, si se quiere, en el escritorio.
;   • Doble clic en un .accion → se abre en ¡Acción! (y «Abrir con» para
;     .fdx y .fountain).
;   • Al instalar una versión nueva encima, reemplaza el programa y no
;     toca los proyectos ni la configuración.
;   • 🎬 Con Inno Setup 6.7 o más nuevo, el asistente tiene personalidad:
;     un fondo propio en cada página (la pizarra de rodaje al empezar,
;     «¡Corten!» al terminar) y, mientras avanza la barra, seis estilos de
;     cine que se van alternando: la pizarra, el guion, el estreno, el rollo
;     de 35 mm, la cinta y los 8 bits. Los fondos están en la carpeta
;     «estilos_instalador». Con un Inno Setup más antiguo, o sin esa
;     carpeta, sale con el aspecto de siempre.
;   • 🎞 Y los fondos se mueven (como un flipbook): la claqueta se cierra
;     (¡clac!), el guion se escribe a máquina, corren las ampolletas del
;     estreno, la cuenta regresiva del rollo, giran los carretes de la cinta
;     y el saludo de 8 bits pasa en scroll. Los cuadros están en
;     «estilos_instalador\animacion»; sin esa carpeta, los fondos quedan fijos.
;   • 🎷 Una música de bossa jazz (propia, instrumental) mientras se
;     instala, con un botón «♪ Sin música» para apagarla. En las
;     instalaciones silenciosas no suena.
;   • 📁 Siempre se puede elegir la carpeta (también al instalar encima):
;     «Examinar» deja elegir cualquiera o crear una nueva.
;   • 🎨 Deja una marca de la instalación: al abrir ¡Acción! por primera vez
;     después, parte en el tema Nova con hoja blanca.
;   • 🎬 Trae los cinco guiones de ejemplo (en «Guiones de ejemplo»).
;   • 🔄 ¡Acción! se actualiza solo: baja este instalador (de la versión
;     nueva), lo corre en silencio con /SILENT /ABRIR=1 y se vuelve a abrir.
;     Para instalarlo en muchos computadores a la vez (área de informática):
;       Instalar_Accion_<versión>.exe /VERYSILENT /ALLUSERS /NORESTART
;
;  IMPORTANTE: no cambies el AppId. Es lo que hace que cada versión nueva
;  se instale encima de la anterior (y no como otro programa).
; ════════════════════════════════════════════════════════════════════

#define MiNombre      "¡Acción!"
#define MiDescripcion "¡Acción! Software Audiovisual"
#define MiEditor      "Gabriel González Vilches"
#define MiInstagram   "https://www.instagram.com/accionsoftware"
#define MiEjecutable  "Accion.exe"
#define Compilacion   AddBackslash(SourcePath) + "compilacion"

; La versión: la pasa compilar_instalador.bat (/DMiVersion=…) o se lee de
; compilacion\version.txt (la escribe recursos_instalador.py).
#ifndef MiVersion
  #if FileExists(Compilacion + "\version.txt")
    #define ArchivoVersion FileOpen(Compilacion + "\version.txt")
    #define MiVersion Trim(FileRead(ArchivoVersion))
    #expr FileClose(ArchivoVersion)
    #undef ArchivoVersion
  #else
    #define MiVersion "1.9.3"
  #endif
#endif

; 🤖 Con /DConIA=1 (compilar_instalador.bat, IA=si) se arma ADEMÁS el instalador
; «con IA»: lleva Ollama y el modelo del Asesor (compilacion\ia_paquete, lo prepara
; preparar_ia.py). El de siempre (sin IA) es el que usan las actualizaciones.
#ifdef ConIA
  #define SufijoIA "_con_IA"
#else
  #define SufijoIA ""
#endif

[Setup]
AppId={{FF05A8F9-CB6C-4DBE-A687-3B81828B289C}
AppName={#MiNombre}
AppVersion={#MiVersion}
AppVerName={#MiNombre} {#MiVersion}
AppPublisher={#MiEditor}
AppContact={#MiEditor} · Instagram @accionsoftware
; (en «Aplicaciones» de Windows: el nombre del editor y «Ayuda» llevan al Instagram)
AppPublisherURL={#MiInstagram}
AppSupportURL={#MiInstagram}
AppCopyright=© 2026 {#MiEditor} · Licencia MIT
AppComments=Guion, storyboard 3D y producción audiovisual. Gratis y de uso libre.
VersionInfoVersion={#MiVersion}
VersionInfoProductName={#MiNombre}
VersionInfoDescription=Instalador de {#MiDescripcion}
VersionInfoCompany={#MiEditor}
VersionInfoCopyright=© 2026 {#MiEditor}

; Dónde se instala: sin administrador → %LOCALAPPDATA%\Programs\Accion
;                   para todos        → C:\Program Files\Accion
DefaultDirName={autopf}\Accion
DefaultGroupName={#MiNombre}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=commandline dialog
UsePreviousAppDir=yes
; 📁 La página de la carpeta se muestra siempre (también al instalar encima de
;    una versión anterior), para poder elegir otra o crear una nueva
DisableDirPage=no

; La licencia que hay que aceptar (y que queda junto al programa)
LicenseFile=EULA_Accion.rtf

; El asistente
; 🎬 Los estilos de cine piden Inno Setup 6.7 o más nuevo (los fondos de página
;   y cambiarlos mientras se instala) y la carpeta «estilos_instalador».
#if (Ver >= EncodeVer(6, 7, 0)) && FileExists(AddBackslash(SourcePath) + "estilos_instalador\fondo_portada_100.png")
  #define ConEstilos
#else
  #pragma message "Sin los estilos de cine (piden Inno Setup 6.7 o más nuevo y la carpeta estilos_instalador): el instalador sale con el aspecto de siempre."
#endif
#if FileExists(AddBackslash(SourcePath) + "estilos_instalador\musica_instalador.wav") && FileExists(AddBackslash(SourcePath) + "estilos_instalador\silencio.wav")
  #define ConMusica
#endif
; 🎞 Las animaciones de los fondos: los cuadros (estilos_instalador\animacion) y el
;   archivo que dice dónde va cada capa (estilos_instalador\animaciones.iss).
#ifdef ConEstilos
  #if FileExists(AddBackslash(SourcePath) + "estilos_instalador\animaciones.iss") && FileExists(AddBackslash(SourcePath) + "estilos_instalador\animacion\cuadro_pizarra_0_100.png")
    #define ConAnimacion
  #else
    #pragma message "Sin las animaciones de los fondos (falta estilos_instalador\animacion o animaciones.iss): los fondos quedan fijos."
  #endif
#endif
#ifdef ConEstilos
; (oscuro, para que los textos claros se lean sobre los fondos; al empezar, la pizarra)
WizardStyle=modern dark
WizardBackImageFile=estilos_instalador\fondo_portada_100.png,estilos_instalador\fondo_portada_200.png
WizardImageFile=
WizardSmallImageFile=
#else
WizardStyle=modern
#endif
DisableWelcomePage=no
ShowLanguageDialog=no
#if FileExists(Compilacion + "\accion.ico")
SetupIconFile=compilacion\accion.ico
#endif
#ifndef ConEstilos
  #if FileExists(Compilacion + "\asistente_grande.bmp")
WizardImageFile=compilacion\asistente_grande.bmp,compilacion\asistente_grande_2x.bmp
WizardSmallImageFile=compilacion\asistente_chico.bmp,compilacion\asistente_chico_2x.bmp
  #endif
#endif
UninstallDisplayIcon={app}\{#MiEjecutable}
UninstallDisplayName={#MiNombre} {#MiVersion}

; Windows 10 u 11 de 64 bits (lo que pide Qt 6)
MinVersion=10.0
#if Ver >= EncodeVer(6, 3, 0)
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
#else
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
#endif

; Si ¡Acción! está abierto, ofrece cerrarlo antes de instalar encima
CloseApplications=yes
RestartApplications=no

ChangesAssociations=yes
SetupLogging=yes

; El instalador queda en la carpeta «instalador»
OutputDir=instalador
OutputBaseFilename=Instalar_Accion_{#MiVersion}{#SufijoIA}
Compression=lzma2/max
SolidCompression=yes
LZMAUseSeparateProcess=yes
#ifdef ConIA
; (Inno Setup 6.5.2 o más nuevo: un solo .exe de hasta ~4 GB; con NVIDIA o con un
;  Inno Setup más antiguo, el instalador va en partes: el .exe y sus .bin, juntos)
  #if (Ver < EncodeVer(6,5,2)) || Defined(IANvidia)
DiskSpanning=yes
    #if Ver >= EncodeVer(6,5,2)
DiskSliceSize=max
    #endif
  #endif
#endif

[Languages]
Name: "es"; MessagesFile: "compiler:Languages\Spanish.isl"

[Messages]
es.SelectDirBrowseLabel=Para seguir, haz clic en Siguiente. Si quieres otra carpeta, haz clic en Examinar: puedes elegir cualquiera o crear una nueva con «Nueva carpeta». También puedes escribir la ruta aquí abajo: si la carpeta no existe, se crea.
es.WelcomeLabel2=Se instalará [name/ver] en tu computador.%n%nEscribe tu guion, arma el storyboard en 3D y prepara el rodaje: todo en un solo programa, gratis y de uso libre.%n%nTe recomendamos cerrar las demás aplicaciones antes de seguir.

[Tasks]
Name: "escritorio"; Description: "Crear un acceso directo en el escritorio"; GroupDescription: "Accesos directos:"
Name: "asociar"; Description: "Abrir los archivos .accion con ¡Acción! (doble clic)"; GroupDescription: "Archivos:"
#ifndef ConIA
Name: "descargar_ia"; Description: "Preparar al Profesor Claqueta (el asesor con IA, funciona en este computador) en segundo plano: se descarga sola mientras usas el programa, sin ocupar toda tu conexión (unos 3 GB; si hay una tarjeta gráfica, la parte para ella: entre 650 y 950 MB con una NVIDIA, 12 MB con una AMD o Intel)"; GroupDescription: "Profesor Claqueta (IA):"
#endif
Name: "descargar_voz"; Description: "Preparar el dictado por voz (escribir el guion hablando con F2, pensado para personas ciegas; funciona en este computador, sin internet) en segundo plano: unos 250 MB en un computador sin tarjeta gráfica, 1,6 GB con una NVIDIA"; GroupDescription: "Dictado por voz:"

[InstallDelete]
; (lo interno de la versión anterior se reemplaza entero: así no quedan archivos viejos)
Type: filesandordirs; Name: "{app}\_internal"
Type: filesandordirs; Name: "{app}\Licencias de terceros"
#ifdef ConIA
Type: filesandordirs; Name: "{app}\ia\ollama"
#endif

[UninstallRun]
Filename: "{sys}\netsh.exe"; Parameters: "advfirewall firewall delete rule name=""Accion - colaboracion en red"""; Flags: runhidden; RunOnceId: "QuitarReglaFirewall"; Check: IsAdminInstallMode

[UninstallDelete]
; (los modelos de IA que se descarguen después también se van al desinstalar)
Type: filesandordirs; Name: "{app}\ia"
; (y el dictado por voz: whisper.cpp y su modelo, que se bajan a %LOCALAPPDATA%\Accion\voz)
Type: filesandordirs; Name: "{localappdata}\Accion\voz"
; (y la IA que se bajó sola en segundo plano, en %LOCALAPPDATA%\Accion\ia; una carpeta elegida en
; Configuración no se toca: puede ser de la persona)
Type: filesandordirs; Name: "{localappdata}\Accion\ia"
Type: filesandordirs; Name: "{localappdata}\Accion\ia_pendiente"
; (y la parte de Ollama para tarjetas NVIDIA, que se baja aparte si hay una)
Type: filesandordirs; Name: "{localappdata}\Accion\ollama_gpu"
Type: filesandordirs; Name: "{localappdata}\Accion\ollama_gpu.parcial"
Type: files; Name: "{localappdata}\Accion\ollama_gpu.zip"

#ifdef ConIA
[Dirs]
; (los modelos: que se puedan agregar otros desde el Asesor, también sin ser administrador)
Name: "{app}\ia\modelos"; Permissions: users-modify
#endif

[INI]
; (lo que se eligió al instalar: ¡Acción! lo lee al abrir; después se cambia en Configuración)
#ifndef ConIA
Filename: "{app}\preferencias_instalacion.ini"; Section: "ia"; Key: "descargar"; String: "1"; Tasks: descargar_ia
Filename: "{app}\preferencias_instalacion.ini"; Section: "ia"; Key: "descargar"; String: "0"; Tasks: not descargar_ia
#endif
Filename: "{app}\preferencias_instalacion.ini"; Section: "voz"; Key: "descargar"; String: "1"; Tasks: descargar_voz
Filename: "{app}\preferencias_instalacion.ini"; Section: "voz"; Key: "descargar"; String: "0"; Tasks: not descargar_voz
; 🎨 La marca de esta instalación: la primera vez que se abre ¡Acción! después,
;    parte en el tema Nova con hoja blanca. Las actualizaciones automáticas (en
;    silencio, con /ABRIR=1) no la cambian: no le cambian los colores a nadie.
Filename: "{app}\preferencias_instalacion.ini"; Section: "instalacion"; Key: "id"; String: "{#MiVersion}-{code:MarcaDeInstalacion}"; Check: not AbrirDespuesDeActualizar

[Files]
; (Primero lo que solo usa el asistente, que lo saca al abrirse: con la compresión
;  sólida, Inno Setup recomienda poner esos archivos al comienzo.)
#ifdef ConEstilos
; 🎬 Los fondos del asistente: solo los usa el instalador (no se copian al computador).
;   Son dibujos propios; sus letras se dibujaron con tipografías de licencia libre
;   (SIL OFL 1.1: Bebas Neue, Courier Prime, Bungee, Oswald, VT323,
;   Press Start 2P, Inter; Apache 2.0: Permanent Marker, Special Elite). Las
;   tipografías no van en el instalador: solo la imagen ya dibujada.
Source: "estilos_instalador\fondo_*.png"; Flags: dontcopy noencryption
#endif
#ifdef ConAnimacion
; 🎞 Los cuadros de las animaciones (recortes de los mismos dibujos, a 100 % y 200 %)
Source: "estilos_instalador\animacion\cuadro_*.png"; Flags: dontcopy noencryption
#endif
#ifdef ConMusica
; 🎷 La música del asistente (propia: «Cielo de Fa», bossa jazz sintetizada desde
;    cero) y medio segundo de silencio para apagarla. Solo la usa el instalador.
Source: "estilos_instalador\musica_instalador.wav"; Flags: dontcopy noencryption
Source: "estilos_instalador\silencio.wav"; Flags: dontcopy noencryption
#endif
; El programa (lo arma PyInstaller en compilacion\dist\Accion)
Source: "compilacion\dist\Accion\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; La licencia
Source: "EULA_Accion.rtf"; DestDir: "{app}"; DestName: "Licencia.rtf"; Flags: ignoreversion
; Los guiones de ejemplo (si están en la carpeta «guiones de ejemplo»)
Source: "guiones de ejemplo\*.accion"; DestDir: "{app}\Guiones de ejemplo"; Flags: ignoreversion skipifsourcedoesntexist
#ifdef ConIA
; 🤖 La IA del Asesor: Ollama (MIT), el modelo (Qwen, Apache 2.0) y sus licencias
Source: "compilacion\ia_paquete\ollama\*"; DestDir: "{app}\ia\ollama"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "compilacion\ia_paquete\modelos\*"; DestDir: "{app}\ia\modelos"; Flags: ignoreversion recursesubdirs createallsubdirs nocompression
Source: "compilacion\ia_paquete\ia.ini"; DestDir: "{app}\ia"; Flags: ignoreversion
Source: "compilacion\ia_paquete\licencias\*"; DestDir: "{app}\ia\licencias"; Flags: ignoreversion recursesubdirs createallsubdirs
#endif

[Icons]
Name: "{group}\{#MiNombre}"; Filename: "{app}\{#MiEjecutable}"; Comment: "{#MiDescripcion}"
#if DirExists(AddBackslash(SourcePath) + "guiones de ejemplo")
Name: "{group}\Guiones de ejemplo"; Filename: "{app}\Guiones de ejemplo"; Comment: "Guiones para practicar"
#endif
Name: "{group}\Licencia de uso"; Filename: "{app}\Licencia.rtf"
Name: "{group}\Licencias de terceros"; Filename: "{app}\Licencias de terceros\LEEME.txt"
#ifdef ConIA
Name: "{group}\Licencias de la IA (Profesor Claqueta)"; Filename: "{app}\ia\licencias\LEEME_IA.txt"
#endif
Name: "{autodesktop}\{#MiNombre}"; Filename: "{app}\{#MiEjecutable}"; Comment: "{#MiDescripcion}"; Tasks: escritorio

[Registry]
; Doble clic en un .accion
Root: HKA; Subkey: "Software\Classes\.accion"; ValueType: string; ValueName: ""; ValueData: "Accion.Proyecto"; Flags: uninsdeletevalue; Tasks: asociar
Root: HKA; Subkey: "Software\Classes\.accion\OpenWithProgids"; ValueType: string; ValueName: "Accion.Proyecto"; ValueData: ""; Flags: uninsdeletevalue; Tasks: asociar
Root: HKA; Subkey: "Software\Classes\Accion.Proyecto"; ValueType: string; ValueName: ""; ValueData: "Proyecto de ¡Acción!"; Flags: uninsdeletekey; Tasks: asociar
Root: HKA; Subkey: "Software\Classes\Accion.Proyecto\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MiEjecutable},0"; Tasks: asociar
Root: HKA; Subkey: "Software\Classes\Accion.Proyecto\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MiEjecutable}"" ""%1"""; Tasks: asociar
; «Abrir con» ¡Acción! para los guiones de Final Draft y Fountain (sin quitarle esos archivos a otros programas)
Root: HKA; Subkey: "Software\Classes\.fdx\OpenWithProgids"; ValueType: string; ValueName: "Accion.Proyecto"; ValueData: ""; Flags: uninsdeletevalue; Tasks: asociar
Root: HKA; Subkey: "Software\Classes\.fountain\OpenWithProgids"; ValueType: string; ValueName: "Accion.Proyecto"; ValueData: ""; Flags: uninsdeletevalue; Tasks: asociar
; El programa en la lista de «Abrir con»
Root: HKA; Subkey: "Software\Classes\Applications\{#MiEjecutable}"; ValueType: string; ValueName: "FriendlyAppName"; ValueData: "{#MiNombre}"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\Applications\{#MiEjecutable}\SupportedTypes"; ValueType: string; ValueName: ".accion"; ValueData: ""
Root: HKA; Subkey: "Software\Classes\Applications\{#MiEjecutable}\SupportedTypes"; ValueType: string; ValueName: ".fdx"; ValueData: ""
Root: HKA; Subkey: "Software\Classes\Applications\{#MiEjecutable}\SupportedTypes"; ValueType: string; ValueName: ".fountain"; ValueData: ""
Root: HKA; Subkey: "Software\Classes\Applications\{#MiEjecutable}\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MiEjecutable}"" ""%1"""

[Run]
; 👥 Colaboración en red: al instalar para todos los usuarios (como administrador),
;    el firewall de Windows deja entrar a ¡Acción! en las redes privadas. Sin
;    administrador, Windows lo pregunta la primera vez que alguien abre una sesión.
;    (La regla se quita y se vuelve a poner, por si cambió la carpeta.)
Filename: "{sys}\netsh.exe"; Parameters: "advfirewall firewall delete rule name=""Accion - colaboracion en red"""; Flags: runhidden; Check: IsAdminInstallMode
Filename: "{sys}\netsh.exe"; Parameters: "advfirewall firewall add rule name=""Accion - colaboracion en red"" dir=in action=allow program=""{app}\{#MiEjecutable}"" enable=yes profile=private,domain"; Flags: runhidden; StatusMsg: "Permitiendo la colaboración en red…"; Check: IsAdminInstallMode
Filename: "{app}\{#MiEjecutable}"; Description: "Abrir {#MiNombre} ahora"; Flags: nowait postinstall skipifsilent
; 🔄 Cuando ¡Acción! se actualiza solo (corre este instalador con /SILENT /ABRIR=1), se vuelve a abrir
Filename: "{app}\{#MiEjecutable}"; Flags: nowait runasoriginaluser; Check: AbrirDespuesDeActualizar

[Code]
// ¿Lo pidió ¡Acción! al actualizarse? (instalación silenciosa con /ABRIR=1).
// Una instalación silenciosa hecha por el área de informática (sin /ABRIR=1)
// no abre el programa.
function AbrirDespuesDeActualizar: Boolean;
begin
  Result := WizardSilent and (ExpandConstant('{param:ABRIR|0}') = '1');
end;

// 🎨 La marca de la instalación (la versión y la hora): ¡Acción! la ve al abrir
// y, si es nueva, parte en el tema Nova con hoja blanca.
function MarcaDeInstalacion(Param: String): String;
begin
  Result := GetDateTimeString('yyyymmddhhnnss', #0, #0);
end;
#ifdef ConMusica

// ─── 🎷 La música del asistente ───
// Suena en bucle desde que se abre el asistente hasta que se cierra. El botón
// de abajo a la izquierda la apaga y la vuelve a prender. En una instalación
// silenciosa (también las actualizaciones automáticas) no suena.
const
  SND_ASYNC = $0001;
  SND_NODEFAULT = $0002;
  SND_LOOP = $0008;
  SND_FILENAME = $00020000;
var
  BotonMusica: TNewButton;
  MusicaSonando: Boolean;

function PlaySound(const Sonido: String; Modulo: Cardinal; Opciones: Cardinal): Boolean;
  external 'PlaySoundW@winmm.dll stdcall';

procedure PonerMusica(Encendida: Boolean);
begin
  if Encendida then
    PlaySound(ExpandConstant('{tmp}\musica_instalador.wav'), 0, SND_ASYNC or SND_NODEFAULT or SND_LOOP or SND_FILENAME)
  else
    // (medio segundo de silencio, sin bucle: así se suelta el archivo de la música)
    PlaySound(ExpandConstant('{tmp}\silencio.wav'), 0, SND_NODEFAULT or SND_FILENAME);
  MusicaSonando := Encendida;
  if BotonMusica <> nil then
  begin
    if Encendida then
      BotonMusica.Caption := '♪ Sin música'
    else
      BotonMusica.Caption := '♪ Con música';
  end;
end;

procedure BotonMusicaClick(Sender: TObject);
begin
  PonerMusica(not MusicaSonando);
end;

<event('InitializeWizard')>
procedure IniciarMusica;
begin
  BotonMusica := nil;
  MusicaSonando := False;
  if WizardSilent then
    Exit;
  try
    ExtractTemporaryFile('musica_instalador.wav');
    ExtractTemporaryFile('silencio.wav');
  except
    Log('No se pudo sacar la música del asistente: ' + GetExceptionMessage);
    Exit;
  end;
  BotonMusica := TNewButton.Create(WizardForm);
  BotonMusica.Parent := WizardForm;
  BotonMusica.Left := ScaleX(16);
  BotonMusica.Top := WizardForm.CancelButton.Top;
  BotonMusica.Width := ScaleX(118);
  BotonMusica.Height := WizardForm.CancelButton.Height;
  BotonMusica.OnClick := @BotonMusicaClick;
  PonerMusica(True);
end;

<event('DeinitializeSetup')>
procedure PararMusica;
begin
  if MusicaSonando then
    PonerMusica(False);
end;
#endif
#ifdef ConEstilos

// ─── 🎬 Los estilos de cine del asistente ───
// Cada página tiene su fondo: la portada (la pizarra abierta), las de adentro
// (la licencia, las tareas, «Listo para instalar»…), la final («¡Corten!») y,
// mientras se instala, seis «actos» que se van alternando a medida que avanza
// la barra: 1 la pizarra, 2 el guion, 3 el estreno, 4 el rollo de 35 mm,
// 5 la cinta y 6 los 8 bits. Cada fondo viene en dos tamaños (100 % y 200 %):
// Inno Setup elige el que mejor calza con la pantalla.
// (Con /SILENT, cuando ¡Acción! se actualiza solo, se ve la barra con los
//  actos; con /VERYSILENT no se ve nada.)
const
  CANTIDAD_ACTOS = 6;
var
  FondoPuesto: String;

function NombreFondo(I: Integer): String;
begin
  case I of
    0: Result := 'portada';
    1: Result := 'interior';
    8: Result := 'final';
  else
    Result := 'acto' + IntToStr(I - 1);
  end;
end;

procedure CambiarFondo(const Nombre: String);
var
  Imagenes: TArrayOfGraphic;
  Chica, Grande: TPngImage;
begin
  Chica := nil;
  Grande := nil;
  try
    try
      Chica := TPngImage.Create;
      Chica.LoadFromFile(ExpandConstant('{tmp}\fondo_' + Nombre + '_100.png'));
      Grande := TPngImage.Create;
      Grande.LoadFromFile(ExpandConstant('{tmp}\fondo_' + Nombre + '_200.png'));
      SetArrayLength(Imagenes, 2);
      Imagenes[0] := Chica;
      Imagenes[1] := Grande;
      // (WizardSetBackImage se queda con una copia: estas se pueden liberar)
      WizardSetBackImage(Imagenes, True, True, 255);
      FondoPuesto := Nombre;
    except
      Log('No se pudo poner el fondo ' + Nombre + ': ' + GetExceptionMessage);
    end;
  finally
    if Grande <> nil then
      Grande.Free;
    if Chica <> nil then
      Chica.Free;
  end;
end;

#ifdef ConAnimacion
// ─── 🎞 Lo que se mueve en los fondos (como un flipbook) ───
// Cada «capa» es un rectángulo del fondo que cambia: una imagen encima del
// fondo, en la página que corresponde, que cambia de cuadro cada 1/10 de
// segundo con un temporizador de Windows. Los cuadros son recortes de los
// mismos dibujos del fondo, a 100 % y 200 % (se usan los que calzan con la
// pantalla). Qué capas hay, dónde van y en qué orden pasan sus cuadros está
// en estilos_instalador\animaciones.iss (se genera junto con los dibujos).
// (El temporizador va pegado a la ventana del asistente: Windows lo apaga
//  solo cuando la ventana se cierra.)
const
  TIC_ANIMACION = 100;
  ID_TEMPORIZADOR = 4711;
var
  CapaEscena, CapaNombre: array of String;
  CapaPadre, CapaX, CapaY, CapaW, CapaH, CapaCuadros: array of Integer;
  CapaPrimerCuadro, CapaSecInicio, CapaSecLargo, CapaPos, CapaActual: array of Integer;
  CapaImagen: array of TBitmapImage;
  Cuadros: array of TPngImage;
  Secuencias: array of Integer;
  EscenaAnimada: String;
  AnimacionLista: Boolean;

function SetTimer(hWnd, nIDEvent, uElapse, lpTimerFunc: Longword): Longword;
  external 'SetTimer@user32.dll stdcall';

// Una capa (la llama DefinirCapasAnimadas, en animaciones.iss). Sec: el cuadro de
// cada tic, «0*22,1,2» = el 0 durante 22 tics, el 1 y el 2.
procedure AgregarCapa(const Escena: String; Padre, X, Y, W, H: Integer; const Nombre: String;
  NCuadros: Integer; const Sec: String);
var
  I, J, K, Rep, Cuadro, Coma: Integer;
  Resto, Parte: String;
begin
  I := GetArrayLength(CapaEscena);
  SetArrayLength(CapaEscena, I + 1);
  SetArrayLength(CapaNombre, I + 1);
  SetArrayLength(CapaPadre, I + 1);
  SetArrayLength(CapaX, I + 1);
  SetArrayLength(CapaY, I + 1);
  SetArrayLength(CapaW, I + 1);
  SetArrayLength(CapaH, I + 1);
  SetArrayLength(CapaCuadros, I + 1);
  SetArrayLength(CapaPrimerCuadro, I + 1);
  SetArrayLength(CapaSecInicio, I + 1);
  SetArrayLength(CapaSecLargo, I + 1);
  SetArrayLength(CapaPos, I + 1);
  SetArrayLength(CapaActual, I + 1);
  SetArrayLength(CapaImagen, I + 1);
  CapaEscena[I] := Escena;
  CapaNombre[I] := Nombre;
  CapaPadre[I] := Padre;
  CapaX[I] := X;
  CapaY[I] := Y;
  CapaW[I] := W;
  CapaH[I] := H;
  CapaCuadros[I] := NCuadros;
  CapaPrimerCuadro[I] := -1;
  CapaPos[I] := 0;
  CapaActual[I] := -1;
  CapaImagen[I] := nil;
  CapaSecInicio[I] := GetArrayLength(Secuencias);
  Resto := Sec + ',';
  while Resto <> '' do
  begin
    Coma := Pos(',', Resto);
    Parte := Copy(Resto, 1, Coma - 1);
    Delete(Resto, 1, Coma);
    if Parte = '' then
      Continue;
    K := Pos('*', Parte);
    if K > 0 then
    begin
      Cuadro := StrToIntDef(Copy(Parte, 1, K - 1), 0);
      Rep := StrToIntDef(Copy(Parte, K + 1, Length(Parte)), 1);
    end
    else
    begin
      Cuadro := StrToIntDef(Parte, 0);
      Rep := 1;
    end;
    if (Cuadro < 0) or (Cuadro >= NCuadros) then
      Cuadro := 0;
    for J := 1 to Rep do
    begin
      K := GetArrayLength(Secuencias);
      SetArrayLength(Secuencias, K + 1);
      Secuencias[K] := Cuadro;
    end;
  end;
  CapaSecLargo[I] := GetArrayLength(Secuencias) - CapaSecInicio[I];
end;

#include "estilos_instalador\animaciones.iss"

// Dónde va la capa: su rectángulo en el fondo de 596×432, llevado al tamaño de la
// ventana (el fondo se estira a toda la ventana) y a las coordenadas de su página.
procedure UbicarCapa(I: Integer);
var
  Ctl: TControl;
  OX, OY, CW, CH, X0, Y0, X1, Y1: Integer;
begin
  OX := 0;
  OY := 0;
  Ctl := CapaImagen[I].Parent;
  while (Ctl <> nil) and (Ctl <> WizardForm) do
  begin
    OX := OX + Ctl.Left;
    OY := OY + Ctl.Top;
    Ctl := Ctl.Parent;
  end;
  CW := WizardForm.ClientWidth;
  CH := WizardForm.ClientHeight;
  X0 := CapaX[I] * CW div 596;
  Y0 := CapaY[I] * CH div 432;
  X1 := (CapaX[I] + CapaW[I]) * CW div 596;
  Y1 := (CapaY[I] + CapaH[I]) * CH div 432;
  CapaImagen[I].SetBounds(X0 - OX, Y0 - OY, X1 - X0, Y1 - Y0);
end;

procedure PonerCuadro(I: Integer);
var
  C: Integer;
begin
  C := Secuencias[CapaSecInicio[I] + CapaPos[I]];
  if C <> CapaActual[I] then
  begin
    CapaImagen[I].PngImage := Cuadros[CapaPrimerCuadro[I] + C];
    CapaActual[I] := C;
  end;
end;

procedure TicAnimacion(Wnd, Msg, IdEvento, Tiempo: Longword);
var
  I: Integer;
begin
  if not AnimacionLista then
    Exit;
  try
    for I := 0 to GetArrayLength(CapaEscena) - 1 do
      if CapaEscena[I] = EscenaAnimada then
      begin
        CapaPos[I] := CapaPos[I] + 1;
        if CapaPos[I] >= CapaSecLargo[I] then
          CapaPos[I] := 0;
        PonerCuadro(I);
      end;
  except
    // (si algo falla, los fondos quedan fijos: el asistente sigue igual)
    AnimacionLista := False;
    Log('Se detuvieron las animaciones: ' + GetExceptionMessage);
  end;
end;

// Muestra las capas de una escena (desde su primer cuadro) y esconde las demás.
procedure ActivarEscena(const Nombre: String);
var
  I: Integer;
begin
  EscenaAnimada := Nombre;
  if not AnimacionLista then
    Exit;
  try
    for I := 0 to GetArrayLength(CapaEscena) - 1 do
      if CapaEscena[I] = Nombre then
      begin
        UbicarCapa(I);
        CapaPos[I] := 0;
        PonerCuadro(I);
        CapaImagen[I].Visible := True;
      end
      else
        CapaImagen[I].Visible := False;
  except
    AnimacionLista := False;
    Log('No se pudo mostrar la animación de ' + Nombre + ': ' + GetExceptionMessage);
  end;
end;

<event('InitializeWizard')>
procedure PrepararAnimaciones;
var
  I, K: Integer;
  Escala: String;
  Png: TPngImage;
begin
  AnimacionLista := False;
  EscenaAnimada := '';
  try
    DefinirCapasAnimadas;
    // (los cuadros que calzan con la pantalla: los de 200 % desde 125 % de escala)
    if WizardForm.ClientWidth > 700 then
      Escala := '200'
    else
      Escala := '100';
    ExtractTemporaryFiles('{tmp}\cuadro_*_' + Escala + '.png');
    for I := 0 to GetArrayLength(CapaEscena) - 1 do
    begin
      // (dos capas con el mismo nombre usan los mismos cuadros: la claqueta de la
      //  portada y la del final)
      for K := 0 to I - 1 do
        if (CapaNombre[K] = CapaNombre[I]) and (CapaPrimerCuadro[I] < 0) then
          CapaPrimerCuadro[I] := CapaPrimerCuadro[K];
      if CapaPrimerCuadro[I] < 0 then
      begin
        CapaPrimerCuadro[I] := GetArrayLength(Cuadros);
        SetArrayLength(Cuadros, CapaPrimerCuadro[I] + CapaCuadros[I]);
        for K := 0 to CapaCuadros[I] - 1 do
        begin
          Png := TPngImage.Create;
          Png.LoadFromFile(ExpandConstant('{tmp}\cuadro_' + CapaNombre[I] + '_' + IntToStr(K) + '_' + Escala + '.png'));
          Cuadros[CapaPrimerCuadro[I] + K] := Png;
        end;
      end;
      CapaImagen[I] := TBitmapImage.Create(WizardForm);
      case CapaPadre[I] of
        0: CapaImagen[I].Parent := WizardForm.WelcomePage;
        1: CapaImagen[I].Parent := WizardForm.FinishedPage;
        2: CapaImagen[I].Parent := WizardForm.InstallingPage;
      else
        CapaImagen[I].Parent := WizardForm.MainPanel;
      end;
      CapaImagen[I].Stretch := True;
      CapaImagen[I].Visible := False;
    end;
    AnimacionLista := True;
    if SetTimer(WizardForm.Handle, ID_TEMPORIZADOR, TIC_ANIMACION, CreateCallback(@TicAnimacion)) = 0 then
    begin
      AnimacionLista := False;
      Log('No se pudo poner el temporizador de las animaciones.');
    end;
  except
    AnimacionLista := False;
    Log('Sin animaciones: ' + GetExceptionMessage);
  end;
end;
#endif

// El fondo de la página y, si hay, su animación.
procedure PonerFondo(const Nombre: String);
begin
  if Nombre <> FondoPuesto then
    CambiarFondo(Nombre);
#ifdef ConAnimacion
  if Nombre <> EscenaAnimada then
    ActivarEscena(Nombre);
#endif
end;

<event('InitializeWizard')>
procedure PrepararFondos;
var
  I: Integer;
begin
  // (la portada ya la pone WizardBackImageFile)
  FondoPuesto := 'portada';
  try
    for I := 0 to 8 do
    begin
      ExtractTemporaryFile('fondo_' + NombreFondo(I) + '_100.png');
      ExtractTemporaryFile('fondo_' + NombreFondo(I) + '_200.png');
    end;
  except
    Log('No se pudieron sacar los fondos del asistente: ' + GetExceptionMessage);
  end;
end;

procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = wpWelcome then
    PonerFondo('portada')
  else if CurPageID = wpInstalling then
    PonerFondo('acto1')
  else if CurPageID = wpFinished then
    PonerFondo('final')
  else
    PonerFondo('interior');
end;

// A medida que avanza la barra: un sexto para cada acto.
procedure CurInstallProgressChanged(CurProgress, MaxProgress: Integer);
var
  Acto: Integer;
begin
  if MaxProgress <= 0 then
    Exit;
  // (sin multiplicar números grandes, para no pasarse del máximo de un Integer)
  if MaxProgress >= CANTIDAD_ACTOS then
    Acto := CurProgress div (MaxProgress div CANTIDAD_ACTOS) + 1
  else
    Acto := (CurProgress * CANTIDAD_ACTOS) div MaxProgress + 1;
  if Acto < 1 then
    Acto := 1;
  if Acto > CANTIDAD_ACTOS then
    Acto := CANTIDAD_ACTOS;
  PonerFondo('acto' + IntToStr(Acto));
end;
#endif
