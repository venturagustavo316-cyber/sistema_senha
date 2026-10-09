#include <WiFi.h>
#include <HTTPClient.h>
#include <RCSwitch.h>

// Preencha com as credenciais da rede Wi-Fi que também conecta o computador.
const char* WIFI_SSID = "SEU_WIFI";
const char* WIFI_PASSWORD = "SUA_SENHA_WIFI";

// Troque pelo IPv4 do computador (ipconfig no Windows). Não use 127.0.0.1:
// esse endereço apontaria para o próprio ESP32.
const char* SERVER_URL = "http://IP_DO_COMPUTADOR:8080/webhook-rf";

const uint8_t PINO_RECEPTOR = 13;
const uint8_t LED_INTERNO = 2;
const unsigned long CODIGO_ABRIR = 4765425UL;
const unsigned long CODIGO_FECHAR = 4765426UL;
const unsigned long INTERVALO_ANTI_REPETICAO_MS = 500;

RCSwitch receptor;
unsigned long ultimaLeituraValida = 0;

void conectarWiFi() {
  if (WiFi.status() == WL_CONNECTED) return;

  Serial.printf("Conectando ao Wi-Fi %s", WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWi-Fi conectado.");
  Serial.print("IP do ESP32: ");
  Serial.println(WiFi.localIP());
}

void enviarComando(unsigned long codigo, char botao) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Wi-Fi desconectado; comando nao enviado.");
    return;
  }

  WiFiClient cliente;
  HTTPClient http;
  http.setTimeout(3000);

  if (!http.begin(cliente, SERVER_URL)) {
    Serial.println("Nao foi possivel iniciar a conexao HTTP.");
    return;
  }

  http.addHeader("Content-Type", "application/json");
  String corpo = "{\"codigo\":" + String(codigo) + ",\"botao\":\"" + botao + "\"}";
  int resposta = http.POST(corpo);

  Serial.printf("POST botao %c: HTTP %d\n", botao, resposta);
  if (resposta > 0) Serial.println(http.getString());
  http.end();
}

void setup() {
  Serial.begin(115200);
  pinMode(LED_INTERNO, OUTPUT);
  digitalWrite(LED_INTERNO, LOW);

  receptor.enableReceive(digitalPinToInterrupt(PINO_RECEPTOR));
  conectarWiFi();
  Serial.println("Pronto para receber os comandos RF.");
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) conectarWiFi();

  if (!receptor.available()) return;

  const unsigned long codigo = receptor.getReceivedValue();
  receptor.resetAvailable();

  if (codigo == 0) return;
  Serial.printf("Codigo RF recebido: %lu\n", codigo);

  const unsigned long agora = millis();
  if (agora - ultimaLeituraValida < INTERVALO_ANTI_REPETICAO_MS) return;

  char botao = '\0';
  if (codigo == CODIGO_ABRIR) {
    botao = 'A';
    digitalWrite(LED_INTERNO, HIGH);
  } else if (codigo == CODIGO_FECHAR) {
    botao = 'B';
    digitalWrite(LED_INTERNO, LOW);
  }

  if (botao != '\0') {
    ultimaLeituraValida = agora;
    enviarComando(codigo, botao);
  } else {
    Serial.println("Codigo ignorado: nao corresponde aos botoes A ou B.");
  }
}
