from ursina import *
import math

app = Ursina()

# --- ENTIDADES ---
robot = Entity(model='cube', color=color.blue, scale=1.5, y=0.75)
# Visor para saber donde es el frente
visor = Entity(parent=robot, model='cube', color=color.yellow, scale=(0.8, 0.3, 0.2), position=(0, 0.2, 0.55))

suelo = Entity(model='plane', scale=40, texture='brick', texture_scale=(20,20), color=color.gray, collider='box')

# --- VARIABLES DE CONFIGURACIÓN ---
velocidad_movimiento = 6
velocidad_rotacion = 100

# --- VARIABLES DE CÁMARA ---
modos_camara = ['tercera', 'primera', 'aerea'] # Lista de modos disponibles
indice_modo = 0 # Empezamos en el modo 0 (tercera)

# Configuración por defecto
distancia_tercera = 12
altura_aerea = 20
fov_primera = 90

def update():
    # --- 1. MOVIMIENTO DEL ROBOT (Lógica híbrida anterior) ---
    input_dir = Vec3(held_keys['d'] - held_keys['a'], 0, held_keys['w'] - held_keys['s']).normalized()
    
    if input_dir.length() > 0:
        # Rotación hacia donde caminamos
        angulo = math.degrees(math.atan2(input_dir.x, input_dir.z))
        robot.rotation_y = lerp(robot.rotation_y, angulo, 10 * time.dt)
        # Movimiento
        robot.position += input_dir * velocidad_movimiento * time.dt

    # --- 2. LÓGICA DE CÁMARA (MÁQUINA DE ESTADOS) ---
    modo_actual = modos_camara[indice_modo] # Obtenemos el nombre del modo actual (ej: 'tercera')

    if modo_actual == 'tercera':
        # --- MODO TERCERA PERSONA ---
        robot.visible = True # El robot se debe ver
        # Posición: Donde está el robot + Offset hacia atrás y arriba
        # Usamos la variable 'distancia_tercera' que podemos cambiar con el mouse
        offset = Vec3(0, 6, -distancia_tercera)
        camera.position = lerp(camera.position, robot.position + offset, 4 * time.dt)
        camera.look_at(robot.position)
        camera.fov = 90 # Fov estándar

    elif modo_actual == 'primera':
        # --- MODO PRIMERA PERSONA (FPS) ---
        robot.visible = False # OCULTAMOS el robot para no ver sus tripas
        
        # Posición: Exactamente donde está el robot + un poco arriba (ojos)
        # Usamos robot.forward para mover la camara un pelin adelante y no atravesar la textura
        posicion_ojos = robot.position + Vec3(0, 0.5, 0) + (robot.forward * 0.4)
        
        camera.position = posicion_ojos
        camera.rotation = robot.rotation # La cámara rota exactamente igual que el robot
        camera.fov = fov_primera # Aquí usamos el FOV variable

    elif modo_actual == 'aerea':
        # --- MODO VISTA AÉREA (TOP DOWN) ---
        robot.visible = True
        # Posición: Justo encima del robot, muy alto
        objetivo = robot.position + Vec3(0, altura_aerea, 0) # Altura variable
        camera.position = lerp(camera.position, objetivo, 2 * time.dt)
        # Rotación: Mirando picado hacia abajo (90 grados en X)
        camera.rotation_x = 90 
        camera.rotation_y = 0
        camera.rotation_z = 0


# --- FUNCIÓN INPUT (Manejo de Eventos) ---
def input(key):
    global indice_modo, distancia_tercera, fov_primera, altura_aerea
    
    # 1. CAMBIO DE CÁMARA (Tecla TAB)
    if key == 'tab':
        indice_modo += 1 # Pasamos al siguiente modo
        if indice_modo >= len(modos_camara): # Si llegamos al final de la lista...
            indice_modo = 0 # ...volvemos al principio (Bucle)
        
        print(f"Cambiado a modo: {modos_camara[indice_modo]}")

    # 2. RUEDA DEL MOUSE (Contextual: Hace cosas distintas según el modo)
    modo_actual = modos_camara[indice_modo]

    if key == 'scroll up': # Rueda hacia adelante
        if modo_actual == 'tercera':
            distancia_tercera -= 1 # Acercamos la cámara
        elif modo_actual == 'primera':
            fov_primera -= 5       # Zoom in (Efecto francotirador)
        elif modo_actual == 'aerea':
            altura_aerea -= 2      # Bajamos el dron

    if key == 'scroll down': # Rueda hacia atrás
        if modo_actual == 'tercera':
            distancia_tercera += 1 # Alejamos la cámara
        elif modo_actual == 'primera':
            fov_primera += 5       # Zoom out (Ojo de pez)
        elif modo_actual == 'aerea':
            altura_aerea += 2      # Subimos el dron

    # LIMITES (Para no romper la camara)
    distancia_tercera = clamp(distancia_tercera, 4, 20) # Mínimo 4, Máximo 20
    fov_primera = clamp(fov_primera, 30, 120)           # Mínimo 30, Máximo 120
    altura_aerea = clamp(altura_aerea, 10, 50)

app.run()