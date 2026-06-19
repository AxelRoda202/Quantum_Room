from ursina import * #importo ursina y todo lo que tiene (*)

app = Ursina() #loop principal (una ventana con un escenario 3D)

# Iluminación
AmbientLight(color=color.rgba(100, 100, 100, 0.5)) #iluminación ambiental, sin direccion, ilumina todo por igual
#color.rgba(rojo, verde, azul, alfa) alfa es la transparencia
DirectionalLight(y=2, z=3, shadows=False) # Luz con dirección, como el sol. shadows=False para no calcular sombras

# --- SUELO DE PASTO ---
ground = Entity( #Entity es cualquier objeto 3D en ursina (un objeto)
    model='plane', #plano 2d en el espacio 3d 
    scale=10, #escala 10 veces en X y Z
    texture='grass',       # Ursina trae esta textura incluida
    texture_scale=(10,10)  # Repetimos la imagen 10 veces para que parezca pasto real
)   #(10 veces en X y 10 veces en Z)

# --- ROBOT DE LADRILLO AZUL ---
robot = Entity(
    model='cube', #cubo estandar
    scale=1.5, #escala 1.5 veces en X, Y, Z
    y=0.75, #elevamos el cubo 0.75 en Y para que quede sobre el suelo
    texture='brick',       # Textura de ladrillos
    color=color.blue       # "Teñimos" los ladrillos de azul (multiplica la textura por el color)
)

EditorCamera() #agrega una cámara que podemos mover con el mouse y el teclado
app.run() #ejecuta el loop principal, abre la ventana y muestra el escenario 3D