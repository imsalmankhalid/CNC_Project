//*********************************************************
//  displayLcdBasicsXZ()  lcdFeedDispBasic()
//*********************************************************
void displayLcdBasicsXZ()      //only displays the basics (Memory # & in/mm). Changing values from button presses.
{
  //print "mm" or "in"
  if(unitConverter==25.4)
  {
    lcd.setCursor(14,1);
    lcd.print("in");
    lcd.setCursor(14,0);
    lcd.print("in");
  }
  else
  {
    lcd.setCursor(14,1);
    lcd.print("mm");
    lcd.setCursor(14,0);
    lcd.print("mm");
  }
  //print active memory location
  lcd.setCursor(19,1);
  lcd.print(mZ+1);
  lcd.setCursor(19,0);
  lcd.print(mX+1);
  displayLcdFullValZ();      //write of the linear z positon done in separate function to minimize update time
  displayLcdFullValX();      //todo: uncomment. linear x positon done in separate function to minimize update time
}
//*********************************************************
void lcdFeedDispBasic()
{
  lcd.setCursor(0,2);
  lcd.print("RPM =         ");
  lcd.setCursor(14,2);
  lcd.print("Z-STOP");
  lcd.setCursor(0,3);
  lcd.print("IPM =               ");
}
