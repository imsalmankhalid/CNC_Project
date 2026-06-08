//*********************************************************
//  displayLcdFullValX()  displayLcdPartValX()
//*********************************************************
void displayLcdFullValX()   //prints full value with +/- 
{
  xValNumNew=-(((float(mtrNewPosX)-float(memOffsetX[mX]))*xPitch)/float(xMtrCntPerRev))/unitConverter;    
                            //SET NEG TO DISPLAY CORRECT
  lcd.setCursor(6,0);
  if (unitConverter==1.0)                 
  {
    dtostrf(abs(xValNumNew),7,3,xValChNew);  //Set string if mm w/ 3 decimals (blanks will auto fill in: 000.000)
  }
  else
  {
    dtostrf(abs(xValNumNew),7,4,xValChNew);  //Set string if inch w/ 4 decimals (blanks will auto fill in: 00.0000)
  }
  xValChJoin = xValChNew;                 
  lcd.print(xValChJoin.substring(0,7));
  lcd.setCursor(5,0);
  if(xValNumNew>=0)
  {
    lcd.print("+");
  }
  else
  {
    lcd.print("-");
  }
}
//*********************************************************
void displayLcdPartValX()   //called from xEnc() to update x positon on LCD display
{
  //Convert Motor counts to a linear value with consideration for in/mm & memory offset.
  //"mtrNewPosX" is input from xEnc().  memOffsetX[mX] & unitConverter is defined by button functions.
  xValNumNew=-(((float(mtrNewPosX)-float(memOffsetX[mX]))*xPitch)/float(xMtrCntPerRev))/unitConverter;    
                            //SET NEG TO DISPLAY CORRECT
  //Convert float into char array
  if (unitConverter==1.0)                 
  {
    dtostrf(abs(xValNumNew),7,3,xValChNew);   //Set string if mm w/ 3 decimals (blanks will auto fill in: 000.000)
  }
  else
  {
    dtostrf(abs(xValNumNew),7,4,xValChNew);   //Set string if inch w/ 4 decimals (blanks will auto fill in: 00.0000)
  }

  xValChJoin = xValChNew;

  if(xCalcVel <= xVelLimitA)                      //Full value +sign print when buffer is small
  {
    lcd.setCursor(6,0);                    
    lcd.print(xValChJoin.substring(0,7));
    
    if (xValNumNew > 0.0 && xValNumOld <= 0.0)      //Inside full updte sign change
    {
      lcd.setCursor(5,0);
      lcd.print("+");
    }
    else if (xValNumNew < 0.0 && xValNumOld >= 0.0) //Inside full updte sign change
    {
      lcd.setCursor(5,0);
      lcd.print("-");
    }
  }
  else if (xValNumNew > 0.0 && xValNumOld <= 0.0)   //if we switched from - to + (just change sign and ignore value update)
  {
    lcd.setCursor(5,0);
    lcd.print("+");
    lcd.setCursor(4,0);   //just to use time
  }
  else if (xValNumNew < 0.0 && xValNumOld >= 0.0)   //if we switched from - to + (just change sign and ignore value update)
  {
    lcd.setCursor(5,0);
    lcd.print("-");
    lcd.setCursor(4,0);   //just to use time
  }
  else if(xCalcVel <= xVelLimitB && xBufTog==1)       //"1" cycle: prints 6 char 000----
  {
    lcd.setCursor(6,0);
    lcd.print(xValChJoin.substring(0,3));    
  }
  else if(xCalcVel <= xVelLimitB && xBufTog==0)       //"0" cycle: prints 6 char ---.00-
  {
    lcd.setCursor(9,0);
    lcd.print(xValChJoin.substring(3,6));    
  }
  else if(xCalcVel <= xVelLimitC && xBufTog==1)       //"1" cycle: prints 5 char 000----
  {
    lcd.setCursor(6,0);
    lcd.print(xValChJoin.substring(0,3));    
    }
  else if(xCalcVel <= xVelLimitC && xBufTog==0)       //"0" cycle: prints 5 char ---.0--
  {
    lcd.setCursor(9,0);
    lcd.print(xValChJoin.substring(3,5));
    lcd.setCursor(9,0);   //used as delay to balance out "1" cycle    
    }
  else if(xCalcVel <= xVelLimitD && xBufTog==1)       //"1" cycle: prints 4 char 00-----
  {
    lcd.setCursor(6,0);
    lcd.print(xValChJoin.substring(0,2));    
    }
  else if(xCalcVel <= xVelLimitD && xBufTog==0)       //"0" cycle: prints 4 char --0.---
  {
    lcd.setCursor(8,0);
    lcd.print(xValChJoin.substring(2,4));    
    }
  xValNumOld=xValNumNew;                            //set old as next call needs to determine +/- setting
}
