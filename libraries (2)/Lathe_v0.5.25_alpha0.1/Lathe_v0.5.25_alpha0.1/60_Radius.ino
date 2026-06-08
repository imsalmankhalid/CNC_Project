//*********************************************************
//  arcSetup()  arcMove()  ArcOffsetCalc()  x7_IX_ArcRetract()  z0_IX_ArcToStart()  x1_I__ArcAdvFace()  x2_IX_ArcAdvStock()
//                                          r3_I__ArcRadius()   z4_IX_ArcProfile()  r5__X_ArcRadius()   x6__X_ArcFace()
//*********************************************************
void arcSetup()
{
  if(modeCt==4)
  {
    if(arcQustCt==0)    //Choose Arc Type
    {
      lcd.setCursor(0,2);
      lcd.print("Choose Arc Type:    ");
      lcd.setCursor(0,3);
      if(arcType==0) lcd.print("Type = Internal Rad ");
      if(arcType==1) lcd.print("Type = External Rad ");
      arcQustCt=1;
    }
    if(arcQustCt==1) arcButtons();
//________________________________________________      
    if(arcQustCt==2)    //Choose Insert Type
    {
      lcd.setCursor(0,2);
      lcd.print("Choose Insert Type: ");
      lcd.setCursor(0,3);
      if(arcInsType==0) lcd.print("Type = Round        ");
      if(arcInsType==1) lcd.print("Type = Diamond (any)");
      arcQustCt=3;
    }
    if(arcQustCt==3) arcButtons();
//________________________________________________ 
    if(arcQustCt==4)    //Insert tool size
    {
      if(arcInsType==0) arcInsRad=5.0;      //(mm) Diam 10
      if(arcInsType==1) arcInsRad=0.79375;  //(mm) Rad 1/32"
      lcd.setCursor(0,2);
      lcd.print("Measured insert size");
      lcd.setCursor(0,3);
      if(arcInsType==0) lcd.print("Round OD(IC)=       ");
      else lcd.print("Nose Radius =       ");
      arcQustCt=5;
    }
    if(arcQustCt==5)
    {
      if(arcInsType==0) arcInsRadDisp=arcInsRad*2.0;  //To display Diam when round 
      else arcInsRadDisp=arcInsRad;    
      lcd.setCursor(14,3);
      
      if(unitConverter==1.0)
      {
        if(arcInsRadDisp >= 10.0) lcd.print(arcInsRadDisp, 3);
        else {lcd.print(" "); lcd.print(arcInsRadDisp, 3);}
      }
      else lcd.print((arcInsRadDisp/unitConverter), 4); 
               
      arcInsRadCntX=arcInsRad*(xMtrCntPerRev/xPitch)+0.5;   //Insert tool X Radius in counts
      arcInsRadCntZ=arcInsRad*(zMtrCntPerRev/zPitch)+0.5;   //Insert tool Z Radius in counts
      arcQustCt=6; 
    }
    if(arcQustCt==6) arcButtons();
//________________________________________________
    if(arcQustCt==7)    //Find X axis position with tool on known OD (12.7)
    {
      lcd.setCursor(0,2);
      lcd.print("Move X: Touch ANY OD");
      lcd.setCursor(0,3);
      lcd.print("Measured OD=        ");
      arcQustCt=8;
    }
    if(arcQustCt==8)
    {  
      lcd.setCursor(13,3);
      if(unitConverter==1.0){
        if(arcStkOD >= 100.0) lcd.print(arcStkOD, 3);
        else if(arcStkOD >= 9.9995) {lcd.print(" "); lcd.print(arcStkOD, 3);} //todo check all 10 or 9.9995 's
        else {lcd.print("  "); lcd.print(arcStkOD, 3);}
      }
      else {
        if(arcStkOD >= 10.0) lcd.print((arcStkOD/unitConverter), 4);
        else {lcd.print(" "); lcd.print((arcStkOD/unitConverter), 4);}
      }
      arcQustCt=9; 
    }
    if(arcQustCt==9)
    {
      arcButtons();
      zMotorFeed();
    }
    if(arcQustCt==10)
    {
      arcStkRad=mtrNewPosX;   //arcStkOD(mm) is now related to arcStkRad (mtr cnts)
      arcStkCntr=arcStkRad-(arcStkOD/2.0*(xMtrCntPerRev/xPitch));
      arcQustCt=11;
    }
//________________________________________________
    if(arcQustCt==11)    //Find Z axis position with tool on known FACE
    {
      lcd.setCursor(0,2);
      lcd.print("Move Z: Set Tool on ");
      lcd.setCursor(0,3);
      lcd.print("FACE tangent to arc ");
      arcQustCt=12;
    }
    if(arcQustCt==12)
    {
      arcButtons();
    }
    if(arcQustCt==13)
    {
      arcTngFace=mtrNewPosZ;
      arcQustCt=14;
    }
//________________________________________________
    if(arcQustCt==14)    //Find X axis max stock position
    {
      lcd.setCursor(0,2);
      lcd.print("Move X: Set Tool on ");
      lcd.setCursor(0,3);
      lcd.print("max STOCK OD to cut ");
      arcQustCt=15;
    }
    if(arcQustCt==15) arcButtons();
    if(arcQustCt==16)
    {
      arcMaxStk=mtrNewPosX;
      arcQustCt=17;
    }
//________________________________________________
    if(arcQustCt==17)    //Find Radius by Z axis move
    {
      lcd.setCursor(0,2);
      lcd.print("Move Z: TL cntr to  ");
      lcd.setCursor(0,3);
      lcd.print("rad cntr: Rad=      ");
      arcQustCt=18;
    }
    if(arcQustCt==18)
    {  
      arcRadCntrZ=mtrNewPosZ;                     //current motor position
      arcRadOffSzZ=abs(arcTngFace-arcRadCntrZ);   //CUT Radius in motor counts
      if(arcType==0)
      {
        arcRadDisp=(arcRadOffSzZ+arcInsRadCntZ)*(zPitch/zMtrCntPerRev); //Display value for LCD
      }
      else arcRadDisp=(arcRadOffSzZ-arcInsRadCntZ)*(zPitch/zMtrCntPerRev);
      lcd.setCursor(14,3);
      if(unitConverter==1.0){
        if(arcRadDisp < 0.0) lcd.print(arcRadDisp, 2);
        else if(arcRadDisp >= 10.0) lcd.print(arcRadDisp, 3);
        else {lcd.print(" "); lcd.print(arcRadDisp, 3);}
      }
      else {
        if(arcRadDisp < 0.0) lcd.print(float(arcRadDisp)/unitConverter, 3);
        else lcd.print(float(arcRadDisp)/unitConverter, 4);
      }
      arcButtons();
    }
    if(arcQustCt==19) //TODO:  make sure radius is large enough to accomodate finish offset - replace 0.1 then later check that finish does not get set over some value
    {
      if(arcType==0 && ((abs(arcTngFace-arcRadCntrZ)) < (arcZFin*2.0)))   //Internal Rad not large enough (32 cnts min, 2*16), 2x insures finish can be '0' and still ok
      {
        lcd.setCursor(0,3); lcd.print("Min move        reqd");
        lcd.setCursor(9,3); lcd.print(((arcZFin*2.0)*(zPitch/zMtrCntPerRev)/unitConverter), 3);
        delay(2000);
        arcQustCt=17;
      }
      else if(arcType==1 && ((abs(arcTngFace-arcRadCntrZ)) < (arcInsRadCntZ+(arcZFin*2.0)))) //External Rad not large enough (32+InsRad min), 2x insures finish can be '0' and still ok
      {
        lcd.setCursor(0,3); lcd.print("Min move        reqd");
        lcd.setCursor(9,3); lcd.print((((arcZFin*2.0)+arcInsRadCntZ)*(zPitch/zMtrCntPerRev)/unitConverter), 3);
        delay(2000);
        arcQustCt=17;
      }
      else
      {
        arcRadCntrZ=mtrNewPosZ;                                         //current motor position
        arcRadCutSzZ=abs(arcTngFace-arcRadCntrZ);                       //CUT Radius in Z mtr counts
        arcRadCutSzX=arcRadCutSzZ*(zPitch/xPitch);                      //CUT Radius in X mtr counts
        //remove arcRadDisp=(arcRadOffSzZ+arcInsRadCntZ)*(zPitch/zMtrCntPerRev); //Display value for LCD
        if(((arcRadCntrZ < arcTngFace) && arcType==0) || ((arcRadCntrZ > arcTngFace) && arcType==1))
        {
          arcCutDir=0;    //Defines motion direction from Spindle 
        }
        else arcCutDir=1;
        arcQustCt=21;           //oops skip 20
      }
    }
//________________________________________________
    if(arcQustCt==21)    //Enter desired diameter (Min. for internal & Max. for external)
    {
      lcd.setCursor(0,2);
      if(arcType==0) lcd.print("Min Dia @ Arc Finish");
      else lcd.print("Max Dia @ Arc Start ");
      lcd.setCursor(0,3);
      lcd.print("Diameter =          ");
      if(arcType==0) {
        arcTngOdRad=arcMaxStk-(arcInsRadCntX+arcRadCutSzX); //(Internal) Initial count value starts at "max stock rad" minus defined radius (Biggest OD for given arcMaxStk)
      }
      else arcTngOdRad=arcMaxStk;                           //(External) Initial display value starts at "max stock rad"
      
      arcQustCt=22;
    }
    if(arcQustCt==22)
    {
      arcTngOdDisp=abs(arcStkCntr-arcTngOdRad)*(xPitch/xMtrCntPerRev)*2.0;  //Delta from arcStkCntr (0mm)
      if(arcTngOdRad < arcStkCntr)
      {
        lcd.setCursor(10,3);
        lcd.print("-");         //As arcTngOdDisp is abs value, '-' represents a radius value beyond center of stock (still allowed)
      }
      lcd.setCursor(11,3);
      if(unitConverter==1.0){
        if(arcTngOdDisp >= 100.0) lcd.print(arcTngOdDisp, 3);
        else if(arcTngOdDisp >= 9.9995) {lcd.print(" "); lcd.print(arcTngOdDisp, 3);} //todo check all 10 or 9.9995 's
        else {lcd.print("  "); lcd.print(arcTngOdDisp, 3);}
      }
      else {
        if(arcTngOdDisp/unitConverter >= 10.0) lcd.print(arcTngOdDisp/unitConverter, 4);
        else {lcd.print(" "); lcd.print(arcTngOdDisp/unitConverter, 4);}
      }
      arcQustCt=23;
    }
    if(arcQustCt==23) arcButtons();
    if(arcQustCt==24)
    {
      //Add calc for OD   arcTngOdRad is now set (cnts) to Min-or-Max OD to cut
      if(arcType==0) 
      {
        arcRadCntrX=arcTngOdRad+arcRadCutSzX; //must do calc after arcTanOdRadis completed
        if((arcMaxStk-arcInsRadCntX-10) < arcRadCntrX) arcMaxStk=arcRadCntrX+arcInsRadCntX+10; //Protects arcMaxStk position.  Forces arcMaxStk completly outside radius cutting
      }
      else if(arcType==1)
      {
        arcRadCntrX=arcTngOdRad-arcRadCutSzX;
        if((arcMaxStk-10) < arcTngOdRad) arcMaxStk=arcTngOdRad+10; //Protects arcMaxStk position. Forces arcMaxStk outside radius cutting
      }     
      arcQustCt=25;
    }
//________________________________________________
    if(arcQustCt==25)     //Extend cut along OD (Z)
    {
      arcCnt=0;
      lcd.setCursor(0,2);
      lcd.print("Add profile along OD");
      lcd.setCursor(0,3);
      lcd.print("Z Extension=        ");
      arcQustCt=26;
    }
    if(arcQustCt==26)
    {
      arcCntDisp=arcCnt*(zPitch/zMtrCntPerRev);
      lcd.setCursor(13,3);
      if(unitConverter==1.0)
      {
        if(arcCntDisp >= 100.0) lcd.print(arcCntDisp, 3);
        else if(arcCntDisp >= 10.0){lcd.print(" "); lcd.print(arcCntDisp);}
        else if(arcCntDisp == 0.0) lcd.print("  None ");
        else {lcd.print("  "); lcd.print(arcCntDisp, 3);}
      }
      else
      {
        if(arcCntDisp >= 10.0) lcd.print(arcCntDisp/unitConverter, 4);
        else if(arcCntDisp == 0.0) lcd.print("  None ");
        else {lcd.print(" "); lcd.print(arcCntDisp/unitConverter, 4);}
      }
      arcQustCt=27;
    }
    if(arcQustCt==27) arcButtons();
    if(arcQustCt==28)
    {
      if((arcCutDir==0 && arcType==0) || (arcCutDir==1 && arcType==1))
      {
        arcTngOdExt=arcRadCntrZ-arcCnt;
        if(arcTngOdExt==0) arcTngOdExt=arcRadCntrZ-1;   //Force at least one count
      }
      else
      {
        arcTngOdExt=arcRadCntrZ+arcCnt;
        if(arcTngOdExt==0) arcTngOdExt=arcRadCntrZ+1;   //Force at least one count
      }
      arcCnt=0;
      arcQustCt=29;
    }
//________________________________________________
    if(arcQustCt==29)    //Extend cut along face (X)
    {
      arcCnt=0;
      lcd.setCursor(0,2);
      lcd.print("Add extra facing Op.");
      lcd.setCursor(0,3);
      lcd.print("X Extension=        ");
      arcQustCt=30;
    }
    if(arcQustCt==30)
    {
      arcCntDisp=arcCnt*(xPitch/xMtrCntPerRev);
      lcd.setCursor(13,3);
      if(unitConverter==1.0)
      {
        if(arcCntDisp >= 100.0) lcd.print(arcCntDisp, 3);
        else if(arcCntDisp >= 10.0){lcd.print(" "); lcd.print(arcCntDisp);}
        else if(arcCntDisp == 0.0) lcd.print("  None ");
        else {lcd.print("  "); lcd.print(arcCntDisp, 3);}
      }
      else
      {
        if(arcCntDisp >= 10.0) lcd.print(arcCntDisp/unitConverter, 4);
        else if(arcCntDisp == 0.0) lcd.print("  None ");
        else {lcd.print(" "); lcd.print(arcCntDisp/unitConverter, 4);}
      }
      arcQustCt=31;
    }
    if(arcQustCt==31) arcButtons();
    if(arcQustCt==32)
    {
      if(arcType==0)
      {
        arcFaceExt=arcRadCntrX+arcCnt;
        if(arcFaceExt < arcMaxStk+1) arcFaceExt=arcMaxStk+1;    //Force at least one count
      }
      else if(arcType==1)
      {
        arcFaceExt=arcRadCntrX-arcCnt;          //TODO: Dumbell stuff (if this is done then no dumbell)
      }   
      arcQustCt=33;
    }
//________________________________________________
    if(arcQustCt==33 && arcType==1 && arcCnt==0)    //Stop short 'Ball' (Dumbbell) only if extension not done
    {
      lcd.setCursor(0,2);
      lcd.print("Create Dumbbell Diam");
      lcd.setCursor(0,3);
      lcd.print("Inner Diam=         ");
      arcCnt=0;
      arcQustCt=34;
      //if(arcStkCntr > arcRadCntrX) arcQustCt=38;  //safety - if radius center already past stock center line skip this
    }
    else if(arcQustCt==33 && (arcType==0 || arcCnt!=0)) arcQustCt=38;  //if above not true then skip down to next set (depth of cut)
    if(arcQustCt==34)
    {
      lcd.setCursor(12,3);
      lcd.print(" ");  //Gets rid of '-' prior to re-calc
      arcCntDisp=((arcRadCntrX-arcStkCntr)+arcCnt)*(xPitch/xMtrCntPerRev)*2.0;  //Diam Display.  '-' means no dumbell left (but maybe a 'tit')
      lcd.setCursor(13,3);
      if(unitConverter==1.0)
      {
        if(arcCnt==0) lcd.print("  None ");
        else if(arcCntDisp >= 100.0) lcd.print(arcCntDisp, 3);
        else if(arcCntDisp >= 10.0){lcd.print(" "); lcd.print(arcCntDisp);}
        else {lcd.print("  "); lcd.print(arcCntDisp, 3);}
      }
      else
      {
        if(arcCnt==0) lcd.print("  None ");
        else if(arcCntDisp >= 10.0) lcd.print(arcCntDisp/unitConverter, 4);
        else {lcd.print(" "); lcd.print(arcCntDisp/unitConverter, 4);}
      }
      arcQustCt=35;
    }
    if(arcQustCt==35) arcButtons();
    if(arcQustCt==36)
    {
      if(arcCnt > 0)  //safety, only if arcCnt set does arcFaceExt get overwritten
      {
        arcFaceExt=arcRadCntrX+arcCnt;
      }
      arcQustCt=38;     //Skipped 37, moves on even if above not done
    }
//________________________________________________
    if(arcQustCt==38)    //Depth of Cut (Roughing)
    {
      lcd.setCursor(0,2);
      lcd.print("Enter Roughing D.O.C");
      lcd.setCursor(0,3);
      lcd.print("Depth =             ");
      arcQustCt=39;
    }
    if(arcQustCt==39)
    {
      lcd.setCursor(8,3);
      if(unitConverter==1) lcd.print((arcDpthCutX*(xPitch/float(xMtrCntPerRev))), 2);
      else lcd.print(((arcDpthCutX*(xPitch/float(xMtrCntPerRev)))/unitConverter), 3);
      arcQustCt=40;
    }
    if(arcQustCt==40) arcButtons();
//________________________________________________
    if(arcQustCt==41)    //Depth of Cut (Finish)
    {
      if(arcXFin >= arcDpthCutX) arcXFin=arcDpthCutX-10;    //prevents finish > rough to begin
      lcd.setCursor(0,2);
      lcd.print("Enter Finish D.O.C. ");
      lcd.setCursor(0,3);
      lcd.print("Depth =             ");
      arcQustCt=42;
    }
    if(arcQustCt==42)
    {
      lcd.setCursor(8,3);
      if(unitConverter==1) lcd.print((arcXFin*(xPitch/float(xMtrCntPerRev))), 2);
      else lcd.print(((arcXFin*(xPitch/float(xMtrCntPerRev)))/unitConverter), 3);
      arcQustCt=43;
    }
    if(arcQustCt==43) arcButtons();
//________________________________________________
    if(arcQustCt==44)     //Pause to set RPM & Feed ("void loop" potentiometer & spindIndex allows arcQustCt==44)
    {
      potentiometer();
      delay(500);       //Todo: remove?
      calcSpeed();
      displayLcdSpeed();
      calcFeed();
      displayLcdFeed();
      lcd.setCursor(0,2);
      lcd.print("Set RPM & Feed Rate ");
      lcd.setCursor(0,3);
      lcd.print("RPM=      IPM=      ");
      lcd.setCursor(5,3);
      lcd.print(spindleRpmChJoin);
      lcd.setCursor(15,3);
      lcd.print(feedRateChJoin);
      arcButtons();
    }
//________________________________________________
    if(arcQustCt==45)   //Arc READY!  Toggle HalfNut Mssg
    {
      lcd.setCursor(0,2);
      lcd.print("Radius is ready     ");     
      lcd.setCursor(0,3);
      lcd.print("Engage Half Nut...  ");
      arcQustCt=46;

      /*Serial.println("Arc End Questions");
      Serial.print("#0 arcType = "); Serial.println(arcType);
      Serial.print("#2 arcInsType = "); Serial.println(arcInsType);
      Serial.print("#4 arcInsRad = "); Serial.println(arcInsRad);
      Serial.print("#4 arcInsRadCntX = "); Serial.println(arcInsRadCntX);
      Serial.print("#4 arcInsRadCntZ = "); Serial.println(arcInsRadCntZ);
      Serial.print("#7 arcStkOD = "); Serial.println(arcStkOD);
      Serial.print("#7 arcStkRad = "); Serial.println(arcStkRad);
      Serial.print("#7 arcStkCntr = "); Serial.println(arcStkCntr);
      Serial.print("#11 arcTngFace = "); Serial.println(arcTngFace);
      Serial.print("#14 arcMaxStk = "); Serial.println(arcMaxStk);
      Serial.print("#17 arcRadCntrZ = "); Serial.println(arcRadCntrZ);
      Serial.print("#17 arcRadCutSzZ = "); Serial.println(arcRadCutSzZ);
      Serial.print("#17 arcRadCutSzX = "); Serial.println(arcRadCutSzX);
      Serial.print("#17 arcRadDisp = "); Serial.println(arcRadDisp);
      Serial.print("#17 arcCutDir = "); Serial.println(arcCutDir);
      Serial.print("#21 arcTngOdRad = "); Serial.println(arcTngOdRad);
      Serial.print("#21 arcRadCntrX = "); Serial.println(arcRadCntrX);
      Serial.print("#25 arcTngOdExt = "); Serial.println(arcTngOdExt);
      Serial.print("#29 arcFaceExt = "); Serial.println(arcFaceExt);
      Serial.print("#38 arcDpthCutX = "); Serial.println(arcDpthCutX);
      Serial.print("#41 arcXFin = "); Serial.println(arcXFin);
      Serial.print("#44 spindleRpmChJoin = "); Serial.println(spindleRpmChJoin);
      Serial.print("#44 feedRateChJoin = "); Serial.println(feedRateChJoin);
      Serial.println(""); */
    }
    if(arcQustCt==46) arcMove(); 
  }
}
//*********************************************************
void arcMove()    //Arc main loop
{
  tempEncPosZ=encNewPosZ;   //save current Z encoder cnts
  tempEncPosX=encNewPosX;   //save current X encoder cnts

  arcCntl=0;            //todo: remove?
  ArcOffsetCalc();      //Populates points (Rough=Offset)

  while(modeCt==4 && arcCntl < 6 && arcQustCt >= 46 && arcQustCt <= 59) //change 48 to ?? and arcCntl<5(change 22 and 222)
  {
    curStateS1=digitalRead(inPinS1);          //Checks current halfnut lever status
    if(curStateS1==LOW) prevStateS1=LOW;      //IF Halfnut lever is OFF, set prevStateS1=LOW -> reset to allow another feed.
    if(curStateS1==HIGH && prevStateS1==LOW) delay(50);   //Debouce
    curStateS1=digitalRead(inPinS1);
    if(curStateS1==HIGH && prevStateS1==LOW)              //Run 2nd time just to be sure we want to move
    {
      if(arcQustCt==46)                     //Set tool to "start"
      {
        prevStateS1=HIGH;
        lcd.setCursor(5,0);
        lcd.print("--------");
        lcd.setCursor(5,1);
        lcd.print("--------");
        lcd.setCursor(0,2);
        lcd.print("Radius Run/B3:Pause ");
        lcd.setCursor(0,3);
        lcd.print("Moving to start...  ");
        
        x7_IX_ArcRetract();
        z0_IX_ArcToStart();  
       
        arcQustCt=47;
        lcd.setCursor(0,3);
        lcd.print("Re-Engage Half Nut..");
      }
      //Profile Rough ONLY
      else if(arcQustCt==47)
      {
        prevStateS1=HIGH;
        
        lcd.setCursor(0,3);
        lcd.print("Pass     of         ");
        //0.49 is 2x remainder rough & 1.0 is finish pass. TODO: fix this (remainder on 'end' not included)
        arcPassTtl=round(0.49+0.49+1.0+(abs(arcX[0]-arcX[2])/arcDpthCutX)+(abs(arcX[2]-arcX[3])/arcDpthCutX)+(abs(arcX[4]-arcX[5])/arcDpthCutX)+(abs(arcX[5]-arcX[6])/arcDpthCutX));
        lcd.setCursor(12,3);
        lcd.print("   ");
        lcd.setCursor(12,3);
        lcd.print(arcPassTtl); 
          
        while(arcCntl==0)
        {
          if((arcRunStrt-arcX[2]) >= arcDpthCutX) arcRunStrt=arcRunStrt-arcDpthCutX;      //set rough cut depth
          else if((arcRunStrt-arcX[2]) < arcDpthCutX && (arcRunStrt-arcX[2]) > 0) arcRunStrt=arcX[2];
          else if(arcRunStrt==arcX[2])
          {
            arcRadCtRdy=1;
            if((arcRunRad-arcX[5]) >= arcDpthCutX) arcRunRad=arcRunRad-arcDpthCutX;   //although internal rad is "3" we can still use "5" for each
            else if((arcRunRad-arcX[5]) < arcDpthCutX && (arcRunRad-arcX[5]) > 0) arcRunRad=arcX[5];
            else if(arcRunRad==arcX[5])
            {
              arcRadCtRdy=2;
              if((arcRunEnd-arcX[6]) >= arcDpthCutX) arcRunEnd=arcRunEnd-arcDpthCutX;
              else if((arcRunEnd-arcX[6]) < arcDpthCutX && (arcRunEnd-arcX[6]) > 0) arcRunEnd=arcX[6];
              else if(arcRunEnd==arcX[6])
              {
                arcCntl=1;           //Stops Roughing calc... last one (exits 'while')
              }
            }
            Serial.println(""); 
            Serial.print("arcDpthCutX= "); Serial.println(arcDpthCutX); 
            Serial.print("arcRunStrt= "); Serial.println(arcRunStrt);
            Serial.print("arcRunRad= "); Serial.println(arcRunRad);
            Serial.print("arcRunEnd= "); Serial.println(arcRunEnd);
          }
          if(arcCntl==0) arcPassCrnt=arcPassTtl-round(0.49+0.49+1.0+(abs(arcRunStrt-arcX[2])/arcDpthCutX)+(abs(arcRunRad-arcX[5])/arcDpthCutX)+(abs(arcRunEnd-arcX[6])/arcDpthCutX));
          else if(arcCntl==1) arcPassCrnt=arcPassTtl-1;
          lcd.setCursor(5,3);
          lcd.print("   ");
          lcd.setCursor(5,3);
          lcd.print(arcPassCrnt);

          x1_I__ArcAdvFace();
          x2_IX_ArcAdvStock();
          r3_I__ArcRadius();
          z4_IX_ArcProfile();
          r5__X_ArcRadius();
          x6__X_ArcFace();
          x7_IX_ArcRetract();
          if(arcCntl==0) z0_IX_ArcToStart();
        }
        arcCntl=2;          //set cntl for finish
        ArcOffsetCalc();    //Does calc for finish pass (coming up)
        arcQustCt=48;
        lcd.setCursor(0,2);
        lcd.print("Ready for Finish    ");     
        lcd.setCursor(0,3);
        lcd.print("Re-Engage Half Nut..");
      }

      else if(arcQustCt==48 && (arcCntl==2 || arcCntl==4))    //Arc Finish (or spring). Simply cuts with existing values
      {
        prevStateS1=HIGH;   //TODO: add   if(arcQustCt==48 OR last pass of offset)

        if(arcCntl==2 && aNxtOpPos!=3)
        {
          lcd.setCursor(0,2);
          lcd.print("Radius Run - Finish ");

          lcd.setCursor(0,3);
          lcd.print("Pass     of         ");
          arcPassCrnt=arcPassTtl;
          lcd.setCursor(12,3);
          lcd.print("   ");
          lcd.setCursor(12,3);
          lcd.print(arcPassTtl); 
  
          arcPassCrnt=arcPassTtl;
          lcd.setCursor(5,3);
          lcd.print("   ");
          lcd.setCursor(5,3);
          lcd.print(arcPassCrnt);
        }
        else if(arcCntl==2 && aNxtOpPos==3) {
          lcd.setCursor(0,2);
          lcd.print("                    ");
          lcd.setCursor(0,3);
          lcd.print("Spring Pass         ");
        }
        
        z0_IX_ArcToStart();           //"ToStart" now starts sequence
        x1_I__ArcAdvFace();
        x2_IX_ArcAdvStock();
        r3_I__ArcRadius();
        z4_IX_ArcProfile();
        r5__X_ArcRadius();
        x6__X_ArcFace();
        x7_IX_ArcRetract();

        arcQustCt=49;         //this used to be the end
        arcCntl=3;            //3=Pause (goto questions)
      }

      else if(arcQustCt==58 && arcCntl==5)    //Adjust Pass
      {
        prevStateS1=HIGH;

        while(arcCntl==5)
        {
          if(arcXOffset > 0) {
            if(arcXOffset > (arcDpthCutX+arcXFin)) {            //if we can rough (leaves at least a finish cut)
              arcXOffAct=arcXOffAct+arcDpthCutX;                //set value to send to calc (adds a rough)
              arcXOffset=arcXOffset-arcDpthCutX;                //Reduce requested value by cut amount
            }
            else if(arcXOffset > arcXFin && arcXOffset <= (arcDpthCutX+arcXFin)) {  //if some beyond a finish but less than rough
              arcXOffAct=arcXOffAct+(arcXOffset-arcXFin);                           //set value to send to calc (leaves exactly a finish)
              arcXOffset=arcXOffset-(arcXOffset-arcXFin);                           //Reduce requested value by cut amount
            }
            else if(arcXOffset > 0 && arcXOffset <= arcXFin) {  //if finish size (or smaller but never happen)
              arcXOffAct=arcXOffAct+arcXOffset;                 //take off whatever is left (exact finish)
              arcXOffset=0;                                     //Requested now is complete =0
            }
          }
          if(arcZOffset > 0) {
            if(arcZOffset > (arcDpthCutZ+arcZFin)) {            //if we can rough (leaves at least a finish cut)
              arcZOffAct=arcZOffAct+arcDpthCutZ;                //set value to send to calc (adds a rough)
              arcZOffset=arcZOffset-arcDpthCutZ;                //Reduce requested value by cut amount
            }
            else if(arcZOffset > arcZFin && arcZOffset <= (arcDpthCutZ+arcZFin)) {  //if some beyond a finish but less than rough
              arcZOffAct=arcZOffAct+(arcZOffset-arcZFin);                           //set value to send to calc (leaves exactly a finish)
              arcZOffset=arcZOffset-(arcZOffset-arcZFin);                           //Reduce requested value by cut amount
            }
            else if(arcZOffset > 0 && arcZOffset <= arcZFin) {  //if finish size (or smaller but never happen)
              arcZOffAct=arcZOffAct+arcZOffset;                 //take off whatever is left (exact finish)
              arcZOffset=0;                                     //Requested now is complete =0
            }
          }

          ArcOffsetCalc();      //Populates points with new offset

          z0_IX_ArcToStart();
          x1_I__ArcAdvFace();
          x2_IX_ArcAdvStock();
          r3_I__ArcRadius();
          z4_IX_ArcProfile();
          r5__X_ArcRadius();
          x6__X_ArcFace();
          x7_IX_ArcRetract();

          if(arcZOffset==0 && arcXOffset==0)   //Done here - back to post questions
            {
              arcCntl=3;
            }
          //Done with 'While'
        }
        arcQustCt=49; 
      }
    }

    //Complete with primary cut - ask Radius specific completion questions
    if(arcQustCt==49)
    {
      lcd.setCursor(0,2);
      lcd.print("Done: Select next Op");
      lcd.setCursor(0,3);
      lcd.print(arcNextOp[aNxtOpPos]);    //Exit(0), Adjust Radius(1), Mirror Ext(2), Spring Pass(3)
      arcQustCt=50;
    }
    if(arcQustCt==50) arcButtons();
    if(arcQustCt==51 && aNxtOpPos==0) modeCt=999;           //Exit
    if(arcQustCt==51 && aNxtOpPos==2) {                     //Mirror(none) TODO: for now exit, add function
        lcd.setCursor(0,3);
        lcd.print("Not available yet   ");
        delay(2000);
        arcQustCt=49;
      }
    if(arcQustCt==51 && aNxtOpPos==3)                       //Spring Pass
    {
      lcd.setCursor(0,2);
      lcd.print("Spring Pass         ");
      lcd.setCursor(0,3);
      lcd.print("Toggle HalfNut again");
      arcQustCt=48;      //back to finish
      arcCntl=2;         //allows finish only
    }

    if(arcQustCt==51 && aNxtOpPos==1)                     //Adjust Radius
    {
      if(arcCutDir==0) {
        lcd.setCursor(0,2);
        lcd.print("Shift Rad Left  <=  ");
      }
      else {
        lcd.setCursor(0,2);
        lcd.print("Shift Rad Right =>  ");
      }
      lcd.setCursor(0,3);
      lcd.print("Infeed =            ");
      arcQustCt=52;
    }
    if(arcQustCt==52 && aNxtOpPos==1) 
    {
      if(arcZOffset < 0) arcZOffset=0;    //Prevents '0' - best way to prevent input beyond allowed range TODO:change all
      arcCntDisp=arcZOffset*(zPitch/zMtrCntPerRev);
      lcd.setCursor(10,3);
      if(unitConverter==1.0) {
        if(arcCntDisp >= 100.0) lcd.print(arcCntDisp, 3);
        else if(arcCntDisp >= 10.0){lcd.print(" "); lcd.print(arcCntDisp);}
        else if(arcCntDisp == 0.0) lcd.print("  None ");
        else {lcd.print("  "); lcd.print(arcCntDisp, 3);}
      }
      else {
        if(arcCntDisp >= 10.0) lcd.print(arcCntDisp/unitConverter, 4);
        else if(arcCntDisp == 0.0) lcd.print("  None ");
        else {lcd.print(" "); lcd.print(arcCntDisp/unitConverter, 4);}
      }
      arcQustCt=53;
    }
    if(arcQustCt==53 && aNxtOpPos==1) arcButtons();
    if(arcQustCt==54 && aNxtOpPos==1)
    {
      lcd.setCursor(0,2);
      lcd.print("Cut Rad Deeper  ^   ");
      lcd.setCursor(0,3);
      lcd.print("Offset =            ");
      arcQustCt=55;
    }

    if(arcQustCt==55 && aNxtOpPos==1) 
    {
      if(arcXOffset < 0) arcXOffset=0;    //Prevents '0' - best way to prevent input beyond allowed range TODO:change all
      arcCntDisp=arcXOffset*(xPitch/xMtrCntPerRev);
      lcd.setCursor(10,3);
      if(unitConverter==1.0) {
        if(arcCntDisp >= 100.0) lcd.print(arcCntDisp, 3);
        else if(arcCntDisp >= 10.0){lcd.print(" "); lcd.print(arcCntDisp);}
        else if(arcCntDisp == 0.0) lcd.print("  None ");
        else {lcd.print("  "); lcd.print(arcCntDisp, 3);}
      }
      else {
        if(arcCntDisp >= 10.0) lcd.print(arcCntDisp/unitConverter, 4);
        else if(arcCntDisp == 0.0) lcd.print("  None ");
        else {lcd.print(" "); lcd.print(arcCntDisp/unitConverter, 4);}
      }
      arcQustCt=56;
    }
    if(arcQustCt==56) arcButtons();

    if(arcQustCt==57)
    {
      if(arcXOffset > 0 || arcZOffset > 0)
      {
        lcd.setCursor(0,2);
        lcd.print("Adjust Pass         ");
        lcd.setCursor(0,3);
        lcd.print("Toggle HalfNut again");
        arcQustCt=58;      //Set qust & cntl to re-enter above and go into 'offset' while loop
        arcCntl=5;
      }
      else arcQustCt=49;   //back to post questions (no input for offset)
    }

  }
  //After 'while' write encoder X & Z to prevent movement from encoder changes
  zAxisEnc.write(tempEncPosZ);
  encNewPosZ=tempEncPosZ;
  encOldPosZ=tempEncPosZ;  
  xAxisEnc.write(tempEncPosX);
  encNewPosX=tempEncPosX;
  encOldPosX=tempEncPosX; 
  modeCt=999;                   //Gets out of Radius function and sends us to choose new function.
}
//*********************************************************
void ArcOffsetCalc()
{
  for(int arci = 0; arci < arcArSize; arci++)   //Populate 'Fin' & 'Off' arrays to zero
  {
    arcXFinAr[arci]=0; arcZFinAr[arci]=0; arcXOffAr[arci]=0; arcZOffAr[arci]=0;
    arcX[arci]=0; arcZ[arci]=0; 
  }
  if(arcCntl==0 && arcType==0)    //Rough pass (Internal) - Finish offset required
  {
    //Right: (All)
    arcZFinAr[0]=-1*arcZFin;  arcZFinAr[1]=-1*arcZFin;  arcZFinAr[2]=-1*arcZFin;  arcZFinAr[3]=0;
    arcZFinAr[4]=0;           arcZFinAr[5]=0;           arcZFinAr[6]=0;           arcZFinAr[7]=0;
    arcXFinAr[0]=0;           arcXFinAr[1]=0;           arcXFinAr[2]=0;           arcXFinAr[3]=arcXFin; 
    arcXFinAr[4]=arcXFin;     arcXFinAr[5]=arcXFin;     arcXFinAr[6]=arcXFin;     arcXFinAr[7]=0; 

    if(arcCutDir==1)  //Left: Only deltas from above
    {
      arcZFinAr[0]=arcZFin; arcZFinAr[1]=arcZFin; arcZFinAr[2]=arcZFin;
    }
  }
  if(arcCntl==0 && arcType==1)    //Rough pass (external) - Finish offset required
  {
    //Right: (All)
    arcZFinAr[0]=0;         arcZFinAr[1]=0;           arcZFinAr[2]=0;           arcZFinAr[3]=0; 
    arcZFinAr[4]=0;         arcZFinAr[5]=-1*arcZFin;  arcZFinAr[6]=-1*arcZFin;  arcZFinAr[7]=-1*arcZFin;
    arcXFinAr[0]=arcXFin;   arcXFinAr[1]=arcXFin;     arcXFinAr[2]=arcXFin;     arcXFinAr[3]=arcXFin; 
    arcXFinAr[4]=arcXFin;   arcXFinAr[5]=0;           arcXFinAr[6]=0;           arcXFinAr[7]=arcXFin; 

    if(arcCutDir==1)  //Left: Only deltas from above
    {
      arcZFinAr[5]=arcZFin; arcZFinAr[6]=arcZFin; arcZFinAr[7]=arcZFin;  
    }
  }
  if(arcCntl==5)    //Offset required
  {
    //All negative to start (internal & external)
    for(int arcii = 0; arcii < arcArSize; arcii++)        //Populate 'Off' array both X & Z
    {
      arcXOffAr[arcii]=-1*arcXOffAct;
      arcZOffAr[arcii]=-1*arcZOffAct;
    }
    if(arcCutDir==0)                                      //Right  (Only deltas from above)
    {
      for(int arciii = 0; arciii < arcArSize; arciii++)   //Populate all Z's '+'
      {
        arcZOffAr[arciii]=arcZOffAct; 
      }      
    }
    if(arcType==0) {      //Internal
      arcXOffAr[0]=0; arcXOffAr[7]=0;
      arcZOffAr[4]=0; arcZOffAr[5]=0; arcZOffAr[6]=0; arcZOffAr[7]=0; 
    }
    if(arcType==1) {      //External
      arcXOffAr[0]=0; arcXOffAr[7]=0;
    }
  }
  //Note: if arcCntl==2 (finish) then no "Fin" offsets will be applied, & if arcCntl!=555 no offset (both nulled out at start of function)
  if(arcType==0)      //Internal
  {
    arcZ[0]=arcTngFace+arcZFinAr[0]+arcZOffAr[0];   arcZ[1]=arcTngFace+arcZFinAr[1]+arcZOffAr[1]; 
    arcZ[2]=arcTngFace+arcZFinAr[2]+arcZOffAr[2];   arcZ[3]=arcRadCntrZ+arcZFinAr[3]+arcZOffAr[3]; 
    arcZ[4]=arcTngOdExt+arcZFinAr[4]+arcZOffAr[4];  arcZ[5]=arcTngOdExt+arcZFinAr[5]+arcZOffAr[5]; 
    arcZ[6]=arcTngOdExt+arcZFinAr[6]+arcZOffAr[6];  arcZ[7]=arcTngOdExt+arcZFinAr[7]+arcZOffAr[7];
    arcX[0]=arcFaceExt+arcXFinAr[0]+arcXOffAr[0];   arcX[1]=arcMaxStk+arcXFinAr[1]+arcXOffAr[1]; 
    arcX[2]=arcRadCntrX+arcXFinAr[2]+arcXOffAr[2];  arcX[3]=arcTngOdRad+arcXFinAr[3]+arcXOffAr[3]; 
    arcX[4]=arcTngOdRad+arcXFinAr[4]+arcXOffAr[4];  arcX[5]=arcTngOdRad+arcXFinAr[5]+arcXOffAr[5]; 
    arcX[6]=arcTngOdRad+arcXFinAr[6]+arcXOffAr[6];  arcX[7]=arcFaceExt+arcXFinAr[7]+arcXOffAr[7]; 
  }
  else if(arcType==1) //External
  {
    arcZ[0]=arcTngOdExt+arcZFinAr[0]+arcZOffAr[0];  arcZ[1]=arcTngOdExt+arcZFinAr[1]+arcZOffAr[1]; 
    arcZ[2]=arcTngOdExt+arcZFinAr[2]+arcZOffAr[2];  arcZ[3]=arcTngOdExt+arcZFinAr[3]+arcZOffAr[3]; 
    arcZ[4]=arcRadCntrZ+arcZFinAr[4]+arcZOffAr[4];  arcZ[5]=arcTngFace+arcZFinAr[5]+arcZOffAr[5]; 
    arcZ[6]=arcTngFace+arcZFinAr[6]+arcZOffAr[6];   arcZ[7]=arcTngFace+arcZFinAr[7]+arcZOffAr[7]; 
    arcX[0]=arcMaxStk+arcXFinAr[0]+arcXOffAr[0];    arcX[1]=arcMaxStk+arcXFinAr[1]+arcXOffAr[1]; 
    arcX[2]=arcTngOdRad+arcXFinAr[2]+arcXOffAr[2];  arcX[3]=arcTngOdRad+arcXFinAr[3]+arcXOffAr[3]; 
    arcX[4]=arcTngOdRad+arcXFinAr[4]+arcXOffAr[4];  arcX[5]=arcRadCntrX+arcXFinAr[5]+arcXOffAr[5]; 
    arcX[6]=arcFaceExt+arcXFinAr[6]+arcXOffAr[6];   arcX[7]=arcMaxStk+arcXFinAr[7]+arcXOffAr[7]; 
    if(arcFaceExt > arcRadCntrX) arcX[5]=arcFaceExt+arcXFinAr[5]+arcXOffAr[5];  //Dumbell         //todo: check ******
  }
  
  //Set Radius (only in X reqd to control depth/#passes but will do both x/z)
  if(arcCntl==0) {                    //Rough
    if(arcType==0) {                  //+Internal
      arcX[8]=arcRadCutSzX-arcXFin;
      arcZ[8]=arcRadCutSzZ-arcZFin;
    }
    else {
      arcX[8]=arcRadCutSzX+arcXFin;   //+External
      arcZ[8]=arcRadCutSzZ+arcZFin;
    }
  }
  else {                              //NOT Rough  (Finish or offset - no Rad change)
    arcX[8]=arcRadCutSzX;             //+both Internal/External, No Rad change
    arcZ[8]=arcRadCutSzZ;
  }
  
  //Set 45 deg control point as motor count in space - used when cutting radius to drive X or Z axis
  if(arcType==0) {      //Internal
    if(arcCutDir==0){
      arcZ[9]=arcZ[2]-(arcRadCutSzZ-(sqrt(arcRadCutSzZ*arcRadCutSzZ/2.0)));      //Right
    }
    else arcZ[9]=arcZ[2]+(arcRadCutSzZ-(sqrt(arcRadCutSzZ*arcRadCutSzZ/2.0)));   //Left
  }
  else if(arcType==1) { //External
    if(arcCutDir==0) {
      arcZ[9]=arcZ[4]-(arcRadCutSzZ-(sqrt(arcRadCutSzZ*arcRadCutSzZ/2.0)));      //Right
    }
    else arcZ[9]=arcZ[4]+(arcRadCutSzZ-(sqrt(arcRadCutSzZ*arcRadCutSzZ/2.0)));   //Left
  }
  
  //Set Initial Running values: Used to track progress during rough cuts
  if(arcCntl==0)  //Rough
  {
    arcRunStrt=arcX[1];   //"1" is first possible infeed cut - must be regulated with depth/pass
    if(arcType==0) arcRunRad=arcX[2];
    else arcRunRad=arcX[4];
    arcRunEnd=arcX[5];
  }
  else            //Not Rough TODO: is this ok or more exact
  {
    arcRunStrt=arcX[2];
    if(arcType==0) arcRunRad=arcX[3];                                       //Internal - End of Radius
    else if(arcType==1 && arcFaceExt > arcRadCntrX) arcRunRad=arcFaceExt;   //External + Barbell req'd so cut short //TODO: how is arcX[5] defined?
    else arcRunRad=arcX[5];                                                 //External - End of Radius
    arcRunEnd=arcX[6];          //TODO: how does this fit ??
  }

  /*Serial.println("Calculations");
  for( int calci = 0; calci < arcArSize; calci++)
  {
    Serial.print("X"); Serial.print(calci); Serial.print(" = "); Serial.print(arcX[calci]);
    Serial.print("       Z"); Serial.print(calci); Serial.print(" = "); Serial.println(arcZ[calci]);
  }
  Serial.print("X Rad = "); Serial.println(arcX[8]);
  Serial.print("Z Rad = "); Serial.println(arcZ[8]);
  Serial.print("Z Control Point = "); Serial.println(arcZ[9]);
  Serial.print("arcRunStrt = "); Serial.println(arcRunStrt);
  Serial.print("arcRunRad = "); Serial.println(arcRunRad);
  Serial.print("arcRunEnd = "); Serial.println(arcRunEnd);
  Serial.print(""); */
}
//*********************************************************
void x7_IX_ArcRetract()
{
  //Serial.println(""); Serial.println("ArcRetract: to 7");
  while(mtrNewPosX != arcX[7])
  {
    if(mtrNewPosX < arcX[7]) arcRapidStep=1;          //Fine move +cnts (-linear value)
    if(mtrNewPosX > arcX[7]) arcRapidStep=-1;         //Fine move -cnts (+linear value)
    if((mtrNewPosX+20) < arcX[7]) arcRapidStep=2;     //Rapid move +cnts (-linear value)
    if((mtrNewPosX-20) > arcX[7]) arcRapidStep=-2;    //Rapid move -cnts (+linear value)
    //resetButton();  //TODO: uncomment and add feature
    delayMicroseconds(arcRapidDelay);                     //Delay sets velocity
    X.move(arcRapidStep);                                 //Move x motor
    mtrNewPosX=mtrOldPosX+arcRapidStep;                 //Calculates where motor is (cnt) from absolute (machine start)
    mtrOldPosX=mtrNewPosX;                              //don't know why i keep tracking old pos but i do
    curStateS1=digitalRead(inPinS1);
    if(curStateS1==LOW) modeCt=999;                     //Dump out if halfnut disengaged too early
  }
  //Serial.print("  arcX[7] = mtrNewPosX = "); Serial.println(mtrNewPosX);
}
//*********************************************************
void z0_IX_ArcToStart()
{
  while(mtrNewPosZ!=arcZ[0])      //TODO: do i need (&& arcCntl==?)
  {
    if(mtrNewPosZ > arcZ[0]) arcRapidStep=-1;         //Fine move +cnts     
    if(mtrNewPosZ < arcZ[0]) arcRapidStep=1;          //Fine move +cnts
    if(mtrNewPosZ >= (arcZ[0]+20)) arcRapidStep=-2;   //Rapid move +cnts
    if(mtrNewPosZ <= (arcZ[0]-20)) arcRapidStep=2;    //Rapid move +cnts
     
    //resetButton();  //TODO: uncomment and add feature
    delayMicroseconds(arcRapidDelay);                         //Delay sets velocity
    Z.move(arcRapidStep);                                     //Move z motor
    mtrNewPosZ=mtrOldPosZ+arcRapidStep;                     //Calculates where motor is (cnt) from absolute (machine start)
    mtrOldPosZ=mtrNewPosZ;                                    //don't know why i keep tracking old pos but i do
    curStateS1=digitalRead(inPinS1);
    if(curStateS1==LOW) modeCt=999;                         //Dump out if halfnut disengaged too early
  }
  //Serial.print("  arcZ[0] = mtrNewPosZ = "); Serial.println(mtrNewPosZ);
}
//*********************************************************
void x1_I__ArcAdvFace()     //Only face - no material infeed removal.  Full motion for all passes.
{
  //Speed set here - this is first non-rapid motion   TODO: add adjust during pass
  if(arcSpdChange==0)
  {
    arcDelay=(1/(((feedRateMm)/zPitch)*float(zMtrCntPerRev)))*(60*1000000)-arcDelayCode;     //=us/cnt:  TODO: watch for 5/2 ratio chg on psudo step
    tprSpdChange=2;
  }

  //Serial.println("ArcAdvFace: to 1");
  while(mtrNewPosX!=arcX[1])
  {
    delayMicroseconds(arcDelay);
    if(mtrNewPosX > arcX[1]) arcXStep=-1;
    else arcXStep=1;  //Should never happen
    X.move(arcXStep);
    mtrNewPosX=mtrOldPosX+arcXStep;
    mtrOldPosX=mtrNewPosX;
    curStateS1=digitalRead(inPinS1);
    if(curStateS1==LOW) modeCt=999;
  }
  //Serial.print("  arcX[1] = mtrNewPosX = "); Serial.println(mtrNewPosX);
}
//*********************************************************
void x2_IX_ArcAdvStock()    //Must step thru stock with rough cut depth.
{
  //Serial.println("ArcAdvStock: to 2");
  while(mtrNewPosX!=arcRunStrt)
  {
    //if(mtrNewPosX > (arcRunStrt+arcDpthCutX+20) && arcCntl==0) delayMicroseconds(arcRapidDelay);  //Rapids if previously cut AND rough
    delayMicroseconds(arcDelay);      //removed the else TODO
    if(mtrNewPosX > arcRunStrt) arcXStep=-1;
    else arcXStep=1;    //Should never happen
    X.move(arcXStep);
    mtrNewPosX=mtrOldPosX+arcXStep;
    mtrOldPosX=mtrNewPosX;
    curStateS1=digitalRead(inPinS1);
    if(curStateS1==LOW) modeCt=999;
  }
  //Serial.print("  arcRunStrt = mtrNewPosX = "); Serial.println(mtrNewPosX);
}
//*********************************************************
void r3_I__ArcRadius()  //Internal: Cut radius by X (pre-45), radius by Z (post-45) + continue Z out straight
{
  if(arcType==0)  //Internal only
  {
    //Serial.println("ArcRadius: to 3 First half");
    //TODO:  Enter the speed change stuff here

    //Each time this function is called all values reset because we need to step thru the entire radius
    arcXStpRad=1;
    arcZStpRad=0;
    arcXStpRun=0.0;
    arcZStpRun=0.0;
    arcXStpActual=0;
    arcZStpActual=0;
    
    //Drive in X -> Z follows until 1st half arc complete (only if arcRadCtRdy > 0 = radius ready to cut)
    while(mtrNewPosX!=arcRunRad && arcRadCtRdy > 0 && ((arcCutDir==0 && mtrNewPosZ > arcZ[9]) || (arcCutDir==1 && mtrNewPosZ < arcZ[9])))
    {
      delayMicroseconds(arcDelay);
                                            //TODO: Add arcRapidDelay "if" statement
      X.move(-1*arcXStpRad);
      arcXStpRun=arcXStpRun+arcXStpRad;
      arcXStpActual=arcXStpActual+arcXStpRad;
      mtrNewPosX=mtrOldPosX-arcXStpRad;
      mtrOldPosX=mtrNewPosX;
      
      //Serial.println(""); Serial.println("before");
      //Serial.println("arcZStpRun=(arcX[8]-sqrt((arcX[8]*arcX[8])-(arcXStpRun*arcXStpRun)))*(xPitch/zPitch)"); 
      //Serial.print(arcZStpRun); Serial.print("="); Serial.print(arcX[8]);Serial.print("-sqrt("); Serial.print(arcX[8]); Serial.print("^2-"); Serial.print(arcXStpRun); Serial.println("^2");
      //Serial.println("");
      arcZStpRun=(arcX[8]-sqrt((arcX[8]*arcX[8])-(arcXStpRun*arcXStpRun)))*(xPitch/zPitch); //new Z position
      //Serial.println(""); Serial.println("after");
      //Serial.println("arcZStpRun=(arcX[8]-sqrt((arcX[8]*arcX[8])-(arcXStpRun*arcXStpRun)))*(xPitch/zPitch)");
      //Serial.print(arcZStpRun); Serial.print("="); Serial.print(arcX[8]);Serial.print("-sqrt("); Serial.print(arcX[8]); Serial.print("^2-"); Serial.print(arcXStpRun); Serial.println("^2");
      //Serial.println("");      
      arcZStpRad=int(arcZStpRun)-arcZStpActual; //Current step over '1' minus previous steps
      arcZStpActual=arcZStpActual+arcZStpRad;   //Adds current step to 'tracked' total. Could be '0'.
      
      if(arcCutDir==0) {
        Z.move(-1*arcZStpRad);    //sometimes '0'
        mtrNewPosZ=mtrOldPosZ-arcZStpRad;
        mtrOldPosZ=mtrNewPosZ;
      }
      else {
        Z.move(arcZStpRad);    //sometimes '0'
        mtrNewPosZ=mtrOldPosZ+arcZStpRad;
        mtrOldPosZ=mtrNewPosZ;
      }
      curStateS1=digitalRead(inPinS1);
      if(curStateS1==LOW) modeCt=999;

      //Serial.println("");
      //Serial.print("mtrNewPosX= "); Serial.println(mtrNewPosX);
      //Serial.print("arcXStpRun= "); Serial.println(arcXStpRun); 
      //Serial.print("arcXStpActual= "); Serial.println(arcXStpActual);
      //Serial.print("mtrNewPosZ= "); Serial.println(mtrNewPosZ);
      //Serial.print("arcZStpRun= "); Serial.println(arcZStpRun); 
      //Serial.print("arcZStpActual= "); Serial.println(arcZStpActual);
    }
    //Serial.print("  mtrNewPosX = "); Serial.print(mtrNewPosX); Serial.print("  arcRunRad = "); Serial.println(arcRunRad);
    
    arcZStpRun=int(arcZStpRun);     //Round down to make 'run' = 'actual' (removes remainder)
    arcXStpActual=arcXStpRun;       //Keeps track of already moved X full steps  TODO: could remove?
    arcXStpRun=sqrt((2.0*arcZStpRun*arcZ[8])-(arcZStpRun*arcZStpRun))*(zPitch/xPitch);  //calculate (lowers) X to match Z truncated value (x now float)
    arcZStpRad=1;                   //Set Z step '1' full values now for Z
    
    //Drive in Z -> X follows until 2nd half arc complete (and arcRadCtRdy shows ready for radius cut)
    //Serial.println("ArcRadius: to 3 second half");
    while(mtrNewPosX > arcRunRad && arcRadCtRdy > 0)     //Use > here as int Z moves may push X beyond exact equal
    {
      delayMicroseconds(arcDelay*2);    //slowed down when driving in Z
                                      //TODO: Add arcRapidDelay "if" statement
      if(arcCutDir==0) {
        Z.move(-1*arcZStpRad);
        mtrNewPosZ=mtrOldPosZ-arcZStpRad;
        mtrOldPosZ=mtrNewPosZ;
      }
      else {
        Z.move(arcZStpRad);
        mtrNewPosZ=mtrOldPosZ+arcZStpRad;
        mtrOldPosZ=mtrNewPosZ;
      }
      arcZStpRun=arcZStpRun+arcZStpRad;         //adds '1' to running Z count
      arcZStpActual=arcZStpActual+arcZStpRad;
      
      arcXStpRun=sqrt((2.0*arcZStpRun*arcZ[8])-(arcZStpRun*arcZStpRun))*(zPitch/xPitch);  //New X position
      arcXStpRad=int(arcXStpRun)-arcXStpActual;  //Current step over '1' minus previous step
      arcXStpActual=arcXStpActual+arcXStpRad;  //Adds current step to 'tracked' total
      X.move(-1*arcXStpRad);  //sometimes '0'
      mtrNewPosX=mtrOldPosX-arcXStpRad;
      mtrOldPosX=mtrNewPosX;
    }
    //Serial.print("  mtrNewPosX= "); Serial.print(mtrNewPosX); Serial.print("  arcRunRad= "); Serial.println(arcRunRad);

    //Drive in Z ONLY to finish motion
    //Serial.println("ArcRadius: to 3 Z only");
    arcZStpRad=1;
    while((arcCutDir==0 && mtrNewPosZ > arcZ[3]) || (arcCutDir==1 && mtrNewPosZ < arcZ[3]))
    {
      delayMicroseconds(arcDelay);                //Delay sets velocity
      if(arcCutDir==0 && mtrNewPosZ > arcZ[3]) {  //safety added
        Z.move(-1*arcZStpRad);
        mtrNewPosZ=mtrOldPosZ-arcZStpRad;
        mtrOldPosZ=mtrNewPosZ;
      }
      else if(arcCutDir==1 && mtrNewPosZ < arcZ[3]) {
        Z.move(arcZStpRad);
        mtrNewPosZ=mtrOldPosZ+arcZStpRad;
        mtrOldPosZ=mtrNewPosZ;
      }
      curStateS1=digitalRead(inPinS1);
      if(curStateS1==LOW) modeCt=999;                         //Dump out if halfnut disengaged too early
    }
    //Serial.print("  mtrNewPosX= "); Serial.print(mtrNewPosX); Serial.print("  arcRunRad= "); Serial.println(arcRunRad);
    //Serial.print("  mtrNewPosZ= "); Serial.println(mtrNewPosZ);
  }
}
//*********************************************************
void z4_IX_ArcProfile()
{
  //Serial.println("ArcProfile: to 4");
  while(mtrNewPosZ!=arcZ[4])
  {
    if(mtrNewPosZ > arcZ[4]) arcZStep=-1;   //Right
    if(mtrNewPosZ < arcZ[4]) arcZStep=1;    //Left

    delayMicroseconds(arcDelay);                              //Delay sets velocity
    Z.move(arcZStep);                                         //Move z motor
    mtrNewPosZ=mtrOldPosZ+arcZStep;                         //Calculates where motor is (cnt) from absolute (machine start)
    mtrOldPosZ=mtrNewPosZ;                                    //don't know why i keep tracking old pos but i do
    curStateS1=digitalRead(inPinS1);
    if(curStateS1==LOW) modeCt=999;                         //Dump out if halfnut disengaged too early
  }
    //Serial.print("  mtrNewPosZ=arcZ[4]= "); Serial.println(mtrNewPosZ);
}
//*********************************************************
void r5__X_ArcRadius()  //External: Cut radius by Z (pre-45), radius by X (post-45), & continue Z out straight
{
  if(arcType==1)  //External only
  {
    //TODO:  Enter the speed change stuff here

    //Each time this function is called all values reset because we need to step thru the entire radius
    arcXStpRad=0;
    arcZStpRad=1;
    arcXStpRun=0.0;
    arcZStpRun=0.0;
    arcXStpActual=0;
    arcZStpActual=0;

    //Drive in Z -> X follows until 1st half arc complete (and arcRadCtRdy shows ready for radius cut)
    while(mtrNewPosX!=arcRunRad && arcRadCtRdy > 0 && ((arcCutDir==0 && mtrNewPosZ > arcZ[9]) || (arcCutDir==1 && mtrNewPosZ < arcZ[9])))
    {
      delayMicroseconds(arcDelay*2);  //slowed down when driving in Z
                                      //TODO: Add arcRapidDelay "if" statement
      if(arcCutDir==0) {
        Z.move(-1*arcZStpRad);
        mtrNewPosZ=mtrOldPosZ-arcZStpRad;
        mtrOldPosZ=mtrNewPosZ;
      }
      else {
        Z.move(arcZStpRad);
        mtrNewPosZ=mtrOldPosZ+arcZStpRad;
        mtrOldPosZ=mtrNewPosZ;
      }
      
      arcZStpRun=arcZStpRun+arcZStpRad;         //adds '1' to running Z count
      arcZStpActual=arcZStpActual+arcZStpRad;
      
      arcXStpRun=(arcZ[8]-sqrt((arcZ[8]*arcZ[8])-(arcZStpRun*arcZStpRun)))*(zPitch/xPitch);   //New X position
      arcXStpRad=int(arcXStpRun)-arcXStpActual;  //Current step over '1' minus previous step
      arcXStpActual=arcXStpActual+arcXStpRad;  //Adds current step to 'tracked' total. Could be '0'.
      
      X.move(-1*arcXStpRad);  //sometimes '0'
      mtrNewPosX=mtrOldPosX-arcXStpRad;
      mtrOldPosX=mtrNewPosX;
    }

    arcXStpRun=int(arcXStpRun);     //Round down to make 'run' = 'actual' (removes remainder)
    arcZStpActual=arcZStpRun;       //Keeps track of already moved Z full steps  TODO: could remove?
    arcZStpRun=sqrt((2.0*arcXStpRun*arcX[8])-(arcXStpRun*arcXStpRun))*(xPitch/zPitch);  //calculate (lowers) Z to match X truncated value (Z now float)
    arcXStpRad=1;                   //Set X step '1' full values now for X

    //Drive in X -> Z follows until 2nd half arc complete (and arcRadCtRdy shows ready for radius cut)
    while(mtrNewPosX > arcRunRad && arcRadCtRdy > 0)     //Use > here as int Z moves may push X beyond exact equal
    {
      delayMicroseconds(arcDelay);
                                            //TODO: Add arcRapidDelay "if" statement
      X.move(-1*arcXStpRad);
      
      arcXStpRun=arcXStpRun+arcXStpRad;
      arcXStpActual=arcXStpActual+arcXStpRad;
      mtrNewPosX=mtrOldPosX-arcXStpRad;
      mtrOldPosX=mtrNewPosX;
      
      arcZStpRun=sqrt((2.0*arcXStpRun*arcX[8])-(arcXStpRun*arcXStpRun))*(xPitch/zPitch);    //New Z position
      arcZStpRad=int(arcZStpRun)-arcZStpActual; //Current step over '1' minus previous steps
      arcZStpActual=arcZStpActual+arcZStpRad;   //Adds current step to 'tracked' total
      
      if(arcCutDir==0) {
        Z.move(-1*arcZStpRad);    //sometimes '0'
        mtrNewPosZ=mtrOldPosZ-arcZStpRad;
        mtrOldPosZ=mtrNewPosZ;
      }
      else {
        Z.move(arcZStpRad);    //sometimes '0'
        mtrNewPosZ=mtrOldPosZ+arcZStpRad;
        mtrOldPosZ=mtrNewPosZ;
      }
      curStateS1=digitalRead(inPinS1);
      if(curStateS1==LOW) modeCt=999;
    }

    //Drive in Z ONLY to finish motion
    arcZStpRad=1;
    while((arcCutDir==0 && mtrNewPosZ > arcZ[5]) || (arcCutDir==1 && mtrNewPosZ < arcZ[5]))
    {
      delayMicroseconds(arcDelay);                //Delay sets velocity
      if(arcCutDir==0 && mtrNewPosZ > arcZ[5]) {  //safety added
        Z.move(-1*arcZStpRad);
        mtrNewPosZ=mtrOldPosZ-arcZStpRad;
        mtrOldPosZ=mtrNewPosZ;
      }
      else if(arcCutDir==1 && mtrNewPosZ < arcZ[5]) {
        Z.move(arcZStpRad);
        mtrNewPosZ=mtrOldPosZ+arcZStpRad;
        mtrOldPosZ=mtrNewPosZ;
      }
      curStateS1=digitalRead(inPinS1);
      if(curStateS1==LOW) modeCt=999;                         //Dump out if halfnut disengaged too early
    }
  }
}
//*********************************************************
void x6__X_ArcFace()    //External face extend beyond radius
{
  if(arcType==1 && arcRadCtRdy==2 && arcFaceExt < arcRadCntrX)
  {
    while(mtrNewPosX!=arcRunEnd)
    {
      delayMicroseconds(arcDelay);
      if(mtrNewPosX > arcX[6]) arcXStep=-1;
      else arcXStep=1;    //Should never happen
      X.move(arcXStep);
      mtrNewPosX=mtrOldPosX+arcXStep;
      mtrOldPosX=mtrNewPosX;
      curStateS1=digitalRead(inPinS1);
      if(curStateS1==LOW) modeCt=999;
    }
  }
}
//*********************************************************
