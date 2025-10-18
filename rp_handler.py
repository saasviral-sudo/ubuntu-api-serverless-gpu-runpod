import runpod
import subprocess
import shlex

def handler(event):
    print("Worker Start")
    input_data = event.get('input', {})
    
    # Pega o comando para executar
    command_string = input_data.get('command')  

    if not command_string:
        return {
            "error": "Nenhum 'command' foi fornecido no 'input'."
        }

    print(f"Executando comando: {command_string}")

    try:
        # Executa o comando usando shell=True para interpretar a string como um comando de shell
        # (permite pipes '|', redirecionamentos '>', etc.)
        # ATENÇÃO: Isso pode ser um risco de segurança se a entrada não for confiável.
        result = subprocess.run(
            command_string, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=900
        )
        
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")

        # Retorna a saída padrão, erro padrão e o código de retorno
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode
        }
    
    except subprocess.TimeoutExpired:
        print("Comando expirou")
        return {
            "error": "Comando expirou (timeout de 900s).",
            "stdout": "",
            "stderr": "TimeoutExpired"
        }
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {str(e)}")
        return {
            "error": f"Ocorreu um erro inesperado: {str(e)}",
            "stdout": "",
            "stderr": str(e)
        }

if __name__ == '__main__':
    runpod.serverless.start({'handler': handler })