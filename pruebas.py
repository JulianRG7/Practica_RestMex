#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análisis Geográfico Rest-Mex 2025 con Folium
Técnico en Visualización y Análisis de Datos
"""

import pandas as pd
import folium
from folium import plugins
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

class RestMexGeoAnalyzer:
    """
    Analizador geográfico para el dataset Rest-Mex 2025
    Genera mapas interactivos con Folium por polaridad
    """
    
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.df = None
        self.processed_data = {}
        
        # Mapeo de nombres del dataset a nombres estándar
        self.state_mapping = {
            'QuintanaRoo': 'Quintana Roo',
            'Estado_de_Mexico': 'Estado de Mexico', 
            'Baja_CaliforniaSur': 'Baja California Sur',
            'San_Luis_Potosi': 'San Luis Potosi',
            'Michoacan': 'Michoacan',
            'Queretaro': 'Queretaro',
            'Yucatan': 'Yucatan',
            'Nayarit': 'Nayarit',
            'Chiapas': 'Chiapas',
            'Chihuahua': 'Chihuahua',
            'Guerrero': 'Guerrero',
            'Puebla': 'Puebla',
            'Jalisco': 'Jalisco',
            'Coahuila': 'Coahuila',
            'Veracruz': 'Veracruz',
            'Hidalgo': 'Hidalgo',
            'Morelos': 'Morelos',
            'Oaxaca': 'Oaxaca',
            'Guanajuato': 'Guanajuato'
        }
        
        # Coordenadas de capitales estatales (lat, lng)
        self.state_coordinates = {
            'Quintana Roo': [21.1619, -86.8515],
            'Estado de Mexico': [19.4326, -99.6795],
            'Baja California Sur': [24.1442, -110.3005],
            'San Luis Potosi': [22.1565, -100.9855],
            'Michoacan': [19.7007, -101.1884],
            'Queretaro': [20.5888, -100.3899],
            'Yucatan': [20.9674, -89.5926],
            'Nayarit': [21.7514, -104.8455],
            'Chiapas': [16.7569, -93.1292],
            'Chihuahua': [28.6353, -106.0889],
            'Guerrero': [17.4391, -99.5451],
            'Puebla': [19.0414, -98.2063],
            'Jalisco': [20.6597, -103.3496],
            'Coahuila': [25.4232, -101.0053],
            'Veracruz': [19.1738, -96.1342],
            'Hidalgo': [20.0911, -98.7624],
            'Morelos': [18.6813, -99.1013],
            'Oaxaca': [17.0732, -96.7266],
            'Guanajuato': [21.0190, -101.2574]
        }
        
        # Colores por polaridad
        self.polarity_colors = {
            1: '#DC2626',  # Rojo intenso - Muy Negativa
            2: '#F87171',  # Rojo claro - Negativa  
            3: '#6B7280',  # Gris - Neutral
            4: '#34D399',  # Verde claro - Positiva
            5: '#10B981'   # Verde intenso - Muy Positiva
        }
        
        self.polarity_labels = {
            1: 'Muy Negativa',
            2: 'Negativa',
            3: 'Neutral', 
            4: 'Positiva',
            5: 'Muy Positiva'
        }
    
    def load_and_validate_data(self):
        """
        Carga y valida el dataset CSV
        """
        try:
            print("📊 Cargando dataset Rest-Mex 2025...")
            self.df = pd.read_csv(self.csv_path, encoding='utf-8')
            
            # Validar columnas requeridas
            required_columns = ['Title', 'Review', 'Polarity', 'Town', 'Region', 'Type']
            missing_columns = [col for col in required_columns if col not in self.df.columns]
            
            if missing_columns:
                raise ValueError(f"❌ Columnas faltantes: {missing_columns}")
            
            # Filtrar datos válidos
            initial_count = len(self.df)
            self.df = self.df[
                (self.df['Region'].notna()) & 
                (self.df['Polarity'].notna()) &
                (self.df['Polarity'].between(1, 5))
            ]
            
            print(f"✅ Dataset cargado exitosamente:")
            print(f"   - Registros totales: {initial_count:,}")
            print(f"   - Registros válidos: {len(self.df):,}")
            print(f"   - Estados únicos: {self.df['Region'].nunique()}")
            print(f"   - Rango de polaridad: {self.df['Polarity'].min()}-{self.df['Polarity'].max()}")
            
            # Mostrar distribución por estado
            print("\n📍 Distribución por estado:")
            state_counts = self.df['Region'].value_counts()
            for state, count in state_counts.head(10).items():
                print(f"   - {state}: {count:,} reseñas")
            
            return True
            
        except Exception as e:
            print(f"❌ Error al cargar el dataset: {str(e)}")
            return False
    
    def process_data_by_polarity(self, polarity):
        """
        Procesa los datos para una polaridad específica
        """
        # Filtrar por polaridad
        polarity_data = self.df[self.df['Polarity'] == polarity]
        
        # Agrupar por región
        region_counts = polarity_data['Region'].value_counts().to_dict()
        
        # Procesar para cada estado
        processed = {}
        max_count = 0
        
        for region, count in region_counts.items():
            standard_name = self.state_mapping.get(region, region)
            coordinates = self.state_coordinates.get(standard_name)
            
            if coordinates:
                # Obtener estadísticas completas del estado
                state_data = self.df[self.df['Region'] == region]
                total_reviews = len(state_data)
                polarity_distribution = state_data['Polarity'].value_counts().to_dict()
                
                processed[standard_name] = {
                    'original_name': region,
                    'coordinates': coordinates,
                    'count': count,
                    'total_reviews': total_reviews,
                    'percentage': (count / total_reviews * 100) if total_reviews > 0 else 0,
                    'polarity_distribution': polarity_distribution
                }
                
                max_count = max(max_count, count)
        
        return processed, max_count
    
    def create_folium_map(self, polarity, save_path=None):
        """
        Crea un mapa interactivo con Folium para una polaridad específica
        """
        if self.df is None:
            print("❌ Primero debes cargar los datos con load_and_validate_data()")
            return None
        
        print(f"\n🗺️ Generando mapa para Polaridad {polarity} ({self.polarity_labels[polarity]})...")
        
        # Procesar datos
        data, max_count = self.process_data_by_polarity(polarity)
        
        if not data:
            print("❌ No se encontraron datos para esta polaridad")
            return None
        
        # Crear mapa centrado en México
        mexico_center = [23.6345, -102.5528]
        m = folium.Map(
            location=mexico_center,
            zoom_start=5,
            tiles='OpenStreetMap',
            prefer_canvas=True
        )
        
        # Configurar límites del mapa
        m.fit_bounds([
            [14.5388, -118.4662],  # Southwest
            [32.7186, -86.7104]    # Northeast
        ])
        
        # Color para esta polaridad
        color = self.polarity_colors[polarity]
        
        # Añadir marcadores para cada estado
        for state_name, state_data in data.items():
            lat, lng = state_data['coordinates']
            count = state_data['count']
            total = state_data['total_reviews']
            percentage = state_data['percentage']
            
            # Calcular tamaño del marcador (escala logarítmica)
            if max_count > 0:
                intensity = np.log(count + 1) / np.log(max_count + 1)
                radius = 10 + (intensity * 25)
                opacity = 0.4 + (intensity * 0.5)
            else:
                radius = 10
                opacity = 0.4
            
            # Crear popup con información detallada
            popup_html = f"""
            <div style="font-family: Arial, sans-serif; width: 250px;">
                <h3 style="margin: 0 0 10px 0; color: #1f2937; border-bottom: 2px solid {color}; padding-bottom: 5px;">
                    {state_name}
                </h3>
                <div style="margin: 5px 0;">
                    <strong>Polaridad {polarity} ({self.polarity_labels[polarity]}):</strong><br>
                    <span style="color: {color}; font-size: 18px; font-weight: bold;">
                        {count:,} reseñas
                    </span>
                </div>
                <div style="margin: 5px 0;">
                    <strong>Total del estado:</strong> {total:,} reseñas
                </div>
                <div style="margin: 5px 0;">
                    <strong>Porcentaje:</strong> {percentage:.1f}%
                </div>
                <hr style="margin: 10px 0; border: none; border-top: 1px solid #e5e7eb;">
                <div style="font-size: 12px; color: #6b7280;">
                    <strong>Distribución por polaridad:</strong><br>
            """
            
            # Añadir distribución de polaridad
            for pol in range(1, 6):
                pol_count = state_data['polarity_distribution'].get(pol, 0)
                pol_color = self.polarity_colors[pol]
                popup_html += f'<span style="color: {pol_color};">●</span> {pol}: {pol_count:,}<br>'
            
            popup_html += '</div></div>'
            
            # Añadir marcador circular
            folium.CircleMarker(
                location=[lat, lng],
                radius=radius,
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"{state_name}: {count:,} reseñas",
                color='white',
                weight=2,
                fillColor=color,
                fillOpacity=opacity,
            ).add_to(m)
            
            # Añadir etiqueta del estado
            folium.Marker(
                location=[lat, lng],
                icon=folium.DivIcon(
                    html=f'<div style="font-size: 10px; color: #374151; font-weight: bold; text-shadow: 1px 1px 2px white;">{state_name}</div>',
                    class_name="state-label"
                )
            ).add_to(m)
        
        # Añadir leyenda personalizada
        legend_html = f'''
        <div style="position: fixed; 
                    top: 10px; right: 10px; width: 200px; height: auto; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px; border-radius: 5px;
                    box-shadow: 0 0 15px rgba(0,0,0,0.2);">
            <h4 style="margin: 0 0 10px 0;">Rest-Mex 2025</h4>
            <p style="margin: 5px 0;"><strong>Polaridad {polarity}</strong></p>
            <p style="margin: 5px 0; color: {color};">{self.polarity_labels[polarity]}</p>
            <hr style="margin: 10px 0;">
            <p style="margin: 5px 0; font-size: 12px;">
                <span style="color: {color};">●</span> Tamaño = Cantidad de reseñas<br>
                <span style="color: {color};">●</span> Intensidad = Concentración relativa<br>
                <span style="color: {color};">●</span> Total: {sum(d['count'] for d in data.values()):,} reseñas
            </p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Añadir título al mapa
        title_html = f'''
        <h2 style="position: absolute; top: 10px; left: 50%; transform: translateX(-50%);
                   background-color: rgba(255,255,255,0.8); padding: 10px; border-radius: 5px;
                   margin: 0; z-index: 1000; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">
            Mapa México - Polaridad {polarity} ({self.polarity_labels[polarity]})
        </h2>
        '''
        m.get_root().html.add_child(folium.Element(title_html))
        
        # Guardar mapa si se especifica ruta
        if save_path:
            m.save(save_path)
            print(f"✅ Mapa guardado en: {save_path}")
        
        print(f"✅ Mapa generado exitosamente para {len(data)} estados")
        
        return m
    
    def create_all_polarity_maps(self, output_dir="mapas_restmex"):
        """
        Genera mapas para todas las polaridades (1-5)
        """
        import os
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"📁 Directorio creado: {output_dir}")
        
        maps_created = []
        
        for polarity in range(1, 6):
            filename = f"{output_dir}/mapa_polaridad_{polarity}_{self.polarity_labels[polarity].lower().replace(' ', '_')}.html"
            map_obj = self.create_folium_map(polarity, filename)
            
            if map_obj:
                maps_created.append(filename)
        
        print(f"\n🎉 ¡Análisis completo! Se generaron {len(maps_created)} mapas:")
        for i, map_path in enumerate(maps_created, 1):
            print(f"   {i}. {map_path}")
        
        return maps_created
    
    def generate_summary_statistics(self):
        """
        Genera estadísticas resumidas del dataset
        """
        if self.df is None:
            print("❌ Primero debes cargar los datos")
            return
        
        print("\n📈 RESUMEN ESTADÍSTICO REST-MEX 2025")
        print("=" * 50)
        
        # Estadísticas generales
        print(f"📊 Total de reseñas: {len(self.df):,}")
        print(f"📍 Estados únicos: {self.df['Region'].nunique()}")
        print(f"🏢 Tipos de establecimiento: {self.df['Type'].nunique()}")
        
        # Distribución por polaridad
        print(f"\n🎯 DISTRIBUCIÓN POR POLARIDAD:")
        polarity_dist = self.df['Polarity'].value_counts().sort_index()
        for pol, count in polarity_dist.items():
            percentage = (count / len(self.df)) * 100
            print(f"   {pol} ({self.polarity_labels[pol]}): {count:,} ({percentage:.1f}%)")
        
        # Top estados
        print(f"\n🏆 TOP 10 ESTADOS (por total de reseñas):")
        top_states = self.df['Region'].value_counts().head(10)
        for i, (state, count) in enumerate(top_states.items(), 1):
            standard_name = self.state_mapping.get(state, state)
            print(f"   {i:2d}. {standard_name}: {count:,}")
        
        # Distribución por tipo
        print(f"\n🏪 TOP 5 TIPOS DE ESTABLECIMIENTO:")
        top_types = self.df['Type'].value_counts().head(5)
        for i, (type_name, count) in enumerate(top_types.items(), 1):
            print(f"   {i}. {type_name}: {count:,}")
    
    def create_interactive_dashboard(self, save_path="dashboard_restmex.html"):
        """
        Crea un dashboard interactivo con selector de polaridad
        """
        # Crear página HTML con JavaScript para selector de polaridad
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Dashboard Rest-Mex 2025 - Análisis por Polaridad</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f8fafc;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .controls {{
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }}
        .polarity-btn {{
            padding: 10px 20px;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-weight: bold;
            font-size: 14px;
            transition: all 0.3s ease;
            color: white;
        }}
        .polarity-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }}
        .map-container {{
            width: 100%;
            height: 70vh;
            border: 2px solid #e5e7eb;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        iframe {{
            width: 100%;
            height: 100%;
            border: none;
        }}
        .stats {{
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 20px;
            flex-wrap: wrap;
        }}
        .stat-card {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            min-width: 120px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .stat-number {{
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .stat-label {{
            font-size: 12px;
            color: #6b7280;
            text-transform: uppercase;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🗺️ Dashboard Rest-Mex 2025</h1>
        <p>Análisis geográfico interactivo por polaridad de reseñas turísticas</p>
    </div>
    
    <div class="controls">
        <button class="polarity-btn" style="background-color: #DC2626;" onclick="loadMap(1)">
            1 - Muy Negativa
        </button>
        <button class="polarity-btn" style="background-color: #F87171;" onclick="loadMap(2)">
            2 - Negativa
        </button>
        <button class="polarity-btn" style="background-color: #6B7280;" onclick="loadMap(3)">
            3 - Neutral
        </button>
        <button class="polarity-btn" style="background-color: #34D399;" onclick="loadMap(4)">
            4 - Positiva
        </button>
        <button class="polarity-btn" style="background-color: #10B981;" onclick="loadMap(5)">
            5 - Muy Positiva
        </button>
    </div>
    
    <div class="map-container">
        <iframe id="mapFrame" src="mapa_default.html"></iframe>
        <div id="loadingMsg" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center; color: #6b7280; display: none;">
            <h3>🔄 Cargando mapa...</h3>
            <p>Cambiando a nueva polaridad</p>
        </div>
        <div id="errorMsg" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center; color: #dc2626; display: none;">
            <h3>⚠️ Error al cargar mapa</h3>
            <p>Ejecuta primero: <code>python rest_mex_analysis.py</code></p>
        </div>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <div class="stat-number">{len(self.df):,}</div>
            <div class="stat-label">Total Reseñas</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{self.df['Region'].nunique()}</div>
            <div class="stat-label">Estados</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{self.df['Type'].nunique()}</div>
            <div class="stat-label">Tipos</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">1-5</div>
            <div class="stat-label">Polaridades</div>
        </div>
    </div>
    
    <script>
        function loadMap(polarity) {{
            const polarityNames = {{
                1: 'muy_negativa',
                2: 'negativa', 
                3: 'neutral',
                4: 'positiva',
                5: 'muy_positiva'
            }};
            
            const filename = `mapa_polaridad_${{polarity}}_${{polarityNames[polarity]}}.html`;
            document.getElementById('mapFrame').src = filename;
            
            // Actualizar botones
            document.querySelectorAll('.polarity-btn').forEach(btn => {{
                btn.style.opacity = '0.6';
                btn.style.transform = 'scale(1)';
            }});
            
            event.target.style.opacity = '1';
            event.target.style.transform = 'scale(1.05)';
        }}
        
        // Cargar mapa neutral por defecto
        window.onload = function() {{
            document.querySelectorAll('.polarity-btn')[2].click();
        }};
    </script>
</body>
</html>
"""
        
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Dashboard interactivo creado: {save_path}")
        return save_path

def main():
    """
    Función principal para ejecutar el análisis
    """
    print("🚀 INICIANDO ANÁLISIS GEOGRÁFICO REST-MEX 2025")
    print("=" * 60)
    
    # Especificar ruta del CSV (cambiar por la ruta real)
    # ⚠️ CAMBIAR POR LA RUTA REAL DE TU ARCHIVO CSV
    csv_path = "Rest-Mex_2025_train.csv"
    
    # Si el archivo no existe en el directorio actual, intentar rutas comunes
    import os
    possible_paths = [
        csv_path,
        f"data/{csv_path}",
        f"datasets/{csv_path}",
        f"../data/{csv_path}",
        f"../../{csv_path}"
    ]
    
    csv_found = None
    for path in possible_paths:
        if os.path.exists(path):
            csv_found = path
            break
    
    if not csv_found:
        print(f"❌ ARCHIVO CSV NO ENCONTRADO")
        print(f"📁 Rutas intentadas:")
        for path in possible_paths:
            print(f"   - {os.path.abspath(path)}")
        print(f"\n💡 SOLUCIÓN:")
        print(f"   1. Coloca el archivo 'Rest-Mex_2025_train.csv' en el mismo directorio que este script")
        print(f"   2. O cambia la variable csv_path con la ruta correcta")
        return
    
    csv_path = csv_found
    print(f"✅ Archivo encontrado: {os.path.abspath(csv_path)}")
    
    # Crear analizador
    analyzer = RestMexGeoAnalyzer(csv_path)
    
    # Cargar y validar datos
    if not analyzer.load_and_validate_data():
        return
    
    # Generar estadísticas
    analyzer.generate_summary_statistics()
    
    # Crear mapas para todas las polaridades
    print(f"\n🗺️ GENERANDO MAPAS INTERACTIVOS...")
    maps_created = analyzer.create_all_polarity_maps()
    
    # Crear dashboard interactivo
    print(f"\n📊 CREANDO DASHBOARD INTERACTIVO...")
    dashboard_path = analyzer.create_interactive_dashboard()
    
    # Crear un mapa por defecto para cargar automáticamente
    print(f"\n🎯 GENERANDO MAPA POR DEFECTO (Polaridad 3 - Neutral)...")
    default_map = analyzer.create_folium_map(3, "mapa_default.html")
    
    print(f"\n🎉 ¡ANÁLISIS COMPLETO!")
    print(f"📁 Archivos generados:")
    print(f"   • Dashboard principal: {dashboard_path}")
    print(f"   • Mapa por defecto: mapa_default.html")
    for map_path in maps_created:
        print(f"   • {map_path}")
    
    print(f"\n💡 INSTRUCCIONES:")
    print(f"   1. Abre '{dashboard_path}' en tu navegador")
    print(f"   2. O abre 'mapa_default.html' para ver el mapa neutral directamente")
    print(f"   3. Usa los botones de polaridad para cambiar entre mapas")
    print(f"   4. Haz clic en los círculos para ver detalles de cada estado")

if __name__ == "__main__":
    main()