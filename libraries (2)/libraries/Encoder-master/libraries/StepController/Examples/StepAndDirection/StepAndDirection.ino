/*
  StepAndDirection
  Runs a Teknic Clearpath motor in step and direction mode, back and forth
 
 
 This example code is in the public domain.
 */

//Import Required libraries
#include <PulseClearpath.h>
#include <StepController.h>
#include <StepClearpath.h>

// initialize a StepClearpath Motor
StepClearpath X;

//initialize the controller and pass the reference to the motor we are controlling
StepController machine(&X);

// the setup routine runs once when you press reset:
void setup()
{  
  //DEBUG declare pin 2 as output.  Abe, this shows when the arduino is in the ISR
  pinMode(2,OUTPUT);
  
  //Begin Serial Communication  NOTE: WHEN GOING FAST, communication may lag
  Serial.begin(9600);
  
//X.attach(9);                //attach motor so Step/B is connected to pin 9
//X.attach(8,9);              //Direction/A is pin 8, Step/B is pin 9
  X.attach(8,9,6);            //Direction/A is pin 8, Step/B is pin 9, Enable is pin 6
//X.attach(8,9,6,4);          //Direction/A is pin 8, Step/B is pin 9, Enable is pin 6, HLFB is pin 4

// Set max Velocity.  Parameter can be between 2 and 100,000
  X.setMaxVel(100000);
  
// Set max Acceleration.  Parameter can be between 4000 and 2,000,000
  X.setMaxAccel(200000);
  
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
   Serial.println("Positive Move Begins");
   
// wait until the command is finished and then 1 more second
   while(!X.commandDone())
   { 
   }
   Serial.println("Move Done");
   delay(1000);
  
// Move the motor backwards 100,000 counts
   X.move(-100000);
   Serial.println("Negative Move Begins");
   
// wait until the command is finished and then 1 more second   
   while(!X.commandDone())
   { 
   }
   Serial.println("Move Done");
   delay(1000);
   
   
}
