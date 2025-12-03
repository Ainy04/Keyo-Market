from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from juego import SimuladorComercio

app = Flask(__name__, static_folder='.')
CORS(app)

simulador = SimuladorComercio()

# ============================================
# RUTAS HTML
# ============================================

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

@app.route('/api/mercado', methods=['GET'])
def obtener_mercado():
    """Obtiene recursos, opcionalmente filtrados por ubicación"""
    ubicacion = request.args.get('ubicacion', '')
    orden = request.args.get('orden', 'precio')  # precio, demanda, oferta
    
    print(f"Obteniendo mercado - Ubicación: '{ubicacion}' - Orden: {orden}")
    
    # Filtrar por ubicación
    if ubicacion and ubicacion != "":
        recursos = simulador.mercado.obtener_recursos_por_ubicacion(ubicacion)
        print(f"Encontrados {len(recursos)} recursos en {ubicacion}")
    else:
        # Sin filtro: mostrar precios PROMEDIO de todas las regiones
        recursos = []
        for recurso_base in simulador.mercado.recursos.values():
            import copy
            recurso_promedio = copy.copy(recurso_base)
            
            # Calcular precio promedio de todas las regiones
            if recurso_base.precios_regionales:
                precio_total = sum(recurso_base.precios_regionales.values())
                recurso_promedio.precio_actual = precio_total / len(recurso_base.precios_regionales)
                
                # Stock promedio
                stock_total = sum(recurso_base.stocks_regionales.values())
                recurso_promedio.stock = int(stock_total / len(recurso_base.stocks_regionales))
            else:
                recurso_promedio.precio_actual = recurso_base.precio_base
                recurso_promedio.stock = 100
            
            recursos.append(recurso_promedio)
    
    # Ordenar según criterio
    if orden == 'demanda':
        recursos = sorted(recursos, key=lambda r: r.demanda, reverse=True)
    elif orden == 'oferta':
        recursos = sorted(recursos, key=lambda r: r.oferta, reverse=True)
    else:
        recursos = sorted(recursos, key=lambda r: r.precio_actual, reverse=True)
    
    resultado = []
    for recurso in recursos:
        resultado.append({
            'nombre': recurso.nombre,
            'precio': recurso.precio_actual,
            'precio_base': recurso.precio_base,
            'demanda': recurso.demanda,
            'oferta': recurso.oferta,
            'stock': recurso.stock,
            'peso': recurso.peso,
            'rareza': recurso.rareza,
            'ubicacion': recurso.ubicacion,
            'cambio_porcentaje': round(((recurso.precio_actual - recurso.precio_base) / recurso.precio_base) * 100, 1)
        })
    
    return jsonify(resultado)

@app.route('/api/comprar', methods=['POST'])
def comprar_recurso():
    """Compra un recurso"""
    data = request.json
    recurso_nombre = data['recurso']
    cantidad = data.get('cantidad', 1)
    
    # Buscar recurso (case-insensitive)
    recurso = None
    for nombre, r in simulador.mercado.recursos.items():
        if nombre.lower() == recurso_nombre.lower():
            recurso = r
            break
    
    if not recurso:
        print(f"❌ Recurso no encontrado: '{recurso_nombre}'")
        print(f"📋 Recursos disponibles: {list(simulador.mercado.recursos.keys())}")
        return jsonify({
            'error': 'Recurso no encontrado', 
            'exito': False,
            'mensaje': f'El recurso "{recurso_nombre}" no existe en el mercado'
        }), 404
    
    # Validaciones previas
    costo_total = recurso.precio_actual * cantidad
    peso_total = recurso.peso * cantidad
    
    if simulador.jugador.dinero < costo_total:
        return jsonify({
            'exito': False,
            'mensaje': f'💰 DINERO INSUFICIENTE\n\nNecesitas: ${round(costo_total):,}\nTienes: ${round(simulador.jugador.dinero):,}\nTe faltan: ${round(costo_total - simulador.jugador.dinero):,}'
        })
    
    if simulador.jugador.capacidad_usada + peso_total > simulador.jugador.capacidad_max:
        capacidad_disponible = simulador.jugador.capacidad_max - simulador.jugador.capacidad_usada
        return jsonify({
            'exito': False,
            'mensaje': f'🎒 INVENTARIO LLENO\n\nPeso necesario: {peso_total}kg\nCapacidad disponible: {round(capacidad_disponible, 1)}kg\nTe faltan: {round(peso_total - capacidad_disponible, 1)}kg de espacio\n\n💡 Vende algunos recursos para liberar espacio'
        })
    
    exito = simulador.jugador.comprar_recurso(recurso, cantidad, simulador.mercado)
    
    return jsonify({
        'exito': exito,
        'dinero': simulador.jugador.dinero,
        'inventario': simulador.jugador.inventario,
        'capacidad_usada': simulador.jugador.capacidad_usada,
        'capacidad_max': simulador.jugador.capacidad_max,
        'mensaje': f'✅ COMPRA EXITOSA\n\nCompraste: {cantidad}x {recurso_nombre}\nGastaste: ${round(costo_total):,}\nDinero restante: ${round(simulador.jugador.dinero):,}' if exito else 'No se pudo completar la compra'
    })

@app.route('/api/vender', methods=['POST'])
def vender_recurso():
    """Vende un recurso"""
    data = request.json
    recurso_nombre = data['recurso']
    cantidad = data.get('cantidad', 1)
    
    # Buscar el nombre correcto del recurso (case-insensitive)
    nombre_correcto = None
    for nombre in simulador.mercado.recursos.keys():
        if nombre.lower() == recurso_nombre.lower():
            nombre_correcto = nombre
            break
    
    if not nombre_correcto:
        return jsonify({'error': 'Recurso no encontrado', 'exito': False}), 404
    
    exito = simulador.jugador.vender_recurso(nombre_correcto, cantidad, simulador.mercado)
    
    return jsonify({
        'exito': exito,
        'dinero': simulador.jugador.dinero,
        'inventario': simulador.jugador.inventario,
        'capacidad_usada': simulador.jugador.capacidad_usada,
        'mensaje': f'Vendiste {cantidad}x {recurso_nombre}' if exito else 'No se pudo completar la venta'
    })

@app.route('/api/simular_turno', methods=['POST'])
def simular_turno():
    """Avanza un turno"""
    simulador.mercado.simular_mercado()
    simulador.turno += 1
    return jsonify({'turno': simulador.turno, 'mensaje': 'Mercado actualizado'})

# ============================================
# API INVENTARIO
# ============================================

@app.route('/api/jugador', methods=['GET'])
def obtener_jugador():
    """Estado del jugador"""
    # Calcular valor de recursos
    valor_recursos = 0
    for nombre, cantidad in simulador.jugador.inventario.items():
        if nombre in simulador.mercado.recursos:
            valor_recursos += simulador.mercado.recursos[nombre].precio_actual * cantidad
    
    return jsonify({
        'nombre': simulador.jugador.nombre,
        'dinero': simulador.jugador.dinero,
        'inventario': simulador.jugador.inventario,
        'capacidad_max': simulador.jugador.capacidad_max,
        'capacidad_usada': simulador.jugador.capacidad_usada,
        'valor_recursos': round(valor_recursos, 2),
        'patrimonio_total': round(simulador.jugador.dinero + valor_recursos, 2)
    })

@app.route('/api/optimizar_inventario', methods=['GET'])
def optimizar_inventario():
    """Optimiza inventario con DP"""
    recomendaciones = simulador.jugador.optimizar_inventario_mochila(simulador.mercado)
    
    resultado = []
    for recurso, cantidad in recomendaciones:
        resultado.append({
            'nombre': recurso.nombre,
            'cantidad': cantidad,
            'precio': recurso.precio_actual,
            'peso': recurso.peso,
            'costo_total': round(recurso.precio_actual * cantidad, 2),
            'peso_total': recurso.peso * cantidad
        })
    
    return jsonify(resultado)

@app.route('/api/estadisticas', methods=['GET'])
def obtener_estadisticas():
    """Obtiene estadísticas del mercado"""
    recursos = list(simulador.mercado.recursos.values())
    
    # Calcular estadísticas generales
    precio_promedio = sum(r.precio_actual for r in recursos) / len(recursos)
    demanda_promedio = sum(r.demanda for r in recursos) / len(recursos)
    oferta_promedio = sum(r.oferta for r in recursos) / len(recursos)
    
    # Recursos más valiosos
    mas_valiosos = sorted(recursos, key=lambda r: r.precio_actual, reverse=True)[:5]
    
    # Recursos con mayor demanda
    mayor_demanda = sorted(recursos, key=lambda r: r.demanda, reverse=True)[:5]
    
    return jsonify({
        'precio_promedio': round(precio_promedio, 2),
        'demanda_promedio': round(demanda_promedio, 2),
        'oferta_promedio': round(oferta_promedio, 2),
        'turno_actual': simulador.turno,
        'recursos_mas_valiosos': [
            {'nombre': r.nombre, 'precio': round(r.precio_actual, 2)} 
            for r in mas_valiosos
        ],
        'recursos_mayor_demanda': [
            {'nombre': r.nombre, 'demanda': r.demanda} 
            for r in mayor_demanda
        ]
    })
# ============================================
# API RUTAS
# ============================================

@app.route('/api/calcular_ruta', methods=['POST'])
def calcular_ruta():
    """Calcula ruta óptima con Dijkstra"""
    data = request.json
    origen = data['origen']
    destino = data['destino']
    
    print(f"🔍 Calculando ruta: {origen} → {destino}")
    print(f"📦 Inventario actual: {simulador.jugador.inventario}")
    
    distancia, costo, camino = simulador.grafo.dijkstra(origen, destino)
    
    if camino:
        # Calcular tiempo (1 minuto por cada 10 km)
        tiempo = round(distancia / 10)
        
        # Calcular ganancia basada en el INVENTARIO del jugador
        ganancia = 0
        detalles_ganancia = []
        
        print(f"💰 Analizando recursos para vender en {destino}...")
        
        # Revisar cada recurso en el inventario
        for nombre_recurso, cantidad in simulador.jugador.inventario.items():
            print(f"  🔎 Revisando: {nombre_recurso} x{cantidad}")
            
            # Buscar recurso (case-insensitive)
            recurso = None
            for nombre, r in simulador.mercado.recursos.items():
                if nombre.lower() == nombre_recurso.lower():
                    recurso = r
                    break
            
            if recurso:
                print(f"    📍 Ubicación del recurso: {recurso.ubicacion}")
                print(f"    🎯 Destino: {destino}")
                
                # Si el recurso se vende bien en el destino (ubicación coincide)
                if recurso.ubicacion.lower() == destino.lower():
                    # Precio de venta con 10% de comisión
                    precio_venta = recurso.precio_actual * 0.9
                    ganancia_recurso = precio_venta * cantidad
                    ganancia += ganancia_recurso
                    
                    detalles_ganancia.append({
                        'recurso': nombre_recurso,
                        'cantidad': cantidad,
                        'precio_unitario': round(precio_venta, 2),
                        'ganancia_total': round(ganancia_recurso, 2)
                    })
                    
                    print(f"    ✅ VENDIBLE: ${round(ganancia_recurso, 2)}")
                else:
                    print(f"    ❌ No vendible en {destino}")
            else:
                print(f"    ⚠️ Recurso no encontrado en mercado")
        
        # Restar el costo del viaje
        ganancia_neta = round(ganancia - costo, 2)
        
        print(f"📊 Ganancia bruta: ${ganancia}")
        print(f"💸 Costo viaje: ${costo}")
        print(f"💰 Ganancia neta: ${ganancia_neta}")
        
        # Determinar nivel de riesgo
        if distancia < 200:
            riesgo = "Bajo"
        elif distancia < 300:
            riesgo = "Medio"
        else:
            riesgo = "Alto"
        
        return jsonify({
            'exito': True,
            'distancia': distancia,
            'costo': costo,
            'camino': camino,
            'tiempo': tiempo,
            'riesgo': riesgo,
            'ganancia_bruta': round(ganancia, 2),
            'ganancia_neta': ganancia_neta,
            'recursos_vendibles': detalles_ganancia
        })
    else:
        return jsonify({
            'exito': False,
            'mensaje': 'No hay ruta disponible'
        }), 404

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 SERVIDOR MARKET KEYO")
    print("="*60)
    print("📍 Dashboard: http://localhost:5000")
    print("📍 Mercado:   http://localhost:5000/market.html")
    print("📍 Mapa:      http://localhost:5000/servers.html")
    print("📍 Inventario: http://localhost:5000/inventory.html")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5000, host='0.0.0.0')