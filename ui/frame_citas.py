"""
Módulo: frame_citas.py
Interfaz gráfica para gestión de citas.
Pantalla #4 del sistema. Integra patrón Observer.
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from utils.servicios import ServicioCita, ServicioAnimal, ServicioVeterinario, ServicioCliente
from patterns.observer import notificador_vet, notificador_cliente


ESTADO_COLORES = {
    "Pendiente":  "#FFA502",
    "Confirmada": "#0099FF",
    "En curso":   "#B388FF",
    "Completada": "#2ED573",
    "Cancelada":  "#FF4757",
}


class FrameCitas(ctk.CTkFrame):
    def __init__(self, parent, colors: dict):
        super().__init__(parent, fg_color=colors["bg_primary"], corner_radius=0)
        self.C = colors
        self._svc = ServicioCita()
        self._svc_animal = ServicioAnimal()
        self._svc_vet = ServicioVeterinario()
        self._svc_cli = ServicioCliente()
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._construir()
        self._cargar_tabla()

    def _construir(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=30, pady=(30, 15), sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header, text="📅 Gestión de Citas",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=self.C["text_primary"]
        ).grid(row=0, column=0, sticky="w")

        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.grid(row=0, column=2, sticky="e")

        ctk.CTkButton(
            btn_frame, text="🔔 Notificaciones",
            fg_color=self.C["bg_card"],
            hover_color=self.C["border"],
            text_color=self.C["accent"],
            border_width=1, border_color=self.C["accent"],
            height=38, width=170, corner_radius=10,
            command=self._ver_notificaciones
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_frame, text="➕ Agendar Cita",
            fg_color=self.C["accent"], hover_color="#00A87C",
            text_color="#000", height=38, width=160, corner_radius=10,
            command=self._abrir_form
        ).pack(side="left")

        # Tabla
        self._tabla_frame = ctk.CTkScrollableFrame(
            self, fg_color=self.C["bg_card"], corner_radius=16,
            border_width=1, border_color=self.C["border"]
        )
        self._tabla_frame.grid(row=1, column=0, padx=30, pady=(5, 30), sticky="nsew")
        self._tabla_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        cols = ["Fecha y hora", "Motivo", "Animal", "Veterinario", "Estado / Acciones"]
        for c, t in enumerate(cols):
            ctk.CTkLabel(
                self._tabla_frame, text=t,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=self.C["text_secondary"]
            ).grid(row=0, column=c, padx=12, pady=12, sticky="w")

        ctk.CTkFrame(self._tabla_frame, height=1,
                     fg_color=self.C["border"]).grid(
            row=1, column=0, columnspan=5, sticky="ew", padx=10
        )

    def _cargar_tabla(self):
        for widget in self._tabla_frame.winfo_children():
            info = widget.grid_info()
            if info and int(info.get("row", 0)) > 1:
                widget.destroy()

        citas = self._svc.listar()
        if not citas:
            ctk.CTkLabel(
                self._tabla_frame,
                text="No hay citas agendadas.",
                text_color=self.C["text_secondary"],
                font=ctk.CTkFont(size=14)
            ).grid(row=2, column=0, columnspan=5, padx=15, pady=40)
            return

        for r, cita in enumerate(reversed(citas)):
            row_idx = r + 2
            doc_id = str(cita.get("_id", ""))

            # Fecha
            fecha = cita.get("fecha_hora", "")
            if isinstance(fecha, datetime):
                fecha_str = fecha.strftime("%d/%m/%Y %H:%M")
            else:
                fecha_str = str(fecha)[:16]

            ctk.CTkLabel(self._tabla_frame, text=fecha_str,
                         font=ctk.CTkFont(size=12),
                         text_color=self.C["text_primary"]
                         ).grid(row=row_idx, column=0, padx=12, pady=10, sticky="w")

            ctk.CTkLabel(self._tabla_frame, text=cita.get("motivo", "?")[:25],
                         font=ctk.CTkFont(size=13),
                         text_color=self.C["text_primary"]
                         ).grid(row=row_idx, column=1, padx=12, pady=10, sticky="w")

            # Animal
            animal = self._svc_animal.buscar_por_id(cita.get("animal_id", ""))
            animal_nombre = animal.get("nombre", "?") if animal else cita.get("animal_id", "?")[:8]
            ctk.CTkLabel(self._tabla_frame, text=animal_nombre,
                         font=ctk.CTkFont(size=12),
                         text_color=self.C["text_secondary"]
                         ).grid(row=row_idx, column=2, padx=12, pady=10, sticky="w")

            # Veterinario
            vet = self._svc_vet.buscar_por_id(cita.get("veterinario_id", ""))
            vet_nombre = f"Dr. {vet.get('apellido', '?')}" if vet else "?"
            ctk.CTkLabel(self._tabla_frame, text=vet_nombre,
                         font=ctk.CTkFont(size=12),
                         text_color=self.C["text_secondary"]
                         ).grid(row=row_idx, column=3, padx=12, pady=10, sticky="w")

            # Estado + botón cambiar
            estado = cita.get("estado", "Pendiente")
            estado_color = ESTADO_COLORES.get(estado, self.C["text_secondary"])

            acciones_frame = ctk.CTkFrame(self._tabla_frame, fg_color="transparent")
            acciones_frame.grid(row=row_idx, column=4, padx=12, pady=8, sticky="w")

            ctk.CTkLabel(acciones_frame, text=estado,
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=estado_color
                         ).pack(side="left", padx=(0, 8))

            if estado not in ["Completada", "Cancelada"]:
                ctk.CTkButton(
                    acciones_frame, text="✏", width=28, height=26,
                    fg_color="transparent",
                    hover_color=self.C["bg_primary"],
                    text_color=self.C["accent2"],
                    corner_radius=6,
                    command=lambda did=doc_id, est=estado: self._cambiar_estado(did, est)
                ).pack(side="left")

    def _cambiar_estado(self, doc_id: str, estado_actual: str):
        siguientes = {
            "Pendiente": "Confirmada",
            "Confirmada": "Completada",
            "En curso": "Completada"
        }
        nuevo = siguientes.get(estado_actual, "Cancelada")
        if messagebox.askyesno("Cambiar estado", f"¿Cambiar estado a '{nuevo}'?"):
            if self._svc.actualizar_estado(doc_id, nuevo):
                self._cargar_tabla()
            else:
                messagebox.showerror("Error", "No se pudo actualizar el estado.")

    def _ver_notificaciones(self):
        VisorNotificaciones(self, self.C)

    def _abrir_form(self):
        FormCita(self, self.C, self._svc, self._svc_animal,
                 self._svc_vet, self._svc_cli, self._cargar_tabla)


class FormCita(ctk.CTkToplevel):
    def __init__(self, parent, colors, svc, svc_animal, svc_vet, svc_cli, callback):
        super().__init__(parent)
        self.C = colors
        self._svc = svc
        self._svc_animal = svc_animal
        self._svc_vet = svc_vet
        self._svc_cli = svc_cli
        self._callback = callback
        self.title("Agendar Cita")
        self.geometry("500x580")
        self.configure(fg_color=colors["bg_secondary"])
        self.grab_set()

        # Datos cargados
        self._animales = self._svc_animal.listar()
        self._vets = self._svc_vet.listar()
        self._clientes = self._svc_cli.listar()

        self._construir()

    def _construir(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        ctk.CTkLabel(scroll, text="Agendar Nueva Cita",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=self.C["accent"]).pack(padx=30, pady=(25, 20), anchor="w")

        def campo(label, widget_fn):
            ctk.CTkLabel(scroll, text=label, font=ctk.CTkFont(size=12),
                         text_color=self.C["text_secondary"]).pack(padx=30, anchor="w")
            w = widget_fn()
            w.pack(padx=30, pady=(2, 12), fill="x")
            return w

        # Animal
        animal_options = [f"{a.get('nombre','')} ({a.get('tipo','')})" for a in self._animales]
        self._animal_combo = campo("Animal / Mascota *", lambda: ctk.CTkComboBox(
            scroll, values=animal_options if animal_options else ["(Sin animales)"],
            fg_color=self.C["bg_card"], border_color=self.C["border"],
            text_color=self.C["text_primary"], height=36
        ))

        # Veterinario
        vet_options = [f"Dr. {v.get('apellido','')} - {v.get('especialidad','')}" for v in self._vets]
        self._vet_combo = campo("Veterinario *", lambda: ctk.CTkComboBox(
            scroll, values=vet_options if vet_options else ["(Sin veterinarios)"],
            fg_color=self.C["bg_card"], border_color=self.C["border"],
            text_color=self.C["text_primary"], height=36
        ))

        # Fecha
        self._entry_fecha = campo("Fecha (DD/MM/AAAA) *", lambda: ctk.CTkEntry(
            scroll, height=36, fg_color=self.C["bg_card"],
            border_color=self.C["border"], text_color=self.C["text_primary"],
            placeholder_text="ej: 25/06/2025"
        ))

        # Hora
        self._entry_hora = campo("Hora (HH:MM) *", lambda: ctk.CTkEntry(
            scroll, height=36, fg_color=self.C["bg_card"],
            border_color=self.C["border"], text_color=self.C["text_primary"],
            placeholder_text="ej: 10:30"
        ))

        # Motivo
        self._entry_motivo = campo("Motivo de la consulta *", lambda: ctk.CTkEntry(
            scroll, height=36, fg_color=self.C["bg_card"],
            border_color=self.C["border"], text_color=self.C["text_primary"],
            placeholder_text="ej: Vacunación anual"
        ))

        # Notas
        ctk.CTkLabel(scroll, text="Notas adicionales",
                     font=ctk.CTkFont(size=12),
                     text_color=self.C["text_secondary"]).pack(padx=30, anchor="w")
        self._text_notas = ctk.CTkTextbox(
            scroll, height=70, fg_color=self.C["bg_card"],
            border_color=self.C["border"], text_color=self.C["text_primary"]
        )
        self._text_notas.pack(padx=30, pady=(2, 20), fill="x")

        ctk.CTkButton(
            scroll, text="📅 Agendar Cita",
            fg_color=self.C["accent"], hover_color="#00A87C",
            text_color="#000", height=40, corner_radius=10,
            command=self._guardar
        ).pack(padx=30, pady=(0, 30), fill="x")

    def _guardar(self):
        try:
            animal_idx = self._animal_combo.get()
            vet_idx = self._vet_combo.get()
            fecha_str = self._entry_fecha.get().strip()
            hora_str = self._entry_hora.get().strip()
            motivo = self._entry_motivo.get().strip()

            if not all([animal_idx, vet_idx, fecha_str, hora_str, motivo]):
                messagebox.showwarning("Campos requeridos", "Completa todos los campos obligatorios.")
                return

            # Parsear fecha
            fecha_hora = datetime.strptime(f"{fecha_str} {hora_str}", "%d/%m/%Y %H:%M")

            # Obtener IDs
            a_idx = [f"{a.get('nombre','')} ({a.get('tipo','')})" for a in self._animales].index(animal_idx)
            v_idx = [f"Dr. {v.get('apellido','')} - {v.get('especialidad','')}" for v in self._vets].index(vet_idx)

            animal = self._animales[a_idx]
            vet = self._vets[v_idx]

            # Obtener cliente del animal
            cli_id = animal.get("cliente_id", "")
            if not cli_id:
                messagebox.showwarning(
                    "Sin propietario",
                    "La mascota seleccionada no tiene propietario registrado.\n"
                    "Registra primero al dueño y vuelve a crear la mascota."
                )
                return

            notas = self._text_notas.get("1.0", "end").strip()

            ok, msg = self._svc.agendar(
                animal_id=str(animal.get("_id", "")),
                veterinario_id=str(vet.get("_id", "")),
                cliente_id=cli_id,
                fecha_hora=fecha_hora,
                motivo=motivo,
                notas=notas
            )
            if ok:
                messagebox.showinfo("Éxito", "Cita agendada. Se han enviado notificaciones.")
                self._callback()
                self.destroy()
            else:
                messagebox.showerror("Error", msg)
        except ValueError:
            messagebox.showerror("Error de formato", "Verifica el formato de fecha (DD/MM/AAAA) y hora (HH:MM).")
        except Exception as e:
            messagebox.showerror("Error", str(e))


class VisorNotificaciones(ctk.CTkToplevel):
    """Muestra las notificaciones generadas por el patrón Observer."""

    def __init__(self, parent, colors):
        super().__init__(parent)
        self.C = colors
        self.title("🔔 Notificaciones del Sistema (Observer)")
        self.geometry("600x500")
        self.configure(fg_color=colors["bg_secondary"])
        self.grab_set()
        self._construir()

    def _construir(self):
        ctk.CTkLabel(self, text="🔔 Notificaciones",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=self.C["accent"]).pack(padx=30, pady=(25, 5), anchor="w")

        ctk.CTkLabel(self,
                     text="Generadas por el Patrón Observer al crear/actualizar citas",
                     font=ctk.CTkFont(size=11),
                     text_color=self.C["text_secondary"]).pack(padx=30, anchor="w")

        scroll = ctk.CTkScrollableFrame(self, fg_color=self.C["bg_card"],
                                        corner_radius=12)
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        todas = (notificador_vet.get_notificaciones() +
                 notificador_cliente.get_notificaciones())
        todas.sort(key=lambda x: x["timestamp"], reverse=True)

        if not todas:
            ctk.CTkLabel(scroll, text="No hay notificaciones aún.",
                         text_color=self.C["text_secondary"],
                         font=ctk.CTkFont(size=13)).pack(pady=30)
            return

        for notif in todas:
            card = ctk.CTkFrame(scroll, fg_color=self.C["bg_primary"],
                                corner_radius=10)
            card.pack(fill="x", padx=10, pady=5)

            tipo_color = self.C["accent2"] if notif["tipo"] == "Veterinario" else self.C["accent"]
            ctk.CTkLabel(card, text=f"[{notif['tipo']}] {notif['destinatario']}",
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=tipo_color).pack(padx=15, pady=(10, 2), anchor="w")
            ctk.CTkLabel(card, text=notif["mensaje"],
                         font=ctk.CTkFont(size=12),
                         text_color=self.C["text_primary"]).pack(padx=15, pady=(0, 2), anchor="w")
            ctk.CTkLabel(card, text=notif["timestamp"].strftime("%d/%m/%Y %H:%M:%S"),
                         font=ctk.CTkFont(size=10),
                         text_color=self.C["text_secondary"]).pack(padx=15, pady=(0, 10), anchor="w")
