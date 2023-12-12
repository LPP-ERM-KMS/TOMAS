#include <ArxContainer.h>
#include <ezButton.h>

/*
   Define the stepper motors conntected to the motors (A is prematchingbox, P is parallel and S is series in L-box)
   and to the probes (X is sample manipulator, Y is horizontal triple probe, Z is vertical triple probe).
*/
arx::vector<String> Motors = {"A", "P", "S", "X", "Y", "Z"};

/*
  Define a vector to keep track of the positions of the objects (capacitors and probes) that are moved by the stepper motors
*/
arx::vector<int> Pos = {0, 0, 0, 0, 0, 0};

/*
   Define a vector for the pins of the Arduino that are used to drive the stepper motors
*/

arx::vector<int> limitPinMin = {2, 7, 13, 17, 22, 27};
arx::vector<int> limitPinMax = {3, 8, 12, 18, 23, 28};
arx::vector<int> dirPin = {4, 9, 14, 19, 24, 29};
arx::vector<int> pulsePin = {5, 10, 15, 20, 25, 30};
arx::vector<int> enablePin = {6, 11, 16, 21, 26, 31};


/*
   Define a vector for the limit switches. It was only possible to work with pointers
*/
arx::vector<ezButton*> limitSwitchMin;
arx::vector<ezButton*> limitSwitchMax;

/*
   List the characteristics of the stepper motors
*/
arx::vector<int> pulsesPerRev = {400, 400, 400, 400, 400, 400}; //The number of pulses that let the stepper motor make a full revolution of 360 degrees
arx::vector<int> stepsPerRev = {400, 400, 400, 4, 4, 4}; //The user-defined number of steps we want there to be in a full revolution
arx::vector<int> pulsesPerStep = {0, 0, 0, 0, 0, 0}; // The setup function will enter the number of pulses per step in the vector
int millisbetweenPulses = 1; // The number of milliseconds the motor waits between pulses

//====================================================================================================================

/*
  Function to split an input string at the spaces
*/
arx::vector<String> splitString(String str)
{
  arx::vector<String> strs;
  while (str.length() > 0) {
    int index = str.indexOf(' ');
    if (index == -1) { // No space found
      strs.push_back(str);
      break;
    } else {
      strs.push_back(str.substring(0, index));
      str = str.substring(index + 1);
    }
  }
  return strs;
}

/*
   Function to find the index of an entry in a vector
*/
int findIndex(arx::vector<String> vec, String s)
{
  int i = 0;
  for (i; i < vec.size(); i++) {
    if (vec[i] == s) break;
  }
  // if entry is not part of the vector, return errormessage
  if (i == vec.size()) Serial.println("Error: Motor not found by Arduino");
  else return i;
  
}

/*
   Function to determine the limit positions of the Motors
*/
void findLimits(String motor, int &min, int &max)
{
  //Find the index for the motor X that is used in the Arduino code
  int i = findIndex(Motors, motor);

  // Set the direction of the stepper motor, first for decreasing steps
  digitalWrite(dirPin[i], HIGH);  //CCW

  // Step until the limit switch is touched
  bool status = true;
  while (status == true) {
    status = Step(i);
  }
  min = Pos[i];

  // Set the direction of the stepper motor, now for increasing steps
  digitalWrite(dirPin[i], LOW); //CW

  // Step until the limit switch is touched
  status = true;
  while (status == true) {
    status = Step(i);
  }
  max = Pos[i];

  // Motor for vertical (dynamic zero)
  max = max-min;
  min = 0;
  Pos[i] = max;
}

/*
   Turn the stepper motor with index i a number of pulses according to one steps, e.g. 40 pulses in 1 step.
   If a limitswitch is touched, go back until the limit switch is no longer touched and return false.
*/
bool Step(int i)
{

  // Start counting from 1 in order to keep track of number of steps with modulo-operator.
  for (int nPulses = 1; nPulses <= pulsesPerStep[i]; nPulses++) {

    // Check if the moving object touches the limit switch.
    // In order to do so, the loop() function of the limitswitch must be called first.
    limitSwitchMin[i]->loop();
    limitSwitchMax[i]->loop();
    bool HitASwitch = false;
    // Move until no longer hitting min limit switch
    while (limitSwitchMin[i]->getState() == HIGH) {
        HitASwitch = true;
        digitalWrite(dirPin[i], LOW);
        for (int nPulses = 1; nPulses <= pulsesPerStep[i]; nPulses++) {
            digitalWrite(pulsePin[i], HIGH);
            digitalWrite(pulsePin[i], LOW);
            delay(millisbetweenPulses);
        }
        limitSwitchMin[i]->loop();
    }
    // Move until no longer hitting max limit switch
    while (limitSwitchMax[i]->getState() == HIGH) {
        HitASwitch = true;
        digitalWrite(dirPin[i], HIGH);
        for (int nPulses = 1; nPulses <= pulsesPerStep[i]; nPulses++) {
            digitalWrite(pulsePin[i], HIGH);
            digitalWrite(pulsePin[i], LOW);
            delay(millisbetweenPulses);
        }
        limitSwitchMax[i]->loop();
    }
    if (HitASwitch){return false;}
    digitalWrite(pulsePin[i], HIGH);
    digitalWrite(pulsePin[i], LOW);
    delay(millisbetweenPulses);
    if (nPulses % pulsesPerStep[i] == 0) {
        if (!digitalRead(dirPin[i])) Pos[i] += 1;
        else Pos[i] -= 1;
    }
  }
  return true;
}

/*
   The setup function will be executed once by the Arduino, at the start of the program
*/
void setup() {

  /*
     Start the serial monitor for textual input/output.
     The serial monitor is connected to the python script, so the input/output becomes communication between Python and Arduino.
  */
  Serial.begin(9600);
  Serial.println("Arduino is ready");

  /*
    Determine the number of pulses per step
  */
  for (int i = 0; i < Motors.size(); i++) {
    pulsesPerStep[i] = pulsesPerRev[i] / stepsPerRev[i];
  }
  /*
     Set the dedicated arduino pins for output purposes
  */
  for (int i = 0; i < Motors.size(); i++) {
    pinMode(dirPin[i], OUTPUT);
    pinMode(pulsePin[i], OUTPUT);
  }

  /*
    Initialize the limitswitches and set the debounce times to 50 millisecons such that the state of the switch does not
    toggle quickly between high and low due to mechanical issues.
  */
  for (int i = 0; i < Motors.size(); i++) {
    limitSwitchMin[i] = new ezButton(limitPinMin[i]);
    limitSwitchMin[i]->setDebounceTime(50);
    limitSwitchMax[i] = new ezButton(limitPinMax[i]);
    limitSwitchMax[i]->setDebounceTime(50);
  }

  /*
     Recieve start position of motors from Python in the form X x Y y Z z
     with X,Y,Z in [A,P,S, X, Y, Z] and x,y,z in [1,100].
     Split the string at the white spaces, to obtain a vector <X,x,Y,y,Z,z>.
  */
  String str = Serial.readStringUntil('\n');
  arx::vector<String> strs  = splitString(str);

  /*
     Enter the start positions of the motors in the array [a,p,s]
  */
  for (int n = 0; n < strs.size(); n += 2) {
    //Find the index for the motor that is used in the Arduino code
    int i = findIndex(Motors, strs[n]);
    Pos[i] = strs[n + 1].toInt();
  }

  /*
     Return positions to Python for cross-check.
  */
  // Return the positions to Python
  String returnMessage = Motors[0] + " " + String(Pos[0]);
  for (int i = 1; i < Motors.size(); i++) returnMessage += " " + Motors[i] + " " + String(Pos[i]);
  Serial.println(returnMessage);
}

/*
   The loop function will be executed on repeat by the Arduino. 
   Do not put any code outside the if-else structure
*/
void loop() {

  /*
     Split the string at the white spaces, to obtain a vector <X,x,Y,y,Z,z>.
  */
  String str = Serial.readStringUntil('\n');
  arx::vector<String> strs  = splitString(str);

  /*
     Determine the limits of the specified motors
  */
  if (strs[0] == "limits") {

    //If no motor is specified, determine limits for all motors
    if (strs.size() == 0) {
      for (int i = 0; i < Motors.size(); i++) strs.push_back(Motors[i]);
    }

    String returnLimits;
    for (int n = 1; n < strs.size(); n++) {
      int Limitmin, Limitmax;
      findLimits(strs[n], Limitmin, Limitmax);
      returnLimits += " " + strs[n] + " " + Limitmin + " " + Limitmax;
    }
    // Return the limits
    Serial.println(returnLimits);

    // Return the positions to Python
    String returnMessage = Motors[0] + " " + String(Pos[0]);
    for (int i = 1; i < Motors.size(); i++) returnMessage += " " + Motors[i] + " " + String(Pos[i]);
    Serial.println(returnMessage);
    
    /*
       Move motors to new position, specified by Python in the form X x Y y Z z
       with X,Y,Z in [A,P,S, X, Y, Z] and x,y,z in [1,100].
    */
  } else if (strs.size() >= 2) {

    // For consecutive pairs in the string, e.g. X x,
    for (int n = 0; n < strs.size(); n += 2) {

      int arg;
      // if x is a valid position, i.e. an integer (not 0),
      if (strs[n + 1].toInt() || (strs[n + 1] == "0")) {
	if (strs[n + 1] == "0"){arg=0;}
	else {arg = strs[n + 1].toInt();}
        //Find the index for the motor X that is used in the Arduino code
        int i = findIndex(Motors, strs[n]);

        // determine the steps to be taken relative to the current position.
        int steps = arg - Pos[i];
        // Set the direction of the stepper motor, based on the sign of the steps to be taken. [shorter, digitalWrite(dirPinA, steps > 0? LOW : HIGH);]
        if (steps > 0) digitalWrite(dirPin[i], LOW); //CW
        else digitalWrite(dirPin[i], HIGH);  //CCW
        // Turn the stepper motor a number of steps
        for (int s = 0; s < abs(steps); s++) {
          bool status = Step(i);
          if (status == false) {
            Serial.println("Error: motor " + Motors[i] + " at limit");
            Pos[i] = 1;
            break;
          }
        }
      } else {
        Serial.println("Error: Command not understood by Arduino");
      }
    }
    
    // Return the positions to Python
    String returnMessage = Motors[0] + " " + String(Pos[0]);
    for (int i = 1; i < Motors.size(); i++) returnMessage += " " + Motors[i] + " " + String(Pos[i]);
    Serial.println(returnMessage);
  }

}
