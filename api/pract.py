import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import requests
import json
from datetime import datetime
import threading
from ttkthemes import ThemedTk
from PIL import Image, ImageTk
import base64
import io
import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../chatbot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class ThemeManager:
    LIGHT_THEME = {
        "background": "#ffffff",
        "primary": "#2196F3",
        "secondary": "#4CAF50",
        "text_dark": "#212121",
        "text_light": "#ffffff",
        "user_message": "#E3F2FD",
        "bot_message": "#F5F5F5",
        "accent": "#9C27B0",
        "error": "#F44336",
        "success": "#4CAF50",
        "border": "#E0E0E0"
    }

    @classmethod
    def get_theme(cls, is_dark: bool = False) -> dict:
        return cls.DARK_THEME if is_dark else cls.LIGHT_THEME

class ImageViewer(tk.Toplevel):
    def __init__(self, parent, image_data):
        super().__init__(parent)
        self.title("Visualizador de Imagem")
        self.zoom_level = 1.0
        self.pan_x = 0
        self.pan_y = 0

        try:
            image_bytes = base64.b64decode(image_data)
            self.original_image = Image.open(io.BytesIO(image_bytes))
            self.setup_ui()
            self.center_window()
            self.bind_events()
            self.update_image()

        except Exception as e:
            logging.error(f"Erro ao inicializar visualizador: {e}")
            messagebox.showerror("Erro", "Não foi possível abrir a imagem")
            self.destroy()

    def setup_ui(self):
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(
            self.main_frame,
            bg='#121212',
            highlightthickness=0
        )
        self.h_scroll = ttk.Scrollbar(
            self.main_frame,
            orient='horizontal',
            command=self.canvas.xview
        )
        self.v_scroll = ttk.Scrollbar(
            self.main_frame,
            orient='vertical',
            command=self.canvas.yview
        )

        self.canvas.configure(
            xscrollcommand=self.h_scroll.set,
            yscrollcommand=self.v_scroll.set
        )

        self.canvas.grid(row=0, column=0, sticky='nsew')
        self.h_scroll.grid(row=1, column=0, sticky='ew')
        self.v_scroll.grid(row=0, column=1, sticky='ns')

        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

    def bind_events(self):
        self.canvas.bind('<ButtonPress-1>', self.start_pan)
        self.canvas.bind('<B1-Motion>', self.pan_image)
        self.canvas.bind('<MouseWheel>', self.zoom_at_point)
        self.canvas.bind('<Button-4>', lambda e: self.zoom_at_point(e, 1))
        self.canvas.bind('<Button-5>', lambda e: self.zoom_at_point(e, -1))

    def start_pan(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def pan_image(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def zoom_at_point(self, event, delta=None):
        if delta is None:
            delta = event.delta

        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        if delta > 0:
            self.zoom_level = min(5.0, self.zoom_level * 1.1)
        else:
            self.zoom_level = max(0.1, self.zoom_level / 1.1)

        self.update_image(zoom_point=(x, y))

    def update_image(self, zoom_point=None):
        try:
            width = int(self.original_image.width * self.zoom_level)
            height = int(self.original_image.height * self.zoom_level)

            resized = self.original_image.resize(
                (width, height),
                Image.Resampling.LANCZOS
            )

            self.photo = ImageTk.PhotoImage(resized)

            self.canvas.delete('all')

            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            x = max(0, (canvas_width - width) // 2)
            y = max(0, (canvas_height - height) // 2)

            self.canvas.create_image(x, y, image=self.photo, anchor='nw')

            self.canvas.configure(scrollregion=self.canvas.bbox('all'))

            if zoom_point:
                self.canvas.xview_moveto(zoom_point[0] / width)
                self.canvas.yview_moveto(zoom_point[1] / height)

        except Exception as e:
            logging.error(f"Erro ao atualizar imagem: {e}")

    def center_window(self):
        """Centraliza a janela na tela"""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        width = min(self.original_image.width + 100, int(screen_width * 0.8))
        height = min(self.original_image.height + 100, int(screen_height * 0.8))

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        self.geometry(f'{width}x{height}+{x}+{y}')

class ChatbotPRACT:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.load_config()
        self.setup_styles()
        self.create_widgets()
        self.initialize_chat()

    def setup_window(self):
        self.root.title("ERP Master Assistant")
        self.root.geometry("1000x800")
        self.is_dark_mode = False
        self.colors = ThemeManager.get_theme(self.is_dark_mode)

        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass

        self.style = ttk.Style()
        self.style.theme_use('clam')

    def load_config(self):
        config_path = Path("config.json")
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
                self.is_dark_mode = config.get("dark_mode", False)
                self.colors = ThemeManager.get_theme(self.is_dark_mode)

    def setup_styles(self):
        self.style.configure(".",
            background=self.colors["background"],
            foreground=self.colors["text_dark"],
            font=("Segoe UI", 10)
        )

        self.style.configure("Accent.TButton",
            padding=10,
            background=self.colors["accent"],
            foreground=self.colors["text_light"]
        )

        self.style.configure("Control.TButton",
            padding=5,
            background=self.colors["primary"],
            foreground=self.colors["text_light"],
            font=("Segoe UI", 9)
        )

        self.style.configure("Chat.TFrame",
            background=self.colors["background"]
        )

        self.style.configure("Chat.TEntry",
            padding=10,
            fieldbackground=self.colors["background"],
            foreground=self.colors["text_dark"]
        )

    def create_widgets(self):
        self.main_frame = ttk.Frame(
            self.root,
            style="Chat.TFrame",
            padding="20 20 20 20"
        )
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.create_header()
        self.create_chat_area()
        self.create_input_area()

    def create_header(self):
        header_frame = ttk.Frame(self.main_frame, style="Chat.TFrame")
        header_frame.pack(fill='x', pady=(0, 20))

        title_frame = ttk.Frame(header_frame, style="Chat.TFrame")
        title_frame.pack(side='left')

        shadow_label = ttk.Label(
            title_frame,
            text="ERP Master Assistant",
            font=("Segoe UI", 20, "bold"),
            foreground="#404040",
            background=self.colors["background"]
        )
        shadow_label.place(x=2, y=2)

        title_label = ttk.Label(
            title_frame,
            text="ERP Master Assistant",
            font=("Segoe UI", 20, "bold"),
            foreground=self.colors["primary"],
            background=self.colors["background"]
        )
        title_label.pack(side='left')

        control_frame = ttk.Frame(header_frame, style="Chat.TFrame")
        control_frame.pack(side='right')

        self.export_button = ttk.Button(
            control_frame,
            text="Exportar",
            style="Control.TButton",
            command=self.export_chat
        )
        self.export_button.pack(side='right', padx=5)

        self.clear_button = ttk.Button(
            control_frame,
            text="Limpar",
            style="Control.TButton",
            command=self.clear_chat
        )
        self.clear_button.pack(side='right', padx=5)

        self.exit_button = ttk.Button(
            control_frame,
            text="Sair",
            style="Control.TButton",
            command=self.exit_app
        )
        self.exit_button.pack(side='right', padx=5)

        self.status_label = ttk.Label(
            control_frame,
            text="●  Conectado",
            font=("Segoe UI", 10),
            foreground=self.colors["success"],
            background=self.colors["background"]
        )
        self.status_label.pack(side='right', padx=10)

    def create_chat_area(self):
        chat_frame = ttk.Frame(
            self.main_frame,
            style="Chat.TFrame",
            relief="solid",
            borderwidth=1
        )
        chat_frame.pack(fill=tk.BOTH, expand=True)

        self.chat_area = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=("Segoe UI", 11),
            bg=self.colors["background"],
            fg=self.colors["text_dark"],
            insertbackground=self.colors["text_dark"],
            selectbackground=self.colors["primary"],
            selectforeground=self.colors["text_light"],
            padx=20,
            pady=20,
            borderwidth=0,
            relief="flat"
        )
        self.chat_area.pack(fill=tk.BOTH, expand=True)
        self.chat_area.config(state=tk.DISABLED)

    def create_input_area(self):
        input_frame = ttk.Frame(
            self.main_frame,
            style="Chat.TFrame",
            padding="0 20 0 0"
        )
        input_frame.pack(fill='x', pady=(20, 0))

        self.input_field = ttk.Entry(
            input_frame,
            font=("Segoe UI", 11),
            style="Chat.TEntry"
        )
        self.input_field.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        self.send_button = ttk.Button(
            input_frame,
            text="Enviar",
            style="Accent.TButton",
            command=self.send_message
        )
        self.send_button.pack(side=tk.RIGHT)

        self.input_field.bind("<Return>", lambda e: self.send_message())

    def initialize_chat(self):
        self.chat_history = []
        self.images = []

        welcome_message = (
            "👋 Olá! Eu sou o assistente virtual do ERP Master.\n\n"
            "Posso ajudar você com:\n"
            "• Relatórios Personalizados\n"
            "• Solução de Erros Comuns\n"
            "• Suporte Técnico\n"
            "• Informações Gerais\n\n"
            "Como posso ajudar você hoje?"
        )
        self.add_bot_message(welcome_message)

    def add_bot_message(self, message, images_data=None):
        self.add_message(message, "bot", images_data)

    def add_user_message(self, message):
        self.add_message(message, "user")

    def send_message(self):
        message = self.input_field.get().strip()
        if message:
            self.input_field.delete(0, tk.END)
            self.add_user_message(message)
            threading.Thread(target=self.get_bot_response, args=(message,)).start()

    def get_bot_response(self, message):
        try:
            response = requests.post(
                "http://localhost:8000/chat",
                json={"question": message},
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                if data["status"] == "success":
                    self.root.after(0, self.add_bot_message,
                                  data["response"],
                                  data.get("images", []))
                else:
                    self.root.after(0, self.add_bot_message,
                        "Desculpe, não entendi. Pode reformular a pergunta?")
            else:
                self.root.after(0, self.add_bot_message,
                    "Desculpe, estou com problemas técnicos no momento.")

        except requests.exceptions.RequestException as e:
            self.root.after(0, self.add_bot_message,
                f"Erro ao conectar com o servidor: {str(e)}")
            self.update_status("Desconectado", "error")

    def add_message(self, message, sender, images_data=None):
        try:
            self.chat_area.config(state=tk.NORMAL)

            if self.chat_history:
                self.chat_area.insert(tk.END, "\n\n")

            if sender == "user":
                tag_name = "user_message"
                sender_name = "Você"
            else:
                tag_name = "bot_message"
                sender_name = "Assistente"

            self.chat_area.tag_configure(
                tag_name,
                background=self.colors[f"{sender}_message"],
                foreground=self.colors["text_dark"],
                font=("Segoe UI", 11),
                spacing1=10,
                spacing3=10,
                lmargin1=20,
                lmargin2=20,
                rmargin=20
            )

            timestamp = datetime.now().strftime("%H:%M")
            header = f"{sender_name} - {timestamp}"
            self.chat_area.insert(tk.END, header + "\n", "small")

            self.chat_area.insert(tk.END, message, tag_name)

            if images_data:
                for image_data in images_data:
                    self.add_image(image_data)

            self.chat_area.see(tk.END)
            self.chat_area.config(state=tk.DISABLED)

            self.chat_history.append({
                "sender": sender,
                "message": message,
                "timestamp": timestamp,
                "images": images_data
            })

        except Exception as e:
            logging.error(f"Erro ao adicionar mensagem: {e}")
            messagebox.showerror("Erro", "Erro ao adicionar mensagem ao chat")

    def add_image(self, image_data):
        try:
            image_bytes = base64.b64decode(image_data)
            original_image = Image.open(io.BytesIO(image_bytes))

            max_width = 300
            ratio = max_width / float(original_image.width)
            height = int(float(original_image.height) * ratio)
            thumbnail = original_image.resize((max_width, height), Image.Resampling.LANCZOS)

            photo = ImageTk.PhotoImage(thumbnail)
            self.images.append(photo)

            image_frame = ttk.Frame(
                self.chat_area,
                style="Chat.TFrame",
                relief="solid",
                borderwidth=1
            )

            image_label = ttk.Label(
                image_frame,
                image=photo,
                cursor="hand2",
                background=self.colors["background"]
            )
            image_label.pack(pady=5)

            hint_label = ttk.Label(
                image_frame,
                text="Clique para ampliar",
                font=("Segoe UI", 9),
                foreground="#666666",
                background=self.colors["background"]
            )
            hint_label.pack(pady=(0, 5))

            self.chat_area.window_create(tk.END, window=image_frame)
            self.chat_area.insert(tk.END, "\n")

            image_label.bind('<Button-1>',
                lambda e: ImageViewer(self.root, image_data))

        except Exception as e:
            logging.error(f"Erro ao adicionar imagem: {e}")
            self.chat_area.insert(tk.END, "\n[Erro ao carregar imagem]\n")

    def update_status(self, status, status_type="success"):
        self.status_label.configure(
            text=f"●  {status}",
            foreground=self.colors[status_type]
        )

    def update_colors(self):
        self.setup_styles()

        self.chat_area.configure(
            bg=self.colors["background"],
            fg=self.colors["text_dark"]
        )

        self.status_label.configure(
            foreground=self.colors["success"]
            if "Conectado" in self.status_label.cget("text")
            else self.colors["error"],
            background=self.colors["background"]
        )

        self.redraw_messages()

    def redraw_messages(self):
        messages = self.chat_history.copy()
        self.chat_history = []
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.delete(1.0, tk.END)

        for msg in messages:
            self.add_message(
                msg["message"],
                msg["sender"],
                msg.get("images")
            )

    def export_chat(self):
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Arquivo de texto", "*.txt")],
                title="Exportar conversa"
            )

            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    for msg in self.chat_history:
                        sender = "Você" if msg["sender"] == "user" else "Assistente"
                        f.write(f"{sender} - {msg['timestamp']}\n")
                        f.write(f"{msg['message']}\n\n")

                messagebox.showinfo(
                    "Sucesso",
                    "Conversa exportada com sucesso!"
                )

        except Exception as e:
            logging.error(f"Erro ao exportar chat: {e}")
            messagebox.showerror(
                "Erro",
                "Não foi possível exportar a conversa"
            )

    def clear_chat(self):
        if messagebox.askyesno("Confirmar", "Deseja limpar toda a conversa?"):
            self.chat_history = []
            self.images = []
            self.chat_area.config(state=tk.NORMAL)
            self.chat_area.delete(1.0, tk.END)
            self.chat_area.config(state=tk.DISABLED)
            self.initialize_chat()

    def exit_app(self):
        if messagebox.askyesno("Confirmar", "Deseja realmente sair?"):
            self.root.quit()

def main():
    try:
        root = ThemedTk(theme="arc")
        app = ChatbotPRACT(root)
        root.mainloop()

    except Exception as e:
        logging.error(f"Erro fatal: {e}")
        messagebox.showerror(
            "Erro Fatal",
            "Ocorreu um erro ao iniciar a aplicação"
        )

if __name__ == "__main__":
    main()
