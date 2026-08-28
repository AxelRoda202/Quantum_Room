from panda3d.core import loadPrcFileData
# Fuerza a Panda3D a usar el renderizador por software (ignora la GPU)
loadPrcFileData('', 'load-display p3tinydisplay')
from ursina import *
from ursina.prefabs.editor_camera import EditorCamera
from panda3d.core import TransparencyAttrib, Vec4
import math
import random

# --- DENTRO DE clases.py ---
class ObjetoFisico(Entity):
    def __init__(self, altura_pies, **kwargs):
        # Extraemos la lista de ignorados si existe, o creamos una vacía
        self.entidades_ignoradas = kwargs.pop('entidades_ignoradas', [])
        
        super().__init__(**kwargs)
        self.gravedad = -20.0 
        self.velocidad_y = 0.0
        self.en_el_suelo = False
        self.masa = kwargs.get('masa', 1.0) 
        self.fuerza_salto = 10.0 
        self.altura_pies = altura_pies 
        
        # Nos aseguramos de que el objeto siempre se ignore a sí mismo
        if self not in self.entidades_ignoradas:
            self.entidades_ignoradas.append(self)

    def update(self):
        self.velocidad_y += self.gravedad * time.dt
        movimiento_y = self.velocidad_y * time.dt
        nueva_y = self.y + movimiento_y

        distancia_rayo = self.altura_pies + abs(movimiento_y) + 0.1 
        
        # Usamos la lista de ignorados para evitar el bug de levitación
        rayo_suelo = raycast(self.position, Vec3(0, -1, 0), distance=distancia_rayo, ignore=self.entidades_ignoradas)

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

    def ser_empujado(self, direccion, paso, ignorar_frontal):
        """
        Lanza un rayo frontal para verificar si el objeto puede ser empujado.
        Retorna True si se movió, False si chocó con la pared.
        """
        # distance = paso + la mitad de su tamaño (para que choque el borde, no el centro)
        margen = paso + (max(self.scale) / 2) + 0.1
        
        # Lanzamos un rayo desde el centro del objeto hacia donde lo empujan
        colision = raycast(self.position + Vec3(0, self.altura_pies, 0), direccion, distance=margen, ignore=ignorar_frontal)
        
        if not colision.hit:
            self.position += direccion * paso
            return True # Camino libre
        
        return False # Chocó contra la geometría del mapa
            
# --- FUNCIÓN DE ONDA (NIEBLA CUÁNTICA) ---
class FuncionOndaCuantica:
    def __init__(self, origen_entity, brazo_i, brazo_d):
        self.origen = origen_entity
        self.brazos = [brazo_i, brazo_d]
        self.particulas = []
        self.activo = False
        self.tiempo_expansion = 0.0
        
        self.radio_minimo = 2.0  
        self.radio_maximo = 7.0 
        self.distancia_entre_anillos = 1.2 
        self.distancia_entre_cubos = 1.2   
        
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
                
                cubo = Entity(model='cube', scale=Vec3(1.5, 0.1, 1.5), unlit=True, enabled=True)
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
        
        # Filtramos cubos visibles con probabilidad válida mayor a cero
        cubos_candidatos = [p for p in self.particulas if p['entidad'].enabled and p.get('probabilidad_actual', 0) > 0]
        
        if cubos_candidatos:
            posiciones = [Vec3(p['entidad'].x, self.origen.y, p['entidad'].z) for p in cubos_candidatos]
            pesos = [p['probabilidad_actual'] for p in cubos_candidatos]
            
            # Sorteo ponderado: a mayor altura del cubo, mayor probabilidad de aparecer ahí
            posicion_elegida = random.choices(posiciones, weights=pesos, k=1)[0]
            self.origen.position = posicion_elegida

        for p in self.particulas: 
            destroy(p['entidad'])
        self.particulas.clear()
        
        self.nucleo.enabled = False
        self.origen.visible = True
        for b in self.brazos: 
            b.visible = True

    def actualizar(self, dt):
        if not self.activo: return
        self.tiempo_expansion += dt
        
        self.nucleo.scale = 0.8 + (math.sin(self.tiempo_expansion * 8) * 0.15)
        self.nucleo.position = self.origen.position + Vec3(0, 0.5, 0)
        self.nucleo.rotation = self.origen.rotation
        
        objetos_a_ignorar = (self.origen, self.nucleo)
        
        for p in self.particulas:
            entidad = p['entidad']
            dist = p['distancia_centro']
            ox = p['offset'].x
            oz = p['offset'].z
            
            pos_objetivo_x = self.nucleo.x + ox
            pos_objetivo_z = self.nucleo.z + oz
            direccion_rayo = Vec3(ox, 0, oz)
            
            # Lanzamos rayo desde el núcleo
            rayo = raycast(self.nucleo.position, direccion_rayo.normalized(), distance=dist, ignore=objetos_a_ignorar)
            
            # Obtenemos permeabilidad (1.0 libre, 0.0 pared sólida, 0.4 rendijas)
            factor_permeabilidad = 1.0
            if rayo.hit:
                factor_permeabilidad = getattr(rayo.entity, 'permeabilidad_cuantica', 0.0)
            
            # Si es pared completamente sólida (0.0), el cubo no es visible
            if factor_permeabilidad <= 0.0:
                entidad.enabled = False
                p['probabilidad_actual'] = 0.0
                continue
            
            entidad.enabled = True
            entidad.x = pos_objetivo_x
            entidad.z = pos_objetivo_z
            
            # Cálculo probabilístico base (senoidal)
            onda_base = math.sin(dist * 1.5 - self.tiempo_expansion * self.velocidad_onda)
            onda_x = math.cos(ox * 0.8 + self.tiempo_expansion * 2.0)
            onda_z = math.sin(oz * 0.8 - self.tiempo_expansion * 3.0)
            probabilidad_base = clamp((onda_base + onda_x + onda_z + 3.0) / 6.0, 0.0, 1.0)
            
            # Multiplicamos la probabilidad por la permeabilidad del objeto atravesado
            probabilidad_final = probabilidad_base * factor_permeabilidad
            p['probabilidad_actual'] = probabilidad_final
            
            # Escala (altura) proporcional a la probabilidad ajustada
            nueva_altura = lerp(self.altura_min, self.altura_max, probabilidad_final)
            entidad.scale_y = nueva_altura
            entidad.y = 0.05 + (nueva_altura / 2)
            
            a = lerp(0.05, 0.9, probabilidad_final)
            entidad.color = Vec4(90/255, 0, 2, a)