//*********************************************************
//  spindRevCount()  spindIndex()  calcSpeed()
//  potentiometer()  calcFeed()
//*********************************************************
void spindRevCount()
{
  spindRev++;
  sIndexTimeO=sIndexTimeN;
  sIndexTimeN=micros();
}
//*********************************************************
void spindIndex()
{
  if(modeCt==0 || tprQustCt==23 || tprSpdChange==1 || arcQustCt==44) 
  {
    sRpmN=1000000.0*60.0/(sIndexTimeN-sIndexTimeO);   //Calc current RPM

    if(sRpmN > 0 && sRpmN < spndlRpmMax) {    //prevent overflow on time (negative) & beyond maxRpm
      if(abs(sRpmN-sAnchor) > 20) {     //change RPM and reset timer
        //Serial.println(""); Serial.print("Enter Anchor  "); 
        //Serial.print("sRpmN= "); Serial.print(sRpmN); 
        //Serial.print(" sAnchor= "); Serial.print(sAnchor); Serial.println("  is >20?");
        sRpmO=sRpmN;
        sAnchor=sRpmN;
        sElapseTimeO=sElapseTimeN;
        sElapseTimeN=millis();
        //Serial.print(""); Serial.print("OldTime= "); Serial.print(sElapseTimeO); 
        //Serial.print(" NewTime= "); Serial.println(sElapseTimeN);
        calcSpeed();
        displayLcdSpeed();
      }
      else if((sElapseTimeN-sElapseTimeO) <= 2500 && abs(sRpmN-sRpmO) > 3) {
        //Serial.println(""); Serial.print("Quick  "); 
        //Serial.print("delaRPM= "); Serial.println(abs(sRpmN-sRpmO));
        sRpmO=sRpmN;
        sElapseTimeN=millis();
        calcSpeed();
        displayLcdSpeed();
      }
      if((sElapseTimeN-sElapseTimeO) > 2500 && sAnchor!=sRpmO) {
        //Serial.println(""); Serial.print("Set Anchor "); Serial.println(sRpmO);
        sAnchor=sRpmO;
      }
    }
  }
}
//*********************************************************
void calcSpeed()
{
  //RPM will be limited by input (2->+2000 = 30Mil->+30,000us) AND will prevent overflows (neg) && debounce (small micro deltas)
  //If not within range spindleRpm will stay at "last" stored value (last live spindle value)
  if((sIndexTimeN-sIndexTimeO) > spndlMaxRpmTime && (sIndexTimeN-sIndexTimeO) < 30000000) {    //30M=2RPM to max (w/ 20% buffer)
    spindleRpm=1000000.0*60.0/(sIndexTimeN-sIndexTimeO);
    if(spindleRpm < (spndlRpmMin*0.8)) spindleRpm=0;  //< 80% minimum RPM then 0
  }
}
//*********************************************************
void potentiometer()
{
  if(modeCt==0 || tprQustCt==23 || tprSpdChange==1 || arcQustCt==44)
  {
    potNew=analogRead(potPin);

    if(abs(potNew-potAnchor) > 5) {      //change pot and reset timer (count size results in 0.4 IPM)
      potOld=potNew;
      potAnchor=potNew;
      potTimeOld=potTimeNew;
      potTimeNew=millis();
      calcFeed();
      displayLcdFeed();
    }
    else if((potTimeNew-potTimeOld) <= 2500 && abs(potNew-potOld) > 1) {
      potOld=potNew;
      potTimeNew=millis();
      calcFeed();
      displayLcdFeed();
    }
    if((potTimeNew-potTimeOld) > 2500 && potAnchor!=potOld) {   //Not really req'd - just to insure anchor is close to old/new
      potAnchor=potOld;
    }
  }
}
//*********************************************************
void calcFeed()
{
  //Determining feeds:  G0752 lists 0.063mm/rev()(0.0025"/rev) to 0.356mm/rev()(0.0140"/rev) for feed
  //Results (based on 240-2000 RPM) in range from 0.6 to 28 IPM feed.  User input will extend to 0.5-50IPM (12.7-1270mm/min)
  if(potNew < 18) feedRateMm=feedRateMin;   
  else if(potNew > 1007) feedRateMm=feedRateMax;
  else feedRateMm=map(potNew, 18, 1007, int(feedRateMin+0.5), int(feedRateMax-0.5));  //results in 0.05 IPM increments
  feedRate=feedRateMm/25.4;   //Value to display on LCD (Always IPM)
}
