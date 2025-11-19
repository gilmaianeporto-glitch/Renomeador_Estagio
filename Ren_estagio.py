import os
import shutil
import zipfile
from tkinterdnd2 import TkinterDnD
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk  # Importa ttk
from PIL import Image, ImageTk
from datetime import datetime

# Listagem dos tipos principais de fotos
tipos_fotos = [
    "Antena", "VistaTotalTorre", "GPSInstalado", "PainelSolarLimpo",
    "PainelSolarLimpo_2",
    "Piranometro1(Limpo)", "Piranometro1(AntesLimpeza)",
    "Piranometro2(Limpo)", "Piranometro2(AntesLimpeza)",
    "Piranometro3(Limpo)", "Piranometro3(AntesLimpeza)", "Dessecante_Sunshine",
    "Albedometro_Superior(Limpo)", "Albedometro_Superior(AntesLimpeza)",
    "Albedometro_Inferior(Limpo)", "Albedometro_Inferior(AntesLimpeza)",
    "Piranometro_Sunshine(Limpo)", "Piranometro_Sunshine(AntesLimpeza)",
    "KitSoiling(Limpo)", "KitSoiling(AntesLimpeza)",
    "Pluviometro(Limpo)", "Pluviometro(AntesLimpeza)"
]

# Dicionários globais
fotos = {}
botoes = {}
previews = {}
extras = []
view_buttons = {}

# Cores
COR_FUNDO = "#f1f1f1"
COR_BOTAO_NORMAL = "#3a86ff"
COR_BOTAO_SELECIONADO = "#28a745"
COR_BOTAO_CANCELAR = "#e63946"
COR_BOTAO_LARANJA = "#E76B3C"
COR_LABEL = "#cccccc"
COR_BG_PREVIEW = "#CFCFCF"

# --- Variáveis Globais para a Janela de Texto Automático ---
janela_texto_automatico = None
entry_desenvolvedor = None
faltaram_fotos_var = None
ordem_fotos_var = None
fotos_duplicadas_var = None
etiqueta_horario_var = None
interferencias_var = None
info_adicionais_var = None
text_output = None

# --- Funções de Mensagem Personalizadas ---
def _mostrar_mensagem_silencioso(parent, title, message, message_type="info"):
    top = tk.Toplevel(parent)
    top.title(title)
    top.transient(parent)
    top.grab_set()
    top.resizable(False, False)

    frame_msg = ttk.Frame(top, padding=15, style="TFrame")
    frame_msg.pack(fill="both", expand=True)

    msg_label = ttk.Label(frame_msg, text=message, wraplength=400, justify="center", font=("Work Sans", 10))
    msg_label.pack(padx=20, pady=20)

    # Botão TTK
    ok_button = ttk.Button(frame_msg, text="OK", command=top.destroy, width=10, style="Normal.TButton")
    ok_button.pack(pady=(0, 10))

    top.update_idletasks()
    parent_x = parent.winfo_x()
    parent_y = parent.winfo_y()
    parent_width = parent.winfo_width()
    parent_height = parent.winfo_height()
    top_width = top.winfo_width()
    top_height = top.winfo_height()
    x = parent_x + (parent_width // 2) - (top_width // 2)
    y = parent_y + (parent_height // 2) - (top_height // 2)
    top.geometry(f"+{x}+{y}")
    parent.wait_window(top)

def _mostrar_info_silencioso(parent, title, message):
    _mostrar_mensagem_silencioso(parent, title, message, "info")

def _mostrar_erro_silencioso(parent, title, message):
    _mostrar_mensagem_silencioso(parent, title, message, "error")

def _mostrar_aviso_silencioso(parent, title, message):
    _mostrar_mensagem_silencioso(parent, title, message, "warning")

# --- Função de Visualização de Imagem ---
def visualizar_imagem_popup(tipo):
    if tipo not in fotos or not os.path.isfile(fotos[tipo]):
        _mostrar_aviso_silencioso(janela_principal, "Aviso", "Nenhuma imagem válida selecionada para este item.")
        return

    file_path = fotos[tipo]
    popup = tk.Toplevel(janela_principal)
    popup.title(f"Visualizando: {os.path.basename(file_path)}")
    popup.configure(bg=COR_FUNDO)
    popup.transient(janela_principal)
    popup.grab_set()

    try:
        screen_w = popup.winfo_screenwidth()
        screen_h = popup.winfo_screenheight()
        max_w = int(screen_w * 0.85)
        max_h = int(screen_h * 0.85)

        img = Image.open(file_path)
        img.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)

        lbl_popup_img = ttk.Label(popup, image=img_tk, background=COR_FUNDO)
        lbl_popup_img.image = img_tk
        lbl_popup_img.pack(padx=10, pady=10)

        popup.update_idletasks()
        win_w = popup.winfo_width()
        win_h = popup.winfo_height()
        x = (screen_w // 2) - (win_w // 2)
        y = (screen_h // 2) - (win_h // 2)
        popup.geometry(f'{win_w}x{win_h}+{x}+{y}')
        
        lbl_popup_img.bind("<Button-1>", lambda e: popup.destroy())
        popup.bind("<Escape>", lambda e: popup.destroy())

    except Exception as e:
        popup.destroy()
        _mostrar_erro_silencioso(janela_principal, "Erro de Visualização", f"Não foi possível abrir a imagem.\n\nDetalhes: {e}")

# --- Funções Principais ---
def selecionar_arquivo(tipo):
    caminho = filedialog.askopenfilename(title=f"Selecionar imagem para {tipo}")
    if caminho:
        fotos[tipo] = caminho
        # Atualiza o estilo do botão para TTK
        botoes[tipo].config(text="Selecionado", style="Green.TButton")
        view_buttons[tipo].state(["!disabled"])  # Habilita botão TTK

        img = Image.open(caminho)
        img.thumbnail((230, 230)) 
        img_tk = ImageTk.PhotoImage(img)
        previews[tipo].config(image=img_tk, text="")
        previews[tipo].image = img_tk

def cancelar_selecao(tipo):
    if tipo in fotos:
        del fotos[tipo]
    # Atualiza o estilo do botão para TTK
    botoes[tipo].config(text="Selecionar", style="Normal.TButton")
    previews[tipo].config(image="", text="Arraste a imagem aqui")
    previews[tipo].image = None
    view_buttons[tipo].state(["disabled"])  # Desabilita botão TTK

def selecionar_extras():
    global extras
    arquivos = filedialog.askopenfilenames(title="Selecionar Fotos Extras")
    if arquivos:
        extras.clear()
        extras.extend(arquivos)
        # Atualiza o estilo do botão para TTK
        btn_extras.config(text=f"{len(extras)} arquivos selecionados", style="Green.Large.TButton")

def validar_e_formatar_data(data_input):
    try:
        data_obj = datetime.strptime(data_input, "%d%m%Y")
        return data_obj.strftime("%Y%m%d"), data_obj.strftime("%d/%m/%Y")
    except ValueError:
        return None, None

def gerar_pasta():
    global extras
    torre = entry_torre.get().strip()
    data_input = entry_data.get().strip()

    if not torre or not data_input:
        _mostrar_erro_silencioso(janela_principal, "Erro", "Preencha os campos TORRE e DATA!")
        return

    data_formatada, _ = validar_e_formatar_data(data_input)
    if data_formatada is None:
        _mostrar_erro_silencioso(janela_principal, "Erro", "Formato de data inválido. Use DDMMYYYY (ex: 25062025).")
        return

    pasta_destino = filedialog.askdirectory(title="Selecione onde salvar a pasta")
    if not pasta_destino:
        return

    nome_pasta = f"{torre}_{data_formatada}_RL"
    caminho_pasta = os.path.join(pasta_destino, nome_pasta)

    if not os.path.exists(caminho_pasta):
        os.makedirs(caminho_pasta)

    pasta_extras = os.path.join(caminho_pasta, "EXTRAS")
    os.makedirs(pasta_extras, exist_ok=True)

    for tipo, caminho in fotos.items():
        if os.path.isfile(caminho):
            extensao = os.path.splitext(caminho)[1]
            nome_arquivo = f"{torre}_{data_formatada}_GERAL_RL_{tipo}{extensao}"
            destino = os.path.join(caminho_pasta, nome_arquivo)
            shutil.copy2(caminho, destino)

    for i, caminho_extra in enumerate(extras, 1):
        if os.path.isfile(caminho_extra):
            nome_original = os.path.basename(caminho_extra)
            extensao = os.path.splitext(nome_original)[1]
            nome_arquivo = f"{i}_{torre}_{data_formatada}_EXTRA_RL_{nome_original.replace(extensao, '')}{extensao}"
            destino = os.path.join(pasta_extras, nome_arquivo)
            shutil.copy2(caminho_extra, destino)

    _mostrar_info_silencioso(janela_principal, "Sucesso", f"Pasta gerada com sucesso em:\n{caminho_pasta}")
    print(f"Pasta salva em: {os.path.abspath(caminho_pasta)}")


def gerar_zip():
    global extras
    torre = entry_torre.get().strip()
    data_input = entry_data.get().strip()

    if not torre or not data_input:
        _mostrar_erro_silencioso(janela_principal, "Erro", "Preencha os campos TORRE e DATA!")
        return

    data_formatada, _ = validar_e_formatar_data(data_input)
    if data_formatada is None:
        _mostrar_erro_silencioso(janela_principal, "Erro", "Formato de data inválido. Use DDMMYYYY (ex: 25062025).")
        return

    zip_nome = filedialog.asksaveasfilename(
        defaultextension=".zip",
        filetypes=[("Arquivo ZIP", "*.zip")],
        initialfile=f"{torre}_{data_formatada}_RL.zip",
        title="Salvar Arquivo ZIP"
    )
    if not zip_nome:
        return

    pasta_temp = "fotos_temp"
    pasta_extras = os.path.join(pasta_temp, "EXTRAS")
    os.makedirs(pasta_temp, exist_ok=True)
    os.makedirs(pasta_extras, exist_ok=True)

    arquivos_copiados = 0

    for tipo, caminho in fotos.items():
        if os.path.isfile(caminho):
            extensao = os.path.splitext(caminho)[1]
            nome_arquivo = f"{torre}_{data_formatada}_GERAL_RL_{tipo}{extensao}"
            destino = os.path.join(pasta_temp, nome_arquivo)
            shutil.copy2(caminho, destino)
            arquivos_copiados += 1

    for i, caminho_extra in enumerate(extras, 1):
        if os.path.isfile(caminho_extra):
            nome_original = os.path.basename(caminho_extra)
            extensao = os.path.splitext(nome_original)[1]
            nome_arquivo = f"{i}_{torre}_{data_formatada}_EXTRA_RL_{nome_original.replace(extensao, '')}{extensao}"
            destino = os.path.join(pasta_extras, nome_arquivo)
            shutil.copy2(caminho_extra, destino)
            arquivos_copiados += 1

    if arquivos_copiados == 0:
        shutil.rmtree(pasta_temp)
        _mostrar_erro_silencioso(janela_principal, "Erro", "Nenhuma foto válida para gerar o ZIP!")
        return

    with zipfile.ZipFile(zip_nome, 'w') as zipf:
        for root_dir, dirs, files in os.walk(pasta_temp):
            for file in files:
                file_path = os.path.join(root_dir, file)
                arcname = os.path.relpath(file_path, pasta_temp)
                zipf.write(file_path, arcname=arcname)

    shutil.rmtree(pasta_temp)
    _mostrar_info_silencioso(janela_principal, "Sucesso", f"Arquivo ZIP gerado com sucesso em:\n{zip_nome}")
    print(f"ZIP salvo em: {os.path.abspath(zip_nome)}")

def apagar_tudo():
    fotos.clear()
    for tipo in tipos_fotos:
        # Atualiza o estilo do botão para TTK
        botoes[tipo].config(text="Selecionar", style="Normal.TButton")
        previews[tipo].config(image="", text="Arraste a imagem aqui")
        previews[tipo].image = None
        view_buttons[tipo].state(["disabled"]) # Desabilita botão TTK

    extras.clear()
    # Atualiza o estilo do botão para TTK
    btn_extras.config(text="Selecionar Extras", style="Normal.Large.TButton")

    entry_torre.delete(0, tk.END)
    entry_data.delete(0, tk.END)
    
    if entry_desenvolvedor:
        entry_desenvolvedor.delete(0, tk.END) 
    if faltaram_fotos_var:
        faltaram_fotos_var.set("Não")
    if ordem_fotos_var:
        ordem_fotos_var.set("Não")
    if fotos_duplicadas_var:
        fotos_duplicadas_var.set("Não")
    if etiqueta_horario_var:
        etiqueta_horario_var.set("Não")
    if interferencias_var:
        interferencias_var.set("Não")
    if info_adicionais_var:
        info_adicionais_var.set("Não")
    if text_output:
        text_output.config(state=tk.NORMAL)
        text_output.delete(1.0, tk.END)
        text_output.config(state=tk.DISABLED)

def centralizar_janela(janela_tk):
    janela_tk.update_idletasks()
    largura_janela = janela_tk.winfo_width()
    altura_janela = janela_tk.winfo_height()
    largura_tela = janela_tk.winfo_screenwidth()
    altura_tela = janela_tk.winfo_screenheight()
    pos_x = int((largura_tela / 2) - (largura_janela / 2))
    pos_y = int((altura_tela / 2) - (altura_janela / 2))
    janela_tk.geometry(f'{largura_janela}x{altura_janela}+{pos_x}+{pos_y}')

canvas_window_id = None 

def on_canvas_configure(event):
    global canvas_window_id
    canvas_width = event.width
    scroll_frame.update_idletasks()
    scroll_frame_width = scroll_frame.winfo_reqwidth()
    
    current_y = 0
    if canvas_window_id:
        coords = canvas.coords(canvas_window_id)
        if len(coords) >= 2:
            current_y = coords[1]
    
    if canvas_width > scroll_frame_width:
        x_offset = (canvas_width - scroll_frame_width) / 2
        if canvas_window_id:
            canvas.coords(canvas_window_id, x_offset, current_y)
    else:
        if canvas_window_id:
            canvas.coords(canvas_window_id, 0, current_y)
        
    canvas.configure(scrollregion=canvas.bbox("all"))

# --- Funções para Geração de Texto Automático ---
def gerar_texto_automatico():
    torre = entry_torre.get().strip()
    data_input_os = entry_data.get().strip()
    
    if entry_desenvolvedor is None or faltaram_fotos_var is None:
        _mostrar_erro_silencioso(janela_principal, "Erro", "A janela do Gerador de Texto Automático não está aberta ou foi fechada.")
        return

    desenvolvedor = entry_desenvolvedor.get().strip() 
    faltaram_fotos = faltaram_fotos_var.get()
    fotos_duplicadas = fotos_duplicadas_var.get()
    etiqueta_horario = etiqueta_horario_var.get()
    interferencias = interferencias_var.get()
    info_adicionais = info_adicionais_var.get()
    
    if not torre:
        _mostrar_erro_silencioso(janela_principal, "Erro", "O campo 'Torre/Equipamento' na tela principal é obrigatório para gerar o texto!")
        return
    if not desenvolvedor:
        _mostrar_erro_silencioso(janela_principal, "Erro", "O campo 'Desenvolvedor' é obrigatório para gerar o texto!")
        return
    if not data_input_os:
        _mostrar_erro_silencioso(janela_principal, "Erro", "O campo 'Data (DDMMYYYY)' na tela principal é obrigatório para gerar o texto!")
        return

    data_os_ymd, data_os_br = validar_e_formatar_data(data_input_os)
    if data_os_ymd is None:
        _mostrar_erro_silencioso(janela_principal, "Erro", "Formato da 'Data' (tela principal) inválido. Use DDMMYYYY (ex: 25062025).")
        return
    if not all([faltaram_fotos, fotos_duplicadas, etiqueta_horario, interferencias, info_adicionais]):
         _mostrar_erro_silencioso(janela_principal, "Erro", "Responda a todas as perguntas Sim/Não do gerador de texto!")
         return

    texto_gerado = ""
    if torre != "":
        duplicadas_str = "" if fotos_duplicadas == "Sim" else "não" 
        faltante_str = "" if faltaram_fotos == "Sim" else "não" 
        etiqueta_horario_str = "" if etiqueta_horario == "Sim" else "não" 
        interferencias_str = "não" if interferencias == "Não" else "" 
        info_adicionais_str = "" if info_adicionais == "Sim" else "não" 
        
        texto_gerado = (
            f"A limpeza da torre foi realizada pelo colaborador {desenvolvedor}, em {data_os_br}. "
            f"Durante a verificação dos registros fotográficos da limpeza {duplicadas_str} foram encontradas fotos duplicadas e "
            f"{faltante_str} tem foto faltante. "
            f"As fotos enviadas {etiqueta_horario_str} possuem a etiqueta de horário. "
            f"De acordo com os registros fotográficos {interferencias_str} é possível afirmar que o colaborador causou interferências na antena ou nos demais instrumentos. "
            f"As condições de aceiro, acesso e vegetação {info_adicionais_str} foram relatadas pelo colaborador."
        )
    
    text_output.config(state=tk.NORMAL)
    text_output.delete(1.0, tk.END)
    text_output.insert(tk.END, texto_gerado.strip())
    text_output.config(state=tk.DISABLED)
    
    _mostrar_info_silencioso(janela_texto_automatico, "Texto Gerado", "Texto gerado com sucesso! Agora você pode copiá-lo.")


def copiar_texto_automatico():
    global janela_texto_automatico
    if text_output is not None and text_output.get(1.0, tk.END).strip():
        janela_principal.clipboard_clear()
        janela_principal.clipboard_append(text_output.get(1.0, tk.END).strip())
        _mostrar_info_silencioso(janela_principal, "Sucesso", "Texto copiado para a área de transferência!")
        
        if janela_texto_automatico and janela_texto_automatico.winfo_exists():
            janela_texto_automatico.destroy()
            janela_texto_automatico = None
    else:
        _mostrar_aviso_silencioso(janela_principal, "Aviso", "Nenhum texto para copiar.")

def abrir_janela_texto_automatico():
    global janela_texto_automatico, entry_desenvolvedor, faltaram_fotos_var, ordem_fotos_var, fotos_duplicadas_var, etiqueta_horario_var, interferencias_var, info_adicionais_var, text_output

    if janela_texto_automatico and janela_texto_automatico.winfo_exists():
        janela_texto_automatico.lift()
        return

    janela_texto_automatico = tk.Toplevel(janela_principal)
    janela_texto_automatico.title("Gerador de Texto Automático")
    janela_texto_automatico.geometry("900x650")
    janela_texto_automatico.configure(bg=COR_FUNDO)

    janela_texto_automatico.update_idletasks()
    largura_janela_texto = janela_texto_automatico.winfo_width()
    altura_janela_texto = janela_texto_automatico.winfo_height()
    largura_tela = janela_texto_automatico.winfo_screenwidth()
    altura_tela = janela_texto_automatico.winfo_screenheight()
    pos_x = int((largura_tela / 2) - (largura_janela_texto / 2))
    pos_y = int((altura_tela / 2) - (altura_janela_texto / 2))
    janela_texto_automatico.geometry(f'{largura_janela_texto}x{altura_janela_texto}+{pos_x}+{pos_y}')

    frame_conteudo_texto = ttk.Frame(janela_texto_automatico, padding=10, style="TFrame")
    frame_conteudo_texto.pack(fill="both", expand=True, padx=20, pady=20)
    frame_conteudo_texto.grid_columnconfigure(0, weight=1)
    frame_conteudo_texto.grid_columnconfigure(6, weight=1)

    ttk.Label(frame_conteudo_texto, text="Desenvolvedor:", style="Header.TLabel").grid(row=0, column=1, padx=5, pady=5, sticky="e")
    # Entry TTK
    entry_desenvolvedor = ttk.Entry(frame_conteudo_texto, width=25, font=("Work Sans", 10), style="TEntry")
    entry_desenvolvedor.grid(row=0, column=2, padx=5, pady=5, sticky="w", columnspan=3)

    frame_perguntas = ttk.Frame(frame_conteudo_texto, style="TFrame")
    frame_perguntas.grid(row=1, column=0, columnspan=7, sticky="ew", pady=5)
    frame_perguntas.grid_columnconfigure(0, weight=1)
    frame_perguntas.grid_columnconfigure(3, weight=1)
    frame_perguntas.grid_columnconfigure(5, weight=1)

    # Radiobuttons TTK
    faltaram_fotos_var = tk.StringVar(janela_principal, value="Não")
    ordem_fotos_var = tk.StringVar(janela_principal, value="Não")
    fotos_duplicadas_var = tk.StringVar(janela_principal, value="Não")
    etiqueta_horario_var = tk.StringVar(janela_principal, value="Não")
    interferencias_var = tk.StringVar(janela_principal, value="Não")
    info_adicionais_var = tk.StringVar(janela_principal, value="Não")

    ttk.Label(frame_perguntas, text="Faltaram Fotos?:", style="Header.TLabel").grid(row=0, column=1, padx=5, pady=2, sticky="w")
    ttk.Radiobutton(frame_perguntas, text="Sim", variable=faltaram_fotos_var, value="Sim", style="TRadiobutton").grid(row=0, column=2, padx=(5,0), pady=2, sticky="w")
    ttk.Radiobutton(frame_perguntas, text="Não", variable=faltaram_fotos_var, value="Não", style="TRadiobutton").grid(row=0, column=2, padx=(50,5), pady=2, sticky="w")

    ttk.Label(frame_perguntas, text='As fotos foram enviadas na ordem "Antes" e "Depois"?:', style="Header.TLabel").grid(row=1, column=1, padx=5, pady=2, sticky="w")
    ttk.Radiobutton(frame_perguntas, text="Sim", variable=ordem_fotos_var, value="Sim", style="TRadiobutton").grid(row=1, column=2, padx=(5,0), pady=2, sticky="w")
    ttk.Radiobutton(frame_perguntas, text="Não", variable=ordem_fotos_var, value="Não", style="TRadiobutton").grid(row=1, column=2, padx=(50,5), pady=2, sticky="w")

    ttk.Label(frame_perguntas, text="Existem fotos duplicadas?:", style="Header.TLabel").grid(row=2, column=1, padx=5, pady=2, sticky="w")
    ttk.Radiobutton(frame_perguntas, text="Sim", variable=fotos_duplicadas_var, value="Sim", style="TRadiobutton").grid(row=2, column=2, padx=(5,0), pady=2, sticky="w")
    ttk.Radiobutton(frame_perguntas, text="Não", variable=fotos_duplicadas_var, value="Não", style="TRadiobutton").grid(row=2, column=2, padx=(50,5), pady=2, sticky="w")

    ttk.Label(frame_perguntas, text="As fotos contêm a etiqueta de horário?:", style="Header.TLabel").grid(row=0, column=3, padx=5, pady=2, sticky="w")
    ttk.Radiobutton(frame_perguntas, text="Sim", variable=etiqueta_horario_var, value="Sim", style="TRadiobutton").grid(row=0, column=4, padx=(5,0), pady=2, sticky="w")
    ttk.Radiobutton(frame_perguntas, text="Não", variable=etiqueta_horario_var, value="Não", style="TRadiobutton").grid(row=0, column=4, padx=(50,5), pady=2, sticky="w")

    ttk.Label(frame_perguntas, text="É possível identificar interferências?:", style="Header.TLabel").grid(row=1, column=3, padx=5, pady=2, sticky="w")
    ttk.Radiobutton(frame_perguntas, text="Sim", variable=interferencias_var, value="Sim", style="TRadiobutton").grid(row=1, column=4, padx=(5,0), pady=2, sticky="w")
    ttk.Radiobutton(frame_perguntas, text="Não", variable=interferencias_var, value="Não", style="TRadiobutton").grid(row=1, column=4, padx=(50,5), pady=2, sticky="w")

    ttk.Label(frame_perguntas, text="Relatadas info. de aceiro, acesso e vegetação?:", style="Header.TLabel").grid(row=2, column=3, padx=5, pady=2, sticky="w")
    ttk.Radiobutton(frame_perguntas, text="Sim", variable=info_adicionais_var, value="Sim", style="TRadiobutton").grid(row=2, column=4, padx=(5,0), pady=2, sticky="w")
    ttk.Radiobutton(frame_perguntas, text="Não", variable=info_adicionais_var, value="Não", style="TRadiobutton").grid(row=2, column=4, padx=(50,5), pady=2, sticky="w")

    # Botões TTK
    btn_gerar_texto = ttk.Button(frame_conteudo_texto, text="Gerar Texto Automático", command=gerar_texto_automatico, style="Normal.TButton")
    btn_gerar_texto.grid(row=2, column=1, padx=10, pady=5, sticky="w") 

    btn_copiar_texto = ttk.Button(frame_conteudo_texto, text="Copiar Texto", command=copiar_texto_automatico, style="Normal.TButton")
    btn_copiar_texto.grid(row=2, column=2, padx=10, pady=5, sticky="w") 

    ttk.Label(frame_conteudo_texto, text="Texto Gerado:", style="Header.TLabel").grid(row=3, column=1, columnspan=4, padx=5, pady=5, sticky="w") 

    # tk.Text não tem equivalente TTK, então permanece tk
    text_output = tk.Text(frame_conteudo_texto, height=12, width=80, wrap=tk.WORD, font=("Work Sans", 9), relief="flat", borderwidth=2, highlightbackground="#ccc", highlightthickness=1)
    text_output.grid(row=4, column=1, columnspan=4, padx=5, pady=5, sticky="nsew") 
    text_output.config(state=tk.DISABLED)

    # tk.Scrollbar é comumente usado com ttk
    scrollbar_texto = tk.Scrollbar(frame_conteudo_texto, command=text_output.yview)
    scrollbar_texto.grid(row=4, column=5, sticky="ns") 
    text_output.config(yscrollcommand=scrollbar_texto.set)

    frame_conteudo_texto.grid_columnconfigure(1, weight=1) 
    frame_conteudo_texto.grid_columnconfigure(2, weight=1)
    frame_conteudo_texto.grid_columnconfigure(3, weight=1)
    frame_conteudo_texto.grid_columnconfigure(4, weight=1)
    frame_conteudo_texto.grid_columnconfigure(5, weight=0)
    frame_conteudo_texto.grid_rowconfigure(4, weight=1)

    def on_janela_texto_close():
        global janela_texto_automatico, entry_desenvolvedor, faltaram_fotos_var, ordem_fotos_var, fotos_duplicadas_var, etiqueta_horario_var, interferencias_var, info_adicionais_var, text_output
        if janela_texto_automatico:
            janela_texto_automatico.destroy()
        
        janela_texto_automatico = None
        entry_desenvolvedor = None
        if faltaram_fotos_var: faltaram_fotos_var.set("Não")
        if ordem_fotos_var: ordem_fotos_var.set("Não")
        if fotos_duplicadas_var: fotos_duplicadas_var.set("Não")
        if etiqueta_horario_var: etiqueta_horario_var.set("Não")
        if interferencias_var: interferencias_var.set("Não")
        if info_adicionais_var: info_adicionais_var.set("Não")
        text_output = None
        
    janela_texto_automatico.protocol("WM_DELETE_WINDOW", on_janela_texto_close)

# --- Funções de Scroll (Mousewheel) ---
def _on_mousewheel(event):
    if event.num == 5 or event.delta == -120:
        canvas.yview_scroll(1, "unit")
    elif event.num == 4 or event.delta == 120:
        canvas.yview_scroll(-1, "unit")

def _bind_mousewheel_recursively(widget):
    widget.bind("<MouseWheel>", _on_mousewheel)
    widget.bind("<Button-4>", _on_mousewheel)
    widget.bind("<Button-5>", _on_mousewheel)
    for child in widget.winfo_children():
        _bind_mousewheel_recursively(child)

# --- Interface Principal ---
janela_principal = TkinterDnD.Tk()
janela_principal.title("Renomeador de Fotos")

screen_width = janela_principal.winfo_screenwidth()
screen_height = janela_principal.winfo_screenheight()
window_width = int(screen_width * 0.8)
window_height = int(screen_height * 0.8)
janela_principal.geometry(f"{window_width}x{window_height}")
janela_principal.configure(bg=COR_FUNDO)
janela_principal.resizable(True, True)
centralizar_janela(janela_principal)

# --- Configuração de Estilos TTK (Sugestão 4) ---
style = ttk.Style()
style.theme_use('clam')
style.configure("TFrame", background=COR_FUNDO)
style.configure("Header.TLabel", font=("Work Sans", 11, "bold"), foreground="#000000", background=COR_FUNDO)
style.configure("TLabel", background=COR_FUNDO, font=("Work Sans", 9))
style.configure("TEntry", font=("Work Sans", 10))
style.configure("TRadiobutton", background=COR_FUNDO, font=("Work Sans", 9))

# Estilos de Botão para os Cards
style.configure("TButton", font=("Work Sans", 9, "bold"), padding=5, width=9)
style.configure("Normal.TButton", background=COR_BOTAO_NORMAL, foreground="white")
style.map("Normal.TButton", background=[('active', '#2b6dcc'), ('disabled', COR_BG_PREVIEW)])
style.configure("Green.TButton", background=COR_BOTAO_SELECIONADO, foreground="white")
style.map("Green.TButton", background=[('active', '#1e7e34')])
style.configure("Red.TButton", background=COR_BOTAO_CANCELAR, foreground="white")
style.map("Red.TButton", background=[('active', '#a32a3a')])

# Estilos de Botão para a Sidebar (Maiores)
style.configure("Large.TButton", font=("Work Sans", 11, "bold"), padding=(10, 8))
style.configure("Normal.Large.TButton", font=("Work Sans", 11, "bold"), padding=(10, 8), background=COR_BOTAO_NORMAL, foreground="white")
style.map("Normal.Large.TButton", background=[('active', '#2b6dcc')])
style.configure("Green.Large.TButton", font=("Work Sans", 11, "bold"), padding=(10, 8), background=COR_BOTAO_SELECIONADO, foreground="white")
style.map("Green.Large.TButton", background=[('active', '#1e7e34')])
style.configure("Orange.Large.TButton", font=("Work Sans", 11, "bold"), padding=(10, 8), background=COR_BOTAO_LARANJA, foreground="white")
style.map("Orange.Large.TButton", background=[('active', '#e7ac3e')])
style.configure("Red.Large.TButton", font=("Work Sans", 11, "bold"), padding=(10, 8), background=COR_BOTAO_CANCELAR, foreground="white")
style.map("Red.Large.TButton", background=[('active', '#a32a3a')])

# Estilo para o Label de Preview (Drag-and-Drop)
style.configure("Preview.TLabel", background=COR_BG_PREVIEW, foreground="#000000", font=("Work Sans", 10, "italic"), relief="ridge", anchor="center")

# --- Layout com Sidebar (Sugestão 1) ---

# 1. Sidebar (Frame da Esquerda)
# Largura fixa para a barra lateral
sidebar_frame = ttk.Frame(janela_principal, width=280, style="TFrame")
sidebar_frame.pack(side="left", fill="y", padx=20, pady=10)
# Impede que a barra lateral encolha para caber os widgets
sidebar_frame.pack_propagate(False)

# 2. Conteúdo Principal (Frame da Direita)
main_content_frame = ttk.Frame(janela_principal, style="TFrame")
main_content_frame.pack(side="left", fill="both", expand=True, pady=10, padx=(0, 20))

# --- Widgets do Sidebar ---

# Frame para os campos de entrada (Torre, Data) no topo do sidebar
frame_campos = ttk.Frame(sidebar_frame, padding=10, style="TFrame")
frame_campos.pack(side="top", fill="x", pady=10)

ttk.Label(frame_campos, text="Torre/Equipamento:", style="Header.TLabel").pack(fill="x", padx=5, pady=(5,0))
entry_torre = ttk.Entry(frame_campos, width=20, style="TEntry")
entry_torre.pack(fill="x", padx=5, pady=(0, 10))

ttk.Label(frame_campos, text="Data (DDMMYYYY):", style="Header.TLabel").pack(fill="x", padx=5, pady=5)
entry_data = ttk.Entry(frame_campos, width=20, style="TEntry")
entry_data.pack(fill="x", padx=5, pady=(0, 10))

# Frame para os botões de ação no rodapé do sidebar
frame_botoes = ttk.Frame(sidebar_frame, padding=10, style="TFrame") 
frame_botoes.pack(side="bottom", fill="x", pady=20) 

# Botões de Ação (TTK) empilhados verticalmente
btn_gerar_zip = ttk.Button(frame_botoes, text="Gerar ZIP", command=gerar_zip, style="Normal.Large.TButton")
btn_gerar_zip.pack(fill="x", pady=4)

btn_gerar_pasta = ttk.Button(frame_botoes, text="Gerar pasta (sem zip)", command=gerar_pasta, style="Normal.Large.TButton")
btn_gerar_pasta.pack(fill="x", pady=4)

btn_extras = ttk.Button(frame_botoes, text="Selecionar Extras", command=selecionar_extras, style="Normal.Large.TButton")
btn_extras.pack(fill="x", pady=4)

btn_abrir_texto_auto = ttk.Button(frame_botoes, text="Abrir Gerador de Texto", command=abrir_janela_texto_automatico, style="Normal.Large.TButton")
btn_abrir_texto_auto.pack(fill="x", pady=4)

btn_apagartudo = ttk.Button(frame_botoes, text="Apagar Tudo", command=apagar_tudo, style="Orange.Large.TButton")
btn_apagartudo.pack(fill="x", pady=4)

btn_sair = ttk.Button(frame_botoes, text="Sair", command=janela_principal.quit, style="Red.Large.TButton")
btn_sair.pack(fill="x", pady=4)

# --- Widgets do Conteúdo Principal ---

# Canvas para a área de seleção de imagens (rolável)
# Movido para dentro do main_content_frame
scroll_y = ttk.Scrollbar(main_content_frame, orient="vertical")
scroll_x = ttk.Scrollbar(main_content_frame, orient="horizontal")

canvas = tk.Canvas(main_content_frame, bg=COR_FUNDO, highlightthickness=0, yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

scroll_y.config(command=canvas.yview)
scroll_x.config(command=canvas.xview)

scroll_y.pack(side="right", fill="y")
scroll_x.pack(side="bottom", fill="x")
canvas.pack(side="left", fill="both", expand=True)

scroll_frame = ttk.Frame(canvas, style="TFrame")
canvas_window_id = canvas.create_window((0, 0), window=scroll_frame, anchor="nw") 

canvas.bind("<Configure>", on_canvas_configure)
scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

frame_grade = ttk.Frame(scroll_frame, style="TFrame")
frame_grade.grid(row=0, column=0, sticky="nsew") 

colunas_por_linha = 4
for c in range(colunas_por_linha):
    frame_grade.grid_columnconfigure(c, weight=1)

def criar_drop_callback(tipo_local):
    def drop_callback(event):
        caminho_arquivo = event.data.strip('{}')
        if os.path.isfile(caminho_arquivo):
            fotos[tipo_local] = caminho_arquivo
            botoes[tipo_local].config(text="Selecionado", style="Green.TButton")
            view_buttons[tipo_local].state(["!disabled"]) # Habilita TTK

            img = Image.open(caminho_arquivo)
            img.thumbnail((230, 230)) 
            img_tk = ImageTk.PhotoImage(img)
            previews[tipo_local].config(image=img_tk, text="")
            previews[tipo_local].image = img_tk
    return drop_callback

# Loop para criar os cards de fotos
for i, tipo in enumerate(tipos_fotos):
    linha = i // colunas_por_linha
    coluna = i % colunas_por_linha

    frame_individual = ttk.Frame(frame_grade, borderwidth=1, relief="solid", padding=12, style="TFrame", width=280, height=320)
    frame_individual.grid(row=linha, column=coluna, padx=10, pady=10, sticky="n")
    frame_individual.grid_propagate(False)

    # Label (TTK)
    label_nome = ttk.Label(frame_individual, text=tipo, wraplength=240, justify="center",
                            style="TLabel", font=("Work Sans", 9, "bold"))
    label_nome.pack(pady=(0, 8))

    # Label de Preview (TTK)
    lbl_img = ttk.Label(frame_individual, text="Arraste a imagem aqui", width=30, style="Preview.TLabel")
    lbl_img.pack(expand=True, fill="both", ipadx=10, ipady=50) 
    previews[tipo] = lbl_img

    lbl_img.drop_target_register("DND_Files")
    lbl_img.dnd_bind("<<Drop>>", criar_drop_callback(tipo))

    frame_botoes_inferior = ttk.Frame(frame_individual, style="TFrame")
    frame_botoes_inferior.pack(pady=(5, 0), fill="x")

    # Botões (TTK)
    btn = ttk.Button(frame_botoes_inferior, text="Selecionar", style="Normal.TButton",
                    command=lambda t=tipo: selecionar_arquivo(t))
    btn.pack(side="left", expand=True, fill="x", padx=(0, 2))
    botoes[tipo] = btn

    btn_view = ttk.Button(frame_botoes_inferior, text="Visualizar", style="Normal.TButton",
                         command=lambda t=tipo: visualizar_imagem_popup(t))
    btn_view.pack(side="left", expand=True, fill="x", padx=2)
    btn_view.state(["disabled"]) # Começa desabilitado
    view_buttons[tipo] = btn_view

    btn_cancelar = ttk.Button(frame_botoes_inferior, text="Cancelar", style="Red.TButton",
                                command=lambda t=tipo: cancelar_selecao(t))
    btn_cancelar.pack(side="left", expand=True, fill="x", padx=(2, 0))


# --- Chamada dos Bindings de Scroll ---
_bind_mousewheel_recursively(scroll_frame)
canvas.bind("<MouseWheel>", _on_mousewheel)
canvas.bind("<Button-4>", _on_mousewheel)
canvas.bind("<Button-5>", _on_mousewheel)


janela_principal.mainloop()