//*********************************************************
//  stdButtons()  modeButtons()  arcButtons()  
//*********************************************************
void stdButtons()
//Each of 3 buttons has 2 functions for either momentary push (<600ms) or push and hold (>700 & <1200ms)
//Button 1:  Push = Switch X memory display between M1, M2, M3.  Hold = zero X axis.
//Button 2:  Push = Switch Z memory display between M1, M2, M3.  Hold = zero Z axis.
//Button 3:  Push(<600ms) = Swith units in<->mm.  Hold(600-1200ms) = Set Z axis stop.  Hold(1800-5000ms) = Mode change
{
  if(modeCt==0)    //Only runs in '0' Standard Mode
  {
  //Button #1:  X Axis (stdButtons)
  //==================================================================================
    curStateB1 = digitalRead(inPinB1);
    if (curStateB1 == HIGH && prevStateB1 == LOW && (millis() - startTimeB1) > 200)
    {
      startTimeB1 = millis();         
    }
    millisHeldB1 = (millis() - startTimeB1);
    if (millisHeldB1 > 40)  //Simple debounce
    {
      if (curStateB1 == LOW && prevStateB1 == HIGH)     //check if button released
      {
        if (millisHeldB1 <= 600)           //Short button press will change memory #
        {
          mX=mX+1;
          if(mX==3)
          {
            mX=0;
          }
          displayLcdBasicsXZ();                 //go update the display
        }
        if (millisHeldB1 > 600)  //Long button press will set display to 0
        {                                               
          memOffsetX[mX]=mtrNewPosX;            //(stores absolute motor count into array memory location)
          displayLcdBasicsXZ();                 //go update the display
        }
      }
    }
    prevStateB1 = curStateB1;
    prevMillisHeldB1 = millisHeldB1;
    
  //Button #2:  Z Axis (stdButtons)
  //==================================================================================
    curStateB2 = digitalRead(inPinB2);
    if (curStateB2 == HIGH && prevStateB2 == LOW && (millis() - startTimeB2) > 200)
    {
      startTimeB2 = millis();         
    }
    millisHeldB2 = (millis() - startTimeB2);
    if (millisHeldB2 > 40)  //Simple debounce
    {
      if (curStateB2 == LOW && prevStateB2 == HIGH)     //check if button released
      {
        if (millisHeldB2 <= 600)           //Short button press will change memory #
        {
          mZ=mZ+1;
          if(mZ==3)
          {
            mZ=0;
          }
          displayLcdBasicsXZ();                           //go update the display
          toggleStopZ[mZ]=4;                              //resets toggleStop so Stop postion can be rewritten
          displayLcdStop();                               //go update stop value with memory change
        }
        if (millisHeldB2 > 600)   //Long button press will set display to 0
        {                                                 //(stores absolute motor count into array memory location)
          memOffsetZ[mZ]=mtrNewPosZ;
          displayLcdBasicsXZ();                           //go update the display
          toggleStopZ[mZ]=4;                              //resets toggleStop so Stop postion can be rewritten
          displayLcdStop();                               //go update stop value relative to new 0.0 z position
        }
      }
    }
    prevStateB2 = curStateB2;
    prevMillisHeldB2 = millisHeldB2;
  
  //Button #3:  General (stdButtons)
  //==================================================================================
    curStateB3 = digitalRead(inPinB3);
    if (curStateB3 == HIGH && prevStateB3 == LOW && (millis() - startTimeB3) > 200)   //todo uncomment
    {
      startTimeB3 = millis();         
    }
    millisHeldB3 = (millis() - startTimeB3);
    if (millisHeldB3 > 120)  //simple debounce   //todo?? changed from 40ms  Bad button?
    {
      if (curStateB3 == LOW && prevStateB3 == HIGH)   //check if button released
      {
        if (millisHeldB3 <= 600)         //change from mm <-> inch
        {
          if(unitConverter==25.4)
          {
            unitConverter=1.0;
          }
          else
          {
            unitConverter=25.4;
          }
            displayLcdBasicsXZ();                 //go update the X display
            displayLcdFeed();                     //go update the Feed display
            toggleStopZ[mZ]=4;                    //resets toggleStop so Stop postion can be rewritten
            displayLcdStop();                     //go update the stop value 
        }
        if (millisHeldB3 > 600 && millisHeldB3 <= 1800) 
        {
          memStopZ[mZ]=mtrNewPosZ;                //sets the z-stop value
        }
        if (millisHeldB3 > 1800 && millisHeldB3 < 5000) //Mode select
        {
          modeCt=999;                             //Allows "Mode" function to run
        }
        
        if (millisHeldB3 >= 10000)
        {
          lcd.setCursor(11,2);                    //Resets error code on LCD (10 second hold)
          lcd.print("   Z-STOP"); 
        }
          toggleStopZ[mZ]=4;                      //resets toggleStop so Stop postion can be rewritten
          displayLcdStop();                       //go update the stop display
      }
    }
    prevStateB3 = curStateB3;
    prevMillisHeldB3 = millisHeldB3;
  }
}
//*********************************************************
void modeButtons()
{
  if(modeCt==1 || modeCt==3 || modeCt > 998)  //TODO: Split up 1&3 into separate button functions
  {
    //_____________________________________________________
    //Button #1:  Selector + (modeButtons)
    //_____________________________________________________
    curStateB1 = digitalRead(inPinB1);
    if (curStateB1 == HIGH && prevStateB1 == LOW && (millis() - startTimeB1) > 200)
    {
      startTimeB1 = millis();         
    }
    millisHeldB1 = (millis() - startTimeB1);
    if (millisHeldB1 > 40) 
    {
      if (curStateB1 == LOW && prevStateB1 == HIGH) 
      {
        if(tQustCt==1)
        {
          tSizePos++;
          if(tSizePos==28) tSizePos=0;      //was 14 TODO: remove comment
          tQustCt=0;
        }
        if(tQustCt==3)
        {
          tMtlPos++;
          if(tMtlPos==10) tMtlPos=0;
          tQustCt=2;
        }
        if(tQustCt==5)
        {
          tTlPos++;
          if(tTlPos==3) tTlPos=0;
          tQustCt=4;
        }
        if(tQustCt==7 && millisHeldB1 <= 600)
        {
          if(thrdOdMeasOffset <= ((thrdOdTol[tSizePos]/2.0)-0.002))
          {
            thrdOdMeasOffset=thrdOdMeasOffset+0.002;
            tQustCt=6;            
          }
          else tQustCt=6;            
        }
        if(tQustCt==7 && millisHeldB1 > 600)      //Sets X axis to 0 during OD turning
        {
          memOffsetX[mX]=mtrNewPosX;            //(stores absolute motor count into array memory location)
          displayLcdBasicsXZ();                 //go update the display
        }
        if(tQustCt==31)
        {
          tNxtOpPos++;
          if(tNxtOpPos==4) tNxtOpPos=0;
          tQustCt=30;
        }
        if(tQustCt==36)
        {
          if(thrdInfeedAdj < 0.1)   //Limit the depth for adjustment pass to within reason.
          {
            thrdInfeedAdj=thrdInfeedAdj+0.002;
            tQustCt=35;            
          }
          else tQustCt=35;            
        }        
        if(modeCt > 999)
        {
          modeCt++;
          if(modeCt==1005) modeCt=1000;
        }
        //----------TAPERSTUFF----------
        if(tprQustCt==2 && millisHeldB1 <= 600)
        {
          if(unitConverter==1)
          {
            tprStkOD=tprStkOD+0.001; 
          }
          else tprStkOD=tprStkOD+(0.0001*25.4);
          tprQustCt=1;     
        }
        if(tprQustCt==9)
        {
          tprNumPnts++;
          if(tprNumPnts==30) tprNumPnts=1;    //skips over '0' so min 2 pnts allowable
          tprQustCt=8;
        }
        if(tprQustCt==11)
        {
          tprCutDir++;
          if(tprCutDir==2) tprCutDir=0;
          tprQustCt=10;
        }
        if(tprQustCt==15 && millisHeldB1 <= 600 && (tprXRad[tprNumPnts]+1) <= tprStkRad)
        {
          tprXRad[tprNumPnts]=tprXRad[tprNumPnts]+1; 
          tprQustCt=14;     
        }
        if(tprQustCt==19 && millisHeldB1 <= 600)
        {
          tprDpthCut=tprDpthCut+4;
          tprQustCt=18;
        }
        if(tprQustCt==22 && millisHeldB1 <= 600)
        {
          if(tprDpthFinCut < (tprDpthCut-5)) tprDpthFinCut=tprDpthFinCut+4;   //'If' prevents finish > rough
          tprQustCt=21;
        }
      }
      if (curStateB1 == HIGH && tprQustCt==2 && millisHeldB1 > 600)
      {
        if(millisHeldB1 <= 5000)
        {
          if(unitConverter==1)
          {
            tprStkOD=tprStkOD+0.100;
          }
          else tprStkOD=tprStkOD+(0.01*25.4);
          delay(70);
        }
        else 
        {
          if(unitConverter==1)
          {
            tprStkOD=tprStkOD+1.000;
          }
          else tprStkOD=tprStkOD+(0.1*25.4);
        }
        delay(230);
        tprQustCt=1;
      }
      if (curStateB1 == HIGH && tprQustCt==15 && millisHeldB1 > 600 && (tprXRad[tprNumPnts]+20) < tprStkRad)
      {
        if(millisHeldB1 <= 5000)
        {
          tprXRad[tprNumPnts]=tprXRad[tprNumPnts]+20;
          delay(70);
        }
        else tprXRad[tprNumPnts]=tprXRad[tprNumPnts]+200;
        delay(230);
        tprQustCt=14;
      }
    }
    prevStateB1 = curStateB1;
    prevMillisHeldB1 = millisHeldB1;
    //_____________________________________________________
    //Button #2:  Selector - (modeButtons)
    //_____________________________________________________
    curStateB2 = digitalRead(inPinB2);
    if (curStateB2 == HIGH && prevStateB2 == LOW && (millis() - startTimeB2) > 200)
    {
      startTimeB2 = millis();         
    }
    millisHeldB2 = (millis() - startTimeB2);
    if (millisHeldB2 > 40) 
    {
      if (curStateB2 == LOW && prevStateB2 == HIGH) 
      {
        if(tQustCt==1)
        {
          tSizePos--;
          if(tSizePos==-1) tSizePos=27;   //was 13 TODO: remove comment
          tQustCt=0;
        }
        if(tQustCt==3)
        {
          tMtlPos--;
          if(tMtlPos==-1) tMtlPos=9;
          tQustCt=2;
        }
        if(tQustCt==5) {  //Do nothing - only B1 works with mat'l selection
        }  
        if(tQustCt==7)
        {
          if(thrdOdMeasOffset >= ((-thrdOdTol[tSizePos]/2.0)+0.002))
          {
            thrdOdMeasOffset=thrdOdMeasOffset-0.002;
            tQustCt=6;            
          }
          else tQustCt=6;            
        }
        if(tQustCt==31)
        {
          tNxtOpPos--;
          if(tNxtOpPos==-1) tNxtOpPos=3;
          tQustCt=30;
        }
        if(tQustCt==36)
        {
          if(thrdInfeedAdj > 0.0)   //Cannot allow negative infeed.
          {
            thrdInfeedAdj=thrdInfeedAdj-0.002;
            tQustCt=35;            
          }
          else tQustCt=35;            
        }        
        if(modeCt > 999)
        {
          modeCt--;
          if(modeCt==999) modeCt=1004;
        }
        //----------TAPERSTUFF----------
        if(tprQustCt==2 && millisHeldB2 <= 600 && tprStkOD > 0.010)
        {
          if(unitConverter==1)
          {
            tprStkOD=tprStkOD-0.001;
          }
          else tprStkOD=tprStkOD-(0.0001*25.4);
          tprQustCt=1;
        }
        if(tprQustCt==9)
        {
          tprNumPnts--;
          if(tprNumPnts==0) tprNumPnts=29;   //skips over '0' so min pnts is 2
          tprQustCt=8;
        }         
        if(tprQustCt==11)
        {
          tprCutDir--;
          if(tprCutDir==-1) tprCutDir=1;
          tprQustCt=10;
        }
        if(tprQustCt==15 && millisHeldB2 <= 600)  //todo: maybe add limit to neg value?
        {
          tprXRad[tprNumPnts]=tprXRad[tprNumPnts]-1; 
          tprQustCt=14;     
        }
        if(tprQustCt==19 && millisHeldB2 <= 600)
        {
          if(tprDpthCut > 13) tprDpthCut=tprDpthCut-4;  //'If' prevents rough < 10
          tprQustCt=18;
        }
        if(tprQustCt==22 && millisHeldB2 <= 600)  //ToDo: force finish < rough && finish < retract (both + & - questions.  PLUS prevent starting > rough
        {
          if(tprDpthFinCut > 5) tprDpthFinCut=tprDpthFinCut-4;   //'If' prevents finish < 1
          tprQustCt=21;
        }
      }
      if (curStateB2 == HIGH && tprQustCt==2 && millisHeldB2 > 600 && tprStkOD > 0.101)
      {
        if(millisHeldB2 <= 5000)
        {
          if(unitConverter==1)
          {
            tprStkOD=tprStkOD-0.100;
          }
          else tprStkOD=tprStkOD-(0.01*25.4);
          delay(70);
        }
        else if(tprStkOD > 2.6)     //0.1*25.4=2.6 - sets minimum so we don't go below zero
        {
          if(unitConverter==1)
          {
            tprStkOD=tprStkOD-1.000;
          }
          else tprStkOD=tprStkOD-(0.1*25.4);
        }
        delay(230);
        tprQustCt=1;      
      }
      if (curStateB2 == HIGH && tprQustCt==15 && millisHeldB2 > 600) //todo: maybe add min value?
      {
        if(millisHeldB2 <= 5000)
        {
          tprXRad[tprNumPnts]=tprXRad[tprNumPnts]-20;
          delay(70);
        }
        else tprXRad[tprNumPnts]=tprXRad[tprNumPnts]-200;
        delay(230);
        tprQustCt=14;
      }     
    }
    prevStateB2 = curStateB2;
    prevMillisHeldB2 = millisHeldB2;
    //_____________________________________________________
    //Button #3:  Accept Input or Go to Mode selector (modeButtons)
    //_____________________________________________________
    curStateB3 = digitalRead(inPinB3);
    if (curStateB3 == HIGH && prevStateB3 == LOW && (millis() - startTimeB3) > 200)
    {
      startTimeB3 = millis();         
    }
    millisHeldB3 = (millis() - startTimeB3);
    if (millisHeldB3 > 120)       //todo?? was 40ms  Bad button?
    {
      if (curStateB3 == LOW && prevStateB3 == HIGH) 
      {
        if((tprQustCt==18 || tprQustCt==19) && tprSpdChange==1)   //to change speed & DOC "mid" profile  todo: set tprSpdChange=0 after finish
        {
          tprQustCt=26;
        }
        if (modeCt==1 && millisHeldB3 <= 600  && tQustCt != 28 && tQustCt != 29)
        {
          tQustCt++;          
        }
        if (modeCt==3 && millisHeldB3 <= 600)
        {
          tprQustCt++;          
        }        
        if (modeCt > 999 && millisHeldB3 <= 600)
        {
          modeCt=modeCt-1000;
          if(modeCt==0) 
          {
            lcdFeedDispBasic();
            displayLcdFeed();
            displayLcdStop();
          }
          if(modeCt==2)       //Internal threads remain todo
          {
            lcd.setCursor(0,3);
            lcd.print("* Mode not available");
            delay(2000);
            modeCt=999;
          }
        }
        if (millisHeldB3 > 600) //Mode select
        {
          modeCt=999;
        }
      }
    }
    prevStateB3 = curStateB3;
    prevMillisHeldB3 = millisHeldB3;
  }
}
//*********************************************************
void arcButtons()
{
  if(modeCt==4)
  {
    //_____________________________________________________
    //Button #1:  Selector + (arcButtons)
    //_____________________________________________________
    curStateB1 = digitalRead(inPinB1);
    if (curStateB1 == HIGH && prevStateB1 == LOW && (millis() - startTimeB1) > 200)
    {
      startTimeB1 = millis();         
    }
    millisHeldB1 = (millis() - startTimeB1);
    if (millisHeldB1 > 40) 
    {
      if (curStateB1 == LOW && prevStateB1 == HIGH) 
      {
        if(arcQustCt==1)
        {
          arcType++;
          if(arcType==2) arcType=0;
          arcQustCt=0;
        }
        if(arcQustCt==3)
        {
          arcInsType++;
          if(arcInsType==2) arcInsType=0;
          arcQustCt=2;
        }
        if(arcQustCt==6 && millisHeldB1 <= 600)
        {
          if(unitConverter==1)
          {
            if(arcInsType==0) arcInsRad=arcInsRad+0.0005;
            else arcInsRad=arcInsRad+0.001;            
          }
          else
          {
            if(arcInsType==0) arcInsRad=arcInsRad+(0.00005*25.4);
            else arcInsRad=arcInsRad+(0.0001*25.4);               
          }
          arcQustCt=5;
        }
        if(arcQustCt==9 && millisHeldB1 <= 600)
        {
          if(unitConverter==1){
            arcStkOD=arcStkOD+0.001; 
          }
          else arcStkOD=arcStkOD+(0.0001*25.4);
          arcQustCt=8;     
        }
        if(arcQustCt==23 && millisHeldB1 <= 600)
        {
          arcTngOdRad=arcTngOdRad+1; 
          arcQustCt=22;     
        }
        if((arcQustCt==27 || arcQustCt==31 || arcQustCt==35) && millisHeldB1 <=600)
        {
          arcCnt++;
          if(arcQustCt==27) arcQustCt=26;
          else if(arcQustCt==31) arcQustCt=30;
          else if(arcQustCt==35) arcQustCt=34;
        }
        if(arcQustCt==40 && millisHeldB1 <= 600)
        {
          arcDpthCutX=arcDpthCutX+4;
          arcQustCt=39;
        }
        if(arcQustCt==43 && millisHeldB1 <= 600)
        {
          if(arcXFin < (arcDpthCutX-5)) arcXFin=arcXFin+4;   //'If' prevents finish > rough
          arcQustCt=42;
        }
        if(arcQustCt==50)
        {
          aNxtOpPos++;
          if(aNxtOpPos==4) aNxtOpPos=0;
          arcQustCt=49;
        }
        if(arcQustCt==53)
        {
          arcZOffset++;
          arcQustCt=52;
        }
        if(arcQustCt==56)
        {
          arcXOffset++;
          arcQustCt=55;
        }
      }
      //-----------------
      if(curStateB1 == HIGH && millisHeldB1 > 600)    //todo general button +- numbers .... limit high end to reasonable and avoid overun lcd
      {
        if(arcQustCt==6)
        {
          if(unitConverter==1)
          {
            if(arcInsType==0) arcInsRad=arcInsRad+0.05;
            else arcInsRad=arcInsRad+0.1;            
          }
          else
          {
            if(arcInsType==0) arcInsRad=arcInsRad+(0.005*25.4);
            else arcInsRad=arcInsRad+(0.01*25.4);               
          }
          if(millisHeldB1 <= 5000) {
            delay(230);
          }
          else if(millisHeldB1 <= 7000) delay(110);
          else if(millisHeldB1 <= 9000) delay(50);
          else delay(5);
          arcQustCt=5;
        }     
        if(arcQustCt==9)
        {
          if(millisHeldB1 <= 3000) {
            if(unitConverter==1) {
              arcStkOD=arcStkOD+0.01;            
            }
            else {
              arcStkOD=arcStkOD+(0.001*25.4);               
            }
            delay(200);
          }
          else if(millisHeldB1 <= 6000) {
            if(unitConverter==1) {
              arcStkOD=arcStkOD+0.1;            
            }
            else {
              arcStkOD=arcStkOD+(0.01*25.4);               
            }
            delay(200);
          }
          else {                              //(millisHeldB1 <= 9000) 
            if(unitConverter==1) {
              arcStkOD=arcStkOD+1;            
            }
            else {
              arcStkOD=arcStkOD+(0.1*25.4);               
            }
            delay(200);
          }
          arcQustCt=8;
        }          
        if(arcQustCt==23)
        {
          if(millisHeldB1 <= 3000) {
            arcTngOdRad=arcTngOdRad+1;
            delay(200);
          }
          else if(millisHeldB1 <= 6000) 
          {
            arcTngOdRad=arcTngOdRad+2;
            delay(100);
          }
          else if(millisHeldB1 <= 9000)
          {
            arcTngOdRad=arcTngOdRad+20;
            delay(100);
          }
          else if(millisHeldB1 > 9000)
          {
            arcTngOdRad=arcTngOdRad+200;
            delay(100);
          }
          arcQustCt=22;
        }
        if(arcQustCt==27 || arcQustCt==31 || arcQustCt==35)
        {
          if(millisHeldB1 <= 3000) {
            arcCnt=arcCnt+1;
            delay(200);
          }
          else if(millisHeldB1 <= 6000) {
            arcCnt=arcCnt+2;
            delay(100);
          }
          else if(millisHeldB1 <= 9000) {
            arcCnt=arcCnt+20;
            delay(100);
          }
          else if(millisHeldB1 > 9000) {
            arcCnt=arcCnt+200;
            delay(100);
          }
          if(arcQustCt==27) arcQustCt=26;
          else if(arcQustCt==31) arcQustCt=30;
          else if(arcQustCt==35) arcQustCt=34;
        }
        if(arcQustCt==53)
        {
          if(millisHeldB1 <= 2000) {
            arcZOffset++;
            delay(200);
          }
          if(millisHeldB1 <= 6000) {
            if(unitConverter=1) {
              arcZOffset=arcZOffset+(0.1*(zMtrCntPerRev/zPitch));
            }
            else arcZOffset=arcZOffset+(0.01*unitConverter*(zMtrCntPerRev/zPitch));
            delay(100);
          }
          if(millisHeldB1 > 6000) {
            if(unitConverter=1) {
              arcZOffset=arcZOffset+(1.0*(zMtrCntPerRev/zPitch));
            }
            else arcZOffset=arcZOffset+(0.1*unitConverter*(zMtrCntPerRev/zPitch));
            delay(100);
          }
          arcQustCt=52;
        }
        if(arcQustCt==56)
        {
          if(millisHeldB1 <= 3000) {
            arcXOffset++;
            delay(200);
          }
          if(millisHeldB1 <= 7000) {
            if(unitConverter=1) {
              arcXOffset=arcXOffset+(0.1*(xMtrCntPerRev/xPitch));
            }
            else arcXOffset=arcXOffset+(0.01*unitConverter*(xMtrCntPerRev/xPitch));
            delay(180);
          }
          if(millisHeldB1 > 7000) {
            if(unitConverter=1) {
              arcXOffset=arcXOffset+(1.0*(xMtrCntPerRev/xPitch));
            }
            else arcXOffset=arcXOffset+(0.1*unitConverter*(xMtrCntPerRev/xPitch));
            delay(180);
          }
          arcQustCt=55;
        }

      }
    }
    prevStateB1 = curStateB1;
    prevMillisHeldB1 = millisHeldB1;
    //_____________________________________________________
    //Button #2:  Selector - (arcButtons)
    //_____________________________________________________
    curStateB2 = digitalRead(inPinB2);
    if (curStateB2 == HIGH && prevStateB2 == LOW && (millis() - startTimeB2) > 200)
    {
      startTimeB2 = millis();         
    }
    millisHeldB2 = (millis() - startTimeB2);
    if (millisHeldB2 > 40) 
    {
      if (curStateB2 == LOW && prevStateB2 == HIGH) 
      {
        if(arcQustCt==1)
        {
          arcType--;
          if(arcType==-1) arcType=1;
          arcQustCt=0;
        }
        if(arcQustCt==3)
        {
          arcInsType--;
          if(arcInsType==-1) arcInsType=1;
          arcQustCt=2;
        }
        if(arcQustCt==6 && millisHeldB2 <= 600)
        {
          if(unitConverter==1)
          {
            if((arcInsType==0 && arcInsRad <= 0.0005) || (arcInsType==1 && arcInsRad <= 0.001)) arcInsRad=0.0;
            else if(arcInsType==0) arcInsRad=arcInsRad-0.0005;
            else arcInsRad=arcInsRad-0.001;            
          }
          else
          {
            if((arcInsType==0 && arcInsRad <= (0.00005*25.4)) || (arcInsType==1 && arcInsRad <= (0.0001*25.4))) arcInsRad=0.0;
            else if(arcInsType==0) arcInsRad=arcInsRad-(0.00005*25.4);
            else arcInsRad=arcInsRad-(0.0001*25.4);               
          }
            arcQustCt=5;
        }
        if(arcQustCt==9 && millisHeldB2 <= 600)
        {
          if(unitConverter==1)
          {
            if(arcStkOD <=0.001) arcStkOD=0.0;
            else arcStkOD=arcStkOD-0.001; 
          }
          else
          {
            if(arcStkOD <= (0.0001*25.4)) arcStkOD=0.0;
            else arcStkOD=arcStkOD-(0.0001*25.4);
          }
          arcQustCt=8;
        }
        if(arcQustCt==23 && millisHeldB2 <= 600)
        {
          arcTngOdRad=arcTngOdRad-1;
          arcQustCt=22;
        }
        if((arcQustCt==27 || arcQustCt==31 || arcQustCt==35) && millisHeldB2 <=600)
        {
          if(arcCnt > 0)
          {
            arcCnt--;
          }
          if(arcQustCt==27) arcQustCt=26;
          else if(arcQustCt==31) arcQustCt=30;
          else if(arcQustCt==35) arcQustCt=34;
        }
        if(arcQustCt==40 && millisHeldB2 <= 600)
        {
          if(arcDpthCutX > 13) arcDpthCutX=arcDpthCutX-4;  //'If' prevents rough < 10
          arcQustCt=39;
        }
        if(arcQustCt==43 && millisHeldB2 <= 600)  //ToDo: force finish < rough && finish < retract (both + & - questions.  PLUS prevent starting > rough
        {
          if(arcXFin > 5) arcXFin=arcXFin-4;   //'If' prevents finish < 1
          arcQustCt=42;
        }       
        if(arcQustCt==50)
        {
          aNxtOpPos--;
          if(aNxtOpPos==-1) aNxtOpPos=3;
          arcQustCt=49;
        }
        if(arcQustCt==53 && arcZOffset >= 1)
        {
          arcZOffset--;
          arcQustCt=52;
        }
        if(arcQustCt==56 && arcXOffset >= 1)
        {
          arcXOffset--;
          arcQustCt=55;
        }
      }
      //-----------------
      if(curStateB2 == HIGH && millisHeldB2 > 600)
      {
        if(arcQustCt==6)
        {
          if(unitConverter==1)
          {
            if((arcInsType==0 && arcInsRad <= 0.05) || (arcInsType==1 && arcInsRad <= 0.1)) arcInsRad=0.0;
            else if(arcInsType==0) arcInsRad=arcInsRad-0.05;
            else arcInsRad=arcInsRad-0.1;            
          }
          else
          {
            if((arcInsType==0 && arcInsRad <= (0.005*25.4)) || (arcInsType==1 && arcInsRad <= (0.01*25.4))) arcInsRad=0.0;
            else if(arcInsType==0) arcInsRad=arcInsRad-(0.005*25.4);
            else arcInsRad=arcInsRad-(0.01*25.4);               
          }
          if(millisHeldB2 <= 5000) {
            delay(230);
          }
          else if(millisHeldB2 <= 7000) delay(110);
          else if(millisHeldB2 <= 9000) delay(50);
          else delay(5);
          arcQustCt=5;
        }
        if(arcQustCt==9)
        {
          if(millisHeldB2 <= 3000) {
            if(unitConverter==1) {
              if(arcStkOD <= 0.01) arcStkOD=0.0;
              else arcStkOD=arcStkOD-0.01;            
            }
            else {
              if(arcStkOD <= 0.001*25.4) arcStkOD=0.0;
              else arcStkOD=arcStkOD-(0.001*25.4);               
            }
            delay(200);
          }
          else if(millisHeldB2 <= 6000) {
            if(unitConverter==1) {
              if(arcStkOD <= 0.1) arcStkOD=0.0;
              else arcStkOD=arcStkOD-0.1;            
            }
            else {
              if(arcStkOD <= 0.01*25.4) arcStkOD=0.0;
              else arcStkOD=arcStkOD-(0.01*25.4);               
            }
            delay(200);
          }
          else {
            if(unitConverter==1) {
              if(arcStkOD <= 1) arcStkOD=0.0;
              else arcStkOD=arcStkOD-1;            
            }
            else {
              if(arcStkOD <= 0.1*25.4) arcStkOD=0.0;
              else arcStkOD=arcStkOD-(0.1*25.4);               
            }
            delay(200);
          }
          arcQustCt=8;
        }    
        if(arcQustCt==23)
        {
          if(millisHeldB2 <= 3000) {
            arcTngOdRad=arcTngOdRad-1;
            delay(200);
          }
          else if(millisHeldB2 <= 6000) 
          {
            arcTngOdRad=arcTngOdRad-2;
            delay(100);
          }
          else if(millisHeldB2 <= 9000) 
          {
            arcTngOdRad=arcTngOdRad-20;
            delay(100);
          }
          else if(millisHeldB2 > 9000) 
          {
            arcTngOdRad=arcTngOdRad-200;
            delay(100);
          }
          arcQustCt=22;
        }            
        if(arcQustCt==27 || arcQustCt==31 || arcQustCt==35)
        {
          if((millisHeldB2 <= 3000 && arcCnt > 0) || (millisHeldB2 > 9000 && arcCnt > 0 && arcCnt < 2)) {
            arcCnt--;
            delay(200);
          }
          else if((millisHeldB2 <= 6000 && arcCnt > 1) || (millisHeldB2 > 9000 && arcCnt > 1 && arcCnt <= 19)) {
            arcCnt=arcCnt-2;
            delay(100);
          }
          else if((millisHeldB2 <= 9000 && arcCnt > 19) || (millisHeldB2 > 9000 && arcCnt > 19 && arcCnt <= 199)) {
            arcCnt=arcCnt-20;
            delay(100);
          }
          else if(millisHeldB2 > 9000 && arcCnt > 199) {
            arcCnt=arcCnt-200;
            delay(100);
          }
          if(arcQustCt==27) arcQustCt=26;
          else if(arcQustCt==31) arcQustCt=30;
          else if(arcQustCt==35) arcQustCt=34;
        }     

        if(arcQustCt==53)
        {
          if(millisHeldB2 <= 2000) {
            arcZOffset--;
            delay(200);
          }
          if(millisHeldB2 <= 6000) {
            if(unitConverter=1) {
              arcZOffset=arcZOffset-(0.1*(zMtrCntPerRev/zPitch));
            }
            else arcZOffset=arcZOffset-(0.01*unitConverter*(zMtrCntPerRev/zPitch));
            delay(100);
          }
          if(millisHeldB2 > 6000) {
            if(unitConverter=1) {
              arcZOffset=arcZOffset-(1.0*(zMtrCntPerRev/zPitch));
            }
            else arcZOffset=arcZOffset-(0.1*unitConverter*(zMtrCntPerRev/zPitch));
            delay(100);
          }
          arcQustCt=52;
        }
        if(arcQustCt==56)
        {
          if(millisHeldB2 <= 3000) {
            arcXOffset--;
            delay(200);
          }
          if(millisHeldB2 <= 7000) {
            if(unitConverter=1) {
              arcXOffset=arcXOffset-(0.1*(xMtrCntPerRev/xPitch));
            }
            else arcXOffset=arcXOffset-(0.01*unitConverter*(xMtrCntPerRev/xPitch));
            delay(180);
          }
          if(millisHeldB2 > 7000) {
            if(unitConverter=1) {
              arcXOffset=arcXOffset-(1.0*(xMtrCntPerRev/xPitch));
            }
            else arcXOffset=arcXOffset-(0.1*unitConverter*(xMtrCntPerRev/xPitch));
            delay(180);
          }
          arcQustCt=55;
        }
        
      }
    }
    prevStateB2 = curStateB2;
    prevMillisHeldB2 = millisHeldB2;
    //_____________________________________________________
    //Button #3:  Accept Input or Go to Mode selector (arcButtons)
    //_____________________________________________________
    curStateB3=digitalRead(inPinB3);
    if(curStateB3==HIGH && prevStateB3==LOW && (millis()-startTimeB3) > 200)
    {
      startTimeB3=millis();
    }
    millisHeldB3=(millis()-startTimeB3);
    if(millisHeldB3 > 120)
    {
      if(curStateB3==LOW && prevStateB3==HIGH)
      {
        if(millisHeldB3 <= 600)
        {
          arcQustCt=arcQustCt+1;
        }
        //if(millisHeldB3 > 600)
        //{
          //modeCt=999;
        //}
      }
    }
    prevStateB3=curStateB3;
    prevMillisHeldB3=millisHeldB3;
  }
}
