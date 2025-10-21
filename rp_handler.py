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
        
        headers.setdefault('Content-Type', 'application/json')

        response = requests.post(
            url,
            json=payload,
            headers=headers,
            params=params,
            timeout=10
        )
        print(f"Webhook enviado para {url}. Status: {response.status_code}")
    
    except Exception as e:
        print(f"ERRO AO ENVIAR WEBHOOK para {url}: {str(e)}")

def handler(event):
    print("Worker Start")
    input_data = event.get('input', {})
    
    # Pega os parâmetros
    command_string = input_data.get('command')
    uuid = input_data.get('uuid', '')
    webhook_url = input_data.get('webhook')
    webhook_config = input_data.get('webhook_config', {})
    transitional_content = input_data.get('transitional_content', {})

    if not command_string:
        return {
            "error": "Nenhum 'command' foi fornecido no 'input'.",
            "success": False
        }

    print(f"Executando comando: {command_string}")

    stdout_str = ""
    stderr_str = ""
    return_code = -1
    success = False
    error_message = None

    try:
        result = subprocess.run(
            command_string,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        stdout_str = result.stdout
        stderr_str = result.stderr
        return_code = result.returncode
        success = (return_code == 0)

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
        if webhook_url:
            
            webhook_payload = transitional_content.copy() 
            
            webhook_payload.update({
                "uuid": uuid,
                "stdout": stdout_str,
                "stderr": stderr_str,
                "success": success
            })
            
            print(f"Enviando webhook para: {webhook_url}")
            send_webhook(webhook_url, webhook_payload, webhook_config)

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