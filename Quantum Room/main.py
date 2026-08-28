from panda3d.core import loadPrcFileData
loadPrcFileData('', 'load-display p3tinydisplay')
from panda3d.core import TransparencyAttrib, Vec4

from ursina import *
from ursina.prefabs.editor_camera import EditorCamera
from ursina.shaders import lit_with_shadows_shader

import math
import random

from scripts.clases import ObjetoFisico, FuncionOndaCuantica
from scripts.salas_niveles import MapaNivel1

app = Ursina(title = 'Quantum Room', borderless = False, fullscreen = True) # Fullscreen falso temporal para pruebas

# --- VARIABLES ---
velocidad_normal = 6
indice_vel_ctrl = 1.5
indice_vel_shift = 0.5
velocidad_actual = velocidad_normal

rotacion_normal = 100 
indice_rot_ctrl = 1.25
indice_rot_shift = 0.75
rotacion_actual = rotacion_normal

modos_camara = ["tercera", "primera", "aerea", "libre"]
indice_modo = 0 
distancia_tercera = 10
altura_aerea = 20
fov_primera = 90
editor_camera = EditorCamera(enabled=False)

modelo_cuerpo = "assets/models/player/Jugador_particula_body"
modelo_brazo_izq = "assets/models/player/Jugador_particula_arm_right"
modelo_brazo_der = "assets/models/player/Jugador_particula_arm_left"

spawn = Vec3(0, 10, 0)

rot_brazo_caminar_normal = 35
rot_brazo_girar_normal = 15
velocidad_lerp_brazos = 8.0
rotacion_brazo_caminar_actual = rot_brazo_caminar_normal
rotacion_brazo_girar_actual = rot_brazo_girar_normal

# --- ENTIDADES FÍSICAS ---

cuerpo_robot = ObjetoFisico(
    altura_pies = 1,
    model = modelo_cuerpo,
    scale = (0.7,0.7,0.7),
    position = spawn,
    collider = 'box',
    shader = lit_with_shadows_shader,
    masa = 70.0,
    color=color.rgb(0.3,0.3,0.3) 
)
cuerpo_robot.setTransparency(TransparencyAttrib.MNone, 1)
cuerpo_robot.setDepthWrite(True)
cuerpo_robot.setDepthTest(True)

brazo_izq = Entity(
    model = modelo_brazo_izq,
    scale = (0.85,0.85,0.85),
    position = Vec3(0.2,  0.15,  0.0), 
    parent = cuerpo_robot,
    collider = 'box',
    shader = lit_with_shadows_shader,
    color=color.rgb(0.3,0.3,0.3) 
)
brazo_izq.setTransparency(TransparencyAttrib.MNone, 1)
brazo_izq.setDepthWrite(True)
brazo_izq.setDepthTest(True)

brazo_der = Entity(
    model = modelo_brazo_der,
    scale = (0.85,0.85,0.85),
    position = Vec3( -0.2,  0.15,  0.0),
    parent = cuerpo_robot,
    collider = 'box',
    shader = lit_with_shadows_shader,
    color=color.rgb(0.3,0.3,0.3) 
)
brazo_der.setTransparency(TransparencyAttrib.MNone, 1)
brazo_der.setDepthWrite(True)
brazo_der.setDepthTest(True)

# --- CONSTRUCCIÓN DEL MAPA ---
sala1 = MapaNivel1(modo_edicion=False)  

arcade = Entity(
    model='assets/models/decoracion/arcade', # Tu modelo 3D
    position=(-21, 0, -24.8),             # Coordenadas en la sala                    
    rotation_y = -90,               # Rotación para que mire al jugador
    scale=2,                          # Ajusta si el modelo es muy grande/chico
    collider='box',                   # Vital para que el jugador choque contra él
    color=color.rgb(0.07, 0.07, 0.07),
                       # O usa el shader que estés usando para el mapa
    shader = lit_with_shadows_shader
)
arcade.setTransparency(TransparencyAttrib.MNone, 1)
arcade.setDepthWrite(True)
arcade.setDepthTest(True)

silla_gamer = ObjetoFisico(
    model='assets/models/decoracion/silla_gamer', # Tu modelo 3D
    position=(-0.6, 4, -0.4),             # Coordenadas en la sala                    
    rotation_y = -126,               # Rotación para que mire al jugador
    scale=2,                          # Ajusta si el modelo es muy grande/chico
    collider='box',                   # Vital para que el jugador choque contra ésl
    color=color.rgb(5, 5, 5),
                       # O usa el shader que estés usando para el mapa
    shader = lit_with_shadows_shader,
    altura_pies = 1,
    masa = 5,
    entidades_ignoradas=[cuerpo_robot]
)

silla_gamer.setTransparency(TransparencyAttrib.MNone, 1)
silla_gamer.setDepthWrite(True)
silla_gamer.setDepthTest(True)

onda = FuncionOndaCuantica(cuerpo_robot, brazo_izq, brazo_der)

AmbientLight(color=color.rgb(10, 10, 10))
sun = DirectionalLight(shadows=True, color=color.rgb(15, 15, 15))
sun.look_at(Vec3(-1,-1,-1))

tiempo_juego = 0

def update():
    global velocidad_actual, rotacion_actual, tiempo_juego, onda
    tiempo_juego += time.dt

    velocidad_camara = velocidad_actual
    
    if held_keys['left control'] or held_keys['right control']:
        velocidad_actual = velocidad_normal * indice_vel_ctrl
        rotacion_actual = rotacion_normal * indice_rot_ctrl
        rotacion_brazo_caminar_actual = rot_brazo_caminar_normal * indice_rot_ctrl
        rotacion_brazo_girar_actual = rot_brazo_girar_normal * indice_rot_ctrl
    elif held_keys['left shift'] or held_keys['right shift']:
        velocidad_actual = velocidad_normal * indice_vel_shift
        rotacion_actual = rotacion_normal * indice_rot_shift
        rotacion_brazo_caminar_actual = rot_brazo_caminar_normal * indice_rot_shift
        rotacion_brazo_girar_actual = rot_brazo_girar_normal * indice_rot_shift
    else:
        velocidad_actual = velocidad_normal
        rotacion_actual = rotacion_normal
        rotacion_brazo_caminar_actual = rot_brazo_caminar_normal
        rotacion_brazo_girar_actual = rot_brazo_girar_normal
    
    target_rot_x_der = 0.0   
    target_rot_x_izq = 0.0   
    target_rot_z_der = 0.0   
    target_rot_z_izq = 0.0   
    
    if held_keys['a']:
        cuerpo_robot.rotation_y -= rotacion_actual * time.dt
        target_rot_z_der = rotacion_brazo_girar_actual 
        target_rot_z_izq = rotacion_brazo_girar_actual
        
    if held_keys['d']:
        cuerpo_robot.rotation_y += rotacion_actual * time.dt
        target_rot_z_der = -rotacion_brazo_girar_actual
        target_rot_z_izq = -rotacion_brazo_girar_actual

    if held_keys['w']:
        direccion = cuerpo_robot.forward
        paso = velocidad_actual * time.dt
        
        colision_frente = raycast(cuerpo_robot.position + Vec3(0, 1, 0), direccion, distance=paso + 0.9, ignore=(cuerpo_robot, onda.nucleo))
        
        if not colision_frente.hit: 
            cuerpo_robot.position += direccion * paso
            
        elif hasattr(colision_frente.entity, 'masa') and colision_frente.entity.masa <= cuerpo_robot.masa:
            # Lista de cosas que el mueble debe ignorar al avanzar (él mismo, el jugador y el núcleo de onda)
            ignorar_empuje = (colision_frente.entity, cuerpo_robot, onda.nucleo)
            
            # Pedimos al objeto que intente moverse. Si retorna True, entonces avanzamos con él.
            if colision_frente.entity.ser_empujado(direccion, paso, ignorar_empuje):
                cuerpo_robot.position += direccion * paso
            
        target_rot_x_der = rotacion_brazo_caminar_actual
        target_rot_x_izq = rotacion_brazo_caminar_actual
        
    if held_keys['s']:
        direccion = -cuerpo_robot.forward
        paso = velocidad_actual * time.dt
        
        colision_atras = raycast(cuerpo_robot.position + Vec3(0, 1, 0), direccion, distance=paso + 0.9, ignore=(cuerpo_robot, onda.nucleo))
        
        if not colision_atras.hit: 
            cuerpo_robot.position += direccion * paso
            
        elif hasattr(colision_atras.entity, 'masa') and colision_atras.entity.masa <= cuerpo_robot.masa:
            ignorar_empuje = (colision_atras.entity, cuerpo_robot, onda.nucleo)
            
            if colision_atras.entity.ser_empujado(direccion, paso, ignorar_empuje):
                cuerpo_robot.position += direccion * paso
            
        target_rot_x_der = -rotacion_brazo_caminar_actual
        target_rot_x_izq = -rotacion_brazo_caminar_actual
        
    if held_keys['e']:
        onda.activar()
    
    if held_keys['f']:
        onda.desactivar()
        
    factor = min(velocidad_lerp_brazos * time.dt, 1.0)

    brazo_der.rotation_x = lerp(brazo_der.rotation_x, target_rot_x_der, factor)
    brazo_izq.rotation_x = lerp(brazo_izq.rotation_x, target_rot_x_izq, factor)
    brazo_der.rotation_z = lerp(brazo_der.rotation_z, target_rot_z_der, factor)
    brazo_izq.rotation_z = lerp(brazo_izq.rotation_z, target_rot_z_izq, factor)
    
    onda.actualizar(time.dt)
        
    modo_actual = modos_camara[indice_modo]
    
    if modo_actual == "primera":
        editor_camera.enabled = False
        cuerpo_robot.visible = False 
        posicion_ojos = cuerpo_robot.position + Vec3(0, 0.5, 0) + (cuerpo_robot.forward * 0.4)
        camera.position = posicion_ojos
        camera.rotation = cuerpo_robot.rotation
        camera.fov = 110
    
    elif modo_actual == "tercera":
        editor_camera.enabled = False
        cuerpo_robot.visible = not onda.activo
        posicion_camara_objetivo = cuerpo_robot.position - (cuerpo_robot.forward * distancia_tercera) + (Vec3(0, 6, 0)* distancia_tercera/6)
        camera.position = lerp(camera.position, posicion_camara_objetivo, velocidad_camara * time.dt)
        camera.look_at(cuerpo_robot.position + Vec3(0, 1, 0))
        camera.fov = 90 
        camera.rotation_z = 0
    
    elif modo_actual == 'aerea':
        editor_camera.enabled = False
        cuerpo_robot.visible = not onda.activo
        objetivo = cuerpo_robot.position + Vec3(0, altura_aerea, -2) 
        camera.position = lerp(camera.position, objetivo, velocidad_camara * time.dt)
        camera.rotation_x = 80 
        camera.rotation_y = 0
        camera.rotation_z = 0
        
    elif modo_actual == 'libre':
        editor_camera.enabled = True
        cuerpo_robot.visible = not onda.activo
        
    print(cuerpo_robot.position)

def input(key):
    global indice_modo, distancia_tercera, fov_primera, altura_aerea, onda
    
    if key == 'space': # Salto añadido a la tecla espacio
        cuerpo_robot.saltar()

    if key == 'tab':
        indice_modo += 1 
        if indice_modo >= len(modos_camara): 
            indice_modo = 0 
        
        print(f"Cambiado a modo: {modos_camara[indice_modo]}")

    modo_actual = modos_camara[indice_modo]

    if key == 'scroll up': 
        if modo_actual == 'tercera':
            distancia_tercera -= 1 
        elif modo_actual == 'primera':
            fov_primera -= 5       
        elif modo_actual == 'aerea':
            altura_aerea -= 2      

    if key == 'scroll down': 
        if modo_actual == 'tercera':
            distancia_tercera += 1 
        elif modo_actual == 'primera':
            fov_primera += 5       
        elif modo_actual == 'aerea':
            altura_aerea += 2      

    distancia_tercera = clamp(distancia_tercera, 4, 20) 
    fov_primera = clamp(fov_primera, 30, 120)           
    altura_aerea = clamp(altura_aerea, 10, 50)

app.run()