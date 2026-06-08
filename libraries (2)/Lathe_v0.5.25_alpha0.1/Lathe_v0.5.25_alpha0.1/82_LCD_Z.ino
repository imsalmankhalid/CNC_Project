//*********************************************************
//  displayLcdFullValZ()  displayLcdPartValZ()
//*********************************************************
void displayLcdFullValZ()   //prints full value with +/- used after halfnut move + initial + after button change
{
  zValNumNew=-(((float(mtrNewPosZ)-float(memOffsetZ[mZ]))*zPitch)/float(zMtrCntPerRev))/unitConverter;    
                            //SET NEG TO DISPLAY CORRECT
  lcd.setCursor(6,1);
  if (unitConverter==1.0)                 
  {
    dtostrf(abs(zValNumNew),7,3,zValChNew);  //Set string if mm w/ 3 decimals (blanks will auto fill in: 000.000)
  }
  else
  {
    dtostrf(abs(zValNumNew),7,4,zValChNew);  //Set string if inch w/ 4 decimals (blanks will auto fill in: 00.0000)
  }
  zValChJoin = zValChNew;                 
  lcd.print(zValChJoin.substring(0,7));
  lcd.setCursor(5,1);
  if(zValNumNew>=0)
  {
    lcd.print("+");
  }
  else
  {
    lcd.print("-");
  }
}
//*********************************************************
void displayLcdPartValZ()   //called from zEnc() to update z positon on LCD display
{
  //Convert Motor counts to a linear value with consideration for in/mm & memory offset.
  //"mtrNewPosZ" is input from zEnc().  memOffsetZ[mZ] & unitConverter is defined by button functions.
  zValNumNew=-(((float(mtrNewPosZ)-float(memOffsetZ[mZ]))*zPitch)/float(zMtrCntPerRev))/unitConverter;    
                            //SET NEG TO DISPLAY CORRECT
  //Convert float into char array
  if (unitConverter==1.0)                 
  {
    dtostrf(abs(zValNumNew),7,3,zValChNew);     //Set string if mm w/ 3 decimals (blanks will auto fill in: 000.000)
  }
  else
  {
    dtostrf(abs(zValNumNew),7,4,zValChNew);     //Set string if inch w/ 4 decimals (blanks will auto fill in: 00.0000)
  }

  zValChJoin = zValChNew;

  if(zCalcVel <= zVelLimitA)                      //Full value +sign print when buffer is small
  {
    lcd.setCursor(6,1);                    
    lcd.print(zValChJoin.substring(0,7));
    
    if (zValNumNew > 0.0 && zValNumOld <= 0.0)      //Inside full updte sign change
    {
      lcd.setCursor(5,1);
      lcd.print("+");
    }
    else if (zValNumNew < 0.0 && zValNumOld >= 0.0) //Inside full updte sign change
    {
      lcd.setCursor(5,1);
      lcd.print("-");
    }
  }
  else if (zValNumNew > 0.0 && zValNumOld <= 0.0)   //if we switched from - to + (just change sign and ignore value update)
  {
    lcd.setCursor(5,1);
    lcd.print("+");
    lcd.setCursor(4,1);   //just to use time
  }
  else if (zValNumNew < 0.0 && zValNumOld >= 0.0)   //if we switched from + to - (just change sign and ignore value update)
  {
    lcd.setCursor(5,1);
    lcd.print("-");
    lcd.setCursor(4,1);   //just to use time
  }
  else if(zCalcVel <= zVelLimitB && zBufTog==1)       //"1" cycle: prints 6 char 000----
  {
    lcd.setCursor(6,1);
    lcd.print(zValChJoin.substring(0,3));    
  }
  else if(zCalcVel <= zVelLimitB && zBufTog==0)       //"0" cycle: prints 6 char ---.00-
  {
    lcd.setCursor(9,1);
    lcd.print(zValChJoin.substring(3,6));    
  }
  else if(zCalcVel <= zVelLimitC && zBufTog==1)       //"1" cycle: prints 5 char 000----
  {
    lcd.setCursor(6,1);
    lcd.print(zValChJoin.substring(0,3));    
    }
  else if(zCalcVel <= zVelLimitC && zBufTog==0)       //"0" cycle: prints 5 char ---.0--
  {
    lcd.setCursor(9,1);
    lcd.print(zValChJoin.substring(3,5));
    lcd.setCursor(9,1);   //used as delay to balance out "1" cycle    
    }
  else if(zCalcVel <= zVelLimitD && zBufTog==1)       //"1" cycle: prints 4 char 00-----
  {
    lcd.setCursor(6,1);
    lcd.print(zValChJoin.substring(0,2));    
    }
  else if(zCalcVel <= zVelLimitD && zBufTog==0)       //"0" cycle: prints 4 char --0.---
  {
    lcd.setCursor(8,1);
    lcd.print(zValChJoin.substring(2,4));    
    }
  zValNumOld=zValNumNew;                            //set old as next call needs to determine +/- setting
}
