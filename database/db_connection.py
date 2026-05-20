"""
Módulo: db_connection.py
Patrón de Diseño: SINGLETON
Garantiza que exista una sola instancia de la conexión a MongoDB en toda la app.
"""

import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# Carga el archivo .env si python-dotenv está disponible
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))
except ImportError:
    pass  # python-dotenv no instalado; usa variables de entorno del sistema


class DatabaseConnection:
    """
    Singleton para la conexión a MongoDB.
    
    Solo se crea UNA instancia de MongoClient en todo el ciclo de vida
    de la aplicación. Cualquier módulo que llame a DatabaseConnection.get_instance()
    recibirá la misma conexión.
    """

    _instance = None          # La única instancia (atributo de clase)
    _client = None
    _db = None
    _connected = False

    def __new__(cls):
        """Sobreescribe __new__ para garantizar una sola instancia."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def connect(self, uri: str = None, db_name: str = "vetcare_pro"):
        """
        Establece la conexión a MongoDB.
        Si ya está conectado, no hace nada (Singleton).
        """
        if self._connected:
            return True

        if uri is None:
            uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

        try:
            self._client = MongoClient(uri, serverSelectionTimeoutMS=3000)
            # Verificar conexión real
            self._client.admin.command('ping')
            self._db = self._client[db_name]
            self._connected = True
            print(f"✅ MongoDB conectado: {db_name}")
            self._create_indexes()
            return True
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"⚠️  MongoDB no disponible: {e}")
            self._connected = False
            return False

    def _create_indexes(self):
        """Crea índices para mejorar el rendimiento de las consultas."""
        try:
            self._db["clientes"].create_index("cedula", unique=True)
            self._db["veterinarios"].create_index("cedula", unique=True)
            self._db["animales"].create_index("cliente_id")
            self._db["citas"].create_index([("fecha_hora", 1), ("veterinario_id", 1)])
        except Exception:
            pass

    @classmethod
    def get_instance(cls):
        """Punto de acceso global al Singleton."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_db(self):
        """Retorna la base de datos. None si no hay conexión."""
        return self._db

    def get_collection(self, name: str):
        """Retorna una colección de MongoDB."""
        if self._db is not None:
            return self._db[name]
        return None

    @property
    def is_connected(self):
        return self._connected

    def disconnect(self):
        if self._client:
            self._client.close()
            self._connected = False
            DatabaseConnection._instance = None
            print("🔌 MongoDB desconectado.")
