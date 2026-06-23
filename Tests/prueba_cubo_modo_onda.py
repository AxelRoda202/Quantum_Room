from panda3d.core import loadPrcFileData
loadPrcFileData('', 'load-display p3tinydisplay') # Forzamos tu CPU
from panda3d.core import TransparencyAttrib, Vec4
from ursina import *
import math

app = Ursina()
EditorCamera()

cubo = Entity(model='cube', scale=2, unlit=True)
cubo.setTransparency(TransparencyAttrib.MAlpha, 1)

def update():
    # Simulamos la probabilidad oscilando entre 0.0 y 1.0
    probabilidad = (math.sin(time.time() * 3) + 1.0) / 2.0
    
    # Altura
    cubo.scale_y = lerp(0.5, 3.5, probabilidad)
    
    # Color y Transparencia con Vec4 (R, G, B, Alpha)
    # IMPORTANTE: Vec4 usa valores de 0.0 a 1.0, NO de 0 a 255
    r = lerp(40/255, 180/255, probabilidad)
    a = lerp(0.1, 1.0, probabilidad) # 0.1 es casi invisible, 1.0 es sólido
    
    cubo.color = Vec4(90/255, 0, 1, a)

app.run()