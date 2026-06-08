/*Lathe_2axis_Controller
 * This program uses an Arduino MEGA to ...
 * Receive input from 2 incremental encoders attached to a lathe X & Z axis handwheels.
 * Drive two clearpath step & direction motors from the encoder inputs.
 * Drive Z axis by half nut lever (switch) to a set feedrate from potentiometer & spindle sensor input.
 * Output onto DRO (4x20 LCD display): X & Z linear positon, RPM, and feed rate (& stop feed positon).
 * Change LCD display values with 3 button inputs having both press and hold functionality.
 *    Buttons 1&2: Push= Toggle X & Z readout between 3 stored memory fields (M1,M2,M3).
 *    Buttons 1&2: Hold= Zero X & Z display value for current memory being displayed.
 *    Button 3: Push= Change units mm<-->inch.
 *    Button 3: Hold >1sec= Store current Z axis position to use as half nut feed automatic disengagement
 *    Button 3: Hold >3sec= Enter "Mode" functions which automate basic operations (Thread, Profile, Sphere)
 *              Button operation in "Mode" is B1=Inc selection, B2=Dec selection, B3=Accept
 *    ______________________
 *    |X_=__+00.0000_in__M1|                   -111.23  = Numeric value indicates feed has been set &
 *    |Z_=__+000.000_mm__M3|                              is the disengage position relative to Z zero.
 *    |RPM_=_0000____Z-STOP|     Z STOP       "_+++>>>" = Z axis is beyond stop location (must move +Z).
 *    |IPM_=_00.0___*******| => Settings =>   "Not_Set" = Indicates no stop defined (use button#3 hold).
 *    ----------------------
 *    Half nut lever can be engaged or disengaged at ANY time with ALL above "Z STOP" settings but only
 *    engagement with "Z STOP" displaying a number will provide auto stop functionality. 
 *  Created 2017-07-15 by Rob Wade www.WadeODesign.com
 *  Sketch uses 89856 bytes (35%) of program storage space. Maximum is 253952 bytes.
 *  Global variables use 5593 bytes (68%) of dynamic memory, leaving 2599 bytes for local variables */
 //********************Library List********************
#include <Encoder.h>            //Uses 2x or *1x interupt pins. https://github.com/PaulStoffregen/Encoder
#include <PulseClearpath.h>     //Clearpath Motor (old ver) See my website www.wadeodesign.com 
#include <StepController.h>     //Clearpath Motor (old ver) See my website www.wadeodesign.com 
#include <Wire.h>               //For LCD I2C communication. On Mega use pins SDA=D20/SDL=D21 (UNO A4/A5).
#include <LiquidCrystal_I2C.h>  //https://github.com/fdebrabander/Arduino-LiquidCrystal-I2C-library
#define EI_NOTEXTERNAL          //Limit for <EnableInterrupt.h> below.
#define EI_NOTPORTK             //Limit for <EnableInterrupt.h> below.
#define EI_NOTPORTJ             //Limit for <EnableInterrupt.h> below.
#include <EnableInterrupt.h>    //For spindle sensor pin external interupt - updated to new library
//********************Library settings********************
PulseClearpath Z;               
PulseClearpath X;               
StepController machine(&X,&Z);  //initialize the controller and pass the reference to the motor we are controlling.####
Encoder xAxisEnc(18, 19);       //BestPerf needs 2 interrupt pins per encoder.
Encoder zAxisEnc(2, 3);         //BestPerf needs 2 interrupt pins per encoder.
LiquidCrystal_I2C lcd(0x3F, 2, 1, 0, 4, 5, 6, 7, 3, POSITIVE);  //Replace 0x3F with your I2C address. 
                                //Use http://playground.arduino.cc/Main/I2cScanner to find your I2C address.
//********************Mechanics Z********************
const int       zMtrPulley =      28;       //USER INPUT: # teeth on Z motor pulley
const int       zScrPulley =      28;       //USER INPUT: # teeth on Z screw pulley
const float     zScrPitch =       5.0;      //USER INPUT: Z lead screw pitch (mm)
const float     zHandwheel =      20.0;     //USER INPUT: Z linear motion (mm) per handwheel rev (was 0.95"/rev)
const int       zEncCntPerRev =   2000;     //USER INPUT: Z encoder counts/rev.  Careful - output may be 4x enc setting.
const int       zMtrCntPerRev =   800;      //USER INPUT: Z motor counts per rev.  Variable with MSP Clearpath software
const float     zPitch =          zScrPitch*((float)zMtrPulley/zScrPulley);  //Screw*Pulley=Resultant Pitch (mm)
const float     zCountAdjust =    (zHandwheel/zEncCntPerRev)/(zPitch/zMtrCntPerRev);  //Z MtrCnts/EncCnts (1.6)
const float     zCountAdjInv =    1.0/zCountAdjust;   //Z EncCnts/MtrCnts.  Inverted to avoid float division (0.625)
//********************Mechanics X********************
const int       xMtrPulley =      24;       //USER INPUT: # teeth on X motor pulley
const int       xScrPulley =      24;       //USER INPUT: # teeth on X screw pulley
const float     xScrPitch =       2.0;      //USER INPUT: X lead screw pitch (mm)
const float     xHandwheel =      2.0;      //USER INPUT: X linear motion (mm) per handwheel rev (was 0.060"/rev)
const int       xEncCntPerRev =   2000;     //USER INPUT: X encoder counts/rev.  Careful - output may be 4x enc setting.
const int       xMtrCntPerRev =   800;      //USER INPUT: X motor counts per rev.  Variable with MSP Clearpath software
const float     xPitch =          xScrPitch*((float)xMtrPulley/xScrPulley);  //Screw*Pulley=Resultant Pitch (mm)
const float     xCountAdjust =    (xHandwheel/xEncCntPerRev)/(xPitch/xMtrCntPerRev);  //X MtrCnts/EncCnts (0.4)
const float     xCountAdjInv =    1.0/xCountAdjust;     //X EncCnts/MtrCnts.  Inverted to avoid float division (2.5)
//********************Encoder variables XZ********************
long            encOldPosZ =      0;
long            encNewPosZ;
long            mtrOldPosZ =      0;
long            mtrNewPosZ;
long            encOldPosX =      0; 
long            encNewPosX;
long            mtrOldPosX =      0;
long            mtrNewPosX;
//********************Z HandWheel Motion variables********************
const int z0Time=24000;         //Max delay allowed (8000+16000... <LCDupdate+maxdelay). Results in delay <16000 which is max value delayMicroseconds can send
const int zATime=8750;          //Tested: Full LCD update = 8524 (was 9120) us    000.000      (7 characters)
const int zBTime=4800;          //Tested: Part-1 LCD update = 4584 (was 3392) us  000 & .00    (2x 3 characters)
const int zCTime=4800;          //Tested: Part-2 LCD update = 4584 (was 3392) us  000 & .0 & x (same as B time but drops a decimal)
const int zDTime=3900;          //Tested: Part-3 LCD update = 3676(was 2508) us  00 & 0.      (2x 2 characters)
const int zETime=700;           //No LCD delay = 404 (was 116) us but min delay motor can handle is 500us (+200 is safety)

const int zVelLimitA=20;
const int zVelLimitB=100;
const int zVelLimitC=800;
const int zVelLimitD=2000;
//const int zVelLimitE=     //todo: remove

const float zMaxHwVel=5.0;                      //(rev/sec) Max possible HW physical rotation as tested.
const float zBuffMult=0.3;                      //# HW rotations allowed as buffer.  Also sets max "lag" (~1/3 seems good)
const float zMaxEncBuf=zBuffMult*zEncCntPerRev; //Max buffer counts allowed (value will correspond to max velocity)
const float zMaxVel=zMaxHwVel*zHandwheel*60.0;  //(mm/min) Max velocity of screw requested based on user inputs HW-rev/s & HW-mm/rev

float zCalcVel;
//float zPrevVel;           //todo: remove
long zDelay1stp;
long zDelayNstp;
unsigned long zTime1st;
unsigned long zTime2nd;
unsigned long zDeltaT;

int       zStepSize;
float     zEncBuffer =      0.0;      //Accumulated # Z encoder counts to move.  Not Integer
float     zEncBufferOld =   0.0;
int       zDelay;                     //Microseconds (us)
//********************X HandWheel Motion variables********************
const int x0Time=24000;         //Max delay allowed (8000+16000... <LCDupdate+maxdelay). Results in delay <16000 which is max value delayMicroseconds can send
const int xATime=8750;          //Tested: Full LCD update = 8524 (was 9120) us    000.000      (7 characters)
const int xBTime=4800;          //Tested: Part-1 LCD update = 4584 (was 3392) us  000 & .00    (2x 3 characters)
const int xCTime=4800;          //Tested: Part-2 LCD update = 4584 (was 3392) us  000 & .0 & x (same as B time but drops a decimal)
const int xDTime=3900;          //Tested: Part-3 LCD update = 3676(was 2508) us  00 & 0.      (2x 2 characters)
const int xETime=700;           //No LCD delay = 404 (was 116) us but min delay motor can handle is 500us (+200 is safety)

const int xVelLimitA=20;
const int xVelLimitB=100;
const int xVelLimitC=300;
const int xVelLimitD=500;
//const int xVelLimitE=     //todo: remove

const float xMaxHwVel=5.0;                      //(rev/sec) Max possible HW physical rotation as tested.
const float xBuffMult=0.3;                      //# HW rotations allowed as buffer.  Also sets max "lag" (~1/3 seems good)
const float xMaxEncBuf=xBuffMult*xEncCntPerRev; //Max buffer counts allowed (value will correspond to max velocity)
const float xMaxVel=xMaxHwVel*xHandwheel*60.0;  //(mm/min) Max velocity of screw requested based on user inputs HW-rev/s & HW-mm/rev

float xCalcVel;
//float xPrevVel;   //todo: remove
long xDelay1stp;
long xDelayNstp;
unsigned long xTime1st;
unsigned long xTime2nd;
unsigned long xDeltaT;

int       xStepSize;                  
float     xEncBuffer =      0.0;      //Accumulated # X encoder counts to move.  Not Integer
float     xEncBufferOld =   0.0;
int       xDelay;                     //Microseconds (us)
//********************LCD variables********************
float     unitConverter =   1.0;        //value 1.0 (mm) or 25.4 (inch) set by button#3 press (mm default).
int       toggleStopZ[] =   {0,0,0};    //toggleStopZ will allow only update to LCD when required.
long      memOffsetZ[] =    {0,0,0};    //Array to hold mtr memory offsets [0,1,2]=[mZ] (mtr cnts).
long      memOffsetX[] =    {0,0,0};    //Array to hold mtr memory offsets [0,1,2]=[mX] (mtr cnts).
int       mZ =              0;          //Memory #.  Array variable of memOffsetZ.
int       mX =              0;          //Memory #.  Array variable of memOffsetX.
//
float     zValNumNew;                   //Z linear distance value calculated from motor counts
float     zValNumOld =      0.0;        //used to determine if new linear distance changes sign +/-
char      zValChNew[8] =    "  0.000";  //Linear distance converted to char to minimize LCD write time 
String    zValChJoin;
int       zBufTog =         1;          //used to alternate LCD display update - saves time to update 1/2
//
float     xValNumNew;                   //x linear distance value calculated from motor counts
float     xValNumOld =      0.0;        //used to determine if new linear distance changes sign +/-
char      xValChNew[8] =    "  0.000";  //Linear distance converted to char to minimize LCD write time 
String    xValChJoin;
int       xBufTog =         1;          //used to alternate LCD display update - saves time to update 1/2
//********************Potentiometer********************
int           potPin =      A3;     //Set potentiometer pin input (wiper)
int           potNew =      2000;   //new potentiometer reading - obtained during each loop
int           potOld =      2000;   //Old pot value for "<2sec & >1cnts" to change potValue
int           potAnchor =   2000;   //Old pot value for "<2sec & >5cnts" to change potValue AND reset timer
unsigned long potTimeNew =  0;  
unsigned long potTimeOld =  0;   
//********************Spindle & Feed********************
volatile byte   spindRev;           //simple counter to keep track of 'new' count
volatile unsigned long sIndexTimeN=0; 
volatile unsigned long sIndexTimeO=0;
float     spndlRpmMax = 2060.0;     //USER INPUT: Machine limit
float     spndlRpmMin = 240.0;      //USER INPUT: Machine limit
float     spndlMaxRpmTime = (1/(spndlRpmMax*1.2))*60*1000000;   //+20% allows some beyond top entered rpm. Smallest time value.
int       inSpindPin =      13;     //Spindle sensor input pin
int       spindleRpm = 0;
int       spindleRpmOld=2;          //Saved RPM value after written to Lcd (to prevent rewriting duplicates)
float     feedRate;                 //(IPM) calculated inside displayLcdFeed function.
float     feedRateOld;              //Saved IPM value after written to Lcd (to prevent rewriting duplicates)
float     feedRateMm;               //mm/min feedrate from pot map
char      feedRateCh[5];
String    feedRateChJoin;
float     feedRateMin = 12.7;       //USER INPUT: Min feed rate mm/min (12.7=0.5 IPM)
float     feedRateMax = 1270.0;     //USER INPUT: Max feed rate mm/min (1270.0=50 IPM)
char      spindleRpmCh[5];
String    spindleRpmChJoin;
int       sRpmN;                    //New delta time for 1x spindle rev (allows neg)
int       sRpmO = 0;                //Old (saved) delta time for 1x spindle rev (allows neg)
int       sAnchor = 0;              //Saved 1x spindle rev time used for trigger to change RPM value. Protects against continuous updating
long      sElapseTimeO;        
long      sElapseTimeN;
//********************Button variables********************
int       inPinB1 =         49;     // Button #1 pin number for input.  "Top" X axis Button.
int       inPinB2 =         51;     // Button #2 pin number for input.  "Middle" Z axis Button.
int       inPinB3 =         50;     // Button #3 pin number for input.  "Bottom" A Button (General).
int       curStateB1;             
int       curStateB2;             
int       curStateB3;
int       curStateB4;           
long      millisHeldB1;        
long      millisHeldB2;        
long      millisHeldB3;
long      millisHeldB4;       
long      prevMillisHeldB1;
long      prevMillisHeldB2;
long      prevMillisHeldB3;
byte      prevStateB1 = LOW;
byte      prevStateB2 = LOW;
byte      prevStateB3 = LOW;
byte      prevStateB4=LOW;
unsigned long   startTimeB1;  
unsigned long   startTimeB2;  
unsigned long   startTimeB3;
unsigned long   startTimeB4;
unsigned long   startTimeS1;
//********************HalfNut********************
int         inPinS1 =       8;        //todo: move to void setup?  Half Nut lever switch pin assignment.
int         curStateS1;
byte        prevStateS1 =   HIGH;     //set initially to 'HIGH' to prevent motion if lever on during Arduino pwr up
const int   zMaxTravel =    1000;     //userchange: max z axis travel range (mm). Just make sure it's higher than actual.
const long  zMaxMtrCnt =    (long(zMaxTravel)*long(zMtrCntPerRev))/long(zPitch);
long        halfnutMoveDist;          //Calculated move distance when halfnut engaged (mtr cnts).
long        memStopZ[] =    {999999, 999999, 999999};  //Halfnut stop location (without memory offset) - set by button#3 hold - initial value 'null'
float       displayLinStopZ;          //Stop Z linear distance to display on LCD.
char        disLinStopChZ[7];
String      disLinStopChZJoin;
long        tempMtrPosZ;              //to save 'start' motor position when feeding
long        tempEncPosZ;              //to save 'start' encoder positon when feeding
long        tempMtrPosX;              //not used yet - to add when X feed added
long        tempEncPosX;
long        zFeedDelay;               //Delay sets the velocity
int         zFeedDelayCode =  40;     //Tested: Time code takes to loop thru per mtr pulse (us). Value must be subtracted from zFeedDelay                 
long        zFeedDelayOver;
int         zFeedDelOvCnt;
int         zFeedStepPre;             //"Pre" step to execute to create even counts required per step size.
long        actualMoveNew =   0;
long        actualMoveOld =   0;
int         zFeedStep;                //Mtr steps per cycle to send
int         mtrMinDelay =     600;    //USER INPUT: (us) Clearpath min delay/cycle spec (500+100 buffer).  Fastest at 1 step/cycle.  Note 470ok
float       zFeedStepFloat;           //exact step size required to move requested speed (10-1524mm/rev)
//********************MODES********************
int   modeCt=0;                       //Determines Modes
int   modeCtOld;
char* modeTxt[] = {"Standard Feed  ", "External Thread", "Internal Thread","Profile (Taper)","Radius (Sphere)"};
const float   Pi = 3.1415926536;      //3.1415926535897932384626433832795
//********************THREADING********************
//TODO: write thrdC391 to EEPROM & add question in mode to change... measure over pin (then calculate c391)
//TODO - remove thrdNap and replace by formula
int       tQustCt = 0;                //Counter used to determine step sequence (question) for thread operation & prevent rewrite display
float     thrdC391 = 13.860;          //USER INPUT: MEASURED!! Starrett C391 dimension, tip to edge (Drawing = 13.804905)
float     thrdAng = 27.5*Pi*180.0;    //USER INPUT: (rad) Modified flange feed angle (0.4799655 rad = 27.5 deg)
float     thrdMaxFeed = 450.0;        //Specific machine limit mm/min @ 1 Cnt/Pulse (with buffer - actual ~682)
float     thrdMaxRpm = spndlRpmMax*0.8;     //USER INPUT: 80% of machine max
float     thrdMinRpm = spndlRpmMin*1.05;    //USER INPUT: 105% of machine min
float     thrdRpm = 0.0;
float     thrdRpmRcmnd = 0.0;
float     thrdRpmActual = 0.0;
unsigned long thrdIndexTime = 0;
float     thrdRpmTemp = 0.0;
int       tSizePos = 0;               //Array position for thread Nominal Size, Pitch, ODnom, ODpitch
char*     thrdNomSize[] = {"M1.6","M2  ","M2.5","M3  ","M4  ","M5  ","M6  ","M8  ","M10 ","M12 ","M16 ","M20 ","M24 ","M30 ","#6","#8","#10","1/4","5/16","3/8","7/16","1/2","9/16","5/8","3/4","7/8","1","1.1/8"};  //Array[28]: Nominal Thread Size 'M' ISO 68 0-13.  Inch 14-27
float     thrdPitch[] = {0.35,0.40,0.45,0.50,0.70,0.80,1.00,1.25,1.50,1.75,2.00,2.50,3.00,3.50,0.793750,0.793750,1.058333,1.270000,1.411111,1.587500,1.814286,1.953846,2.116667,2.309091,2.540000,2.822222,3.175000,3.628571}; //Array[28]14+14: Pitch
float     thrdOdNom[] = {1.5385,1.9335,2.4300,2.9270,3.9080,4.9010,5.8840,7.8660,9.8500,11.8335,15.8220,19.7905,23.7645,29.7345,3.408680,4.066540,4.709160,6.219190,7.796530,9.372600,10.946130,12.523470,14.102080,15.680690,18.840450,22.000210,25.158700,28.310840}; //Array[28]14+14: OD Nominal
float     thrdOdTol[] = {0.0850,0.0950,0.1000,0.1060,0.1400,0.1500,0.1800,0.2120,0.2360,0.2650,0.2800,0.3350,0.3750,0.4250,0.152400,0.152400,0.182880,0.205740,0.220980,0.238760,0.261620,0.276860,0.289560,0.307340,0.327660,0.353060,0.381000,0.416560}; //Array[28]14+14: Full range around OD Nom
float     thrdOdPitchNom[] = {1.3225,1.6875,2.1525,2.6175,3.4780,4.4085,5.2680,7.1010,8.9280,10.7540,14.5830,18.2490,21.9030,27.5680,2.933700,3.590290,4.070350,5.449570,6.939280,8.404860,9.838690,11.328400,12.806680,14.265910,17.278350,20.262850,23.200360,26.070560};  //Array[28]14+14: OD Nom Pitch
float     thrdOdPitchTol[] = {0.0630,0.0670,0.0710,0.0750,0.0900,0.0950,0.1120,0.1180,0.1320,0.1500,0.1600,0.1700,0.2000,0.2120,0.071120,0.073660,0.083820,0.093980,0.101600,0.111760,0.119380,0.127000,0.132080,0.139700,0.149860,0.160020,0.172720,0.182880};   //Array[28]14+14: Used for MoWire
float     thrdRootMaxD1[] = {1.2020,1.5480,1.9930,2.4380,3.2200,4.1100,4.8910,6.6190,8.3440,10.0710,13.7970,17.2510,20.7040,26.1580}; //TODO remove?
float     thrdRootMinD3[] = {1.0750,1.4080,1.8400,2.2720,3.0020,3.8680,4.5960,6.2720,7.9380,9.6010,13.2710,16.6240,19.9550,25.3060};  //TODO remove?
float     thrdWire[] = {0,0,0, 0.4572, 0.4572, 0.6096, 0.6096, 0.7366, 1.0160, 1.0160, 1.1430, 1.3970, 1.6002, 2.0574,0.6096,0.6096,0.7366,0.7366,0.8128,1.0160,1.0160,1.1430,1.3970,1.3970,1.3970,1.6002,1.8288,2.0574};  //[28]14+14
float     thrdWireConst = 0.0;
float     thrdWireMic = 0.0;
int       thrdNap;                    //Thread number of passes
int       tMtlPos = 0;                //Array position for work material text, SFM
char*     thrdMtlText[] = {"Aluminum ","Brass    ","Stl LowC ","Stl MedC ","Stl HighC","Stainless","Cast Iron","Copper   ","Titanium ","Delrin   "};  //Array[10]
float     thrdMtlSfm[] = {62.0, 27.0, 27.0, 21.0, 15.0, 15.0, 19.0, 19.0, 12.0, 125.0}; //Array[10]: SFM per Mtl Text array. 
int       tTlPos = 0;
char*     thrdToolText[] = {"HSS    ","Carbide","Exit   "};
float     thrdToolVal[] = {1.0,2.5,999.0};   //HSS=1, Carbide=2.5 - used as multiplyer for RPM
float     thrdOdMeasOffset = 0.0;     //mm
float     thrdC391Offset = 0.0;       //Cnts
float     thrdTipDim = 0.0;           //Cnts
float     thrdXRetract = 0.0;         //Cnts
float     thrdZEnd = 0.0;             //Cnts
float     thrdZStart = 0.0;           //Cnts
int       thrdRapidDelay = 1000;      //Delay for all rapid moves (increase step size for faster)  
int       thrdRapidStep;              //Set in code
int       thrdPassNum = 0;            //Keeps track of pass number in 'for' loop
int       thrdAutoSpr = 2;            //USERINPUT: # automatic spring passes to perform after cut complete
int       tTotPass;                   //Used for LCD only
int       tSprCnt = 0;                //Counter to adjust lcd print of pass number (adds auto sprint)
int       thrdXDepthPos = 0;          //X-Motor position at final thread depth (Cnts) 
int       thrdInfeedTotal = 0;        //From Tool Tip on OD to final thread depth.  (maybe not reqd)
int       thrdInfeed1stPass = 0;      //Pass #1 Infeed amount [(SQRT(1) and not SQRT(nap-1)]
int       thrdInfeed = 0;             //Infeed for each NAP
int       thrdOffset1stPass = 0;      //Pass #1 Z Offset - Max Offset (also used for scratch pass)
int       thrdOffset = 0;             //Offset for each NAP.  (due to 27.5 deg infeed)
int       tNxtOpPos = 0;              //supports lcd question AFTER thread completed.
char*     thrdNextOp[] = {"=> Exit             ","=> Measure over wire","=> Spring Pass      ","=> Adjust Depth     "}; //[4]
float     thrdInfeedAdj = 0.0;        //User LCD entered value to adjust depth of cut AFTER thread complete.
int       thrdCutStep = 1;            //1=default  1cnt/pulse of motor (2 is max for now and works fine for all thrds)
float     thrdFeedRcmnd = 0.0;        //calculated based on question inputs
float     thrdFeedActual = 0.0;       //Actual feed in mm/min based on 'actual' RPM
int       thrdCutDelay = 0;           //Delay used to Cut threads (does not included program time)
int       thrdCutDelayCalc = 0;       //(ms)Calculated delay to output correct feed for thread cutting (will be adjusted "on the fly")
int       thrdCutDelayProg = 100;     //(ms)TODO: remove assignment from 3 cut function and leave measured delay here
int       thrdCutDelayAdj = 0;        //(ms)Delay adjustment calculated to sync TODO:Remove
unsigned long sIndexTimeNSaved = 0;   //used to set index trigger for Z cut move(3)
int       mtrCntsPerIndex = 0;        //Calc constant used for running subtraction to orig mtr position (to match index)
long      mtrCntOrig = 0;
long      mtrCntExpSaved = 0;         //Saves Expected cnt for running value
int       deltaCnts = 0;
int       deltaDelay = 0;
int       spindleRpm3 = 0;
int       tCount=0;                       //ToDo remove?
int       iCount=0;                       //ToDo remove?
//int       tStCutDelay[100];         //Debug only
//int       tStExpSav[100];           //Debug only
//int       tStActSav[100];           //Debug only
//int       tStDeltaCnts[100];        //Debug only
int       tRpmZero=0;
byte      spindRevSaved;
//********************TAPER********************
int       tprQustCt = 0;                //Counter used for taper operation questions
float     tprStkOD = 12.7;              //Operator input.  Measured stock OD in mm
long      tprStkRad = 0;                //Saved X motor cnt or tprStkOD.  = Center stock to tool tip 
long      tprXRetract = 0;              //Retract X Cnts from stock center
int       tprNumPnts = 3;               //Array size[0-19]: Default number of profile points. '0' not allowed => 1-19(2-20) points
long      tprZPos[] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};            //[20] 0-19
long      tprZPosOffst[] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};       //[20] 0-19
long      tprXRad[] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};            //[20] 0-19    FINAL profile X for all points
long      tprXRadOffst[] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};       //[20] 0-19    ROUGH profile X for all points
long      tprXRadRun[] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};         //[20] 0-19    MOVING profile X for all points (start=tprStkRad+Fin+1, end=trpXRad)
int       tprCutDir = 0;                //Cut direction.  Away from spindle = 0 (left->right), Toward Spindle = 1 (right->left)
int       tprArSize = 0;                //Used for setting profile positions in loop
float     tprOD = 0.0;                  //lcd print value for profile OD points
float     tprDpthCut = 0.60*(xMtrCntPerRev/xPitch);      //Default is 0.6mm~=0.024" (240 cnts)
float     tprDpthFinCut = 0.10*(xMtrCntPerRev/xPitch);   //Default is 0.1mm~=0.004" (40 cnts)
float     tprMaxDp = 0.0;               //Max depth value from stock-to-tprXRad
int       tprMaxArPos = 0;              //Max depth value array position
int       tprMaxDpOffst = 0;            //Max depth OFFSET motor position  
int       tprCntl = 0;                  //To Determine progress of loop.  0=Need more rough cuts, 1=Ready for finish pass, 2=Totally finished
int       tprRapidDelay = 700;          //Delay for all rapid moves (increase step size for faster)  
int       tprRapidStep;                 //Set in code
float     angIn;
float     angOut;
float     angRslt;
const float   zCvrt=zPitch/float(zMtrCntPerRev);        //Converts Z cnts to mm
const float   xCvrt=xPitch/float(xMtrCntPerRev);        //Converts X cnts to mm
int       tprPassTtl;
int       tprPassCrnt;
int       tprZStep;
int       tprXStep;
int       tprDelay;
float     angBeta;                      //angle used to calculate lngBeta
float     lngBeta;                      //(mm) Length of cord intersection of "in/out" angles at offset of depthFinCut
float     tprXOffmm;
float     tprZOffmm;
int       tprXRadRunMaxSave;
int       tprDeltaX;
int       tprDeltaXFull;
int       tprDeltaZ;
int       tprDeltaZFull;
int       tprSpdChange=0;
//********************RADIUS********************
int       arcQustCt = 0;                //Counter used for arc operation questions
int       arcType = 0;                  //0=Internal, 1=External, 2=Sphere (likely not sphere - just 2x external)
int       arcInsType = 0;               //0=Circular, 1=Daimond

float     arcInsRad = 5.0;              //-:mm:Dist:Bttn:   Nose radius of insert (round lists IC but take 1/2)
float     arcInsRadDisp = 0.0;          //-:mm:Dist:Calc:   Used only to display arcInsRad (to accomodate Dia/Rad)
long      arcInsRadCntX = 0;            //X:Cnt:Dist:Calc:  Tool Radius in counts on X axis (rounded up)
long      arcInsRadCntZ = 0;            //Z:Cnt:Dist:Calc:  Tool Radius in counts on Z axis (rounded up)

float     arcStkOD = 25.4;              //X:mm:Dist:Bttn:   Measurement of ANY stock OD (25.4 is initial display)
long      arcStkRad = 0;                //X:Cnt:Pnt:Pos:    X axis mtr cnt @ arcStkOD.  = Center stock to tool tip position
long      arcStkCntr = 0;               //X:Cnt:Pnt:Calc:   X axis mtr cnt @ center line of part.  =Tool tip at center axis of stock

long      arcTngFace = 0;               //Z1:Cnt:Pnt:Pos:   Z axis mnt cnt position @ arc tangent to face (tool touch position)
long      arcMaxStk = 0;                //XA:Cnt:Pnt:Pos:   X axis mnt cnt position @ max stock positon (start of real cutting)

long      arcRadCntrZ = 0;              //Z2:Cnt:Pnt:Pos:   Z axis mnt cnt @ arc rad center by moving Z axis mtr cnts away from previous "touch" face
long      arcRadCntrX = 0;              //XC:Cnt:Pnt:Calc:  X axis mnt cnt @ arc rad center by calc (***after arcTngOdRad is determined)
long      arcRadCutSzZ = 0;             //Z:Cnt:Dist:Calc:  Saved value of arc radius size in cnts Z (Radius which tool travels over - not real radius)
long      arcRadCutSzX = 0;             //X:Cnt:Dist:Calc:  Saved value of arc radius size in cnts X (Radius which tool travels over - not real radius)
int       arcRadOffSzZ;                 //X:Cnt:Dist:Calc:  Saved value of Tangent to radius center (temp # during move to find rad)
float     arcRadDisp = 0.0;             //-:mm:Dist:Calc    Arc Radius to display in mm

long      arcTngOdRad = 0;              //XB:Cnt:Pnt:Bttn:  Button Input (mtr cnt): to choose OD arc is tangent with (min OD for int & max OD for ext)
float     arcTngOdDisp = 0;             //-:mm:Dist:Calc:   OD to display on LCD

int       arcCnt = 0;                   //Counter for incremental input
float     arcCntDisp = 0;               //-:mm:Dist:Bttn:   Distance for offsets (z and x)
long      arcTngOdExt = 0;              //Z3:Cnt:Dist:Bttn:  Button Input (Z mtr cnt): to define profile extension along OD
long      arcFaceExt = 0;               //XD:Cnt:Dist:Bttn:  Button Input (X mtr cnt): to define face extension along face (or retract "Dumbbell")

int       arcCutDir = 0;                //Calc:  Cut direction.  Away from spindle = 0 (left->right), Toward Spindle = 1 (right->left)

long      arcDpthCutX = 0.60*(xMtrCntPerRev/xPitch);  //(240 cnts) Default is 0.60mm~=0.024"
long      arcDpthCutZ = arcDpthCutX*xPitch/zPitch;    //used only for adjusting arc
long      arcXFin = 0.10*(xMtrCntPerRev/xPitch);      //(40  cnts) Default is 0.10mm~=0.004"
long      arcZFin = arcXFin*xPitch/zPitch;            //For Z offset TODO: check what is used on taper z offset.

int       arcArSize = 8;
long      arcXFinAr[] = {0,0,0,0,0,0,0,0};      //8 points (0-7)
long      arcZFinAr[] = {0,0,0,0,0,0,0,0};      //8 points (0-7)
long      arcXOffAr[] = {0,0,0,0,0,0,0,0};      //8 points (0-7)
long      arcZOffAr[] = {0,0,0,0,0,0,0,0};      //8 points (0-7)
long      arcX[] =      {0,0,0,0,0,0,0,0,0};    //9 = 8 points + Rad (0-8)
long      arcZ[] =      {0,0,0,0,0,0,0,0,0,0};  //10 = 8 points + Rad + Rad45 (0-9)
long      arcRunStrt = 0;
long      arcRunRad = 0;
long      arcRunEnd = 0;

int       arcRapidDelay = 700;          //Delay for all rapid moves (increase step size for faster)  
int       arcRapidStep;                 //Set in code
int       arcXStep;
int       arcZStep;
int       arcDelay=1000;                //TODO****************** remove 1000 and insert function
int       arcDelayCode=140;             //TODO - test and assign
int       arcSpdChange=0;               //TODO - assign

int       arcCntl = 0;                  //To determine rough/finish/modify
int       arcRadCtRdy=0;                //To determine if prior "run" is completed so that next "run" can occur
int       arcPassTtl;
int       arcPassCrnt;

int       arcXStpRad;                   //Steps to move X per cycle
int       arcZStpRad;                   //Steps to move Z per cycle
float     arcXStpRun;                   //Tracks total X value around arc (with remainder)
float     arcZStpRun;                   //Tracks total Z value around arc (with remainder)
int       arcXStpActual;                //Keeps track of actual moved X full steps
int       arcZStpActual;                //Keeps track of actual moved Z full steps

int       aNxtOpPos=0;                  //supports lcd question AFTER arc completed.
char*     arcNextOp[] = {"=> Exit             ","=> Adjust Radius Pos","=> Mirror Ext Radius","=> Spring Pass      "}; //[4]

int       arcZOffset=0;                 //Adjust arc pass Z input - running value goes back to '0'
int       arcXOffset=0;                 //Adjust arc pass X input - running value goes back to '0'
int       arcZOffAct=0;                 //Actual Z offset sent to calc - accumulates by increments of d.o.c finish
int       arcXOffAct=0;                 //Actual X offset sent to calc - accumulates by increments of d.o.c finish
//-*-*-*-*  arcDpthCut & arcDpthFinCut(s) should be int or long !!! check tpr also.
//TODO: check all int/or/long
//*********************************************************
//*********************************************************
void setup()
{
  Serial.begin(9600);
  Serial.println("START:");
  
  Z.attach(22,23,27);       //ClearPath: Must use 22-29 on Mega.
  Z.enable();               //Clearpath: Enable motor, reset the motor position to 0
  X.attach(24,25,26);       //ClearPath: Must use 22-29 on Mega.
  X.enable();               //Clearpath: Enable motor, reset the motor position to 0
  machine.Start(249);       //Clearpath: Set up ISR to constantly check motor position.  PARAMETER MUST BE SET TO 249
  
  //Print LCD static feilds ONLY ONCE
  lcd.begin(40,4);          //sets display columns x rows
  lcd.clear();              //clear the display
  lcd.print("X =");
  lcd.setCursor(0,1);
  lcd.print("Z =");
  lcd.setCursor(18,0);
  lcd.print("M");
  lcd.setCursor(18,1);
  lcd.print("M");
  lcdFeedDispBasic();      //Initially populate "Feed" (Standard Mode) basics

  //Set Buttons and other pins
  digitalWrite(inPinB1, LOW);
  digitalWrite(inPinB2, LOW);
  digitalWrite(inPinB3, LOW);
  pinMode(13, INPUT);

  //creates interrupt pin for spindle
  digitalWrite(13, HIGH);
  enableInterrupt(13,spindRevCount,RISING);

  //Populate LCD values
  displayLcdBasicsXZ();     //Populate X & Z values
  displayLcdStop();         //Initially populates with 'not set'
  displayLcdSpeed();
}
//*********************************************************
void loop() 
{
  zEnc();             //Needs buffer cnt to initiate function
  xEnc();             //Needs buffer cnt to initiate function
  potentiometer();    //Read Pot pin:  Needs >5 to initiate function
  spindIndex();       //Change in index time > 10RPM to initiate function.
  zMotorFeed();       //Read Halfnut pin: High to initiate function.
  stdButtons();       //Read 3 buttons: High to initiate function.
  modeSetup();        //if modecnt>998 to initiate function
  extThrdSetup();     //if modeCnt=1 to initiate function
  taperSetup();       //if modeCnt=3 to initiate function
  arcSetup();         //if modeCnt=4 to initiate function
}
