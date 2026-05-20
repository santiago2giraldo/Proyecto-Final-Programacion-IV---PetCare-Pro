"""
Módulo: observer.py
Patrón de Diseño: OBSERVER
Cuando se registra/actualiza una cita, notifica automáticamente a los observadores.

Componentes:
  - Observable (Subject): genera eventos
  - Observer (interfaz): define update()
  - NotificadorVeterinario: observador concreto
  - NotificadorCliente: observador concreto
  - LogSistema: observador concreto (registra todo en consola/archivo)
"""

from abc import ABC, abstractmethod
from datetime import datetime


# ─────────────────────────────────────────
# INTERFAZ OBSERVER
# ─────────────────────────────────────────
class Observer(ABC):
    """Interfaz que deben implementar todos los observadores."""

    @abstractmethod
    def update(self, evento: str, datos: dict):
        """Recibe la notificación del evento."""
        pass


# ─────────────────────────────────────────
# OBSERVABLE (SUBJECT)
# ─────────────────────────────────────────
class Observable:
    """
    Clase base para objetos que pueden ser observados.
    Gestiona la lista de observers y los notifica.
    """

    def __init__(self):
        self._observers: list[Observer] = []

    def agregar_observer(self, observer: Observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def remover_observer(self, observer: Observer):
        if observer in self._observers:
            self._observers.remove(observer)

    def notificar(self, evento: str, datos: dict):
        """Notifica a TODOS los observers registrados."""
        for observer in self._observers:
            observer.update(evento, datos)


# ─────────────────────────────────────────
# GESTIÓN DE CITAS (usa Observable)
# ─────────────────────────────────────────
class GestorCitas(Observable):
    """
    Gestiona las citas y notifica a los observers cuando ocurren eventos.
    Eventos: CITA_CREADA, CITA_CONFIRMADA, CITA_CANCELADA, CITA_COMPLETADA
    """

    def registrar_cita(self, cita_data: dict):
        self.notificar("CITA_CREADA", cita_data)

    def confirmar_cita(self, cita_data: dict):
        self.notificar("CITA_CONFIRMADA", cita_data)

    def cancelar_cita(self, cita_data: dict):
        self.notificar("CITA_CANCELADA", cita_data)

    def completar_cita(self, cita_data: dict):
        self.notificar("CITA_COMPLETADA", cita_data)


# ─────────────────────────────────────────
# OBSERVERS CONCRETOS
# ─────────────────────────────────────────
class NotificadorVeterinario(Observer):
    """
    Notifica al veterinario cuando se le asigna o modifica una cita.
    En producción enviaría email/SMS; aquí registra el mensaje.
    """

    def __init__(self):
        self.notificaciones: list[dict] = []

    def update(self, evento: str, datos: dict):
        vet_nombre = datos.get("veterinario_nombre", "Veterinario")
        animal_nombre = datos.get("animal_nombre", "paciente")
        fecha = datos.get("fecha_hora", "")
        if isinstance(fecha, datetime):
            fecha = fecha.strftime("%d/%m/%Y %H:%M")

        mensajes = {
            "CITA_CREADA": f"📅 Nueva cita asignada: {animal_nombre} el {fecha}",
            "CITA_CONFIRMADA": f"✅ Cita confirmada: {animal_nombre} el {fecha}",
            "CITA_CANCELADA": f"❌ Cita cancelada: {animal_nombre} el {fecha}",
            "CITA_COMPLETADA": f"🏁 Cita completada: {animal_nombre} el {fecha}"
        }

        mensaje = mensajes.get(evento, f"Evento: {evento}")
        notif = {
            "destinatario": vet_nombre,
            "tipo": "Veterinario",
            "evento": evento,
            "mensaje": mensaje,
            "timestamp": datetime.now()
        }
        self.notificaciones.append(notif)
        print(f"  🔔 [VET] {vet_nombre}: {mensaje}")

    def get_notificaciones(self) -> list:
        return list(self.notificaciones)


class NotificadorCliente(Observer):
    """
    Notifica al cliente sobre el estado de su cita.
    """

    def __init__(self):
        self.notificaciones: list[dict] = []

    def update(self, evento: str, datos: dict):
        cliente_nombre = datos.get("cliente_nombre", "Cliente")
        animal_nombre = datos.get("animal_nombre", "su mascota")
        fecha = datos.get("fecha_hora", "")
        if isinstance(fecha, datetime):
            fecha = fecha.strftime("%d/%m/%Y %H:%M")

        mensajes = {
            "CITA_CREADA": f"Tu cita para {animal_nombre} fue agendada para el {fecha}",
            "CITA_CONFIRMADA": f"Tu cita para {animal_nombre} el {fecha} está confirmada ✅",
            "CITA_CANCELADA": f"Tu cita para {animal_nombre} el {fecha} fue cancelada ❌",
            "CITA_COMPLETADA": f"La consulta de {animal_nombre} ha finalizado 🏁"
        }

        mensaje = mensajes.get(evento, f"Actualización de cita: {evento}")
        notif = {
            "destinatario": cliente_nombre,
            "tipo": "Cliente",
            "evento": evento,
            "mensaje": mensaje,
            "timestamp": datetime.now()
        }
        self.notificaciones.append(notif)
        print(f"  🔔 [CLI] {cliente_nombre}: {mensaje}")

    def get_notificaciones(self) -> list:
        return list(self.notificaciones)


class LogSistema(Observer):
    """
    Observer que registra todos los eventos en un log del sistema.
    """

    def __init__(self):
        self.logs: list[str] = []

    def update(self, evento: str, datos: dict):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entrada = f"[{timestamp}] {evento} | {datos.get('animal_nombre', '')} | {datos.get('veterinario_nombre', '')}"
        self.logs.append(entrada)

    def get_logs(self) -> list:
        return list(self.logs)

    def limpiar(self):
        self.logs.clear()


# ─────────────────────────────────────────
# INSTANCIA GLOBAL DEL GESTOR DE CITAS
# ─────────────────────────────────────────
# Se crea una instancia compartida con sus observers listos
notificador_vet = NotificadorVeterinario()
notificador_cliente = NotificadorCliente()
log_sistema = LogSistema()

gestor_citas_global = GestorCitas()
gestor_citas_global.agregar_observer(notificador_vet)
gestor_citas_global.agregar_observer(notificador_cliente)
gestor_citas_global.agregar_observer(log_sistema)
