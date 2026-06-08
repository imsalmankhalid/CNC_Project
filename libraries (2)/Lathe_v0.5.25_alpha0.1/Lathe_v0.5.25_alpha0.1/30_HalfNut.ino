//*********************************************************
//  zMotorFeed()
//*********************************************************
void zMotorFeed()   //HalfNut engagement
{
  if(modeCt==0 || tQustCt==7 || tprQustCt==2 || arcQustCt==9)
  {
    //Reset halfnut lever
    curStateS1 = digitalRead(inPinS1);  //Checks current halfnut lever status
    
    if(curStateS1==LOW)                 //IF Halfnut lever is OFF
    {
      prevStateS1=LOW;                  //Set prevStateS1 halfnut lever OFF -> resets lever to allow another feed.
    }
    
    //Move Z axis motor defined position and determine if successful
    if(curStateS1 == HIGH && prevStateS1 == LOW)
    {
      delay(50);               //delay 100 - simple debounce tool
      //displayLcdFeed();         //this also includes spindle lookup  ToDo: not required as we're continuous lookup on RPM/IPM
    }
    curStateS1 = digitalRead(inPinS1);
    if(curStateS1 == HIGH && prevStateS1 == LOW)    //Run "If" lever 'high' again to make sure we want to move
    {
      prevStateS1=HIGH;         //This insures single operation of code while halfnut is engaged beyond finishing feed

      tempMtrPosZ=mtrNewPosZ;   //save 'start' motor cnts: required to offset mtr position cnt after feed
      tempEncPosZ=encNewPosZ;   //to prevent Z motion during halfnut move
      tempEncPosX=encNewPosX;   //to prevent X motion during halfnut move

      //Determine step size required for input speed
      zFeedStepFloat=mtrMinDelay*feedRateMm*zMtrCntPerRev/(60.0*1000000.0*zPitch);
      zFeedStep=round(zFeedStepFloat+0.5);  //Next largest integer for step size
      if(zFeedStep > 1 && memStopZ[mZ] > tempMtrPosZ) {
        zFeedStepPre=round(((abs(tempMtrPosZ-memStopZ[mZ])/float(zFeedStep))-int(abs(tempMtrPosZ-memStopZ[mZ])/zFeedStep))*zFeedStep);
      }
      else zFeedStepPre=0;
      //Serial.println(""); Serial.print("zFeedStep= "); Serial.print(zFeedStep); Serial.print(" delta steps= "); Serial.println(abs(tempMtrPosZ-memStopZ[mZ]));
      //Serial.print("zFeedStepPre= "); Serial.println(zFeedStepPre);

      //Determine delays required for given step size and speed
      zFeedDelay=(1/(((feedRateMm)/zPitch)*float(zMtrCntPerRev/float(zFeedStep))))*(60.0*1000000.0)-zFeedDelayCode;     //=us/cnt
      if(zFeedDelay > 16000) {              //Because max 16000 accurate for microsecond delays
        zFeedDelayOver=zFeedDelay-16000;
        zFeedDelay=16000;
        zFeedDelOvCnt=zFeedDelayOver/16000.0;  //int results in # times to delay full 16000
        zFeedDelayOver=zFeedDelayOver-(16000*zFeedDelOvCnt);
      }
      else {
        zFeedDelayOver=0; zFeedDelOvCnt=0;
      }

      //Find out how many mtr counts to move 
      //If user has set stop and carriage is + that location. Both values are '-' reversed z
      if(memStopZ[mZ]>tempMtrPosZ && memStopZ<999999) //TODO: add [mZ] to memStopZ - why does this work now???
      {
        halfnutMoveDist=abs(tempMtrPosZ-memStopZ[mZ]); //(mtr counts) Results always '-' but abs='+'
      }
      else 
      {
        halfnutMoveDist=zMaxMtrCnt;       //If no setting just move length of bed (+).  Even if stop=current positon
      }
      //Serial.println("");
      //Serial.print("MtrNewPosZ= "); Serial.println(mtrNewPosZ);
      //Serial.print("memStopZ= "); Serial.println(memStopZ[mZ]);
      
      int k=1;
      while(k>0)                //We step into a infinite while loop for motion. todo: use move dist instead of 'k'
      { 
        if(zFeedDelayOver!=0) {
          for(int u = 0; u < zFeedDelOvCnt; u++) {
            delayMicroseconds(16000);
          }
          delayMicroseconds(zFeedDelayOver);
        }  
        delayMicroseconds(zFeedDelay);
        //if(!Z.commandDone())
        //{
        //  lcd.setCursor(11,2);
        //  lcd.print("ER: Z-HfN"); 
          //todo: stop motor here and go into loop
        //}      

        if(zFeedStepPre > 0) {
          Z.move(zFeedStepPre);            //Move initial "remander" step
          actualMoveNew=actualMoveOld+zFeedStepPre;
          zFeedStepPre=0;
        }
        else {
          Z.move(zFeedStep);            //'+' moves motor -z.
          actualMoveNew=actualMoveOld+zFeedStep;
        }
        
        curStateS1 = digitalRead(inPinS1);

        //See if we stop or continue
        if(actualMoveNew < halfnutMoveDist && curStateS1==HIGH) //INPROCESS: more to move && lever still 'high'
        {
          k=k+1;                      //continue loop
        }
        else if(actualMoveNew >= halfnutMoveDist || actualMoveNew!=halfnutMoveDist)   //TODO: don't understand  maybe change != to > .. now remove || 
                                      //COMPLETE-OK motor "not busy" (both now - don't care)
        {
          zAxisEnc.write(tempEncPosZ);  //todo:  why - set to 0. Encoder gets set to virtual move amount
          encNewPosZ=tempEncPosZ;
          encOldPosZ=tempEncPosZ;
          xAxisEnc.write(tempEncPosX);
          encNewPosX=tempEncPosX;
          encOldPosX=tempEncPosX;
          mtrNewPosZ = (tempMtrPosZ+actualMoveNew); //Temp set for display update - will be rewritten by encZ
          mtrOldPosZ = mtrNewPosZ;
          //Serial.print("mtrNewPosZ End = "); Serial.println(mtrNewPosZ);

          displayLcdFullValZ();                   //update Z display with adjusted position.      
          displayLcdStop();
          k=0;                                    //ends loop (complete)
        }
        else    //error
        {
          lcd.setCursor(11,2);
          lcd.print("ER:HNelse"); 
        }
        actualMoveOld=actualMoveNew;
      }
      //tempMtrPosZ=0;
      actualMoveNew=0;                      //Reset to '0' to be ready for next time halfnut engaged
      actualMoveOld=0;                      //Reset to '0' to be ready for next time halfnut engaged
    }  
  }  
}
