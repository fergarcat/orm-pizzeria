#IMPORTAR LIBRERÍAS
import os
from dotenv import load_dotenv #PARA CARGAR VARIABLES DE ENTORNO DESDE EL .ENV
from sqlalchemy import create_engine, Column, Integer, String, inspect, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

#🔹 ESTABLECEMOS VALORES PARA LA CADENA DE CONEXIÓN
#FUNCIÓN PARA CAMBIO DE BASE LOCAL SQLITE A POSTGRES SEGÚN VARIABLES DE ENTORNO
def get_db_url(ConnectLocalSQLite): 
    if ConnectLocalSQLite == True:      #Conecta con nuestra db SQLite local
        os.getenv("LOCALDB_URL")
    elif ConnectLocalSQLite == False:   #Conecta con la db alternativa de postgres
        return (f'postgresql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}')


# 🔹 ESTABLECEMOS EL MOTOR DE CONEXIÓN
# El engine es el punto de entrada para que SQLAlchemy se comunique con la base de datos. 
# Se encarga de administrar la conexión y traducir las consultas Python a SQL.
#engine = create_engine(connection_string(), echo=True)

engine = create_engine(get_db_url(True), echo = True)

# 🗺 BASE → Define las tablas y estructura de datos mediante clases ORM.
# 🔹 DEFINIMOS LA BASE ORM
# SQLAlchemy permite definir modelos de datos usando declarative_base().
# Este objeto es la base de todas las clases de modelo.
Base = declarative_base()

#DEFINIMOS EL MODELO DE DATOS EN LA BASE: TABLAS PLATOS E INGREDIENTES
class Plato(Base):
    __tablename__ = "platos"
    id = Column(Integer, primary_key = True)
    nombre_plato = Column(String, nullable = False)
    def __repr__(self):
        return f"Plato={self.nombre_plato}"

class Ingrediente(Base):
    __tablename__ = "ingredientes"
    id = Column(Integer, primary_key = True, autoincrement = True)
    id_plato = Column(Integer, ForeignKey("platos.id"), nullable = False)
    nombre_ingrediente = Column(String, nullable = False)

    rlc_platos = relationship("Plato",backref="ingredientes")
    def __repr__(self):
        return f"Ingrediente={self.nombre_ingrediente}"

#CREAMOS LA DB Y TABLAS SI NO EXISTEN
Base.metadata.create_all(engine)

## FUNCIONES DISPONIBLES PARA USAR EN EL COMMIT
# INSPECCIÓN DE TABLAS
def muestra_tablas():
    inspector = inspect(engine)
    print(inspector.get_table_names())
    session.commit()

##  DEFINIMOS NUESTRO CRUD
#   INSERT
def nuevo_plato(nuevo_id, nuevo_nombre):
    nuevo_plato = Plato(id = nuevo_id, nombre_plato=nuevo_nombre)
    session.add(nuevo_plato)
    session.commit()
def nuevo_ingrediente(nuevo_id_plato, nuevo_nombre):
    nuevo_ingrediente = Ingrediente(id_plato = nuevo_id_plato, nombre_ingrediente=nuevo_nombre)
    session.add(nuevo_ingrediente)
    session.commit()

#   READ
def consultar_plato_id(id_buscado):
    platos = session.query(Plato).filter_by(id=id_buscado).first()
    print("Plato buscado:", platos)
    session.commit()
def consulta_ingredientes():
    ingredientes = session.query(Ingrediente, Plato).join(Plato).all()
    print(ingredientes)
    session.commit()
def consulta_platos_con_ingredientes():
    platos = session.query(Plato, Ingrediente).outerjoin(Ingrediente, Plato.id == Ingrediente.id_plato).all()
    for plato, ingrediente in platos:
        print(f"{plato} - {ingrediente}")

#   UPDATE
def actualizar_plato_por_id(id_buscado,nuevo_nombre):
    platos = session.query(Plato).filter_by(id = id_buscado).first()
    if platos:
        platos.nombre_plato = nuevo_nombre
    session.commit()

#   DELETE
def borrar_plato(id_buscado):
    platos = session.query(Plato).filter_by(id = id_buscado).first()
    if platos:
        session.delete(platos)
        session.commit()
        print("Plato eliminado", platos)


# 🧠 SESSION → Maneja las transacciones y consultas de manera eficiente.
#ABRIMOS LA SESIÓN
# Por buscar una similitud, la sesión sería como el Staging Area de GIT
# Todas las operaciones que se hagan en la sesión, no se aplicarán en la Base de Datos
# hasta que ejecutemos session.commit()
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

# EJECUTAMOS FUNCIONES CRUD DENTRO DE NUESTRA SESIÓN
#   INTENTA EJECUTAR LA FUNCIÓN CON SU COMMIT
try: 
    consulta_platos_con_ingredientes()
    # consulta_ingredientes()
#   CAPTURA LA EXCEPCIÓN EN CASO DE HABER ERROR
except Exception as e: 
    os.system('cls')
    print(f'{type(e).__name__.upper()}')
    print('\n')
    print(f'Error in database: {e}')
    print('\n')
    input("Press ENTER...")    

session.close()