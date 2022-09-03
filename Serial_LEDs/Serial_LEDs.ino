const int ledPin1 = 12;
const int ledPin2 = 13;
const int ledPin3 = 14;

void setup() {
  Serial.begin(9600);

  pinMode(ledPin1,OUTPUT);
  pinMode(ledPin2,OUTPUT);
  pinMode(ledPin3,OUTPUT);
}

void loop() {
  
  //Leer puerto serial
  
  if(Serial.available()>0){
    switch(Serial.read()){
      case 'A':    //Corresponde a limon amarillo
        digitalWrite(ledPin1,HIGH);
        digitalWrite(ledPin2,LOW);
        digitalWrite(ledPin3,LOW);
        break;
      case 'V':    //Corresponde a limon Verde
        digitalWrite(ledPin2,HIGH);
        digitalWrite(ledPin1,LOW);
        digitalWrite(ledPin3,LOW);
        break;
      case 'R':    //Corresponde a Limon Rechazado
        digitalWrite(ledPin3,HIGH);
        digitalWrite(ledPin1,LOW);
        digitalWrite(ledPin2,LOW);
        break;
    }
  }
  
}
