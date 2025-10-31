import './App.css';
import { useState, useEffect } from 'react';

function App() {
  const [inventarios, setInventarios] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedBodega, setSelectedBodega] = useState("Selecione una bodega");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/v1/")
      .then((response) => response.json())
      .then((data) => {
        setInventarios(data);
        setLoading(false);
      })
      .catch((error) => console.error("Error fetching data:", error));
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }
   // Filtra los inventarios en función de la bodega seleccionada
  const filteredInventarios = inventarios.filter(inventario =>
    inventario.codigo_bodega === selectedBodega && inventario.f400_cant_existencia_1 > 0
  );

   // Función para formatear como moneda (peso colombiano)
  const formatCurrency = (value) => {
    return value ? value.toLocaleString('es-CO', { style: 'currency', currency: 'COP' }) : '-';
  };

  const totalCosto = filteredInventarios.reduce((total, inventario) => total + (inventario.f400_costo_prom_tot || 0), 0);

  return (
    <div className="App">
      <h1>Inventarios</h1>
      <div>
        <label>Filtrar por Bodega: </label>
        <select
          value={selectedBodega}
          onChange={(e) => setSelectedBodega(e.target.value)}  // Cambia la bodega seleccionada
        >
          <option value="MP001">MP001</option>
          <option value="MP002">MP002</option>
  
          {/* Agrega más opciones según las bodegas disponibles */}
        </select>
      </div>
      <div>Total Costo Inventario : {totalCosto}</div>
      <table>
        <thead>
          <tr>
            <th>Código Item</th>
            <th>Descripcion Item</th>
            <th>Codigo Bodega</th>
            <th>Descripcion Bodega</th>
            <th>Inventario</th>
            <th>Costo Promedio Unt</th>
            <th>Costo Total</th>
          </tr>
        </thead>

        <tbody>
          {filteredInventarios.length === 0 ? (
            <tr>
              <td colSpan="5">No se encontraron inventarios para esta bodega.</td>
            </tr>
          ) : (
            filteredInventarios.map((inventario) => (
              <tr key={inventario.id_item}>
                <td>{inventario.codigo_item}</td>
                <td>{inventario.item}</td>
                <td>{inventario.codigo_bodega}</td>
                <td>{inventario.bodega}</td>
                <td>{inventario.f400_cant_existencia_1}</td>
                <td>{formatCurrency(inventario.f400_costo_prom_uni)}</td>
                <td>{formatCurrency(inventario.f400_costo_prom_tot)}</td>
              </tr>
            ))
          )}
          
        </tbody>
        
      </table>
      
      
    </div>
  );
}

export default App;




