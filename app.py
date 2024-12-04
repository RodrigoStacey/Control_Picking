from flask import Flask, render_template, request, redirect, url_for,flash,jsonify
from flask_mysqldb import MySQL
from flask import session
import mysql.connector
from flask_wtf.csrf import CSRFProtect
from datetime import timezone,datetime,date
from zoneinfo import ZoneInfo
import pandas as pd
import locale
import os
import csv


quito_tz = ZoneInfo("America/Guayaquil")
now = datetime.now(quito_tz)
print("Fecha y hora en Quito:", now.strftime("%Y-%m-%d %H:%M:%S"))

#locale.setlocale(locale.LC_ALL, '')
#now = datetime.now(timezone.utc)

app = Flask(__name__) 

app.config['SECRET_KEY'] = 'AlpinaProduccion2024'

csrf=CSRFProtect()

db_config = {
    'host': 'localhost',
    'user': 'admin',
    'password': 'Mpsal1991###',
    'database': 'picking'
}

def get_db_connection():
    connection = mysql.connector.connect(**db_config)
    return connection



######################## FORMATOS #################################

def integer_formatter(number):
    return f'{number}' 

def percent_formatter(number):
    locale.setlocale(locale.LC_ALL, '')  #
    return locale.format_string('%.1f%%', number, grouping=True)

def float_formatter_1(number):
    locale.setlocale(locale.LC_ALL, '')  
    return locale.format_string('%.1f', number, grouping=True)

def float_formatter_2(number):
    locale.setlocale(locale.LC_ALL, '')  
    return locale.format_string('%.2f', number, grouping=True)

def integer_with_commas_formatter(number):
    locale.setlocale(locale.LC_ALL, '')
    return locale.format_string('%d', number, grouping=True)

def absolute_with_commas_formatter(number):
    # Obtener el valor absoluto del número
    absolute_value = abs(number)
    # Formatear el número con comas y devolverlo como una cadena
    return '{:,}'.format(absolute_value)

def date_formatter(date):
    # Suponiendo que 'date' es un objeto de fecha
    return date.strftime('%d-%b-%Y')  # Formato AAAA-MM-DD 

#############################################################

@app.route('/')
def index():
        return redirect(url_for('home'))

@app.route('/home')
def home():
    return render_template('index.html')

############  PRODUCTOS #############
    
@app.route('/productos_view')

def productos_view():
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM productos')
    prod_list = cursor.fetchall()
    cursor.close()
    connection.close()
    
    return render_template('productos/pro_view.html',prod_list=prod_list)

@app.route('/productos_create', methods=['GET', 'POST'])
def productos_create():
    
    if request.method == 'POST':
        vidproducto = request.form['idproducto']
        vcodigoEAN = request.form['codigoEAN']
        vdescripcion = request.form['descripcion']
        vestacion = request.form['estacion']
        vpesoSTD = request.form['pesoSTD']
        vestado = 'A'
        
        if vdescripcion == "":
            flash("Descripcion no puede estar en blanco")
            return render_template('productos/pro_create.html')
        
        connection = get_db_connection()
        cursor = connection.cursor()
        query = 'INSERT INTO productos VALUES (%s, %s, %s,%s, %s, %s)'
        values = (vidproducto,vcodigoEAN,vdescripcion,vestacion,vpesoSTD,vestado)

        cursor.execute(query, values)
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('productos_view'))
    return render_template('productos/pro_create.html')


@app.route('/productos_edit/<string:id>', methods=['GET', 'POST'])
def productos_edit(id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    if request.method == 'POST':
        
        vidproducto = id
        vcodigoEAN = request.form['codigoEAN']
        vdescripcion = request.form['descripcion']
        vestacion = request.form['estacion']
        vpesoSTD = request.form['pesoSTD']

       
        query = 'UPDATE productos SET codigoEAN = %s, descripcion = %s, estacion = %s, pesoSTD = %s WHERE idproducto = %s'
        values = (vcodigoEAN, vdescripcion, vestacion, vpesoSTD, vidproducto)

        cursor.execute(query, values)
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('productos_view'))

    cursor.execute('SELECT * FROM productos WHERE idproducto = %s', (id,))
    prod_list = cursor.fetchone()
    cursor.close()
    connection.close()
    
    return render_template('productos/pro_edit.html', prod_list=prod_list)

@app.route('/productos_del/<string:id>', methods=['GET'])
def productos_del(id):
    connection = get_db_connection()
    cursor = connection.cursor()

    query = 'DELETE FROM productos WHERE idproducto = %s'
    cursor.execute(query, (id,))
    connection.commit()
    cursor.close()
    connection.close()

    return redirect(url_for('productos_view'))

@app.route('/productos_act/<string:id>')
def productos_act(id):
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    vestado = 'A'

    query = 'UPDATE productos SET estado = %s  WHERE idproducto = %s'
    values = (vestado,id)

    cursor.execute(query, values)
    connection.commit()
    cursor.close()
    connection.close()
    
    return redirect(url_for('productos_view')) 

@app.route('/productos_inact/<string:id>')
def productos_inact(id):
   
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    vestado = 'I'

    query = 'UPDATE productos SET estado = %s  WHERE idproducto = %s'
    values = (vestado,id)

    cursor.execute(query, values)
    connection.commit()
    cursor.close()
    connection.close()
    
    return redirect(url_for('productos_view')) 

#####################CARGA FECHAS ###############################
@app.route('/inicio_fechas', methods=['GET', 'POST'])
def inicio_fechas():
    if request.method == 'GET':
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM centros')
        cen_list = cursor.fetchall()
        cursor.execute('SELECT * FROM almacenes')
        alm_list = cursor.fetchall()
        cursor.close()
        connection.close()
        fecha_actual = now
        return render_template('fechascortas/inicio_fechas.html', cen_list=cen_list, alm_list=alm_list, fecha_actual=fecha_actual)

    elif request.method == 'POST':
        var_centro = request.form.get('txtCentro')
        var_almacen = request.form.get('txtAlmacen')
        var_fecha = request.form.get('txtFechaActual')
        var_confirmacion = request.form.get('txtConfirmacion')
        var_fechacopia = request.form.get('txtFechaCopia')

        if var_confirmacion == 'on':
            connection = get_db_connection()

            # Cursor para verificar registros existentes
            cursor_check = connection.cursor(dictionary=True)
            query_check = '''
                SELECT *
                FROM fechascortas
                WHERE fechatoma = %s AND idcentro = %s AND idalmacen = %s
            '''
            cursor_check.execute(query_check, (var_fechacopia, var_centro, var_almacen))
            existing = cursor_check.fetchone()

            # Consume resultados pendientes, si los hay
            while cursor_check.nextset():
                pass

            cursor_check.close()  # Cierra el cursor de verificación

            if existing:
                cursor_execute = connection.cursor()

                # Usa una tabla temporal para copiar los datos
                query_temp = '''
                    CREATE TEMPORARY TABLE Temporal AS
                    SELECT fechatoma,idcentro,idalmacen,idproducto,fechavencimiento,cantidad,estado
                    FROM fechascortas
                    WHERE fechatoma = %s AND idcentro = %s AND idalmacen = %s
                '''
                cursor_execute.execute(query_temp, (var_fechacopia, var_centro, var_almacen))

                # Inserta los datos nuevamente
                query_insert = '''
                    INSERT INTO fechascortas
                    SELECT null,%s,idcentro,idalmacen,idproducto,fechavencimiento,cantidad,estado FROM Temporal
                '''
                cursor_execute.execute(query_insert,(var_fecha,))

                cursor_execute.close()  # Cierra el cursor de ejecución
            else:
                flash(f"No existe información con esa fecha.")
                return redirect(url_for('inicio_fechas',method = 'GET'))

            connection.commit()
            connection.close()

        return render_template('fechascortas/principal_fechas.html', var_centro=var_centro, var_almacen=var_almacen, var_fecha=var_fecha)

    return redirect(url_for('home'))



@app.route('/menu_fechas')
def menu_fechas():
    
    return render_template('fechascortas/principal_fechas.html')

@app.route('/fechas_manual/<string:centro>/<string:almacen>/<string:fecha>')
def fechas_manual(centro, almacen, fecha):
    
    fecha_formateada = datetime.strptime(fecha[:10], "%Y-%m-%d").date()
    fecha = fecha_formateada
    connection = get_db_connection()
    cursor = connection.cursor()
    query_check = '''
        SELECT fechascortas.idproducto AS Códigp,productos.descripcion AS Producto,fechavencimiento AS Vencimiento,cantidad AS Cantidad
        FROM fechascortas 
        LEFT OUTER JOIN productos on fechascortas.idproducto = productos.idproducto
        WHERE fechatoma = %s AND idcentro = %s AND idalmacen = %s 
    '''
    
    cursor.execute(query_check, (fecha, centro, almacen))
    fec_list = cursor.fetchall()  
    connection.commit()
    cursor.close()
    connection.close()
    
    columnas = ["Código", "Producto", "Vencimiento", "Cantidad"]
    df = pd.DataFrame(fec_list, columns=columnas)
         
    tabla_html = df.to_html(index=False, classes='table table-striped table-bordered table-hover', border=0).replace('<table ', '<table id="example1" ')
  
    # Redirigir según la acción solicitada
    
    return render_template('fechascortas/fechas_manual.html',tabla=tabla_html,centro=centro,almacen=almacen,fecha=fecha)

@app.route('/fechas_scan/<string:centro>/<string:almacen>/<string:fecha>', methods=['GET', 'POST'])
def fechas_scan(centro, almacen, fecha):
    fecha_formateada = datetime.strptime(fecha[:10], "%Y-%m-%d").date()
    connection = get_db_connection()
    cursor = connection.cursor()

    # Obtener el código EAN desde el formulario POST o la URL GET
    if request.method == 'POST':
        codigo_ean = request.form.get('txtCodigoEAN', None)
    else:
        codigo_ean = request.args.get('codigo_ean')

    if codigo_ean:
        # Consultar el producto correspondiente al código EAN
        cursor.execute('SELECT idproducto, descripcion FROM codigosEAN WHERE codigoEAN = %s', (codigo_ean,))
        producto = cursor.fetchone()

        if producto:
            id_producto, descripcion = producto
            # Filtrar por el producto si se encontró
            query_check = '''
                SELECT fechascortas.idproducto AS Código, productos.descripcion AS Producto, fechavencimiento AS Vencimiento, cantidad AS Cantidad
                FROM fechascortas
                LEFT JOIN productos ON fechascortas.idproducto = productos.idproducto
                WHERE fechatoma = %s AND idcentro = %s AND idalmacen = %s AND fechascortas.idproducto = %s
            '''
            params = [fecha, centro, almacen, id_producto]
        else:
            flash('El código EAN no existe.')
            return redirect(url_for('fechas_scan', centro=centro, almacen=almacen, fecha=fecha))
    else:
        # Mostrar todos los registros si no se ingresó un código EAN
        query_check = '''
            SELECT fechascortas.idproducto AS Código, productos.descripcion AS Producto, fechavencimiento AS Vencimiento, cantidad AS Cantidad
            FROM fechascortas
            LEFT JOIN productos ON fechascortas.idproducto = productos.idproducto
            WHERE fechatoma = %s AND idcentro = %s AND idalmacen = %s
        '''
        params = [fecha, centro, almacen]

        id_producto = None
        descripcion = None

    # Ejecutar la consulta
    cursor.execute(query_check, params)
    fec_list = cursor.fetchall()

    # Crear la tabla con pandas
    columnas = ["Código", "Producto", "Vencimiento", "Cantidad"]
    df = pd.DataFrame(fec_list, columns=columnas)
    tabla_html = df.to_html(index=False, classes='table table-striped table-bordered table-hover', border=0).replace('<table ', '<table id="example2" ')

    connection.close()
    return render_template('fechascortas/fechas_scan.html',
                           tabla=tabla_html,
                           centro=centro,
                           almacen=almacen,
                           fecha=fecha,
                           idproducto=id_producto,
                           descripcion=descripcion,
                           codigo_ean=codigo_ean
                           )


@app.route('/nuevo_registro/<string:centro>/<string:almacen>/<string:fecha>', methods=['POST'])
def nuevo_registro(centro, almacen, fecha):
    idproducto = request.form['idproducto']
    fechavencimiento = request.form['fechavencimiento']
    cantidad = request.form['cantidad']
    codigo_ean = request.form['codigo_ean']  # Recuperar el código EAN

    if codigo_ean == None :
        
        flash('Registro no agregado, no tiene codigo asociado.')

    else:            
        connection = get_db_connection()
        cursor = connection.cursor()

        # Insertar el nuevo registro en la tabla fechascortas
        cursor.execute('''
            INSERT INTO fechascortas (idcentro, idalmacen, fechatoma, idproducto, fechavencimiento, cantidad)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (centro, almacen, fecha, idproducto, fechavencimiento, cantidad))
        
        flash('Registro agregado con éxito.')
        
        connection.commit()
        connection.close()
            

        
    # Redirigir nuevamente a fechas_scan conservando el código EAN
    return redirect(url_for('fechas_scan', centro=centro, almacen=almacen, fecha=fecha, codigo_ean=codigo_ean))


@app.route('/fechas_carga/<string:centro>/<string:almacen>/<string:fecha>',methods=["GET","POST"])
def fechas_carga(centro, almacen, fecha):
    
    fecha_formateada = datetime.strptime(fecha[:10], "%Y-%m-%d").date()
    fecha = fecha_formateada

    if request.method == 'GET':
        
        return render_template('fechascortas/fechas_carga.html',centro=centro,almacen=almacen,fecha=fecha)
    
    elif request.method == 'POST':
        error_msg = ""
        var_agencia = request.form.get('txtCentro')
        var_fecha = request.form.get('txtFecha')
        fecha_partes = var_fecha.split('-')
        var_year = fecha_partes[0]
        var_month = fecha_partes[1]
        var_dia = fecha_partes[2]
        
        var_confirmacion = 'on'
        var_nombre_archivo = request.form.get('txtNombreArchivoFC')
        
            
        if error_msg:
            flash(error_msg.strip())
            return render_template('pedidos/carga_pedidos.html',error=True)  

        if var_confirmacion == 'on':
            nombreCSV = f'{var_nombre_archivo}.csv'
    
            if os.path.exists(f'static/fuentes/{nombreCSV}'):
                with open(f'static/fuentes/{nombreCSV}', newline='') as csvfile:
                    csv_data = csv.reader(csvfile, delimiter=';')
                    next(csv_data)  # Saltar la primera fila (cabecera)
                    
                    connection = get_db_connection()
                    cursor = connection.cursor()

                    for row in csv_data:
                        date_str = row[0] 
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                        date_str = row[4] 
                        date_objven = datetime.strptime(date_str, '%Y-%m-%d')
                        fechatoma = date_obj
                        idcentro = row[1]
                        idalmacen = row[2]
                        idproducto = row[3]
                        fechavencimiento = date_objven
                        cantidad = row[5]
                        estado = 'A'
                        query = 'INSERT INTO fechascortas VALUES (null,%s, %s, %s,%s, %s, %s, %s)'
                        values = (fechatoma,idcentro,idalmacen,idproducto,fechavencimiento,cantidad,estado)                            
                        cursor.execute(query, values)
                            
                    connection.commit()
                    cursor.close()
                    connection.close()
                    # os.remove(f'static/fuentes/{nombreCSV}')
            else:
                flash(f"El archivo {f'static/fuentes/{nombreCSV}'} no existe.")               
                return  render_template('pedidos/carga_pedidos.html')
    
        return redirect(url_for('menu_pedidos'))
 

    
    
    return render_template('fechascortas/fechas_carga.html')



@app.route('/fechas_store', methods=['POST'])
def fechas_store():
    
    
    var_fechatoma = request.form['txtFechaToma']
    var_idcentro = request.form['txtIdCentro']
    var_idalmacen = request.form['txtIdAlmacen']
    var_idproducto = request.form['txtIdProducto']
    var_fechavencimiento = request.form['txtFechaVencimiento']
    var_cantidad = request.form['txtCantidad']
    var_estado = 'A'
    
    connection = get_db_connection()
    cursor = connection.cursor()

    var_fechavencimiento = datetime.strptime(var_fechavencimiento, "%Y-%m-%d").date()

    # Validar si es mayor o igual a la fecha actual
    fecha_actual = date.today()
    if var_fechavencimiento < fecha_actual:
        flash("La fecha de vencimiento debe ser mayor o igual a la fecha actual.")
        return redirect(url_for('fechas_manual',centro=var_idcentro,almacen=var_idalmacen,fecha=var_fechatoma))


    # Verificar si ya existe el registro
    query_check = '''
        SELECT cantidad 
        FROM fechascortas 
        WHERE fechatoma = %s AND idcentro = %s AND idalmacen = %s 
        AND idproducto = %s AND fechavencimiento = %s
    '''
    cursor.execute(query_check, (var_fechatoma, var_idcentro, var_idalmacen, var_idproducto, var_fechavencimiento))
    existing = cursor.fetchone()

    if existing:
        # Si existe, actualizar la cantidad
        nueva_cantidad = var_cantidad
        query_update = '''
            UPDATE fechascortas 
            SET cantidad = %s 
            WHERE fechatoma = %s AND idcentro = %s AND idalmacen = %s 
            AND idproducto = %s AND fechavencimiento = %s
        '''
        cursor.execute(query_update, (nueva_cantidad, var_fechatoma, var_idcentro, var_idalmacen, var_idproducto, var_fechavencimiento))
    else:
        # Si no existe, insertar un nuevo registro
        query_insert = '''
            INSERT INTO fechascortas (id,fechatoma, idcentro, idalmacen, idproducto, fechavencimiento, cantidad, estado)
            VALUES (null,%s, %s, %s, %s, %s, %s, %s)
        '''
        cursor.execute(query_insert, (var_fechatoma, var_idcentro, var_idalmacen, var_idproducto, var_fechavencimiento, var_cantidad, var_estado))
    
    connection.commit()
    cursor.close()
    connection.close()
    

    return redirect(url_for('fechas_manual',centro=var_idcentro,almacen=var_idalmacen,fecha=var_fechatoma))


@app.route('/fechas_store_scan', methods=['POST'])
def fechas_store_scan():
    var_fechatoma = request.form['txtFechaToma']
    var_idcentro = request.form['txtIdCentro']
    var_idalmacen = request.form['txtIdAlmacen']
    var_fechavencimiento = request.form['txtFechaVencimiento']
    var_cantidad = request.form['txtCantidad']
    var_idproducto = request.form.get('txtIdProducto')

    if not var_idproducto:
        flash("No se seleccionó un producto válido.")
        return redirect(url_for('fechas_scan', centro=var_idcentro, almacen=var_idalmacen, fecha=var_fechatoma))

    connection = get_db_connection()
    cursor = connection.cursor()

    # Validar la fecha de vencimiento
    var_fechavencimiento = datetime.strptime(var_fechavencimiento, "%Y-%m-%d").date()
    fecha_actual = date.today()
    if var_fechavencimiento < fecha_actual:
        flash("La fecha de vencimiento debe ser mayor o igual a la fecha actual.")
        return redirect(url_for('fechas_scan', centro=var_idcentro, almacen=var_idalmacen, fecha=var_fechatoma))

    # Verificar si ya existe el registro
    query_check = '''
        SELECT cantidad 
        FROM fechascortas 
        WHERE fechatoma = %s AND idcentro = %s AND idalmacen = %s 
        AND idproducto = %s AND fechavencimiento = %s
    '''
    cursor.execute(query_check, (var_fechatoma, var_idcentro, var_idalmacen, var_idproducto, var_fechavencimiento))
    existing = cursor.fetchone()

    if existing:
        nueva_cantidad = existing[0] + int(var_cantidad)
        query_update = '''
            UPDATE fechascortas 
            SET cantidad = %s 
            WHERE fechatoma = %s AND idcentro = %s AND idalmacen = %s 
            AND idproducto = %s AND fechavencimiento = %s
        '''
        cursor.execute(query_update, (nueva_cantidad, var_fechatoma, var_idcentro, var_idalmacen, var_idproducto, var_fechavencimiento))
    else:
        query_insert = '''
            INSERT INTO fechascortas (id, fechatoma, idcentro, idalmacen, idproducto, fechavencimiento, cantidad, estado)
            VALUES (NULL, %s, %s, %s, %s, %s, %s, 'A')
        '''
        cursor.execute(query_insert, (var_fechatoma, var_idcentro, var_idalmacen, var_idproducto, var_fechavencimiento, var_cantidad))

    connection.commit()
    cursor.close()
    connection.close()

    flash("Registro guardado exitosamente.")
    return redirect(url_for('fechas_scan', centro=var_idcentro, almacen=var_idalmacen, fecha=var_fechatoma))


#####################CARGA PEDIDOS ###############################

@app.route('/menu_pedidos')
def menu_pedidos():
    vcentro = session.get('var_centro')
    fecha_actual = session.get('fecha_actual')
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    query = '''
        SELECT * FROM pivot_contro_dia where fecha = %s and idcentro = %s;
    '''
    cursor.execute(query,(fecha_actual,vcentro))
    listado_ped = cursor.fetchall()
    cursor.close()
    connection.close()
    
    return render_template('pedidos/principal_pedidos.html',listado_ped=listado_ped,vcentro=vcentro,fecha_actual=fecha_actual)

@app.route('/procesar_pedidos',methods=['GET','POST'])
def procesar_pedidos():
    
    vfecha = session.get('fecha_actual')
  
    vcentro = session.get('var_centro')
    
    if request.method == 'GET':    
        return render_template('pedidos/carga_pedidos.html',vfecha=vfecha,vcentro=vcentro)
    elif request.method == 'POST':
        error_msg = ""

        var_confirmacion = request.form.get('txtConfirmacion')
        var_nombre_archivo = request.form.get('txtNombreArchivo')
        
            
        if error_msg:
            flash(error_msg.strip())
            return render_template('pedidos/carga_pedidos.html',error=True)  

        if var_confirmacion == 'on':
            nombreCSV = f'{var_nombre_archivo}.csv'
    
            if os.path.exists(f'static/fuentes/{nombreCSV}'):
                with open(f'static/fuentes/{nombreCSV}', newline='') as csvfile:
                    csv_data = csv.reader(csvfile, delimiter=';')
                    next(csv_data)  # Saltar la primera fila (cabecera)
                    
                    connection = get_db_connection()
                    cursor = connection.cursor()

                    for row in csv_data:
                        # Solo proceder si la columna 'validacion' (índice 7) es '1'
                        if row[7] == '1': 
                            date_str = row[0]  # La fecha original está en 'YYYY-MM-DD'
                            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                            fecha = date_obj
                            centro = row[1]
                            cliente = row[2]
                            idcliente = row[3]
                            num_transporte = row[4]
                            ruta = row[5]
                            num_entrega = row[6]
                            valida = row[7]
                            idproducto = row[8]
                            cantidad = row[9]
                            conteo = 0
                            despacho = 0
                            diferencial = 0
                            idmotivo = None 
                            estado = 'A'
                            query = 'INSERT INTO pedidos VALUES (null,%s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s, %s)'
                            values = (fecha,centro,idcliente,cliente,num_transporte,ruta,num_entrega,idproducto,cantidad,conteo,despacho,diferencial,idmotivo,estado,valida)                            
                            cursor.execute(query, values)
                            
                    connection.commit()
                    cursor.close()
                    connection.close()
                    os.remove(f'static/fuentes/{nombreCSV}')
            else:
                flash(f"El archivo {f'static/fuentes/{nombreCSV}'} no existe.")               
                return  render_template('pedidos/carga_pedidos.html')
    
        return redirect(url_for('menu_pedidos'))
    
@app.route('/ruta_pedidos', methods=['GET','POST'])
def ruta_pedidos():
    
    now = datetime.now()
    
    if request.method == 'GET':
        # Obtener la fecha actual y centros disponibles
        fecha_actual = now.strftime('%Y-%m-%d')
        session['fecha_actual'] = fecha_actual  # Guardar en la sesión
        
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM centros')
        cen_list = cursor.fetchall()
        cursor.close()
        connection.close()

        #session['cen_list'] = cen_list  # Guardar en la sesión

    elif request.method == 'POST':
        # Recuperar variables de formulario y fecha actual de la sesión
        var_centro = request.form.get('txtCentro')
        session['var_centro'] = var_centro  # Guardar en la sesión

        fecha_actual = session.get('fecha_actual')  # Obtener de la sesión

        # Obtener listado de pedidos del día
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        query = '''
            SELECT * FROM pivot_contro_dia WHERE fecha = %s and idcentro = %s;
        '''
        cursor.execute(query, (fecha_actual,var_centro))
        listado_ped = cursor.fetchall()
        cursor.close()
        connection.close()

        session['listado_ped'] = listado_ped  

        return redirect(url_for('menu_pedidos'))

    # Renderizar el template utilizando variables almacenadas en la sesión
    # cen_list = session.get('cen_list', [])
    # fecha_actual = session.get('fecha_actual', now.strftime('%Y-%m-%d'))

    return render_template('pedidos/ruta_pedidos.html', cen_list=cen_list, fecha_actual=fecha_actual)


@app.route('/control_pedidos/<string:var_centro>', methods=['GET','POST'])
def control_pedidos(var_centro):
    
    estado = 'A'    
    fecha_actual = now.strftime('%Y-%m-%d')

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    query = '''
        SELECT ruta,num_transporte,num_entrega,estado,count(idproducto) as total_productos 
        FROM pedidos 
        WHERE idcentro = %s and estado = %s and fecha = %s 
        GROUP BY ruta,num_transporte,num_entrega,estado
        '''
    values = (var_centro,estado,fecha_actual)
    cursor.execute(query, values)
    ped = cursor.fetchall()
    cursor.close()
    connection.close()
       
    return render_template('pedidos/lista_pedidos.html', ped=ped,fecha_actual=fecha_actual,var_centro=var_centro)

@app.route('/revision_pedidos/<string:var_centro>', methods=['GET','POST'])
def revision_pedidos(var_centro):
    
    estado = 'P'    
    fechaactual = session.get('fecha_actual')
    fecha_formateada = datetime.strptime(fechaactual[:10], "%Y-%m-%d").date()
    fechaactual = fecha_formateada
 
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    query = '''
        SELECT ruta,num_transporte,num_entrega,estado,count(idproducto) as total_productos 
        FROM pedidos 
        WHERE idcentro = %s and estado = %s and fecha = %s 
        GROUP BY ruta,num_transporte,num_entrega,estado
        '''
    values = (var_centro,estado,fechaactual)
    cursor.execute(query, values)
    ped_list = cursor.fetchall()
    cursor.close()
    connection.close()
       
    return render_template('pedidos/lista_pedidos_procesados.html', ped_list=ped_list,fechaactual=fechaactual,var_centro=var_centro)



@app.route('/edita_pedidos/<string:num_entrega>/<string:var_centro>/<string:fecha_actual>', methods=['GET', 'POST'])
def edita_pedidos(num_entrega,var_centro,fecha_actual):

    ventrega = num_entrega
    vcentro = var_centro
    fecha_formateada = datetime.strptime(fecha_actual[:10], "%Y-%m-%d").date()
    fecha_actual = fecha_formateada
    
    if 'registros' not in session:
        session['registros'] = []

    if request.method == 'POST':
        vcodigoEAN = request.form.get('codigoEAN')
        vcant_conteo = request.form.get('cant_conteo')

        # Validar existencia de códigoEAN en la tabla Productos

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        query = ('SELECT * FROM codigosEAN WHERE codigoEAN = %s')
        values = (vcodigoEAN,)
        cursor.execute(query, values)
        producto = cursor.fetchall()
        cursor.close()
        connection.close()
        
        if producto and float(vcant_conteo) >= 0:
            # Accede al primer resultado de la lista (un diccionario)
            producto_dict = producto[0]  # Renombra a producto_dict para mayor claridad
            
            # Recuperar la lista actual de registros de la sesión o inicializarla si no existe
            registros = session.get('registros', [])
            
            # Verificar si el código EAN ya está en la lista
            if any(registro['codigoEAN'] == vcodigoEAN for registro in registros):
                flash('Error: el código EAN ya ha sido ingresado', 'danger')
            else:
                nuevo_registro = {
                    'codigoEAN': vcodigoEAN,
                    'idproducto': producto_dict['idproducto'],  
                    'descripcion': producto_dict['descripcion'],  
                    'cant_conteo': vcant_conteo
                }
                registros.append(nuevo_registro)  # Agregar el nuevo registro
                session['registros'] = registros  # Guardar la lista actualizada en la sesión
                # flash('Producto agregado correctamente', 'success')
        else:
            flash('Error: código EAN no encontrado o cantidad inválida', 'danger')

    # Convertir registros a tabla HTML
    registros_guardados = session.get('registros', [])
    
    df = pd.DataFrame(registros_guardados)
   
    if not df.empty:
        columnas_ordenadas = ['codigoEAN', 'idproducto', 'descripcion', 'cant_conteo']
        df = df[columnas_ordenadas]
    
    df.rename(columns={
    'idproducto': 'Producto',
    'codigoEAN': 'Código EAN',
    'descripcion': 'Descripción',
    'cant_conteo': 'Cantidad'
    }, inplace=True)

    tabla_html = df.to_html(index=False, classes='table table-striped table-bordered table-hover', border=0)
    
    return render_template('pedidos/editar_pedidos.html', tabla=tabla_html, ventrega=ventrega,vcentro=vcentro,fecha_actual=fecha_actual)


@app.route('/edita_pedidos_procesados/<string:num_entrega>/<string:var_centro>/<string:fecha_actual>')
def edita_pedidos_procesados(num_entrega,var_centro,fecha_actual):

    ventrega = num_entrega
    vcentro = var_centro
    fecha_formateada = datetime.strptime(fecha_actual[:10], "%Y-%m-%d").date()
    fechaactual = fecha_formateada

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    query = '''
        SELECT ruta,PED.idproducto,PROD.descripcion AS descripcion,cantidad_pedido,cantidad_contada,cantidad_despachada,diferencial,MOT.motivo_descripcion
        FROM pedidos as PED
        LEFT OUTER JOIN productos AS PROD ON PED.idproducto = PROD.idproducto 
        LEFT OUTER JOIN motivos AS MOT ON PED.idmotivo = MOT.idmotivo 
        WHERE fecha = %s and num_entrega = %s 
        '''
    values = (fechaactual,ventrega)
    cursor.execute(query, values)
    registros_pedidos = cursor.fetchall()
    cursor.close()
    connection.close()
       
    df = pd.DataFrame(registros_pedidos)
    
    registros = df.to_dict(orient='records')
    
    total_pedido = df['cantidad_pedido'].sum()
    total_contada = df['cantidad_contada'].sum()
    total_despachada = df['cantidad_despachada'].sum()
   
        
    return render_template('pedidos/editar_pedidos_procesados.html', registros=registros, ventrega=ventrega,vcentro=vcentro,fecha_actual=fecha_actual,total_pedido=total_pedido,total_contada=total_contada,total_despachada=total_despachada)


@app.route('/guardar_pedidos/<string:num_entrega>/<string:var_centro>/<string:fecha_actual>', methods=['POST'])
def guardar_pedidos(num_entrega,var_centro,fecha_actual):
    
    registros_guardados = session.get('registros', [])

    ventrega = num_entrega
    vcentro = var_centro
    fecha_formateada = datetime.strptime(fecha_actual[:10], "%Y-%m-%d").date()
    fecha_actual = fecha_formateada
 
    if registros_guardados:
        for registro in registros_guardados:
            fecha = fecha_actual
            entrega=ventrega
            codigoEAN=registro['codigoEAN']
            idproducto=registro['idproducto']
            can_conteo=registro['cant_conteo']
                                      
            connection = get_db_connection()
            cursor = connection.cursor()
            query = 'INSERT INTO conteos VALUES (null,%s, %s,%s, %s, %s)'
            values = (fecha,entrega,codigoEAN,idproducto,can_conteo)                            
            cursor.execute(query, values)
            connection.commit()
            cursor.close()
            connection.close()
            
        # Elimina los registros de la sesión después de guardarlos
        session.pop('registros', None)
        
        # Redirigir a la ruta 'compara_pedidos' después de guardar
        return redirect(url_for('compara_pedidos', ventrega=ventrega,vcentro=vcentro,fecha_actual=fecha_actual))
    else:
        flash('No hay registros para guardar', 'danger')
        return redirect(url_for('control_pedidos',vcentro=vcentro))



@app.route('/regresar_control_pedidos/<string:var_centro>', methods=['POST'])
def regresar_control_pedidos(var_centro):
    session.pop('registros', None)  # Eliminar los registros de la sesión
    return redirect(url_for('control_pedidos',var_centro=var_centro, method='POST'))  # Regresa a 'control_pedidos' con método POST

@app.route('/compara_pedidos/<string:ventrega>/<string:vcentro>/<string:fecha_actual>', methods=['GET', 'POST'])
def compara_pedidos(ventrega, vcentro, fecha_actual):
    var_entrega = ventrega
    fecha_actual = datetime.strptime(fecha_actual[:10], "%Y-%m-%d").date()

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Obtener conteos y pedidos
    cursor.execute('SELECT * FROM conteos WHERE fecha = %s AND entrega = %s', (fecha_actual, var_entrega))
    conteo_registros = cursor.fetchall()

    cursor.execute('SELECT * FROM pedidos WHERE num_entrega = %s AND fecha = %s', (var_entrega, fecha_actual))
    pedidos = cursor.fetchall()

    # Si no se encontró ningún pedido
    if not pedidos:
        print("No se encontró el pedido.")
        cursor.close()
        connection.close()
        return render_template('pedidos/compara_pedidos.html', df_records=[], motivos=[], vEntrega=var_entrega, vcentro=vcentro, fecha_actual=fecha_actual)

    pedido_general = pedidos[0]
    vFecha = pedido_general['fecha']
    vruta = pedido_general['ruta']
    vidcliente = pedido_general['idcliente']
    vCentro = pedido_general['idcentro']
    vCliente = pedido_general['cliente']
    vNum_Transporte = pedido_general['num_transporte']

    for conteo in conteo_registros:
        idproducto = conteo['idproducto']
        can_conteo = conteo['can_conteo']

        # Buscar pedido específico
        pedido_especifico = next((p for p in pedidos if p['idproducto'] == idproducto), None)

        if pedido_especifico:
            diferencial = can_conteo - pedido_especifico['cantidad_pedido']
            cursor.execute('''
                UPDATE pedidos 
                SET cantidad_contada = %s, diferencial = %s, estado = 'P', valida = 3
                WHERE id = %s
            ''', (can_conteo, diferencial, pedido_especifico['id']))
        else:
            # Insertar nuevo pedido
            cursor.execute('''
                INSERT INTO pedidos (fecha, idcentro, idcliente, cliente, num_transporte, ruta, num_entrega, idproducto, 
                                     cantidad_pedido, cantidad_contada, cantidad_despachada, diferencial, estado, valida) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0, %s, 'P', 2)
            ''', (vFecha, vCentro, vidcliente, vCliente, vNum_Transporte, vruta, var_entrega, idproducto, 
                  0, can_conteo, can_conteo))

    # Actualización de los pedidos según la validación
    cursor.execute('''
        UPDATE pedidos 
        SET diferencial = cantidad_contada - cantidad_pedido, cantidad_despachada = cantidad_pedido, estado = 'P'
        WHERE num_entrega = %s AND fecha = %s AND valida <> 1
    ''', (var_entrega, fecha_actual))

    cursor.execute('''
        UPDATE pedidos 
        SET diferencial = cantidad_contada - cantidad_pedido, cantidad_despachada = 0, estado = 'P'
        WHERE num_entrega = %s AND fecha = %s AND valida = 1
    ''', (var_entrega, fecha_actual))

    # Obtener todos los pedidos actualizados
    cursor.execute('''
        SELECT p.*, pr.descripcion 
        FROM pedidos p 
        LEFT JOIN productos pr ON p.idproducto = pr.idproducto 
        WHERE p.num_entrega = %s AND p.fecha = %s
    ''', (var_entrega, fecha_actual))
    ped = cursor.fetchall()

    # Convertir a DataFrame
    column_order = ['id', 'fecha', 'idcentro', 'cliente', 'idcliente', 'num_transporte', 'ruta',
                    'num_entrega', 'validacion', 'idproducto', 'descripcion', 'cantidad_pedido', 'estado',
                    'cantidad_contada', 'cantidad_despachada', 'diferencial', 'idmotivo']
    df = pd.DataFrame(ped, columns=column_order)
    df = df.rename(columns={'cantidad_despachada': 'cantidaddespachada'})
    df_records = df.to_records(index=False)

        # Calcular totales
    total_cantidad_pedido = df['cantidad_pedido'].sum()
    total_cantidad_contada = df['cantidad_contada'].sum()
    total_cantidad_despachada = df['cantidaddespachada'].sum()


    # Obtener lista de motivos
    cursor.execute('SELECT * FROM motivos')
    mot_list = cursor.fetchall()

    connection.commit()
    cursor.close()
    connection.close()

    return render_template('pedidos/compara_pedidos.html', 
                           df_records=df_records, 
                           motivos=mot_list, 
                           vEntrega=var_entrega, 
                           vcentro=vcentro, 
                           fecha_actual=fecha_actual,
                           total_cantidad_pedido=total_cantidad_pedido,
                           total_cantidad_contada=total_cantidad_contada,
                           total_cantidad_despachada=total_cantidad_despachada)

@app.route('/update_motivos/<string:num_entrega>/<string:vcentro>/<string:fecha_actual>', methods=['POST'])
def update_motivos(num_entrega, vcentro,fecha_actual):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        # Actualizar cada campo en la base de datos
        for field_name, value in request.form.items():
            record_id = field_name.split('_')[1]

            if field_name.startswith('motivo_') and value:
                cursor.execute('UPDATE pedidos SET idmotivo = %s WHERE id = %s', (value, record_id))
            elif field_name.startswith('cantidaddespachada_') and value:
                cursor.execute('UPDATE pedidos SET cantidad_despachada = %s WHERE id = %s', (value, record_id))
        flash('Datos actualizados exitosamente.', 'success')
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        cursor.close()
        connection.close()

    # Redirigir de vuelta a compara_pedidos después de actualizar
    return redirect(url_for('aprobacion_pedidos', num_entrega=num_entrega, vcentro=vcentro, fecha_actual=fecha_actual))

@app.route('/aprobacion_pedidos/<string:num_entrega>/<string:vcentro>/<string:fecha_actual>')
def aprobacion_pedidos(num_entrega,vcentro,fecha_actual):
    
    estado = 'P'    
    fecha_formateada = datetime.strptime(fecha_actual[:10], "%Y-%m-%d").date()
    vfecha = fecha_formateada
    ventrega = num_entrega
 
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    query = '''
        SELECT ruta,PED.idproducto,PROD.descripcion AS descripcion,cantidad_pedido,cantidad_contada,cantidad_despachada,diferencial,MOT.motivo_descripcion
        FROM pedidos as PED
        LEFT OUTER JOIN productos AS PROD ON PED.idproducto = PROD.idproducto 
        LEFT OUTER JOIN motivos AS MOT ON PED.idmotivo = MOT.idmotivo
        WHERE fecha = %s and num_entrega = %s and idcentro = %s
        '''
    values = (vfecha,ventrega,vcentro)
    cursor.execute(query, values)
    ped_list = cursor.fetchall()
    cursor.close()
    connection.close()
    
    df = pd.DataFrame(ped_list)
    
    registros = df.to_dict(orient='records')
    
    total_pedido = df['cantidad_pedido'].sum()
    total_contada = df['cantidad_contada'].sum()
    total_despachada = df['cantidad_despachada'].sum()
       
    return render_template('pedidos/lista_pedidos_aprobados.html', 
                           registros=registros,
                           vfecha=vfecha,
                           vcentro=vcentro,
                           ventrega=ventrega,
                           total_pedido=total_pedido,
                           total_contada=total_contada,
                           total_despachada=total_despachada)

   
@app.route('/analitica_pedidos', methods=['GET', 'POST'])
def analitica_pedidos():
    
    fecha_actual = now.strftime('%Y-%m-%d')
    
    if request.method == 'GET':
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM centros')
        cen_list = cursor.fetchall()
        cursor.close()
        connection.close()
    elif request.method == 'POST':
        fecha_inicial = request.form.get('txtFechaInicial')       
        fecha_final = request.form.get('txtFechaFinal')       
        
        #   fecha_formateada = datetime.strptime(fecha_actual[:10], "%Y-%m-%d").date()
        #   fecha_actual = fecha_formateada

        
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        ped = '''
            SELECT *, productos.descripcion,motivos.motivo_descripcion 
            FROM pedidos 
            LEFT OUTER JOIN productos ON pedidos.idproducto = productos.idproducto
            LEFT OUTER JOIN motivos ON pedidos.idmotivo = motivos.idmotivo
            WHERE fecha >= %s and fecha <= %s
            '''
        values=(fecha_inicial,fecha_final)
        cursor.execute(ped,values)
        ped = cursor.fetchall()
        
        ped1 = "SELECT * FROM pivot_contro_dia"
        cursor.execute(ped1)
        ped1 = cursor.fetchall()
        
        connection.commit()
        cursor.close()
        connection.close()
        
        for record in ped:
            record.pop('_sa_instance_state', None)
        
        column_order = ['id', 'fecha','idcentro', 'idcliente','cliente', 'num_transporte','ruta'
                        ,'num_entrega','validacion','idproducto','descripcion','cantidad_pedido','estado'
                        ,'cantidad_contada','cantidad_despachada','diferencial','idmotivo','motivo']
        
        # Crea el DataFrame
        df = pd.DataFrame(ped, columns=column_order)
        df_records = df.to_records(index=False)

        for record in ped1:
            record.pop('_sa_instance_state', None)
        
        
        df1 = pd.DataFrame(ped1)
        df_records1 = df1.to_records(index=False)
        
        return render_template('pedidos/analitica_pedidos.html',df_records=df_records,df_records1=df_records1)


    return render_template('pedidos/ruta_pedidos.html',cen_list=cen_list,fecha_actual=fecha_actual)

    
    
    
 


##################################################################

def protected():
    return "<h1>Esta es una vista protegida, solo para usuarios autenticados.</h1>"

def status_401(error):
    return render_template('401.html'), 401


def status_404(error):
    return render_template('404.html'), 404

csrf.init_app(app)
app.register_error_handler(401, status_401)
app.register_error_handler(404, status_404)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)