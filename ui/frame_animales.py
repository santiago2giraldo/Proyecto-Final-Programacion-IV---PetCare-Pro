"""
Módulo: frame_animales.py
Interfaz gráfica para gestión de animales/mascotas.
Pantalla #3 del sistema. Demuestra polimorfismo visualmente.
"""

import customtkinter as ctk
from tkinter import messagebox
from utils.servicios import ServicioAnimal, ServicioCliente


TIPO_ICONOS = {"Perro": "🐶", "Gato": "🐱", "Ave": "🦜", "Reptil": "🦎"}
TIPO_COLORES = {
    "Perro":  "#0099FF",
    "Gato":   "#B388FF",
    "Ave":    "#00C896",
    "Reptil": "#FFA502",
}


class FrameAnimales(ctk.CTkFrame):
    def __init__(self, parent, colors: dict):
        super().__init__(parent, fg_color=colors["bg_primary"], corner_radius=0)
        self.C = colors
        self._svc = ServicioAnimal()
        self._svc_cli = ServicioCliente()
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self._construir()
        self._cargar_tabla()

    def _construir(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=30, pady=(30, 15), sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header, text="🐾 Gestión de Animales",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=self.C["text_primary"]
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            header, text="➕ Registrar Mascota",
            fg_color=self.C["accent"], hover_color="#00A87C",
            text_color="#000", height=38, width=180, corner_radius=10,
            command=self._abrir_form
        ).grid(row=0, column=2, sticky="e")

        # Filtro por tipo
        filtro_frame = ctk.CTkFrame(self, fg_color=self.C["bg_card"],
                                    corner_radius=12, border_width=1,
                                    border_color=self.C["border"])
        filtro_frame.grid(row=1, column=0, padx=30, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(filtro_frame, text="Filtrar:",
                     font=ctk.CTkFont(size=12),
                     text_color=self.C["text_secondary"]).pack(side="left", padx=15, pady=10)

        self._filtro_var = ctk.StringVar(value="Todos")
        for tipo in ["Todos", "Perro", "Gato", "Ave", "Reptil"]:
            ctk.CTkRadioButton(
                filtro_frame, text=tipo,
                variable=self._filtro_var, value=tipo,
                font=ctk.CTkFont(size=12),
                text_color=self.C["text_primary"],
                fg_color=self.C["accent"],
                command=self._cargar_tabla
            ).pack(side="left", padx=10, pady=10)

        # Tabla
        self._tabla_frame = ctk.CTkScrollableFrame(
            self, fg_color=self.C["bg_card"], corner_radius=16,
            border_width=1, border_color=self.C["border"]
        )
        self._tabla_frame.grid(row=2, column=0, padx=30, pady=(5, 30), sticky="nsew")
        self._tabla_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        cols = ["Tipo", "Nombre", "Raza / Especie", "Edad", "Peso", "Riesgo"]
        for c, texto in enumerate(cols):
            ctk.CTkLabel(
                self._tabla_frame, text=texto,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=self.C["text_secondary"]
            ).grid(row=0, column=c, padx=12, pady=12, sticky="w")

        ctk.CTkFrame(self._tabla_frame, height=1,
                     fg_color=self.C["border"]).grid(
            row=1, column=0, columnspan=6, sticky="ew", padx=10
        )

    def _cargar_tabla(self, datos=None):
        for widget in self._tabla_frame.winfo_children():
            info = widget.grid_info()
            if info and int(info.get("row", 0)) > 1:
                widget.destroy()

        animales = datos if datos is not None else self._svc.listar()
        filtro = self._filtro_var.get()
        if filtro != "Todos":
            animales = [a for a in animales if a.get("tipo", "") == filtro]

        if not animales:
            ctk.CTkLabel(
                self._tabla_frame,
                text="No hay animales registrados.",
                text_color=self.C["text_secondary"],
                font=ctk.CTkFont(size=14)
            ).grid(row=2, column=0, columnspan=6, padx=15, pady=40)
            return

        for r, animal in enumerate(animales):
            tipo = animal.get("tipo", "?")
            icono = TIPO_ICONOS.get(tipo, "🐾")
            color_tipo = TIPO_COLORES.get(tipo, self.C["text_secondary"])
            row_idx = r + 2

            # Tipo con ícono y color
            ctk.CTkLabel(
                self._tabla_frame, text=f"{icono} {tipo}",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=color_tipo
            ).grid(row=row_idx, column=0, padx=12, pady=10, sticky="w")

            # Nombre
            ctk.CTkLabel(
                self._tabla_frame, text=animal.get("nombre", "?"),
                font=ctk.CTkFont(size=13),
                text_color=self.C["text_primary"]
            ).grid(row=row_idx, column=1, padx=12, pady=10, sticky="w")

            # Raza/Especie
            raza = animal.get("raza", animal.get("especie_ave", animal.get("especie", "?")))
            ctk.CTkLabel(
                self._tabla_frame, text=str(raza),
                font=ctk.CTkFont(size=12),
                text_color=self.C["text_secondary"]
            ).grid(row=row_idx, column=2, padx=12, pady=10, sticky="w")

            # Edad
            ctk.CTkLabel(
                self._tabla_frame, text=f"{animal.get('edad', '?')} años",
                font=ctk.CTkFont(size=12),
                text_color=self.C["text_secondary"]
            ).grid(row=row_idx, column=3, padx=12, pady=10, sticky="w")

            # Peso
            ctk.CTkLabel(
                self._tabla_frame, text=f"{animal.get('peso', '?')} kg",
                font=ctk.CTkFont(size=12),
                text_color=self.C["text_secondary"]
            ).grid(row=row_idx, column=4, padx=12, pady=10, sticky="w")

            # Riesgo (calculado)
            riesgo = self._calcular_riesgo_display(animal)
            ctk.CTkLabel(
                self._tabla_frame, text=riesgo,
                font=ctk.CTkFont(size=11),
                text_color=self.C["text_primary"]
            ).grid(row=row_idx, column=5, padx=12, pady=10, sticky="w")

    def _calcular_riesgo_display(self, animal: dict) -> str:
        """Llama al método polimórfico del objeto correspondiente."""
        from models.animal import Perro, Gato, Ave, Reptil
        tipo = animal.get("tipo", "")
        try:
            if tipo == "Perro":
                obj = Perro.from_dict(animal)
            elif tipo == "Gato":
                obj = Gato.from_dict(animal)
            elif tipo == "Ave":
                obj = Ave.from_dict(animal)
            elif tipo == "Reptil":
                obj = Reptil.from_dict(animal)
            else:
                return "?"
            return obj.calcular_riesgo()
        except Exception:
            return "?"

    def _abrir_form(self):
        FormAnimal(self, self.C, self._svc, self._svc_cli, self._cargar_tabla)


class FormAnimal(ctk.CTkToplevel):
    """Formulario modal para registrar un animal."""

    def __init__(self, parent, colors, svc, svc_cli, callback):
        super().__init__(parent)
        self.C = colors
        self._svc = svc
        self._svc_cli = svc_cli
        self._callback = callback
        self.title("Registrar Animal")
        self.geometry("500x620")
        self.configure(fg_color=colors["bg_secondary"])
        self.grab_set()
        self._tipo_var = ctk.StringVar(value="Perro")
        self._construir()

    def _construir(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=0, pady=0)

        ctk.CTkLabel(scroll, text="Registrar Mascota",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=self.C["accent"]).pack(padx=30, pady=(25, 10), anchor="w")

        # Tipo de animal
        ctk.CTkLabel(scroll, text="Tipo de animal *",
                     font=ctk.CTkFont(size=12),
                     text_color=self.C["text_secondary"]).pack(padx=30, anchor="w")
        tipo_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        tipo_frame.pack(padx=30, pady=(4, 14), fill="x")
        for tipo in ["Perro", "Gato", "Ave", "Reptil"]:
            ctk.CTkRadioButton(
                tipo_frame, text=f"{TIPO_ICONOS[tipo]} {tipo}",
                variable=self._tipo_var, value=tipo,
                fg_color=self.C["accent"],
                text_color=self.C["text_primary"]
            ).pack(side="left", padx=10)

        # Campos base
        self._campos = {}
        campos_base = [
            ("nombre", "Nombre de la mascota *"),
            ("raza", "Raza / Especie *"),
            ("edad", "Edad (años) *"),
            ("peso", "Peso (kg) *"),
        ]
        for key, label in campos_base:
            ctk.CTkLabel(scroll, text=label, font=ctk.CTkFont(size=12),
                         text_color=self.C["text_secondary"]).pack(padx=30, anchor="w")
            entry = ctk.CTkEntry(
                scroll, height=36, fg_color=self.C["bg_card"],
                border_color=self.C["border"], text_color=self.C["text_primary"]
            )
            entry.pack(padx=30, pady=(2, 10), fill="x")
            self._campos[key] = entry

        # Sexo
        ctk.CTkLabel(scroll, text="Sexo *", font=ctk.CTkFont(size=12),
                     text_color=self.C["text_secondary"]).pack(padx=30, anchor="w")
        self._sexo_var = ctk.StringVar(value="Macho")
        sexo_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        sexo_frame.pack(padx=30, pady=(4, 14), fill="x")
        for s in ["Macho", "Hembra"]:
            ctk.CTkRadioButton(
                sexo_frame, text=s, variable=self._sexo_var, value=s,
                fg_color=self.C["accent"], text_color=self.C["text_primary"]
            ).pack(side="left", padx=10)

        # Cliente propietario
        ctk.CTkLabel(scroll, text="Cédula del propietario *",
                     font=ctk.CTkFont(size=12),
                     text_color=self.C["text_secondary"]).pack(padx=30, anchor="w")
        self._entry_cedula = ctk.CTkEntry(
            scroll, height=36, fg_color=self.C["bg_card"],
            border_color=self.C["border"], text_color=self.C["text_primary"],
            placeholder_text="Ingresa la cédula del dueño"
        )
        self._entry_cedula.pack(padx=30, pady=(2, 20), fill="x")

        ctk.CTkButton(
            scroll, text="✅ Registrar Mascota",
            fg_color=self.C["accent"], hover_color="#00A87C",
            text_color="#000", height=40, corner_radius=10,
            command=self._guardar
        ).pack(padx=30, pady=(0, 30), fill="x")

    def _guardar(self):
        try:
            datos = {k: v.get().strip() for k, v in self._campos.items()}
            datos["sexo"] = self._sexo_var.get()
            tipo = self._tipo_var.get()

            if not all([datos["nombre"], datos["raza"], datos["edad"], datos["peso"]]):
                messagebox.showwarning("Campos requeridos", "Completa todos los campos obligatorios.")
                return

            # Buscar cliente por cédula (obligatorio)
            cedula = self._entry_cedula.get().strip()
            if not cedula:
                messagebox.showwarning("Campo requerido", "La cédula del propietario es obligatoria.")
                return
            cli = self._svc_cli.buscar_por_cedula(cedula)
            if cli:
                datos["cliente_id"] = str(cli.get("_id", ""))
            else:
                messagebox.showwarning("Cliente no encontrado",
                                       f"No se encontró cliente con cédula {cedula}.")
                return

            ok, msg = self._svc.registrar(tipo, datos)
            if ok:
                messagebox.showinfo("Éxito", f"{tipo} registrado correctamente.")
                self._callback()
                self.destroy()
            else:
                messagebox.showerror("Error", msg)
        except Exception as e:
            messagebox.showerror("Error", str(e))
