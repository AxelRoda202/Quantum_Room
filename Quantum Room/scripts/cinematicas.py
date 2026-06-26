# 1. PRIMERO CONFIGURAMOS EL MOTOR (Antes de que Ursina nazca)
from panda3d.core import loadPrcFileData
loadPrcFileData('', 'textures-power-2 none')

# 2. AHORA SÍ IMPORTAMOS TODO LO DEMÁS
from ursina import *
from panda3d.core import MovieTexture, Filename
import os

class GestorCinematica(Entity):
    def __init__(self, callback_fin, **kwargs):
        super().__init__(**kwargs)
        self.callback_fin = callback_fin
        
        # --- UI DE LA CINEMÁTICA ---
        # 1. El velo negro base (fondo absoluto)
        self.fondo_negro = Entity(parent=camera.ui, model='quad', scale=2, color=color.black, z=1)
        
       # 2. La pantalla donde se proyecta el video (Cambiado a negro por si falla)
        self.pantalla = Entity(parent=camera.ui, model='quad', scale=(camera.aspect_ratio, 1), color=color.black, z=0)
        
        # 3. Subtítulos (Estilo cinematográfico con sombra)
        self.subtitulos = Text(
            parent=camera.ui, 
            text='', 
            origin=(0, 0), # Centrado
            y=-0.4,        # Abajo en la pantalla
            scale=1.5, 
            color=color.white,
            shadow=True,   # Sombra negra para que resalte sobre fondos claros
            z=-1
        )
        
        # 4. El velo de parpadeo (Para transiciones de corte a negro)
        self.velo_parpadeo = Entity(parent=camera.ui, model='quad', scale=2, color=color.black, z=-2)
        
        self.indice_actual = 0
        self.audio_actual = None
        
        # --- LISTA DE ESCENAS ---
        # Ajusta el nombre de tus archivos y la duración EXACTA de cada video en segundos.
        # Si separas el audio, pon el nombre en 'audio'. Si no, déjalo como None.
        self.escenas = [
            {'video': 'assets/videos/choque.mp4', 'audio': None, 'duracion': 5.0, 'texto': 'Hay cosas que la mente decide enterrar...'},
            {'video': 'assets/videos/osito.mp4', 'audio': None, 'duracion': 5.0, 'texto': '...simplemente para poder seguir respirando.'},
            {'video': 'assets/videos/pared_fotos.mp4', 'audio': None, 'duracion': 5.0, 'texto': 'Pero los espacios vacíos terminan consumiéndote.'},
            {'video': 'assets/videos/aviso_deuda.mp4', 'audio': None, 'duracion': 5.0, 'texto': 'Y el mundo exterior no perdona.'},
            {'video': 'assets/videos/oferta_QR.mp4', 'audio': None, 'duracion': 5.0, 'texto': 'Hasta que alguien te ofrece una salida.'},
            {'video': 'assets/videos/pasillo.mp4', 'audio': None, 'duracion': 5.0, 'texto': 'Un precio justo por tu mente.'},
            {'video': 'assets/videos/contrato_firma.mp4', 'audio': None, 'duracion': 5.0, 'texto': 'Solo te piden que no hagas preguntas.'},
            {'video': 'assets/videos/acuerdo.mp4', 'audio': None, 'duracion': 5.0, 'texto': 'Después de todo, nadie más las hace.'},
            {'video': 'assets/videos/simulacion.mp4', 'audio': None, 'duracion': 5.0, 'texto': 'Solo cierra los ojos.'}
        ]

    def iniciar(self):
        self.velo_parpadeo.color = color.clear
        self.indice_actual = 0
        self.reproducir_siguiente()

    def reproducir_siguiente(self):
        # Detener audio anterior si existe
        if self.audio_actual:
            self.audio_actual.stop()

        if self.indice_actual < len(self.escenas):
            escena = self.escenas[self.indice_actual]
            ruta_video = escena['video']
            
            # --- MAGIA DE RUTAS ---
            ruta_script = os.path.dirname(os.path.abspath(__file__))
            ruta_raiz = os.path.dirname(ruta_script)
            ruta_absoluta = os.path.join(ruta_raiz, ruta_video)
            ruta_panda = Filename.fromOsSpecific(ruta_absoluta).getFullpath()
            
            try:
                # 1. Cargamos el video como MovieTexture
                tex_video = application.base.loader.loadTexture(ruta_panda)
                
                # 2. Asignamos a la pantalla y fijamos a 16:9 exacto
                self.pantalla.texture = tex_video
                self.pantalla.color = color.white 
 # 2. Asignamos a la pantalla y fijamos a 16:9 exacto
                self.pantalla.texture = tex_video
                self.pantalla.color = color.white 
                self.pantalla.scale = (camera.aspect_ratio, 1) 
                
                # PLAN B (Añade esta línea solo si el video sigue aplastado):
                self.pantalla.texture_scale = (1, 0.5)
                # 3. CARGAR SONIDO (Del propio .mp4 o de un archivo externo)
                if escena['audio']:
                    ruta_audio = os.path.join(ruta_raiz, escena['audio'])
                    ruta_audio_panda = Filename.fromOsSpecific(ruta_audio).getFullpath()
                    self.audio_actual = application.base.loader.loadSfx(ruta_audio_panda)
                else:
                    self.audio_actual = application.base.loader.loadSfx(ruta_panda)
                
                # 4. SINCRONIZAR Y REPRODUCIR (El método que descubriste)
                if type(tex_video) == MovieTexture:
                    tex_video.synchronizeTo(self.audio_actual)
                
                self.audio_actual.play()
                
            except Exception as e:
                print(f"Error al cargar el video {ruta_video}: {e}")
                self.pantalla.texture = None
                self.pantalla.color = color.black # Si falla, al menos queda en negro
            
            # --- Actualizar texto ---
            if escena['texto']:
                self.subtitulos.text = escena['texto']
            else:
                self.subtitulos.text = ''
            
            # Programar el salto a la siguiente escena
            invoke(self.reproducir_siguiente, delay=escena['duracion'])
            
            self.indice_actual += 1
        else:
            self.ejecutar_parpadeo_final()

    def ejecutar_parpadeo_final(self):
        # CORTE DE GOLPE A NEGRO
        self.velo_parpadeo.color = color.black
        self.pantalla.texture = None
        self.subtitulos.text = ''
        self.subtitulos.background.enabled = False
        
        # Esperamos 2 segundos en silencio total absoluto, luego llamamos al main
        invoke(self.terminar_y_limpiar, delay=2.0)

    def terminar_y_limpiar(self):
        # Le avisamos al main.py que ya terminamos
        self.callback_fin()
        
        # Nos destruimos para no consumir RAM
        destroy(self.fondo_negro)
        destroy(self.pantalla)
        destroy(self.subtitulos)
        destroy(self)
        # Nota: NO destruimos el velo_parpadeo aquí, porque el main.py lo usará para hacer el fade-in de despertar.
        
# =============================================================================
# BUCLE DE PRUEBA LOCAL (Solo se ejecuta si corres este script directamente)
# =============================================================================
if __name__ == '__main__':
    from panda3d.core import loadPrcFileData
    # Fuerza a Panda3D a usar el renderizador por software (ignora la GPU fallida)
    loadPrcFileData('', 'load-display p3tinydisplay')
    
    from ursina import *

    # 1. Inicializamos Ursina primero
    app = Ursina(title="Prueba de Cinemática")

    # 2. Función de prueba que se llamará al terminar los videos
    def al_terminar_prueba():
        print("La cinemática ha terminado correctamente.")
        application.quit() # Cierra la ventana automáticamente

    # 3. Creamos el gestor
    cinematica = GestorCinematica(callback_fin=al_terminar_prueba)

    # 4. Texto temporal de instrucciones
    texto_ayuda = Text(
        text="Presiona ESPACIO para iniciar la cinemática\n(Asegúrate de tener los .mp4 en la carpeta correcta)", 
        origin=(0,0), 
        scale=1.5,
        color=color.yellow
    )

    # 5. Control local para disparar la prueba
    def input(key):
        if key == 'space':
            if cinematica.indice_actual == 0:
                texto_ayuda.enabled = False # Ocultamos el texto
                cinematica.iniciar()
        
        elif key == 'escape':
            application.quit()

    app.run()