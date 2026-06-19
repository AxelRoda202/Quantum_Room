from panda3d.core import loadPrcFileData
# Fuerza a Panda3D a usar el renderizador por software (ignora la GPU)
loadPrcFileData('', 'load-display p3tinydisplay')
from ursina.shaders import basic_lighting_shader
from ursina import *
from ursina.prefabs.editor_camera import EditorCamera
from panda3d.core import TransparencyAttrib
from ursina.shader import Shader
from ursina.shaders import lit_with_shadows_shader
import math
import random

# =============================================================================
# CLASE: FUNCIÓN DE ONDA (NIEBLA CUÁNTICA)
# =============================================================================

class FuncionOndaCuantica:
    def __init__(self, origen_entity, brazo_i, brazo_d):
        self.origen = origen_entity
        self.brazos = [brazo_i, brazo_d]
        self.particulas = []
        self.activo = False
        self.tiempo_expansion = 0.0
        
        # Configuraciones
        self.radio_maximo = 10.0
        self.cantidad_particulas = 100 # Menos entidades, pero más grandes y volumétricas
        self.velocidad_expansion = 12.0
        
        # El NÚCLEO CUÁNTICO (Esfera central)
        self.nucleo = Entity(
            model='sphere',
            color=color.magenta,
            scale=0.8,
            enabled=False # Apagado por defecto
        )
        self.nucleo.setTransparency(TransparencyAttrib.MAlpha, 1)

    def activar(self):
        if self.activo: return # Seguro para no generar entidades infinitas si dejas apretada la tecla
        
        self.activo = True
        self.tiempo_expansion = 0.0
        
        # 1. DESAPARECER ROBOT Y ENCENDER NÚCLEO
        self.origen.visible = False
        for b in self.brazos: b.visible = False
        
        self.nucleo.enabled = True
        self.nucleo.position = self.origen.position + Vec3(0, 0.5, 0)
        
        # 2. GENERAR NUBE DE PROBABILIDAD (CUBOS)
        for i in range(self.cantidad_particulas):
            angulo = random.uniform(0, 360) # Distribución en todos los ángulos
            
            dir_x = math.cos(math.radians(angulo))
            dir_z = math.sin(math.radians(angulo))
            direccion = Vec3(dir_x, 0, dir_z)
            
            cubo = Entity(
                model='cube',
                position=self.nucleo.position,
                scale=1
            )
            cubo.setTransparency(TransparencyAttrib.MAlpha, 1)
            cubo.setDepthWrite(False)
            
            # Cada cubo viaja a una velocidad ligeramente distinta para dar efecto de "nube"
            velocidad_propia = self.velocidad_expansion * random.uniform(0.6, 1.2)
            
            self.particulas.append({
                'entidad': cubo,
                'direccion': direccion,
                'distancia_actual': 0.0,
                'velocidad': velocidad_propia,
                'fase': random.uniform(0, math.pi * 2),
                'choco_pared': False # ¡El flag de optimización!
            })

    def desactivar(self):
        if not self.activo: return
        self.activo = False
        
        # 1. DESTRUIR CUBOS
        for p in self.particulas:
            destroy(p['entidad'])
        self.particulas.clear()
        
        # 2. APAGAR NÚCLEO Y REAPARECER ROBOT
        self.nucleo.enabled = False
        self.origen.visible = True
        for b in self.brazos: b.visible = True

    def actualizar(self, dt):
        if not self.activo: return
        self.tiempo_expansion += dt
        
        # El núcleo palpita rítmicamente
        self.nucleo.scale = 0.8 + (math.sin(self.tiempo_expansion * 8) * 0.15)
        self.nucleo.position = self.origen.position + Vec3(0, 0.5, 0)
        
        for p in self.particulas:
            entidad = p['entidad']
            
            # --- OPTIMIZACIÓN DE RAYCAST ---
            # Solo calculamos choques si el cubo aún no ha tocado una pared
            if not p['choco_pared']:
                distancia_objetivo = self.tiempo_expansion * p['velocidad']
                distancia_objetivo = min(distancia_objetivo, self.radio_maximo)
                
                rayo = raycast(self.nucleo.position, p['direccion'], distance=distancia_objetivo, ignore=(self.origen, self.nucleo))
                
                if rayo.hit:
                    p['distancia_actual'] = rayo.distance
                    p['choco_pared'] = True # Apaga el raycast para este cubo el resto del tiempo
                else:
                    p['distancia_actual'] = distancia_objetivo
            
            # Mover el cubo
            entidad.position = self.nucleo.position + (p['direccion'] * p['distancia_actual'])
            
            # --- CÁLCULO DE PROBABILIDAD VISUAL ---
            # Probabilidad de 1.0 (centro) a 0.0 (borde máximo)
            probabilidad = 1.0 - (p['distancia_actual'] / self.radio_maximo)
            probabilidad = clamp(probabilidad, 0.01, 1.0)
            
            fluctuacion = math.sin(self.tiempo_expansion * 5.0 + p['fase'])
            
            # COLOR: Violeta claro en el centro (probabilidad alta), oscuro en el borde
            rojo = int(100 + (100 * probabilidad))
            azul = 255
            # TRANSPARENCIA: Alta en el centro, casi invisible en los bordes
            alfa = int(220 * probabilidad + (fluctuacion * 30))
            alfa = clamp(alfa, 0, 255)
            
            entidad.color = color.rgba(rojo, 0, azul, alfa)
            
            # ESCALA: Cubos más grandes en el centro, se encogen al perder probabilidad
            entidad.scale = 0.4 + (probabilidad * 1.0) + (fluctuacion * 0.2)
            
            # Le damos una ligera rotación 3D para que no parezcan estáticos
            entidad.rotation_y += dt * 40
            entidad.rotation_x += dt * 20

app = Ursina()

app = Ursina(
    title = 'Quantum Room',
    borderless = False,
    fullscreen =  True
)

# --- VARIABLES ---
velocidad_normal = 6
indice_vel_ctrl = 1.5
indice_vel_shift = 0.5
velocidad_actual = velocidad_normal

#grados por segundo
rotacion_normal = 100 
indice_rot_ctrl = 1.25
indice_rot_shift = 0.75
rotacion_actual = rotacion_normal

# perspectivas de camara
modos_camara = ["tercera", "primera", "aerea", "libre"]
indice_modo = 0 # empezar en tercera persona
# Configuración por defecto
distancia_tercera = 10
altura_aerea = 20
fov_primera = 90
editor_camera = EditorCamera(
    enabled=False
)

# --- direcciones de modelos ---
modelo_cuerpo = "assets/models/player/Jugador_particula_body"
modelo_brazo_izq = "assets/models/player/Jugador_particula_arm_right"
modelo_brazo_der = "assets/models/player/Jugador_particula_arm_left"
modelo_sala_principal = ""
modelo_sala_ET = ""
modelo_sala_OP = ""

spawn = Vec3(0, 1.2, 0)

# --- variables fisicas de brazos ---
rot_brazo_caminar_normal = 35
rot_brazo_girar_normal = 15
velocidad_lerp_brazos = 8.0
rotacion_brazo_caminar_actual = rot_brazo_caminar_normal
rotacion_brazo_girar_actual = rot_brazo_girar_normal

# --- ENTIDADES ---
cuerpo_robot = Entity(
    model = modelo_cuerpo,
    scale = (1,1,1),
    position = spawn,
    collider = 'box',
    shader = lit_with_shadows_shader
)
#transparencia cuerpo
cuerpo_robot.setTransparency(TransparencyAttrib.MNone, 1)
cuerpo_robot.setDepthWrite(True)
cuerpo_robot.setDepthTest(True)

brazo_izq = Entity(
    model = modelo_brazo_izq,
    scale = (1,1,1),
    position = Vec3(0.05,  0.15,  0.0), #(x)
    parent = cuerpo_robot,
    collider = 'box',
    shader = lit_with_shadows_shader
)
#transparencia brazo izquierdo
brazo_izq.setTransparency(TransparencyAttrib.MNone, 1)
brazo_izq.setDepthWrite(True)
brazo_izq.setDepthTest(True)

brazo_der = Entity(
    model = modelo_brazo_der,
    scale = (1,1,1),
    position = Vec3( -0.05,  0.15,  0.0),
    parent = cuerpo_robot,
    collider = 'box',
    shader = lit_with_shadows_shader
)
#transparencia brazo derecho
brazo_der.setTransparency(TransparencyAttrib.MNone, 1)
brazo_der.setDepthWrite(True)
brazo_der.setDepthTest(True)

onda = FuncionOndaCuantica(cuerpo_robot, brazo_izq, brazo_der)

AmbientLight(color=color.rgb(10, 10, 20))
sun = DirectionalLight(
    shadows=False,
    color=color.rgb(100, 100, 100))
sun.look_at(Vec3(-1,-1,-1))

ground = Entity(model='plane', scale=30, texture='brick', texture_scale=(15,15), color=color.gray)

# --- Variables de fisicas ---
tiempo_juego = 0
inercia_brazos = Vec3(0,0,0)
posicion_anterior_cuerpo = Vec3(0,0,0)

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
    
    #Fisicas de los Brazos
    target_rot_x_der = 0.0   # rotación X objetivo brazo derecho
    target_rot_x_izq = 0.0   # rotación X objetivo brazo izquierdo
    target_rot_z_der = 0.0   # rotación Z objetivo brazo derecho (apertura)
    target_rot_z_izq = 0.0   # rotación Z objetivo brazo izquierdo (apertura)
    
    # 1. ROTACIÓN (Izquierda / Derecha)
    if held_keys['a']:
        cuerpo_robot.rotation_y -= rotacion_actual * time.dt
        target_rot_z_der = rotacion_brazo_girar_actual 
        target_rot_z_izq = rotacion_brazo_girar_actual
        
    if held_keys['d']:
        cuerpo_robot.rotation_y += rotacion_actual * time.dt
        target_rot_z_der = -rotacion_brazo_girar_actual
        target_rot_z_izq = -rotacion_brazo_girar_actual

    # 2. MOVIMIENTO (Adelante / Atrás)
    
    if held_keys['w']:
        # Sumamos a la posición actual el vector del frente
        cuerpo_robot.position += cuerpo_robot.forward * velocidad_actual * time.dt
        target_rot_x_der = rotacion_brazo_caminar_actual
        target_rot_x_izq = rotacion_brazo_caminar_actual
        
    if held_keys['s']:
        # Restamos el vector del frente (ir hacia atrás)
        cuerpo_robot.position -= cuerpo_robot.forward * velocidad_actual * time.dt
        target_rot_x_der = -rotacion_brazo_caminar_actual
        target_rot_x_izq = -rotacion_brazo_caminar_actual
        
    if held_keys['e']:
        onda.activar()
    
    if held_keys['f']:
        onda.desactivar()
        
    # lerp: mueve el ángulo ACTUAL hacia el OBJETIVO suavemente cada frame
    factor = min(velocidad_lerp_brazos * time.dt, 1.0)

    brazo_der.rotation_x = lerp(brazo_der.rotation_x, target_rot_x_der, factor)
    brazo_izq.rotation_x = lerp(brazo_izq.rotation_x, target_rot_x_izq, factor)
    brazo_der.rotation_z = lerp(brazo_der.rotation_z, target_rot_z_der, factor)
    brazo_izq.rotation_z = lerp(brazo_izq.rotation_z, target_rot_z_izq, factor)
    
    # --- modo onda ---
    onda.actualizar(time.dt)
        
    modo_actual = modos_camara[indice_modo]
    
    if modo_actual == "primera":
        # --- MODO PRIMERA PERSONA ---
        editor_camera.enabled = False
        cuerpo_robot.visible = False # Ocultamos el robot para no ver sus tripas
        posicion_ojos = cuerpo_robot.position + Vec3(0, 0.5, 0) + (cuerpo_robot.forward * 0.4)
        camera.position = posicion_ojos
        camera.rotation = cuerpo_robot.rotation
        camera.fov = 110
    
    elif modo_actual == "tercera":
        # --- MODO TERCERA PERSONA ---
        editor_camera.enabled = False
        cuerpo_robot.visible = True # El robot se debe ver
        # Posición: Donde está el robot + Offset hacia atrás y arriba
        # Usamos la variable 'distancia_tercera' que podemos cambiar con el mouse
        posicion_camara_objetivo = cuerpo_robot.position - (cuerpo_robot.forward * distancia_tercera) + (Vec3(0, 6, 0)* distancia_tercera/6)
        camera.position = lerp(camera.position, posicion_camara_objetivo, velocidad_camara * time.dt)
        camera.look_at(cuerpo_robot.position + Vec3(0, 1, 0))
        camera.fov = 90 # Fov estándar
        camera.rotation_z = 0
    
    elif modo_actual == 'aerea':
        # --- MODO VISTA AÉREA (TOP DOWN) ---
        editor_camera.enabled = False
        cuerpo_robot.visible = True
        # Posición: Justo encima del robot, muy alto
        objetivo = cuerpo_robot.position + Vec3(0, altura_aerea, -2) # Altura variable
        camera.position = lerp(camera.position, objetivo, velocidad_camara * time.dt)
        # Rotación: Mirando picado hacia abajo (90 grados en X)
        camera.rotation_x = 80 
        camera.rotation_y = 0
        camera.rotation_z = 0
        
    elif modo_actual == 'libre':
        editor_camera.enabled = True
        cuerpo_robot.visible = True

def input(key):
    global indice_modo, distancia_tercera, fov_primera, altura_aerea, onda
    
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