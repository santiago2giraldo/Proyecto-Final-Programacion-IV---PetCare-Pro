"""
Módulo: persona.py
Contiene la clase abstracta Persona y sus subclases: Cliente, Veterinario, Recepcionista.
Demuestra: Herencia, Encapsulamiento, Polimorfismo, Abstracción.
"""

from abc import ABC, abstractmethod
from datetime import datetime


class Persona(ABC):
    """Clase base abstracta para todas las personas del sistema."""

    def __init__(self, nombre: str, apellido: str, cedula: str, telefono: str, email: str):
        # Encapsulamiento: atributos privados con _ (convención Python)
        self._nombre = nombre
        self._apellido = apellido
        self._cedula = cedula
        self._telefono = telefono
        self._email = email
        self._fecha_registro = datetime.now()

    # --- Getters y Setters (Encapsulamiento) ---
    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        if not valor.strip():
            raise ValueError("El nombre no puede estar vacío.")
        self._nombre = valor.strip()

    @property
    def apellido(self):
        return self._apellido

    @apellido.setter
    def apellido(self, valor: str):
        if not valor.strip():
            raise ValueError("El apellido no puede estar vacío.")
        self._apellido = valor.strip()

    @property
    def cedula(self):
        return self._cedula

    @property
    def telefono(self):
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str):
        self._telefono = valor

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, valor: str):
        if "@" not in valor:
            raise ValueError("Email inválido.")
        self._email = valor

    @property
    def nombre_completo(self):
        return f"{self._nombre} {self._apellido}"

    @property
    def fecha_registro(self):
        return self._fecha_registro

    # Método abstracto: cada subclase define su rol
    @abstractmethod
    def get_rol(self) -> str:
        pass

    @abstractmethod
    def describir(self) -> str:
        pass

    def to_dict(self) -> dict:
        """Serializa la persona a diccionario para MongoDB."""
        return {
            "nombre": self._nombre,
            "apellido": self._apellido,
            "cedula": self._cedula,
            "telefono": self._telefono,
            "email": self._email,
            "fecha_registro": self._fecha_registro,
            "rol": self.get_rol()
        }

    def __str__(self):
        return f"{self.get_rol()}: {self.nombre_completo} (CC: {self._cedula})"


class Cliente(Persona):
    """
    Cliente de la clínica veterinaria.
    Hereda de Persona. Tiene una lista de mascotas asociadas.
    """

    def __init__(self, nombre: str, apellido: str, cedula: str,
                 telefono: str, email: str, direccion: str = ""):
        super().__init__(nombre, apellido, cedula, telefono, email)
        self._direccion = direccion
        self._mascotas_ids: list = []  # IDs de animales en MongoDB

    @property
    def direccion(self):
        return self._direccion

    @direccion.setter
    def direccion(self, valor: str):
        self._direccion = valor

    @property
    def mascotas_ids(self):
        return list(self._mascotas_ids)

    def agregar_mascota(self, animal_id: str):
        if animal_id not in self._mascotas_ids:
            self._mascotas_ids.append(animal_id)

    def get_rol(self) -> str:
        return "Cliente"

    def describir(self) -> str:
        return (f"Cliente: {self.nombre_completo}\n"
                f"  Cédula: {self._cedula}\n"
                f"  Teléfono: {self._telefono}\n"
                f"  Email: {self._email}\n"
                f"  Dirección: {self._direccion}\n"
                f"  Mascotas registradas: {len(self._mascotas_ids)}")

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            "direccion": self._direccion,
            "mascotas_ids": self._mascotas_ids
        })
        return data

    @classmethod
    def from_dict(cls, data: dict):
        """Crea un Cliente desde un documento de MongoDB."""
        cliente = cls(
            nombre=data["nombre"],
            apellido=data["apellido"],
            cedula=data["cedula"],
            telefono=data["telefono"],
            email=data["email"],
            direccion=data.get("direccion", "")
        )
        cliente._mascotas_ids = data.get("mascotas_ids", [])
        if "fecha_registro" in data:
            cliente._fecha_registro = data["fecha_registro"]
        return cliente


class Veterinario(Persona):
    """
    Veterinario de la clínica.
    Hereda de Persona. Tiene especialidad y tarjeta profesional.
    """

    ESPECIALIDADES = [
        "Medicina General", "Cirugía", "Dermatología",
        "Cardiología", "Oncología", "Exóticos", "Ortopedia"
    ]

    def __init__(self, nombre: str, apellido: str, cedula: str,
                 telefono: str, email: str,
                 especialidad: str = "Medicina General",
                 tarjeta_profesional: str = ""):
        super().__init__(nombre, apellido, cedula, telefono, email)
        self._especialidad = especialidad
        self._tarjeta_profesional = tarjeta_profesional
        self._citas_ids: list = []

    @property
    def especialidad(self):
        return self._especialidad

    @especialidad.setter
    def especialidad(self, valor: str):
        if valor not in self.ESPECIALIDADES:
            raise ValueError(f"Especialidad inválida. Opciones: {self.ESPECIALIDADES}")
        self._especialidad = valor

    @property
    def tarjeta_profesional(self):
        return self._tarjeta_profesional

    def get_rol(self) -> str:
        return "Veterinario"

    def describir(self) -> str:
        return (f"Dr(a). {self.nombre_completo}\n"
                f"  Especialidad: {self._especialidad}\n"
                f"  Tarjeta Prof.: {self._tarjeta_profesional}\n"
                f"  Citas asignadas: {len(self._citas_ids)}")

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            "especialidad": self._especialidad,
            "tarjeta_profesional": self._tarjeta_profesional,
            "citas_ids": self._citas_ids
        })
        return data

    @classmethod
    def from_dict(cls, data: dict):
        vet = cls(
            nombre=data["nombre"],
            apellido=data["apellido"],
            cedula=data["cedula"],
            telefono=data["telefono"],
            email=data["email"],
            especialidad=data.get("especialidad", "Medicina General"),
            tarjeta_profesional=data.get("tarjeta_profesional", "")
        )
        vet._citas_ids = data.get("citas_ids", [])
        if "fecha_registro" in data:
            vet._fecha_registro = data["fecha_registro"]
        return vet


class Recepcionista(Persona):
    """
    Recepcionista de la clínica.
    Hereda de Persona. Gestiona turnos y registros.
    """

    def __init__(self, nombre: str, apellido: str, cedula: str,
                 telefono: str, email: str, turno: str = "Mañana"):
        super().__init__(nombre, apellido, cedula, telefono, email)
        self._turno = turno  # "Mañana", "Tarde", "Noche"

    @property
    def turno(self):
        return self._turno

    @turno.setter
    def turno(self, valor: str):
        opciones = ["Mañana", "Tarde", "Noche"]
        if valor not in opciones:
            raise ValueError(f"Turno inválido. Opciones: {opciones}")
        self._turno = valor

    def get_rol(self) -> str:
        return "Recepcionista"

    def describir(self) -> str:
        return (f"Recepcionista: {self.nombre_completo}\n"
                f"  Turno: {self._turno}\n"
                f"  Email: {self._email}")

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({"turno": self._turno})
        return data

    @classmethod
    def from_dict(cls, data: dict):
        rec = cls(
            nombre=data["nombre"],
            apellido=data["apellido"],
            cedula=data["cedula"],
            telefono=data["telefono"],
            email=data["email"],
            turno=data.get("turno", "Mañana")
        )
        if "fecha_registro" in data:
            rec._fecha_registro = data["fecha_registro"]
        return rec
