#--------------------------------------------------------------------
# Pip install mysql-connector-python
import mysql.connector
import mysql.connector.errorcode

# Pip install Flask
from flask import Flask, request, jsonify, render_template
from flask import request

# Pip install flask-cors
from flask_cors import CORS


# Pip install Werkzeug
from werkzeug.utils import secure_filename

# 
import os
import time


#Creamos una instancia de la aplicación Flask
app = Flask(__name__)
CORS(app)  


# -------------------------------------------------------------------
# Definimos la clase Catalogo
# -------------------------------------------------------------------

class Catalogo:
        
    #----------------------------------------------------------------
    # Constructor de la clase  

    def __init__(self, host, user, password, database):
              
        self.conn = mysql.connector.connect(
            host = host,
            # port= port,
            user = user,
            password = password
        )        
        
        self.cursor = self.conn.cursor()
     
        # Intentamos seleccionar la base de datos
        try:
            self.cursor.execute(f"USE {database}")
        except mysql.connector.Error as err:

            # Si la base de datos no existe, la creamos
            if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
                self.conn.database = database
            else:
                raise err

        # Una vez que la base de datos está establecida, creamos la tabla si no existe
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS recetas (
            codigo INT AUTO_INCREMENT PRIMARY KEY,
            titulo VARCHAR(255) NOT NULL,
            duracion VARCHAR(20),
            dificultad VARCHAR(20),
            ingredientes VARCHAR(300) NOT NULL,
            procedimiento VARCHAR (500) NOT NULL,
            imagen_url VARCHAR(255)
            )''')

        # Guardamos los cambios en la base de datos.
        self.conn.commit()

        # Cerrar el cursor inicial y abrir uno nuevo con el parámetro dictionary=True
        self.cursor.close()
        self.cursor = self.conn.cursor(dictionary=True)        
        

    # -------------------------------------------------------------------
    # Método para agregar una receta
    # -------------------------------------------------------------------
    def agregar_receta(self, titulo, duracion, dificultad, ingredientes, procedimiento, imagen_url):
        
        sql = "INSERT INTO recetas (titulo, duracion, dificultad, ingredientes, procedimiento, imagen_url) VALUES (%s, %s, %s, %s, %s, %s)"
        
        valores = (titulo, duracion, dificultad, ingredientes, procedimiento, imagen_url)

        self.cursor.execute(sql, valores) #Ejecuta
        self.conn.commit() #Guarda
        return self.cursor.lastrowid 


    # -------------------------------------------------------------------
    # Método para consultar una receta a partir de su código
    # -------------------------------------------------------------------
    def consultar_receta(self, codigo):

        self.cursor.execute(f"SELECT * FROM recetas WHERE codigo = {codigo}")
        return self.cursor.fetchone() 

    # -------------------------------------------------------------------
    # Método para modificar los datos de una receta a partir de su código
    # -------------------------------------------------------------------
    def modificar_receta(self, codigo, nuevo_titulo, nueva_duracion, nueva_dificultad, nuevos_ingredientes, nuevo_procedimiento, nueva_imagen):


        sql = "UPDATE recetas SET titulo =%s, duracion=%s, dificultad=%s, ingredientes=%s, procedimiento=%s, imagen_url=%s WHERE codigo = %s"

        valores = (nuevo_titulo, nueva_duracion, nueva_dificultad, nuevos_ingredientes, nuevo_procedimiento, nueva_imagen, codigo)

        self.cursor.execute(sql, valores)
        self.conn.commit() #Guardo
        return self.cursor.rowcount > 0
       

    # -------------------------------------------------------------------
    # Método para obtener un listado de las recetas
    # -------------------------------------------------------------------
    def listar_recetas(self):

        self.cursor.execute("SELECT * FROM recetas")
        recetas = self.cursor.fetchall() 
        return recetas


    # -------------------------------------------------------------------
    # Método para eliminar una receta a partir de su código
    # -------------------------------------------------------------------
    def eliminar_receta(self, codigo):

        # receta_eliminada = receta['titulo']
        # print(f"Receta {receta_eliminada} eliminada.")

        self.cursor.execute(f"DELETE FROM recetas WHERE codigo = {codigo}")
        self.conn.commit() #Guardo
        return self.cursor.rowcount > 0
    

    # -------------------------------------------------------------------
    # Método para mostrar los datos de una receta según su código
    # ------------------------------------------------------------------- 
        def mostrar_receta(self, codigo):
            receta = self.consultar_receta(codigo)
            if receta:
                print("-"*50)
                print(f"Título de la receta...: {receta['titulo']}")
                print(f"Dificultad............: {receta['dificultad']}")
                print(f"Duración..............: {receta['duracion']}")
                print(f"Ingredientes..........: {receta['ingredientes']}")
                print(f"Procedimiento.........: {receta['procedimiento']}")
                print(f"Imagen................: {receta['imagen']}")
                print("-"*50)
            else:
                 print("Receta no encontrada.")




# -------------------------------------------------------------------
# Cuerpo del Programa
# -------------------------------------------------------------------
# catalogo = Catalogo(host='localhost', port=3307, user='root', password='root', database='recetario')
catalogo = Catalogo(host='julimalagamba.mysql.pythonanywhere-services.com', user='julimalagamba', password='#recetario', database='julimalagamba$recetario')



# ***********************************************************************************************************************************SE VA
#Agregamos recetas
# catalogo.agregar_receta("Mousse de limón", '30 minutos', 'media', "ingrediente 1, ingrediente 2, ingrediente 3, ingrediente 4", "mezclar, batir, hornear", 'limon.jpg')
# catalogo.agregar_receta('Tarta de frutilla', '40 minutos', 'media', "ingrediente 1, ingrediente 2, ingrediente 3, ingrediente 4", 
# "mezclar, batir, hornear", 'frutilla.jpg')
# catalogo.agregar_receta('Lemon pie', '30 minutos', 'alta', "ingrediente 1, ingrediente 2, ingrediente 3, ingrediente 4",
# "mezclar, batir, hornear", 'lemon-pie.jpg')
# catalogo.agregar_receta('Carrot cake', '60 minutos', 'media-alta', "ingrediente 1, ingrediente 2, ingrediente 3, ingrediente 4",
# "mezclar, batir, hornear", 'carrot.jpg')
# catalogo.agregar_receta('Cuadraditos de frutilla', '45 minutos', 'dificil', "ingrediente 1, ingrediente 2, ingrediente 3, ingrediente 4",
# "mezclar, batir, hornear", 'cuadraditos.jpg')





# Carpeta para guardar las imagenes.
# RUTA_DESTINO = './static/imagenes/'

#Al subir al servidor, deberá utilizarse la siguiente ruta. USUARIO debe ser reemplazado por el nombre de usuario de Pythonanywhere
RUTA_DESTINO = '/home/julimalagamba/mysite/static/imagenes'


#--------------------------------------------------------------------
# Listar todos los productos
#--------------------------------------------------------------------

@app.route("/recetas", methods=["GET"])
def listar_recetas():
    recetas = catalogo.listar_recetas()
    return jsonify(recetas)


#--------------------------------------------------------------------
# Mostrar un sólo producto según su código
#--------------------------------------------------------------------

@app.route("/recetas/<int:codigo>", methods=["GET"])
def mostrar_receta(codigo):
    receta = catalogo.consultar_receta(codigo)
    if receta:
        return jsonify(receta), 201
    else:
        return "Receta no encontrada", 404


#--------------------------------------------------------------------
# Agregar un producto
#--------------------------------------------------------------------
@app.route("/recetas", methods=["POST"])

def agregar_receta():
    #Recojo los datos del form
    titulo = request.form['titulo']
    duracion = request.form['duracion']
    dificultad = request.form['dificultad']
    ingredientes = request.form['ingredientes']  
    procedimiento = request.form['procedimiento']  
    imagen = request.files['imagen_url']
    nombre_imagen=""

    
    # Genero el nombre de la imagen
    nombre_imagen = secure_filename(imagen.filename) #Chequea el nombre del archivo de la imagen, asegurándose de que sea seguro para guardar en el sistema de archivos
    nombre_base, extension = os.path.splitext(nombre_imagen) #Separa el nombre del archivo de su extensión.
    nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}" #Genera un nuevo nombre para la imagen usando un timestamp, para evitar sobreescrituras y conflictos de nombres.

    nuevo_codigo = catalogo.agregar_receta(titulo, duracion, dificultad, ingredientes, procedimiento, nombre_imagen)
    if nuevo_codigo:    
        imagen.save(os.path.join(RUTA_DESTINO, nombre_imagen))

        return jsonify({"mensaje": "Receta agregada correctamente.", "codigo": nuevo_codigo, "imagen": nombre_imagen}), 201
    else:

        return jsonify({"mensaje": "Error al agregar la receta."}), 500
    

#--------------------------------------------------------------------
# Modificar un producto según su código
#--------------------------------------------------------------------
@app.route("/recetas/<int:codigo>", methods=["PUT"])

def modificar_receta(codigo):
    #Se recuperan los nuevos datos del formulario
    nuevo_titulo = request.form.get("titulo")
    nueva_duracion = request.form.get("duracion")
    nueva_dificultad = request.form.get("dificultad")
    nuevos_ingredientes = request.form.get("ingredientes")
    nuevo_procedimiento = request.form.get("procedimiento")
    
    
    # Verifica si se proporcionó una nueva imagen
    if 'imagen' in request.files:
        imagen = request.files['imagen']
        # Procesamiento de la imagen
        nombre_imagen = secure_filename(imagen.filename) 
        nombre_base, extension = os.path.splitext(nombre_imagen) 
        nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}" 

        # Guardar la imagen en el servidor
        imagen.save(os.path.join(RUTA_DESTINO, nombre_imagen))
        
        # Busco el producto guardado
        receta= catalogo.consultar_receta(codigo)
        if receta: # Si existe el producto...
            imagen_vieja = receta["imagen_url"]
            # Armo la ruta a la imagen
            ruta_imagen = os.path.join(RUTA_DESTINO, imagen_vieja)

            # Y si existe la borro.
            if os.path.exists(ruta_imagen):
                os.remove(ruta_imagen)
    
    else:
        # Si no se proporciona una nueva imagen, simplemente usa la imagen existente 
        receta= catalogo.consultar_receta(codigo)
        if receta:
            nombre_imagen = receta["imagen_url"]


    # Se llama al método modificar_producto pasando el codigo del producto y los nuevos datos.
    if catalogo.modificar_receta(codigo, nuevo_titulo, nueva_duracion, nueva_dificultad, nuevos_ingredientes, nuevo_procedimiento, nombre_imagen):
        
        #Si la actualización es exitosa, se devuelve una respuesta JSON con un mensaje de éxito y un código de estado HTTP 200 (OK).
        return jsonify({"mensaje": "Receta modificada"}), 200
    else:
        
        return jsonify({"mensaje": "Receta no encontrada"}), 403



#--------------------------------------------------------------------
# Eliminar un producto según su código
#--------------------------------------------------------------------
@app.route("/recetas/<int:codigo>", methods=["DELETE"])
def eliminar_receta(codigo):
    # Busco la receta en la base de datos
    receta = catalogo.consultar_receta(codigo)
    if receta: # Si la receta existe, verifica si hay una imagen asociada en el servidor.
        imagen_vieja = receta["imagen_url"]
        # Armo la ruta a la imagen
        ruta_imagen = os.path.join(RUTA_DESTINO, imagen_vieja)

        # Y si existe, la elimina del sistema de archivos.
        if os.path.exists(ruta_imagen):
            os.remove(ruta_imagen)

        # Luego, elimina el producto del catálogo
        if catalogo.eliminar_receta(codigo):
            #Si la receta se elimina correctamente, se devuelve una respuesta JSON con un mensaje de éxito y un código de estado HTTP 200 (OK).
            return jsonify({"mensaje": "Receta eliminada"}), 200
        else:
            #Si ocurre un error durante la eliminación (por ejemplo, si la receta no se puede eliminar de la base de datos por alguna razón), se devuelve un mensaje de error con un código de estado HTTP 500 (Error Interno del Servidor).
            return jsonify({"mensaje": "Error al eliminar la receta"}), 500
    else:
        #Si la receta no se encuentra (por ejemplo, si no existe una receta con el codigo proporcionado), se devuelve un mensaje de error con un código de estado HTTP 404 (No Encontrado). 
        return jsonify({"mensaje": "Receta no encontrada"}), 404


#----------------------- FLASK ------------------------------
if __name__ == "__main__":
    app.run(debug=True)