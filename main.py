from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import Literal

from pydantic import BaseModel, Field

app = FastAPI(title="Painel de Senha Interativo")

# Permite que o painel aberto como arquivo local consulte a API no navegador.
# A API não usa cookies nem autenticação, então credenciais CORS ficam desativadas.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"]
)

# Estado global: controle da posição da senha
painel_estado = {
    "posicao_atual": 0,
    "mensagem": "Painel inicializado. Use o controle para navegar.",
    "ultimo_comando": "Nenhum"
}

class RegistroSinal(BaseModel):
    codigo: int = Field(gt=0)
    botao: Literal["A", "B"]

@app.get("/status")
def obter_status():
    """O Frontend consulta esta rota a cada 1 segundo para atualizar a tela."""
    return painel_estado

@app.post("/webhook-rf")
def receber_sinal_esp32(dados: RegistroSinal):
    """O ESP32 chama esta rota quando você clica no controle remoto."""
    global painel_estado

    if dados.botao == "A":
        # Botão A: Avança a senha para a frente
        painel_estado["posicao_atual"] += 1
        painel_estado["ultimo_comando"] = "Avançar (Botão A)"
        painel_estado["mensagem"] = f"Avançou para o dígito/posição {painel_estado['posicao_atual']}"
        print(f"[PAINEL] Avançando. Posição atual: {painel_estado['posicao_atual']}")
        
    else:  # Literal valida que o botão só pode ser A ou B.
        # Botão B: Volta a senha para trás (evitando números negativos)
        if painel_estado["posicao_atual"] > 0:
            painel_estado["posicao_atual"] -= 1
            painel_estado["mensagem"] = f"Voltou para o dígito/posição {painel_estado['posicao_atual']}"
        else:
            painel_estado["mensagem"] = "Já está no início da senha! Não é possível voltar mais."
            
        painel_estado["ultimo_comando"] = "Voltar (Botão B)"
        print(f"[PAINEL] Voltando. Posição atual: {painel_estado['posicao_atual']}")
        
    return {"status": "sucesso", "posicao": painel_estado["posicao_atual"]}

@app.post("/reset")
def zerar_painel():
    """Rota opcional para zerar o painel pelo frontend."""
    global painel_estado
    painel_estado["posicao_atual"] = 0
    painel_estado["mensagem"] = "Painel reiniciado manualmente para a posição 0."
    painel_estado["ultimo_comando"] = "Reset Web"
    return painel_estado


# Sirva o painel pela mesma origem da API para evitar restrições de file://.
app.mount("/", StaticFiles(directory=Path(__file__).parent, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
