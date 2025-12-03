import heapq
from collections import defaultdict
import random
import time

class GrafoCiudades:
    def __init__(self):
        self.grafo = defaultdict(list)
        self.ciudades = set()
    
    def agregar_ruta(self, origen, destino, distancia, costo):
        self.grafo[origen].append((destino, distancia, costo))
        self.grafo[destino].append((origen, distancia, costo))
        self.ciudades.add(origen)
        self.ciudades.add(destino)
    
    #Algoritmo para encontrar la ruta optima entre ciudades
    def dijkstra(self, inicio, fin):
        distancias = {ciudad: float('inf') for ciudad in self.ciudades}
        costos = {ciudad: float('inf') for ciudad in self.ciudades}
        distancias[inicio] = 0
        costos[inicio] = 0
        
        # Cola de prioridad: (costo_acumulado, distancia_acumulada, ciudad, camino)
        cola = [(0, 0, inicio, [inicio])]
        visitados = set()
        
        while cola:
            costo_actual, dist_actual, ciudad_actual, camino = heapq.heappop(cola)
            
            if ciudad_actual in visitados:
                continue
            
            visitados.add(ciudad_actual)
            
            # Si llegamos al destino
            if ciudad_actual == fin:
                return dist_actual, costo_actual, camino
            
            # Explorar vecinos
            for vecino, distancia, costo in self.grafo[ciudad_actual]:
                if vecino not in visitados:
                    nuevo_costo = costo_actual + costo
                    nueva_dist = dist_actual + distancia
                    
                    if nuevo_costo < costos[vecino]:
                        costos[vecino] = nuevo_costo
                        distancias[vecino] = nueva_dist
                        nuevo_camino = camino + [vecino]
                        heapq.heappush(cola, (nuevo_costo, nueva_dist, vecino, nuevo_camino))
        
        return None, None, None  # No hay ruta

class Recurso:    
    def __init__(self, nombre, precio_base, rareza, peso):
        self.nombre = nombre
        self.precio_base = precio_base
        self.precio_actual = precio_base
        self.rareza = rareza  # 1-5, afecta disponibilidad
        self.peso = peso
        self.demanda = 50  # 0-100
        self.oferta = 50   # 0-100
        self.ubicacion = "Torre Keio"
        self.stock = 100

        self.precios_regionales = {}
        self.stocks_regionales = {}  
    
    def actualizar_precio(self):
        # Fórmula: precio = precio_base * (demanda/oferta)
        ratio = self.demanda / max(self.oferta, 1)
        self.precio_actual = round(self.precio_base * ratio * random.uniform(0.9, 1.1), 2)
        
        # Limitar fluctuaciones extremas
        self.precio_actual = max(self.precio_base * 0.3, 
                                 min(self.precio_actual, self.precio_base * 3))
    
    def __repr__(self):
        return f"{self.nombre}: ${self.precio_actual:.2f} (D:{self.demanda} O:{self.oferta})"


class Mercado:
    def __init__(self):
        self.recursos = {}
        self.inicializar_recursos()
    
    def inicializar_recursos(self):
        recursos_base = [
            Recurso("CPU Shards", 500, 3, 5),
            Recurso("RAM Blocks", 350, 2, 8),
            Recurso("Data Packets", 600, 3, 6),
            Recurso("Quantum Keys", 2000, 5, 2),
            Recurso("Bug Residue", 80, 1, 4),
            Recurso("Neural Chips", 1200, 4, 3),
            Recurso("Energy Cores", 900, 4, 7),
            Recurso("Crypto Keys", 1500, 5, 2),
        ]
        
        # Asignar ubicaciones a los recursos
        ubicaciones = {
            "CPU Shards": "Torre Keio",
            "RAM Blocks": "Anillos de Datos", 
            "Data Packets": "Torre Keio",
            "Quantum Keys": "Montaña",
            "Bug Residue": "Puerto Cache",
            "Neural Chips": "Minas de Silicio",
            "Energy Cores": "Bosque del Firmware",
            "Crypto Keys": "Refinería de Códigos"
        }

        todas_ubicaciones = [
            "Torre Keio",
            "Anillos de Datos",
            "Bosque del Firmware",
            "Minas de Silicio",
            "Montaña",
            "Refinería de Códigos",
            "Puerto Cache",
            "Valle Binario",
            "Nodo Central"
        ]
        
        # ESTO ES LO QUE FALTABA - ASIGNAR RECURSOS Y PRECIOS
        for recurso in recursos_base:
            recurso.ubicacion = ubicaciones.get(recurso.nombre, "Torre Keio")
            
            # Configurar precios y stocks por región
            for ubicacion in todas_ubicaciones:
                if ubicacion == recurso.ubicacion:
                    # En la ubicación de origen: BARATO y MUCHO STOCK
                    recurso.precios_regionales[ubicacion] = recurso.precio_base * random.uniform(0.7, 0.9)
                    recurso.stocks_regionales[ubicacion] = random.randint(150, 250)
                else:
                    # En otras ubicaciones: MÁS CARO y MENOS STOCK
                    multiplicador = 1.2 + (recurso.rareza * 0.15)
                    recurso.precios_regionales[ubicacion] = recurso.precio_base * random.uniform(multiplicador, multiplicador + 0.3)
                    recurso.stocks_regionales[ubicacion] = random.randint(20, 80)
            
            # Variar oferta/demanda inicial
            recurso.demanda = random.randint(30, 70)
            recurso.oferta = random.randint(30, 70)
            
            # AGREGAR AL DICCIONARIO DE RECURSOS
            self.recursos[recurso.nombre] = recurso

    def simular_mercado(self):
        """Simula cambios aleatorios en oferta y demanda"""
        for recurso in self.recursos.values():
            recurso.demanda = max(10, min(100, recurso.demanda + random.randint(-15, 15)))
            recurso.oferta = max(10, min(100, recurso.oferta + random.randint(-15, 15)))
            recurso.actualizar_precio()
        
    def obtener_recursos_por_ubicacion(self, ubicacion):
        """Obtiene recursos con precios y stocks específicos de una ubicación"""
        recursos_ubicacion = []
        
        for recurso in self.recursos.values():
            import copy
            recurso_regional = copy.copy(recurso)
            
            if ubicacion in recurso.precios_regionales:
                recurso_regional.precio_actual = recurso.precios_regionales[ubicacion]
                recurso_regional.stock = recurso.stocks_regionales[ubicacion]
            else:
                recurso_regional.precio_actual = recurso.precio_base * 1.5
                recurso_regional.stock = 50
            
            recursos_ubicacion.append(recurso_regional)
        
        return recursos_ubicacion

    def ordenar_por_precio(self, descendente=True):
        """Ordena recursos por precio"""
        return sorted(self.recursos.values(), 
                     key=lambda r: r.precio_actual, 
                     reverse=descendente)
    
    def ordenar_por_ratio_valor_peso(self):
        """Ordena recursos por eficiencia (precio/peso)"""
        return sorted(self.recursos.values(), 
                     key=lambda r: r.precio_actual / r.peso, 
                     reverse=True)

    def ordenar_por_demanda(self, recursos=None):
        """Ordena recursos por demanda (mayor a menor)"""
        if recursos is None:
            recursos = list(self.recursos.values())
        return sorted(recursos, key=lambda r: r.demanda, reverse=True)

    def ordenar_por_oferta(self, recursos=None):
        """Ordena recursos por oferta (mayor a menor)"""
        if recursos is None:
            recursos = list(self.recursos.values())
        return sorted(recursos, key=lambda r: r.oferta, reverse=True)

class Jugador:
    def __init__(self, nombre, dinero=50000, capacidad_max=50):
        self.nombre = nombre
        self.dinero = dinero
        self.inventario = {}  # {nombre_recurso: cantidad}
        self.capacidad_max = capacidad_max
        self.capacidad_usada = 0
    
    def comprar_recurso(self, recurso, cantidad, mercado):
        costo_total = recurso.precio_actual * cantidad
        peso_total = recurso.peso * cantidad
        
        if self.dinero < costo_total:
            print(f"Dinero insuficiente. Necesitas ${costo_total:.2f}")
            return False
        
        if self.capacidad_usada + peso_total > self.capacidad_max:
            print(f"Capacidad insuficiente. Necesitas {peso_total}kg de espacio")
            return False
        
        self.dinero -= costo_total
        self.capacidad_usada += peso_total
        self.inventario[recurso.nombre] = self.inventario.get(recurso.nombre, 0) + cantidad
        
        # Afectar mercado
        recurso.stock = max(0, recurso.stock - cantidad)
        recurso.oferta = max(10, recurso.oferta - cantidad * 2)
        recurso.demanda = min(100, recurso.demanda + cantidad)
        recurso.actualizar_precio()
        
        print(f"Compraste {cantidad}x {recurso.nombre} por ${costo_total:.2f}")
        return True
    
    def vender_recurso(self, nombre_recurso, cantidad, mercado):
        if nombre_recurso not in self.inventario or self.inventario[nombre_recurso] < cantidad:
            print(f"No tienes suficiente {nombre_recurso}")
            return False
        
        recurso = mercado.recursos[nombre_recurso]
        ganancia = recurso.precio_actual * cantidad * 0.9  # 10% de comisión
        peso_liberado = recurso.peso * cantidad
        
        self.dinero += ganancia
        self.capacidad_usada -= peso_liberado
        self.inventario[nombre_recurso] -= cantidad
        
        if self.inventario[nombre_recurso] == 0:
            del self.inventario[nombre_recurso]
        
        # Afectar mercado
        recurso.oferta = min(100, recurso.oferta + cantidad * 2)
        recurso.demanda = max(10, recurso.demanda - cantidad)
        
        print(f"Vendiste {cantidad}x {nombre_recurso} por ${ganancia:.2f}")
        return True
    
    def optimizar_inventario_mochila(self, mercado):
        recursos_disponibles = list(mercado.recursos.values())
        W = int(self.capacidad_max - self.capacidad_usada)
        
        if W <= 0:
            print("No hay capacidad disponible")
            return []
        
        dp = [0 for _ in range(W + 1)]
        parent = [-1 for _ in range(W + 1)]
        
        for w in range(1, W + 1):
            for i, recurso in enumerate(recursos_disponibles):
                peso = int(recurso.peso)
                valor = int(recurso.precio_actual)
                
                if peso <= w and self.dinero >= recurso.precio_actual:
                    if dp[w - peso] + valor > dp[w]:
                        dp[w] = dp[w - peso] + valor
                        parent[w] = i
        
        recomendaciones = {}
        w = W
        dinero_gastado = 0
        
        while w > 0 and parent[w] != -1:
            recurso_idx = parent[w]
            recurso = recursos_disponibles[recurso_idx]
            
            if dinero_gastado + recurso.precio_actual > self.dinero:
                break
            
            if recurso.nombre not in recomendaciones:
                recomendaciones[recurso.nombre] = 0
            recomendaciones[recurso.nombre] += 1
            
            w -= int(recurso.peso)
            dinero_gastado += recurso.precio_actual
        
        resultado = []
        for nombre, cantidad in recomendaciones.items():
            recurso = mercado.recursos[nombre]
            resultado.append((recurso, cantidad))
        
        return resultado

class SimuladorComercio:
    """Sistema principal que integra todos los componentes"""
    
    def __init__(self):
        self.mercado = Mercado()
        self.grafo = GrafoCiudades()
        self.jugador = Jugador("Jugador1")
        self.turno = 0
        self.inicializar_mundo()
    
    def inicializar_mundo(self):
            """Crea el mundo del juego con ciudades y rutas - RED COMPLEJA"""
            
            # Torre Keio connections
            self.grafo.agregar_ruta("Torre Keio", "Puerto Cache", 100, 120)
            self.grafo.agregar_ruta("Torre Keio", "Nodo Central", 95, 100)
            self.grafo.agregar_ruta("Torre Keio", "Refinería de Códigos", 280, 350)
            
            # Puerto Cache connections
            self.grafo.agregar_ruta("Puerto Cache", "Anillos de Datos", 120, 150)
            self.grafo.agregar_ruta("Puerto Cache", "Valle Binario", 85, 90)
            
            # Nodo Central connections
            self.grafo.agregar_ruta("Nodo Central", "Bosque del Firmware", 130, 140)
            self.grafo.agregar_ruta("Nodo Central", "Montaña", 100, 110)
            
            # Anillos de Datos connections
            self.grafo.agregar_ruta("Anillos de Datos", "Valle Binario", 75, 80)
            self.grafo.agregar_ruta("Anillos de Datos", "Minas de Silicio", 180, 200)
            self.grafo.agregar_ruta("Anillos de Datos", "Bosque del Firmware", 350, 400)
            
            # Valle Binario connections
            self.grafo.agregar_ruta("Valle Binario", "Refinería de Códigos", 120, 130)
            self.grafo.agregar_ruta("Valle Binario", "Minas de Silicio", 140, 160)
            
            # Montaña connections
            self.grafo.agregar_ruta("Montaña", "Bosque del Firmware", 90, 95)
            self.grafo.agregar_ruta("Montaña", "Refinería de Códigos", 160, 180)
            
            # Bosque del Firmware connections
            self.grafo.agregar_ruta("Bosque del Firmware", "Refinería de Códigos", 150, 170)
            
            # Minas de Silicio connections
            self.grafo.agregar_ruta("Minas de Silicio", "Refinería de Códigos", 130, 140)
            
            # Torre Keio connections
            self.grafo.agregar_ruta("Torre Keio", "Puerto Cache", 100, 120)
            self.grafo.agregar_ruta("Torre Keio", "Nodo Central", 95, 100)
            self.grafo.agregar_ruta("Torre Keio", "Refinería de Códigos", 280, 350)  # Ruta directa larga
            
            # Puerto Cache connections
            self.grafo.agregar_ruta("Puerto Cache", "Anillos de Datos", 120, 150)
            self.grafo.agregar_ruta("Puerto Cache", "Valle Binario", 85, 90)
            
            # Nodo Central connections
            self.grafo.agregar_ruta("Nodo Central", "Bosque del Firmware", 130, 140)
            self.grafo.agregar_ruta("Nodo Central", "Montaña", 100, 110)
            
            # Anillos de Datos connections
            self.grafo.agregar_ruta("Anillos de Datos", "Valle Binario", 75, 80)
            self.grafo.agregar_ruta("Anillos de Datos", "Minas de Silicio", 180, 200)
            self.grafo.agregar_ruta("Anillos de Datos", "Bosque del Firmware", 350, 400)  # Ruta directa larga
            
            # Valle Binario connections
            self.grafo.agregar_ruta("Valle Binario", "Refinería de Códigos", 120, 130)
            self.grafo.agregar_ruta("Valle Binario", "Minas de Silicio", 140, 160)
            
            # Montaña connections
            self.grafo.agregar_ruta("Montaña", "Bosque del Firmware", 90, 95)
            self.grafo.agregar_ruta("Montaña", "Refinería de Códigos", 160, 180)
            
            # Bosque del Firmware connections
            self.grafo.agregar_ruta("Bosque del Firmware", "Refinería de Códigos", 150, 170)
            
            # Minas de Silicio connections
            self.grafo.agregar_ruta("Minas de Silicio", "Refinería de Códigos", 130, 140)