from datetime import date, timedelta;
from rtmt import RTMiddleTier, Tool, ToolResult, ToolResultDirection

async def callfunction(object, name, args):
    print(name)
    print(args)
    result = getattr(object, name)(**args)
    return ToolResult(result, ToolResultDirection.TO_SERVER) 

def attach_bank_tools(rtmt: RTMiddleTier) -> None:
    bank_functions = FullBankFunctions()
    my_tools = FullBankFunctions.get_openai_functions()
    rtmt.bankFunctions = bank_functions
    for tool in my_tools:
        print(tool["name"])
        rtmt.tools[tool["name"]] = Tool(schema=tool, target=lambda args,tool=tool: callfunction(bank_functions, tool["name"], args))
        
class BankFunctionsData:
    def __init__(self, contaPrincipal,  boletos, contasFavoritas, investimentos):
        self.contaPrincipal = contaPrincipal
        self.boletos = boletos
        self.contasFavoritas = contasFavoritas
        self.investimentos = investimentos
    

class FullBankFunctions:

    sessions = {}

    def __init__(self):
        pass

    def init_session(self, session_id):
        self.sessions[session_id] = BankFunctionsData(
                               ContaCorrente(numero="123", saldo=1000, apelido="conta principal", limite=100),
                               [
                                Boleto(100, "123", "João da Silva", "Escola XPTO", date.today() +timedelta(10), "pendente"),
                                Boleto(200, "456", "João da Silva", "Academia Contoso", date.today(), "pendente"),
                                Boleto(1200, "789", "João da Silva", "Condomínio", date.today() +timedelta(5), "pendente"),
                                ],
                                [
                                    ContaCorrente(numero="andre@abc.com", saldo=0, apelido="André"),
                                    ContaCorrente(numero="11912341234", saldo=0, apelido="João"),
                                ],
                                [
                                    ContaCorrente(numero="Poupança", saldo=400)
                                ])

    def boletos_pendentes(self, session_id):
        session = self.sessions[session_id]
        return "Boleto Pendentes:\n" + "\n".join([f"Numero: {b.numero} - Valor: {b.valor}- Cedente: {b.cedente} - Data vencimento: {b.data_vencimento}" for b in session.boletos if b.status == 'pendente'])

    def boletos_agendados(self, session_id):
        session = self.sessions[session_id]
        return "Boleto Agendados:\n" + "\n".join([f"Numero: {b.numero} - Valor: {b.valor} - Cedente: {b.cedente} - Data vencimento: {b.data_vencimento} - Data agendamento: {b.data_agendamento}" for b in session.boletos if b.status == 'agendado'])


    def pagarBoleto(self, session_id, numero_boleto):
        session = self.sessions[session_id]
        boleto = None
        for b in session.boletos:
            if b.numero == numero_boleto:
                boleto = b
                break
        if boleto == None:
            return "Boleto não encontrado"
        try:
            boleto.pagar(session.contaPrincipal)
        except Exception as e:
            return str(e)
        return "Boleto pago com sucesso"

    def agendarBoleto(self, session_id, numero_boleto, data_agendamento):
        session = self.sessions[session_id]
        boleto = None
        for b in session.boletos:
            if b.numero == numero_boleto:
                boleto = b
                break
        if boleto == None:
            return "Boleto não encontrado"
        try:
            boleto.agendar(session.contaPrincipal, data_agendamento)
        except Exception as e:
            return str(e)
        return "Boleto agendado com sucesso"
    
    def cadastrar_pix(self, session_id, chave_pix, apelido):
        """Cadastra uma chave pix"""
        session = self.sessions[session_id]
        conta_destino = None
        for conta in session.contasFavoritas:
            if conta.apelido == apelido:
                conta_destino = conta
                break
        if conta_destino == None:
            conta_destino = ContaCorrente(numero=chave_pix, saldo=0, apelido=apelido)
            session.contasFavoritas.append(conta_destino)
        else:
            return "Já existe uma conta com esse apelido"
        return "Chave pix cadastrada com sucesso"
    
    def transferir_pix(self, session_id, valor, chave_pix):
        session = self.sessions[session_id]
        conta_destino = None
        for conta in session.contasFavoritas:
            if conta.numero == chave_pix:
                conta_destino = conta
                break
        if conta_destino == None:
            conta_destino = ContaCorrente(numero=chave_pix, saldo=0)
            session.contasFavoritas.append(conta_destino)
        try:
            session.contaPrincipal.transferir(valor, conta_destino)
        except Exception as e:
            return str(e)
        return "Transferência realizada com sucesso"


    def transferir(self, session_id, valor, numero_conta_destino):
        session = self.sessions[session_id]
        conta_destino = None
        for conta in session.contasFavoritas:
            if conta.numero == numero_conta_destino:
                conta_destino = conta
                break
        if conta_destino == None:
            return "Conta não encontrada"
        try:
            session.contaPrincipal.transferir(valor, conta_destino)
        except Exception as e:
            return str(e)
        return "Transferência realizada com sucesso"

    def saldo(self, session_id):
        session = self.sessions[session_id]
        return f"Saldo: {session.contaPrincipal.saldo}\nLimite Total: {session.contaPrincipal.limite}\nTotal Disponível: {session.contaPrincipal.limite + session.contaPrincipal.saldo}"
    
    def obter_numero_conta_por_apelido(self, session_id, apelido):
        """Obtem o numero da conta pelo apelido"""
        session = self.sessions[session_id]
        for conta in session.contasFavoritas:
            if conta.apelido.lower() == apelido.lower():
                return conta.numero
        return "Conta não encontrada"
    
    def investir(self, session_id, valor, produto):
        """Investe um valor em um produto"""
        session = self.sessions[session_id]
        #valida se já existe um investimento no produto
        for investimento in session.investimentos:
            if investimento.numero == produto:
                session.contaPrincipal.transferir(valor, investimento)
                return "Investimento realizado com sucesso"
        #cria uma nova conta pra esse investimento
        conta = ContaCorrente(numero=produto, saldo=0)
        session.contaPrincipal.transferir(valor, conta)
        session.investimentos.append(conta)
        return "Investimento realizado com sucesso"
    
    def resgatar(self, session_id, valor, produto):
        """Resgata um valor de um produto"""
        session = self.sessions[session_id]
        #valida se já existe um investimento no produto
        for investimento in session.investimentos:
            if investimento.numero == produto:
                investimento.sacar(valor)
                session.contaPrincipal.depositar(valor)
                return "Resgate realizado com sucesso"
        return "Investimento não encontrado"


    def meus_investimentos(self, session_id):
        """Lista os investimentos do cliente"""
        session = self.sessions[session_id]
        return "Investimentos:\n" + "\n".join([f"Produto: {b.numero} - Valor: {b.saldo}" for b in session.investimentos])
    
    def produtos_investimentos(self, session_id):
        session = self.sessions[session_id]
        return "Produtos de Investimentos:\n" + "\n".join(["CDB - 1.5% a.m.", "LCI - 1.2% a.m.", "LCA - 1.3% a.m.", "Poupança - 0.3% a.m.", "Fundo Multimercado - 1.0% a.m."])
    
    @staticmethod
    def get_openai_functions():
        return [  
            {
                "type": "function",
                "name": "meus_investimentos",
                "description": "Lista os investimentos do cliente",
                "parameters": {
                    "type": "object",
                    "properties": {
                    },
                    "required": [],
                }
            },
            {
                "type": "function",
                "name": "investir",
                "description": "Investe um valor em um produto",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "valor": {
                            "type": "integer",
                            "description": "valor a ser investido"
                        },
                        "produto": {
                            "type": "string",
                            "description": "produto a ser investido"
                        }
                    },
                    "required": ["valor", "produto"],
                }
            },
            {
                "type": "function",
                "name": "resgatar",
                "description": "Resgata um valor de um produto",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "valor": {
                            "type": "integer",
                            "description": "valor a ser investido"
                        },
                        "produto": {
                            "type": "string",
                            "description": "produto a ser investido"
                        }
                    },
                    "required": ["valor", "produto"],
                }
            },
            {
                "type": "function",
                "name": "produtos_investimentos",
                "description": "Lista os produtos de investimentos disponíveis",
                "parameters": {
                    "type": "object",
                    "properties": {
                    },
                    "required": [],
                }
            },
            {
                "type": "function",
                "name": "pagarBoleto",
                "description": "Paga um boleto pelo seu número",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "numero_boleto": {
                            "type": "string",
                            "description": "numero do boleto a pagar"
                        }
                    },
                    "required": ["numero_boleto"],
                }
            },
            {
                "type": "function",
                "name": "agendarBoleto",
                "description": "Agenda um boleto para pagamento futuro pelo seu número",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "numero_boleto": {
                            "type": "string",
                            "description": "numero do boleto a agendar"
                        },
                        "data_agendamento": {
                            "type": "string",
                            "description": "data em que o boleto deve ser pago"
                        }
                    },
                    "required": ["numero_boleto", "data_agendamento"],
                }
            },
            
            {
                "type": "function",
                "name": "boletos_pendentes",
                "description": "Obtem a lista de boletos não pagos",
                "parameters": {
                    "type": "object",
                    "properties": {
                    },
                    "required": [],
                }
            },
            {
                "type": "function",
                "name": "boletos_agendados",
                "description": "Obtem a lista de boletos agendados",
                "parameters": {
                    "type": "object",
                    "properties": {
                    },
                    "required": [],
                }
            },
            {
                "type": "function",
                "name": "cadastrar_pix",
                "description": "Cadastra uma chave pix",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "chave_pix": {
                            "type": "string",
                            "description": "chave pix, pode ser e-mail, telefone, cpf ou numero da conta"
                        },
                        "apelido": {
                            "type": "string",
                            "description": "apelido da conta"
                        }
                    },
                    "required": ["chave_pix", "apelido"],
                }
            },
            {
                "type": "function",
                "name": "transferir_pix",
                "description": "Transfere um valor para uma conta pela chave pix (e-mail, telefone, cpf ou numero da conta)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "valor": {
                            "type": "integer",
                            "description": "valor a ser transferido"
                        },
                        "chave_pix": {
                            "type": "string",
                            "description": "chave pix, pode ser e-mail, telefone, cpf ou numero da conta"
                        },
                        
                    },
                    "required": ["valor", "numero_conta_destino"],
                }
            },
            {
                "type": "function",
                "name": "saldo",
                "description": "Obtem o saldo e limite da conta principal",
                "parameters": {
                    "type": "object",
                    "properties": {
                    },
                    "required": [],
                }
            },
            {
                "type": "function",
                "name": "obter_numero_conta_por_apelido",
                "description": "Obtem a chave pix de uma conta favorita pelo apelido",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "apelido": {
                            "type": "string",
                            "description": "apelido da conta"
                        }
                    },
                    "required": ["apelido"],
                }
            },
            
        ]  


class ContaCorrente:
    def __init__(self, numero, saldo, apelido=None, limite=0):
        self.numero = numero
        self.saldo = saldo
        self.apelido = apelido
        self.limite = limite

    def sacar(self, valor):
        if valor > self.saldo + self.limite:
            raise Exception("Saldo insuficiente")
        self.saldo -= valor

    def depositar(self, valor):
        self.saldo += valor

    def transferir(self, valor, conta_destino):
        self.sacar(valor)
        conta_destino.depositar(valor)

    def __str__(self):
        return f'Numero: {self.numero}\nSaldo: {self.saldo}'
    

class Boleto:
    def __init__(self, valor, numero, sacado, cedente, data_vencimento, status='pendente', data_agendamento=None, **kwargs):
        self.valor = valor
        self.numero = numero
        self.sacado = sacado
        self.cedente = cedente
        self.data_vencimento = data_vencimento
        self.status = status
        self.data_agendamento = data_agendamento

    def pagar(self, conta):
        conta.sacar(self.valor)
        self.status = 'pago'

    def agendar(self, conta, data_agendamento):
        print(data_agendamento)
        self.data_agendamento = data_agendamento
        self.status = 'agendado'

    def __str__(self):
        return f"""Valor: {self.valor}
Numero: {self.numero}
Data de Vencimento: {self.data_vencimento}
Sacado: {self.sacado}
Cedente: {self.cedente}
Data de Agendamento: {self.data_agendamento == None and "Não agendado" or self.data_agendamento}
Status: {self.status}"""