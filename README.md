# Talk to Yoyr Bank: uma aplicação do móduto GPT-4o Realtime do Azure OpenAI

Esse repositório é um exemplo de uso da API Realtime do GPT-4o em Azure. Ele foi baseado em um repositório de exemplo criado pela Microsoft, para [este artigo](https://aka.ms/voicerag).

![RTMTPattern](docs/RTMTPattern.png)

## Rodando esse exempli
Segueiremos 3 passos para rodar o exemplo no seu ambiente: pre-requisitos, montar o ambiente e executar o app.

### 1. Pre-requisitos
Voce precisará do seguinte serviço no seu ambiente Azure: 
1. [Azure OpenAI](https://ms.portal.azure.com/#create/Microsoft.CognitiveServicesOpenAI), com 1 modelo deployado: **gpt-4o-realtime-preview**. 

### 2. Montando o ambiente
Essa aplicação precisa saber quais serviços usar para o Azure OpenAI and Azure AI Search. Para isso, você pode definir as seguintes variáveis de ambiente ou usar elas em um arquivo ".env" file no diretório "app/backend/".
   ```
   AZURE_OPENAI_ENDPOINT=wss://<your instance name>.openai.azure.com
   AZURE_OPENAI_DEPLOYMENT=gpt-4o-realtime-preview
   AZURE_OPENAI_API_KEY=<your api key>
   ```
   Para usar o Entra ID (seu usuário localmente ou identidade gerenciada quando deployado) é só não setar a chave. 

### 4. Rodando a aplicação

1. Instale as ferramentas necessárias:
   - [Node.js >= 20.0](https://nodejs.org/en)
   - [Python >=3.11](https://www.python.org/downloads/)
      - **Important**: Python e o gerenciador de pacotes pip devem estar no path do Windows para que os scripts functionem.
      - **Important**: Garanta que você consegue rodar `python --version` no console. Em sistemas operacionais Ubuntu, você pode ter que rodar o comando `sudo apt install python-is-python3` para linkar `python` a `python3`.

2. Clone o repo (`git clone https://github.com/andreracz/RealTimeBank.git`)
3. Crie um virtual environment de python e ative ele.
4. Rode o seguinte comando no console para fazer o build do front:

   Windows:

   ```pwsh
   cd app
   cd frontend
   npm install
   npm run build
   ```

   Linux/Mac:

   ```bash
   cd app
   cd frontend
   npm install
   npm run build
   ```
5. Rode o seguinte comando no console para subir o servidor:

   Windows:

   ```pwsh
   cd app
   cd backend
   pip install -r requirements.txt
   python app.py
   ```

   Linux/Mac:

   ```bash
   cd app
   cd backend
   pip install -r requirements.txt
   python app.py
   ```

6. A aplicação deverá rodar em http://localhost:8765

