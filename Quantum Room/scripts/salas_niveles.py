from panda3d.core import loadPrcFileData
# Forzamos la CPU para tu gráfica integrada
loadPrcFileData('', 'load-display p3tinydisplay')
from panda3d.core import TransparencyAttrib
from ursina import *
import os
from pathlib import Path
RAIZ_PROYECTO = Path(__file__).resolve().parent.parent
application.asset_folder = RAIZ_PROYECTO

def crear_hitbox(posicion, escala, permeable=0.0, modo_edicion=True):
    # Definir colores llamativos según permeabilidad
    if permeable > 0.0:
        color_caja = color.rgba(255, 165, 0, 10) # Naranja semi-transparente (Puertas)
        color_borde = color.orange
    else:
        color_caja = color.rgba(255, 0, 0, 10)   # Rojo semi-transparente (Paredes)
        color_borde = color.red

    hitbox = Entity(
        model='cube',
        position=posicion,
        scale=escala,
        collider='box',
        # Si estamos editando, muestra el color neón, si no, lo hace invisible
        color=color_caja if modo_edicion else color.clear 
    )
    hitbox.permeabilidad_cuantica = permeable

    if modo_edicion:
        Entity(
            parent=hitbox,
            model='wireframe_cube',
            color=color_borde,
            scale=1.02,
            unlit=True
        )
    return hitbox

class MapaNivel1:
    def __init__(self, modo_edicion=True):
        self.modo_edicion = modo_edicion
        
        # 1. CARGAR EL MODELO VISUAL
        self.modelo_visual = Entity(
            model='assets/models/salas/sala1(2).glb', # C
            position=(0, 0, 0),
            scale=1,
            unlit=True
        )
        self.modelo_visual.setTransparency(TransparencyAttrib.MNone, 1) #transparencia
        self.modelo_visual.setDepthWrite(True) #distancia con respecto a la camara
        self.modelo_visual.setDepthTest(True) #no dibuja los pixeles tapados por otros
        self.modelo_visual.color_scale = Vec4(0.8, 0.8, 0.8, 1.0)  #escalado del color

        # Listas para guardar las hitboxes
        self.hitboxes_paredes = []
        self.hitboxes_puertas = []
        self.hitboxes_suelo = []

        # 2. CONSTRUIR COLISIONES
        self.construir_colisiones()

    def construir_colisiones(self):
        # Color del suelo en modo edición (Cian semi-transparente)
        color_suelo = color.rgba(0, 255, 255, 10) if self.modo_edicion else color.clear

        # --- SUELO (Posición, Escala) ---
        datos_suelos = [
            ((4, -0.25, -2), (28, 0.5, 24)),
            ((4, -0.25, 20), (20, 0.5, 12)),
            ((4, -0.25, -24), (20, 0.5, 12)),
            ((22, -0.25, -2), (8, 0.5, 8)),
            ((-16, -0.25, -24), (12, 0.5, 12)),
            ((4, -0.25, 12), (4, 0.5, 4)),
            ((4, -0.25, -16), (4, 0.5, 4)),
            ((-8, -0.25, -24), (4, 0.5, 4))
        ]

        for pos, esc in datos_suelos:
            suelo = Entity(
                model='cube', position=pos, scale=esc, 
                collider='box', color=color_suelo
            )
            self.hitboxes_suelo.append(suelo)

        # --- PAREDES SÓLIDAS (Posición, Escala, Rotación Y) ---
        datos_paredes = [
            ((-3, 2.5, 10), (10, 5, 1), 0),         # Pared 1
            ((-9, 2.5, 9), (4, 5, 1), -45),         # Pared 2
            ((-10, 2.5, -2), (22, 5, 1), -90),      # Pared 3
            ((-9, 2.5, -13), (4, 5, 1), 45),        # Pared 4
            ((-3, 2.5, -14), (10, 5, 1), 0),        # Pared 5
            ((11, 2.5, -14), (10, 5, 1), 0),        # Pared 6
            ((11, 2.5, 10), (10, 5, 1), 0),         # Pared 7
            ((17, 2.5, -13), (4, 5, 1), -45),       # Pared 8
            ((17, 2.5, 9), (4, 5, 1), 45),          # Pared 9
            ((18, 2.5, -9), (6, 5, 1), -90),        # Pared 10
            ((18, 2.5, 5), (6, 5, 1), -90),         # Pared 11
            ((22, 2.5, 2), (8, 5, 1), 0),           # Pared 12
            ((22, 2.5, -6), (8, 5, 1), 0),          # Pared 13
            ((26, 2.5, -2), (8, 5, 1), -90),        # Pared 14
            ((6, 2.5, 12), (4, 5, 1), -90),         # Pared 15
            ((2, 2.5, 12), (4, 5, 1), -90),         # Pared 16
            ((2, 2.5, -16), (4, 5, 1), -90),        # Pared 17
            ((6, 2.5, -16), (4, 5, 1), -90),        # Pared 18
            ((14, 2.5, -24), (8, 5, 1), -90),       # Pared 19
            ((14, 2.5, 20), (8, 5, 1), -90),        # Pared 20
            ((-6, 2.5, 20), (8, 5, 1), -90),        # Pared 21
            ((-22, 2.5, -24), (8, 5, 1), -90),      # Pared 22
            ((-10, 2.5, -21), (3, 5, 1), -90),      # Pared 23
            ((-6, 2.5, -21), (3, 5, 1), -90),       # Pared 24
            ((-10, 2.5, -27), (3, 5, 1), -90),      # Pared 25
            ((-6, 2.5, -27), (3, 5, 1), -90),       # Pared 26
            ((13, 2.5, 15), (4, 5, 1), -45),        # Pared 27
            ((-5, 2.5, 25), (4, 5, 1), -45),        # Pared 28
            ((-5, 2.5, -19), (4, 5, 1), -45),       # Pared 29
            ((13, 2.5, -29), (4, 5, 1), -45),       # Pared 30
            ((-11, 2.5, -29), (4, 5, 1), -45),      # Pared 31
            ((-21, 2.5, -19), (4, 5, 1), -45),      # Pared 32
            ((-5, 2.5, 15), (4, 5, 1), 45),         # Pared 33
            ((13, 2.5, 25), (4, 5, 1), 45),         # Pared 34
            ((13, 2.5, -19), (4, 5, 1), 45),        # Pared 35
            ((-5, 2.5, -29), (4, 5, 1), 45),        # Pared 36
            ((-21, 2.5, -29), (4, 5, 1), 45),       # Pared 37
            ((-11, 2.5, -19), (4, 5, 1), 45),       # Pared 38
            ((-16, 2.5, -30), (10, 5, 1), 0),       # Pared 39
            ((4, 2.5, -30), (18, 5, 1), 0),         # Pared 40
            ((4, 2.5, 26), (18, 5, 1), 0),          # Pared 41
            ((-16, 2.5, -18), (10, 5, 1), 0),       # Pared 42
            ((-1, 2.5, -18), (7, 5, 1), 0),         # Pared 43
            ((9, 2.5, -18), (7, 5, 1), 0),          # Pared 44
            ((-1, 2.5, 14), (7, 5, 1), 0),          # Pared 45
            ((9, 2.5, 14), (7, 5, 1), 0),           # Pared 46
            ((-8, 2.5, -26), (4, 5, 1), 0),         # Pared 47
            ((-8, 2.5, -22), (4, 5, 1), 0)          # Pared 48
        ]
        
        for pos, esc, rot in datos_paredes:
            pared = crear_hitbox(posicion=pos, escala=esc, permeable=0.0, modo_edicion=self.modo_edicion)
            if rot != 0:
                pared.rotation_y = rot
            self.hitboxes_paredes.append(pared)


        # --- PUERTAS Y RENDIJAS --- (mas adelante)
        #puerta = crear_hitbox(posicion=(5, 2.5, 0), escala=(1, 5, 3), permeable=1.0, modo_edicion=self.modo_edicion)
        #self.hitboxes_puertas.append(puerta)

    def destruir(self):
        destroy(self.modelo_visual)
        for h in self.hitboxes_paredes + self.hitboxes_puertas + self.hitboxes_suelo:
            destroy(h)

# =====================================================================
# ZONA DE PRUEBAS (Solo se ejecuta si corres este script directamente)
# =====================================================================
if __name__ == '__main__':
    from ursina.prefabs.editor_camera import EditorCamera
    
    app = Ursina(title='Laboratorio de Mapas')
    
    # Instanciamos el mapa 
    mapa_prueba = MapaNivel1(modo_edicion=False)
    
    # Cámara libre para volar por el mapa
    EditorCamera()
    
    # Ejes de referencia (opcional, para orientarte)
    Entity(model='cube', color=color.green, scale=(0.05, 2, 0.05), y=1) # Y es Arriba
    Entity(model='cube', color=color.red, scale=(2, 0.05, 0.05), x=1)   # X es Derecha
    Entity(model='cube', color=color.blue, scale=(0.05, 0.05, 2), z=1)  # Z es Profundidad

    Text(text="Laboratorio de Hitboxes\nClick Derecho: Rotar\nRueda: Zoom\nMiddle Click: Mover", position=(-0.85, 0.45), scale=0.8)
    
    app.run()