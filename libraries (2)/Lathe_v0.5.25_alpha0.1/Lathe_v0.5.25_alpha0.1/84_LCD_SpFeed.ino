//*********************************************************
//  displayLcdSpeed()  displayLcdFeed()  displayLcdStop()
//*********************************************************
void displayLcdSpeed()
{
  if((abs(spindleRpmOld-spindleRpm)) > 1.9) {
    spindleRpmOld=spindleRpm;
    dtostrf(abs(spindleRpm),4,0,spindleRpmCh);  //Set string w/ 0 decimals (blanks will auto fill in: 0000)
    spindleRpmChJoin = spindleRpmCh; 
    if((tprQustCt!=23 || arcQustCt!=44 || tprQustCt!=19) && modeCt==0) {   //Request from taper/arc function needs values but no display
      lcd.setCursor(6,2);
      lcd.print(spindleRpmChJoin);
    }
  }  
}
//*********************************************************
void displayLcdFeed()
{
  if((abs(feedRateOld-feedRate)) > 0.09) {  //Display only increments by 0.1 IPM steps
    feedRateOld=feedRate;
    dtostrf(abs(feedRate),4,1,feedRateCh);  //Set string w/ 1 decimals (blanks will auto fill in: 00.0)
    feedRateChJoin = feedRateCh;
    if((tprQustCt!=23 || arcQustCt!=44 || tprQustCt!=19) && modeCt==0) {   //Request from taper/arc function needs values but no display
      lcd.setCursor(6,3);
      lcd.print(feedRateChJoin);
    }
  }
}
//*********************************************************
void displayLcdStop()
{
  //print halfnut stop set point relative to 0.0, or "++++" if apron negative of set point, or "Not Set".
  //Set point value is current ABSOLUTE mtr position when button set NOT accounting for memOffsetZ[mZ] until display
  //memStopZ[mZ] is a stored value and will not change until button 3 sets new.  Set to 999999 in void setup.
  //toggleStop:  0=Initial, 1="Not Set", 2="-234.67", 3="+++>>>"
  //toggleStop set to '0' after: memSet, stopSet(button), mm/inch
  //Call displayLcdStop() after: halfNut, EncZ, Button3
  
  displayLinStopZ=(((memStopZ[mZ]-memOffsetZ[mZ])*zPitch)/zMtrCntPerRev)/unitConverter;
  
  if(displayLinStopZ<0.00001 && displayLinStopZ>-0.00001)       //TODO: fix/remove
  {
    displayLinStopZ=-0.0;
  }
  
  //Set "Not Set" initial '0' (or revert to 999999 although does not happen in code)
  if(toggleStopZ[mZ]==0 || (memStopZ[mZ]==999999 && toggleStopZ[mZ]!=1) && modeCt==0)
  {
    lcd.setCursor(12,3);
    lcd.print(" Not Set");        //8 character write always
    toggleStopZ[mZ]=1;
  }
  else if(memStopZ[mZ]!=999999 && mtrNewPosZ > memStopZ[mZ] && toggleStopZ[mZ]!=3 && modeCt==0)   //NOK: Apron neg of stop
  {
    lcd.setCursor(12,3);
    lcd.print(" +++>>> ");
    toggleStopZ[mZ]=3;
  }
  else if(memStopZ[mZ]!=999999 && mtrNewPosZ <= memStopZ[mZ] && toggleStopZ[mZ]!=2 && modeCt==0)  //OK:Arpon pos of stop
  {
    if (unitConverter==1.0)
    {
      dtostrf(abs(displayLinStopZ),7,3,disLinStopChZ);  //Set string if mm w/ 3 dec (000.000)
    }
    else
    {
      dtostrf(abs(displayLinStopZ),7,4,disLinStopChZ);  //Set string if inch w/ 4 dec (00.0000)
    }
    disLinStopChZJoin = disLinStopChZ;
    lcd.setCursor(13,3);                                //cursor position 12 retained for +/- sign
    lcd.print(disLinStopChZJoin.substring(0,7));
    lcd.setCursor(12,3);
    if(memStopZ[mZ]<memOffsetZ[mZ])
    {
     lcd.print("+");
    }
    else if(memStopZ[mZ]>memOffsetZ[mZ])
    {
      lcd.print("-");
    }
    else
    {
      lcd.print(" ");
    }
    toggleStopZ[mZ]=2;
  }
}
