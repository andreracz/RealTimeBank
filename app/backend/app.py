import os

from dotenv import load_dotenv
from aiohttp import web
from rtmt import RTMiddleTier
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential
from fullbankdomain import attach_bank_tools

systemmsg = """Voce é um assistente bancário que ajuda um cliente a transacionar em usa conta. Seja solicito e educado. Sempre que o usuário pedir uma informação, chame a função correspondente para obter ela atualizada.  A data atual é {date.today()}", "Este é uma simulação de um assistente bancário, que simula um bot de operações bancárias com linguagem natural.\nSe tiver dúvidas das capacidades, pergunte o que ele pode fazer.
O usuário está ouvindo com audio, então é *super* importante que as respostas sejam tão curtas quanto possíveis, se possível, em uma única frase. """

if __name__ == "__main__":
    load_dotenv()
    llm_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    llm_deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT")
    llm_key = os.environ.get("AZURE_OPENAI_API_KEY")

    app = web.Application()

    rtmt = RTMiddleTier(llm_endpoint, llm_deployment, AzureKeyCredential(llm_key))
    rtmt.system_message = systemmsg
    print(rtmt.system_message)
    #attach_rag_tools(rtmt, search_endpoint, search_index, AzureKeyCredential(search_key) if search_key else credentials)
    attach_bank_tools(rtmt)

    rtmt.attach_to_app(app, "/realtime")

    app.add_routes([web.get('/', lambda _: web.FileResponse('./static/index.html'))])
    app.router.add_static('/', path='./static', name='static')
    web.run_app(app, host='localhost', port=8765)
