// A página e a API são servidas pelo mesmo computador.
const API_URL = window.location.protocol === "file:" ? "http://localhost:8080" : window.location.origin;

async function buscarAtualizacoes() {
  try {
    const resposta = await fetch(`${API_URL}/status`);
    if (!resposta.ok) throw new Error(`HTTP ${resposta.status}`);
    const dados = await resposta.json();
    document.getElementById("connectionDot").className = "connection-dot online";
    document.getElementById("connectionLabel").innerText = "Sistema conectado";
    document.getElementById("numeroDisplay").innerText = dados.senha_atual || `A${String(dados.posicao_atual).padStart(3, "0")}`;
    document.getElementById("txtComando").innerText = dados.ultimo_comando;
    document.getElementById("txtMensagem").innerText = dados.mensagem;
    const seletor = document.getElementById("guicheSelect");
    if (seletor.value !== String(dados.guiche_atual)) seletor.value = String(dados.guiche_atual);
  } catch (erro) {
    console.error("Erro ao buscar dados do servidor:", erro);
    document.getElementById("connectionDot").className = "connection-dot offline";
    document.getElementById("connectionLabel").innerText = "Sem conexão com o servidor";
    document.getElementById("txtMensagem").innerText = "Verifique se o servidor está rodando em http://localhost:8080.";
  }
}

async function zerarContador() {
  try {
    const resposta = await fetch(`${API_URL}/reset`, { method: "POST" });
    if (!resposta.ok) throw new Error(`HTTP ${resposta.status}`);
    await buscarAtualizacoes();
  } catch (erro) { console.error("Erro ao reiniciar a fila:", erro); }
}

async function trocarGuiche(evento) {
  const seletor = evento.currentTarget;
  seletor.disabled = true;
  try {
    const resposta = await fetch(`${API_URL}/guiche`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ guiche: Number(seletor.value) })
    });
    if (!resposta.ok) throw new Error(`HTTP ${resposta.status}`);
    await buscarAtualizacoes();
  } catch (erro) {
    console.error("Erro ao trocar o guichê:", erro);
    document.getElementById("txtMensagem").innerText = "Não foi possível trocar o guichê.";
  } finally { seletor.disabled = false; }
}

document.getElementById("guicheSelect").addEventListener("change", trocarGuiche);
buscarAtualizacoes();
setInterval(buscarAtualizacoes, 1000);
