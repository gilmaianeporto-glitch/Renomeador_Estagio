# 📸 Renomeador e Organizador de Relatórios Fotográficos

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![Tkinter](https://img.shields.io/badge/Interface-Tkinter-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Funcional-brightgreen?style=for-the-badge)

## 📝 Descrição

Esta aplicação desktop foi desenvolvida para automatizar e padronizar o processo de organização de fotos de manutenção em campo (Torres, Painéis Solares, Estações Meteorológicas). 

O sistema permite que o usuário arraste e solte imagens em categorias específicas, renomeie automaticamente os arquivos seguindo um padrão rigoroso (`TORRE_DATA_TIPO`) e gere pacotes prontos para envio (Pastas ou ZIP), além de auxiliar na redação do relatório textual.

## 🚀 Funcionalidades

* **Interface Drag & Drop:** Arraste fotos diretamente das pastas para os cards correspondentes (ex: Antena, Piranômetro, Pluviômetro).
* **Padronização Automática:** Renomeia os arquivos com base no nome da Torre e Data (ex: `TORRE_20231025_GERAL_RL_Antena.jpg`).
* **Visualização Prévia:** Exibe thumbnails das imagens selecionadas e permite visualização em tamanho ampliado.
* **Gestão de Extras:** Permite adicionar fotos extras que não se encaixam nas categorias principais.
* **Exportação Flexível:** Gera uma pasta organizada ou um arquivo `.zip` pronto para upload.
* **Gerador de Texto Automático:** Cria um resumo textual para ordens de serviço baseado em um formulário interativo (checagem de duplicatas, horário, interferências, etc.).

## 🛠️ Tecnologias Utilizadas

* **Python 3**
* **Tkinter:** Para a interface gráfica nativa.
* **TkinterDnD2:** Para funcionalidade de arrastar e soltar arquivos.
* **Pillow (PIL):** Para manipulação e visualização de imagens.
* **OS / Shutil / Zipfile:** Para manipulação de arquivos e sistema.

## 📦 Pré-requisitos e Instalação

Para rodar este projeto localmente, você precisará do Python instalado e das seguintes bibliotecas:

1. **Clone o repositório ou baixe o código:**
   ```bash
   git clone <seu-link-do-repositorio>
   cd nome-do-projeto
