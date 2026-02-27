let servicioSeleccionado = "";

let barberoIdSeleccionado = null;



async function seleccionarServicio(nombre, precio) {

    servicioSeleccionado = nombre;

    document.getElementById('contenedor-servicios').style.display = 'none';

    document.getElementById('formulario-datos').style.display = 'block';

    document.getElementById('resumen-servicio').innerText = nombre;

    await cargarBarberos();

}



async function cargarBarberos() {

    const contenedor = document.getElementById('contenedor-barberos-fotos');

    contenedor.innerHTML = "<p style='text-align:center;'>Buscando barberos...</p>";

    

    try {

        const response = await fetch('/barberos/1');

        const barberos = await response.json();

        contenedor.innerHTML = ""; 

        

        barberos.forEach(b => {

            const card = document.createElement('div');

            card.className = "barbero-card";

            card.innerHTML = `

                <img src="${b.foto_url || 'https://via.placeholder.com/100'}" alt="${b.nombre}">

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



function volverAServicios() {

    document.getElementById('contenedor-servicios').style.display = 'block';

    document.getElementById('formulario-datos').style.display = 'none';

    barberoIdSeleccionado = null;

}



async function agendarCita() {

    const nombre = document.getElementById('cliente_nombre').value;

    const email = document.getElementById('cliente_email').value;

    const telefono = document.getElementById('cliente_telefono').value;

    const fecha = document.getElementById('fecha').value;

    const hora = document.getElementById('hora').value;



    if (!barberoIdSeleccionado) return alert("Selecciona un barbero.");

    if (!nombre || !email || !telefono || !fecha || !hora) return alert("Completa todos los campos.");



    const url = `/reservas?barberia_id=1&barbero_id=${barberoIdSeleccionado}&cliente_nombre=${encodeURIComponent(nombre)}&cliente_email=${encodeURIComponent(email)}&cliente_telefono=${encodeURIComponent(telefono)}&servicio=${encodeURIComponent(servicioSeleccionado)}&fecha=${fecha}&hora=${hora}`;



    try {

        const response = await fetch(url, { method: 'POST' });

        if (response.ok) {

            alert("✅ Reserva confirmada");

            window.location.reload();

        } else {

            const data = await response.json();

            alert("❌ Error: " + data.detail);

        }

    } catch (e) { alert("Error de conexión"); }

}
