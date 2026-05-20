"""
Módulo: repositorios.py
Capa de acceso a datos (DAO/Repository pattern).
Cada clase maneja las operaciones CRUD de una colección en MongoDB.
Si MongoDB no está disponible, persiste los datos en archivos JSON dentro
de la carpeta data/ del proyecto (modo local).
"""

import json
import os
import uuid
from datetime import datetime
from bson import ObjectId
from database.db_connection import DatabaseConnection


# ── Serialización de datetime en JSON ────────────────────────────────────────

def _json_encoder(obj):
    """Convierte datetime a un dict marcado para poder recuperarlo al cargar."""
    if isinstance(obj, datetime):
        return {"__datetime__": obj.isoformat()}
    raise TypeError(f"Tipo no serializable: {type(obj)}")


def _json_decoder(dct: dict):
    """Convierte de vuelta los dicts marcados a datetime al cargar JSON."""
    if "__datetime__" in dct:
        return datetime.fromisoformat(dct["__datetime__"])
    return dct


# ── Repositorio base ──────────────────────────────────────────────────────────

class BaseRepositorio:
    """
    Clase base para todos los repositorios.

    En modo local (sin MongoDB) usa un almacén compartido a nivel de CLASE
    indexado por nombre de colección, y lo persiste en archivos JSON dentro
    de data/<coleccion>.json para que los datos sobrevivan cambios de pestaña
    y reinicios de la aplicación.
    """

    # Almacén compartido entre TODAS las instancias de la misma colección.
    # Clave: nombre de colección → Valor: lista de documentos.
    _almacen: dict[str, list] = {}

    # Directorio donde se guardan los archivos JSON.
    _DIR_DATOS: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"
    )

    def __init__(self, coleccion_nombre: str):
        self._coleccion_nombre = coleccion_nombre
        self._db_conn = DatabaseConnection.get_instance()

        # Inicializar la colección sólo la primera vez que alguien la usa.
        if coleccion_nombre not in BaseRepositorio._almacen:
            BaseRepositorio._almacen[coleccion_nombre] = []
            self._cargar_json()

    # ── Helpers JSON ─────────────────────────────────────────────────────────

    def _ruta_json(self) -> str:
        os.makedirs(BaseRepositorio._DIR_DATOS, exist_ok=True)
        return os.path.join(BaseRepositorio._DIR_DATOS, f"{self._coleccion_nombre}.json")

    def _cargar_json(self):
        ruta = self._ruta_json()
        if os.path.exists(ruta):
            try:
                with open(ruta, "r", encoding="utf-8") as f:
                    BaseRepositorio._almacen[self._coleccion_nombre] = json.load(
                        f, object_hook=_json_decoder
                    )
            except Exception as e:
                print(f"[Repositorio] Error cargando {self._coleccion_nombre}: {e}")

    def _guardar_json(self):
        try:
            with open(self._ruta_json(), "w", encoding="utf-8") as f:
                json.dump(
                    BaseRepositorio._almacen[self._coleccion_nombre],
                    f, ensure_ascii=False, indent=2, default=_json_encoder
                )
        except Exception as e:
            print(f"[Repositorio] Error guardando {self._coleccion_nombre}: {e}")

    # ── Acceso a la colección en memoria ─────────────────────────────────────

    @property
    def _memoria(self) -> list:
        return BaseRepositorio._almacen[self._coleccion_nombre]

    def _get_col(self):
        return self._db_conn.get_collection(self._coleccion_nombre)

    def _usar_mongo(self) -> bool:
        return self._db_conn.is_connected

    # ── CRUD ──────────────────────────────────────────────────────────────────

    def insertar(self, documento: dict) -> str:
        """Inserta un documento. Retorna el ID generado."""
        if self._usar_mongo():
            resultado = self._get_col().insert_one(documento)
            return str(resultado.inserted_id)

        doc_id = str(uuid.uuid4())[:24]
        documento["_id"] = doc_id
        self._memoria.append(documento)
        self._guardar_json()
        return doc_id

    def buscar_todos(self) -> list:
        if self._usar_mongo():
            docs = list(self._get_col().find())
            for d in docs:
                d["_id"] = str(d["_id"])
            return docs
        return list(self._memoria)

    def buscar_por_id(self, doc_id: str) -> dict:
        if self._usar_mongo():
            try:
                doc = self._get_col().find_one({"_id": ObjectId(doc_id)})
                if doc:
                    doc["_id"] = str(doc["_id"])
                return doc
            except Exception:
                return None
        return next((d for d in self._memoria if d.get("_id") == doc_id), None)

    def buscar_por_campo(self, campo: str, valor) -> list:
        if self._usar_mongo():
            docs = list(self._get_col().find({campo: valor}))
            for d in docs:
                d["_id"] = str(d["_id"])
            return docs
        return [d for d in self._memoria if d.get(campo) == valor]

    def buscar_uno_por_campo(self, campo: str, valor) -> dict:
        if self._usar_mongo():
            doc = self._get_col().find_one({campo: valor})
            if doc:
                doc["_id"] = str(doc["_id"])
            return doc
        return next((d for d in self._memoria if d.get(campo) == valor), None)

    def actualizar(self, doc_id: str, datos: dict) -> bool:
        if self._usar_mongo():
            try:
                res = self._get_col().update_one(
                    {"_id": ObjectId(doc_id)},
                    {"$set": datos}
                )
                return res.matched_count > 0
            except Exception:
                return False
        for i, d in enumerate(self._memoria):
            if d.get("_id") == doc_id:
                self._memoria[i].update(datos)
                self._guardar_json()
                return True
        return False

    def eliminar(self, doc_id: str) -> bool:
        if self._usar_mongo():
            try:
                res = self._get_col().delete_one({"_id": ObjectId(doc_id)})
                return res.deleted_count > 0
            except Exception:
                return False
        coleccion = BaseRepositorio._almacen[self._coleccion_nombre]
        original = len(coleccion)
        BaseRepositorio._almacen[self._coleccion_nombre] = [
            d for d in coleccion if d.get("_id") != doc_id
        ]
        if len(BaseRepositorio._almacen[self._coleccion_nombre]) < original:
            self._guardar_json()
            return True
        return False

    def contar(self) -> int:
        if self._usar_mongo():
            return self._get_col().count_documents({})
        return len(self._memoria)


# ── Repositorios especializados ───────────────────────────────────────────────

class ClienteRepositorio(BaseRepositorio):
    def __init__(self):
        super().__init__("clientes")

    def buscar_por_cedula(self, cedula: str) -> dict:
        return self.buscar_uno_por_campo("cedula", cedula)

    def buscar_por_nombre(self, texto: str) -> list:
        if self._usar_mongo():
            docs = list(self._get_col().find({
                "$or": [
                    {"nombre": {"$regex": texto, "$options": "i"}},
                    {"apellido": {"$regex": texto, "$options": "i"}}
                ]
            }))
            for d in docs:
                d["_id"] = str(d["_id"])
            return docs
        texto_lower = texto.lower()
        return [d for d in self._memoria
                if texto_lower in d.get("nombre", "").lower()
                or texto_lower in d.get("apellido", "").lower()]


class VeterinarioRepositorio(BaseRepositorio):
    def __init__(self):
        super().__init__("veterinarios")

    def buscar_por_especialidad(self, especialidad: str) -> list:
        return self.buscar_por_campo("especialidad", especialidad)

    def buscar_por_cedula(self, cedula: str) -> dict:
        return self.buscar_uno_por_campo("cedula", cedula)


class AnimalRepositorio(BaseRepositorio):
    def __init__(self):
        super().__init__("animales")

    def buscar_por_cliente(self, cliente_id: str) -> list:
        return self.buscar_por_campo("cliente_id", cliente_id)

    def buscar_por_tipo(self, tipo: str) -> list:
        return self.buscar_por_campo("tipo", tipo)


class CitaRepositorio(BaseRepositorio):
    def __init__(self):
        super().__init__("citas")

    def buscar_por_veterinario(self, veterinario_id: str) -> list:
        return self.buscar_por_campo("veterinario_id", veterinario_id)

    def buscar_por_fecha(self, fecha: datetime) -> list:
        if self._usar_mongo():
            inicio = fecha.replace(hour=0, minute=0, second=0)
            fin = fecha.replace(hour=23, minute=59, second=59)
            docs = list(self._get_col().find({
                "fecha_hora": {"$gte": inicio, "$lte": fin}
            }))
            for d in docs:
                d["_id"] = str(d["_id"])
            return docs
        fecha_str = fecha.strftime("%Y-%m-%d")
        return [d for d in self._memoria
                if isinstance(d.get("fecha_hora"), datetime)
                and d["fecha_hora"].strftime("%Y-%m-%d") == fecha_str]

    def buscar_pendientes(self) -> list:
        return self.buscar_por_campo("estado", "Pendiente")


class HistorialRepositorio(BaseRepositorio):
    def __init__(self):
        super().__init__("historiales")

    def buscar_por_animal(self, animal_id: str) -> list:
        return self.buscar_por_campo("animal_id", animal_id)
