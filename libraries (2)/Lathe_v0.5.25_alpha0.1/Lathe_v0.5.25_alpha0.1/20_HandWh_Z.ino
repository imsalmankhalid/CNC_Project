//*********************************************************
//  zEnc()
//*********************************************************
void zEnc()
{
  encNewPosZ = zAxisEnc.read(); 
  if (encNewPosZ != encOldPosZ)
  {
    tempEncPosX=encNewPosX;                 //to prevent X motion during halfnut move
    zEncBuffer=zEncBuffer+(float(encNewPosZ)-float(encOldPosZ));  //Calculate buffer
    zBufTog=1;                              //Set LCD toggle to 1
    zTime1st=micros();                      //'seed' initial value to be used on first delay time evaluation
    //Serial.println(zEncBuffer);

    while(zEncBuffer >= zCountAdjInv || zEncBuffer <= -(zCountAdjInv))  //Is buffer large enough to move 1 MtrCnt? (0.625 encCnt / 1 mtrCnt)
    {                                         //TODO: when "<" used (not <=) the (-)1 MtrCnt does not initiate move and can act as Debounce.
      if(abs(zEncBuffer) > zMaxEncBuf) {    //Protection against HW rotation above max defined
        if(zEncBuffer > 0) zEncBuffer=zMaxEncBuf;
        else zEncBuffer=-(zMaxEncBuf);
      }
      zCalcVel=(abs(zEncBuffer)*zMaxVel)/zMaxEncBuf;
      zDelay1stp=(zPitch/(zCalcVel*zMtrCntPerRev))*60.0*1000000.0;  //Delay for single motor cnt
      if(zDelay1stp > z0Time) zDelay1stp=z0Time;                //Protection against delay value too large "too slow". 
      //Serial.print("    zCalcVel= "); Serial.print(zCalcVel); Serial.print("    zDelay1stp= "); Serial.println(zDelay1stp);  

      if(zCalcVel <= zVelLimitA) {                              //zVelLimitA = 60 mm/min
        zStepSize=round((zATime/zDelay1stp)+0.5);                   //# mtr cnts per cycle required
        zDelayNstp=zStepSize*zDelay1stp;                            //re-calculated delay for adjusted step/cycle size
        //Serial.print("    zStepSize= "); Serial.print(zStepSize); Serial.print("    zDelayNstp= "); Serial.println(zDelayNstp);
      }
      else if(zCalcVel <= zVelLimitB) {                         //zVelLimitB = 600 mm/min
        zStepSize=round((zBTime/zDelay1stp)+0.5);
        zDelayNstp=zStepSize*zDelay1stp;
      }
      else if(zCalcVel <= zVelLimitC) {                         //zVelLimitC = 800 mm/min
        zStepSize=round((zCTime/zDelay1stp)+0.5);
        zDelayNstp=zStepSize*zDelay1stp;
      }
      else if(zCalcVel <= zVelLimitD) {                         //zVelLimitD = 1600 mm/min
        zStepSize=round((zDTime/zDelay1stp)+0.5);
        zDelayNstp=zStepSize*zDelay1stp;
      }
      else {                                                    //else >D = E
        zStepSize=round((zETime/zDelay1stp)+0.5);
        zDelayNstp=zStepSize*zDelay1stp;
      }

      if (zEncBuffer < 0.0) {               //simply switch signs of step if neg.
        zStepSize=-(zStepSize);
      }

      mtrNewPosZ=mtrOldPosZ+zStepSize;      //Calculates where motor is (counts) from absolute (machine start)
      //Serial.print("    mtrNewPosZ= "); Serial.println(mtrNewPosZ);
      if(zCalcVel <= zVelLimitD) {            //any velocity > 'D' limit gets no LCD update
        displayLcdPartValZ();               //goto write value for Z - pass along mtrNewPosZ  ***was after delay/step***
      }

      zTime2nd=micros();
      zDeltaT=zDelayNstp-(zTime2nd-zTime1st);
      if(zDeltaT < 0) zDelay=0;                         //protect overflow & any LCD which takes longer than expected
      else zDelay=zDeltaT;                              //subtract exact time taken for LCD + code
      //if(zDelayNstp >= zETime && zDelayNstp < zDTime) Serial.println(zTime2nd-zTime1st);
      delayMicroseconds(zDelay);                        //Delay sets velocity
      if(!Z.commandDone()) {
        lcd.clear();
        lcd.setCursor(11,2);
        lcd.print("ER: Z-Mtr"); 
        for(int uuu=0; uuu == 0; uuu=0) uuu=0;
      }
      
      Z.move(zStepSize);
      zTime1st=micros();

      if(zBufTog==1){zBufTog--;} else{zBufTog++;}  //Set LCD toggle 1 to 0 for alternating write value to display
      mtrOldPosZ=mtrNewPosZ;
      encOldPosZ=encNewPosZ;
      zEncBufferOld=zEncBuffer;

      encNewPosZ=zAxisEnc.read();       //Read new encoder position
      //Serial.print("    encNewPosZ= "); Serial.println(encNewPosZ);
      zEncBuffer=zEncBufferOld+(float(encNewPosZ)-float(encOldPosZ))-(float(zStepSize)*zCountAdjInv);   //set new buffer amount
      //Serial.print("    zEncBuffer= "); Serial.println(zEncBuffer);
      }
    encOldPosZ=encNewPosZ;              //when loops stops working (OR only IF performed) then set EncOld to New value
    displayLcdStop();
    
    xAxisEnc.write(tempEncPosX);        //when loop stops or only 'if': reSet X encoder to prevent move
    encNewPosX=tempEncPosX;
    encOldPosX=tempEncPosX;
  }
}
