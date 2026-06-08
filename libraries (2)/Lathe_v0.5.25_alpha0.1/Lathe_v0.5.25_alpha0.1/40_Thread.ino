//*********************************************************
//  extThrdSetup()  extThrdMove()  xMoveRetract_4()  zMoveReturn_5()  zMoveStart_1()  xMoveDepth_2()  zMoveThread_3()  
//*********************************************************
void extThrdSetup() 
{
  if(modeCt==1)
  {
    //_____________________________________________________
    if(tQustCt==0)    //Thread Size?
    {
      lcd.setCursor(0,2);
      lcd.print("Thread Size?        ");
      lcd.setCursor(0,3);
      lcd.print("                    ");
      lcd.setCursor(0,3);

      lcd.print(thrdNomSize[tSizePos]);     //todo: remove.... this is new inch thread text display
      if(tSizePos < 14)
      {
        lcd.print("x ");
        lcd.print(thrdPitch[tSizePos], 2);
      }
      else
      {
        lcd.print("-");
        lcd.print((1.0/(thrdPitch[tSizePos]/25.4)), 0);        
      }

             
      tQustCt=1;
    }
    if(tQustCt==1) modeButtons();
    //_____________________________________________________
    if(tQustCt==2)    //Part Material?
    {
      lcd.setCursor(0,2);
      lcd.print("Part Material?      ");
      lcd.setCursor(0,3);
      lcd.print("                    ");
      lcd.setCursor(0,3);
      lcd.print(thrdMtlText[tMtlPos]);        
      tQustCt=3;
    }
    if(tQustCt==3) modeButtons();
    //_____________________________________________________
    if(tQustCt==4)    //Cutting Tool Matl?
    {
      thrdRpmTemp = thrdMtlSfm[tMtlPos]*4.0/(thrdOdNom[tSizePos]/25.4);  //PreCalc if Carb needed
      if(thrdRpmTemp < thrdMinRpm && tTlPos==0) tTlPos=1;   //Skips to only allow Carbide choice
      if(thrdRpmTemp >= thrdMinRpm && tTlPos==2) tTlPos=0;  //Skips the 'exit' choice as both HSS & Carbide allowed
      lcd.setCursor(0,2);
      lcd.print("Cutting Tool Matl?  ");
      lcd.setCursor(0,3);
      lcd.print("                    ");
      lcd.setCursor(0,3);
      lcd.print(thrdToolText[tTlPos]);        
      tQustCt=5;
    }
    if(tQustCt==5) modeButtons();
    if(tQustCt==6 && tTlPos==2) modeCt=999;   //This exits thread program if "exit" on Tool Selector
    //_____________________________________________________
    if(tQustCt==6)    //Turn OD & Measure OD?
    {
      lcd.setCursor(0,2);
      lcd.print("OD = ");
      if(unitConverter==1.0) lcd.print(thrdOdNom[tSizePos], 3);
      else lcd.print((thrdOdNom[tSizePos]/unitConverter), 4);
      lcd.print("   ");
      lcd.setCursor(12,2);
      lcd.print("+-");
      lcd.setCursor(14,2);
      if(unitConverter==1.0) lcd.print((thrdOdTol[tSizePos]/2.0), 3);
      else lcd.print((thrdOdTol[tSizePos]*0.5/unitConverter), 4);
      lcd.setCursor(0,3);
      lcd.print("Measured? = ");
      lcd.setCursor(12,3);
      if(unitConverter==1.0) lcd.print((thrdOdNom[tSizePos]+thrdOdMeasOffset), 3);
      else lcd.print(((thrdOdNom[tSizePos]+thrdOdMeasOffset)/unitConverter), 4);
      tQustCt=7;      
    }
    if(tQustCt==7) 
    {
      modeButtons();
      zMotorFeed();
    }
    //_____________________________________________________
    if(tQustCt==8)    //Set X w/ C391 Tool
    { 
      lcd.setCursor(0,2);
      lcd.print("Set X C391 tool @ OD");  
      lcd.setCursor(0,3);
      lcd.print("B3 when done        ");
      tQustCt=9;
    }
    if(tQustCt==9) modeButtons();
    if(tQustCt==10)
    {
      thrdC391Offset = mtrNewPosX;
      tQustCt=11;
    }
    //_____________________________________________________
    if(tQustCt==11)   //Set X Tool Tip on OD
    { 
      lcd.setCursor(0,2);
      lcd.print("Set X Tool Tip on OD");  
      lcd.setCursor(0,3);
      lcd.print("B3 when done        ");
      tQustCt=12;
    }
    if(tQustCt==12) modeButtons();
    if(tQustCt==13)
    {
      thrdTipDim = mtrNewPosX;            //TODO:  make sure tip is in spec. Need tol of pitch array!  
      if((thrdC391Offset-thrdTipDim) > ((thrdC391+2.0)*(xMtrCntPerRev/xPitch)) 
        || (thrdC391Offset-thrdTipDim) < ((thrdC391-2.0)*(xMtrCntPerRev/xPitch)))  //TODO replace 2mm with max geomotry tol.
      {
        lcd.setCursor(0,3);
        lcd.print("*Tool Tip Geom. NOK ");
        delay(2000);
        tQustCt=11;         
      }
      else tQustCt=14;
    }
    //_____________________________________________________
    if(tQustCt==14)   //Set X Retract Pos
    { 
      lcd.setCursor(0,2);
      lcd.print("Set X Retract Pos   ");      //TODO: make sure retract is farther than tool tip
      lcd.setCursor(0,3);
      lcd.print("B3 when done        ");
      tQustCt=15;
    }
    if(tQustCt==15) modeButtons();
    if(tQustCt==16)
    {
      thrdXRetract = mtrNewPosX;
      if(thrdXRetract <= thrdTipDim)
      {
        lcd.setCursor(0,3);
        lcd.print("*X Retract NOK      ");
        delay(2000);
        tQustCt=14;
      }
      else tQustCt=17;
    }
    //_____________________________________________________
    if(tQustCt==17)   //Set Z <- End Pos
    { 
      lcd.setCursor(0,2);
      lcd.print("Set Z <- End Pos    ");    
      lcd.setCursor(0,3);
      lcd.print("B3 when done        ");
      tQustCt=18;
    }
    if(tQustCt==18) modeButtons();
    if(tQustCt==19)
    {
      thrdZEnd = mtrNewPosZ;   
      tQustCt=20;
    }
    //_____________________________________________________
    if(tQustCt==20)   //Set Z -> Start Pos
    { 
      lcd.setCursor(0,2);
      lcd.print("Set Z -> Start Pos  ");
      lcd.setCursor(0,3);
      lcd.print("B3 when done        ");
      tQustCt=21;
    }
    if(tQustCt==21) modeButtons();
    if(tQustCt==22)
    {
      thrdZStart = mtrNewPosZ; 
      if(thrdZStart > (thrdZEnd-(5.0*(zMtrCntPerRev/zPitch))))    //must be at least 5mm greater
      {
        lcd.setCursor(0,3);
        lcd.print("*Z Start NOK        ");
        delay(2000);
        tQustCt=20;          
      }
      else tQustCt=23;
    }
    //_____________________________________________________
    if(tQustCt==23)   //Set Spindle RPM
    { 
      thrdRpmRcmnd = thrdMtlSfm[tMtlPos]*thrdToolVal[tTlPos]*4.0/(thrdOdNom[tSizePos]/25.4);  //Calculated value
      if(thrdRpmRcmnd > thrdMaxRpm) thrdRpmRcmnd = thrdMaxRpm;    //Limits RPM to user input
      thrdFeedRcmnd = thrdRpmRcmnd*thrdPitch[tSizePos];              //Determine mm/min req'd by motor @ Rcmnd RPM
      if(thrdFeedRcmnd > thrdMaxFeed) thrdCutStep = 2;              //Allows now double feed 900mm/min  TODO: move to cut
      if(thrdFeedRcmnd > thrdMaxFeed*2) 
      {
        thrdFeedRcmnd = thrdMaxFeed*2;                                //Limits feed Rcmnd to 900mm/min
        thrdRpmRcmnd = thrdFeedRcmnd/thrdPitch[tSizePos];            //Refind RPM RCMND based on adjusted feed
      }
      
      lcd.setCursor(0,2);
      lcd.print("Set Spindle to ");
      lcd.print(thrdRpmRcmnd, 0);
      lcd.print(" ");
      lcd.setCursor(0,3);
      lcd.print("RPM =      B3:Accept");
      spindleRpm3=0;
      tQustCt=24;
    }
    if(tQustCt==24) 
    {
      spindleRpm3=1000000/((sIndexTimeN-sIndexTimeO)*0.016667);
      if(spindleRpm3 > 200 && spindleRpm3 < 2400 && spindRev!=spindRevSaved)   //TODO: use spndlRpmMax&Min
      {
        spindRevSaved=spindRev;
        tRpmZero=0;
        if(spindleRpm3 <= 999)
        {
          lcd.setCursor(6,3);
          lcd.print(" ");
          delay(150);
          lcd.setCursor(7,3);
          lcd.print(spindleRpm3);
        }
        else
        {
          lcd.setCursor(6,3);
          delay(150);
          lcd.print(spindleRpm3);
        }        
      }
      else tRpmZero++;
      if(tRpmZero > 1000)   //tested value: program cycles which represent spindle idle
      {
        lcd.setCursor(6,3);
        lcd.print("   0");
        tRpmZero=0;
      }
      modeButtons();
    }
    if(tQustCt==25)
    {
      if(spindleRpm3 > (thrdRpmRcmnd*1.15) || spindleRpm3 > (thrdMaxRpm*1.03))  //Limits: +/-15%Recomnd, +3%Max
      {
        lcd.setCursor(0,3);
        lcd.print("RPM too high!!!     ");
        delay(2000);
        tQustCt=23;
      }
      else if(spindleRpm3 < (thrdRpmRcmnd*0.85) || spindleRpm3 < (thrdMinRpm-5))    //Limits: +/-15%Rcmnd, -5rpm
      {
        lcd.setCursor(0,3);
        lcd.print("RPM too low!!!      ");
        delay(2000);
        tQustCt=23;        
      }
      else 
      {
        thrdRpmActual=spindleRpm3;                             //Saves the current RPM (may change later).
        thrdFeedActual=thrdRpmActual*thrdPitch[tSizePos];  //mm/min storing for first time.
        tQustCt=26;
      }
    }
    //_____________________________________________________
    if(tQustCt==26)   //READY!  Toggle HalfNut Mssg
    {
      lcd.setCursor(16,2);
      lcd.print("    ");
      lcd.setCursor(0,2);

      lcd.print(thrdNomSize[tSizePos]);             //todo: remove.... this is new inch thread text display
      if(tSizePos < 14)
      {
        lcd.print("x ");
        lcd.print(thrdPitch[tSizePos], 2);
      }
      else
      {
        lcd.print("-");
        lcd.print((1.0/(thrdPitch[tSizePos]/25.4)), 0);        
      }
      
      //lcd.setCursor(11,2);                  //TODO: remove - packs lcd text on line
      lcd.print(" is Ready  ");     
      lcd.setCursor(0,3);
      lcd.print("Engage Half Nut...  ");
      tQustCt=27;
    }
    if(tQustCt==27)    //Holder to do stuff & set tQustCt=28
    {
      tQustCt=28;     //need to prevent B3 changing this to Qust29.  todo:Can do stuff in here or remove
    }
    if(tQustCt==28) extThrdMove();
  }
}
//*********************************************************
void extThrdMove()
{
  tempEncPosZ=encNewPosZ;   //save current Z encoder cnts
  tempEncPosX=encNewPosX;   //save current X encoder cnts
  
  thrdNap = 72*(thrdPitch[tSizePos]/25.4)+4;        //Truncated down to integer
  thrdXDepthPos = thrdC391Offset-((thrdC391+(thrdOdMeasOffset/2.0)+(thrdOdNom[tSizePos]/2.0)
    -(thrdOdPitchNom[tSizePos]/2.0)+(((sqrt(3.0)/2.0)*thrdPitch[tSizePos])/2.0))*(float(xMtrCntPerRev)/float(xPitch)))-0.5;
    //This is the X mtr count location at max thread depth (0.5 subtracted due to int truncated result in abs #)
  thrdInfeedTotal = thrdXDepthPos-thrdTipDim;       //Absolute value of infeed in counts (neg value)
  thrdInfeed1stPass = (thrdInfeedTotal/sqrt(float(thrdNap)-1.0))*sqrt(0.3);
  thrdOffset1stPass = (thrdInfeedTotal-thrdInfeed1stPass)*tan(thrdAng)*(xPitch/zPitch);  //this is also MAX.  2/5 is cnt conversion
          /*Serial.print("thrdC391Offset (start) = ");
          Serial.println(thrdC391Offset);
          Serial.print("thrdOdMeasOffset = ");
          Serial.println(thrdOdMeasOffset);
          Serial.print("thrdXDepthPos (end) = ");
          Serial.println(thrdXDepthPos);
          Serial.print("thrdTipDim = ");
          Serial.println(thrdTipDim);                  
          Serial.print("thrdInfeedTotal (depth from tip) = ");
          Serial.println(thrdInfeedTotal);
          Serial.print("thrdInfeed1stPass = ");
          Serial.println(thrdInfeed1stPass);
          Serial.print("thrdOffset1stPass (why is this 2/5?) = ");
          Serial.println(thrdOffset1stPass);
          */
  while(modeCt==1 && tQustCt >= 28 && tQustCt <= 37)     //ToDo:  I think only Qust28 & Qust29 required
  {
    curStateS1 = digitalRead(inPinS1);        //Checks current halfnut lever status
    if(curStateS1==LOW) prevStateS1=LOW;      //IF Halfnut lever is OFF, set prevStateS1=LOW -> reset to allow another feed.
    if(curStateS1 == HIGH && prevStateS1 == LOW) delay(50);   //Debouce
    curStateS1 = digitalRead(inPinS1);
    if(curStateS1 == HIGH && prevStateS1 == LOW)              //Run 2nd time just to be sure we want to move
    {
      if(tQustCt==28)           //Run Thread "Scratch Pass".  Sets initial tool position and runs a 0.001" pass
      {
        prevStateS1=HIGH;
        xMoveRetract_4();
        zMoveReturn_5();
        thrdOffset = thrdOffset1stPass;
        lcd.setCursor(5,0);
        lcd.print("--------");
        lcd.setCursor(5,1);
        lcd.print("--------");
        lcd.setCursor(0,2);
        lcd.print("                    ");
        lcd.setCursor(0,3);
        lcd.print("Thread Scratch Pass ");        
        zMoveStart_1();
        thrdInfeed = -10;        //Scratch pass.  10 cnts = 0.025mm (0.001")  TODO: Fix to variable
        xMoveDepth_2();
        zMoveThread_3();
        xMoveRetract_4();
        zMoveReturn_5();
        tQustCt=29;
        lcd.setCursor(0,2);
        lcd.print("Check Pitch OK, then");
        lcd.setCursor(0,3);
        lcd.print("toggle HalfNut again");
      }
      else if(tQustCt==29)     //Run Threading operation - All passes
      {
        tTotPass=thrdNap+thrdAutoSpr;
        lcd.setCursor(0,2);
        lcd.print("     Threading:     ");
        lcd.setCursor(16,2);
        lcd.print(thrdNap);
        //lcd.setCursor(18,2);    //TODO: remove (not reqd - packs)
        lcd.print("+");
        //lcd.setCursor(19,2);    //TODO: remove (not reqd - packs)
        lcd.print((tTotPass-thrdNap));
        
        prevStateS1=HIGH;
        for(thrdPassNum=1; thrdPassNum <= thrdNap; thrdPassNum++)
        {
          if(tNxtOpPos==2 || tNxtOpPos==3) thrdPassNum = thrdNap;  //Spring & Depth Pass, Set to "Final" pass
          if(thrdPassNum==1) thrdInfeed = thrdInfeed1stPass;
          else thrdInfeed = (thrdInfeedTotal/sqrt(float(thrdNap)-1.0))*sqrt(thrdPassNum-1.0);
          if(thrdPassNum==1) thrdOffset = thrdOffset1stPass;
          else thrdOffset = (thrdInfeedTotal-thrdInfeed)*tan(thrdAng)*(xPitch/zPitch);  //2/5 is cnt conversion

          thrdInfeed=thrdInfeed-(thrdInfeedAdj*(xMtrCntPerRev/xPitch));  //ADDS Depth Adjust to infeed. Must be done after offset calc. (subtract out immediately)

                /*Serial.println("-----------------------");
                Serial.print("thrdPassNum = ");
                Serial.println(thrdPassNum);
                Serial.print("thrdInfeed = ");
                Serial.println(thrdInfeed);
                Serial.print("thrdOffset = ");
                Serial.println(thrdOffset);
                Serial.print("thrdInfeedAdj = ");
                Serial.println(thrdInfeedAdj);
                Serial.println("-----------------------");
                */
          lcd.setCursor(0,3);
          if(tNxtOpPos==2) lcd.print("Spring Pass         ");
          else if(tNxtOpPos==3) lcd.print("Adjust Pass         ");
          else
          {
            lcd.print("Pass    of          ");
            lcd.setCursor(5,3);
            lcd.print(thrdPassNum+tSprCnt);
            lcd.setCursor(11,3);
            lcd.print(tTotPass);  
          }

          zMoveStart_1();
          xMoveDepth_2();
          zMoveThread_3();
          xMoveRetract_4();
          zMoveReturn_5();
          
          thrdInfeed=thrdInfeed+(thrdInfeedAdj*(xMtrCntPerRev/xPitch));  //REMOVES the additional depth for 'next' loop
          //Serial.println(thrdPassNum);
          
          if(thrdPassNum == thrdNap && thrdAutoSpr > 0)          //Performs automatic spring pass if set
          {
            thrdPassNum--;
            thrdAutoSpr--;
            tSprCnt++;
          }
        }
        tQustCt=30;
      }
    }
    if(tQustCt==30)     //stay here to ask questions 30-37.
    {
      lcd.setCursor(0,2);
      lcd.print("Done: Select next Op");
      lcd.setCursor(0,3);
      lcd.print(thrdNextOp[tNxtOpPos]);    //Exit, Measure over wire, Spring Pass, Adjust Depth
      tQustCt=31;
    }
    if(tQustCt==31) modeButtons();
    if(tQustCt==32 && tNxtOpPos==0) modeCt=999;    //Exit
    if(tQustCt==32 && tNxtOpPos==1)                 //Measure over wire
    {
      thrdWireConst=(3.0*thrdWire[tSizePos])-(0.86603*thrdPitch[tSizePos]);
      thrdWireMic=thrdOdPitchNom[tSizePos]+thrdWireConst;
      lcd.setCursor(0,2);
      lcd.print("Use wire =        mm");
      lcd.setCursor(11,2);
      lcd.print((thrdWire[tSizePos]/unitConverter), 4);
      lcd.setCursor(0,3);
      lcd.print("Mic=        +-      ");
      if(thrdWireMic > 9.9999)
      {
        lcd.setCursor(4,3);
      }
      else lcd.setCursor(5,3);
      lcd.print((thrdWireMic/unitConverter), 4);
      lcd.setCursor(14,3);
      lcd.print((thrdOdPitchTol[tSizePos]*0.5/unitConverter), 4);
      tQustCt=33;
    }
    if(tQustCt==33) modeButtons();              //wait for "continue from measure over wire info
    if(tQustCt==34) tQustCt=30;                 //Go back to "Next Op" question
    
    if(tQustCt==32 && tNxtOpPos==2)             //Spring Pass.  
    {
      tQustCt=29;                               //Just go back into 'for' where num pass set to 'final'
      lcd.setCursor(0,2);
      lcd.print("Spring Pass         ");
      lcd.setCursor(0,3);
      lcd.print("Toggle HalfNut again");
    }
    if(tQustCt==32 && tNxtOpPos==3) tQustCt=35; //Ask RADIAL depth required for Adjustment
    if(tQustCt==35)                             //Set RADIAL offset depth
    {
      lcd.setCursor(0,2);
      lcd.print("Set Adjusted Depth..");
      lcd.setCursor(0,3);
      lcd.print("RADIAL infeed=      ");
      lcd.setCursor(14,3);
      lcd.print((thrdInfeedAdj/unitConverter), 4);
      tQustCt=36;
    }
    if(tQustCt==36) modeButtons();
    if(tQustCt==37)                                 //Adjust Depth Pass
    {
      tQustCt=29;                         //Just go back into 'for' where num pass set to 'final' & Depth now added
      lcd.setCursor(0,2);
      lcd.print("Adjust Depth Pass   ");
      lcd.setCursor(0,3);
      lcd.print("Toggle HalfNut again");      
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
void xMoveRetract_4()   //X Motor move to the retract position (current motor count to "retract")
{
  while(mtrNewPosX != thrdXRetract && modeCt==1)
  {
    if(mtrNewPosX < thrdXRetract) thrdRapidStep=1;        //Fine move +cnts (-linear value)
    if(mtrNewPosX > thrdXRetract) thrdRapidStep=-1;       //Fine move -cnts (+linear value)
    if((mtrNewPosX+20) < thrdXRetract) thrdRapidStep=3;   //Rapid move +cnts (-linear value)
    if((mtrNewPosX-20) > thrdXRetract) thrdRapidStep=-3;  //Rapid move -cnts (+linear value)
    delayMicroseconds(thrdRapidDelay);                      //Delay sets velocity
    X.move(thrdRapidStep);                                  //Move x motor
    mtrNewPosX = mtrOldPosX+thrdRapidStep;                  //Calculates where motor is (cnt) from absolute (machine start)
    mtrOldPosX=mtrNewPosX;                                    //don't know why i keep tracking old pos but i do
    curStateS1 = digitalRead(inPinS1);
    if(curStateS1 == LOW) modeCt=999;                        //Dump out if halfnut disengaged too early
  }
}
//*********************************************************
void zMoveReturn_5()    //Z Motor move -> to just prior to start of thread
{
  while(mtrNewPosZ != (thrdZStart+80) && modeCt==1)        //Stops 80 counts prior to thrd Start (80cnts=0.5mm)
  {
    if(mtrNewPosZ > (thrdZStart+80)) thrdRapidStep=-1;    //Fine move +cnts     
    if(mtrNewPosZ < (thrdZStart+80)) thrdRapidStep=1;     //Fine move +cnts
    if(mtrNewPosZ >= (thrdZStart+200)) thrdRapidStep=-3;  //Rapid move +cnts
    if(mtrNewPosZ <= (thrdZStart-120)) thrdRapidStep=3;   //Rapid move +cnts   
    delayMicroseconds(thrdRapidDelay);                      //Delay sets velocity
    Z.move(thrdRapidStep);                                  //Move x motor
    mtrNewPosZ = mtrOldPosZ+thrdRapidStep;                  //Calculates where motor is (cnt) from absolute (machine start)
    mtrOldPosZ=mtrNewPosZ;                                    //don't know why i keep tracking old pos but i do
    curStateS1 = digitalRead(inPinS1);
    if(curStateS1 == LOW) modeCt=999;                        //Dump out if halfnut disengaged too early
  }
}
//*********************************************************
void zMoveStart_1()     //Z Motor move -> to the start of thread (with adjustment for infeed at 27.5 deg)
{
  while(mtrNewPosZ != (thrdZStart+thrdOffset) && modeCt==1) //This is where the position is controlled
  {
    thrdRapidStep=-1;      
    delayMicroseconds(thrdRapidDelay);                        //Delay sets velocity
    Z.move(thrdRapidStep);                                    //Move x motor
    mtrNewPosZ = mtrOldPosZ+thrdRapidStep;                    //Calculates where motor is (cnt) from absolute (machine start)
    mtrOldPosZ=mtrNewPosZ;                                      //don't know why i keep tracking old pos but i do
    curStateS1 = digitalRead(inPinS1);
    if(curStateS1 == LOW) modeCt=999;                          //Dump out if halfnut disengaged too early
  }
}
//*********************************************************
void xMoveDepth_2()     //X Motor move to thread depth (with adjustment for infeed per pass)
{
  while(mtrNewPosX != (thrdTipDim+thrdInfeed) && modeCt==1) //This is where the position is controlled
  {
    thrdRapidStep=-1;                                                         //Default
    if((mtrNewPosX) > (thrdTipDim+thrdInfeed)) thrdRapidStep=-1;           //Fine move -cnts (+linear value)
    if((mtrNewPosX) > (thrdTipDim+thrdInfeed+20)) thrdRapidStep=-3;        //Rapid move -cnts (+linear value)        
    delayMicroseconds(thrdRapidDelay);                      //Delay sets velocity
    X.move(thrdRapidStep);                                  //Move x motor
    mtrNewPosX = mtrOldPosX+thrdRapidStep;                  //Calculates where motor is (cnt) from absolute (machine start)
    mtrOldPosX=mtrNewPosX;                                    //don't know why i keep tracking old pos but i do
    curStateS1 = digitalRead(inPinS1);
    if(curStateS1 == LOW) modeCt=999;                        //Dump out if halfnut disengaged too early
  }  
}
//*********************************************************
void zMoveThread_3()    //Z Motor move for cutting thread (actively controlled to spindle speed)
{
  //INPUT: thrdRpmRcmnd
  //INPUT: thrdFeedRcmnd
  //INPUT: thrdCutStep

  //RECALC ACTUAL RPM/FEED & CALCULATE DELAY
  int sTime = 0;
  while(sTime==0)
  {
    sIndexTimeNSaved = sIndexTimeN;
    thrdRpmActual = 1000000/((sIndexTimeN-sIndexTimeO)*0.016667);  //or  1.0/(((sIndexTimeN-sIndexTimeO)/1000000.0)/60.0)  
    if(thrdRpmActual > (thrdRpmRcmnd*1.15) || thrdRpmActual > (thrdMaxRpm*1.03))    //Limits High: +/-15%Recomnd, +3%Max
    {
      lcd.setCursor(0,3);
      lcd.print("RPM too high!!!     ");
    }
    else if(thrdRpmActual < (thrdRpmRcmnd*0.85) || thrdRpmActual < (thrdMinRpm-5))  //Limits Low: +/-15%Rcmnd, -5rpm
    {
      lcd.setCursor(0,3);
      lcd.print("RPM too low!!!      ");     
    }
    else 
    {
      //thrdRpmActual is correct and will be used.  Prior to 'while' the RPM must be correct (Axis is live when RPM ok)
      thrdIndexTime = 1000000/(thrdRpmActual*0.016667);     //is used to make sure next index is within range (debounce)
      thrdFeedActual=thrdRpmActual*thrdPitch[tSizePos];    //Feed to use in 'Cut'
      //NEW CALCS FOR DELAY
      thrdCutDelayCalc = (zPitch*thrdCutStep*1000000*60)/(thrdFeedActual*zMtrCntPerRev);
      thrdCutDelayProg = 150;  //######****** ADJUST THIS DELAY TO MATCH REQD INITIAL SPEED (by testing)
      thrdCutDelay = thrdCutDelayCalc - thrdCutDelayProg;
      //NEW MOTOR CNT CALCULATIONS
      mtrCntsPerIndex = zMtrCntPerRev*thrdPitch[tSizePos]/zPitch;   //Constant value regardless of speed.  For mm always INT (maybe change for inch)
      mtrCntOrig = mtrNewPosZ;     //Absolute start Z pos saved
      mtrCntExpSaved = mtrNewPosZ;    //todo:move out... Saves Expected cnt for running value
      deltaDelay = 0;
      sTime=1;    //Exits out of "calc" while loop
    }
  }
  /*Serial.print("thrdRpmActual = ");
  Serial.println(thrdRpmActual);
  Serial.print("thrdFeedActual = ");
  Serial.println(thrdFeedActual);
  Serial.print("thrdCutDelayCalc = ");
  Serial.println(thrdCutDelayCalc);
  Serial.print("thrdCutDelay = ");
  Serial.println(thrdCutDelay);
  Serial.print("mtrCntsPerIndex = ");
  Serial.println(mtrCntsPerIndex);
  Serial.print("mtrCntOrig = ");
  Serial.println(mtrCntOrig);  
  Serial.println("");
  */
  tCount=0; //can be remove - for debug
  iCount=1; //used as index count... used to mult orig mtr cnt to obtain Expected count per cycle. Avoids accum error.
  int tTime = 0;
  sIndexTimeNSaved = sIndexTimeN;
  while(tTime==0)   //Fast trigger: 
  {
    if(sIndexTimeN > (sIndexTimeNSaved+(0.63*thrdIndexTime)) && sIndexTimeN < (sIndexTimeNSaved+(1.38*thrdIndexTime)) && (sIndexTimeN-sIndexTimeO) > 0 && sIndexTimeN < 3600000000)   //Index has changed && not overflow && 10mins before overflow occurs (<60mins)
    {
      tTime=1;    //allows exit 'while' and enter next 'while' to start motor move (move Z at index pulse)
    }
    if(sIndexTimeN > (sIndexTimeNSaved+(2.5*thrdIndexTime)))   //if time is way beyond (2.5x) single index pulse then reset
    {
      sIndexTimeNSaved = sIndexTimeN;
    }
  }
  sIndexTimeNSaved = sIndexTimeN;     //yesneeded  ... Save the index time again just before entering 'move'
  //____________________________________________
  while(mtrNewPosZ < thrdZEnd && modeCt==1)
  {
    delayMicroseconds(thrdCutDelay);              //Delay sets velocity.
    Z.move(thrdCutStep);                          //Move x motor
    mtrNewPosZ = mtrOldPosZ+thrdCutStep;          //Calculates where motor is (cnt) from absolute (machine start)
    mtrOldPosZ=mtrNewPosZ;                          //don't know why i keep tracking old pos but i do

    if(sIndexTimeN > (sIndexTimeNSaved+(0.63*thrdIndexTime)) && sIndexTimeN < (sIndexTimeNSaved+(1.38*thrdIndexTime)))
    //Is next index found?  Then determine tracking and adjust.
    {
      thrdCutDelay = thrdCutDelay-deltaDelay;
      mtrCntExpSaved = mtrCntOrig+(mtrCntsPerIndex*iCount);       //Determines expected mtr cnt value at Index
      iCount++;
      deltaCnts = mtrNewPosZ-mtrCntExpSaved;     //Num of counts "Lagging". (Neg value will dec. delay)

      deltaDelay = ((float(thrdCutDelay)*(((float(mtrCntsPerIndex)+float(deltaCnts))*1000.0)/float(mtrCntsPerIndex)))-(float(thrdCutDelay)*1000.0))/1000.0; //time in us to correct        
      //deltaDelay = (thrdCutDelay*((mtrCntsPerIndex+deltaCnts)/mtrCntsPerIndex))-thrdCutDelay; //time in us to correct
      thrdCutDelay = thrdCutDelay+(deltaDelay*2);   //What delay should be BUT does not include adj from last cycle
      //thrdCutDelay = thrdCutDelay*((mtrCntsPerIndex+(deltaCnts*1.1))/mtrCntsPerIndex);   //*1.x?? to catch up +anticipate
      //IMPORTANT:  Without 1.x 'x': the thrdCutDelay does NOT change ???  int/float?

      sIndexTimeNSaved=sIndexTimeN;   //Reset
      /*if(tCount<100)                          //Debug only
      {
        tStExpSav[tCount]=mtrCntExpSaved;
        tStActSav[tCount]=mtrNewPosZ;
        tStDeltaCnts[tCount]=deltaCnts;
        tStCutDelay[tCount]=thrdCutDelay;
        tCount++;
      }*/
    }
    curStateS1 = digitalRead(inPinS1);
    if(curStateS1 == LOW) modeCt=999;                        //Dump out if halfnut disengaged too early
  }
  int tCount2 = 0;
  while(tCount >= 0)
  {
    /*Serial.print("tStExpSav = ");
    Serial.println(tStExpSav[tCount2]); 
    Serial.print("tStActSav = ");
    Serial.println(tStActSav[tCount2]); 
    Serial.print("deltaCnts = ");
    Serial.println(tStDeltaCnts[tCount2]);
    Serial.print("tStCutDelay = ");
    Serial.println(tStCutDelay[tCount2]);
    Serial.println("");
    */
    tCount2++;
    tCount--;
  }
}
//*********************************************************
