"""
Módulo: cita.py y historial.py
Contiene las clases Cita e HistorialMedico.
"""

from datetime import datetime
from enum import Enum


class EstadoCita(Enum):
    PENDIENTE = "Pendiente"
    CONFIRMADA = "Confirmada"
    EN_CURSO = "En curso"
    COMPLETADA = "Completada"
    CANCELADA = "Cancelada"


class Cita:
    """
    Conecta un Veterinario + Animal + fecha/hora.
    Encapsula el estado de la cita con lógica de transición.
    """

    def __init__(self, animal_id: str, veterinario_id: str, cliente_id: str,
                 fecha_hora: datetime, motivo: str, notas: str = ""):
        self._animal_id = animal_id
        self._veterinario_id = veterinario_id
        self._cliente_id = cliente_id
        self._fecha_hora = fecha_hora
        self._motivo = motivo
        self._notas = notas
        self._estado = EstadoCita.PENDIENTE
        self._fecha_creacion = datetime.now()

    # --- Getters ---
    @property
    def animal_id(self):
        return self._animal_id

    @property
    def veterinario_id(self):
        return self._veterinario_id

    @property
    def cliente_id(self):
        return self._cliente_id

    @property
    def fecha_hora(self):
        return self._fecha_hora

    @property
    def motivo(self):
        return self._motivo

    @property
    def notas(self):
        return self._notas

    @notas.setter
    def notas(self, valor: str):
        self._notas = valor

    @property
    def estado(self):
        return self._estado.value

    def confirmar(self):
        if self._estado == EstadoCita.PENDIENTE:
            self._estado = EstadoCita.CONFIRMADA

    def iniciar(self):
        if self._estado == EstadoCita.CONFIRMADA:
            self._estado = EstadoCita.EN_CURSO

    def completar(self):
        if self._estado in [EstadoCita.EN_CURSO, EstadoCita.CONFIRMADA]:
            self._estado = EstadoCita.COMPLETADA

    def cancelar(self):
        if self._estado in [EstadoCita.PENDIENTE, EstadoCita.CONFIRMADA]:
            self._estado = EstadoCita.CANCELADA

    def to_dict(self) -> dict:
        return {
            "animal_id": self._animal_id,
            "veterinario_id": self._veterinario_id,
            "cliente_id": self._cliente_id,
            "fecha_hora": self._fecha_hora,
            "motivo": self._motivo,
            "notas": self._notas,
            "estado": self._estado.value,
            "fecha_creacion": self._fecha_creacion
        }

    @classmethod
    def from_dict(cls, data: dict):
        cita = cls(
            animal_id=data["animal_id"],
            veterinario_id=data["veterinario_id"],
            cliente_id=data["cliente_id"],
            fecha_hora=data["fecha_hora"],
            motivo=data["motivo"],
            notas=data.get("notas", "")
        )
        # Restaurar estado
        estado_str = data.get("estado", "Pendiente")
        for e in EstadoCita:
            if e.value == estado_str:
                cita._estado = e
                break
        if "fecha_creacion" in data:
            cita._fecha_creacion = data["fecha_creacion"]
        return cita

    def __str__(self):
        return (f"Cita [{self._estado.value}] - "
                f"{self._fecha_hora.strftime('%d/%m/%Y %H:%M')} | "
                f"Motivo: {self._motivo}")


class HistorialMedico:
    """
    Registro médico de una consulta.
    Encapsula diagnóstico, tratamiento y medicamentos (atributos privados).
    """

    def __init__(self, animal_id: str, veterinario_id: str, cita_id: str,
                 diagnostico: str, tratamiento: str,
                 medicamentos: list = None, observaciones: str = ""):
        self._animal_id = animal_id
        self._veterinario_id = veterinario_id
        self._cita_id = cita_id
        self.__diagnostico = diagnostico      # doble guion: más privado
        self.__tratamiento = tratamiento
        self.__medicamentos: list = medicamentos if medicamentos else []
        self._observaciones = observaciones
        self._fecha = datetime.now()

    # --- Acceso controlado al historial médico (Encapsulamiento fuerte) ---
    def get_diagnostico(self) -> str:
        return self.__diagnostico

    def get_tratamiento(self) -> str:
        return self.__tratamiento

    def get_medicamentos(self) -> list:
        return list(self.__medicamentos)

    def agregar_medicamento(self, medicamento: str):
        if medicamento not in self.__medicamentos:
            self.__medicamentos.append(medicamento)

    @property
    def animal_id(self):
        return self._animal_id

    @property
    def veterinario_id(self):
        return self._veterinario_id

    @property
    def cita_id(self):
        return self._cita_id

    @property
    def observaciones(self):
        return self._observaciones

    @observaciones.setter
    def observaciones(self, valor: str):
        self._observaciones = valor

    @property
    def fecha(self):
        return self._fecha

    def to_dict(self) -> dict:
        return {
            "animal_id": self._animal_id,
            "veterinario_id": self._veterinario_id,
            "cita_id": self._cita_id,
            "diagnostico": self.__diagnostico,
            "tratamiento": self.__tratamiento,
            "medicamentos": self.__medicamentos,
            "observaciones": self._observaciones,
            "fecha": self._fecha
        }

    @classmethod
    def from_dict(cls, data: dict):
        h = cls(
            animal_id=data["animal_id"],
            veterinario_id=data["veterinario_id"],
            cita_id=data.get("cita_id", ""),
            diagnostico=data["diagnostico"],
            tratamiento=data["tratamiento"],
            medicamentos=data.get("medicamentos", []),
            observaciones=data.get("observaciones", "")
        )
        if "fecha" in data:
            h._fecha = data["fecha"]
        return h

    def __str__(self):
        return (f"Historial [{self._fecha.strftime('%d/%m/%Y')}]\n"
                f"  Diagnóstico: {self.__diagnostico}\n"
                f"  Tratamiento: {self.__tratamiento}\n"
                f"  Medicamentos: {', '.join(self.__medicamentos) or 'Ninguno'}")
