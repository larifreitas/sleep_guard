void setup() {
  Serial.begin(9600);
  pinMode(10, OUTPUT);
  digitalWrite(10, HIGH);
  delay(3000);

  while (Serial.available() > 0) {
    Serial.read();
  }
}


void loop() {
  if (Serial.available() > 0) {
    String comando = Serial.readStringUntil('\n');
    comando.trim();
    if (comando != "SONOLENCIA" && comando != "FADIGA" && comando != "FADIGA_2") {
      return;
    }
    Serial.println(comando);

  
    if (comando == "SONOLENCIA") {
      for (int i = 0; i < 10; i++) {
        digitalWrite(10, LOW); // Liga
        delay(200);
        digitalWrite(10, HIGH); // Desliga
        delay(100);
      }
    } 
    else if (comando == "FADIGA") {
        digitalWrite(10, LOW);
        delay(200);
        digitalWrite(10, HIGH);
        delay(100);
    } 
    else if (comando == "FADIGA_2") {
      for (int i = 0; i < 2; i++) {      
        digitalWrite(10, LOW);
        delay(200);
        digitalWrite(10, HIGH);
        delay(100);
      }
    }
  }
}
