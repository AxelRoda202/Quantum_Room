# from panda3d.core import loadPrcFileData
# Fuerza a Panda3D a usar el renderizador por software (ignora la GPU)
# loadPrcFileData('', 'load-display p3tinydisplay')
from ursina.shaders import basic_lighting_shader
from ursina import *
from ursina.prefabs.editor_camera import EditorCamera
from panda3d.core import TransparencyAttrib
from ursina.shader import Shader
from ursina.shaders import lit_with_shadows_shader
app = Ursina()

vert = '''
#version 140
uniform mat4 p3d_ModelViewProjectionMatrix;
in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;
out vec2 texcoord;

void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    texcoord = p3d_MultiTexCoord0;
}
'''

# El Fragment Shader decide de qué color se pinta cada píxel
frag = '''
#version 140
uniform sampler2D p3d_Texture0;
uniform vec4 p3d_ColorScale;
in vec2 texcoord;
out vec4 fragColor;

void main() {
    // Lee el color original de tu modelo
    vec4 color = texture(p3d_Texture0, texcoord) * p3d_ColorScale;
    
    // Aquí puedes alterar el color. 
    // Por ahora, simplemente le decimos que dibuje tu color base exacto y lo oscurezca un poco.
    fragColor = color * 0.8; 
}
'''

# 2. CREAMOS EL SHADER EN URSINA
mi_shader_personalizado = Shader(language=Shader.GLSL, vertex=vert, fragment=frag)

window.title = "Visor de Modelo - Quantum Room"
#window.color = color.rgb(15, 15, 20)
POS_BRAZO_DER = Vec3( 0.2,  0.15,  0.0)   # derecha, levemente arriba, centrado
POS_BRAZO_IZQ = Vec3(-0.2,  0.15,  0.0)   # izquierda, levemente arriba, centrado

# Escala de los brazos relativa al cuerpo
ESCALA_BRAZOS = 1   # 1.0 = mismo tamaño que en el GLB original
MODELO_BRAZO_DER = 'player/Jugador_particula_arm_left_separado'   # assets/models/player/brazo_izq.glb
MODELO_BRAZO_IZQ = 'player/Jugador_particula_arm_right_separado'   # assets/models/player/brazo_der.glb
# =====================================================
# MODELO
# =====================================================

modelo = Entity(
    model='player/Jugador_particula_body_separado',
    position=(0, 0, 0),
    scale=1,
    shader=lit_with_shadows_shader,
    texture='texture_default'
)
# --- AÑADE ESTO ---
# 1. Fuerza al motor a ignorar cualquier transparencia del .glb (el '1' al final fuerza la prioridad)
modelo.setTransparency(TransparencyAttrib.MNone, 1)
# 2. Obliga a que el modelo calcule qué caras están delante de las otras
modelo.setDepthWrite(True)
modelo.setDepthTest(True)

brazo_der = Entity(
    parent  = modelo,             # HIJO del cuerpo — se mueve con él
    model   = MODELO_BRAZO_DER,
    scale   = ESCALA_BRAZOS,
    position= POS_BRAZO_DER,
    shader=lit_with_shadows_shader
)

brazo_der.setTransparency(TransparencyAttrib.MNone, 1)
brazo_der.setDepthWrite(True)
brazo_der.setDepthTest(True)

# ── Brazo izquierdo ───────────────────────────────────────────────────────────
brazo_izq = Entity(
    parent = modelo,
    model = MODELO_BRAZO_IZQ,
    scale = ESCALA_BRAZOS,
    position = POS_BRAZO_IZQ,
    shader=lit_with_shadows_shader
)

brazo_izq.setTransparency(TransparencyAttrib.MNone, 1)
brazo_izq.setDepthWrite(True)
brazo_izq.setDepthTest(True)

# =====================================================
# EJES DE REFERENCIA
# =====================================================

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