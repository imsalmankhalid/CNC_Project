/*
  PulseBurstPositioning
  Runs a Teknic Clearpath motor in Pulse Burst mode, back and forth 
 
 This example code is in the public domain.
 */
 
//Import Required libraries
#include <PulseClearpath.h>
#include <StepClearpath.h>
#include <StepController.h>

// initialize a PulseClearpath Motor
PulseClearpath X;

//initialize the controller and pass the reference to the motor we are controlling
StepController machine(&X);

// the setup routine runs once when you press reset:
void setup()
{  
  //DEBUG declare pin 2 as output.  Abe, this shows when the arduino is in the ISR
  pinMode(2,OUTPUT);
  
  //Begin Serial Communication  NOTE: WHEN GOING FAST, communication may lag
  Serial.begin(9600);
  
//X.attach(8,9);              //Direction/A is pin 8, Pulse/B is pin 9
  X.attach(8,9,6);            //Direction/A is pin 8, Pulse/B is pin 9, Enable is pin 6
//X.attach(8,9,6,4);          //Direction/A is pin 8, Pulse/B is pin 9, Enable is pin 6, HLFB is pin 4
  
// Enable motor, reset the motor position to 0
X.enable();

delay(100);

// Set up the ISR to constantly check motor position.  PARAMETER MUST BE SET TO 249
machine.Start(249);

 
}

// the loop routine runs over and over again forever:
void loop()
{  
 // Move the motor forward 100,000 counts
   X.move(100000);
   Serial.println("Starting move +100,000");
// wait until the command is finished and then 3 more seconds
   while(!X.commandDone())
   { 
   }
   Serial.println("Move Commanded");
   delay(3000);
   
  // select the the alternate speed set up in MSP
  Serial.println("Alternate Speed");
   X.altSpeed(25);
   
   delay(100);
   
// Move the motor backwards 100,000 counts
   X.move(-100000);
   Serial.println("Starting move -100,000");
// wait until the command is finished and then 10 more seconds  
//We may be moving slower, and unlike step and direction sometimes the motor can lag signifigantly
   while(!X.commandDone())
   { 
   }
    Serial.println("Move Commanded");
   delay(10000);
   
   
}
