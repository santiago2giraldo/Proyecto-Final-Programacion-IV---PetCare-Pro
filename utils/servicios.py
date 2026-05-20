"""
Módulo: servicios.py
Capa de servicios: lógica de negocio entre la UI y los repositorios.
Cada servicio orquesta modelos + repositorios + patrones.
"""

from datetime import datetime
from models.persona import Cliente, Veterinario, Recepcionista
from models.animal import Perro, Gato, Ave, Reptil
from models.cita import Cita, HistorialMedico
from database.repositorios import (ClienteRepositorio, VeterinarioRepositorio,
                                   AnimalRepositorio, CitaRepositorio, HistorialRepositorio)
from patterns.observer import gestor_citas_global


# ─────────────────────────────────────────
# SERVICIO DE CLIENTES
# ─────────────────────────────────────────
class ServicioCliente:
    def __init__(self):
        self._repo = ClienteRepositorio()

    def registrar(self, nombre, apellido, cedula, telefono, email, direccion="") -> tuple[bool, str]:
        if self._repo.buscar_por_cedula(cedula):
            return False, f"Ya existe un cliente con cédula {cedula}."
        try:
            cliente = Cliente(nombre, apellido, cedula, telefono, email, direccion)
            doc_id = self._repo.insertar(cliente.to_dict())
            return True, doc_id
        except ValueError as e:
            return False, str(e)

    def listar(self) -> list:
        return self._repo.buscar_todos()

    def buscar_por_cedula(self, cedula: str) -> dict:
        return self._repo.buscar_por_cedula(cedula)

    def buscar_por_nombre(self, texto: str) -> list:
        return self._repo.buscar_por_nombre(texto)

    def actualizar(self, doc_id: str, datos: dict) -> bool:
        return self._repo.actualizar(doc_id, datos)

    def eliminar(self, doc_id: str) -> bool:
        return self._repo.eliminar(doc_id)

    def contar(self) -> int:
        return self._repo.contar()


# ─────────────────────────────────────────
# SERVICIO DE VETERINARIOS
# ─────────────────────────────────────────
class ServicioVeterinario:
    def __init__(self):
        self._repo = VeterinarioRepositorio()

    def registrar(self, nombre, apellido, cedula, telefono, email,
                  especialidad="Medicina General", tarjeta="") -> tuple[bool, str]:
        if self._repo.buscar_por_cedula(cedula):
            return False, f"Ya existe un veterinario con cédula {cedula}."
        try:
            vet = Veterinario(nombre, apellido, cedula, telefono, email, especialidad, tarjeta)
            doc_id = self._repo.insertar(vet.to_dict())
            return True, doc_id
        except ValueError as e:
            return False, str(e)

    def listar(self) -> list:
        return self._repo.buscar_todos()

    def buscar_por_id(self, doc_id: str) -> dict:
        return self._repo.buscar_por_id(doc_id)

    def buscar_por_cedula(self, cedula: str) -> dict:
        return self._repo.buscar_por_cedula(cedula)

    def contar(self) -> int:
        return self._repo.contar()


# ─────────────────────────────────────────
# SERVICIO DE ANIMALES
# ─────────────────────────────────────────
class ServicioAnimal:
    def __init__(self):
        self._repo = AnimalRepositorio()
        self._repo_cliente = ClienteRepositorio()

    def registrar(self, tipo: str, datos: dict) -> tuple[bool, str]:
        """
        Polimorfismo: crea el animal correcto según el tipo.
        tipo: "Perro", "Gato", "Ave", "Reptil"
        """
        try:
            animal = self._crear_animal(tipo, datos)
            if animal is None:
                return False, f"Tipo de animal desconocido: {tipo}"
            doc_id = self._repo.insertar(animal.to_dict())
            # Vincular al cliente
            cliente_id = datos.get("cliente_id", "")
            if cliente_id:
                cliente_doc = self._repo_cliente.buscar_por_id(cliente_id)
                if cliente_doc:
                    mascotas = cliente_doc.get("mascotas_ids", [])
                    if doc_id not in mascotas:
                        mascotas.append(doc_id)
                    self._repo_cliente.actualizar(cliente_id, {"mascotas_ids": mascotas})
            return True, doc_id
        except (ValueError, KeyError) as e:
            return False, str(e)

    def _crear_animal(self, tipo: str, datos: dict):
        """Factory method interno para crear el animal según tipo."""
        tipo = tipo.capitalize()
        if tipo == "Perro":
            return Perro(
                nombre=datos["nombre"], raza=datos.get("raza", "Mestizo"),
                edad=float(datos["edad"]), peso=float(datos["peso"]),
                sexo=datos["sexo"], cliente_id=datos.get("cliente_id", "")
            )
        elif tipo == "Gato":
            return Gato(
                nombre=datos["nombre"], raza=datos.get("raza", "Mestizo"),
                edad=float(datos["edad"]), peso=float(datos["peso"]),
                sexo=datos["sexo"],
                es_indoor=datos.get("es_indoor", True),
                cliente_id=datos.get("cliente_id", "")
            )
        elif tipo == "Ave":
            return Ave(
                nombre=datos["nombre"],
                especie_ave=datos.get("especie_ave", datos.get("raza", "Periquito")),
                edad=float(datos["edad"]), peso=float(datos["peso"]),
                sexo=datos["sexo"],
                envergadura=float(datos.get("envergadura", 0)),
                cliente_id=datos.get("cliente_id", "")
            )
        elif tipo == "Reptil":
            return Reptil(
                nombre=datos["nombre"],
                especie=datos.get("raza", datos.get("especie", "Iguana")),
                edad=float(datos["edad"]), peso=float(datos["peso"]),
                sexo=datos["sexo"],
                temperatura_ideal=float(datos.get("temperatura_ideal", 28)),
                es_venenoso=datos.get("es_venenoso", False),
                cliente_id=datos.get("cliente_id", "")
            )
        return None

    def listar(self) -> list:
        return self._repo.buscar_todos()

    def buscar_por_cliente(self, cliente_id: str) -> list:
        return self._repo.buscar_por_cliente(cliente_id)

    def buscar_por_id(self, doc_id: str) -> dict:
        return self._repo.buscar_por_id(doc_id)

    def contar(self) -> int:
        return self._repo.contar()


# ─────────────────────────────────────────
# SERVICIO DE CITAS
# ─────────────────────────────────────────
class ServicioCita:
    def __init__(self):
        self._repo = CitaRepositorio()
        self._repo_animal = AnimalRepositorio()
        self._repo_vet = VeterinarioRepositorio()
        self._repo_cliente = ClienteRepositorio()

    def agendar(self, animal_id: str, veterinario_id: str, cliente_id: str,
                fecha_hora: datetime, motivo: str, notas: str = "") -> tuple[bool, str]:
        try:
            cita = Cita(animal_id, veterinario_id, cliente_id, fecha_hora, motivo, notas)
            doc_id = self._repo.insertar(cita.to_dict())

            # Patrón Observer: notificar a veterinario y cliente
            animal = self._repo_animal.buscar_por_id(animal_id)
            vet = self._repo_vet.buscar_por_id(veterinario_id)
            cliente = self._repo_cliente.buscar_por_id(cliente_id)

            gestor_citas_global.registrar_cita({
                "cita_id": doc_id,
                "animal_nombre": animal.get("nombre", "?") if animal else "?",
                "veterinario_nombre": f"{vet.get('nombre', '')} {vet.get('apellido', '')}" if vet else "?",
                "cliente_nombre": f"{cliente.get('nombre', '')} {cliente.get('apellido', '')}" if cliente else "?",
                "fecha_hora": fecha_hora,
                "motivo": motivo
            })
            return True, doc_id
        except Exception as e:
            return False, str(e)

    def listar(self) -> list:
        return self._repo.buscar_todos()

    def buscar_por_id(self, doc_id: str) -> dict:
        return self._repo.buscar_por_id(doc_id)

    def actualizar_estado(self, doc_id: str, nuevo_estado: str) -> bool:
        cita_doc = self._repo.buscar_por_id(doc_id)
        if not cita_doc:
            return False

        cita = Cita.from_dict(cita_doc)
        if nuevo_estado == "Confirmada":
            cita.confirmar()
            gestor_citas_global.confirmar_cita(cita_doc)
        elif nuevo_estado == "Cancelada":
            cita.cancelar()
            gestor_citas_global.cancelar_cita(cita_doc)
        elif nuevo_estado == "Completada":
            cita.completar()
            gestor_citas_global.completar_cita(cita_doc)

        return self._repo.actualizar(doc_id, {"estado": cita.estado})

    def contar(self) -> int:
        return self._repo.contar()

    def pendientes(self) -> list:
        return self._repo.buscar_pendientes()


# ─────────────────────────────────────────
# SERVICIO DE HISTORIAL MÉDICO
# ─────────────────────────────────────────
class ServicioHistorial:
    def __init__(self):
        self._repo = HistorialRepositorio()

    def registrar(self, animal_id: str, veterinario_id: str, cita_id: str,
                  diagnostico: str, tratamiento: str,
                  medicamentos: list = None, observaciones: str = "") -> tuple[bool, str]:
        try:
            h = HistorialMedico(animal_id, veterinario_id, cita_id,
                                diagnostico, tratamiento, medicamentos, observaciones)
            doc_id = self._repo.insertar(h.to_dict())
            return True, doc_id
        except Exception as e:
            return False, str(e)

    def buscar_por_animal(self, animal_id: str) -> list:
        return self._repo.buscar_por_animal(animal_id)

    def listar(self) -> list:
        return self._repo.buscar_todos()
