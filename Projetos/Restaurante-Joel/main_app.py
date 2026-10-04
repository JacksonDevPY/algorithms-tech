# main_app.py
import customtkinter as ctk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime
import os

# Importa a conexão com o banco de dados
from database.db_manager import connect_db

class MainApp(ctk.CTk):
    def __init__(self, usuario_logado):
        super().__init__()

        self.usuario_logado = usuario_logado
        self.title(f"Sistema de Estoque - Restaurante | Utilizador: {self.usuario_logado}")
        self.geometry("900x600")
        self.minsize(800, 500)

        # Configuração do Layout Principal (Menu Lateral + Área de Conteúdo)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- MENU LATERAL ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Restaurante\nControle", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Botões do Menu
        self.btn_dashboard = ctk.CTkButton(self.sidebar_frame, text="📊 Alertas & Dashboard", command=lambda: self.mudar_aba("dashboard"))
        self.btn_dashboard.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.btn_produtos = ctk.CTkButton(self.sidebar_frame, text="📦 Produtos", command=lambda: self.mudar_aba("produtos"))
        self.btn_produtos.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.btn_entradas = ctk.CTkButton(self.sidebar_frame, text="📥 Entradas & Validade", command=lambda: self.mudar_aba("entradas"))
        self.btn_entradas.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        self.btn_sair = ctk.CTkButton(self.sidebar_frame, text="Sair / Fechar", fg_color="red", hover_color="darkred", command=self.destroy)
        self.btn_sair.grid(row=5, column=0, padx=20, pady=20, sticky="ew")

        # --- ÁREA DE CONTEÚDO PRINCIPAL ---
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        # Dicionário para armazenar as telas/abas
        self.frames = {}
        
        # Inicializa as telas
        self.criar_tela_dashboard()
        self.criar_tela_produtos()
        self.criar_tela_entradas()

        # Mostra o Dashboard por padrão
        self.mudar_aba("dashboard")

    def mudar_aba(self, nome_aba):
        """Alterna entre as telas principais do sistema."""
        frame = self.frames[nome_aba]
        frame.tkraise()
        if nome_aba == "dashboard":
            self.atualizar_dashboard()
        elif nome_aba == "produtos":
            self.atualizar_tabela_produtos()
        elif nome_aba == "entradas":
            self.carregar_combo_produtos()
            self.atualizar_tabela_movimentacoes()

    # ==========================================
    # 1. TELA DE DASHBOARD / ALERTAS
    # ==========================================
    def criar_tela_dashboard(self):
        frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        titulo = ctk.CTkLabel(frame, text="Painel de Alertas (Validade e Estoque)", font=ctk.CTkFont(size=22, weight="bold"))
        titulo.grid(row=0, column=0, sticky="w", pady=(0, 10))

        # Caixa de Alertas Próximos do Vencimento
        self.textbox_alertas = ctk.CTkTextbox(frame, width=600, height=350, corner_radius=10)
        self.textbox_alertas.grid(row=1, column=0, sticky="nsew")
        self.textbox_alertas.configure(state="disabled")

        self.frames["dashboard"] = frame

    def atualizar_dashboard(self):
        self.textbox_alertas.configure(state="normal")
        self.textbox_alertas.delete("0.0", "end")
        
        self.textbox_alertas.insert("end", "=== ⚠️ PRODUTOS PRÓXIMOS DA VALIDADE OU VENCIDOS ===\n\n")
        
        try:
            conn = connect_db()
            cursor = conn.cursor()
            
            # Consulta produtos e validades cadastradas
            cursor.execute("""
                SELECT p.nome, m.lote, m.quantidade, m.data_validade 
                FROM movimentacoes m
                JOIN produtos p ON m.produto_id = p.id
                WHERE m.tipo = 'ENTRADA'
                ORDER BY m.data_validade ASC
            """)
            dados = cursor.fetchall()
            conn.close()

            if not dados:
                self.textbox_alertas.insert("end", "Nenhum produto com lote/validade cadastrado no momento.")
            else:
                hoje = datetime.now().date()
                for nome, lote, qtd, validade_str in dados:
                    if validade_str:
                        val_date = datetime.strptime(validade_str, "%Y-%m-%d").date()
                        dias_restantes = (val_date - hoje).days
                        
                        status = ""
                        if dias_restantes < 0:
                            status = "🔴 VENCIDO!"
                        elif dias_restantes <= 3:
                            status = "⚠️ VENCE EM BREVE (Poucos dias)!"
                        else:
                            status = "🟢 OK"
                            
                        linha = f"• Produto: {nome} | Lote: {lote} | Qtd: {qtd} | Validade: {validade_str} ({status})\n"
                        self.textbox_alertas.insert("end", linha)
        except Exception as e:
            self.textbox_alertas.insert("end", f"Erro ao carregar dados do dashboard: {e}")

        self.textbox_alertas.configure(state="disabled")

    # ==========================================
    # 2. TELA DE CADASTRO DE PRODUTOS
    # ==========================================
    def criar_tela_produtos(self):
        frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(2, weight=1)

        titulo = ctk.CTkLabel(frame, text="Cadastro de Produtos do Restaurante", font=ctk.CTkFont(size=22, weight="bold"))
        titulo.grid(row=0, column=0, sticky="w", pady=(0, 10))

        # Formulário de Cadastro
        form_frame = ctk.CTkFrame(frame)
        form_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        form_frame.grid_columnconfigure(3, weight=1)

        self.entry_prod_nome = ctk.CTkEntry(form_frame, placeholder_text="Nome do Produto (Ex: Alcatra)")
        self.entry_prod_nome.grid(row=0, column=0, padx=10, pady=10)

        self.entry_prod_cat = ctk.CTkEntry(form_frame, placeholder_text="Categoria (Ex: Carnes)")
        self.entry_prod_cat.grid(row=0, column=1, padx=10, pady=10)

        self.entry_prod_un = ctk.CTkEntry(form_frame, placeholder_text="Un. (kg, L, un)")
        self.entry_prod_un.grid(row=0, column=2, padx=10, pady=10)

        btn_salvar_prod = ctk.CTkButton(form_frame, text="Cadastrar Produto", command=self.salvar_produto)
        btn_salvar_prod.grid(row=0, column=3, padx=10, pady=10, sticky="e")

        # Lista de Produtos (Treeview do Tkinter adaptada)
        table_frame = ctk.CTkFrame(frame)
        table_frame.grid(row=2, column=0, sticky="nsew")
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        self.tree_produtos = ttk.Treeview(table_frame, columns=("ID", "Nome", "Categoria", "Unidade"), show="headings")
        self.tree_produtos.heading("ID", text="ID")
        self.tree_produtos.heading("Nome", text="Nome do Produto")
        self.tree_produtos.heading("Categoria", text="Categoria")
        self.tree_produtos.heading("Unidade", text="Unidade")
        self.tree_produtos.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.frames["produtos"] = frame

    def salvar_produto(self):
        nome = self.entry_prod_nome.get().strip()
        cat = self.entry_prod_cat.get().strip()
        un = self.entry_prod_un.get().strip()

        if not nome:
            messagebox.showwarning("Aviso", "O nome do produto é obrigatório!")
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO produtos (nome, categoria, unidade) VALUES (?, ?, ?)", (nome, cat, un))
            conn.commit()
            conn.close()

            messagebox.showinfo("Sucesso", "Produto cadastrado com sucesso!")
            self.entry_prod_nome.delete(0, "end")
            self.entry_prod_cat.delete(0, "end")
            self.entry_prod_un.delete(0, "end")
            self.atualizar_tabela_produtos()
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível salvar o produto: {e}")

    def atualizar_tabela_produtos(self):
        for row in self.tree_produtos.get_children():
            self.tree_produtos.delete(row)

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT id, nome, categoria, unidade FROM produtos")
            for row in cursor.fetchall():
                self.tree_produtos.insert("", "end", values=row)
            conn.close()
        except Exception as e:
            print(f"Erro ao atualizar tabela de produtos: {e}")

    # ==========================================
    # 3. TELA DE ENTRADA (LOTE E VALIDADE)
    # ==========================================
    def criar_tela_entradas(self):
        frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(2, weight=1)

        titulo = ctk.CTkLabel(frame, text="Entrada de Mercadorias (Lote & Validade)", font=ctk.CTkFont(size=22, weight="bold"))
        titulo.grid(row=0, column=0, sticky="w", pady=(0, 10))

        # Formulário de Entrada
        form_frame = ctk.CTkFrame(frame)
        form_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))

        self.combo_produtos = ctk.CTkComboBox(form_frame, values=["Selecione o produto"])
        self.combo_produtos.grid(row=0, column=0, padx=10, pady=10)

        self.entry_qtd = ctk.CTkEntry(form_frame, placeholder_text="Quantidade")
        self.entry_qtd.grid(row=0, column=1, padx=10, pady=10)

        self.entry_lote = ctk.CTkEntry(form_frame, placeholder_text="Número do Lote")
        self.entry_lote.grid(row=0, column=2, padx=10, pady=10)

        self.entry_validade = ctk.CTkEntry(form_frame, placeholder_text="Validade (AAAA-MM-DD)")
        self.entry_validade.grid(row=0, column=3, padx=10, pady=10)

        btn_lancar = ctk.CTkButton(form_frame, text="Registrar Entrada", command=self.salvar_entrada)
        btn_lancar.grid(row=0, column=4, padx=10, pady=10)

        # Histórico de Entradas
        table_frame = ctk.CTkFrame(frame)
        table_frame.grid(row=2, column=0, sticky="nsew")
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        self.tree_entradas = ttk.Treeview(table_frame, columns=("ID", "Produto", "Qtd", "Lote", "Validade"), show="headings")
        self.tree_entradas.heading("ID", text="ID")
        self.tree_entradas.heading("Produto", text="Produto")
        self.tree_entradas.heading("Qtd", text="Quantidade")
        self.tree_entradas.heading("Lote", text="Lote")
        self.tree_entradas.heading("Validade", text="Data de Validade")
        self.tree_entradas.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.frames["entradas"] = frame

    def carregar_combo_produtos(self):
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT id, nome FROM produtos")
            produtos = cursor.fetchall()
            conn.close()

            self.produtos_dict = {nome: p_id for p_id, nome in produtos}
            if self.produtos_dict:
                self.combo_produtos.configure(values=list(self.produtos_dict.keys()))
                self.combo_produtos.set(list(self.produtos_dict.keys())[0])
            else:
                self.combo_produtos.configure(values=["Cadastre um produto primeiro"])
                self.combo_produtos.set("Cadastre um produto primeiro")
        except Exception as e:
            print(f"Erro ao carregar combobox: {e}")

    def salvar_entrada(self):
        prod_nome = self.combo_produtos.get()
        qtd_str = self.entry_qtd.get().strip()
        lote = self.entry_lote.get().strip()
        validade = self.entry_validade.get().strip()

        if not prod_nome or prod_nome not in self.produtos_dict:
            messagebox.showwarning("Aviso", "Selecione um produto válido.")
            return

        if not qtd_str or not lote or not validade:
            messagebox.showwarning("Aviso", "Preencha a quantidade, o lote e a validade.")
            return

        try:
            qtd = float(qtd_str)
            produto_id = self.produtos_dict[prod_nome]

            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO movimentacoes (produto_id, tipo, quantidade, lote, data_validade)
                VALUES (?, 'ENTRADA', ?, ?, ?)
            """, (produto_id, qtd, lote, validade))
            conn.commit()
            conn.close()

            messagebox.showinfo("Sucesso", "Entrada de mercadoria registrada com sucesso!")
            self.entry_qtd.delete(0, "end")
            self.entry_lote.delete(0, "end")
            self.entry_validade.delete(0, "end")
            self.atualizar_tabela_movimentacoes()
        except ValueError:
            messagebox.showerror("Erro", "A quantidade deve ser um número válido.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao registrar entrada: {e}")

    def atualizar_tabela_movimentacoes(self):
        for row in self.tree_entradas.get_children():
            self.tree_entradas.delete(row)

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT m.id, p.nome, m.quantidade, m.lote, m.data_validade
                FROM movimentacoes m
                JOIN produtos p ON m.produto_id = p.id
                WHERE m.tipo = 'ENTRADA'
            """)
            for row in cursor.fetchall():
                self.tree_entradas.insert("", "end", values=row)
            conn.close()
        except Exception as e:
            print(f"Erro ao atualizar tabela de entradas: {e}")


# Para testar o painel principal isoladamente se precisar:
if __name__ == "__main__":
    app = MainApp("admin")
    app.mainloop()
