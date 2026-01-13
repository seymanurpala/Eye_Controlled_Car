#include <WiFi.h>
#include <WiFiClient.h>

// WiFi ayarları
const char* ssid = "********";
const char* password = "********";

WiFiServer server(80);

// Motor pinleri
const int IN1 = 5;
const int IN2 = 18;
const int ENA = 23;
const int IN3 = 21;
const int IN4 = 22;
const int ENB = 19;

// Komut işleme
String gelenKomut = "";
unsigned long hareketBaslangic = 0;
bool hareketAktif = false;
String aktifKomut = "";

void setup() {
  Serial.begin(115200);

  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(ENA, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(ENB, OUTPUT);

  dur();

  WiFi.begin(ssid, password);
  Serial.print("WiFi bağlanıyor");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n✅ Bağlandı: " + WiFi.localIP().toString());

  server.begin();
}

void loop() {
  WiFiClient client = server.available();
  if (client) {
    Serial.println("🌐 Yeni bağlantı geldi");
    String requestLine = client.readStringUntil('\r');
    client.read(); // '\n' karakterini temizle

    Serial.println("📥 WiFi komutu: " + requestLine);

    // Komut çözümle
    if (requestLine.indexOf("GET /geri") >= 0) {
      komutIsle("geri");
    } else if (requestLine.indexOf("GET /ileri") >= 0) {
      komutIsle("ileri");
    } else if (requestLine.indexOf("GET /sag") >= 0) {
      komutIsle("sag");
    } else if (requestLine.indexOf("GET /sol") >= 0) {
      komutIsle("sol");
    } else if (requestLine.indexOf("GET /dur") >= 0) {
      komutIsle("dur");
    }

    // İsteklere basit HTTP cevabı döndür
    client.println("HTTP/1.1 200 OK");
    client.println("Content-Type: text/plain");
    client.println("Connection: close");
    client.println();
    client.println("Komut alindi");
    delay(1);
    client.stop();
  }

  // Serial komutu al
  if (Serial.available()) {
    gelenKomut = Serial.readStringUntil('\n');
    gelenKomut.trim();
    Serial.println("📥 Serial komutu: " + gelenKomut);
    komutIsle(gelenKomut);
  }

  // Hareket süresi kontrolü
  if (hareketAktif && millis() - hareketBaslangic >= 5000) {
    dur();
    Serial.println("⏱️ Durdu (5 saniye bitti)");
    hareketAktif = false;
    aktifKomut = "";
  }
}

void komutIsle(String komut) {
  if (komut == "ileri") {
    ileri();
  } else if (komut == "geri") {
    geri();
  } else if (komut == "sol") {
    solaDon();
  } else if (komut == "sag") {
    sagaDon();
  } else if (komut == "dur") {
    dur();
    hareketAktif = false;
    aktifKomut = "";
  }
}

void geri() {
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  analogWrite(ENA, 200);
  analogWrite(ENB, 200);
  hareketBaslangic = millis();
  hareketAktif = true;
  aktifKomut = "geri";
  Serial.println("🚗 Geri gidiyor");
}

void ileri() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
  analogWrite(ENA, 200);
  analogWrite(ENB, 200);
  hareketBaslangic = millis();
  hareketAktif = true;
  aktifKomut = "ileri";
  Serial.println("🔙 İleri gidiyor");
}

void sagaDon() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  analogWrite(ENA, 200);
  analogWrite(ENB, 200);
  hareketBaslangic = millis();
  hareketAktif = true;
  aktifKomut = "sag";
  Serial.println("↩️ Sağa dönüyor");
}

void solaDon() {
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
  analogWrite(ENA, 200);
  analogWrite(ENB, 200);
  hareketBaslangic = millis();
  hareketAktif = true;
  aktifKomut = "sol";
  Serial.println("↪️ Sola dönüyor");
}

void dur() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
  analogWrite(ENA, 0);
  analogWrite(ENB, 0);
  Serial.println("🛑 Durdu");
}
