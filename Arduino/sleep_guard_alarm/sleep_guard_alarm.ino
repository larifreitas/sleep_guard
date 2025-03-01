void setup() {
  Serial.begin(9600);
  pinMode(10, OUTPUT);
  digitalWrite(10, HIGH); // Garante que o buzzer fique desligado inicialmente
}

void loop() {
  if (Serial.available() > 0) {
    String comando = Serial.readStringUntil('\n');
    comando.trim();
    Serial.print("Comando recebido: ");
    Serial.println(comando);
  
    if (comando == "SONOLENCIA") {
      for (int i = 0; i <= 3; i++) {
        digitalWrite(10, LOW);  // Aciona o buzzer
        delay(200);
        digitalWrite(10, HIGH); // Desliga o buzzer
        delay(100);
      }
    } 
    else if (comando == "FADIGA") {
      for (int i = 0; i <= 1; i++) {      
        digitalWrite(10, LOW);  // Aciona o buzzer
        delay(200);
        digitalWrite(10, HIGH); // Desliga o buzzer
        delay(100);
      }
    } 
    else if (comando == "FADIGA_2") {
      for (int i = 0; i <= 2; i++) {      
        digitalWrite(10, LOW);  // Aciona o buzzer
        delay(200);
        digitalWrite(10, HIGH); // Desliga o buzzer
        delay(100);
      }
    }
  }
}
