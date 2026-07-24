from panda3d.core import loadPrcFileData
# Fuerza a Panda3D a usar el renderizador por software (ignora la GPU)
loadPrcFileData('', 'load-display p3tinydisplay')
from ursina.shaders import basic_lighting_shader
from ursina import *
from ursina.prefabs.editor_camera import EditorCamera
from panda3d.core import TransparencyAttrib
from ursina.shader import Shader
from ursina.shaders import lit_with_shadows_shader
app = Ursina()

# =====================================================
# MODELO
# =====================================================

modelo = Entity(
    model='player/sala1',
    position=(0, 0, 0),
    scale=1,
    shader=lit_with_shadows_shader,
    texture='texture_default'
)
modelo.setTransparency(TransparencyAttrib.MNone, 1)
# 2. Obliga a que el modelo calcule qué caras están delante de las otras
modelo.setDepthWrite(True)
modelo.setDepthTest(True)
# --- AÑADE ESTO ---

Entity(
    model='cube',
    color=color.red,
    scale=(0.05,0.05,2),
    z=1
)

Entity(
    model='cube',
    color=color.blue,
    scale=(2,0.05,0.05),
    x=1
)

Entity(
    model='cube',
    color=color.green,
    scale=(0.05,2,0.05),
    y=1
)

# =====================================================
# ILUMINACIÓN
# =====================================================

AmbientLight(
    color=color.rgb(10, 10, 20) # Valores bajos, casi un gris oscuro azulado
)

# El sol principal, un poco menos intenso que el blanco puro
sun = DirectionalLight(
    shadows=True,
    color=color.rgb(100, 100, 100)
)

sun.look_at(Vec3(-1,-1,-1))

# =====================================================
# CÁMARA LIBRE
# =====================================================

camera.fov = 70

editor_camera = EditorCamera(
    rotation_speed=200,
    panning_speed=10,
    zoom_speed=2
)

# =====================================================
# INFO
# =====================================================

Text(
    text="""
CLICK DERECHO = rotar
RUEDA = zoom
MIDDLE CLICK = mover
""",
    scale=0.8,
    position=(-0.85,0.45)
)

app.run()