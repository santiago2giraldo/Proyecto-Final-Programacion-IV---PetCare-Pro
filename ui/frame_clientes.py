"""
Módulo: frame_clientes.py
Interfaz gráfica para gestión de clientes.
Pantalla #2 del sistema.
"""

import customtkinter as ctk
from tkinter import messagebox
from utils.servicios import ServicioCliente


class FrameClientes(ctk.CTkFrame):
    """Frame para registrar, listar y buscar clientes."""

    def __init__(self, parent, colors: dict):
        super().__init__(parent, fg_color=colors["bg_primary"], corner_radius=0)
        self.C = colors
        self._svc = ServicioCliente()
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self._construir()
        self._cargar_tabla()

    def _construir(self):
        # ── Header ──
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=30, pady=(30, 15), sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header, text="👤 Gestión de Clientes",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=self.C["text_primary"]
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            header, text="➕ Nuevo Cliente",
            font=ctk.CTkFont(size=13),
            fg_color=self.C["accent"],
            hover_color="#00A87C",
            text_color="#000",
            height=38, width=160,
            corner_radius=10,
            command=self._abrir_form
        ).grid(row=0, column=2, sticky="e")

        # ── Buscador ──
        search_frame = ctk.CTkFrame(self, fg_color=self.C["bg_card"],
                                    corner_radius=12, border_width=1,
                                    border_color=self.C["border"])
        search_frame.grid(row=1, column=0, padx=30, pady=(0, 10), sticky="ew")
        search_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(search_frame, text="🔍",
                     font=ctk.CTkFont(size=16)).grid(row=0, column=0, padx=(15, 5), pady=10)

        self._entry_buscar = ctk.CTkEntry(
            search_frame, placeholder_text="Buscar por nombre o apellido...",
            font=ctk.CTkFont(size=13),
            fg_color="transparent",
            border_width=0,
            text_color=self.C["text_primary"]
        )
        self._entry_buscar.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        self._entry_buscar.bind("<KeyRelease>", self._on_buscar)

        # ── Tabla (scroll) ──
        self._tabla_frame = ctk.CTkScrollableFrame(
            self, fg_color=self.C["bg_card"],
            corner_radius=16, border_width=1,
            border_color=self.C["border"]
        )
        self._tabla_frame.grid(row=2, column=0, padx=30, pady=(5, 30), sticky="nsew")
        self._tabla_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        # Encabezados
        cols = ["Nombre completo", "Cédula", "Teléfono", "Email", "Acciones"]
        for c, texto in enumerate(cols):
            ctk.CTkLabel(
                self._tabla_frame, text=texto,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=self.C["text_secondary"]
            ).grid(row=0, column=c, padx=12, pady=12, sticky="w")

        ctk.CTkFrame(self._tabla_frame, height=1,
                     fg_color=self.C["border"]).grid(
            row=1, column=0, columnspan=5, sticky="ew", padx=10
        )

    def _cargar_tabla(self, datos=None):
        # Limpiar filas anteriores (no los encabezados)
        for widget in self._tabla_frame.winfo_children():
            info = widget.grid_info()
            if info and int(info.get("row", 0)) > 1:
                widget.destroy()

        clientes = datos if datos is not None else self._svc.listar()

        if not clientes:
            ctk.CTkLabel(
                self._tabla_frame,
                text="No hay clientes registrados. ¡Agrega el primero!",
                text_color=self.C["text_secondary"],
                font=ctk.CTkFont(size=14)
            ).grid(row=2, column=0, columnspan=5, padx=15, pady=40)
            return

        for r, cli in enumerate(clientes):
            bg = self.C["bg_card"] if r % 2 == 0 else self.C["bg_primary"]
            row_idx = r + 2

            nombre = f"{cli.get('nombre', '')} {cli.get('apellido', '')}"
            campos = [nombre, cli.get("cedula", ""), cli.get("telefono", ""), cli.get("email", "")]

            for c, val in enumerate(campos):
                ctk.CTkLabel(
                    self._tabla_frame, text=str(val),
                    font=ctk.CTkFont(size=13),
                    text_color=self.C["text_primary"],
                    anchor="w"
                ).grid(row=row_idx, column=c, padx=12, pady=10, sticky="w")

            doc_id = str(cli.get("_id", ""))
            btn_del = ctk.CTkButton(
                self._tabla_frame, text="🗑", width=36, height=28,
                fg_color="transparent",
                hover_color=self.C["bg_primary"],
                text_color=self.C["danger"],
                corner_radius=6,
                command=lambda did=doc_id: self._eliminar(did)
            )
            btn_del.grid(row=row_idx, column=4, padx=12, pady=8, sticky="w")

    def _on_buscar(self, event=None):
        texto = self._entry_buscar.get().strip()
        if texto:
            resultados = self._svc.buscar_por_nombre(texto)
        else:
            resultados = self._svc.listar()
        self._cargar_tabla(resultados)

    def _eliminar(self, doc_id: str):
        if messagebox.askyesno("Confirmar", "¿Eliminar este cliente?"):
            if self._svc.eliminar(doc_id):
                self._cargar_tabla()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el cliente.")

    def _abrir_form(self):
        FormCliente(self, self.C, self._svc, self._cargar_tabla)


class FormCliente(ctk.CTkToplevel):
    """Formulario modal para registrar un nuevo cliente."""

    def __init__(self, parent, colors, svc, callback):
        super().__init__(parent)
        self.C = colors
        self._svc = svc
        self._callback = callback
        self.title("Registrar Cliente")
        self.geometry("480x500")
        self.configure(fg_color=colors["bg_secondary"])
        self.grab_set()
        self._construir()

    def _construir(self):
        ctk.CTkLabel(self, text="Nuevo Cliente",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=self.C["accent"]).pack(padx=30, pady=(25, 20), anchor="w")

        self._campos = {}
        campos = [
            ("nombre", "Nombre *"),
            ("apellido", "Apellido *"),
            ("cedula", "Cédula *"),
            ("telefono", "Teléfono"),
            ("email", "Email *"),
            ("direccion", "Dirección"),
        ]
        for key, label in campos:
            ctk.CTkLabel(self, text=label, font=ctk.CTkFont(size=12),
                         text_color=self.C["text_secondary"]).pack(padx=30, anchor="w")
            entry = ctk.CTkEntry(
                self, height=36, fg_color=self.C["bg_card"],
                border_color=self.C["border"], text_color=self.C["text_primary"]
            )
            entry.pack(padx=30, pady=(2, 10), fill="x")
            self._campos[key] = entry

        ctk.CTkButton(
            self, text="✅ Guardar Cliente",
            fg_color=self.C["accent"], hover_color="#00A87C",
            text_color="#000", height=40, corner_radius=10,
            command=self._guardar
        ).pack(padx=30, pady=20, fill="x")

    def _guardar(self):
        datos = {k: v.get().strip() for k, v in self._campos.items()}
        if not all([datos["nombre"], datos["apellido"], datos["cedula"], datos["email"]]):
            messagebox.showwarning("Campos requeridos", "Completa los campos obligatorios (*).")
            return
        ok, msg = self._svc.registrar(**datos)
        if ok:
            messagebox.showinfo("Éxito", "Cliente registrado correctamente.")
            self._callback()
            self.destroy()
        else:
            messagebox.showerror("Error", msg)
