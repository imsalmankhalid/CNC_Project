//*********************************************************
//  taperSetup()  tprMove()  zTprProfile()  xTprRetract()  zTprToStart()  TprOffsetCalc()
//*********************************************************
void taperSetup() 
{
  if(modeCt==3)
  {
//________________________________________________
    if(tprQustCt==0)    //Turn Stock OD & Measure.
    {
      lcd.setCursor(0,2);
      lcd.print("Set Tool on stock OD");
      lcd.setCursor(0,3);
      lcd.print("Stock OD =          ");
//                          xxx.xxx
//                          xx.xxxx
      tprQustCt=1;      
    }
    if(tprQustCt==1)
    {
      lcd.setCursor(11,3);
      if(unitConverter==1.0) 
      {
        if(tprStkOD >= 100.0)
        {
          lcd.setCursor(11,3);
          lcd.print(tprStkOD, 3);
        }
        else if(tprStkOD < 100.0 && tprStkOD >= 10.0)
        {
          lcd.setCursor(11,3);
          lcd.print(" ");
          lcd.print(tprStkOD, 3);
        }
        else
        {
          lcd.setCursor(11,3);
          lcd.print("  ");
          lcd.print(tprStkOD, 3);
        }
      }
      else
      {
        if((tprStkOD/25.4) >= 10.0)
        {
          lcd.setCursor(11,3);
          lcd.print((tprStkOD/unitConverter), 4);
        }
        else
        {
          lcd.setCursor(11,3);
          lcd.print(" ");
          lcd.print((tprStkOD/unitConverter), 4);          
        }
      }
      tprQustCt=2;
    }
    if(tprQustCt==2) 
    {
      modeButtons();
      zMotorFeed();
    }
    if(tprQustCt==3)
    {
      tprStkRad = mtrNewPosX;   //tprStkOD (mm) is now related to tprStkRad (mtr cnts)
      tprMaxDp = tprStkRad;
      tprMaxDpOffst = tprStkRad;
      tprQustCt=4;
    }
//________________________________________________
    if(tprQustCt==4)   //Set X Taper Retract Pos
    { 
      lcd.setCursor(0,2);
      lcd.print("Set X Retract Pos   ");
      lcd.setCursor(0,3);
      lcd.print("B3 when done        ");
      tprQustCt=5;
    }
    if(tprQustCt==5) 
    {
      tprXRetract = mtrNewPosX;
      modeButtons();
    }
    if(tprQustCt==6)
    {
      if(tprXRetract < (tprStkRad+(1.0/(xPitch/float(xMtrCntPerRev)))))      //Min 1.0 mm retract
      {
        lcd.setCursor(0,3);
        lcd.print("Retract NOK   > 1 mm");
        delay(2000);
        tprQustCt=4;
      }
      else
      {
        tprQustCt=7;
      }
    }
//________________________________________________
    if(tprQustCt==7)   //Choose number of points on profile
    {
      lcd.setCursor(0,2);
      lcd.print("# points on profile?");
      lcd.setCursor(0,3);
      lcd.print(" =                  ");
      tprQustCt=8;
    }
    if(tprQustCt==8)
    {
      lcd.setCursor(3,3);
      lcd.print("  ");
      lcd.setCursor(3,3);
      lcd.print(tprNumPnts+1);
      tprQustCt=9;
    }
    if(tprQustCt==9) modeButtons();
//________________________________________________
    if(tprQustCt==10)   //Choose cut direction
    {
      lcd.setCursor(0,2);
      lcd.print("Direction of Cut?   ");
      lcd.setCursor(0,3);
      lcd.print("                    ");
      lcd.setCursor(0,3);
      if(tprCutDir==0) lcd.print("Right -> Away Spndl ");
      if(tprCutDir==1) lcd.print("Left  <- Into Spndl ");       
      tprQustCt=11;
    }
    if(tprQustCt==11) modeButtons();
//________________________________________________
    if(tprQustCt==12)     //Set Profile Points
    {
      for(int tpri = 0; tpri < 10; tpri++)    //todo: change to max array size?
      {
        tprXRad[tpri] = tprStkRad;            //Safety: Sets all radius array sizes to stock OD
      }
      tprArSize = tprNumPnts;                 //Sets array size to controlled variable
      tprNumPnts = 0;                         //Sets array position to '0' start
      tprQustCt=13;
    }
    if(tprQustCt==13 && tprNumPnts <= tprArSize)
    {
      lcd.setCursor(0,2);
      lcd.print("Set Z   Axis Pos.   ");
      lcd.setCursor(0,3);
      lcd.print("& Enter OD =        ");
      lcd.setCursor(5,2);
      lcd.print(tprNumPnts+1);
      tprQustCt=14;
    }
    if(tprQustCt==14 && tprNumPnts <= tprArSize)
    {
      tprOD = tprStkOD-((tprStkRad-tprXRad[tprNumPnts])*2.0*(xPitch/float(xMtrCntPerRev)));
      if(unitConverter==1.0)
      {
        if(tprOD >= 10.0)
        {
          lcd.setCursor(13,3);
          lcd.print(tprOD, 3);
        }
        else
        {
          lcd.setCursor(13,3);
          lcd.print(" ");
          lcd.print(tprOD, 3);
        }
      }
      else 
      {
        lcd.setCursor(13,3);
        lcd.print((tprOD/unitConverter), 4);
      }
      tprQustCt=15;
    }
    if(tprQustCt==15) modeButtons();
    if(tprQustCt==16)
    {
      //Check if Z position is incorrect vector direction (message NOK and retry by setting tprQustCt=13)
      if((tprNumPnts > 0 && tprCutDir==0 && mtrNewPosZ > tprZPos[tprNumPnts-1]) || (tprNumPnts > 0 && tprCutDir==1 && mtrNewPosZ < tprZPos[tprNumPnts-1]))
      {
        lcd.setCursor(0,3);
        lcd.print("Z Pos NOK:          ");
        if(tprCutDir==0) lcd.print("-> Right");
        else lcd.print("<- Left ");
        delay(2000);
        tprQustCt=13;
      }
      //Check if duplicate point: nok
      else if(tprNumPnts > 0 && mtrNewPosZ==tprZPos[tprNumPnts-1] && mtrNewPosX==tprXRad[tprNumPnts-1])
      {
        lcd.setCursor(0,3);
        lcd.print("Duplicate Pnt!! NOK ");
        delay(2000);
        tprQustCt=13;
      }
      //Note: Radius is controlled by button input selection to not allow radius > stock
      else          //Position Z & radius is OK so set values
      {
        tprZPos[tprNumPnts] = mtrNewPosZ;                 //Stores Array Z position (z-cnts)
        //Note: tprXRad is set by LCD & operator input (x-cnts) - does not capture actual x axis position
        if((tprStkRad-tprXRad[tprNumPnts]) > tprMaxDp)    //Keep track of max cut depth value (# counts) & array pos TODO:needed now??
        {
          tprMaxDp = tprStkRad-tprXRad[tprNumPnts];
          tprMaxArPos = tprNumPnts;
        }
        tprNumPnts++;                                     //Increase array count
        if(tprNumPnts <= tprArSize) tprQustCt = 13;       //AND determine if another profile point required to record
        else tprQustCt = 17;                              //OR finish
      }
    }
//________________________________________________
    if(tprQustCt==17)    //Depth of Cut (Roughing)
    {
      lcd.setCursor(0,2);
      lcd.print("Enter Roughing D.O.C");
      lcd.setCursor(0,3);
      lcd.print("Depth =             ");
      tprQustCt=18;
    }
    if(tprQustCt==18)
    {
      lcd.setCursor(8,3);
      if(unitConverter==1) lcd.print((tprDpthCut*(xPitch/float(xMtrCntPerRev))), 2);
      else lcd.print(((tprDpthCut*(xPitch/float(xMtrCntPerRev)))/unitConverter), 3);
      tprQustCt=19;
    }
    if(tprQustCt==19) modeButtons();
//________________________________________________
    if(tprQustCt==20)    //Depth of Cut (Finish)
    {
      if(tprDpthFinCut >= tprDpthCut) tprDpthFinCut=tprDpthCut-10;    //prevents finish > rough to begin
      lcd.setCursor(0,2);
      lcd.print("Enter Finish D.O.C. ");
      lcd.setCursor(0,3);
      lcd.print("Depth =             ");
      tprQustCt=21;
    }
    if(tprQustCt==21)
    {
      lcd.setCursor(8,3);
      if(unitConverter==1) lcd.print((tprDpthFinCut*(xPitch/float(xMtrCntPerRev))), 2);
      else lcd.print(((tprDpthFinCut*(xPitch/float(xMtrCntPerRev)))/unitConverter), 3);
      tprQustCt=22;
    }
    if(tprQustCt==22) modeButtons();
//________________________________________________
    if(tprQustCt==23)     //Pause to set RPM & Feed ("void loop" potentiometer & spindIndex allows tprQustCt==23)
    {
      potentiometer();
      delay(500);       //Todo remove??
      calcSpeed();
      displayLcdSpeed();
      calcFeed();
      displayLcdFeed();
      lcd.setCursor(0,2);
      lcd.print("Set RPM & Feed Rate ");
      lcd.setCursor(0,3);
      lcd.print("RPM=      IPM=      ");
      lcd.setCursor(5,3);
      lcd.print(spindleRpmChJoin);
      lcd.setCursor(15,3);
      lcd.print(feedRateChJoin);
      modeButtons();
    }
//________________________________________________
    if(tprQustCt==24)   //Profile READY!  Toggle HalfNut Mssg
    {
      lcd.setCursor(0,2);
      lcd.print("Profile is ready    ");     
      lcd.setCursor(0,3);
      lcd.print("Engage Half Nut...  ");
      tprQustCt=25;
    }
    if(tprQustCt==25) tprMove(); 
  }
}
//*********************************************************
void tprMove()    //Profile main loop
{

  //Serial.print("tprStkOD (mm) = "); Serial.println(tprStkOD);
  //Serial.print("tprStkRad (xcnts) = "); Serial.println(tprStkRad);
  //Serial.print("tprXRetract (xcnts) = "); Serial.println(tprXRetract);
  //Serial.print("tprArSize = "); Serial.println(tprArSize);
  for(int tprj = 0; tprj <= tprArSize; tprj++)
  {
    //Serial.print("tprZPos["); Serial.print(tprj); Serial.print("] = "); Serial.print(tprZPos[tprj]);
    //Serial.print("       ");
    //Serial.print("tprXRad["); Serial.print(tprj); Serial.print("] = "); Serial.println(tprXRad[tprj]);
  }
  //Serial.println("");

  tempEncPosZ=encNewPosZ;   //save current Z encoder cnts
  tempEncPosX=encNewPosX;   //save current X encoder cnts

  TprOffsetCalc(); //Populates radius & Zpos arrays with profile offsets.  TODO: add 0.002" to last rough pass to prevent rubbing.
  for(int tprk = 0; tprk <= tprArSize; tprk++)  //Populate all "Run" array positions with stk rad.  Will continuously subtract each cut pass depth until 'run' = tprXRad
  {
    tprXRadRun[tprk]=tprStkRad+tprDpthFinCut+10;  //Forces "start" of all profile points outside stock+fin+10cnts.
    tprCntl=0;
  }
  tprXRadRunMaxSave=tprStkRad+tprDpthFinCut+10; //Save off original max - Used only to determine number of passes

  while(modeCt==3 && tprCntl < 4 && tprQustCt >= 25 && tprQustCt <= 27)
  {
    curStateS1 = digitalRead(inPinS1);        //Checks current halfnut lever status
    if(curStateS1==LOW) prevStateS1=LOW;      //IF Halfnut lever is OFF, set prevStateS1=LOW -> reset to allow another feed.
    if(curStateS1 == HIGH && prevStateS1 == LOW) delay(50);   //Debouce
    curStateS1 = digitalRead(inPinS1);
    if(curStateS1 == HIGH && prevStateS1 == LOW)              //Run 2nd time just to be sure we want to move
    {
      if(tprQustCt==25)                     //Set tool to "start"
      {
        prevStateS1=HIGH;
        lcd.setCursor(5,0);
        lcd.print("--------");
        lcd.setCursor(5,1);
        lcd.print("--------");
        lcd.setCursor(0,2);
        lcd.print("Profile Run/B3:Pause");
        lcd.setCursor(0,3);
        lcd.print("Moving to start...  ");
        xTprRetract();
        zTprToStart();  
        tprQustCt=26;
        lcd.setCursor(0,3);
        lcd.print("Re-Engage Half Nut..");
      }
      else if(tprQustCt==26)                //Profile Rough ONLY
      {
        prevStateS1=HIGH;
        
        lcd.setCursor(0,3);
        lcd.print("Pass     of         ");
        tprPassTtl=round(0.49+1.0+(abs(tprXRadRunMaxSave-tprXRadOffst[tprMaxArPos])/tprDpthCut));       //0.49 is remainder rough & 1.0 is finish pass
        lcd.setCursor(12,3);
        lcd.print("   ");
        lcd.setCursor(12,3);
        lcd.print(tprPassTtl); 
          
        while(tprCntl==0)
        {
          //Serial.println(""); Serial.print("Rough Pass "); Serial.println(tprPassCrnt+1);
          for(int tpro = 0; tpro <= tprArSize; tpro++)  //subtract rough cut depth (or remainder) from running rad array (tprZRadRun starts at stk rad + Fin + 10)
          {
            if((tprXRadRun[tpro]-tprXRadOffst[tpro]) >= tprDpthCut)  tprXRadRun[tpro]=tprXRadRun[tpro]-tprDpthCut; //set rough cut depth
            else if((tprXRadRun[tpro]-tprXRadOffst[tpro]) < tprDpthCut && (tprXRadRun[tpro]-tprXRadOffst[tpro]) > 0) tprXRadRun[tpro]=tprXRadOffst[tpro]; //set remainder cut depth
            if(tprCntl==0 && tpro==tprMaxArPos && tprXRadRun[tpro]==tprXRadOffst[tpro]) tprCntl=1;   //Stops Roughing calc... last one
            //Serial.print("  Point "); Serial.print(tpro);
            //Serial.print("  X mtr pos = "); Serial.println(tprXRadRun[tpro]);
          }

          if(tprCntl==0) tprPassCrnt=tprPassTtl-round(0.49+1.0+abs((tprXRadRun[tprMaxArPos]-tprXRadOffst[tprMaxArPos])/tprDpthCut));    //TODO: tprMaxDpOffst is actually tprXRad[tprMaxArPos} -> replace all
          else if(tprCntl==1) tprPassCrnt=tprPassTtl-1;
          lcd.setCursor(5,3);
          lcd.print("   ");
          lcd.setCursor(5,3);
          lcd.print(tprPassCrnt);

          zTprProfile();
          xTprRetract();
          zTprToStart();
        }
        tprQustCt=27;
        lcd.setCursor(0,2);
        lcd.print("Ready for Finish    ");     
        lcd.setCursor(0,3);
        lcd.print("Re-Engage Half Nut..");
        //Serial.println(""); Serial.println("Finish Pass");
      }
      
      else if(tprQustCt==27 && tprCntl==2)                //Profile Finish ONLY
      {
        prevStateS1=HIGH;
        
        lcd.setCursor(0,2);
        lcd.print("Profile Run - Finish");

        lcd.setCursor(0,3);
        lcd.print("Pass     of         ");
        tprPassTtl=round(0.49+1.0+(abs(tprXRadRunMaxSave-tprXRadOffst[tprMaxArPos])/tprDpthCut));       //0.49 is remainder rough & 1.0 is finish pass
        lcd.setCursor(12,3);
        lcd.print("   ");
        lcd.setCursor(12,3);
        lcd.print(tprPassTtl); 

        tprPassCrnt=tprPassTtl;
        lcd.setCursor(5,3);
        lcd.print("   ");
        lcd.setCursor(5,3);
        lcd.print(tprPassCrnt);



        for(int tproo = 0; tproo <= tprArSize; tproo++)
        {
          tprXRadRun[tproo]=tprXRad[tproo];
          tprZPosOffst[tproo]=tprZPos[tproo];
          //Serial.print("  Point "); Serial.print(tproo);
          //Serial.print("  X mtr pos = "); Serial.println(tprXRadRun[tproo]);
        }

        tprCntl=3;
        
        zTprProfile();
        xTprRetract();
        zTprToStart();
          
        tprQustCt=28;
      }
    }
    
  }
  //After 'while' write encoder X & Z to prevent movement from encoder changes
  zAxisEnc.write(tempEncPosZ);
  encNewPosZ=tempEncPosZ;
  encOldPosZ=tempEncPosZ;  
  xAxisEnc.write(tempEncPosX);
  encNewPosX=tempEncPosX;
  encOldPosX=tempEncPosX; 
  modeCt=999;
}
//*********************************************************
void zTprProfile()          //Move thru entire profile points (Z & X motions)
{
  int  tprDelayCode=140;   //ToDo: test and adjust... tested ~140 with stop watch  Todo: move up to variables
  if(tprSpdChange==0)
  {
    tprDelay=(1/(((feedRateMm)/zPitch)*float(zMtrCntPerRev)))*(60*1000000)-tprDelayCode;     //=us/cnt:  TODO: watch for 5/2 ratio chg on psudo step
    tprSpdChange=2;
  }
  else if(tprSpdChange==1)
  {
    tprResetSpeed();
    tprDelay=(1/(((feedRateMm)/zPitch)*float(zMtrCntPerRev)))*(60*1000000)-tprDelayCode;
    tprSpdChange=2;
  }
  
  float tprZPsuStepSize=1.0;                                  //Defines 'Psudo' Z step size. Was (=xPitch/zPitch)or(2/5)=0.4... todo: If 1 nok, change to 0.5 (half step)
  float tprZPsuStep=tprZPsuStepSize;                          //Sets first step size.  This value gets added to every loop and subtract actual step size taken
  float tprXPsuStepSize;                                      //Defines 'Psudo' X step.... calculated later
  float tprXPsuStep;                                          //Define 'Psudo' X Step.... assigned later. STARTS @ ratio of x&z full steps :to: x&z step size per cycle.
  int tprZTrigStrt;                                           //Define 'Trigger' Z motor start positon
  int tprZTrigEnd;                                            //Define 'Trigger' Z motor end position
  
  for(int tprp = 0; tprp <= tprArSize; tprp++)                //Define 'Psudo' X step. More complicated
  {
    if(tprp > 0)                          //'0' never has a psudo step (Pure Z or X moves).
    {
      tprDeltaXFull=tprXRad[tprp]-tprXRad[tprp-1];            //resultant sign = direction X motor needs to move.  (-)=intoPart, (+)=retract
      tprDeltaZFull=tprZPos[tprp]-tprZPos[tprp-1];            //TODO**lastPassNOK   resultant sign = direction Z motor needs to move.  (-)=right, (+)=left
      
      tprDeltaX=tprXRadRun[tprp]-tprXRadRun[tprp-1];                  //(-)=intoPart, (+)=retract.  Does both rough & finish as tprXRadRun set =tprXRad for finish
      tprDeltaZ=int((float(tprDeltaZFull)*float(tprDeltaX))/float(tprDeltaXFull));      //Calculated: # Z Cnts which require cooresponding X Cnts

      tprXPsuStepSize=abs(tprZPsuStepSize*tprDeltaXFull)/abs(tprDeltaZFull);        //Size of X step per cycle
      tprXPsuStep=tprXPsuStepSize+0.1;                          //Sets original X step size.  Add a bit to avoid rounding errors. This accumulates

      //Define at what point to start moving the x axis.  Right away for x 'infeed' while wait to special z position when x 'retract'
      if(tprDeltaXFull < 0) tprZTrigStrt=tprZPosOffst[tprp-1];        //Z Position to start X feed
      else if(tprDeltaXFull > 0) tprZTrigStrt=tprZPosOffst[tprp]-tprDeltaZ;
      tprZTrigEnd=tprZTrigStrt+tprDeltaZ;

      /*Serial.println(""); 
      Serial.print("Point# "); Serial.println(tprp);
      Serial.print("DeltaXFull= "); Serial.print(tprDeltaXFull); Serial.print(" DeltaZFull= "); Serial.println(tprDeltaZFull); 
      Serial.print("  tprDeltaX= "); Serial.print(tprDeltaX); Serial.print("  tprDeltaZ= "); Serial.println(tprDeltaZ);
      Serial.print("XPsuStepSize= "); Serial.print(tprXPsuStepSize); Serial.print(" XPsuStep= "); Serial.println(tprXPsuStep);
      Serial.print("zMtrPosNow = "); Serial.println(mtrNewPosZ);
      Serial.print("ZTrigStart = "); Serial.print(tprZTrigStrt); Serial.print(" ZTrigEnd = "); Serial.println(tprZTrigEnd);
      Serial.println("");
      */
    }
    else tprXPsuStep=0;
    
    //Move X only if profile point does not require Z motion
    if((mtrNewPosZ==tprZPosOffst[tprp] && (tprCntl==0 || tprCntl==1)) || (mtrNewPosZ==tprZPos[tprp] && tprCntl==3))     
    {
      while(mtrNewPosX!=tprXRadRun[tprp])
      {
        delayMicroseconds(tprDelay);
        if(mtrNewPosX > tprXRadRun[tprp]) tprXStep=-1;
        else tprXStep=1;
        X.move(tprXStep);
        mtrNewPosX=mtrOldPosX+tprXStep;
        mtrOldPosX=mtrNewPosX;
        curStateS1 = digitalRead(inPinS1);
        if(curStateS1 == LOW) modeCt=999;                         //Dump out if halfnut disengaged too early       
      }
    }
    
    //Move Z only OR Z&X together
    else
    {
      while(mtrNewPosZ!=tprZPosOffst[tprp] && (tprCntl==0 || tprCntl==1 || tprCntl==3))     //TODO:Remove all tprCntl   Captures both rough & finish as offst set to max at finish
          //WAS... while((mtrNewPosZ!=tprZPosOffst[tprp] && (tprCntl==0 || tprCntl==1)) || (mtrNewPosZ!=tprZPos[tprp] && tprCntl==3))
      {
        delayMicroseconds(tprDelay);                              //Delay sets velocity
  
        if(tprCutDir==0) tprZStep=int(-tprZPsuStep);              //Changing to int removes remainder
        else tprZStep=int(tprZPsuStep);
        Z.move(tprZStep);                                         //Move Z motor
        tprZPsuStep=tprZPsuStep-abs(tprZStep);                    //will subtract 0 until step reaches >=1
        tprZPsuStep=tprZPsuStep+tprZPsuStepSize;                  //Add PsuSize (0.4, static for all profile points)
        mtrNewPosZ = mtrOldPosZ+tprZStep;                         //Calculates where motor is (cnt) from absolute (machine start)
        mtrOldPosZ=mtrNewPosZ;                                    //don't know why i keep tracking old pos but i do

        if((tprDeltaX!=0 && tprCutDir==0 && mtrNewPosZ <= tprZTrigStrt && mtrNewPosZ > tprZTrigEnd)
            || (tprDeltaX!=0 && tprCutDir==1 && mtrNewPosZ >= tprZTrigStrt && mtrNewPosZ < tprZTrigEnd))
        {
          if(tprDeltaXFull < 0) tprXStep=int(-tprXPsuStep);       //Changing to int removes remainder TODO:Adjust delay if Xstep>1 OR drive with X
          else tprXStep=int(tprXPsuStep);
          X.move(tprXStep);
          tprXPsuStep=tprXPsuStep-abs(tprXStep);          //will subtract 0 until step reaches >=1.  >1.9 step size is problem for speed
          tprXPsuStep=tprXPsuStep+tprXPsuStepSize;        //Add PsuSize (calculated per profile point)
          mtrNewPosX = mtrOldPosX+tprXStep;
          mtrOldPosX = mtrNewPosX;
        }
        
        curStateS1 = digitalRead(inPinS1);
        if(curStateS1 == LOW) modeCt=999;                         //Dump out if halfnut disengaged too early
      }
    }
  }
}
//*********************************************************
void xTprRetract()    //X Motor move to the retract position
{ 
  while(mtrNewPosX != tprXRetract)
  {
    if(mtrNewPosX < tprXRetract) tprRapidStep=1;          //Fine move +cnts (-linear value)
    if(mtrNewPosX > tprXRetract) tprRapidStep=-1;         //Fine move -cnts (+linear value)
    if((mtrNewPosX+20) < tprXRetract) tprRapidStep=3;     //Rapid move +cnts (-linear value)
    if((mtrNewPosX-20) > tprXRetract) tprRapidStep=-3;    //Rapid move -cnts (+linear value)
    resetButton();
    delayMicroseconds(tprRapidDelay);                     //Delay sets velocity
    X.move(tprRapidStep);                                 //Move x motor
    mtrNewPosX = mtrOldPosX+tprRapidStep;                 //Calculates where motor is (cnt) from absolute (machine start)
    mtrOldPosX = mtrNewPosX;                              //don't know why i keep tracking old pos but i do
    curStateS1 = digitalRead(inPinS1);
    if(curStateS1 == LOW) modeCt=999;                     //Dump out if halfnut disengaged too early
  }
}
//*********************************************************
void zTprToStart()     //Z Motor return to start of profile with pause for speed/depth change
{
  while((mtrNewPosZ!=tprZPosOffst[0] && tprCntl==0) || (mtrNewPosZ!=tprZPos[0] && (tprCntl==1 || tprCntl==3)))  //covers both rough & finish positions
  {
    if(tprCntl==0 && mtrNewPosZ > tprZPosOffst[0]) tprRapidStep=-1;       //Fine move +cnts     
    if(tprCntl==0 && mtrNewPosZ < tprZPosOffst[0]) tprRapidStep=1;        //Fine move +cnts
    if(tprCntl==0 && mtrNewPosZ >= (tprZPosOffst[0]+20)) tprRapidStep=-3;   //Rapid move +cnts
    if(tprCntl==0 && mtrNewPosZ <= (tprZPosOffst[0]-20)) tprRapidStep=3;    //Rapid move +cnts
    //----------
    if((tprCntl==1 || tprCntl==3) && mtrNewPosZ > tprZPos[0]) tprRapidStep=-1;            //Fine move +cnts     
    if((tprCntl==1 || tprCntl==3) && mtrNewPosZ < tprZPos[0]) tprRapidStep=1;             //Fine move +cnts
    if((tprCntl==1 || tprCntl==3) && mtrNewPosZ >= (tprZPos[0]+20)) tprRapidStep=-3;        //Rapid move +cnts
    if((tprCntl==1 || tprCntl==3) && mtrNewPosZ <= (tprZPos[0]-20)) tprRapidStep=3;         //Rapid move +cnts
     
    resetButton();
    delayMicroseconds(tprRapidDelay);                         //Delay sets velocity
    Z.move(tprRapidStep);                                     //Move x motor
    mtrNewPosZ = mtrOldPosZ+tprRapidStep;                     //Calculates where motor is (cnt) from absolute (machine start)
    mtrOldPosZ=mtrNewPosZ;                                    //don't know why i keep tracking old pos but i do
    curStateS1 = digitalRead(inPinS1);
    if(curStateS1 == LOW) modeCt=999;                         //Dump out if halfnut disengaged too early
  }
  if(tprCntl==1) tprCntl=2;   //from rought-last-pass to finish-calc
  if(tprCntl==3) tprCntl=4;   //from finish-pass to STOP
}
//*********************************************************
void TprOffsetCalc()    //Calculate profile point offset in Z (X being finish depth)
{
  for(int tpriii=0; tpriii <= tprArSize; tpriii++)
  {
    //--------------------Determine Angle IN--------------------
    if(tpriii==0 && tprXRad[tpriii] < tprStkRad) angIn=Pi;                                    //180 (0.pt Both)
    else if(tprCutDir==0 && tpriii==0 && tprXRad[tpriii]==tprStkRad) angIn=Pi*0.5;            //90 (0.pt Left)
    else if(tprCutDir==1 && tpriii==0 && tprXRad[tpriii]==tprStkRad) angIn=Pi*1.5;            //270 (0.pt Right)
    
    else if(tprCutDir==0 && (tprZPos[tpriii-1]-tprZPos[tpriii])==0 && tprXRad[tpriii-1] < tprXRad[tpriii]) angIn=Pi*0.0;   //0   Left
    else if(tprCutDir==1 && (tprZPos[tpriii-1]-tprZPos[tpriii])==0 && tprXRad[tpriii-1] < tprXRad[tpriii]) angIn=Pi*2.0;   //360 Right
    
    else if((tprZPos[tpriii-1]-tprZPos[tpriii])==0 && tprXRad[tpriii-1] > tprXRad[tpriii]) angIn=Pi;        //180 Both in/out
    else if((tprXRad[tpriii-1]-tprXRad[tpriii])==0 && tprZPos[tpriii-1] > tprZPos[tpriii]) angIn=Pi*0.5;    //90 Can only happen Dir=0
    else if((tprXRad[tpriii-1]-tprXRad[tpriii])==0 && tprZPos[tpriii-1] < tprZPos[tpriii]) angIn=Pi*1.5;    //270 Can only happen Dir=1
    
    else if(tprXRad[tpriii-1] < tprXRad[tpriii] && tprZPos[tpriii-1] > tprZPos[tpriii])                     //0+
      angIn=(Pi*0.0)+abs(atan(((tprZPos[tpriii-1]-tprZPos[tpriii])*zCvrt)/(xCvrt*(tprXRad[tpriii-1]-tprXRad[tpriii]))));
    else if(tprXRad[tpriii-1] > tprXRad[tpriii] && tprZPos[tpriii-1] > tprZPos[tpriii])                     //90+
      angIn=(Pi*0.5)+abs(atan(((tprXRad[tpriii-1]-tprXRad[tpriii])*xCvrt)/(zCvrt*(tprZPos[tpriii-1]-tprZPos[tpriii]))));
    else if(tprXRad[tpriii-1] > tprXRad[tpriii] && tprZPos[tpriii-1] < tprZPos[tpriii])                     //180+
      angIn=(Pi*1.0)+abs(atan(((tprZPos[tpriii-1]-tprZPos[tpriii])*zCvrt)/(xCvrt*(tprXRad[tpriii-1]-tprXRad[tpriii]))));
    else if(tprXRad[tpriii-1] < tprXRad[tpriii] && tprZPos[tpriii-1] < tprZPos[tpriii])                     //270+
      angIn=(Pi*1.5)+abs(atan(((tprXRad[tpriii-1]-tprXRad[tpriii])*xCvrt)/(zCvrt*(tprZPos[tpriii-1]-tprZPos[tpriii]))));
    else {
      lcd.setCursor(0,3);
      lcd.print("Error Unk:01        ");
      delay(5000);
      modeCt=999;
    }
    //--------------------Determine Angle OUT--------------------
    if(tpriii==tprArSize && tprXRad[tpriii] < tprStkRad) angOut=Pi;                           //180 (MaxPt Both)
    else if(tprCutDir==0 && tpriii==tprArSize && tprXRad[tpriii]==tprStkRad) angOut=Pi*1.5;   //270 (MaxPt Left)
    else if(tprCutDir==1 && tpriii==tprArSize && tprXRad[tpriii]==tprStkRad) angOut=Pi*0.5;   //90 (MaxPt Right)
    
    else if(tprCutDir==0 && (tprZPos[tpriii]-tprZPos[tpriii+1])==0 && tprXRad[tpriii] > tprXRad[tpriii+1]) angOut=Pi*2.0;   //360 Left
    else if(tprCutDir==1 && (tprZPos[tpriii]-tprZPos[tpriii+1])==0 && tprXRad[tpriii] > tprXRad[tpriii+1]) angOut=Pi*0.0;   //0   Right
    
    else if((tprZPos[tpriii]-tprZPos[tpriii+1])==0 && tprXRad[tpriii] < tprXRad[tpriii+1]) angOut=Pi;       //180 Both
    else if((tprXRad[tpriii]-tprXRad[tpriii+1])==0 && tprZPos[tpriii] > tprZPos[tpriii+1]) angOut=Pi*1.5;   //270 Can only happen Dir=0
    else if((tprXRad[tpriii]-tprXRad[tpriii+1])==0 && tprZPos[tpriii] < tprZPos[tpriii+1]) angOut=Pi*0.5;   //90 Can only happen Dir=1
    
    else if(tprXRad[tpriii] < tprXRad[tpriii+1] && tprZPos[tpriii] > tprZPos[tpriii+1])                     //180+
      angOut=(Pi*1.0)+abs(atan(((tprZPos[tpriii+1]-tprZPos[tpriii])*zCvrt)/(xCvrt*(tprXRad[tpriii+1]-tprXRad[tpriii]))));
    else if(tprXRad[tpriii] > tprXRad[tpriii+1] && tprZPos[tpriii] > tprZPos[tpriii+1])                     //270+
      angOut=(Pi*1.5)+abs(atan(((tprXRad[tpriii+1]-tprXRad[tpriii])*xCvrt)/(zCvrt*(tprZPos[tpriii+1]-tprZPos[tpriii]))));
    else if(tprXRad[tpriii] > tprXRad[tpriii+1] && tprZPos[tpriii] < tprZPos[tpriii+1])                     //0+
      angOut=(Pi*0.0)+abs(atan(((tprZPos[tpriii+1]-tprZPos[tpriii])*zCvrt)/(xCvrt*(tprXRad[tpriii+1]-tprXRad[tpriii]))));
    else if(tprXRad[tpriii] < tprXRad[tpriii+1] && tprZPos[tpriii] < tprZPos[tpriii+1])                     //90+
      angOut=(Pi*0.5)+abs(atan(((tprXRad[tpriii+1]-tprXRad[tpriii])*xCvrt)/(zCvrt*(tprZPos[tpriii+1]-tprZPos[tpriii]))));
    else {
      lcd.setCursor(0,3);
      lcd.print("Error Unk:02        ");
      delay(5000);
      modeCt=999;
    }
    //--------------------Check for a couple errors--------------------
    //Note: "Back&Forth" Z Pos not allowed with operator input
    if((angIn==(Pi*0.0) && angOut==(Pi*2.0)) || (angIn==(Pi*2.0) && angOut==(Pi*0.0)) || angIn==angOut) //"X" Back and forth points create 0 angle
    {
      lcd.setCursor(0,3);
      lcd.print("Zero Ang Found - NOK");
      delay(5000);
      modeCt=999;
    }
    //--------------------Determine Resultant, Beta Angle and resultant beta length of cord intersection--------------------
    angRslt=angIn+((angOut-angIn)/2.0);
    
    if(abs(angOut-angIn)==(Pi*1.0)) angBeta=(Pi*1.0);
    else if(abs(angOut-angIn) > (Pi*1.0)) angBeta=(Pi*2.0)-abs(angOut-angIn);
    else if(abs(angOut-angIn) < (Pi*1.0)) angBeta=abs(angOut-angIn);
    else {
      lcd.setCursor(0,3);
      lcd.print("Error Unk:03        ");
      delay(5000);
      modeCt=999;
    }
    lngBeta=(cos(((Pi*1.0)-angBeta)/2.0)*tprDpthFinCut*xCvrt)+((sin(((Pi*1.0)-angBeta)/2.0)*tprDpthFinCut*xCvrt)/tan(angBeta/2.0)); //(mm)!!

    //--------------------Calculate X & Z offset of profile points--------------------
    tprXOffmm=cos(angRslt)*lngBeta;
    tprZOffmm=sin(angRslt)*lngBeta;
    tprZPosOffst[tpriii]=float(tprZPos[tpriii])+(sin(angRslt)*lngBeta/zCvrt);    //(Cnts) TODO:  add +0.5 to both x and z will rounds up int.
    tprXRadOffst[tpriii]=float(tprXRad[tpriii])-(cos(angRslt)*lngBeta/xCvrt);     //(Cnts) Sign (-) actually adds to X (rewritten)

    if(tprXRadOffst[tpriii] < tprMaxDpOffst)    //Keep track of max depth X motor position of OFFSET x.
    {
      tprMaxDpOffst = tprXRadOffst[tpriii];
      //tprMaxArPos = tpriii;                   //TODO:  uncomment if removing the orig. 'Dp' variable
    }
    //Serial.print("angIn/Out = "); Serial.print(angIn*180/Pi); Serial.print("/"); Serial.print(angOut*180/Pi); Serial.print(" AngRslt = "); Serial.print(angRslt*180/Pi); Serial.print(" angBeta = "); Serial.println(angBeta*180/Pi);
    //Serial.print("lngBeta = "); Serial.print(lngBeta, 4); Serial.print(" X-mm = "); Serial.print(tprXOffmm, 4); Serial.print(" Z-mm = "); Serial.println(tprZOffmm, 4);
    //Serial.print("tprZPosOffst["); Serial.print(tpriii); Serial.print("] = "); Serial.print(tprZPosOffst[tpriii]);
    //Serial.print("       ");
    //Serial.print("tprXRadOffst["); Serial.print(tpriii); Serial.print("] = "); Serial.println(tprXRadOffst[tpriii]);
  }
}
//*********************************************************
