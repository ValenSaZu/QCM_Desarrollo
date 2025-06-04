
Pasos a seguir para usar en pycharm:
-
En PyCharm → File → Project from Version Control 
-

- Colocar el Url del repositorio y darle a clone
- Se abrira una ventana para seleccionar la version de Python seleccionas la version Python 3.12. Automaticamente se te instala las dependencias. 

PostgresSQL 17
-
- Ubicarse en el archivo: **infrastructure → bd → conexion.py**
- Tener instalado PosgresSQL 17. 
- Colocar correctamente el Host, Puerto, el nombre de la Base de datos (QCM), usuario (postgres) y la contraseña (1234)
- verificar que esta conectada la base de datos

Ejecución
-
- Ejecutar el archivo **main.py**

Estructura
-
En main.py → handler.py → app/intefaces → app/controllers → domain/entities 
- handler.py  = Se encarga de manejar los endpoints y ApiRest. 