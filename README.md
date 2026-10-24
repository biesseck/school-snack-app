# 🍎 School Snack Pass (MVP)

Aplicação web para controle e gestão da entrega de lanches escolares por meio do escaneamento de leitores de QR Code ou digitação manual de ID. O sistema utiliza **SQLite** como banco de dados local integrado, permitindo que a aplicação rode de forma ágil, segura e totalmente independente de serviços em nuvem para testes e desenvolvimento.

---

## 📋 Pré-requisitos

Antes de iniciar, certifique-se de ter instalado em sua máquina:

* **Git** ([Download](https://git-scm.com/))
* **Miniconda** ou **Anaconda** ([Download](https://docs.conda.io/en/latest/miniconda.html))
* **Node.js** (versão 20 ou superior recomendada, para o servidor do frontend)

---

## 🛠️ Passo a Passo de Configuração

### 1. Clonar o Repositório

Abra o terminal ou prompt de comando e execute:

```bash
git clone https://github.com/SEU-USUARIO/school-snack-app.git
cd school-snack-app
```

---

### 2. Configurar e Executar o Backend (FastAPI + SQLite)

O backend utiliza o **SQLite** como banco de dados principal. Não é necessário instalar nenhum banco de dados externo ou configurar chaves do Google Cloud. Na primeira execução, o arquivo `database.db` será gerado automaticamente na pasta `backend/` com alunos de teste pré-cadastrados.

1. Abra o terminal e navegue até a pasta `backend/`:
   ```bash
   cd backend
   ```

2. Crie e ative o ambiente Conda do backend:
   ```bash
   conda create -n school-snack-api python=3.11 -y
   conda activate school-snack-api
   ```

3. Instale as dependências exigidas:
   ```bash
   pip install fastapi uvicorn[standard] reportlab qrcode[pil] python-multipart
   ```

4. Inicie o servidor FastAPI (ouvindo em `0.0.0.0` para permitir acesso na rede Wi-Fi local):
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

5. **Verificação:** Abra o navegador em `http://localhost:8000/docs` para visualizar a documentação interativa Swagger da API e testar os endpoints.

---

### 3. Configurar e Executar o Frontend (Aplicação Web)

1. Abra uma **nova janela/aba de terminal** e navegue até a pasta `frontend/`:
   ```bash
   cd school-snack-app/frontend
   ```

2. Crie e ative o ambiente Conda do frontend:
   ```bash
   conda create -n school-snack-ui -c conda-forge nodejs=20 -y
   conda activate school-snack-ui
   ```

3. Inicie um servidor estático para servir a aplicação web:
   ```bash
   npx serve -l 3000
   ```

4. Acesse a aplicação no navegador do seu computador:
   ```text
   http://localhost:3000
   ```

---

## 📱 Testando em Dispositivos Móveis na Mesma Rede Wi-Fi

Para testar o escaneamento de QR Code pela câmera de um smartphone conectado à mesma rede Wi-Fi do seu computador:

1. Descubra o IP local da sua máquina (ex: `192.168.1.50`).
2. No celular, acesse `http://192.168.1.50:3000`.
3. **Liberar uso da câmera no Google Chrome (Android):**
   * No Chrome do celular, acesse `chrome://flags`.
   * Busque por `unsafely-treat-insecure-origin-as-secure`.
   * Ative o parâmetro (**Enabled**) e insira o endereço completo do frontend: `http://192.168.1.50:3000`.
   * Clique no botão **Relaunch** no canto inferior da tela. Ao reabrir o navegador, a permissão da câmera funcionará normalmente.

---

## 🔍 Visualizando os Dados do SQLite

Para abrir e inspecionar a tabela de entregas (`deliveries`) e de alunos (`students`) em formato de planilha:

1. **DB Browser for SQLite (Gratuito / Desktop):** Baixe em [sqlitebrowser.org](https://sqlitebrowser.org/), abra o programa e selecione o arquivo `backend/database.db`.
2. **SQLite Viewer (Web / Sem Instalação):** Acesse [sqliteviewer.app](https://sqliteviewer.app/) e arraste o arquivo `database.db` diretamente na página.
3. **Extensão VS Code:** Instale a extensão **SQLite Viewer** (por *qwtel*) diretamente no VS Code para visualizar as tabelas do banco com um clique.