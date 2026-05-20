"""
Módulo: app.py
Ventana principal de VetCare Pro.
Interfaz gráfica con CustomTkinter.
Pantallas: Dashboard, Clientes, Animales, Citas, Veterinarios
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime

from database.db_connection import DatabaseConnection
from utils.servicios import ServicioCliente, ServicioVeterinario, ServicioAnimal, ServicioCita
from ui.frame_clientes import FrameClientes
from ui.frame_animales import FrameAnimales
from ui.frame_citas import FrameCitas
from ui.frame_veterinarios import FrameVeterinarios

# ─── Tema visual ───────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Paleta de colores VetCare Pro
COLORS = {
    "bg_primary":    "#0F1923",   # Fondo oscuro profundo
    "bg_secondary":  "#162032",   # Sidebar
    "bg_card":       "#1E2D3D",   # Tarjetas
    "accent":        "#00C896",   # Verde esmeralda (salud)
    "accent2":       "#0099FF",   # Azul
    "text_primary":  "#E8F0F7",
    "text_secondary":"#7A9BB5",
    "danger":        "#FF4757",
    "warning":       "#FFA502",
    "success":       "#2ED573",
    "border":        "#243447",
}


class VetCareApp(ctk.CTk):
    """Ventana principal de la aplicación VetCare Pro."""

    def __init__(self):
        super().__init__()

        self.title("🐾 VetCare Pro — Sistema de Gestión Veterinaria")
        self.geometry("1280x760")
        self.minsize(1100, 680)
        self.configure(fg_color=COLORS["bg_primary"])

        # Conexión a MongoDB (Singleton)
        self._db = DatabaseConnection.get_instance()
        self._mongo_ok = self._db.connect()

        # Servicios
        self._svc_cliente = ServicioCliente()
        self._svc_vet = ServicioVeterinario()
        self._svc_animal = ServicioAnimal()
        self._svc_cita = ServicioCita()

        # Frame activo
        self._frame_activo = None
        self._frames = {}
        self._btn_activo = None

        self._construir_layout()
        self._mostrar_frame("dashboard")

    # ─────────────────────────────────────────
    # LAYOUT PRINCIPAL
    # ─────────────────────────────────────────
    def _construir_layout(self):
        # Grid principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ── Sidebar ──
        self.sidebar = ctk.CTkFrame(
            self, width=240, fg_color=COLORS["bg_secondary"],
            corner_radius=0
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(10, weight=1)
        self.sidebar.grid_propagate(False)

        # Logo
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=20, pady=(30, 20), sticky="ew")

        ctk.CTkLabel(
            logo_frame, text="🐾", font=ctk.CTkFont(size=36)
        ).pack(anchor="w")
        ctk.CTkLabel(
            logo_frame, text="VetCare Pro",
            font=ctk.CTkFont(family="Arial", size=20, weight="bold"),
            text_color=COLORS["accent"]
        ).pack(anchor="w")
        ctk.CTkLabel(
            logo_frame, text="Sistema Veterinario",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_secondary"]
        ).pack(anchor="w")

        # Estado MongoDB
        mongo_color = COLORS["success"] if self._mongo_ok else COLORS["warning"]
        mongo_txt = "● MongoDB conectado" if self._mongo_ok else "● Modo demo (sin DB)"
        self._lbl_mongo = ctk.CTkLabel(
            self.sidebar, text=mongo_txt,
            font=ctk.CTkFont(size=10),
            text_color=mongo_color
        )
        self._lbl_mongo.grid(row=1, column=0, padx=20, pady=(0, 15), sticky="w")

        # Separador
        ctk.CTkFrame(self.sidebar, height=1, fg_color=COLORS["border"]).grid(
            row=2, column=0, padx=15, pady=5, sticky="ew"
        )

        # Navegación
        nav_items = [
            ("dashboard",    "📊", "Dashboard"),
            ("clientes",     "👤", "Clientes"),
            ("animales",     "🐾", "Animales"),
            ("citas",        "📅", "Citas"),
            ("veterinarios", "🩺", "Veterinarios"),
        ]

        self._nav_buttons = {}
        for idx, (key, icon, label) in enumerate(nav_items):
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"  {icon}  {label}",
                anchor="w",
                font=ctk.CTkFont(size=14),
                fg_color="transparent",
                text_color=COLORS["text_secondary"],
                hover_color=COLORS["bg_card"],
                height=44,
                corner_radius=10,
                command=lambda k=key: self._mostrar_frame(k)
            )
            btn.grid(row=3 + idx, column=0, padx=12, pady=3, sticky="ew")
            self._nav_buttons[key] = btn

        # Fecha en sidebar
        fecha_str = datetime.now().strftime("%d %b %Y")
        ctk.CTkLabel(
            self.sidebar, text=f"📆 {fecha_str}",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_secondary"]
        ).grid(row=11, column=0, padx=20, pady=20, sticky="sw")

        # ── Área de contenido principal ──
        self.contenido = ctk.CTkFrame(
            self, fg_color=COLORS["bg_primary"], corner_radius=0
        )
        self.contenido.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.contenido.grid_columnconfigure(0, weight=1)
        self.contenido.grid_rowconfigure(0, weight=1)

    # ─────────────────────────────────────────
    # NAVEGACIÓN
    # ─────────────────────────────────────────
    def _mostrar_frame(self, nombre: str):
        # Resaltar botón activo
        if self._btn_activo:
            self._btn_activo.configure(
                fg_color="transparent",
                text_color=COLORS["text_secondary"]
            )
        if nombre in self._nav_buttons:
            self._btn_activo = self._nav_buttons[nombre]
            self._btn_activo.configure(
                fg_color=COLORS["bg_card"],
                text_color=COLORS["accent"]
            )

        # Destruir frame anterior
        if self._frame_activo:
            self._frame_activo.destroy()

        # Crear frame nuevo
        if nombre == "dashboard":
            self._frame_activo = self._crear_dashboard()
        elif nombre == "clientes":
            self._frame_activo = FrameClientes(self.contenido, COLORS)
        elif nombre == "animales":
            self._frame_activo = FrameAnimales(self.contenido, COLORS)
        elif nombre == "citas":
            self._frame_activo = FrameCitas(self.contenido, COLORS)
        elif nombre == "veterinarios":
            self._frame_activo = FrameVeterinarios(self.contenido, COLORS)

        if self._frame_activo:
            self._frame_activo.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)

    # ─────────────────────────────────────────
    # DASHBOARD
    # ─────────────────────────────────────────
    def _crear_dashboard(self) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(self.contenido, fg_color=COLORS["bg_primary"], corner_radius=0)
        frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Header
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=4, padx=30, pady=(30, 20), sticky="ew")

        ctk.CTkLabel(
            header, text="Dashboard",
            font=ctk.CTkFont(family="Arial", size=28, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left")

        hora = datetime.now().strftime("%H:%M")
        ctk.CTkLabel(
            header, text=f"Bienvenido • {hora}",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_secondary"]
        ).pack(side="right", pady=8)

        # Tarjetas de estadísticas
        stats = [
            ("👤", "Clientes", self._svc_cliente.contar(), COLORS["accent2"]),
            ("🐾", "Animales", self._svc_animal.contar(), COLORS["accent"]),
            ("📅", "Citas totales", self._svc_cita.contar(), COLORS["warning"]),
            ("🩺", "Veterinarios", self._svc_vet.contar(), "#B388FF"),
        ]

        for col, (icon, label, valor, color) in enumerate(stats):
            card = ctk.CTkFrame(frame, fg_color=COLORS["bg_card"],
                                corner_radius=16, border_width=1,
                                border_color=COLORS["border"])
            card.grid(row=1, column=col, padx=(15 if col > 0 else 30, 15 if col < 3 else 30),
                      pady=10, sticky="ew")
            card.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(card, text=icon, font=ctk.CTkFont(size=32)).grid(
                row=0, column=0, padx=20, pady=(20, 5), sticky="w")
            ctk.CTkLabel(
                card, text=str(valor),
                font=ctk.CTkFont(size=36, weight="bold"),
                text_color=color
            ).grid(row=1, column=0, padx=20, pady=2, sticky="w")
            ctk.CTkLabel(
                card, text=label,
                font=ctk.CTkFont(size=13),
                text_color=COLORS["text_secondary"]
            ).grid(row=2, column=0, padx=20, pady=(2, 20), sticky="w")

        # Citas recientes
        ctk.CTkLabel(
            frame, text="Citas recientes",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text_primary"]
        ).grid(row=2, column=0, columnspan=4, padx=30, pady=(25, 10), sticky="w")

        tabla_frame = ctk.CTkFrame(frame, fg_color=COLORS["bg_card"],
                                   corner_radius=16, border_width=1,
                                   border_color=COLORS["border"])
        tabla_frame.grid(row=3, column=0, columnspan=4, padx=30, pady=(0, 20), sticky="ew")
        tabla_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Encabezados tabla
        headers = ["Motivo", "Animal", "Veterinario", "Estado"]
        for col, h in enumerate(headers):
            ctk.CTkLabel(
                tabla_frame, text=h,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLORS["text_secondary"]
            ).grid(row=0, column=col, padx=15, pady=12, sticky="w")

        todas_citas = self._svc_cita.listar()
        citas = todas_citas[-5:] if todas_citas else []

        if not citas:
            ctk.CTkLabel(
                tabla_frame, text="No hay citas registradas aún.",
                text_color=COLORS["text_secondary"],
                font=ctk.CTkFont(size=13)
            ).grid(row=1, column=0, columnspan=4, padx=15, pady=20)
        else:
            for r, cita in enumerate(reversed(citas)):
                estado = cita.get("estado", "?")
                estado_color = {
                    "Pendiente": COLORS["warning"],
                    "Confirmada": COLORS["accent2"],
                    "Completada": COLORS["success"],
                    "Cancelada": COLORS["danger"]
                }.get(estado, COLORS["text_secondary"])

                animal = self._svc_animal.buscar_por_id(str(cita.get("animal_id", "")))
                animal_nombre = animal.get("nombre", "?") if animal else "?"
                vet = self._svc_vet.buscar_por_id(str(cita.get("veterinario_id", "")))
                vet_nombre = f"Dr. {vet.get('apellido', '?')}" if vet else "?"

                ctk.CTkLabel(tabla_frame, text=cita.get("motivo", "?")[:30],
                             font=ctk.CTkFont(size=13), text_color=COLORS["text_primary"]
                             ).grid(row=r+1, column=0, padx=15, pady=8, sticky="w")
                ctk.CTkLabel(tabla_frame, text=animal_nombre,
                             font=ctk.CTkFont(size=12), text_color=COLORS["text_secondary"]
                             ).grid(row=r+1, column=1, padx=15, pady=8, sticky="w")
                ctk.CTkLabel(tabla_frame, text=vet_nombre,
                             font=ctk.CTkFont(size=12), text_color=COLORS["text_secondary"]
                             ).grid(row=r+1, column=2, padx=15, pady=8, sticky="w")
                ctk.CTkLabel(tabla_frame, text=estado,
                             font=ctk.CTkFont(size=12, weight="bold"),
                             text_color=estado_color
                             ).grid(row=r+1, column=3, padx=15, pady=8, sticky="w")

        # Accesos rápidos
        ctk.CTkLabel(
            frame, text="Accesos rápidos",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text_primary"]
        ).grid(row=4, column=0, columnspan=4, padx=30, pady=(10, 10), sticky="w")

        quick_frame = ctk.CTkFrame(frame, fg_color="transparent")
        quick_frame.grid(row=5, column=0, columnspan=4, padx=30, pady=(0, 30), sticky="ew")

        acciones = [
            ("➕ Nuevo Cliente", "clientes"),
            ("🐾 Registrar Mascota", "animales"),
            ("📅 Agendar Cita", "citas"),
            ("🩺 Agregar Veterinario", "veterinarios"),
        ]
        for i, (texto, destino) in enumerate(acciones):
            ctk.CTkButton(
                quick_frame, text=texto,
                font=ctk.CTkFont(size=13),
                fg_color=COLORS["bg_card"],
                hover_color=COLORS["border"],
                text_color=COLORS["accent"],
                border_width=1,
                border_color=COLORS["accent"],
                height=44,
                corner_radius=10,
                command=lambda d=destino: self._mostrar_frame(d)
            ).grid(row=0, column=i, padx=(0 if i == 0 else 12, 0), sticky="ew")

        return frame

    def on_closing(self):
        self._db.disconnect()
        self.destroy()


# ─────────────────────────────────────────
# PUNTO DE ENTRADA
# ─────────────────────────────────────────
if __name__ == "__main__":
    app = VetCareApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
