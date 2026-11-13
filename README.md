# 🍎 School Snack Pass (MVP)

Aplicação web para controle e gestão da entrega de lanches escolares por meio do escaneamento de leitores de QR Code ou digitação manual de ID. O sistema utiliza arquivos **CSV** (`students.csv` e `deliveries.csv`) como armazenamento local integrado, permitindo que a aplicação rode de forma ágil, simples e totalmente independente de serviços em nuvem, além de facilitar a visualização e edição direta dos dados em planilhas eletrônicas (LibreOffice Calc, Excel ou Google Sheets).

---

## 📋 Pré-requisitos

Antes de iniciar, certifique-se de ter instalado em sua máquina:

* **Git** ([Download](https://git-scm.com/))
* **Miniconda** ou **Anaconda** ([Download](https://docs.conda.io/en/latest/miniconda.html))
* **Node.js** (versão 20 ou superior recomendada, para o servidor do frontend)

---

## 🛠️ Passo a Passo de Configuração

### 1. Configurar o PATH do Conda (Windows)
Caso utilize Windows e o comando `conda` não seja reconhecido no terminal, adicione o seguinte caminho à Variável de Ambiente `PATH`:
`C:\ProgramData\anaconda3\condabin`

---

### 2. Clonar o Repositório

Abra o terminal ou prompt de comando e execute:

```bash
git clone https://github.com/biesseck/school-snack-app.git
cd school-snack-app
```

---

### 3. Configurar e Executar o Backend (FastAPI + CSV)

O backend utiliza arquivos **CSV** locais para armazenar os dados. Não é necessário instalar nenhum banco de dados externo ou configurar chaves do Google Cloud. Na primeira execução, os arquivos `students.csv` (com alunos de teste pré-cadastrados) e `deliveries.csv` serão gerados automaticamente na pasta `backend/`.

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

### 4. Configurar e Executar o Frontend (Aplicação Web)

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

## 📊 Visualizando e Editando os Dados (Arquivos CSV)

Os dados do sistema ficam armazenados diretamente na pasta `backend/` em dois arquivos de texto separados por vírgula e codificados em **UTF-8**:

* **`backend/students.csv`**: Lista de alunos cadastrados (`Student_ID,Full_Name,Grade,Status`). Você pode adicionar ou editar alunos diretamente neste arquivo, salvar e gerar os novos cartões com QR Code pelo botão na interface web.
* **`backend/deliveries.csv`**: Histórico de entregas realizadas (`Delivery_ID,Date,Timestamp,Student_ID,Staff_User`).

### Como abrir em planilhas eletrônicas:
1. **LibreOffice Calc / Microsoft Excel:** Abra o arquivo `.csv` desejado selecionando a codificação **UTF-8** e o separador **Vírgula (`,`)**. *(Nota: no Windows, feche o arquivo `deliveries.csv` no Excel/Calc antes de realizar novas leituras no app para evitar bloqueio de escrita).*
2. **Google Sheets:** Importe o arquivo `.csv` em qualquer planilha do Google Drive para visualizar ou compartilhar os relatórios online com a equipe escolar.