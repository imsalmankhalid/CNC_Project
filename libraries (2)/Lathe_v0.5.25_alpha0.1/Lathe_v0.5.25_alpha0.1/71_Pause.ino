//*********************************************************
//  tprResetSpeed()  resetButton()
//*********************************************************
void tprResetSpeed()
{
  tprQustCt=18;
  
  lcd.setCursor(0,2);
  lcd.print("Adjust...  DOC=     ");
  lcd.setCursor(0,3);
  lcd.print("RPM=      IPM=      ");
  
  while(tprQustCt==18 || tprQustCt==19)
  {
    if(tprQustCt==18)
    {
      lcd.setCursor(15,2);
      if(unitConverter==1) lcd.print((tprDpthCut*(xPitch/float(xMtrCntPerRev))), 2);
      else lcd.print(((tprDpthCut*(xPitch/float(xMtrCntPerRev)))/unitConverter), 3);
      tprQustCt=19;      
    }

    //potentiometer();      //todo - just removed - ok??  check function
    //delay(500);         //todo remove if not needed??
    calcSpeed();            //grabs values but does not use print (also gets rpm)........ todo: remove as pot has this when changes....
    displayLcdSpeed();
    calcFeed();
    displayLcdFeed();
    lcd.setCursor(5,3);
    lcd.print(spindleRpmChJoin);
    lcd.setCursor(15,3);
    lcd.print(feedRateChJoin);
    
    modeButtons();        //B3 will set tprQustCt=26 to get out of loop and return to normal profile loop
  }
  lcd.setCursor(0,2);
  lcd.print("Profile Run/B3:Pause");
  lcd.setCursor(0,3);
  lcd.print("Pass     of         ");
  tprPassTtl=round(0.49+1.0+(abs(tprXRadRunMaxSave-tprXRadOffst[tprMaxArPos])/tprDpthCut));       //0.49 is remainder rough & 1.0 is finish pass
  lcd.setCursor(12,3);
  lcd.print("   ");
  lcd.setCursor(12,3);
  lcd.print(tprPassTtl);
  tprPassCrnt=tprPassTtl-round(0.49+1.0+abs((tprXRadRun[tprMaxArPos]-tprXRadOffst[tprMaxArPos])/tprDpthCut)); 
  lcd.setCursor(5,3);
  lcd.print("   ");
  lcd.setCursor(5,3);
  lcd.print(tprPassCrnt);
}
//*********************************************************
void resetButton()
{
  //Button #3(4):  Used to Pause profile mode rough cut so we can adjust RPM, IPM, DOC
  //_____________________________________________________
  curStateB4=digitalRead(inPinB3);
  if(curStateB4==HIGH && prevStateB4==LOW && (millis()-startTimeB4) > 200)
  {
    startTimeB4=millis();
  }
  millisHeldB4=(millis()-startTimeB4);
  if(millisHeldB4 > 120)       //todo?? was 40ms  Bad button?
  {
    if(curStateB4==LOW && prevStateB4==HIGH)  //does not work when prevStateB4=HIGH added
    {
      if(tprSpdChange==2 && tprCntl==0)      //only allowed during roughing  todo: change to ==2
      {
        tprSpdChange=1;
        lcd.setCursor(15,2);
        lcd.print("*SET*");
      }
    }
  }
  prevStateB4=curStateB4;
  //prevMillisHeldB4=millisHeldB4;    
}
//*********************************************************
