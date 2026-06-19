from ursina import *
import math # Necesario para los calculos de angulos

app = Ursina()

# --- 1. EL ROBOT (Ahora con indicador de frente) ---
robot = Entity( model='Jugador_particula.glb', scale=1, y=0.75,)

# Agregamos un "Visor" o "Sensor" en la cara frontal
# Al poner 'parent=robot', este objeto es parte del robot.
visor = Entity(
    parent=robot,           # Es parte del robot
    model='cube',
    color=color.yellow,     # Color diferente para que resalte
    scale=(0.8, 0.3, 0.2),  # Más ancho y plano
    position=(0, 0.2, 0.55) # Lo movemos hacia adelante (Z positivo) para que sobresalga
)

# --- 2. EL ENTORNO ---
# Usamos una textura de rejilla (grid) si es posible, o 'brick' con repetición
# para ver mejor el suelo moverse.
ground = Entity(model='plane', scale=30, texture='brick', texture_scale=(15,15), color=color.gray)

# --- 3. VARIABLES ---
velocidad_normal = 6
velocidad_ctrl = 9
velocidad_shift = 3

#grados por segundo
rotacion_normal = 100 
rotacion_ctrl = 125
rotacion_shift = 75

# perspectivas de camara
modos_camara = ["tercera", "primera", "aerea"]
indice_modo = 0 # empezar en tercera persona
# Configuración por defecto
distancia_tercera = 10
altura_aerea = 20
fov_primera = 90


def update():
    velocidad_movimiento = velocidad_normal
    velocidad_camara = velocidad_normal
    velocidad_rotacion = rotacion_normal # Grados por segundo
    
    if held_keys['left control'] or held_keys['right control']:
        velocidad_movimiento = velocidad_ctrl
        velocidad_rotacion = rotacion_ctrl
    elif held_keys['left shift'] or held_keys['right shift']:
        velocidad_movimiento = velocidad_shift
        velocidad_rotacion = rotacion_shift
    else:
        velocidad_movimiento = velocidad_normal
        velocidad_rotacion = rotacion_normal
    
    # 1. ROTACIÓN (Izquierda / Derecha)
    # En lugar de movernos en X, ahora A y D giran el cuerpo del robot.
    if held_keys['a']:
        robot.rotation_y -= velocidad_rotacion * time.dt
    if held_keys['d']:
        robot.rotation_y += velocidad_rotacion * time.dt

    # 2. MOVIMIENTO (Adelante / Atrás)
    # Aquí está el secreto: Usamos robot.forward
    # robot.forward es una flecha que SIEMPRE apunta hacia donde está la "nariz" amarilla.
    
    if held_keys['w']:
        # Sumamos a la posición actual el vector del frente
        robot.position += robot.forward * velocidad_movimiento * time.dt
        
    if held_keys['s']:
        # Restamos el vector del frente (ir hacia atrás)
        robot.position -= robot.forward * velocidad_movimiento * time.dt
    
    modo_actual = modos_camara[indice_modo]
    
    if modo_actual == "primera":
        # --- MODO PRIMERA PERSONA ---
        robot.visible = False # Ocultamos el robot para no ver sus tripas
        posicion_ojos = robot.position + Vec3(0, 0.5, 0) + (robot.forward * 0.4)
        camera.position = posicion_ojos
        camera.rotation = robot.rotation
        camera.fov = 110
    
    elif modo_actual == "tercera":
        # --- MODO TERCERA PERSONA ---
        robot.visible = True # El robot se debe ver
        # Posición: Donde está el robot + Offset hacia atrás y arriba
        # Usamos la variable 'distancia_tercera' que podemos cambiar con el mouse
        posicion_camara_objetivo = robot.position - (robot.forward * distancia_tercera) + (Vec3(0, 6, 0)* distancia_tercera/6)
        camera.position = lerp(camera.position, posicion_camara_objetivo, velocidad_camara * time.dt)
        camera.look_at(robot.position + Vec3(0, 1, 0))
        camera.fov = 90 # Fov estándar
        camera.rotation_z = 0
    
    elif modo_actual == 'aerea':
        # --- MODO VISTA AÉREA (TOP DOWN) ---
        robot.visible = True
        # Posición: Justo encima del robot, muy alto
        objetivo = robot.position + Vec3(0, altura_aerea, -2) # Altura variable
        camera.position = lerp(camera.position, objetivo, velocidad_camara * time.dt)
        # Rotación: Mirando picado hacia abajo (90 grados en X)
        camera.rotation_x = 80 
        camera.rotation_y = 0
        camera.rotation_z = 0

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
