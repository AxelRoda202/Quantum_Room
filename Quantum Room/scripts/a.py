import os
from ursina import *

app = Ursina()

# Nombre o ruta de tu archivo MP4
video_path = 'assets/videos/choque.mp4'

# Crear el panel de video adherido a la interfaz de la cámara
video_player = Entity(model='quad', parent=camera.ui, scale=(1.5, 1), texture=video_path)

# Cargar el sonido del video por separado y sincronizarlo
video_sound = loader.loadSfx(video_path)
video_player.texture.synchronizeTo(video_sound)

# Iniciar la reproducción
video_sound.play()

app.run()