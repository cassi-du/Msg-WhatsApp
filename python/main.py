import sys
import json
from python.service import processar_chat

def main():
    try:
        if len(sys.argv) < 2:
            raise ValueError("Caminho do arquivo _chat.txt não informado")

        caminho_txt = sys.argv[1]
        periodo = sys.argv[2] if len(sys.argv) > 2 else "W"

        resultado = processar_chat(
            caminho_txt=caminho_txt,
            periodo=periodo
        )

        # Retorno padrão para o Node
        print(json.dumps({
            "status": "success",
            "data": resultado
        }))

    except Exception as e:
        # Erro padronizado
        print(json.dumps({
            "status": "error",
            "message": str(e)
        }))
        sys.exit(1)

if __name__ == "__main__":
    main()
