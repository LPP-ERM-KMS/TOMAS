#define outputA 34 //green
#define output0 32 //grey -> blue
#define outputB 30 //yellow

int counter = -40;
int currentStateA;
int currentState0;
int lastStateA;
String currentDir ="";

void setup() {
  
  // Set encoder pins as inputs
  pinMode(outputA,INPUT);
  pinMode(outputB,INPUT);


  // Setup Serial Monitor
  Serial.begin(9600);
  // Read the initial state of outputA
  lastStateA = digitalRead(outputA);
}

void loop() {
  
  // Read the current state of outputA
  currentStateA = digitalRead(outputA);


  // If last and current state of outputA are different, then pulse occurred
  // React to only 1 state change to avoid double count
  if (currentStateA != lastStateA  && currentStateA == 1){

    // If the outputB state is different than the outputA state then
    // the encoder is rotating CCW so decrement
    if (digitalRead(outputB) != currentStateA) {
      counter --;
      currentDir ="Inwards";
    } else {
      // Encoder is rotating CW so increment
      counter ++;
      currentDir ="Outwards";
    }

    Serial.print("Direction: ");
    Serial.print(currentDir);
    Serial.print(" | Traveled distance (cm) (needs to be verified): ");
    Serial.println(counter*0.016);
  }
  currentState0 = digitalRead(output0);
  if (currentState0 == 1) {counter = 0;}

  // Remember last outputA state
  lastStateA = currentStateA;

  // Put in a slight delay to help debounce the reading
  delay(1);
}
