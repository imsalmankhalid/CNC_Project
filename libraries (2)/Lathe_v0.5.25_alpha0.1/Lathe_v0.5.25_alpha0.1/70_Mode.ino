//*********************************************************
//  modeSetup()
//*********************************************************
void modeSetup()
{
  if(modeCt > 998)
  {
    if(modeCt==999) 
    {
      lcd.setCursor(0,2);
      lcd.print("Select Mode, B3:OK  ");
      lcd.setCursor(0,3);
      lcd.print("Mode=               ");
      
      tQustCt=0;
      thrdRpm = 0.0;
      thrdRpmRcmnd = 0.0;
      thrdRpmActual = 0.0;
      thrdIndexTime = 0;
      thrdRpmTemp = 0.0;
      tSizePos=0;
      tMtlPos=0;
      tTlPos=0;
      thrdOdMeasOffset=0.0;
      thrdC391Offset=0.0;
      thrdTipDim = 0.0;
      thrdXRetract = 0.0;
      thrdZEnd = 0.0;
      thrdZStart = 0.0;  
      thrdPassNum=0;
      thrdAutoSpr = 2;
      tSprCnt = 0;
      thrdXDepthPos = 0; 
      thrdInfeedTotal = 0;
      thrdInfeed1stPass = 0;
      thrdInfeed = 0;
      thrdOffset1stPass = 0;
      thrdOffset = 0;
      tNxtOpPos = 0;      
      thrdInfeedAdj=0.0;
      thrdCutStep = 1;
      thrdFeedRcmnd = 0.0;
      thrdFeedActual = 0.0;
      thrdCutDelay = 0;
      thrdCutDelayCalc = 0;
      thrdCutDelayProg = 100;
      thrdCutDelayAdj = 0;
      sIndexTimeNSaved = 0;
      mtrCntsPerIndex = 0;
      mtrCntOrig = 0.0;
      mtrCntExpSaved = 0.0;
      deltaCnts = 0.0;
      deltaDelay = 0;
      spindleRpm3 = 0;
      //-------------
      tprQustCt = 0;
      tprStkOD = 12.7;
      tprStkRad = 0;
      tprXRetract = 0;
      tprNumPnts = 3;
      for(int tpru=0; tpru < 10; tpru++) {
        tprZPos[tpru] = 0;
        tprZPosOffst[tpru] = 0;
        tprXRad[tpru] = 0;
        tprXRadOffst[tpru] = 0;
        tprXRadRun[tpru] = 0;
      }
      tprCutDir = 0;
      tprArSize = 0;
      tprOD = 0.0;
      tprDpthCut = 0.5*(xMtrCntPerRev/xPitch);
      tprDpthFinCut = 0.07*(xMtrCntPerRev/xPitch);
      tprMaxDp = 0.0;
      tprMaxArPos = 0;
      tprMaxDpOffst=0;
      tprCntl = 0;
      tprSpdChange=0;
      //-------------
      arcQustCt = 0;
      arcType = 0; 
      arcInsType = 0;
      arcInsRad = 5.0;
      arcInsRadCntX = 0;
      arcInsRadCntZ = 0;
      arcStkOD = 25.4;
      arcStkRad = 0;
      arcStkCntr = 0;
      arcTngFace = 0;
      arcMaxStk = 0;
      arcRadCntrZ = 0;
      arcRadCntrX = 0;
      arcRadCutSzZ = 0;
      arcRadCutSzX = 0;
      arcRadDisp = 0.0;
      arcTngOdRad = 0;
      arcTngOdDisp = 0;
      arcCnt = 0;
      arcCntDisp = 0;
      arcTngOdExt = 0;
      arcFaceExt = 0;
      arcCutDir = 0;
      arcDpthCutX = 0.60*(xMtrCntPerRev/xPitch);  //(240 cnts) Default is 0.60mm~=0.024"
      arcXFin = 0.10*(xMtrCntPerRev/xPitch);      //(40  cnts) Default is 0.10mm~=0.004"
      arcZFin = arcXFin*xPitch/zPitch;            //For Z offset TODO: check what is used on taper z offset.
      arcArSize = 8;
      //arcXFinAr[] = {0,0,0,0,0,0,0,0};      //Keep previous values??
      //arcZFinAr[] = {0,0,0,0,0,0,0,0};      //Keep previous values??
      //arcXOffAr[] = {0,0,0,0,0,0,0,0};      //Keep previous values??
      //arcZOffAr[] = {0,0,0,0,0,0,0,0};      //Keep previous values??
      //arcX[] =      {0,0,0,0,0,0,0,0,0};    //Keep previous values??
      //arcZ[] =      {0,0,0,0,0,0,0,0,0,0};  //Keep previous values??
      arcRunStrt = 0;
      arcRunRad = 0;
      arcRunEnd = 0;
      arcRapidDelay = 700;           
      //arcRapidStep;
      //arcXStep;
      //arcZStep;
      arcDelay=1000;
      arcDelayCode=140;
      arcSpdChange=0;
      arcCntl = 0;
      arcRadCtRdy=0;
      //arcPassTtl;
      //arcPassCrnt;
      //arcXStpRad;
      //arcZStpRad;
      //arcXStpRun;
      //arcZStpRun;
      //arcXStpActual;
      //arcZStpActual;
      aNxtOpPos=0;
      arcZOffset=0;
      arcXOffset=0;
      arcZOffAct=0;
      arcXOffAct=0; 

      displayLcdFullValZ();
      displayLcdFullValX();
  
      modeCt=1000;
      modeCtOld=999;
    }
    if(modeCt > 999) modeButtons();
    if(modeCt > 999 && modeCt!=modeCtOld)
    {
      lcd.setCursor(5,3);
      lcd.print(modeTxt[(modeCt-1000)]);
      modeCtOld=modeCt;
    }
  }
}
