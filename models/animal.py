"""
Módulo: animal.py
Contiene la clase abstracta Animal y sus subclases: Perro, Gato, Ave, Reptil.
Demuestra: Herencia, Polimorfismo (describir, calcular_riesgo), Encapsulamiento.
"""

from abc import ABC, abstractmethod
from datetime import datetime


class Animal(ABC):
    """Clase base abstracta para todos los animales del sistema."""

    def __init__(self, nombre: str, especie: str, edad: float,
                 peso: float, sexo: str, cliente_id: str = ""):
        self._nombre = nombre
        self._especie = especie
        self._edad = edad          # en años
        self._peso = peso          # en kg
        self._sexo = sexo          # "Macho" / "Hembra"
        self._cliente_id = cliente_id
        self._historial_ids: list = []
        self._fecha_registro = datetime.now()

    # --- Getters y Setters ---
    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        if not valor.strip():
            raise ValueError("El nombre no puede estar vacío.")
        self._nombre = valor.strip()

    @property
    def especie(self):
        return self._especie

    @property
    def edad(self):
        return self._edad

    @edad.setter
    def edad(self, valor: float):
        if valor < 0:
            raise ValueError("La edad no puede ser negativa.")
        self._edad = valor

    @property
    def peso(self):
        return self._peso

    @peso.setter
    def peso(self, valor: float):
        if valor <= 0:
            raise ValueError("El peso debe ser positivo.")
        self._peso = valor

    @property
    def sexo(self):
        return self._sexo

    @property
    def cliente_id(self):
        return self._cliente_id

    @cliente_id.setter
    def cliente_id(self, valor: str):
        self._cliente_id = valor

    @property
    def historial_ids(self):
        return list(self._historial_ids)

    def agregar_historial(self, historial_id: str):
        self._historial_ids.append(historial_id)

    # --- Métodos abstractos (Polimorfismo) ---
    @abstractmethod
    def describir(self) -> str:
        """Cada animal se describe de forma diferente."""
        pass

    @abstractmethod
    def calcular_riesgo(self) -> str:
        """Calcula el nivel de riesgo médico según la especie y características."""
        pass

    @abstractmethod
    def get_tipo(self) -> str:
        """Retorna el tipo de animal."""
        pass

    def to_dict(self) -> dict:
        return {
            "nombre": self._nombre,
            "especie": self._especie,
            "tipo": self.get_tipo(),
            "edad": self._edad,
            "peso": self._peso,
            "sexo": self._sexo,
            "cliente_id": self._cliente_id,
            "historial_ids": self._historial_ids,
            "fecha_registro": self._fecha_registro
        }

    def __str__(self):
        return f"{self.get_tipo()} - {self._nombre} ({self._especie}, {self._edad} años)"


class Perro(Animal):
    """
    Perro. Hereda de Animal.
    Atributos extra: raza, vacunas aplicadas.
    """

    def __init__(self, nombre: str, raza: str, edad: float, peso: float,
                 sexo: str, cliente_id: str = "", vacunas: list = None):
        super().__init__(nombre, "Canis lupus familiaris", edad, peso, sexo, cliente_id)
        self._raza = raza
        self._vacunas: list = vacunas if vacunas else []

    @property
    def raza(self):
        return self._raza

    @property
    def vacunas(self):
        return list(self._vacunas)

    def agregar_vacuna(self, vacuna: str):
        if vacuna not in self._vacunas:
            self._vacunas.append(vacuna)

    def get_tipo(self) -> str:
        return "Perro"

    def describir(self) -> str:
        vacunas_str = ", ".join(self._vacunas) if self._vacunas else "Ninguna registrada"
        return (f"🐶 Perro: {self._nombre}\n"
                f"  Raza: {self._raza}\n"
                f"  Edad: {self._edad} años | Peso: {self._peso} kg | Sexo: {self._sexo}\n"
                f"  Vacunas: {vacunas_str}\n"
                f"  Nivel de riesgo: {self.calcular_riesgo()}")

    def calcular_riesgo(self) -> str:
        """
        Polimorfismo: riesgo en perros basado en edad y peso.
        Razas grandes con edad avanzada = mayor riesgo cardíaco.
        """
        if self._edad > 10 or self._peso > 40:
            return "⚠️ Alto - Requiere monitoreo frecuente"
        elif self._edad > 7 or self._peso > 25:
            return "🟡 Medio - Chequeos semestrales"
        else:
            return "🟢 Bajo - Controles anuales"

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({"raza": self._raza, "vacunas": self._vacunas})
        return data

    @classmethod
    def from_dict(cls, data: dict):
        perro = cls(
            nombre=data["nombre"],
            raza=data.get("raza", "Mestizo"),
            edad=data["edad"],
            peso=data["peso"],
            sexo=data["sexo"],
            cliente_id=data.get("cliente_id", ""),
            vacunas=data.get("vacunas", [])
        )
        perro._historial_ids = data.get("historial_ids", [])
        if "fecha_registro" in data:
            perro._fecha_registro = data["fecha_registro"]
        return perro


class Gato(Animal):
    """
    Gato. Hereda de Animal.
    Atributos extra: es_indoor (vive dentro de casa), raza.
    """

    def __init__(self, nombre: str, raza: str, edad: float, peso: float,
                 sexo: str, es_indoor: bool = True, cliente_id: str = ""):
        super().__init__(nombre, "Felis catus", edad, peso, sexo, cliente_id)
        self._raza = raza
        self._es_indoor = es_indoor

    @property
    def raza(self):
        return self._raza

    @property
    def es_indoor(self):
        return self._es_indoor

    @es_indoor.setter
    def es_indoor(self, valor: bool):
        self._es_indoor = valor

    def get_tipo(self) -> str:
        return "Gato"

    def describir(self) -> str:
        tipo_vida = "Indoor (interior)" if self._es_indoor else "Outdoor (exterior)"
        return (f"🐱 Gato: {self._nombre}\n"
                f"  Raza: {self._raza}\n"
                f"  Edad: {self._edad} años | Peso: {self._peso} kg | Sexo: {self._sexo}\n"
                f"  Tipo de vida: {tipo_vida}\n"
                f"  Nivel de riesgo: {self.calcular_riesgo()}")

    def calcular_riesgo(self) -> str:
        """
        Polimorfismo: gatos outdoor tienen más riesgo de enfermedades infecciosas.
        """
        if not self._es_indoor and self._edad > 8:
            return "⚠️ Alto - Outdoor + Edad avanzada"
        elif not self._es_indoor:
            return "🟡 Medio - Outdoor: revisar parásitos"
        elif self._edad > 10:
            return "🟡 Medio - Edad avanzada"
        else:
            return "🟢 Bajo - Indoor y joven"

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({"raza": self._raza, "es_indoor": self._es_indoor})
        return data

    @classmethod
    def from_dict(cls, data: dict):
        gato = cls(
            nombre=data["nombre"],
            raza=data.get("raza", "Mestizo"),
            edad=data["edad"],
            peso=data["peso"],
            sexo=data["sexo"],
            es_indoor=data.get("es_indoor", True),
            cliente_id=data.get("cliente_id", "")
        )
        gato._historial_ids = data.get("historial_ids", [])
        if "fecha_registro" in data:
            gato._fecha_registro = data["fecha_registro"]
        return gato


class Ave(Animal):
    """
    Ave. Hereda de Animal.
    Atributos extra: especie_ave, envergadura (cm).
    """

    def __init__(self, nombre: str, especie_ave: str, edad: float, peso: float,
                 sexo: str, envergadura: float = 0.0, cliente_id: str = ""):
        super().__init__(nombre, especie_ave, edad, peso, sexo, cliente_id)
        self._especie_ave = especie_ave
        self._envergadura = envergadura  # en cm

    @property
    def especie_ave(self):
        return self._especie_ave

    @property
    def envergadura(self):
        return self._envergadura

    def get_tipo(self) -> str:
        return "Ave"

    def describir(self) -> str:
        return (f"🦜 Ave: {self._nombre}\n"
                f"  Especie: {self._especie_ave}\n"
                f"  Edad: {self._edad} años | Peso: {self._peso} kg | Sexo: {self._sexo}\n"
                f"  Envergadura: {self._envergadura} cm\n"
                f"  Nivel de riesgo: {self.calcular_riesgo()}")

    def calcular_riesgo(self) -> str:
        """
        Polimorfismo: aves son delicadas; poco peso = riesgo alto.
        """
        if self._peso < 0.05:
            return "⚠️ Alto - Peso crítico, muy frágil"
        elif self._edad > 15:
            return "🟡 Medio - Edad avanzada para ave"
        else:
            return "🟢 Bajo - Condiciones normales"

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({"especie_ave": self._especie_ave, "envergadura": self._envergadura})
        return data

    @classmethod
    def from_dict(cls, data: dict):
        ave = cls(
            nombre=data["nombre"],
            especie_ave=data.get("especie_ave", "Periquito"),
            edad=data["edad"],
            peso=data["peso"],
            sexo=data["sexo"],
            envergadura=data.get("envergadura", 0.0),
            cliente_id=data.get("cliente_id", "")
        )
        ave._historial_ids = data.get("historial_ids", [])
        if "fecha_registro" in data:
            ave._fecha_registro = data["fecha_registro"]
        return ave


class Reptil(Animal):
    """
    Reptil. Hereda de Animal.
    Atributos extra: temperatura_ideal (°C), es_venenoso.
    """

    def __init__(self, nombre: str, especie: str, edad: float, peso: float,
                 sexo: str, temperatura_ideal: float = 28.0,
                 es_venenoso: bool = False, cliente_id: str = ""):
        super().__init__(nombre, especie, edad, peso, sexo, cliente_id)
        self._temperatura_ideal = temperatura_ideal
        self._es_venenoso = es_venenoso

    @property
    def temperatura_ideal(self):
        return self._temperatura_ideal

    @property
    def es_venenoso(self):
        return self._es_venenoso

    def get_tipo(self) -> str:
        return "Reptil"

    def describir(self) -> str:
        venenoso = "⚠️ Sí" if self._es_venenoso else "No"
        return (f"🦎 Reptil: {self._nombre}\n"
                f"  Especie: {self._especie}\n"
                f"  Edad: {self._edad} años | Peso: {self._peso} kg | Sexo: {self._sexo}\n"
                f"  Temp. ideal: {self._temperatura_ideal}°C | Venenoso: {venenoso}\n"
                f"  Nivel de riesgo: {self.calcular_riesgo()}")

    def calcular_riesgo(self) -> str:
        """
        Polimorfismo: reptiles venenosos o con temperatura inadecuada = riesgo alto.
        """
        if self._es_venenoso:
            return "⚠️ Alto - Especie venenosa: protocolo especial"
        elif self._temperatura_ideal > 35 or self._temperatura_ideal < 20:
            return "🟡 Medio - Requiere ambiente controlado"
        else:
            return "🟢 Bajo - Condiciones estables"

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            "temperatura_ideal": self._temperatura_ideal,
            "es_venenoso": self._es_venenoso
        })
        return data

    @classmethod
    def from_dict(cls, data: dict):
        reptil = cls(
            nombre=data["nombre"],
            especie=data.get("especie", "Iguana"),
            edad=data["edad"],
            peso=data["peso"],
            sexo=data["sexo"],
            temperatura_ideal=data.get("temperatura_ideal", 28.0),
            es_venenoso=data.get("es_venenoso", False),
            cliente_id=data.get("cliente_id", "")
        )
        reptil._historial_ids = data.get("historial_ids", [])
        if "fecha_registro" in data:
            reptil._fecha_registro = data["fecha_registro"]
        return reptil
