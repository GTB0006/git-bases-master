let servicioSeleccionado = "";
let barberoIdSeleccionado = null;

// 1. Manejo de vistas y selección de servicio
async function seleccionarServicio(nombre, precio) {
    servicioSeleccionado = nombre;
    document.getElementById('contenedor-servicios').style.display = 'none';
    document.getElementById('formulario-datos').style.display = 'block';
    document.getElementById('resumen-servicio').innerText = nombre;
    
    // Cargar barberos desde la base de datos
    await cargarBarberos();
}

// 2. Cargar barberos dinámicamente con enfoque de imagen
async function cargarBarberos() {
    const contenedor = document.getElementById('contenedor-barberos-fotos');
    contenedor.innerHTML = "<p style='grid-column: span 2; text-align:center;'>Buscando barberos...</p>";
    
    try {
        const response = await fetch('/barberos/1'); // Asegúrate de que barberia_id sea 1
        const barberos = await response.json();
        
        contenedor.innerHTML = ""; 
        
        barberos.forEach(b => {
            const card = document.createElement('div');
            card.className = "barbero-card";
            card.innerHTML = `
                <img src="${b.foto_url || 'https://via.placeholder.com/100'}" 
                     alt="${b.nombre}" 
                     style="object-fit: cover; object-position: center;">
                <span>${b.nombre}</span>
            `;
            
            card.onclick = () => {
                document.querySelectorAll('.barbero-card').forEach(c => c.classList.remove('selected'));
                card.classList.add('selected');
                barberoIdSeleccionado = b.id;
            };
            
            contenedor.appendChild(card);
        });
    } catch (error) {
        contenedor.innerHTML = "<p style='color:red;'>Error al cargar barberos</p>";
    }
}

// 3. Volver a la lista de servicios
function volverAServicios() {
    document.getElementById('contenedor-servicios').style.display = 'block';
    document.getElementById('formulario-datos').style.display = 'none';
    barberoIdSeleccionado = null;
}

// 4. Enviar reserva al Backend
async function agendarCita() {
    const nombre = document.getElementById('cliente_nombre').value;
    const email = document.getElementById('cliente_email').value;
    const telefono = document.getElementById('cliente_telefono').value; // <--- Nuevo
    const fecha = document.getElementById('fecha').value;
    const hora = document.getElementById('hora').value;

    if (!barberoIdSeleccionado) {
        alert("Por favor, selecciona un barbero.");
        return;
    }
    if (!nombre || !email || !telefono || !fecha || !hora) {
        alert("Todos los campos son obligatorios.");
        return;
    }

    // URL con el nuevo campo cliente_telefono
    const url = `/reservas?barberia_id=1` +
                `&barbero_id=${barberoIdSeleccionado}` +
                `&cliente_nombre=${encodeURIComponent(nombre)}` +
                `&cliente_email=${encodeURIComponent(email)}` +
                `&cliente_telefono=${encodeURIComponent(telefono)}` +
                `&servicio=${encodeURIComponent(servicioSeleccionado)}` +
                `&fecha=${fecha}` +
                `&hora=${hora}`;

    try {
        const response = await fetch(url, { method: 'POST' });
        const data = await response.json();

        if (response.ok) {
            alert("✅ ¡Reserva confirmada! Te hemos enviado un correo.");
            window.location.reload();
        } else {
            alert("❌ Error: " + data.detail);
        }
    } catch (error) {
        alert("❌ Error de conexión con el servidor.");
    }
}
