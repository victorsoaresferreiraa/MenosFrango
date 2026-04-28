import os
import sys

# Lista de variáveis obrigatórias que definimos no .env.example
REQUIRED_VARS = [
    "DATABASE_URL",
    "JWT_SECRET",
    "ALGORITHM",
    "NEXT_PUBLIC_API_URL"
]

def check_env():
    missing = [var for var in REQUIRED_VARS if not os.getenv(var)]
    
    if missing:
        print("❌ ERRO DE CONFIGURAÇÃO!")
        print(f"As seguintes variáveis de ambiente estão faltando: {', '.join(missing)}")
        print("💡 Dica: Copie o arquivo .env.example para .env e preencha os valores.")
        sys.exit(1) # Mata o processo com erro
    
    print("✅ Todas as variáveis de ambiente foram encontradas!")

if __name__ == "__main__":
    check_env()