import React, { useState, useEffect, useRef } from 'react';
import { Upload, Filter, MapPin, BarChart3, FileText, AlertCircle, CheckCircle, TrendingUp } from 'lucide-react';
import * as Papa from 'papaparse';

const FoliumMexicoMap = () => {
  const [csvData, setCsvData] = useState([]);
  const [processedData, setProcessedData] = useState({});
  const [selectedPolarity, setSelectedPolarity] = useState(3);
  const [fileLoaded, setFileLoaded] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [stats, setStats] = useState({ totalStates: 0, totalReviews: 0, maxCount: 0 });
  const mapRef = useRef(null);

  // Mapeo de nombres del dataset a nombres estándar
  const stateMapping = {
    'QuintanaRoo': 'Quintana Roo',
    'Estado_de_Mexico': 'Estado de México', 
    'Baja_CaliforniaSur': 'Baja California Sur',
    'San_Luis_Potosi': 'San Luis Potosí',
    'Michoacan': 'Michoacán',
    'Queretaro': 'Querétaro',
    'Yucatan': 'Yucatán',
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
  };

  // Coordenadas de capitales estatales (lat, lng)
  const stateCoordinates = {
    'Quintana Roo': [21.1619, -86.8515],
    'Estado de México': [19.4326, -99.6795],
    'Baja California Sur': [24.1442, -110.3005],
    'San Luis Potosí': [22.1565, -100.9855],
    'Michoacán': [19.7007, -101.1884],
    'Querétaro': [20.5888, -100.3899],
    'Yucatán': [20.9674, -89.5926],
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
  };

  // Colores por polaridad
  const polarityColors = {
    1: '#DC2626', // Rojo intenso - Muy Negativa
    2: '#F87171', // Rojo claro - Negativa  
    3: '#6B7280', // Gris - Neutral
    4: '#34D399', // Verde claro - Positiva
    5: '#10B981'  // Verde intenso - Muy Positiva
  };

  const polarityLabels = {
    1: 'Muy Negativa',
    2: 'Negativa',
    3: 'Neutral', 
    4: 'Positiva',
    5: 'Muy Positiva'
  };

  // Manejar carga de CSV
  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setLoading(true);
    setError('');

    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      dynamicTyping: true,
      complete: (results) => {
        try {
          // Validar columnas requeridas
          const requiredColumns = ['Title', 'Review', 'Polarity', 'Town', 'Region', 'Type'];
          const headers = Object.keys(results.data[0] || {});
          const missingColumns = requiredColumns.filter(col => !headers.includes(col));
          
          if (missingColumns.length > 0) {
            throw new Error(`Columnas faltantes: ${missingColumns.join(', ')}`);
          }

          // Filtrar filas válidas
          const validData = results.data.filter(row => 
            row.Region && 
            row.Polarity && 
            row.Polarity >= 1 && 
            row.Polarity <= 5
          );

          if (validData.length === 0) {
            throw new Error('No se encontraron datos válidos en el CSV');
          }

          setCsvData(validData);
          setFileLoaded(true);
          console.log(`✅ CSV cargado: ${validData.length} registros válidos`);
          
        } catch (err) {
          setError(err.message);
          console.error('❌ Error al procesar CSV:', err);
        } finally {
          setLoading(false);
        }
      },
      error: (error) => {
        setError(`Error al leer el archivo: ${error.message}`);
        setLoading(false);
      }
    });
  };

  // Procesar datos cuando cambia la polaridad o se carga el CSV
  useEffect(() => {
    if (csvData.length > 0) {
      processData();
    }
  }, [csvData, selectedPolarity]);

  const processData = () => {
    try {
      // Agrupar por Region y Polarity
      const grouped = csvData.reduce((acc, row) => {
        const region = row.Region;
        const polarity = row.Polarity;
        
        if (!acc[region]) {
          acc[region] = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, total: 0 };
        }
        
        acc[region][polarity] = (acc[region][polarity] || 0) + 1;
        acc[region].total += 1;
        
        return acc;
      }, {});

      // Procesar para la polaridad seleccionada
      const processedForPolarity = {};
      let maxCount = 0;
      let totalReviews = 0;

      Object.entries(grouped).forEach(([region, polarityData]) => {
        const standardName = stateMapping[region] || region;
        const count = polarityData[selectedPolarity] || 0;
        const coordinates = stateCoordinates[standardName];
        
        if (coordinates) {
          processedForPolarity[standardName] = {
            originalName: region,
            count: count,
            total: polarityData.total,
            percentage: polarityData.total > 0 ? ((count / polarityData.total) * 100).toFixed(1) : '0.0',
            coordinates: coordinates,
            allPolarities: { ...polarityData }
          };
          
          maxCount = Math.max(maxCount, count);
          totalReviews += count;
        }
      });

      setProcessedData(processedForPolarity);
      setStats({
        totalStates: Object.keys(processedForPolarity).length,
        totalReviews: totalReviews,
        maxCount: maxCount
      });

      // Generar mapa Folium
      generateFoliumMap(processedForPolarity, maxCount);

    } catch (err) {
      setError(`Error al procesar datos: ${err.message}`);
    }
  };

  // Generar código HTML del mapa Folium
  const generateFoliumMap = (data, maxCount) => {
    const centerLat = 23.6345;
    const centerLng = -102.5528;
    
    // Generar HTML del mapa Folium
    const mapHTML = `
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Mapa México - Rest-Mex 2025</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css"/>
    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
    <style>
        body { margin: 0; padding: 0; }
        #map { height: 100vh; width: 100%; }
        .custom-popup {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        .popup-title {
            font-weight: bold;
            font-size: 16px;
            color: #1f2937;
            margin-bottom: 8px;
        }
        .popup-stat {
            margin: 4px 0;
            font-size: 14px;
        }
        .popup-highlight {
            color: ${polarityColors[selectedPolarity]};
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div id="map"></div>
    <script>
        // Crear mapa centrado en México
        var map = L.map('map').setView([${centerLat}, ${centerLng}], 5);
        
        // Agregar tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors | Rest-Mex 2025 Analysis',
            maxZoom: 18
        }).addTo(map);

        ${Object.entries(data).map(([stateName, stateData]) => {
          const intensity = maxCount > 0 ? stateData.count / maxCount : 0;
          const opacity = 0.3 + (intensity * 0.7);
          const radius = 10 + (intensity * 20);
          
          return `
        // Marcador para ${stateName}
        var marker_${stateName.replace(/\s+/g, '_')} = L.circleMarker([${stateData.coordinates[0]}, ${stateData.coordinates[1]}], {
            radius: ${radius},
            fillColor: '${polarityColors[selectedPolarity]}',
            color: '#ffffff',
            weight: 2,
            opacity: 1,
            fillOpacity: ${opacity}
        }).addTo(map);
        
        marker_${stateName.replace(/\s+/g, '_')}.bindPopup(\`
            <div class="custom-popup">
                <div class="popup-title">${stateName}</div>
                <div class="popup-stat">Polaridad ${selectedPolarity} (${polarityLabels[selectedPolarity]}): <span class="popup-highlight">${stateData.count.toLocaleString()}</span></div>
                <div class="popup-stat">Total del estado: ${stateData.total.toLocaleString()}</div>
                <div class="popup-stat">Porcentaje: ${stateData.percentage}%</div>
                <hr style="margin: 8px 0; border: none; border-top: 1px solid #e5e7eb;">
                <div style="font-size: 12px; color: #6b7280;">
                    <div>Distribución por polaridad:</div>
                    <div>1: ${stateData.allPolarities[1] || 0} | 2: ${stateData.allPolarities[2] || 0} | 3: ${stateData.allPolarities[3] || 0} | 4: ${stateData.allPolarities[4] || 0} | 5: ${stateData.allPolarities[5] || 0}</div>
                </div>
            </div>
        \`);`;
        }).join('\n')}

        // Agregar leyenda
        var legend = L.control({position: 'bottomright'});
        legend.onAdd = function (map) {
            var div = L.DomUtil.create('div', 'info legend');
            div.innerHTML = \`
                <div style="background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
                    <h4 style="margin: 0 0 10px 0; font-size: 14px; color: #1f2937;">Polaridad ${selectedPolarity}: ${polarityLabels[selectedPolarity]}</h4>
                    <div style="font-size: 12px; color: #6b7280;">
                        <div>• Tamaño del círculo = Cantidad de reseñas</div>
                        <div>• Intensidad del color = Concentración relativa</div>
                        <div style="margin-top: 8px;">
                            <span style="color: ${polarityColors[selectedPolarity]};">●</span> 
                            ${stats.totalReviews.toLocaleString()} reseñas totales
                        </div>
                    </div>
                </div>
            \`;
            return div;
        };
        legend.addTo(map);

        // Control de zoom personalizado
        map.setMaxBounds([
            [10.0, -120.0], // Southwest
            [35.0, -80.0]   // Northeast
        ]);
    </script>
</body>
</html>`;

    // Actualizar iframe
    if (mapRef.current) {
      mapRef.current.srcdoc = mapHTML;
    }
  };

  // Datos para la tabla
  const tableData = Object.entries(processedData)
    .sort(([,a], [,b]) => b.count - a.count);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h1 className="text-3xl font-bold text-gray-800 flex items-center gap-3">
            <MapPin className="text-blue-600" />
            Mapa Folium México - Rest-Mex 2025
          </h1>
          <p className="text-gray-600 mt-2">
            Análisis geográfico interactivo con datos reales del dataset
          </p>
        </div>

        {/* Panel de Control */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <Upload className="text-blue-600" />
            Carga de Dataset y Configuración
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Carga de archivo */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <FileText className="inline w-4 h-4 mr-1" />
                Cargar Rest-Mex CSV
              </label>
              <input
                type="file"
                accept=".csv"
                onChange={handleFileUpload}
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
              />
              <div className="mt-2 flex items-center text-sm">
                {fileLoaded ? (
                  <><CheckCircle className="w-4 h-4 text-green-600 mr-1" />
                    <span className="text-green-600">CSV cargado exitosamente</span></>
                ) : (
                  <><AlertCircle className="w-4 h-4 text-gray-400 mr-1" />
                    <span className="text-gray-500">Esperando archivo CSV...</span></>
                )}
              </div>
            </div>

            {/* Selector de Polaridad */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Filter className="inline w-4 h-4 mr-1" />
                Seleccionar Polaridad
              </label>
              <select
                value={selectedPolarity}
                onChange={(e) => setSelectedPolarity(parseInt(e.target.value))}
                disabled={!fileLoaded}
                className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:bg-gray-100"
              >
                {[1, 2, 3, 4, 5].map(pol => (
                  <option key={pol} value={pol}>
                    {pol} - {polarityLabels[pol]}
                  </option>
                ))}
              </select>
              {fileLoaded && (
                <div className="mt-2 text-xs" style={{ color: polarityColors[selectedPolarity] }}>
                  ● {stats.totalReviews.toLocaleString()} reseñas con esta polaridad
                </div>
              )}
            </div>

            {/* Información del dataset */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <BarChart3 className="inline w-4 h-4 mr-1" />
                Estadísticas del Dataset
              </label>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Estados:</span>
                  <span className="font-semibold">{stats.totalStates}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Registros CSV:</span>
                  <span className="font-semibold">{csvData.length.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Max por estado:</span>
                  <span className="font-semibold">{stats.maxCount.toLocaleString()}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Error Display */}
          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
              <div className="flex items-start">
                <AlertCircle className="w-5 h-5 text-red-600 mr-2 mt-0.5" />
                <div>
                  <h3 className="text-sm font-medium text-red-800">Error al procesar el archivo</h3>
                  <p className="text-sm text-red-700 mt-1">{error}</p>
                </div>
              </div>
            </div>
          )}

          {/* Loading */}
          {loading && (
            <div className="mt-4 text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="text-sm text-gray-600 mt-2">Procesando CSV...</p>
            </div>
          )}
        </div>

        {/* Mapa y Estadísticas */}
        {fileLoaded && (
          <>
            {/* KPIs */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-600 text-sm">Estados Activos</p>
                    <p className="text-2xl font-bold text-gray-800">{stats.totalStates}</p>
                  </div>
                  <MapPin className="h-8 w-8 text-blue-600" />
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-600 text-sm">Polaridad Actual</p>
                    <p className="text-lg font-bold" style={{ color: polarityColors[selectedPolarity] }}>
                      {selectedPolarity} - {polarityLabels[selectedPolarity]}
                    </p>
                  </div>
                  <Filter className="h-8 w-8" style={{ color: polarityColors[selectedPolarity] }} />
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-600 text-sm">Total Reseñas</p>
                    <p className="text-2xl font-bold text-gray-800">{stats.totalReviews.toLocaleString()}</p>
                  </div>
                  <TrendingUp className="h-8 w-8 text-green-600" />
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-600 text-sm">Estado Líder</p>
                    <p className="text-sm font-bold text-gray-800">
                      {tableData.length > 0 ? tableData[0][0] : 'N/A'}
                    </p>
                    <p className="text-xs text-gray-500">
                      {tableData.length > 0 ? tableData[0][1].count.toLocaleString() : '0'} reseñas
                    </p>
                  </div>
                  <BarChart3 className="h-8 w-8 text-purple-600" />
                </div>
              </div>
            </div>

            {/* Mapa Folium */}
            <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
              <h3 className="text-lg font-semibold mb-4 text-gray-800">
                Mapa Interactivo - Polaridad {selectedPolarity} ({polarityLabels[selectedPolarity]})
              </h3>
              <div className="border border-gray-200 rounded-lg overflow-hidden" style={{ height: '600px' }}>
                <iframe
                  ref={mapRef}
                  width="100%"
                  height="100%"
                  style={{ border: 'none' }}
                  title="Mapa de México - Rest-Mex 2025"
                />
              </div>
              <div className="mt-4 text-sm text-gray-600">
                <p><strong>Instrucciones:</strong> Haz clic en los círculos para ver detalles de cada estado. El tamaño y la intensidad del color representan la cantidad de reseñas.</p>
              </div>
            </div>

            {/* Tabla de Resultados */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-lg font-semibold mb-4 text-gray-800">
                Ranking de Estados - Polaridad {selectedPolarity}
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full table-auto">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">#</th>
                      <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Estado</th>
                      <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Reseñas Polaridad {selectedPolarity}</th>
                      <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Total Estado</th>
                      <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Porcentaje</th>
                      <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Intensidad</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {tableData.map(([stateName, data], index) => (
                      <tr key={stateName} className="hover:bg-gray-50">
                        <td className="px-4 py-3 text-sm font-medium text-gray-900">{index + 1}</td>
                        <td className="px-4 py-3 text-sm font-medium text-gray-900">{stateName}</td>
                        <td className="px-4 py-3 text-sm font-bold" style={{ color: polarityColors[selectedPolarity] }}>
                          {data.count.toLocaleString()}
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-700">{data.total.toLocaleString()}</td>
                        <td className="px-4 py-3 text-sm">
                          <span className="px-2 py-1 rounded-full text-xs font-semibold bg-blue-100 text-blue-800">
                            {data.percentage}%
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div 
                              className="h-2 rounded-full"
                              style={{ 
                                width: `${(data.count / stats.maxCount) * 100}%`,
                                backgroundColor: polarityColors[selectedPolarity]
                              }}
                            />
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default FoliumMexicoMap;