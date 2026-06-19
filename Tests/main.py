
from ursina import *
import math # Necesario para los calculos de angulos

app = Ursina()

# --- 1. EL ROBOT (Ahora con indicador de frente) ---
robot = Entity(
    model='cube',
    color=color.blue,
    scale=1.5,
    y=0.75
)

# Agregamos un "Visor" o "Sensor" en la cara frontal
# Al poner 'parent=robot', este objeto es parte del robot.
visor = Entity(
    parent=robot,           # Es hijo del robot
    model='cube',
    color=color.yellow,     # Color diferente para que resalte
    scale=(0.8, 0.3, 0.2),  # Más ancho y plano
    position=(0, 0.2, 0.55) # Lo movemos hacia adelante (Z positivo) para que sobresalga
)

# --- 2. EL ENTORNO ---
# Usamos una textura de rejilla (grid) si es posible, o 'brick' con repetición
# para ver mejor el suelo moverse.
ground = Entity(
    model='plane',
    scale=30,
    texture='brick',        # Ladrillos ayudan a ver el movimiento
    texture_scale=(15,15),
    color=color.gray
)

# --- 3. VARIABLES ---
velocidad_movimiento = 6
velocidad_camara = 6

def update():
    velocidad_rotacion = 120 # Grados por segundo
    
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

    # --- LÓGICA DE CÁMARA (Igual que antes) ---
    posicion_camara_objetivo = robot.position - (robot.forward * 10) + Vec3(0, 5, 0)
    camera.position = lerp(camera.position, posicion_camara_objetivo, velocidad_camara * time.dt)
    camera.look_at(robot.position + Vec3(0, 1, 0))
    camera.rotation_z = 0

def main():
    app.run()

if __name__ == "__main__":
    main()
