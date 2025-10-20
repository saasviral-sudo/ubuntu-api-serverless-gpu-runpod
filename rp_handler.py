import runpod
import subprocess
import requests
import json

def send_webhook(url, payload, config):
    """
    Função auxiliar para enviar o webhook.
    """
    try:
        headers = config.get('headers', {})
        params = config.get('params', {})
        
        # Garante que o Content-Type seja JSON
        headers.setdefault('Content-Type', 'application/json')

        response = requests.post(
            url,
            json=payload,  # Envia o payload como JSON
            headers=headers,
            params=params,
            timeout=10  # Define um timeout de 10s para o webhook
        )
        print(f"Webhook enviado para {url}. Status: {response.status_code}")
    
    except Exception as e:
        # Se o webhook falhar, apenas imprime o erro.
        # Não queremos que uma falha no webhook pare o worker.
        print(f"ERRO AO ENVIAR WEBHOOK para {url}: {str(e)}")

def handler(event):
    print("Worker Start")
    input_data = event.get('input', {})
    
    # 1. Pega os novos parâmetros opcionais
    command_string = input_data.get('command')
    uuid = input_data.get('uuid', '')  # Default para string vazia
    webhook_url = input_data.get('webhook')  # Default para None
    webhook_config = input_data.get('webhook_config', {})  # Default para dict vazio

    if not command_string:
        return {
            "error": "Nenhum 'command' foi fornecido no 'input'.",
            "success": False
        }

    print(f"Executando comando: {command_string}")

    # 2. Prepara variáveis para o resultado
    stdout_str = ""
    stderr_str = ""
    return_code = -1  # Código de erro padrão
    success = False
    error_message = None

    try:
        # 3. Executa o comando
        result = subprocess.run(
            command_string,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300  # Timeout de 5 minutos
        )
        
        stdout_str = result.stdout
        stderr_str = result.stderr
        return_code = result.returncode
        success = (return_code == 0) # Sucesso se o código de retorno for 0

        print(f"STDOUT: {stdout_str}")
        print(f"STDERR: {stderr_str}")

    except subprocess.TimeoutExpired:
        print("Comando expirou")
        stderr_str = "Comando expirou (timeout de 300s)."
        error_message = stderr_str
        success = False
        
    except Exception as e:
        print(f"Ocorreu um erro inesperado na execução: {str(e)}")
        stderr_str = str(e)
        error_message = f"Ocorreu um erro inesperado: {str(e)}"
        success = False

    finally:
        # 4. Envia o webhook se a URL foi fornecida
        if webhook_url:
            webhook_payload = {
                "uuid": uuid,
                "stdout": stdout_str,
                "stderr": stderr_str,
                "success": success
            }
            print(f"Enviando webhook para: {webhook_url}")
            send_webhook(webhook_url, webhook_payload, webhook_config)

    # 5. Retorna o resultado da execução (para chamadas síncronas)
    if error_message:
        return {
            "error": error_message,
            "stdout": stdout_str,
            "stderr": stderr_str,
            "success": success
        }
    
    return {
        "stdout": stdout_str,
        "stderr": stderr_str,
        "return_code": return_code,
        "success": success
    }

if __name__ == '__main__':
    runpod.serverless.start({'handler': handler})