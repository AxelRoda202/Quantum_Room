# =============================================================================
# PROGRAMA 1 — PERSONAJE CON FÍSICA DE BRAZOS
# =============================================================================
# Muestra el personaje sobre un plano simple para probar:
#   - Carga de modelos GLB del personaje
#   - Animación procedural de los brazos según el movimiento
#   - Controles WASD + cámaras del código original
#
# ESTRUCTURA DE CARPETAS NECESARIA:
# ────────────────────────────────────────────────────────────────
#   quantum_room/
#   ├── programa1_personaje.py   ← este archivo
#   └── assets/
#       └── models/
#           └── player/
#               ├── cuerpo.glb       ← solo el cuerpo/esfera
#               ├── brazo_izq.glb    ← brazo izquierdo
#               ├── brazo_der.glb    ← brazo derecho
#               └── player_todo.glb  ← modelo completo (no se usa aquí)
#
# NOTA: Los nombres de archivos deben coincidir EXACTAMENTE con los de abajo.
#       Si tus archivos tienen otro nombre, cambiá las variables de la sección
#       "CONFIGURACIÓN DE MODELOS" más abajo.
# =============================================================================

from ursina import *
from ursina.shaders import basic_lighting_shader, lit_with_shadows_shader

app = Ursina(
    title='Quantum Room — Test Personaje',
    borderless=False,
    fullscreen=False,
    # ── Cambiar resolución si necesitás ──
    # size=(1280, 720)
)

# =============================================================================
# SECCIÓN 1 — CONFIGURACIÓN DE MODELOS
# Cambiá los nombres de archivo aquí si los tuyos son distintos.
# Ursina busca automáticamente dentro de la carpeta assets/models/
# No hace falta escribir la ruta completa ni la extensión .glb
# =============================================================================

MODELO_CUERPO = 'player/Jugador_particula_body'       # assets/models/player/cuerpo.glb
MODELO_BRAZO_DER = 'player/Jugador_particula_arm_left'   # assets/models/player/brazo_izq.glb
MODELO_BRAZO_IZQ = 'player/Jugador_particula_arm_right'   # assets/models/player/brazo_der.glb

# SECCIÓN 2 — ESCALA Y POSICIÓN DEL PERSONAJE
# Si el modelo aparece muy grande, muy chico o enterrado en el piso,wwww
# ajustá estas variables:
#   ESCALA_PERSONAJE: multiplicador general (1 = tamaño original del GLB)ws
#   ALTURA_INICIAL:   altura Y donde aparece el personaje al iniciar
# =============================================================================

ESCALA_PERSONAJE = 1.0
ALTURA_INICIAL = 0.75   # debe ser aproximadamente la mitad de la altura del modelo

# =============================================================================
# SECCIÓN 3 — POSICIÓN DE LOS BRAZOS RELATIVA AL CUERPO
# Los brazos son hijos del cuerpo (parent=cuerpo), entonces su posición
# es RELATIVA al centro del cuerpo, no al mundo.
#   (x, y, z):
#     x positivo = derecha del personaje
#     x negativo = izquierda del personaje
#     y positivo = arriba
#     z positivo = adelante del personaje
# =============================================================================

# Offset de posición (donde están "pegados" al cuerpo)
POS_BRAZO_DER = Vec3( 0.2,  0.15,  0.0)   # derecha, levemente arriba, centrado
POS_BRAZO_IZQ = Vec3(-0.2,  0.15,  0.0)   # izquierda, levemente arriba, centrado

# Escala de los brazos relativa al cuerpo
ESCALA_BRAZOS = 1   # 1.0 = mismo tamaño que en el GLB original

# =============================================================================
# SECCIÓN 4 — FÍSICA DE BRAZOS (animación procedural)
# Estos valores controlan cómo se mueven los brazos según la acción:
#
#   ROTACION_CAMINAR:  cuántos grados rota el brazo al caminar (adelante/atrás)
#   ROTACION_GIRAR:    cuántos grados rota al girar (izq/der)
#   VELOCIDAD_LERP:    qué tan suave/rápida es la transición (0.1=lento, 0.9=rápido)
#
# Los brazos usan "animación de péndulo":
#   - Avanzar  → brazo der hacia atrás,  brazo izq hacia adelante
#   - Retroceder → brazo der hacia adelante, brazo izq hacia atrás
#   - Girar izq  → brazo der hacia atrás,  brazo izq hacia adelante (y viceversa)
# =============================================================================

ROTACION_CAMINAR = 35.0   # grados máximos al caminar (adelante/atrás)
ROTACION_GIRAR = 20.0   # grados máximos al girar
VELOCIDAD_LERP = 8.0    # suavidad de transición (mayor = más rápido)

# =============================================================================
# SECCIÓN 5 — CONTROLES DE MOVIMIENTO

VELOCIDAD_NORMAL = 5
VELOCIDAD_CTRL = 9
VELOCIDAD_SHIFT = 2.5
ROTACION_NORMAL = 100
ROTACION_CTRL = 130
ROTACION_SHIFT = 60

# =============================================================================
# CONSTRUCCIÓN DEL PERSONAJE
# =============================================================================

# ── Cuerpo principal ──────────────────────────────────────────────────────────
# Si el archivo cuerpo.glb no se encuentra, Ursina mostrará un cubo blanco.
# En ese caso verificá que la carpeta assets/models/player/ existe y tiene el archivo.
cuerpo = Entity(
    model=MODELO_CUERPO,
    scale=ESCALA_PERSONAJE,
    y=ALTURA_INICIAL,
    rotation_y=180
)
print(cuerpo.forward)
print(cuerpo.rotation)
cuerpo.setTransparency(0)       # desactiva el modo de transparencia de Panda3D
cuerpo.alpha = 1                # fuerza opacidad total (0 = invisible, 1 = opaco)

Entity(
    parent=cuerpo,
    model='cube',
    color=color.red,
    scale=(0.1,0.1,1),
    z=0.5
)
# ── Brazo derecho ─────────────────────────────────────────────────────────────
# parent=cuerpo hace que el brazo "siga" al cuerpo automáticamente.
# Cuando el cuerpo rota o se mueve, el brazo lo hace con él.
brazo_der = Entity(
    parent  = cuerpo,             # HIJO del cuerpo — se mueve con él
    model   = MODELO_BRAZO_DER,
    scale   = ESCALA_BRAZOS,
    position= POS_BRAZO_DER,
)
brazo_der.setTransparency(0)
brazo_der.alpha = 1

# ── Brazo izquierdo ───────────────────────────────────────────────────────────
brazo_izq = Entity(
    parent = cuerpo,
    model = MODELO_BRAZO_IZQ,
    scale = ESCALA_BRAZOS,
    position = POS_BRAZO_IZQ,
)
brazo_izq.setTransparency(0)
brazo_izq.alpha = 1

# =============================================================================
# PISO
# texture='white_cube' es una textura incluida en Ursina.
# Podés reemplazarla por 'brick', 'grass', o una textura propia:
#   ground = Entity(model='plane', texture='assets/textures/piso.png', ...)
# =============================================================================

ground = Entity(
    model = 'plane',
    scale = 40,
    texture = 'white_cube',       # textura de prueba incluida en Ursina
    texture_scale = (20, 20),
    color = color.rgb(60, 60, 75),
)

# =============================================================================
# ILUMINACIÓN BÁSICA
# Ursina por defecto no tiene luz, los modelos aparecen sin sombra.
# AmbientLight ilumina todo parejo, DirectionalLight simula el sol.
# =============================================================================

sun = DirectionalLight(
    shadows=True,
    color=color.rgb(255,245,240)
)

sun.look_at(Vec3(1,-1,-1))
AmbientLight(
    color=color.rgba(120,120,140,255)
)

# =============================================================================
# CÁMARAS (igual a tu código original)
# =============================================================================

modos_camara = ["tercera", "primera", "aerea", "libre"]
indice_modo = 0
distancia_tercera = 8
altura_aerea = 18
fov_primera = 90
editor_camera = EditorCamera(
    enabled=False
)

# =============================================================================
# ESTADO INTERNO DEL MOVIMIENTO
# Estas variables rastrean qué teclas están presionadas para calcular
# la animación de los brazos. No las modifiques directamente.
# =============================================================================

_avanzando  = False
_retrocediendo = False
_girando_izq = False
_girando_der = False

# =============================================================================
# UPDATE — se ejecuta cada fotograma
# =============================================================================

def update():
    global _avanzando, _retrocediendo, _girando_izq, _girando_der

    # ── Velocidades según modificadores ──────────────────────────────────────
    if held_keys['left control'] or held_keys['right control']:
        vel_mov = VELOCIDAD_CTRL
        vel_rot = ROTACION_CTRL
    elif held_keys['left shift'] or held_keys['right shift']:
        vel_mov = VELOCIDAD_SHIFT
        vel_rot = ROTACION_SHIFT
    else:
        vel_mov = VELOCIDAD_NORMAL
        vel_rot = ROTACION_NORMAL

    # ── Rotación del cuerpo ───────────────────────────────────────────────────
    _girando_izq = held_keys['a']
    _girando_der = held_keys['d']

    if _girando_izq:
        cuerpo.rotation_y -= vel_rot * time.dt
    if _girando_der:
        cuerpo.rotation_y += vel_rot * time.dt

    # ── Movimiento adelante/atrás ─────────────────────────────────────────────
    _avanzando     = held_keys['w']
    _retrocediendo = held_keys['s']

    if _avanzando:
        cuerpo.position += cuerpo.forward * vel_mov * time.dt
    if _retrocediendo:
        cuerpo.position -= cuerpo.forward * vel_mov * time.dt

    # ── FÍSICA DE BRAZOS ──────────────────────────────────────────────────────
    # Calculamos la rotación objetivo (target) para cada brazo según el estado.
    # Después usamos lerp para llegar suavemente a ese ángulo.
    #
    # Convención de ejes del brazo (local, relativo al cuerpo):
    #   rotation_x positivo = brazo rota hacia ADELANTE (en el eje del hombro)
    #   rotation_x negativo = brazo rota hacia ATRÁS
    #   rotation_z positivo = brazo se abre hacia afuera (izquierda o derecha)
    #
    # Los brazos hacen movimiento OPUESTO entre sí (como al caminar real):
    #   cuando der va atrás → izq va adelante

    target_rot_x_der = 0.0   # rotación X objetivo brazo derecho
    target_rot_x_izq = 0.0   # rotación X objetivo brazo izquierdo
    target_rot_z_der = 0.0   # rotación Z objetivo brazo derecho (apertura)
    target_rot_z_izq = 0.0

    if _avanzando:
        # Al caminar hacia adelante:
        # brazo derecho va hacia atrás → rotation_x negativo
        # brazo izquierdo va hacia adelante → rotation_x positivo
        target_rot_x_der = -ROTACION_CAMINAR
        target_rot_x_izq = ROTACION_CAMINAR

    elif _retrocediendo:
        # Al retroceder: movimiento opuesto
        target_rot_x_der = ROTACION_CAMINAR
        target_rot_x_izq = -ROTACION_CAMINAR

    if _girando_der:
        # Al girar derecha: brazos se abren levemente hacia los lados
        target_rot_z_der = ROTACION_GIRAR
        target_rot_z_izq = -ROTACION_GIRAR

    elif _girando_izq:
        target_rot_z_der = -ROTACION_GIRAR
        target_rot_z_izq = ROTACION_GIRAR

    # lerp: mueve el ángulo ACTUAL hacia el OBJETIVO suavemente cada frame
    factor = min(VELOCIDAD_LERP * time.dt, 1.0)

    brazo_der.rotation_x = lerp(brazo_der.rotation_x, target_rot_x_der, factor)
    brazo_izq.rotation_x = lerp(brazo_izq.rotation_x, target_rot_x_izq, factor)
    brazo_der.rotation_z = lerp(brazo_der.rotation_z, target_rot_z_der, factor)
    brazo_izq.rotation_z = lerp(brazo_izq.rotation_z, target_rot_z_izq, factor)

    # ── Cámaras ───────────────────────────────────────────────────────────────
    modo = modos_camara[indice_modo]

    if modo == "primera":
        editor_camera.enabled = False
        cuerpo.visible = False
        pos_ojos = cuerpo.position + Vec3(0, 0.5, 0) + (cuerpo.forward * 0.4)
        camera.position = pos_ojos
        camera.rotation = cuerpo.rotation
        camera.fov = fov_primera

    elif modo == "tercera":
        editor_camera.enabled = False
        cuerpo.visible = True
        objetivo = (cuerpo.position
                    - cuerpo.forward * distancia_tercera
                    + Vec3(0, 6, 0) * distancia_tercera / 6)
        camera.position = lerp(camera.position, objetivo, VELOCIDAD_NORMAL * time.dt)
        camera.look_at(cuerpo.position + Vec3(0, 1, 0))
        camera.fov = 90
        camera.rotation_z = 0

    elif modo == "aerea":
        editor_camera.enabled = False
        cuerpo.visible = True
        objetivo = cuerpo.position + Vec3(0, altura_aerea, -2)
        camera.position = lerp(camera.position, objetivo, VELOCIDAD_NORMAL * time.dt)
        camera.rotation_x = 80
        camera.rotation_y = 0
        camera.rotation_z = 0
    
    elif modo == 'libre':
        cuerpo.visible = True
        editor_camera.enabled = True


# =============================================================================
# INPUT — teclas especiales
# =============================================================================

def input(key):
    global indice_modo, distancia_tercera, fov_primera, altura_aerea

    if key == 'tab':
        indice_modo = (indice_modo + 1) % len(modos_camara)
        print(f"Cámara: {modos_camara[indice_modo]}")

    modo = modos_camara[indice_modo]

    if key == 'scroll up':
        if modo == 'tercera': distancia_tercera -= 1
        elif modo == 'primera': fov_primera -= 5
        elif modo == 'aerea': altura_aerea -= 2

    if key == 'scroll down':
        if modo == 'tercera': distancia_tercera += 1
        elif modo == 'primera': fov_primera += 5
        elif modo == 'aerea': altura_aerea += 2

    # Límites de cámara
    distancia_tercera = clamp(distancia_tercera, 3, 20)
    fov_primera = clamp(fov_primera, 30, 120)
    altura_aerea = clamp(altura_aerea, 8, 50)

    # Tecla de debug: muestra posición y rotación de brazos
    if key == 'p':
        print(f"Cuerpo pos:    {cuerpo.position}")
        print(f"Brazo der rot: x={brazo_der.rotation_x:.1f}  z={brazo_der.rotation_z:.1f}")
        print(f"Brazo izq rot: x={brazo_izq.rotation_x:.1f}  z={brazo_izq.rotation_z:.1f}")

# HUD de ayuda (se muestra en pantalla)

Text(
    text  = "WASD: mover   TAB: cámara   Scroll: zoom   P: debug",
    origin= (0, 0),
    scale = 0.8,
    position= (0, -0.45),
    color = color.rgba(200, 200, 200, 160),
)

app.run()