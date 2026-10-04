# login_screen.py
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image 
import os

# Importa o banco de dados
try:
    from database.db_manager import connect_db, init_db
except ImportError:
    import sqlite3
    print("AVISO: Módulo db_manager não importado. Tentando criar DB localmente.")
    if not os.path.exists("database"): os.makedirs("database")
    conn = sqlite3.connect("database/estoque_restaurante.db")
    conn.execute("CREATE TABLE IF NOT EXISTS usuarios (username TEXT, password TEXT)")
    conn.execute("INSERT OR IGNORE INTO usuarios (username, password) VALUES ('admin', 'admin')")
    conn.commit()
    conn.close()
    def connect_db(): return sqlite3.connect("database/estoque_restaurante.db")

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class LoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sistema de Estoque - Restaurante | Acesso")
        self.geometry("400x550")
        self.resizable(False, False)

        # Procura o logo na pasta assets
        logo_path = os.path.join("assets", "logo.ico")
        if not os.path.exists(logo_path):
            logo_path = os.path.join("assets", "logo_marca.png")

        try:
            self.logo_image = ctk.CTkImage(light_image=Image.open(logo_path),
                                           dark_image=Image.open(logo_path),
                                           size=(180, 120))
            print(f"Logo carregado de: {logo_path}")
        except Exception as e:
            print(f"AVISO: Não foi possível carregar a imagem do logo: {e}")
            self.logo_image = None

        self.grid_columnconfigure(0, weight=1)

        # --- Cabeçalho da Marca ---
        self.frame_marca = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_marca.grid(row=0, column=0, pady=(40, 20), padx=20, sticky="ew")

        if self.logo_image:
            self.label_logo = ctk.CTkLabel(self.frame_marca, image=self.logo_image, text="")
            self.label_logo.pack()
        else:
            self.label_marca_text = ctk.CTkLabel(self.frame_marca, text="SEU LOGO AQUI", font=("Arial Bold", 24), text_color=("blue", "cyan"))
            self.label_marca_text.pack()
            
        self.label_titulo = ctk.CTkLabel(self.frame_marca, text="Controle de Estoque", font=("Roboto", 18))
        self.label_titulo.pack(pady=(10, 0))

        # --- Área de Login ---
        self.frame_login = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_login.grid(row=1, column=0, pady=20, padx=40, sticky="ew")

        self.entry_usuario = ctk.CTkEntry(self.frame_login, placeholder_text="Utilizador", height=45, corner_radius=10)
        self.entry_usuario.pack(pady=(0, 15), fill="x")
        
        self.entry_senha = ctk.CTkEntry(self.frame_login, placeholder_text="Palavra-passe", show="*", height=45, corner_radius=10)
        self.entry_senha.pack(pady=(0, 20), fill="x")
        
        # Corrigido para evitar erro de cor no botão
        self.btn_login = ctk.CTkButton(self.frame_login, text="Entrar", command=self.fazer_login, height=50, corner_radius=10, fg_color="#1f538d", hover_color="#14375e")
        self.btn_login.pack(pady=(0, 20), fill="x")

        # --- Rodapé ---
        self.label_rodape = ctk.CTkLabel(self, text= "Desenvolvido por: Algorithm's Tech - Solução & Inovação (Jackson Magalhães)", font=("Arial", 10), text_color="gray")
        self.grid_rowconfigure(2, weight=1)
        self.label_rodape.grid(row=2, column=0, pady=10)

    def fazer_login(self):
        usuario = self.entry_usuario.get().strip()
        senha = self.entry_senha.get().strip()
        
        if not usuario or not senha:
             messagebox.showwarning("Campos Vazios", "Por favor, preencha o utilizador e a palavra-passe.")
             return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM usuarios WHERE username = ? AND password = ?", (usuario, senha))
            resultado = cursor.fetchone()
            
            if resultado:
                messagebox.showinfo("Sucesso", f"Bem-vindo(a), {usuario}!")
                self.abrir_tela_principal(usuario)
            else:
                messagebox.showerror("Erro", "Utilizador ou palavra-passe incorretos.")
                
            conn.close()
        except Exception as e:
            messagebox.showerror("Erro de Conexão", f"Não foi possível conectar à base de dados: {e}")

    def abrir_tela_principal(self, usuario_logado):
        self.destroy()
        from main_app import MainApp
        app_principal = MainApp(usuario_logado)
        app_principal.aminloop()

if __name__ == "__main__":
    init_db()
    app = LoginApp()
    app.mainloop()
