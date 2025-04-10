import requests
import urllib3
import json
import time 

urllib3.disable_warnings()
 
url = "https://suporte.blokotecnologia.com.br:8443"
HEADERS ={"authtoken":"98D47231-0B42-4C31-849A-D4DBCA3105F8"}

response = requests.get(url,headers=HEADERS,verify=False)

# Endpoint para obter os chamados
busca_chamados = f"{url}/api/v3/requests/930"

# Endpoint para atualizar chamados (adicionar resposta)
adiciona_resposta = f"{url}/api/v3/requests/{'{request_id}'}/notifications"

# Endpoint que busca todos os chamado para verificar o status do chamado
status_chamado = f"{url}/api/v3/requests"

#Requisição para obter o ID de todos os chamado, para que nas funções seguintes possa ser iterado por cada função
def get_new_requests():

    response = requests.get(busca_chamados, headers=HEADERS, verify=False)
    
    if response.status_code == 200:
        data = response.json()
        return [data["request"]]
    else:
        print("Erro ao buscar chamados:", response.text)
        return []


#FUNÇÃO QUE ENVIA RESPOSTA NO CHAMADO QUE ESTÁ COM STATUS ABERTO!
def send_auto_response(request_id):
    url_chamado = status_chamado.format(request_id=request_id)
    response_chamados = requests.get(url_chamado, headers=HEADERS, verify=False)

    if response_chamados.status_code == 200:
        data = response_chamados.json()

        if "requests" in data and len(data["requests"]) > 0:
            chamado = data["requests"][0]
            subject = chamado.get("subject", "Sem assunto")
            #requester = chamado.get("requester", {}).get("email_id")  PARA OS TESTES EXECUTADOS A CONTA NAO TEM EMAIL_ID !!!
            requester = "b.lacerda@nivati.com.br" #ENVIANDO OS TESTES LOCALMENTE PARA MEU EMAIL
            status_name = chamado.get("status", {}).get("name", "")

            if not requester:
                print(f"Chamado {request_id} não possui e-mail do solicitante.")
                return

            # Correção da interpolação do subject
            notification_dict = {
                "notification": {
                    "subject": f"Re: [Request ID: {request_id}] : {subject}",
                    "description": "Olá, chamado recebido! Vamos analisar a solicitação e logo retornamos com um feedback!",
                    "to": [
                        {
                            "email_id": requester
                        }
                    ],
                    "type": "reply"
                }
            }

            payload = {
                "input_data": json.dumps(notification_dict)
            }

            response = requests.post(
                adiciona_resposta.format(request_id=request_id),
                data=payload,
                headers=HEADERS,
                verify=False
            )
        else:
            print(f"Chamado {request_id} não encontrado na resposta.")
    else:
        print(f"Erro ao buscar dados do chamado {request_id}: {response_chamados.text}")


#Realiza uma requisição para obter apenas os chamados abertos
def open_request(request_id):
    url_chamado = status_chamado.format(request_id=request_id)
    response = requests.get(url_chamado, headers=HEADERS, verify=False)

    # se a requisição de busca de chamados for bem sucedida, coloca os dados em json, obtem o campo de status e verifica se está aberto
    if response.status_code == 200:
        data = response.json()

        
        if "requests" in data and len(data["requests"]) > 0:
            chamado = data["requests"][0]
            status_name = chamado["status"]["name"]

            if status_name == "Aberto":
                #caso o chamado esteja aberto chama a função para realizar a resposta
                send_auto_response(request_id)
            else:
                print(f"Chamado {request_id} está com status: {status_name}, não é 'Aberto'.")
        else:
            print(f"Chamado {request_id} não encontrado na resposta.")
    else:
        print(f"Erro na requisição do chamado {request_id}: {response.text}")


        



"""
Chamada de teste para executar uma request e salvar em um arquivo separado

try:
    data = response.json()

    with open("chamados.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print("Arquivo chamados.json salvo com sucesso.")

except json.JSONDecodeError:
    print("Erro ao decodificar JSON:")
    print(response.text)
"""


if __name__== '__main__':


    chamados = get_new_requests()
    for chamado in chamados:
        request_id = chamado["id"]
        #send_auto_response(request_id)
        open_request(request_id)
    

    #DURANTE OS TESTES NAO ESTA EXECUTANDO A CADA 5 MINUTOS
    #print("Aguardando 5 minutos para nova verificação...")
    #time.sleep(300)  # Espera 5 minutos antes da próxima execução