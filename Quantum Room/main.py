from panda3d.core import loadPrcFileData
# Fuerza a Panda3D a usar el renderizador por software (ignora la GPU)
loadPrcFileData('', 'load-display p3tinydisplay')
from ursina.shaders import basic_lighting_shader
from ursina import *
from ursina.prefabs.editor_camera import EditorCamera
from panda3d.core import TransparencyAttrib, Vec4
from ursina.shaders import lit_with_shadows_shader
import math
import random

# --- SISTEMA DE FÍSICAS Y GRAVEDAD ---
class ObjetoFisico(Entity):
    def __init__(self, altura_pies, **kwargs):
        super().__init__(**kwargs)
        self.gravedad = -20.0 
        self.velocidad_y = 0.0
        self.en_el_suelo = False
        self.masa = kwargs.get('masa', 1.0) 
        
        # fuerza de salto, mientras mas alto mas fuerte
        self.fuerza_salto = 10.0 
        
        # --- ALTURA DE LOS PIES ---
        # Distancia exacta desde el centro geométrico de tu modelo 3D hasta su base.
        self.altura_pies = altura_pies 

    def update(self):
        # La gravedad afecta constantemente a la velocidad
        self.velocidad_y += self.gravedad * time.dt
            
        # Calculamos cuánto nos vamos a mover en este frame
        movimiento_y = self.velocidad_y * time.dt
        nueva_y = self.y + movimiento_y

        # Lanzamos el rayo desde el centro del objeto hacia abajo.
        # La distancia que mira es: la altura a los pies + el movimiento de este frame + 0.1 de margen.
        distancia_rayo = self.altura_pies + abs(movimiento_y) + 0.1 
        
        rayo_suelo = raycast(self.position, Vec3(0, -1, 0), distance=distancia_rayo, ignore=(self,))

        if rayo_suelo.hit and self.velocidad_y <= 0:
            self.velocidad_y = 0
            self.en_el_suelo = True
            self.y = rayo_suelo.world_point.y + self.altura_pies
            
        else:
            self.en_el_suelo = False
            self.y = nueva_y

    def saltar(self):
        if self.en_el_suelo:
            self.velocidad_y = self.fuerza_salto
            self.en_el_suelo = False

# --- HITBOXES MANUALES ---
def crear_hitbox(posicion, escala, permeable=0.0, visible=False):
    hitbox = Entity(
        model='cube',
        position=posicion,
        scale=escala,
        collider='box',
        visible=visible # Cambia a True cuando estés construyendo el nivel para verlas
    )
    # 0.0 = Sólido total (Paredes)
    # 0.5 = Semi-permeable (Puertas láser en el futuro)
    # 1.0 = Permeabilidad total (Puertas cuánticas/naranjas)
    hitbox.permeabilidad_cuantica = permeable 
    return hitbox

# --- FUNCIÓN DE ONDA (NIEBLA CUÁNTICA) ---
class FuncionOndaCuantica:
    def __init__(self, origen_entity, brazo_i, brazo_d):
        self.origen = origen_entity
        self.brazos = [brazo_i, brazo_d]
        self.particulas = []
        self.activo = False
        self.tiempo_expansion = 0.0
        
        self.radio_minimo = 3.0  
        self.radio_maximo = 12.0 
        self.distancia_entre_anillos = 1.8 
        self.distancia_entre_cubos = 1.8   
        
        self.altura_min = 0.01
        self.altura_max = 2.0
        self.velocidad_onda = 0.01
        
        # --- EL NÚCLEO Y SU BRÚJULA VISUAL ---
        self.nucleo = Entity(model='sphere', color=color.magenta, scale=1.5, enabled=False, unlit=True)
        self.nucleo.setTransparency(TransparencyAttrib.MAlpha, 1)
        
        # Este es el VISOR. Es un pequeño cubo alargado atado al núcleo
        self.visor_orientacion = Entity(
            parent=self.nucleo,
            model='sphere',
            color=color.cyan, # Color distinto para que resalte
            scale=(0.6, 0.6, 0.3), # Alargado en el eje Z (frente)
            position=(0, 0, 0.4),  # Desplazado ligeramente hacia adelante del núcleo
            unlit=True
        )

    def activar(self):
        if self.activo: return
        self.activo = True
        self.tiempo_expansion = 0.0
        
        self.origen.visible = False
        for b in self.brazos: b.visible = False
        self.nucleo.enabled = True
        self.nucleo.position = self.origen.position + Vec3(0, 0.5, 0)
        
        radio_actual = self.radio_minimo
        while radio_actual <= self.radio_maximo:
            circunferencia = 2 * math.pi * radio_actual
            num_cubos = int(circunferencia / self.distancia_entre_cubos)
            
            for i in range(num_cubos):
                angulo = (i / num_cubos) * (math.pi * 2)
                offset_x = math.cos(angulo) * radio_actual
                offset_z = math.sin(angulo) * radio_actual
                
                cubo = Entity(model='cube', scale=Vec3(2, 0.1, 2), unlit=True, enabled=True)
                cubo.setTransparency(TransparencyAttrib.MAlpha, 1)
                cubo.setDepthWrite(False)
                
                self.particulas.append({
                    'entidad': cubo,
                    'distancia_centro': radio_actual,
                    'offset': Vec3(offset_x, 0, offset_z)
                })
            radio_actual += self.distancia_entre_anillos

    def desactivar(self):
        if not self.activo: return
        self.activo = False
        for p in self.particulas: destroy(p['entidad'])
        self.particulas.clear()
        
        self.nucleo.enabled = False
        self.origen.visible = True
        for b in self.brazos: b.visible = True

    def actualizar(self, dt):
        if not self.activo: return
        self.tiempo_expansion += dt
        
        self.nucleo.scale = 0.8 + (math.sin(self.tiempo_expansion * 8) * 0.15)
        self.nucleo.position = self.origen.position + Vec3(0, 0.5, 0)
        
        # el núcleo copie la rotación exacta del jugador
        self.nucleo.rotation = self.origen.rotation
        
        # El rayo solo ignora al jugador y al núcleo para no chocar apenas sale
        objetos_a_ignorar_basicos = (self.origen, self.nucleo)
        
        for p in self.particulas:
            entidad = p['entidad']
            dist = p['distancia_centro']
            ox = p['offset'].x
            oz = p['offset'].z
            
            pos_objetivo_x = self.nucleo.x + ox
            pos_objetivo_z = self.nucleo.z + oz
            direccion_rayo = Vec3(ox, 0, oz)
            
            # --- NUEVA LÓGICA DE PERMEABILIDAD ---
            # Lanzamos el rayo
            rayo = raycast(self.nucleo.position, direccion_rayo.normalized(), distance=dist, ignore=objetos_a_ignorar_basicos)
            
            if rayo.hit:
                # Verificamos si el objeto impactado tiene la variable de permeabilidad
                # Si no la tiene (por defecto), asumimos que es una pared sólida (0)
                permeabilidad = getattr(rayo.entity, 'permeabilidad_cuantica', 0.0)
                
                if permeabilidad < 0.5: # Si es sólida (0), ocultamos el cubo
                    entidad.enabled = False
                    continue
                else: 
                    # Si la permeabilidad es alta (1.0 - Puerta naranja), el cubo SÍ se dibuja
                    # Aquí podrías en el futuro hacer que el cubo cambie de color según la permeabilidad
                    entidad.enabled = True
            else:
                entidad.enabled = True
            
            # Reposicionamos
            entidad.x = pos_objetivo_x
            entidad.z = pos_objetivo_z
            
            # Animación visual
            onda_base = math.sin(dist * 1.5 - self.tiempo_expansion * self.velocidad_onda)
            onda_x = math.cos(ox * 0.8 + self.tiempo_expansion * 2.0)
            onda_z = math.sin(oz * 0.8 - self.tiempo_expansion * 3.0)
            probabilidad = clamp((onda_base + onda_x + onda_z + 3.0) / 6.0, 0.0, 1.0)
            
            nueva_altura = lerp(self.altura_min, self.altura_max, probabilidad)
            entidad.scale_y = nueva_altura
            entidad.y = 0.05 + (nueva_altura / 2)
            
            a = lerp(0.05, 0.9, probabilidad)
            entidad.color = Vec4(90/255, 0, 1, a)

app = Ursina(title = 'Quantum Room', borderless = False, fullscreen = False) # Fullscreen falso temporal para pruebas

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
    scale = (1,1,1),
    position = spawn,
    collider = 'box',
    shader = lit_with_shadows_shader,
    masa = 70.0 
)
cuerpo_robot.setTransparency(TransparencyAttrib.MNone, 1)
cuerpo_robot.setDepthWrite(True)
cuerpo_robot.setDepthTest(True)

brazo_izq = Entity(
    model = modelo_brazo_izq,
    scale = (1,1,1),
    position = Vec3(0.05,  0.15,  0.0), 
    parent = cuerpo_robot,
    collider = 'box',
    shader = lit_with_shadows_shader
)

brazo_der = Entity(
    model = modelo_brazo_der,
    scale = (1,1,1),
    position = Vec3( -0.05,  0.15,  0.0),
    parent = cuerpo_robot,
    collider = 'box',
    shader = lit_with_shadows_shader
)

# --- CONSTRUCCIÓN DEL MAPA ---

# Paredes Sólidas Normales (permeable=0.0 por defecto)
pared1 = crear_hitbox(posicion=(0, 2.5, 6), escala=(10, 5, 1), permeable=0.0, visible=True)
pared1.color = color.gray
pared2 = crear_hitbox(posicion=(6, 2.5, 0), escala=(1, 5, 10), permeable=0.0, visible=True)
pared2.color = color.gray

# Puerta Cuántica (permeable=1.0)
puerta_rendija = crear_hitbox(posicion=(-5, 2.5, -5), escala=(4, 5, 0.5), permeable=1.0, visible=True)
puerta_rendija.color = color.orange

# Piso (Debe tener collider para que la gravedad lo detecte)
ground = Entity(
    model='cube',          # Ahora es un bloque sólido
    position=(0, -0.5, 0), # Lo bajamos medio metro para que el ras del suelo quede exactamente en Y = 0
    scale=(30, 1, 30),     # 30x30 de área, y 1 metro entero de grosor
    texture='brick', 
    texture_scale=(15,15), 
    color=color.gray, 
    collider='box'         # Al ser un cubo, Ursina le asigna una hitbox tridimensional perfecta
)

onda = FuncionOndaCuantica(cuerpo_robot, brazo_izq, brazo_der)

AmbientLight(color=color.rgb(10, 10, 20))
sun = DirectionalLight(shadows=False, color=color.rgb(100, 100, 100))
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
        cuerpo_robot.position += cuerpo_robot.forward * velocidad_actual * time.dt
        target_rot_x_der = rotacion_brazo_caminar_actual
        target_rot_x_izq = rotacion_brazo_caminar_actual
        
    if held_keys['s']:
        cuerpo_robot.position -= cuerpo_robot.forward * velocidad_actual * time.dt
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