from pathlib import Path
from typing import Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

app = FastAPI(title="Painel de Senha Interativo")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

painel_estado = {
    "posicao_atual": 0,
    "senha_atual": "A000",
    "guiche_atual": 1,
    "mensagem": "Painel inicializado. Use o controle para navegar.",
    "ultimo_comando": "Nenhum",
}


class RegistroSinal(BaseModel):
    codigo: int = Field(gt=0)
    botao: Literal["A", "B"]


class SelecaoGuiche(BaseModel):
    guiche: int = Field(ge=1, le=5)


def atualizar_senha():
    painel_estado["senha_atual"] = f"A{painel_estado['posicao_atual']:03d}"


@app.get("/status")
def obter_status():
    return painel_estado


@app.post("/webhook-rf")
def receber_sinal_esp32(dados: RegistroSinal):
    if dados.botao == "A":
        painel_estado["posicao_atual"] += 1
        atualizar_senha()
        painel_estado["ultimo_comando"] = "Avançar (Botão A)"
        painel_estado["mensagem"] = f"Senha {painel_estado['senha_atual']} chamada no guichê {painel_estado['guiche_atual']}"
    elif painel_estado["posicao_atual"] > 0:
        painel_estado["posicao_atual"] -= 1
        atualizar_senha()
        painel_estado["ultimo_comando"] = "Voltar (Botão B)"
        painel_estado["mensagem"] = f"Voltou para a senha {painel_estado['senha_atual']}"
    else:
        painel_estado["ultimo_comando"] = "Voltar (Botão B)"
        painel_estado["mensagem"] = "A fila já está na senha inicial A000."
    return {"status": "sucesso", "posicao": painel_estado["posicao_atual"], "senha": painel_estado["senha_atual"]}


@app.post("/guiche")
def selecionar_guiche(dados: SelecaoGuiche):
    painel_estado["guiche_atual"] = dados.guiche
    painel_estado["mensagem"] = f"Atendimento direcionado ao guichê {dados.guiche}"
    painel_estado["ultimo_comando"] = f"Troca para Guichê {dados.guiche}"
    return painel_estado


@app.post("/reset")
def zerar_painel():
    painel_estado["posicao_atual"] = 0
    atualizar_senha()
    painel_estado["mensagem"] = "Fila reiniciada para a senha A000."
    painel_estado["ultimo_comando"] = "Reiniciar fila"
    return painel_estado


app.mount("/", StaticFiles(directory=Path(__file__).parent, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
