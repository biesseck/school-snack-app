# 🍎 School Snack Pass (MVP)

Aplicação web para controle e gestão da entrega de lanches escolares por meio do escaneamento de leitores de QR Code (ou digitação de ID). O sistema utiliza o **Google Sheets** como banco de dados compartilhado, permitindo que a equipe escolar acompanhe os registros de entrega em tempo real sem a necessidade de infraestruturas complexas de banco de dados.

## 📋 Pré-requisitos

Antes de iniciar, certifique-se de ter instalado em sua máquina:

* **Git** ([Download](https://git-scm.com/))

* **Miniconda** ou **Anaconda** ([Download](https://docs.conda.io/en/latest/miniconda.html))

* **Node.js** (versão 20 ou superior recomendada, para o servidor do frontend)

* Uma conta ativa no **Google** (para acessar o Google Sheets e o Google Cloud Console)

## 🛠️ Passo a Passo de Configuração

### 1. Clonar o Repositório

Abra o terminal ou prompt de comando e execute:

```
git clone https://github.com/biesseck/school-snack-app.git
cd school-snack-app

```

### 2. Configurar a Planilha no Google Sheets

1. Acesse o [Google Sheets](https://sheets.google.com) e crie uma nova planilha com o nome exato: **`School Snack MVP`**.

2. Renomeie a primeira aba (`Sheet1` ou `Página1`) para **`Students`** e adicione o seguinte cabeçalho na Linha 1:

   * `A1`: `Student_ID` | `B1`: `Full_Name` | `C1`: `Grade` | `D1`: `Status`
     *(Adicione alguns alunos para teste, ex: `STU-001`, `Maria Silva`, `6º Ano A`, `Active`)*.

3. Crie uma segunda aba e dê o nome de **`Deliveries`** com o seguinte cabeçalho na Linha 1:

   * `A1`: `Delivery_ID` | `B1`: `Date` | `C1`: `Timestamp` | `D1`: `Student_ID` | `E1`: `Staff_User`

### 3. Configurar a API do Google Cloud e Credenciais

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/).

2. Crie um novo projeto (ex: `school-snack-app`).

3. **Ativar APIs Necessárias:**

   * No menu lateral, acesse **APIs e Serviços** > **Biblioteca**.

   * Pesquise por **Google Sheets API** e clique em **Ativar**.

   * Volte à biblioteca, pesquise por **Google Drive API** e clique em **Ativar**.

4. **Criar Conta de Serviço (Service Account):**

   * Acesse **IAM e Administração** > **Contas de serviço**.

   * Clique em **+ Criar Conta de Serviço**, informe um nome (ex: `snack-api-service`) e clique em **Criar e Continuar** > **Concluído**.

   * Clique no e-mail da conta de serviço criada e navegue até a aba **Chaves**.

   * Clique em **Adicionar Chave** > **Criar nova chave** e selecione o formato **JSON**. O arquivo será baixado para o seu computador.

5. **Adicionar o Arquivo no Projeto:**

   * Mova o arquivo `.json` baixado para a pasta `backend/` do projeto e renomeie-o para **`credentials.json`**.

6. **Compartilhar a Planilha com a Conta de Serviço:**

   * Abra o arquivo `credentials.json` e copie o endereço de e-mail do campo `"client_email"` (ex: `snack-api-service@...iam.gserviceaccount.com`).

   * Abra a sua planilha **School Snack MVP** criada no Google Sheets, clique no botão **Compartilhar** no canto superior direito e cole o e-mail da Conta de Serviço, concedendo permissão de **Editor**.

### 4. Configurar e Executar o Backend (FastAPI)

1. Abra o terminal e navegue até a pasta `backend/`:

   ```
   cd backend
   
   ```

2. Crie e ative o ambiente Conda do backend:

   ```
   conda create -n school-snack-api python=3.11 -y
   conda activate school-snack-api
   
   ```

3. Instale as dependências exigidas:

   ```
   pip install fastapi uvicorn[standard] gspread google-auth reportlab qrcode[pil] python-multipart
   
   ```

4. Inicie o servidor FastAPI:

   ```
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   
   ```

5. **Verificação:** Abra o navegador em `http://localhost:8000/docs` para visualizar a documentação interativa Swagger da API.

### 5. Configurar e Executar o Frontend (Aplicação Web)

1. Abra uma **nova janela/aba de terminal** e navegue até a pasta `frontend/`:

   ```
   cd school-snack-app/frontend
   
   ```

2. Crie e ative o ambiente Conda do frontend:

   ```
   conda create -n school-snack-ui -c conda-forge nodejs=20 -y
   conda activate school-snack-ui
   
   ```

3. Inicie um servidor estático simples para servir os arquivos HTML/JS:

   ```
   npx serve -l 3000
   
   ```

4. Acesse a aplicação no navegador do seu computador:

   ```
   http://localhost:3000
   
   ```

## 📱 Testando em Dispositivos Móveis na Mesma Rede Wi-Fi

Para testar o escaneamento por câmera em um smartphone conectado à mesma rede Wi-Fi do seu laptop:

1. Descubra o IP local da sua máquina (ex: `192.168.1.50`).

2. No celular, acesse `http://192.168.1.50:3000`.

3. **Liberar uso da câmera no Google Chrome (Android):**

   * No Chrome do celular, acesse `chrome://flags`.

   * Busque por `unsafely-treat-insecure-origin-as-secure`.

   * Ative o parâmetro (**Enabled**) e insira o endereço completo do seu frontend: `http://192.168.1.50:3000`.

   * Clique em **Relaunch** no canto inferior da tela. Ao reabrir o site, a permissão de câmera estará disponível.

## 🔒 Segurança de Credenciais

O arquivo `backend/credentials.json` contém chaves privadas de acesso ao seu projeto Google Cloud. Este arquivo **nunca deve ser enviado ao GitHub**. Certifique-se de que ele esteja listado no seu arquivo `.gitignore`.