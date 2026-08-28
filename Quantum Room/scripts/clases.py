from panda3d.core import loadPrcFileData
# Fuerza a Panda3D a usar el renderizador por software (ignora la GPU)
loadPrcFileData('', 'load-display p3tinydisplay')
from ursina import *
from ursina.prefabs.editor_camera import EditorCamera
from panda3d.core import TransparencyAttrib, Vec4
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
        # Distancia exacta desde el centro geométrico del modelo 3D hasta su base.
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
            #los distribuyo uniformemente
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
            
            # --- LÓGICA DE PERMEABILIDAD ---
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
            entidad.color = Vec4(90/255, 0, 2, a)
            
