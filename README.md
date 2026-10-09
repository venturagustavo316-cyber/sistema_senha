# Painel de atendimento com ESP32

Aplicação local para acompanhar a posição de uma fila. Um controle remoto RF envia comandos a um ESP32, que atualiza a API Python; o painel web exibe o estado em tempo real.

## Requisitos

- Python 3.10 ou superior
- Arduino IDE e uma placa ESP32
- Biblioteca **RCSwitch** instalada pelo Library Manager da Arduino IDE
- Computador e ESP32 conectados à mesma rede Wi-Fi

## Executar a aplicação

No terminal, na pasta do projeto:

~~~powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py main.py
~~~

Abra http://localhost:8080 no navegador. A API usa a porta 8080; permita o acesso na rede privada caso o Firewall do Windows solicite.

## Configurar o ESP32

Abra esp32_painel_senha.ino na Arduino IDE e configure WIFI_SSID, WIFI_PASSWORD e SERVER_URL no início do arquivo. Use o IPv4 do computador na URL, mantendo :8080/webhook-rf no final. No Windows, encontre o endereço com ipconfig. Não use 127.0.0.1, pois esse endereço apontaria para o próprio ESP32.

Confira também se os códigos RF e os pinos (PINO_RECEPTOR, LED_INTERNO) correspondem à sua montagem. Selecione a placa e a porta serial, carregue o sketch e abra o Monitor Serial em 115200 baud.

O botão A avança uma posição e o botão B volta uma posição, sem deixar o painel abaixo de zero. O sketch ignora repetições RF recebidas em menos de 500 ms.

## Rotas da API

- GET /status: retorna a posição, a última ação e a mensagem atual.
- POST /webhook-rf: recebe um código RF e o botão A ou B.
- POST /reset: reinicia a posição para zero.

## Segurança

O sketch incluído contém apenas valores de exemplo. Configure as credenciais localmente e nunca publique senhas ou dados privados da rede. As credenciais que já tenham sido compartilhadas devem ser trocadas no roteador.

Esta API foi projetada para uso em uma rede local confiável; não a exponha diretamente à internet.
