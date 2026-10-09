// Use o mesmo computador que está servindo esta página. Ao abrir o HTML
// diretamente, hostname fica vazio e o fallback aponta para localhost.
const API_URL =
  window.location.protocol === "file:"
    ? "http://localhost:8080"
    : window.location.origin;

async function buscarAtualizacoes() {
  try {
    const resposta = await fetch(`${API_URL}/status`);
    if (!resposta.ok) throw new Error(`HTTP ${resposta.status}`);
    const dados = await resposta.json();

    document.getElementById("connectionDot").className =
      "connection-dot online";
    document.getElementById("connectionLabel").innerText = "Sistema conectado";

    // Atualiza o número grande no visor e os textos do log
    document.getElementById("numeroDisplay").innerText = dados.posicao_atual;
    document.getElementById("txtComando").innerText = dados.ultimo_comando;
    document.getElementById("txtMensagem").innerText = dados.mensagem;
  } catch (erro) {
    console.error("Erro ao buscar dados do FastAPI:", erro);
    const dot = document.getElementById("connectionDot");
    const label = document.getElementById("connectionLabel");
    const mensagem = document.getElementById("txtMensagem");
    if (dot) dot.className = "connection-dot offline";
    if (label) label.innerText = "Sem conexão com o servidor";
    if (mensagem)
      mensagem.innerText =
        "Sem conexão com a API. Verifique se o servidor está rodando em http://localhost:8080.";
  }
}

async function zerarContador() {
  try {
    const resposta = await fetch(`${API_URL}/reset`, { method: "POST" });
    if (!resposta.ok) throw new Error(`HTTP ${resposta.status}`);
    await buscarAtualizacoes();
  } catch (erro) {
    console.error("Erro ao zerar o painel:", erro);
  }
}

// Monitora a API do Python a cada 1 segundo (Polling)
buscarAtualizacoes();
setInterval(buscarAtualizacoes, 1000);
