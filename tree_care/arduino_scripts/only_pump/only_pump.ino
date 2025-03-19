const int fertilizePin = 2;  // First relay controlled by input1
const int hydratePin = 7;  // Second relay controlled by input2

void setup() {
    Serial.begin(9600);
    pinMode(fertilizePin, OUTPUT);
    pinMode(hydratePin, OUTPUT);
    digitalWrite(fertilizePin, HIGH);  
    digitalWrite(hydratePin, HIGH);
}
void loop() {
    if (Serial.available() > 0) {
        String command = Serial.readStringUntil('\n');
        Serial.print("Received: ");
        Serial.println(command);  // Debugging output

        int pin;
        String state;

        int spaceIndex = command.indexOf(' ');
        if (spaceIndex != -1) {
            pin = command.substring(0, spaceIndex).toInt();
            state = command.substring(spaceIndex + 1);
            
            Serial.print("Parsed pin: ");
            Serial.println(pin);
            Serial.print("Parsed state: ");
            Serial.println(state);
            if (state == "LOW") {
                digitalWrite(pin, HIGH);  // Switch OFF if relay is active LOW
                Serial.println("Pump turned OFF");
            } else if (state == "HIGH") {
                digitalWrite(pin, LOW);   // Switch ON if relay is active LOW
                Serial.println("Pump turned ON");
            } else {
                Serial.println("Invalid state");
            }
        } else {
            Serial.println("Invalid command");
        }
    }
}
