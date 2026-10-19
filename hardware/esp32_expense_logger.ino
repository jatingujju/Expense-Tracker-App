// OPTIONAL IoT extension: log expenses with physical buttons on an ESP32.
// Wiring: one leg of each button to the GPIO below, the other leg to GND.
// INPUT_PULLUP uses the ESP32's internal resistor, so no external resistor is needed
// (a pressed button reads LOW).
const int FOOD_BTN = 4, TRAVEL_BTN = 5, RESET_BTN = 18;
int foodCount = 0, travelCount = 0;

void setup() {
  Serial.begin(115200);
  pinMode(FOOD_BTN, INPUT_PULLUP);
  pinMode(TRAVEL_BTN, INPUT_PULLUP);
  pinMode(RESET_BTN, INPUT_PULLUP);
  Serial.println("date,category,amount");   // CSV header - paste serial output into a .csv
}

void loop() {
  if (digitalRead(FOOD_BTN) == LOW)   { foodCount++;   Serial.println("today,Food,100");   delay(300); }
  if (digitalRead(TRAVEL_BTN) == LOW) { travelCount++; Serial.println("today,Travel,150"); delay(300); }
  if (digitalRead(RESET_BTN) == LOW)  { foodCount = travelCount = 0; Serial.println("# reset"); delay(500); }
}
