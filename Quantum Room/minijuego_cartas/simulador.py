# Ruta: Quantum_Room/minijuego_cartas/simulador.py

import random
import time

# --- CLASE BASE DE CARTAS (Etapa 2) ---
class Carta:
    def __init__(self, nombre, costo, rango_min, rango_max, descripcion):
        self.nombre = nombre
        self.costo_fragmentos = costo
        self.rango_min = rango_min
        self.rango_max = rango_max
        self.descripcion = descripcion
        
        # El valor exacto se "colapsa" (se decide) al instanciar la carta
        self.efecto_actual = self.calcular_efecto()

    def calcular_efecto(self):
        """Genera un valor aleatorio dentro del rango permitido"""
        return random.randint(self.rango_min, self.rango_max)

    def usar(self, jugador):
        if jugador['fragmentos'] >= self.costo_fragmentos:
            jugador['fragmentos'] -= self.costo_fragmentos
            jugador['probabilidad_exito'] += self.efecto_actual
            
            print(f"\n[+] Has jugado: {self.nombre}")
            print(f"[-] Te costó {self.costo_fragmentos} Fragmento(s).")
            print(f"[!] El efecto cuántico resultó en un +{self.efecto_actual}% de probabilidad.")
            return True
        else:
            print(f"\n[X] Error: No tienes fragmentos suficientes.")
            return False

# --- CREACIÓN DEL MAZO (Con rangos dinámicos) ---
# Observación: Barata, poco impacto, muy estable (+10% a +15%)
carta_observacion = Carta("Observación Cuántica", 1, 10, 15, "Aumenta ligeramente el éxito.")

# Interferencia: Coste medio, impacto medio, rango inestable (+15% a +25%)
carta_interferencia = Carta("Interferencia", 2, 15, 25, "Alteración moderada con rango variable.")

# Incertidumbre: Muy cara, puede salvarte la vida o hacer casi nada (+5% a +50%)
carta_incertidumbre = Carta("Incertidumbre Pura", 3, 5, 50, "Riesgo total. Puede ser inútil o decisiva.")

mazo = [carta_observacion, carta_interferencia, carta_incertidumbre]

# --- ESTADO DEL JUGADOR ---
jugador = {
    'fragmentos': 6,             
    'probabilidad_exito': 25,    
    'rondas_restantes': 4
}

# --- BUCLE DEL MINIJUEGO (Etapa 3 - Simulador) ---
def iniciar_simulador():
    print("="*50)
    print(" INICIANDO RECONSTRUCCIÓN COGNITIVA (V2) ")
    print("="*50)
    
    while jugador['rondas_restantes'] > 0:
        print(f"\n--- ESTADO ACTUAL ---")
        print(f"Fragmentos: {jugador['fragmentos']} | Probabilidad de Éxito: {jugador['probabilidad_exito']}% | Rondas: {jugador['rondas_restantes']}")
        
        print("\nTus Cartas en Mano:")
        for i, carta in enumerate(mazo):
            # Mostramos al jugador el rango posible, y el número que le tocó en este turno
            print(f"{i + 1}. {carta.nombre} (Costo: {carta.costo_fragmentos})")
            print(f"   -> Rango: [{carta.rango_min}% a {carta.rango_max}%] | Valor actual robado: +{carta.efecto_actual}%")
        
        print("\n0. Intentar Reconstruir (Terminar ronda y tirar los dados)")
        
        eleccion = input("\nElige una acción (0, 1, 2, 3): ")
        
        if eleccion == '0':
            print("\nProcesando reconstrucción...")
            time.sleep(1)
            tirada = random.randint(1, 100)
            print(f"El sistema tiró un {tirada}. Necesitabas {jugador['probabilidad_exito']} o menos.")
            
            if tirada <= jugador['probabilidad_exito']:
                print("\n[ÉXITO] ¡Recuerdo recuperado!")
                break
            else:
                jugador['rondas_restantes'] -= 1
                print("\n[FALLO] El subconsciente bloqueó el intento.")
                if jugador['rondas_restantes'] == 0:
                    print("\n[DERROTA] Conexión perdida.")
        
        elif eleccion.isdigit() and int(eleccion) > 0 and int(eleccion) <= len(mazo):
            carta_elegida = mazo[int(eleccion) - 1]
            si_se_uso = carta_elegida.usar(jugador)
            
            if si_se_uso:
                # Opcional: Re-calcular el valor de la carta para el siguiente turno
                # simulando que al robar otra copia, tendrá un valor distinto.
                carta_elegida.efecto_actual = carta_elegida.calcular_efecto()
        else:
            print("\nEntrada no válida.")

if __name__ == "__main__":
    iniciar_simulador()