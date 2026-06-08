/*
  3 Axis Axample
  Runs 3 a Teknic Clearpath motors (two in step and dir, one in pulse burst mode)
  
  the motors cycle forward taking turns starting with X, then Y, then Z
 
 
 This example code is in the public domain.
 */



//Import Required libraries
#include <PulseClearpath.h>
#include <StepController.h>
#include <StepClearpath.h>

// initialize a PulseClearpath Motors
PulseClearpath Y;
StepClearpath X,Z;

//initialize the controller and pass the references to the motors we are controlling
StepController machine(&X,&Y,&Z);

// the setup routine runs once when you press reset:
void setup()
{  
  //DEBUG declare pin 2 as output.  Abe, this shows when the arduino is in the ISR
  pinMode(2,OUTPUT);
  
  //Begin Serial Communication  NOTE: WHEN GOING FAST, communication may lag
  Serial.begin(9600);
  
  X.attach(8,9,6);     //Direction/A is pin 8, Step/B is pin 9, Enable is pin 6
  Y.attach(10,11,5);   //Direction/A is pin 10, Pulse/B is pin 11, Enable is pin 5
  Z.attach(12,13,7);   //Direction/A is pin 12, Step/B is pin 13, Enable is pin 7
  
  X.setMaxVel(100000);
  X.setMaxAccel(200000);
  Z.setMaxVel(100000);
  Z.setMaxAccel(4000);
  
// Enable motors, reset each motors position to 0  
X.enable();
Y.enable();
Z.enable();

delay(100);

// Set up the ISR to constantly check motor position.  PARAMETER MUST BE SET TO 249
machine.Start(249);

 
}

// the loop routine runs over and over again forever:
void loop()
{  
// Move the X motor forward 100,000 counts
   X.move(100000);
   Serial.println("X Motor Move");
   
// wait until the command is finished and then 1 more second
   while(!X.commandDone())
   { 
   }

// Move the Y motor forward 100,000 counts   
   Y.move(100000);
   Serial.println("Y Motor Move");
   
// wait until the command is finished and then 1 more second
   while(!Y.commandDone())
   { 
   }
   // Move the Z motor forward 100,000 counts  
   Z.move(100000);
   Serial.println("Z Motor Move (Y might be lagging the command)");
// wait until the command is finished and then 1 more second
   while(!Z.commandDone())
   { 
   }
   
}
