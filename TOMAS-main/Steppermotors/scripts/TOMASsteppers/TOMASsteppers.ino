#include <ArxContainer.h>
#include <ezButton.h>
#include <multi_channel_relay.h>

/*
   Define the stepper motors conntected to the motors (A is prematchingbox, P is parallel and S is series in L-box)
   and to the probes (X is sample manipulator, Y is horizontal triple probe, Z is vertical triple probe).
*/
std::vector<String> Motors = {"A", "P", "S", "X", "Y", "Z"};

Multi_Channel_Relay LPPS; //Langmuir Probe Power Supply and H/V switch (1-3 are power, 4 is H/V)

/*
  Define a vector to keep track of the positions of the objects (capacitors and probes) that are moved by the stepper motors
*/
std::vector<int> Pos = {0, 0, 0, 0, 0, 0};

/*
   Define a vector for the pins of the Arduino that are used to drive the stepper motors
*/

std::vector<int> limitPinMin = {2, 7, 12, 17, 22, 27};
std::vector<int> limitPinMax = {3, 8, 13, 18, 23, 28};
std::vector<int> dirPin =      {4, 9, 14, 19, 24, 29};
std::vector<int> pulsePin =    {5, 10, 15, 20, 25, 30};
std::vector<int> enablePin =   {6, 11, 16, 21, 26, 31};

int K1HPIN = 41;
int K2HPIN = 42;
int K3HPIN = 43;
int K4HPIN = 44;
int K1VPIN = 36;
int K2VPIN = 37;
int K3VPIN = 38;
int K4VPIN = 39;

/*
   Define a vector for the limit switches. It was only possible to work with pointers
*/
std::vector<ezButton*> limitSwitchMin;
std::vector<ezButton*> limitSwitchMax;

/*
   List the characteristics of the stepper motors
*/
std::vector<int> pulsesPerRev = {400, 400, 400, 400, 400, 400}; //The number of pulses that let the stepper motor make a full revolution of 360 degrees
std::vector<int> stepsPerRev = {400, 400, 400, 40, 40, 40}; //The user-defined number of steps we want there to be in a full revolution
std::vector<int> pulsesPerStep = {0, 0, 0, 0, 0, 0}; // The setup function will enter the number of pulses per step in the vector
int millisbetweenPulses = 1; // The number of milliseconds the motor waits between pulses

//====================================================================================================================

/*
  Function to split an input string at the spaces
*/
std::vector<String> splitString(String str)
{
  std::vector<String> strs;
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
int findIndex(std::vector<String> vec, String s)
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
    // Check if the moving object touches the limit switch.
    // In order to do so, the loop() function of the limitswitch must be called first.
    limitSwitchMin[i]->loop();
    limitSwitchMax[i]->loop();
    bool HitASwitch = false;

    // Move until no longer hitting min limit switch
    // Note: Counter hasn't been tested yet
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
    else {
      // Start counting from 1 in order to keep track of number of steps with modulo-operator.
      for (int nPulses = 1; nPulses <= pulsesPerStep[i]; nPulses++) {
        // move a step
        digitalWrite(pulsePin[i], HIGH);
        digitalWrite(pulsePin[i], LOW);
        delay(millisbetweenPulses);
        if (nPulses % pulsesPerStep[i] == 0) {
            if (!digitalRead(dirPin[i])) Pos[i] += 1;
            else Pos[i] -= 1;
        }
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
  LPPS.begin(0x11); //I^2C address of Power Supply relay
                    
  pinMode(K1HPIN, OUTPUT);    
  pinMode(K1VPIN, OUTPUT);    
  pinMode(K2HPIN, OUTPUT);   
  pinMode(K2VPIN, OUTPUT);   
  pinMode(K3HPIN, OUTPUT);  
  pinMode(K3VPIN, OUTPUT);  
  pinMode(K4HPIN, OUTPUT); 
  pinMode(K4VPIN, OUTPUT); 

                            
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
  std::vector<String> strs  = splitString(str);

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
  std::vector<String> strs  = splitString(str);

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
       with X,Y,Z in [A,P,S,X,Y,Z] and x,y,z in [1,100].

       Arthur 2024: now also able to switch LP power supply between 0,65,110 and 160V and switch LP resistors (R5,R6,R7,R8),
       to accomodate this change there are now also L, R and O codes:
       AaPpSsXxYyZzOoLlRr
       O being either horizontal (0) or vertical (1)
       L being the langmuir probe power supp, values 0,1,2,3 corresponding to:
          0: all battery arrays off, 1: first on, 2: second on and 3: third on.
       R being the Resistor, values are 5-8 for R5-R8
    */
  } else if (strs.size() >= 2) {

    // For consecutive pairs in the string, e.g. X x
    for (int n = 0; n < 12; n += 2) {

      int arg;
      // if x is a valid position, i.e. an integer
      if (strs[n + 1].toInt() || (strs[n + 1] == "0")) {
        //issue with value 0 as not int in arduino 
      	if (strs[n + 1] == "0"){arg=0;}
	      else {arg = strs[n + 1].toInt();}

        //If not a switch statement
        if ((strs[n] != "O") && (strs[n] != "L") && (strs[n] != "R")){
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
              if (i==4) {Pos[4] = 20;}
              else if (i==5) {Pos[5] = 35;}
              else {Pos[i] = 0;}
              break;
            }
          }
        }
        else {
          if (strs[n] == "O") {
            if (strs[n+1] == "0") {
              //Horizontal probe
              LPPS.turn_off_channel(4);
            }
            else if (strs[n+1] == "1") {
              //Vertical probe
              LPPS.turn_on_channel(4);
            }
            else {
              Serial.println("Error: Command not understood by Arduino");
            }
          }
          else if (strs[n] == "L") {
            if (strs[n+1] == "0") {
              //turn off all channels for power
              LPPS.turn_off_channel(1);
              LPPS.turn_off_channel(2);
              LPPS.turn_off_channel(3);
              digitalWrite(K4PIN, LOW);
            }
            else {
              LPPS.turn_off_channel(1);
              LPPS.turn_off_channel(2);
              LPPS.turn_off_channel(3);
              digitalWrite(K4PIN, HIGH); //Allow output
              LPPS.turn_on_channel(strs[n+1].toInt()); 
            }
          }
          else if (strs[n] == "R") {
            if (strs[n+1] == "5") {
              digitalWrite(K1HPIN, LOW);
              digitalWrite(K2HPIN, LOW);
              digitalWrite(K3HPIN, LOW);
              digitalWrite(K1VPIN, LOW);
              digitalWrite(K2VPIN, LOW);
              digitalWrite(K3VPIN, LOW);
            }
            else if (strs[n+1] == "6") {
              digitalWrite(K1HPIN, HIGH);
              digitalWrite(K2HPIN, LOW);
              digitalWrite(K3HPIN, LOW);
              digitalWrite(K1VPIN, HIGH);
              digitalWrite(K2VPIN, LOW);
              digitalWrite(K3VPIN, LOW);

            }
            else if (strs[n+1] == "7") {
              digitalWrite(K1HPIN, LOW);
              digitalWrite(K2HPIN, LOW);
              digitalWrite(K3HPIN, HIGH);
              digitalWrite(K1VPIN, LOW);
              digitalWrite(K2VPIN, LOW);
              digitalWrite(K3VPIN, HIGH);

            }
            else if (strs[n+1] == "8") {
              digitalWrite(K1HPIN, LOW);
              digitalWrite(K2HPIN, HIGH);
              digitalWrite(K3HPIN, HIGH);
              digitalWrite(K1VPIN, LOW);
              digitalWrite(K2VPIN, HIGH);
              digitalWrite(K3VPIN, HIGH);

            }
            else {
              Serial.println("Error: Command not understood by Arduino");
            }
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
