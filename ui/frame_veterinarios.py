"""
Módulo: frame_veterinarios.py
Interfaz gráfica para gestión de veterinarios.
Pantalla #5 del sistema.
"""

import customtkinter as ctk
from tkinter import messagebox
from utils.servicios import ServicioVeterinario
from models.persona import Veterinario


class FrameVeterinarios(ctk.CTkFrame):
    def __init__(self, parent, colors: dict):
        super().__init__(parent, fg_color=colors["bg_primary"], corner_radius=0)
        self.C = colors
        self._svc = ServicioVeterinario()
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._construir()
        self._cargar_tabla()

    def _construir(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=30, pady=(30, 15), sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header, text="🩺 Veterinarios",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=self.C["text_primary"]
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            header, text="➕ Agregar Veterinario",
            fg_color=self.C["accent"], hover_color="#00A87C",
            text_color="#000", height=38, width=190, corner_radius=10,
            command=self._abrir_form
        ).grid(row=0, column=2, sticky="e")

        # Cards grid
        self._cards_frame = ctk.CTkScrollableFrame(
            self, fg_color="transparent", corner_radius=0
        )
        self._cards_frame.grid(row=1, column=0, padx=30, pady=(5, 30), sticky="nsew")
        self._cards_frame.grid_columnconfigure((0, 1, 2), weight=1)

    def _cargar_tabla(self):
        for widget in self._cards_frame.winfo_children():
            widget.destroy()

        vets = self._svc.listar()

        if not vets:
            ctk.CTkLabel(
                self._cards_frame,
                text="No hay veterinarios registrados.",
                text_color=self.C["text_secondary"],
                font=ctk.CTkFont(size=14)
            ).grid(row=0, column=0, columnspan=3, padx=15, pady=40)
            return

        ESPECIALIDAD_COLORES = {
            "Medicina General": "#0099FF",
            "Cirugía":          "#FF4757",
            "Dermatología":     "#FFA502",
            "Cardiología":      "#FF6B81",
            "Oncología":        "#B388FF",
            "Exóticos":         "#00C896",
            "Ortopedia":        "#2ED573",
        }

        for idx, vet in enumerate(vets):
            row = idx // 3
            col = idx % 3

            esp = vet.get("especialidad", "Medicina General")
            color_esp = ESPECIALIDAD_COLORES.get(esp, self.C["accent"])
            doc_id = str(vet.get("_id", ""))

            card = ctk.CTkFrame(
                self._cards_frame,
                fg_color=self.C["bg_card"],
                corner_radius=16,
                border_width=2,
                border_color=color_esp
            )
            card.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
            card.grid_columnconfigure(0, weight=1)

            # Ícono
            ctk.CTkLabel(card, text="🩺", font=ctk.CTkFont(size=32)).grid(
                row=0, column=0, padx=20, pady=(20, 5), sticky="w"
            )
            # Nombre
            ctk.CTkLabel(
                card,
                text=f"Dr(a). {vet.get('nombre', '')} {vet.get('apellido', '')}",
                font=ctk.CTkFont(size=15, weight="bold"),
                text_color=self.C["text_primary"]
            ).grid(row=1, column=0, padx=20, pady=2, sticky="w")

            # Especialidad con color
            ctk.CTkLabel(
                card, text=esp,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=color_esp
            ).grid(row=2, column=0, padx=20, pady=(0, 5), sticky="w")

            # Cédula y teléfono
            ctk.CTkLabel(
                card, text=f"CC: {vet.get('cedula', '')}",
                font=ctk.CTkFont(size=11),
                text_color=self.C["text_secondary"]
            ).grid(row=3, column=0, padx=20, pady=1, sticky="w")

            ctk.CTkLabel(
                card, text=f"📞 {vet.get('telefono', '')}",
                font=ctk.CTkFont(size=11),
                text_color=self.C["text_secondary"]
            ).grid(row=4, column=0, padx=20, pady=1, sticky="w")

            ctk.CTkLabel(
                card, text=f"✉ {vet.get('email', '')}",
                font=ctk.CTkFont(size=11),
                text_color=self.C["text_secondary"]
            ).grid(row=5, column=0, padx=20, pady=(1, 15), sticky="w")

            ctk.CTkButton(
                card, text="🗑 Eliminar",
                fg_color="transparent",
                hover_color=self.C["bg_primary"],
                text_color=self.C["danger"],
                height=30, corner_radius=8, width=100,
                command=lambda did=doc_id: self._eliminar(did)
            ).grid(row=6, column=0, padx=20, pady=(0, 15), sticky="w")

    def _eliminar(self, doc_id: str):
        from database.repositorios import VeterinarioRepositorio
        if messagebox.askyesno("Confirmar", "¿Eliminar este veterinario?"):
            repo = VeterinarioRepositorio()
            if repo.eliminar(doc_id):
                self._cargar_tabla()
            else:
                messagebox.showerror("Error", "No se pudo eliminar.")

    def _abrir_form(self):
        FormVeterinario(self, self.C, self._svc, self._cargar_tabla)


class FormVeterinario(ctk.CTkToplevel):
    def __init__(self, parent, colors, svc, callback):
        super().__init__(parent)
        self.C = colors
        self._svc = svc
        self._callback = callback
        self.title("Registrar Veterinario")
        self.geometry("480x560")
        self.configure(fg_color=colors["bg_secondary"])
        self.grab_set()
        self._construir()

    def _construir(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        ctk.CTkLabel(scroll, text="Nuevo Veterinario",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=self.C["accent"]).pack(padx=30, pady=(25, 20), anchor="w")

        self._campos = {}
        campos = [
            ("nombre", "Nombre *"),
            ("apellido", "Apellido *"),
            ("cedula", "Cédula *"),
            ("telefono", "Teléfono"),
            ("email", "Email *"),
            ("tarjeta", "Tarjeta Profesional"),
        ]
        for key, label in campos:
            ctk.CTkLabel(scroll, text=label, font=ctk.CTkFont(size=12),
                         text_color=self.C["text_secondary"]).pack(padx=30, anchor="w")
            entry = ctk.CTkEntry(
                scroll, height=36, fg_color=self.C["bg_card"],
                border_color=self.C["border"], text_color=self.C["text_primary"]
            )
            entry.pack(padx=30, pady=(2, 10), fill="x")
            self._campos[key] = entry

        # Especialidad
        ctk.CTkLabel(scroll, text="Especialidad *", font=ctk.CTkFont(size=12),
                     text_color=self.C["text_secondary"]).pack(padx=30, anchor="w")
        self._esp_combo = ctk.CTkComboBox(
            scroll, values=Veterinario.ESPECIALIDADES,
            fg_color=self.C["bg_card"], border_color=self.C["border"],
            text_color=self.C["text_primary"], height=36
        )
        self._esp_combo.pack(padx=30, pady=(2, 20), fill="x")

        ctk.CTkButton(
            scroll, text="✅ Registrar Veterinario",
            fg_color=self.C["accent"], hover_color="#00A87C",
            text_color="#000", height=40, corner_radius=10,
            command=self._guardar
        ).pack(padx=30, pady=(0, 30), fill="x")

    def _guardar(self):
        datos = {k: v.get().strip() for k, v in self._campos.items()}
        if not all([datos["nombre"], datos["apellido"], datos["cedula"], datos["email"]]):
            messagebox.showwarning("Campos requeridos", "Completa los campos obligatorios.")
            return
        ok, msg = self._svc.registrar(
            nombre=datos["nombre"],
            apellido=datos["apellido"],
            cedula=datos["cedula"],
            telefono=datos["telefono"],
            email=datos["email"],
            especialidad=self._esp_combo.get(),
            tarjeta=datos["tarjeta"]
        )
        if ok:
            messagebox.showinfo("Éxito", "Veterinario registrado correctamente.")
            self._callback()
            self.destroy()
        else:
            messagebox.showerror("Error", msg)
