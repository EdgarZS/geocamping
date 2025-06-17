from flask import Flask, render_template, request, redirect, url_for, session,jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import pyodbc
from datetime import datetime, timedelta
import json
from azure.communication.email import EmailClient
from azure.storage.blob import BlobServiceClient
from PIL import Image
import io, uuid
import stripe
import qrcode
from io import BytesIO

stripe.api_key = "sk_test_"
DOMAIN = "http://127.0.0.1:5000"

acs_connection_string = 'Endpoint'
email_sender = 'DoNotReply@'  # email verificado en ACS

app = Flask(__name__)
app.secret_key = 'clave_secreta_segura'  # Cambiar por una secreta en producción
app.permanent_session_lifetime = timedelta(minutes=30)

# Conexion a la base de datos
server = 'tcp:az-geojson-srvr.database.windows.net'
database = 'az_geojson-bd'
username = 'zenkai'
password = 'az_geojson123'
#conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

def upload_qr_to_blob(image_bytes, blob_name):
    blob_service = BlobServiceClient.from_connection_string("DefaultEndpointsProtocol=https;")
    container_client = blob_service.get_container_client("nombre-contenedor")
    
    blob_client = container_client.get_blob_client(blob_name)
    blob_client.upload_blob(image_bytes, overwrite=True)

    # URL pública (si el contenedor es público)
    return f"https://dominio/{blob_name}"

def send_reservation_email_with_qr(to_email, name, reservation_id):
    try:
        # Generar URL de validación
        validation_url = f"https://dominio?id={reservation_id}"

        # Crear QR con la URL
        qr = qrcode.make(validation_url)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        qr_bytes = buffer.getvalue()

        # Subir QR al blob
        qr_url = upload_qr_to_blob(qr_bytes, f"qr_reserva_{reservation_id}.png")

        # Enviar por Azure Communication Services
        client = EmailClient.from_connection_string(acs_connection_string)

        message = {
            "senderAddress": email_sender,
            "recipients": {"to": [{"address": to_email}]},
            "content": {
                "subject": f"Tu reserva #{reservation_id} - Código QR",
                "html": f"""
                    <html>
                        <body>
                            <h3>Hola {name}, tu reserva ha sido confirmada.</h3>
                            <p>Presenta este código QR en la entrada:</p>
                            <img src="{qr_url}" alt="QR" width="256" height="256">
                            <p><b>ID:</b> {reservation_id}</p>
                            <p>¡Gracias por su preferencia!</p>
                        </body>
                    </html>
                """
            }
        }

        poller = client.begin_send(message)
        result = poller.result()

        if result.status == "Succeeded":
            print("Correo con QR enviado con éxito:", result.message_id)
        else:
            print("Error en el envío:", result)

    except Exception as ex:
        print("Error al enviar email con QR:", ex)




def send_verification_email(to_email, name, token):
    try:
        client = EmailClient.from_connection_string(acs_connection_string)

        verify_url = f"https://dominio?token={token}"
        subject = "Verifica tu cuenta"

        message = {
            "senderAddress": email_sender,
            "recipients": {
                "to": [{"address": to_email}]
            },
            "content": {
                "subject": subject,
                "plainText": f"Hola {name}, haz clic en este enlace para verificar tu cuenta: {verify_url}",
                "html": f"""
                    <html>
                        <body>
                            <p>Hola {name},</p>
                            <p>Haz clic en el siguiente enlace para verificar tu cuenta:</p>
                            <p><a href="{verify_url}">{verify_url}</a></p>
                        </body>
                    </html>
                """
            }
        }

        poller = client.begin_send(message)
        result = poller.result()

        if result.status == "Succeeded":
            print("Correo enviado con éxito:", result.message_id)
        else:
            print("Error al enviar correo:", result)

    except Exception as ex:
        print("Error enviando email:", ex)



# Ruta de registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            return "<h3>Las contraseñas no coinciden</h3>"

        password = generate_password_hash(password)
        token = str(uuid.uuid4())

        try:
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (name, email, password_hash, role, valido, verification_token)
                VALUES (?, ?, ?, 'cliente', 0, ?)
            """, (name, email, password, token))
            conn.commit()
            conn.close()

            # Enviar correo de verificación
            send_verification_email(email, name, token)
            return "<h3>Se ha enviado un correo para verificar tu cuenta.</h3> <br> <a href='/login'><h4>Iniciar sesión</h4></a>"

        except Exception as e:
            return f"<h3>Error de registro: {e}</h3>"

    return render_template('register.html')



# Ruta de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, password_hash, valido FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()
            conn.close()

            if user and check_password_hash(user.password_hash, password):
                if user.valido != 1:
                    return "</h3>Debes verificar tu cuenta por correo antes de iniciar sesión.</h3>"
                
                session['user_id'] = user.id
                session['user_name'] = user.name
                session.permanent = True
                return redirect(url_for('show_zones'))
            else:
                return "</h3>Usuario o contraseña incorrectos</h3>"

        except Exception as e:
            return f"<h3>Error de login: {e}</h3>"

    return render_template('login.html')



# Ruta protegida


# Ruta pública con control de sesión
@app.route('/zones')
def show_zones():
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM zones")
        columns = [column[0] for column in cursor.description]
        zones = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        logged_in = 'user_id' in session
        return render_template('zones.html', zones=zones, logged_in=logged_in)
    except Exception as e:
        return f"Error: {e}"


@app.route('/zones.geojson')
def zones_geojson():
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM zones")
        features = []

        for row in cursor.fetchall():
            try:
                geometry = json.loads(row.geojson)
                # Agrega el Feature
                features.append({
                    "type": "Feature",
                    "properties": {
                        "id": row.id,
                        "name": row.name,
                        "size_m2": row.size_m2,
                        "capacity": row.capacity,
                        "terrain_type": row.terrain_type,
                        "rules": row.rules,
                        "estrategicas": row.nearby_features,
                        "current_state": row.current_state,
                        "main_image_url": row.main_image_url,
                        "precio": row.precio,
                        "logged_in": 'user_id' in session 
                    },
                    "geometry": geometry
                })
            except Exception as ge:
                print(f"Error parsing geojson for zone {row.id}: {ge}")
        
        conn.close()

        geojson = {
            "type": "FeatureCollection",
            "features": features
        }

        return jsonify(geojson)

    except Exception as e:
        return f"Error generando GeoJSON: {e}", 500

@app.route('/verify')
def verify_email():
    token = request.args.get('token')
    if not token:
        return "<h3>Token inválido.</h3>"

    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET valido = 1 WHERE verification_token = ?", (token,))
        if cursor.rowcount == 0:
            return "<h3>Token no válido o ya usado.</h3>"
        conn.commit()
        conn.close()
        return "<h3>¡Correo verificado con éxito! Ya puedes cerrar esta página e iniciar sesión.</h3> <br> <a href='/login'><button><h4>Iniciar sesión</h4></button></a>"
    except Exception as e:
        return f"<h3>Error al verificar correo: {e}</h3>"



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

##########################LOGICA DEL SISTEMA DE ADIMINISTRADOR################################

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']

        try:
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, password_hash, role, valido
                FROM users
                WHERE name = ?
            """, (name,))
            user = cursor.fetchone()
            conn.close()

            if not user:
                return "Nombre de usuario no encontrado."

            if not check_password_hash(user.password_hash, password):
                return "Contraseña incorrecta."

            if user.role != 'admin':
                return "No tienes permisos de administrador."

            if user.valido != 1:
                return "Tu cuenta de administrador no ha sido validada."

            # Login exitoso como admin (no se mezcla con sesión del cliente)
            session['admin_user_id'] = user.id
            session['admin_user_name'] = user.name
            session.permanent = True
            return redirect(url_for('admin_dashboard'))

        except Exception as e:
            return f"Error en el login del administrador: {e}"

    return render_template('admin/login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_user_id' not in session:
        return redirect(url_for('admin_login'))

    admin_name = session.get('admin_user_name', 'Administrador')
    return render_template('admin/dashboard.html', admin_name=admin_name)

@app.route('/admin/registro', methods=['GET', 'POST'])
def admin_register():
    # Solo un administrador logueado puede registrar otro
    if 'admin_user_id' not in session:
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm_password']

        if password != confirm:
            return "Las contraseñas no coinciden"

        password_hash = generate_password_hash(password)

        try:
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (name, email, password_hash, role, valido)
                VALUES (?, ?, ?, 'admin', 1)
            """, (name, email, password_hash))
            conn.commit()
            conn.close()
            return "Administrador registrado con éxito."
        except Exception as e:
            return f"Error registrando administrador: {e}"

    return render_template('admin/registro.html')


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_user_id', None)
    session.pop('admin_user_name', None)
    return redirect(url_for('admin_login'))

@app.route('/admin/zones')
def admin_zones():
    if 'admin_user_id' not in session:
        return redirect(url_for('admin_login'))
    return render_template('admin/zonas.html')

#################REGISTRO DE ZONAS####################

@app.route('/admin/zones/register', methods=['POST'])
def register_zone():
    if 'admin_user_id' not in session:
        return redirect(url_for('admin_login'))

    try:
        # Extrae datos
        name = request.form['name']
        geojson = request.form['geojson']
        size_m2 = float(request.form['size_m2'])
        capacity = int(request.form['capacity'])
        terrain_type = request.form.get('terrain_type')
        rules = request.form.get('rules')
        precio = float(request.form['precio'])
        zonas_interes = request.form['nearby_features']

        # Cargar y redimensionar imagen
        image = request.files['image']
        image_bytes = io.BytesIO()
        img = Image.open(image)
        img = img.resize((512, 288))
        img.save(image_bytes, format='JPEG')
        image_bytes.seek(0)

        # Insertar zona sin imagen aún (para obtener el ID)
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO zones (name, geojson, size_m2, capacity, terrain_type, rules, nearby_features, current_state, precio)
            OUTPUT INSERTED.id
            VALUES (?, ?, ?, ?, ?, ?, ?, 'disponible', ?)
        """, (name, geojson, size_m2, capacity, terrain_type, rules, zonas_interes, precio))
        zone_id = cursor.fetchone()[0]

        # Subir a Azure Blob
        blob_name = f"zona_{zone_id}.jpg"
        blob_service_client = BlobServiceClient.from_connection_string("DefaultEndpointsProtocol")
        blob_client = blob_service_client.get_blob_client(container="contenedor", blob=blob_name)
        blob_client.upload_blob(image_bytes, overwrite=True)

        image_url = f"https://dominio/{blob_name}"

        # Actualizar zona con la URL de imagen
        cursor.execute("UPDATE zones SET main_image_url = ? WHERE id = ?", (image_url, zone_id))
        conn.commit()
        conn.close()

        return redirect(url_for('admin_zones'))

    except Exception as e:
        return f"Error registrando zona: {e}"


############## Actualizar y Eliminar Zona ####################
@app.route('/admin/zones/update', methods=['POST'])
def update_zone():
    if 'admin_user_id' not in session:
        return redirect(url_for('admin_login'))

    try:
        zone_id = int(request.form['id'])
        name = request.form['name']
        size_m2 = float(request.form['size_m2'])
        capacity = int(request.form['capacity'])
        terrain_type = request.form.get('terrain_type')
        rules = request.form.get('rules')
        features = request.form.get('nearby_features')
        precio = float(request.form.get('precio'))
        current_state = request.form.get('current_state')

        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE zones
            SET name=?, size_m2=?, capacity=?, terrain_type=?, rules=?, nearby_features=?, precio=?, current_state=?
            WHERE id=?
        """, (name, size_m2, capacity, terrain_type, rules, features, precio, current_state, zone_id))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_zones'))

    except Exception as e:
        return f"Error actualizando zona: {e}", 500

@app.route('/admin/zones/delete', methods=['POST'])
def delete_zone():
    if 'admin_user_id' not in session:
        return redirect(url_for('admin_login'))

    try:
        zone_id = int(request.form['id'])
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM zones WHERE id = ?", (zone_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_zones'))

    except Exception as e:
        return f"Error eliminando zona: {e}", 500

################## METODOS PARA ADMINSITRAR ADMINISTRADORES ####################
@app.route('/admin/admins')
def admin_list_admins():
    if 'admin_user_id' not in session:
        return redirect(url_for('admin_login'))

    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, created_at FROM users WHERE role = 'admin'")
    admins = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    conn.close()

    return render_template('admin/admins.html', admins=admins)


@app.route('/admin/admins/add', methods=['POST'])
def admin_add_admin():
    name = request.form['name']
    email = request.form['email']
    password = generate_password_hash(request.form['password'])

    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (name, email, password_hash, role, valido)
        VALUES (?, ?, ?, 'admin', 1)
    """, (name, email, password))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_list_admins'))


@app.route('/admin/admins/edit/<int:user_id>', methods=['POST'])
def admin_edit_admin(user_id):
    name = request.form['name']
    email = request.form['email']
    password = request.form.get('password')

    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    if password:
        password_hash = generate_password_hash(password)
        cursor.execute("UPDATE users SET name=?, email=?, password_hash=? WHERE id=?", (name, email, password_hash, user_id))
    else:
        cursor.execute("UPDATE users SET name=?, email=? WHERE id=?", (name, email, user_id))

    conn.commit()
    conn.close()
    return redirect(url_for('admin_list_admins'))


@app.route('/admin/admins/delete/<int:user_id>', methods=['POST'])
def admin_delete_admin(user_id):
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id=? AND role='admin'", (user_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_list_admins'))

################## METODOS PARA ADMINSITRAR USUARIOS ####################
@app.route('/admin/usuarios')
def admin_list_usuarios():
    if 'admin_user_id' not in session:
        return redirect(url_for('admin_login'))

    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, created_at FROM users WHERE role = 'cliente'")
    usuarios = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    conn.close()

    return render_template('admin/usuarios.html', usuarios=usuarios)

@app.route('/admin/usuarios/add', methods=['POST'])
def admin_add_usuarios():
    name = request.form['name']
    email = request.form['email']
    password = generate_password_hash(request.form['password'])

    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (name, email, password_hash, role, valido)
        VALUES (?, ?, ?, 'cliente', 1)
    """, (name, email, password))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_list_usuarios'))


@app.route('/admin/usuarios/edit/<int:user_id>', methods=['POST'])
def admin_edit_usuarios(user_id):
    name = request.form['name']
    email = request.form['email']
    password = request.form.get('password')

    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    if password:
        password_hash = generate_password_hash(password)
        cursor.execute("UPDATE users SET name=?, email=?, password_hash=? WHERE id=?", (name, email, password_hash, user_id))
    else:
        cursor.execute("UPDATE users SET name=?, email=? WHERE id=?", (name, email, user_id))

    conn.commit()
    conn.close()
    return redirect(url_for('admin_list_usuarios'))


@app.route('/admin/usuarios/delete/<int:user_id>', methods=['POST'])
def admin_delete_usuarios(user_id):
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id=? AND role='cliente'", (user_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_list_usuarios'))

####### LOGIOCA DE RESERVAS ##########
@app.route('/reservar')
def reservar():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    zone_id = request.args.get('zone_id')
    start = request.args.get('start')
    end = request.args.get('end')

    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("SELECT name, precio FROM zones WHERE id = ?", (zone_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return "Zona no encontrada", 404

        zone_name = row.name
        precio = float(row.precio)

        # Calcular noches
        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(end, "%Y-%m-%d")
        noches = (end_date - start_date).days
        total = noches * precio

        return render_template("resumen_reserva.html",
                               user_id=session['user_id'],
                               user_name=session['user_name'],
                               zone_id=zone_id,
                               zone_name=zone_name,
                               start=start,
                               end=end,
                               precio=precio,
                               noches=noches,
                               total=total)
    except Exception as e:
        return f"Error al cargar reserva: {e}", 500
    
@app.route('/crear_checkout', methods=['POST'])
def crear_checkout():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    zone_id = int(request.form['zone_id'])
    start_date = request.form['start']
    end_date = request.form['end']
    total = float(request.form['total'])

    # Guardar temporalmente los datos en sesión
    session['checkout_data'] = {
        'user_id': user_id,
        'zone_id': zone_id,
        'start': start_date,
        'end': end_date,
        'total': total
    }

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'mxn',
                'product_data': {
                    'name': f"Reserva Zona #{zone_id} del {start_date} al {end_date}"
                },
                'unit_amount': int(total * 100)  # en centavos
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=DOMAIN + '/pago_exitoso',
        cancel_url=DOMAIN + '/resumen_reserva_cancelado'
    )

    return redirect(checkout_session.url, code=303)



@app.route('/pago_exitoso')
def pago_exitoso():
    if 'checkout_data' not in session:
        return redirect(url_for('show_zones'))

    data = session.pop('checkout_data')

    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        # 1. Insertar reserva con activado = 0
        cursor.execute("""
            INSERT INTO reservations (user_id, zone_id, start_date, end_date, status, activado)
            VALUES (?, ?, ?, ?, 'pagado', 0)
        """, (data['user_id'], data['zone_id'], data['start'], data['end']))

        # 2. Obtener ID de reserva recién creada
        cursor.execute("SELECT @@IDENTITY AS last_id")
        reservation_id = int(cursor.fetchone().last_id)

        # 3. Actualizar estado de la zona
        cursor.execute("UPDATE zones SET current_state = 'reservado' WHERE id = ?", (data['zone_id'],))

        # 4. Obtener correo y nombre del usuario
        cursor.execute("SELECT name, email FROM users WHERE id = ?", (data['user_id'],))
        user = cursor.fetchone()

        conn.commit()
        conn.close()

        # 5. Enviar correo con QR
        if user:
            send_reservation_email_with_qr(user.email, user.name, reservation_id)

        # 6. Mostrar mensaje
        return render_template("mensajes/pago_exitoso.html", user_name=user.name)

    except Exception as e:
        return f"Error al registrar reserva: {e}"


@app.route('/resumen_reserva_cancelado')
def resumen_reserva_cancelado():
    return "<h4>El pago fue cancelado. No se registró ninguna reserva.</h4><a href='/zones'>Volver</a>"

######## CONSULTAR RESERVAS DESDE EL PERFIL DEL USUARIO ########
@app.route('/reservas')
def reservas():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT r.id, z.name as zone_name, r.start_date, r.end_date, r.status, r.created_at
        FROM reservations r
        JOIN zones z ON r.zone_id = z.id
        WHERE r.user_id = ?
        ORDER BY r.created_at DESC
    """, (user_id,))

    reservas = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    conn.close()

    return render_template("reservas.html", reservas=reservas, user_name=session['user_name'])


###METODOS PARA OCULTAR FECHAS RESERVADAS #####################
@app.route('/zones/<int:zone_id>/fechas_ocupadas')
def fechas_ocupadas(zone_id):
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT start_date, end_date
            FROM reservations
            WHERE zone_id = ? AND status = 'pagado'
        """, (zone_id,))

        fechas = [] 
        for row in cursor.fetchall():
            inicio = row.start_date
            fin = row.end_date

            if isinstance(inicio, str):
                inicio = datetime.strptime(inicio, "%Y-%m-%d")
            if isinstance(fin, str):
                fin = datetime.strptime(fin, "%Y-%m-%d")

            actual = inicio
            while actual < fin:
                fechas.append(actual.strftime("%Y-%m-%d"))
                actual += timedelta(days=1)

        conn.close()
        return jsonify(fechas)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


################## VALIDAR QR#####################

@app.route('/validar_qr')
def validar_qr_reserva():
    reserva_id = request.args.get('id')

    if not reserva_id:
        return render_template("admin/validar_qr.html", message="Reserva inválida (ID no especificado)", success=False)

    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        # Verifica si existe y está pagada
        cursor.execute("SELECT zone_id, activado FROM reservations WHERE id = ? AND status = 'pagado'", (reserva_id,))
        row = cursor.fetchone()

        if not row:
            return render_template("admin/validar_qr.html", message="Reserva no encontrada o aún no pagada.", success=False)

        zone_id, activado = row

        # Si no hay sesión admin, redirige al cliente a zonas
        if 'admin_user_id' not in session:
            return redirect(url_for('show_zones'))

        # Si ya estaba activada
        if activado == 1:
            return render_template("admin/validar_qr.html", message="Esta reserva ya fue activada anteriormente.", success=True)

        # Activar reserva y zona
        cursor.execute("UPDATE reservations SET activado = 1 WHERE id = ?", (reserva_id,))
        cursor.execute("UPDATE zones SET current_state = 'ocupado' WHERE id = ?", (zone_id,))
        conn.commit()
        conn.close()

        return render_template("admin/validar_qr.html", message=f"Reserva #{reserva_id} activada correctamente.", success=True)

    except Exception as e:
        return render_template("admin/validar_qr.html", message=f"Error del servidor: {e}", success=False)


@app.route("/admin/reservas")
def admin_reservas():
    if 'admin_user_id' not in session:
        return redirect(url_for('admin_login'))
    return render_template("admin/reservas.html")

@app.route("/admin/reservas_json")
def reservas_json():
    if 'admin_user_id' not in session:
        return jsonify({"error": "Acceso no autorizado"}), 401

    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.id, u.name, u.email, z.name, r.start_date, r.end_date, r.status, r.activado
            FROM reservations r
            JOIN users u ON r.user_id = u.id
            JOIN zones z ON r.zone_id = z.id
            ORDER BY r.created_at DESC
        """)
        data = []
        for row in cursor.fetchall():
            data.append({
                "id": row[0],
                "user_name": row[1],
                "user_email": row[2],
                "zone_name": row[3],
                "start_date": str(row[4]),
                "end_date": str(row[5]),
                "status": row[6],
                "activado": row[7]
            })
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return redirect(url_for('show_zones'))

@app.route('/admin/')
def admin_home_1():
    return redirect(url_for('admin_dashboard'))

@app.route('/admin')
def admin_home_2():
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
