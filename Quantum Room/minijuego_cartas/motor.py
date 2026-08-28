import random

class MotorProbabilistico:
    def __init__(self, modo_juego="NORMAL"):
        
        # 1. Configuración escalable de Modos de Juego
        # formato -> "MODO": (exitos_necesarios, tiempo_limite_en_segundos)
        self.modos_disponibles = {
            "CORTA": {"exitos": 3, "tiempo": 300},         # 5 minutos
            "NORMAL": {"exitos": 5, "tiempo": 600},        # 10 minutos
            "LARGA": {"exitos": 7, "tiempo": 900},         # 15 minutos
            "MUERTE_SUBITA": {"exitos": 1, "tiempo": 60}   # 1 minuto (Tensión máxima)
        }
        
        # Validar modo y aplicar configuración
        config = self.modos_disponibles.get(modo_juego, self.modos_disponibles["NORMAL"])
        self.exitos_necesarios = config["exitos"]
        self.tiempo_limite = config["tiempo"]
        
        # 2. Variables de Estado de la Partida
        self.exitos_jugador = 0
        self.exitos_subconsciente = 0
        self.tiempo_transcurrido = 0.0
        
        self.probabilidad_base = 50 

    def actualizar_tiempo(self, dt):
        """Suma el tiempo que ha pasado en este fotograma"""
        self.tiempo_transcurrido += dt

    def limitar_probabilidad(self, prob):
        return max(0, min(100, prob))

    def resolver_ronda(self, mod_jugador, mod_subconsciente):
        """Calcula el resultado estadístico de una jugada"""
        prob_final = self.probabilidad_base + mod_jugador - mod_subconsciente
        prob_final = self.limitar_probabilidad(prob_final)

        tirada = random.randint(1, 100)
        exito_jugador = tirada <= prob_final
        
        # Registramos el punto para quien gane la ronda
        if exito_jugador:
            self.exitos_jugador += 1
        else:
            self.exitos_subconsciente += 1

        return {
            "victoria_jugador": exito_jugador,
            "probabilidad_final": prob_final,
            "tirada": tirada
        }

    def verificar_estado_partida(self):
        """Evalúa todas las condiciones de fin de partida, incluyendo el empate"""
        
        # Condición 1: Alguien alcanza los éxitos necesarios primero
        if self.exitos_jugador >= self.exitos_necesarios:
            return "VICTORIA"
        elif self.exitos_subconsciente >= self.exitos_necesarios:
            return "DERROTA"
            
        # Condición 2: Se acaba el tiempo
        if self.tiempo_transcurrido >= self.tiempo_limite:
            if self.exitos_jugador > self.exitos_subconsciente:
                return "VICTORIA_POR_TIEMPO"
            elif self.exitos_subconsciente > self.exitos_jugador:
                return "DERROTA_POR_TIEMPO"
            else:
                return "EMPATE"
                
        # Condición 3: La partida sigue
        return "EN_CURSO"