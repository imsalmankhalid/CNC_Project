//*********************************************************
//  xEnc()
//*********************************************************
void xEnc()
{
  encNewPosX = xAxisEnc.read(); 
  if (encNewPosX != encOldPosX)
  {
    tempEncPosZ=encNewPosZ;                 //to prevent Z motion during halfnut move
    xEncBuffer=xEncBuffer+(float(encNewPosX)-float(encOldPosX));  //Calculate buffer
    xBufTog=1;                              //Set LCD toggle to 1
    xTime1st=micros();                      //'seed' initial value to be used on first delay time evaluation
    //Serial.println(xEncBuffer);
    
    while(xEncBuffer >= xCountAdjInv || xEncBuffer <= -(xCountAdjInv))  //Is buffer large enough to move 1 MtrCnt? (2.5 encCnt / 1 mtrCnt)
    {                                         //TODO: when "<" used (not <=) the (-)1 MtrCnt does not initiate move and can act as Debounce.
      if(abs(xEncBuffer) > xMaxEncBuf) {    //Protection against HW rotation above max defined
        if(xEncBuffer > 0) xEncBuffer=xMaxEncBuf;
        else xEncBuffer=-(xMaxEncBuf);
      }
      xCalcVel=(abs(xEncBuffer)*xMaxVel)/xMaxEncBuf;
      xDelay1stp=(xPitch/(xCalcVel*xMtrCntPerRev))*60*1000000;  //Delay for single motor cnt
      if(xDelay1stp > x0Time) xDelay1stp=x0Time;                //Protection against delay value too large "too slow".
      //Serial.print("    xCalcVel= "); Serial.print(xCalcVel); Serial.print("    xDelay1stp= "); Serial.println(xDelay1stp); 

      if(xCalcVel <= xVelLimitA) {                              //xVelLimitA = 60 mm/min
        xStepSize=round((xATime/xDelay1stp)+0.5);                   //# mtr cnts per cycle required
        xDelayNstp=xStepSize*xDelay1stp;                            //re-calculated delay for adjusted step/cycle size
        //Serial.print("    xStepSize= "); Serial.print(xStepSize); Serial.print("    xDelayNstp= "); Serial.println(xDelayNstp);
      }
      else if(xCalcVel <= xVelLimitB) {                         //xVelLimitB = 600 mm/min
        xStepSize=round((xBTime/xDelay1stp)+0.5);
        xDelayNstp=xStepSize*xDelay1stp;
      }
      else if(xCalcVel <= xVelLimitC) {                         //xVelLimitC = 800 mm/min
        xStepSize=round((xCTime/xDelay1stp)+0.5);
        xDelayNstp=xStepSize*xDelay1stp;
      }
      else if(xCalcVel <= xVelLimitD) {                         //xVelLimitD = 1600 mm/min
        xStepSize=round((xDTime/xDelay1stp)+0.5);
        xDelayNstp=xStepSize*xDelay1stp;
      }
      else {                                                    //else >D = E
        xStepSize=round((xETime/xDelay1stp)+0.5);
        xDelayNstp=xStepSize*xDelay1stp;
      }

      if (xEncBuffer < 0.0) {               //simply switch signs of step if neg.
        xStepSize=-(xStepSize);
      }

      mtrNewPosX=mtrOldPosX+xStepSize;      //Calculates where motor is (counts) from absolute (machine start)
      //Serial.print("    mtrNewPosX= "); Serial.println(mtrNewPosX);
      if(xCalcVel <= xVelLimitD) {            //any velocity > 'D' limit gets no LCD update
        displayLcdPartValX();               //goto write value for X - pass along mtrNewPosX  ***was after delay/step***
      }

      xTime2nd=micros();
      xDeltaT=xDelayNstp-(xTime2nd-xTime1st);
      //Serial.print("    xDeltaT= "); Serial.println(xDeltaT);
      if(xDeltaT < 0) xDelay=0;                         //protect overflow & any LCD which takes longer than expected
      else xDelay=xDeltaT;                              //subtract exact time taken for LCD + code
      //if(xDelayNstp >= xETime && xDelayNstp < xDTime) Serial.println(xTime2nd-xTime1st);
      delayMicroseconds(xDelay);                        //Delay sets velocity
      if(!X.commandDone()) {
        lcd.clear();
        lcd.setCursor(11,2);
        lcd.print("ER: X-Mtr"); 
        for(int uuu=0; uuu == 0; uuu=0) uuu=0;
      }
      
      X.move(xStepSize);
      xTime1st=micros();

      if(xBufTog==1){xBufTog--;} else{xBufTog++;}  //Set LCD toggle 1 to 0 for alternating write value to display
      mtrOldPosX=mtrNewPosX;
      encOldPosX=encNewPosX;
      xEncBufferOld=xEncBuffer;

      encNewPosX=xAxisEnc.read();       //Read new encoder position
      //Serial.print("    encNewPosX= "); Serial.println(encNewPosX);
      xEncBuffer=xEncBufferOld+(float(encNewPosX)-float(encOldPosX))-(float(xStepSize)*xCountAdjInv);   //set new buffer amount  
      //Serial.print("    xEncBuffer= "); Serial.println(xEncBuffer);
      }
    encOldPosX=encNewPosX;              //when loops stops working (OR only IF performed) then set EncOld to New value
    
    zAxisEnc.write(tempEncPosZ);        //when loop stops or only 'if': reSet Z encoder to prevent move
    encNewPosZ=tempEncPosZ;
    encOldPosZ=tempEncPosZ;  
  }
}
