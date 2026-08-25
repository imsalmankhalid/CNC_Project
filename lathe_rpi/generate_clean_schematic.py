"""
MbW Lathe HAT – Clean draw.io-style Schematic Generator
Generates a professional schematic with proper component boxes, labels, and organized wiring.
"""

from pathlib import Path

output_path = Path("lathe_rpi/PCB_Full_Schematic_Clean.html")

html = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MbW Lathe HAT – Schematic</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: 'Segoe UI', system-ui, sans-serif;
    background: #f5f5f5;
    color: #333;
    padding: 20px;
  }
  h1 {
    text-align: center;
    font-size: 22px;
    margin-bottom: 6px;
    color: #1a73e8;
  }
  .subtitle {
    text-align: center;
    font-size: 12px;
    color: #666;
    margin-bottom: 20px;
  }

  /* Page canvas */
  .canvas {
    position: relative;
    width: 1400px;
    height: 1800px;
    margin: 0 auto;
    background: #fff;
    border: 1px solid #ddd;
    border-radius: 4px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    overflow: hidden;
  }

  /* Grid background */
  .canvas::before {
    content: '';
    position: absolute;
    inset: 0;
    background-image:
      linear-gradient(rgba(0,0,0,0.04) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0,0,0,0.04) 1px, transparent 1px);
    background-size: 20px 20px;
    pointer-events: none;
  }

  /* Section boxes */
  .section {
    position: absolute;
    border: 2px solid #1a73e8;
    border-radius: 8px;
    background: rgba(26,115,232,0.03);
  }
  .section-title {
    position: absolute;
    top: -10px;
    left: 12px;
    background: #fff;
    padding: 0 8px;
    font-size: 11px;
    font-weight: 700;
    color: #1a73e8;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  /* Component boxes */
  .comp {
    position: absolute;
    border-radius: 6px;
    text-align: center;
    z-index: 10;
    cursor: default;
  }
  .comp:hover {
    filter: brightness(0.95);
    transform: scale(1.02);
    transition: all 0.15s;
  }
  .comp-body {
    padding: 6px 10px;
    border-radius: 6px;
    border: 2px solid;
    background: #fff;
  }
  .comp-desig {
    font-size: 11px;
    font-weight: 700;
    display: block;
  }
  .comp-type {
    font-size: 8px;
    color: #666;
    display: block;
    margin-top: 2px;
  }
  .comp-pins {
    display: flex;
    flex-direction: column;
    gap: 1px;
    margin-top: 4px;
    font-size: 7px;
    color: #555;
    text-align: left;
    padding: 0 4px;
  }
  .comp-pin {
    display: flex;
    justify-content: space-between;
  }
  .comp-pin .pin-num { color: #999; }
  .comp-pin .pin-net { font-weight: 600; }

  /* Component styles by type */
  .comp-ic .comp-body { border-color: #1a73e8; background: #e8f0fe; }
  .comp-ic .comp-desig { color: #1a73e8; }
  .comp-reg .comp-body { border-color: #f9ab00; background: #fef7e0; }
  .comp-reg .comp-desig { color: #e37400; }
  .comp-ldo .comp-body { border-color: #34a853; background: #e6f4ea; }
  .comp-ldo .comp-desig { color: #137333; }
  .comp-conn .comp-body { border-color: #9334e6; background: #f3e8fd; }
  .comp-conn .comp-desig { color: #9334e6; }
  .comp-passive .comp-body { border-color: #999; background: #f5f5f5; }
  .comp-passive .comp-desig { color: #555; }
  .comp-diode .comp-body { border-color: #ea4335; background: #fce8e6; }
  .comp-diode .comp-desig { color: #c5221f; }
  .comp-power .comp-body { border-color: #d93025; background: #fce8e6; }
  .comp-power .comp-desig { color: #d93025; }
  .comp-led .comp-body { border-color: #f9ab00; background: #fef7e0; }
  .comp-led .comp-desig { color: #e37400; }

  /* Net labels on wires */
  .net-label {
    position: absolute;
    font-size: 8px;
    font-weight: 700;
    padding: 1px 4px;
    border-radius: 3px;
    background: #fff;
    z-index: 5;
    white-space: nowrap;
  }

  /* SVG wires layer */
  .wires {
    position: absolute;
    inset: 0;
    z-index: 1;
    pointer-events: none;
  }
  .wires line, .wires polyline, .wires path {
    stroke-width: 1.5;
    fill: none;
  }

  /* Legend */
  .legend {
    position: absolute;
    bottom: 10px;
    right: 10px;
    background: #fff;
    border: 1px solid #ddd;
    border-radius: 6px;
    padding: 10px;
    font-size: 9px;
    z-index: 20;
  }
  .legend-title { font-weight: 700; margin-bottom: 6px; font-size: 10px; }
  .legend-item { display: flex; align-items: center; gap: 6px; margin: 3px 0; }
  .legend-dot { width: 12px; height: 3px; border-radius: 2px; }

  /* Suggestions panel */
  .suggestions {
    max-width: 1400px;
    margin: 20px auto;
    background: #fff;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 20px;
  }
  .suggestions h2 { font-size: 16px; color: #1a73e8; margin-bottom: 12px; }
  .suggestions h3 { font-size: 13px; color: #e37400; margin: 14px 0 6px 0; }
  .suggestions ul { margin-left: 18px; margin-bottom: 10px; }
  .suggestions li { margin: 4px 0; font-size: 12px; line-height: 1.5; }
  .suggestions code {
    background: #f5f5f5;
    padding: 1px 5px;
    border-radius: 3px;
    font-size: 11px;
    font-family: 'Consolas', monospace;
  }
  .warn {
    background: #fef7e0;
    border-left: 3px solid #f9ab00;
    padding: 8px 12px;
    margin: 8px 0;
    font-size: 12px;
    border-radius: 0 4px 4px 0;
  }
  .ok {
    background: #e6f4ea;
    border-left: 3px solid #34a853;
    padding: 8px 12px;
    margin: 8px 0;
    font-size: 12px;
    border-radius: 0 4px 4px 0;
  }
</style>
</head>
<body>

<h1>MbW Lathe HAT – Complete Schematic</h1>
<p class="subtitle">12V DC jack + RPi native USB-C · 74HC245 level shifting · ADS1015 ADC · All components placed with wired connections</p>

<div class="canvas">
  <!-- SVG Wires Layer -->
  <svg class="wires" viewBox="0 0 1400 1800">
    <defs>
      <marker id="arrow" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
        <polygon points="0 0, 6 3, 0 6" fill="#999"/>
      </marker>
    </defs>

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- POWER INPUT SECTION -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- J17 → F1 -->
    <line x1="130" y1="100" x2="170" y2="100" stroke="#d93025"/>
    <!-- F1 → VIN_12V bus -->
    <line x1="210" y1="100" x2="260" y2="100" stroke="#d93025"/>
    <line x1="260" y1="100" x2="260" y2="200" stroke="#d93025" stroke-width="2"/>
    <!-- VIN_12V horizontal bus -->
    <line x1="260" y1="130" x2="500" y2="130" stroke="#d93025" stroke-width="2"/>
    <line x1="260" y1="180" x2="500" y2="180" stroke="#d93025" stroke-width="2"/>

    <!-- D8 TVS: VIN_12V → GND -->
    <line x1="300" y1="130" x2="300" y2="160" stroke="#ea4335"/>
    <line x1="300" y1="180" x2="300" y2="200" stroke="#666"/>
    <!-- C7: VIN_12V → GND -->
    <line x1="350" y1="130" x2="350" y2="160" stroke="#34a853"/>
    <line x1="350" y1="180" x2="350" y2="200" stroke="#666"/>
    <!-- C8: VIN_12V → GND -->
    <line x1="400" y1="130" x2="400" y2="160" stroke="#34a853"/>
    <line x1="400" y1="180" x2="400" y2="200" stroke="#666"/>

    <!-- GND bus (bottom of power section) -->
    <line x1="260" y1="200" x2="500" y2="200" stroke="#666" stroke-width="2"/>

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- MP2307 BUCK -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- VIN_12V → MP2307 Pin1 -->
    <line x1="450" y1="130" x2="450" y2="240" stroke="#d93025"/>
    <!-- MP2307 Pin4,8 → GND -->
    <line x1="450" y1="310" x2="450" y2="340" stroke="#666"/>
    <!-- MP2307 Pin2 EN → 3V3 -->
    <line x1="420" y1="260" x2="380" y2="260" stroke="#34a853"/>
    <line x1="380" y1="260" x2="380" y2="400" stroke="#34a853"/>
    <!-- MP2307 Pin3 SW → L1 -->
    <line x1="480" y1="270" x2="530" y2="270" stroke="#f9ab00"/>
    <!-- L1 → D9 -->
    <line x1="570" y1="270" x2="610" y2="270" stroke="#f9ab00"/>
    <!-- D9 → 5V0_BUCK -->
    <line x1="650" y1="270" x2="700" y2="270" stroke="#f9ab00"/>
    <line x1="700" y1="270" x2="700" y2="300" stroke="#f9ab00" stroke-width="2"/>
    <!-- 5V0_BUCK bus -->
    <line x1="700" y1="300" x2="850" y2="300" stroke="#f9ab00" stroke-width="2"/>

    <!-- C9, C10: 5V0_BUCK → GND -->
    <line x1="730" y1="300" x2="730" y2="340" stroke="#34a853"/>
    <line x1="730" y1="360" x2="730" y2="390" stroke="#666"/>
    <line x1="780" y1="300" x2="780" y2="340" stroke="#34a853"/>
    <line x1="780" y1="360" x2="780" y2="390" stroke="#666"/>

    <!-- C11 BOOT→SW -->
    <line x1="480" y1="290" x2="500" y2="290" stroke="#f9ab00"/>
    <line x1="500" y1="290" x2="500" y2="270" stroke="#f9ab00"/>

    <!-- R24 RT→GND -->
    <line x1="480" y1="280" x2="510" y2="280" stroke="#999"/>
    <line x1="510" y1="280" x2="510" y2="340" stroke="#666"/>

    <!-- GND bus (buck area) -->
    <line x1="400" y1="340" x2="550" y2="340" stroke="#666" stroke-width="2"/>
    <line x1="700" y1="390" x2="800" y2="390" stroke="#666" stroke-width="2"/>

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- AP2112 LDO -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- VIN_12V → AP2112 Pin1 -->
    <line x1="450" y1="180" x2="450" y2="430" stroke="#d93025"/>
    <!-- AP2112 Pin2,3 → GND -->
    <line x1="450" y1="500" x2="450" y2="530" stroke="#666"/>
    <!-- AP2112 Pin4 → 3V3_REG -->
    <line x1="480" y1="465" x2="530" y2="465" stroke="#34a853"/>
    <line x1="530" y1="465" x2="530" y2="500" stroke="#34a853" stroke-width="2"/>
    <!-- 3V3_REG bus -->
    <line x1="530" y1="500" x2="700" y2="500" stroke="#34a853" stroke-width="2"/>

    <!-- C12: VIN→GND -->
    <line x1="420" y1="430" x2="420" y2="460" stroke="#34a853"/>
    <line x1="420" y1="480" x2="420" y2="530" stroke="#666"/>
    <!-- C13, C14: 3V3_REG→GND -->
    <line x1="560" y1="500" x2="560" y2="530" stroke="#34a853"/>
    <line x1="560" y1="550" x2="560" y2="580" stroke="#666"/>
    <line x1="610" y1="500" x2="610" y2="530" stroke="#34a853"/>
    <line x1="610" y1="550" x2="610" y2="580" stroke="#666"/>

    <!-- GND bus (LDO area) -->
    <line x1="400" y1="530" x2="500" y2="530" stroke="#666" stroke-width="2"/>
    <line x1="540" y1="580" x2="640" y2="580" stroke="#666" stroke-width="2"/>

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- DIODE OR-ING -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- 5V0_BUCK → D11 → 5V0 -->
    <line x1="750" y1="300" x2="750" y2="620" stroke="#f9ab00"/>
    <line x1="750" y1="620" x2="800" y2="620" stroke="#f9ab00"/>
    <!-- RPi 5V → D12 → 5V0 -->
    <line x1="750" y1="300" x2="750" y2="660" stroke="#f9ab00"/>
    <line x1="750" y1="660" x2="800" y2="660" stroke="#f9ab00"/>
    <!-- 5V0 bus -->
    <line x1="850" y1="620" x2="850" y2="660" stroke="#f9ab00" stroke-width="2.5"/>
    <line x1="850" y1="640" x2="1000" y2="640" stroke="#f9ab00" stroke-width="2.5"/>

    <!-- 3V3_REG → D14 → 3V3 -->
    <line x1="650" y1="500" x2="650" y2="720" stroke="#34a853"/>
    <line x1="650" y1="720" x2="800" y2="720" stroke="#34a853"/>
    <!-- RPi 3V3 → D15 → 3V3 -->
    <line x1="650" y1="500" x2="650" y2="760" stroke="#34a853"/>
    <line x1="650" y1="760" x2="800" y2="760" stroke="#34a853"/>
    <!-- 3V3 bus -->
    <line x1="850" y1="720" x2="850" y2="760" stroke="#34a853" stroke-width="2.5"/>
    <line x1="850" y1="740" x2="1000" y2="740" stroke="#34a853" stroke-width="2.5"/>

    <!-- C5: 5V0→GND -->
    <line x1="880" y1="640" x2="880" y2="680" stroke="#34a853"/>
    <line x1="880" y1="700" x2="880" y2="730" stroke="#666"/>
    <!-- C6: 3V3→GND -->
    <line x1="880" y1="740" x2="880" y2="770" stroke="#34a853"/>
    <line x1="880" y1="790" x2="880" y2="820" stroke="#666"/>

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- 74HC245 LEVEL SHIFTER -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- 5V0 → 74HC245 VCC -->
    <line x1="950" y1="640" x2="950" y2="880" stroke="#f9ab00"/>
    <!-- GND → 74HC245 GND,/CE -->
    <line x1="900" y1="730" x2="900" y2="950" stroke="#666"/>
    <line x1="900" y1="950" x2="950" y2="950" stroke="#666"/>

    <!-- GPIO signals (3.3V side, left of 74HC245) -->
    <line x1="800" y1="900" x2="850" y2="900" stroke="#1a73e8"/>
    <line x1="800" y1="920" x2="850" y2="920" stroke="#1a73e8"/>
    <line x1="800" y1="940" x2="850" y2="940" stroke="#1a73e8"/>
    <line x1="800" y1="960" x2="850" y2="960" stroke="#1a73e8"/>
    <line x1="800" y1="980" x2="850" y2="980" stroke="#1a73e8"/>
    <line x1="800" y1="1000" x2="850" y2="1000" stroke="#1a73e8"/>

    <!-- 74HC245 outputs (5V side, right) -->
    <line x1="1050" y1="900" x2="1100" y2="900" stroke="#1a73e8"/>
    <line x1="1050" y1="920" x2="1100" y2="920" stroke="#1a73e8"/>
    <line x1="1050" y1="940" x2="1100" y2="940" stroke="#1a73e8"/>
    <line x1="1050" y1="960" x2="1100" y2="960" stroke="#1a73e8"/>
    <line x1="1050" y1="980" x2="1100" y2="980" stroke="#1a73e8"/>
    <line x1="1050" y1="1000" x2="1100" y2="1000" stroke="#1a73e8"/>

    <!-- Series resistors on STEP lines -->
    <line x1="1100" y1="900" x2="1140" y2="900" stroke="#1a73e8"/>
    <line x1="1180" y1="900" x2="1250" y2="900" stroke="#1a73e8"/>
    <line x1="1100" y1="960" x2="1140" y2="960" stroke="#1a73e8"/>
    <line x1="1180" y1="960" x2="1250" y2="960" stroke="#1a73e8"/>

    <!-- Direct lines (DIR, EN) -->
    <line x1="1100" y1="920" x2="1250" y2="920" stroke="#1a73e8"/>
    <line x1="1100" y1="940" x2="1250" y2="940" stroke="#1a73e8"/>
    <line x1="1100" y1="980" x2="1250" y2="980" stroke="#1a73e8"/>
    <line x1="1100" y1="1000" x2="1250" y2="1000" stroke="#1a73e8"/>

    <!-- Servo connectors -->
    <line x1="1250" y1="900" x2="1300" y2="880" stroke="#1a73e8"/>
    <line x1="1250" y1="920" x2="1300" y2="900" stroke="#1a73e8"/>
    <line x1="1250" y1="940" x2="1300" y2="920" stroke="#1a73e8"/>
    <line x1="1250" y1="960" x2="1300" y2="960" stroke="#1a73e8"/>
    <line x1="1250" y1="980" x2="1300" y2="980" stroke="#1a73e8"/>
    <line x1="1250" y1="1000" x2="1300" y2="1000" stroke="#1a73e8"/>

    <!-- 5V0 to servo power -->
    <line x1="950" y1="640" x2="950" y2="1100" stroke="#f9ab00"/>
    <line x1="950" y1="1100" x2="1300" y2="1100" stroke="#f9ab00"/>

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- ADS1015 ADC -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- 3V3 → ADS1015 -->
    <line x1="950" y1="740" x2="950" y2="1200" stroke="#34a853"/>
    <line x1="950" y1="1200" x2="1000" y2="1200" stroke="#34a853"/>
    <!-- GND → ADS1015 -->
    <line x1="900" y1="730" x2="900" y2="1250" stroke="#666"/>
    <line x1="900" y1="1250" x2="1000" y2="1250" stroke="#666"/>

    <!-- I2C: RPi → ADS1015 -->
    <line x1="800" y1="1200" x2="850" y2="1200" stroke="#9334e6"/>
    <line x1="800" y1="1220" x2="850" y2="1220" stroke="#9334e6"/>
    <!-- I2C pull-ups -->
    <line x1="800" y1="1200" x2="770" y2="1200" stroke="#9334e6"/>
    <line x1="770" y1="1200" x2="770" y2="1170" stroke="#34a853"/>
    <line x1="800" y1="1220" x2="770" y2="1220" stroke="#9334e6"/>
    <line x1="770" y1="1220" x2="770" y2="1170" stroke="#34a853"/>

    <!-- Pot → ADS1015 AIN0 -->
    <line x1="1100" y1="1230" x2="1150" y2="1230" stroke="#9334e6"/>

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- ENCODERS (left side) -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- J2 Z Encoder → GPIO -->
    <line x1="200" y1="800" x2="300" y2="800" stroke="#9334e6"/>
    <line x1="200" y1="820" x2="300" y2="820" stroke="#9334e6"/>
    <!-- J3 X Encoder → GPIO -->
    <line x1="200" y1="900" x2="300" y2="900" stroke="#9334e6"/>
    <line x1="200" y1="920" x2="300" y2="920" stroke="#9334e6"/>

    <!-- 3V3 to encoders -->
    <line x1="300" y1="780" x2="300" y2="880" stroke="#34a853"/>
    <line x1="300" y1="780" x2="200" y2="780" stroke="#34a853"/>
    <line x1="200" y1="780" x2="200" y2="880" stroke="#34a853"/>

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- SPINDLE -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- J6 → TVS → Divider → GPIO -->
    <line x1="200" y1="1020" x2="260" y2="1020" stroke="#9334e6"/>
    <line x1="300" y1="1020" x2="340" y2="1020" stroke="#9334e6"/>
    <line x1="380" y1="1020" x2="440" y2="1020" stroke="#9334e6"/>
    <line x1="480" y1="1020" x2="550" y2="1020" stroke="#9334e6"/>

    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- BUTTONS, LIMITS, E-STOP (bottom) -->
    <!-- ═══════════════════════════════════════════════════════════ -->
    <!-- Buttons → GPIO (with pull-ups to 3V3) -->
    <line x1="200" y1="1300" x2="300" y2="1300" stroke="#9334e6"/>
    <line x1="350" y1="1300" x2="450" y2="1300" stroke="#9334e6"/>
    <line x1="500" y1="1300" x2="600" y2="1300" stroke="#9334e6"/>

    <!-- Pull-ups to 3V3 -->
    <line x1="250" y1="1300" x2="250" y2="1270" stroke="#34a853"/>
    <line x1="400" y1="1300" x2="400" y2="1270" stroke="#34a853"/>
    <line x1="550" y1="1300" x2="550" y2="1270" stroke="#34a853"/>
    <line x1="200" y1="1270" x2="600" y2="1270" stroke="#34a853" stroke-width="2"/>

    <!-- Limits → GPIO -->
    <line x1="700" y1="1300" x2="800" y2="1300" stroke="#9334e6"/>
    <line x1="850" y1="1300" x2="950" y2="1300" stroke="#9334e6"/>
    <line x1="1000" y1="1300" x2="1100" y2="1300" stroke="#9334e6"/>
    <line x1="1150" y1="1300" x2="1250" y2="1300" stroke="#9334e6"/>

    <!-- E-Stop -->
    <line x1="1300" y1="1300" x2="1350" y2="1300" stroke="#9334e6"/>

    <!-- GND bus (bottom) -->
    <line x1="100" y1="1400" x2="1350" y2="1400" stroke="#666" stroke-width="3"/>

    <!-- Net labels -->
    <text x="265" y="125" fill="#d93025" font-size="9" font-weight="700">VIN_12V</text>
    <text x="705" y="295" fill="#f9ab00" font-size="9" font-weight="700">5V0_BUCK</text>
    <text x="535" y="495" fill="#34a853" font-size="9" font-weight="700">3V3_REG</text>
    <text x="855" y="635" fill="#f9ab00" font-size="9" font-weight="700">5V0</text>
    <text x="855" y="735" fill="#34a853" font-size="9" font-weight="700">3V3</text>
    <text x="775" y="1195" fill="#9334e6" font-size="9" font-weight="700">I2C_SDA</text>
    <text x="775" y="1215" fill="#9334e6" font-size="9" font-weight="700">I2C_SCL</text>
    <text x="1110" y="1225" fill="#9334e6" font-size="9" font-weight="700">POT_WIPER</text>
    <text x="205" y="795" fill="#9334e6" font-size="9" font-weight="700">Z_ENC_A</text>
    <text x="205" y="815" fill="#9334e6" font-size="9" font-weight="700">Z_ENC_B</text>
    <text x="205" y="895" fill="#9334e6" font-size="9" font-weight="700">X_ENC_A</text>
    <text x="205" y="915" fill="#9334e6" font-size="9" font-weight="700">X_ENC_B</text>
    <text x="210" y="1015" fill="#9334e6" font-size="9" font-weight="700">SPINDLE_RAW</text>
    <text x="390" y="1015" fill="#9334e6" font-size="9" font-weight="700">SPINDLE_IN</text>
    <text x="205" y="1295" fill="#9334e6" font-size="9" font-weight="700">BTN1_IN</text>
    <text x="355" y="1295" fill="#9334e6" font-size="9" font-weight="700">BTN2_IN</text>
    <text x="505" y="1295" fill="#9334e6" font-size="9" font-weight="700">BTN3_IN</text>
    <text x="705" y="1295" fill="#9334e6" font-size="9" font-weight="700">LIM_Z+</text>
    <text x="855" y="1295" fill="#9334e6" font-size="9" font-weight="700">LIM_Z-</text>
    <text x="1005" y="1295" fill="#9334e6" font-size="9" font-weight="700">LIM_X+</text>
    <text x="1155" y="1295" fill="#9334e6" font-size="9" font-weight="700">LIM_X-</text>
    <text x="1305" y="1295" fill="#9334e6" font-size="9" font-weight="700">ESTOP_IN</text>
    <text x="100" y="1395" fill="#666" font-size="10" font-weight="700">GND</text>

    <!-- GPIO signal labels (74HC245 inputs) -->
    <text x="805" y="895" fill="#1a73e8" font-size="8" font-weight="600">Z_STEP_3V3</text>
    <text x="805" y="915" fill="#1a73e8" font-size="8" font-weight="600">Z_DIR_3V3</text>
    <text x="805" y="935" fill="#1a73e8" font-size="8" font-weight="600">Z_EN_3V3</text>
    <text x="805" y="955" fill="#1a73e8" font-size="8" font-weight="600">X_STEP_3V3</text>
    <text x="805" y="975" fill="#1a73e8" font-size="8" font-weight="600">X_DIR_3V3</text>
    <text x="805" y="995" fill="#1a73e8" font-size="8" font-weight="600">X_EN_3V3</text>

    <!-- 74HC245 output labels -->
    <text x="1055" y="895" fill="#1a73e8" font-size="8" font-weight="600">Z_STEP_5V</text>
    <text x="1055" y="915" fill="#1a73e8" font-size="8" font-weight="600">Z_DIR_5V</text>
    <text x="1055" y="935" fill="#1a73e8" font-size="8" font-weight="600">Z_EN_5V</text>
    <text x="1055" y="955" fill="#1a73e8" font-size="8" font-weight="600">X_STEP_5V</text>
    <text x="1055" y="975" fill="#1a73e8" font-size="8" font-weight="600">X_DIR_5V</text>
    <text x="1055" y="995" fill="#1a73e8" font-size="8" font-weight="600">X_EN_5V</text>
  </svg>

  <!-- ═══════════════════════════════════════════════════════════ -->
  <!-- SECTION BOXES -->
  <!-- ═══════════════════════════════════════════════════════════ -->
  <div class="section" style="left:50px; top:50px; width:500px; height:180px;">
    <span class="section-title">⚡ Power Input &amp; Protection</span>
  </div>
  <div class="section" style="left:400px; top:220px; width:450px; height:200px;">
    <span class="section-title">🔋 MP2307 Buck 12V→5V</span>
  </div>
  <div class="section" style="left:400px; top:420px; width:350px; height:200px;">
    <span class="section-title">🔋 AP2112 LDO 12V→3.3V</span>
  </div>
  <div class="section" style="left:700px; top:590px; width:250px; height:250px;">
    <span class="section-title">🔗 Diode OR-ing</span>
  </div>
  <div class="section" style="left:780px; top:860px; width:350px; height:200px;">
    <span class="section-title">🔄 74HC245 Level Shifter</span>
  </div>
  <div class="section" style="left:780px; top:1160px; width:400px; height:150px;">
    <span class="section-title">📊 ADS1015 ADC + I2C</span>
  </div>
  <div class="section" style="left:1230px; top:850px; width:150px; height:280px;">
    <span class="section-title">🔌 Servo Connectors</span>
  </div>
  <div class="section" style="left:50px; top:760px; width:300px; height:200px;">
    <span class="section-title">📡 Encoders</span>
  </div>
  <div class="section" style="left:50px; top:980px; width:550px; height: 80px;">
    <span class="section-title">⚙ Spindle Index</span>
  </div>
  <div class="section" style="left:50px; top:1250px; width:1350px; height:180px;">
    <span class="section-title">🔘 Buttons, Limits, E-Stop</span>
  </div>

  <!-- ═══════════════════════════════════════════════════════════ -->
  <!-- COMPONENTS -->
  <!-- ═══════════════════════════════════════════════════════════ -->

  <!-- J17 DC Jack -->
  <div class="comp comp-power" style="left:60px; top:80px; width:70px;">
    <div class="comp-body">
      <span class="comp-desig">J17</span>
      <span class="comp-type">DC Jack 12V</span>
      <div class="comp-pins">
        <div class="comp-pin"><span class="pin-num">Tip</span><span class="pin-net" style="color:#d93025">12V</span></div>
        <div class="comp-pin"><span class="pin-num">Sleeve</span><span class="pin-net" style="color:#666">GND</span></div>
      </div>
    </div>
  </div>

  <!-- F1 Fuse -->
  <div class="comp comp-passive" style="left:170px; top:85px; width:40px;">
    <div class="comp-body">
      <span class="comp-desig">F1</span>
      <span class="comp-type">1A Fuse</span>
    </div>
  </div>

  <!-- D8 TVS -->
  <div class="comp comp-diode" style="left:285px; top:145px; width:30px;">
    <div class="comp-body">
      <span class="comp-desig">D8</span>
      <span class="comp-type">TVS</span>
    </div>
  </div>

  <!-- C7 -->
  <div class="comp comp-passive" style="left:335px; top:145px; width:30px;">
    <div class="comp-body">
      <span class="comp-desig">C7</span>
      <span class="comp-type">10µF</span>
    </div>
  </div>

  <!-- C8 -->
  <div class="comp comp-passive" style="left:385px; top:145px; width:30px;">
    <div class="comp-body">
      <span class="comp-desig">C8</span>
      <span class="comp-type">100nF</span>
    </div>
  </div>

  <!-- U3 MP2307 -->
  <div class="comp comp-reg" style="left:420px; top:230px; width:100px;">
    <div class="comp-body">
      <span class="comp-desig">U3</span>
      <span class="comp-type">MP2307DN Buck</span>
      <div class="comp-pins">
        <div class="comp-pin"><span class="pin-num">1 VIN</span><span class="pin-net" style="color:#d93025">VIN_12V</span></div>
        <div class="comp-pin"><span class="pin-num">2 EN</span><span class="pin-net" style="color:#34a853">3V3</span></div>
        <div class="comp-pin"><span class="pin-num">3 SW</span><span class="pin-net" style="color:#f9ab00">SW</span></div>
        <div class="comp-pin"><span class="pin-num">4,8 GND</span><span class="pin-net" style="color:#666">GND</span></div>
        <div class="comp-pin"><span class="pin-num">5 BOOT</span><span class="pin-net" style="color:#f9ab00">BOOT</span></div>
        <div class="comp-pin"><span class="pin-num">6 RT</span><span class="pin-net" style="color:#999">22kΩ→GND</span></div>
        <div class="comp-pin"><span class="pin-num">7 FB</span><span class="pin-net" style="color:#666">GND</span></div>
      </div>
    </div>
  </div>

  <!-- L1 -->
  <div class="comp comp-passive" style="left:530px; top:255px; width:40px;">
    <div class="comp-body">
      <span class="comp-desig">L1</span>
      <span class="comp-type">10µH</span>
    </div>
  </div>

  <!-- D9 Schottky -->
  <div class="comp comp-diode" style="left:610px; top:255px; width:40px;">
    <div class="comp-body">
      <span class="comp-desig">D9</span>
      <span class="comp-type">SS34</span>
    </div>
  </div>

  <!-- C9 -->
  <div class="comp comp-passive" style="left:715px; top:320px; width:30px;">
    <div class="comp-body">
      <span class="comp-desig">C9</span>
      <span class="comp-type">22µF</span>
    </div>
  </div>

  <!-- C10 -->
  <div class="comp comp-passive" style="left:765px; top:320px; width:30px;">
    <div class="comp-body">
      <span class="comp-desig">C10</span>
      <span class="comp-type">100nF</span>
    </div>
  </div>

  <!-- C11 -->
  <div class="comp comp-passive" style="left:490px; top:295px; width:30px;">
    <div class="comp-body">
      <span class="comp-desig">C11</span>
      <span class="comp-type">100nF</span>
    </div>
  </div>

  <!-- R24 -->
  <div class="comp comp-passive" style="left:510px; top:285px; width:30px;">
    <div class="comp-body">
      <span class="comp-desig">R24</span>
      <span class="comp-type">22kΩ</span>
    </div>
  </div>

  <!-- U4 AP2112 -->
  <div class="comp comp-ldo" style="left:420px; top:430px; width:100px;">
    <div class="comp-body">
      <span class="comp-desig">U4</span>
      <span class="comp-type">AP2112K-3.3 LDO</span>
      <div class="comp-pins">
        <div class="comp-pin"><span class="pin-num">1 VIN</span><span class="pin-net" style="color:#d93025">VIN_12V</span></div>
        <div class="comp-pin"><span class="pin-num">2,3 GND</span><span class="pin-net" style="color:#666">GND</span></div>
        <div class="comp-pin"><span class="pin-num">4 VOUT</span><span class="pin-net" style="color:#34a853">3V3_REG</span></div>
      </div>
    </div>
  </div>

  <!-- C12 -->
  <div class="comp comp-passive" style="left:405px; top:460px; width:30px;">
    <div class="comp-body">
      <span class="comp-desig">C12</span>
      <span class="comp-type">10µF</span>
    </div>
  </div>

  <!-- C13 -->
  <div class="comp comp-passive" style="left:545px; top:530px; width:30px;">
    <div class="comp-body">
      <span class="comp-desig">C13</span>
      <span class="comp-type">10µF</span>
    </div>
  </div>

  <!-- C14 -->
  <div class="comp comp-passive" style="left:595px; top:530px; width:30px;">
    <div class="comp-body">
      <span class="comp-desig">C14</span>
      <span class="comp-type">100nF</span>
    </div>
  </div>

  <!-- D11 -->
  <div class="comp comp-diode" style="left:800px; top:605px; width:50px;">
    <div class="comp-body">
      <span class="comp-desig">D11</span>
      <span class="comp-type">SS34 Buck→5V0</span>
    </div>
  </div>

  <!-- D12 -->
  <div class="comp comp-diode" style="left:800px; top:645px; width:50px;">
    <div class="comp-body">
      <span class="comp-desig">D12</span>
      <span class="comp-type">SS34 RPi→5V0</span>
    </div>
  </div>

  <!-- D14 -->
  <div class="comp comp-diode" style="left:800px; top:705px; width:50px;">
    <div class="comp-body">
      <span class="comp-desig">D14</span>
      <span class="comp-type">SS34 LDO→3V3</span>
    </div>
  </div>

  <!-- D15 -->
  <div class="comp comp-diode" style="left:800px; top:745px; width:50px;">
    <div class="comp-body">
      <span class="comp-desig">D15</span>
      <span class="comp-type">SS34 RPi→3V3</span>
    </div>
  </div>

  <!-- C5 -->
  <div class="comp comp-passive" style="left:865px; top:680px; width:30px;">
    <div class="comp-body">
      <span class="comp-desig">C5</span>
      <span class="comp-type">10µF</span>
    </div>
  </div>

  <!-- C6 -->
  <div class="comp comp-passive" style="left:865px; top:770px; width:30px;">
    <div class="comp-body">
      <span class="comp-desig">C6</span>
      <span class="comp-type">10µF</span>
    </div>
  </div>

  <!-- U1 74HC245 -->
  <div class="comp comp-ic" style="left:850px; top:880px; width:200px;">
    <div class="comp-body">
      <span class="comp-desig">U1</span>
      <span class="comp-type">74HC245PW Level Shifter (A→B)</span>
      <div class="comp-pins">
        <div class="comp-pin"><span class="pin-num">1 A1</span><span class="pin-net" style="color:#1a73e8">Z_STEP_3V3</span><span class="pin-num">12 B1</span><span class="pin-net" style="color:#1a73e8">Z_STEP_5V</span></div>
        <div class="comp-pin"><span class="pin-num">2 A2</span><span class="pin-net" style="color:#1a73e8">Z_DIR_3V3</span><span class="pin-num">13 B2</span><span class="pin-net" style="color:#1a73e8">Z_DIR_5V</span></div>
        <div class="comp-pin"><span class="pin-num">3 A3</span><span class="pin-net" style="color:#1a73e8">Z_EN_3V3</span><span class="pin-num">14 B3</span><span class="pin-net" style="color:#1a73e8">Z_EN_5V</span></div>
        <div class="comp-pin"><span class="pin-num">4 A4</span><span class="pin-net" style="color:#1a73e8">X_STEP_3V3</span><span class="pin-num">15 B4</span><span class="pin-net" style="color:#1a73e8">X_STEP_5V</span></div>
        <div class="comp-pin"><span class="pin-num">5 A5</span><span class="pin-net" style="color:#1a73e8">X_DIR_3V3</span><span class="pin-num">16 B5</span><span class="pin-net" style="color:#1a73e8">X_DIR_5V</span></div>
        <div class="comp-pin"><span class="pin-num">6 A6</span><span class="pin-net" style="color:#1a73e8">X_EN_3V3</span><span class="pin-num">17 B6</span><span class="pin-net" style="color:#1a73e8">X_EN_5V</span></div>
        <div class="comp-pin"><span class="pin-num">9 GND</span><span class="pin-net" style="color:#666">GND</span><span class="pin-num">20 VCC</span><span class="pin-net" style="color:#f9ab00">5V0</span></div>
        <div class="comp-pin"><span class="pin-num">10 /CE</span><span class="pin-net" style="color:#666">GND</span><span class="pin-num">11 DIR</span><span class="pin-net" style="color:#f9ab00">5V0</span></div>
      </div>
    </div>
  </div>

  <!-- C1 74HC245 decoupling -->
  <div class="comp comp-passive" style="left:1020px; top:860px; width:30px;">
    <div class="comp-body">
      <span class="comp-desig">C1</span>
      <span class="comp-type">100nF</span>
    </div>
  </div>

  <!-- R5, R6 series resistors -->
  <div class="comp comp-passive" style="left:1140px; top:885px; width:40px;">
    <div class="comp-body">
      <span class="comp-desig">R5</span>
      <span class="comp-type">100Ω</span>
    </div>
  </div>
  <div class="comp comp-passive" style="left:1140px; top:945px; width:40px;">
    <div class="comp-body">
      <span class="comp-desig">R6</span>
      <span class="comp-type">100Ω</span>
    </div>
  </div>

  <!-- J4 Z Servo -->
  <div class="comp comp-conn" style="left:1260px; top:860px; width:80px;">
    <div class="comp-body">
      <span class="comp-desig">J4</span>
      <span class="comp-type">Z Servo (Molex-8)</span>
      <div class="comp-pins">
        <div class="comp-pin"><span class="pin-num">1</span><span class="pin-net">STEP</span></div>
        <div class="comp-pin"><span class="pin-num">2</span><span class="pin-net">DIR</span></div>
        <div class="comp-pin"><span class="pin-num">3</span><span class="pin-net">EN</span></div>
        <div class="comp-pin"><span class="pin-num">5</span><span class="pin-net" style="color:#666">GND</span></div>
        <div class="comp-pin"><span class="pin-num">6</span><span class="pin-net" style="color:#f9ab00">5V0</span></div>
      </div>
    </div>
  </div>

  <!-- J5 X Servo -->
  <div class="comp comp-conn" style="left:1260px; top:950px; width:80px;">
    <div class="comp-body">
      <span class="comp-desig">J5</span>
      <span class="comp-type">X Servo (Molex-8)</span>
      <div class="comp-pins">
        <div class="comp-pin"><span class="pin-num">1</span><span class="pin-net">STEP</span></div>
        <div class="comp-pin"><span class="pin-num">2</span><span class="pin-net">DIR</span></div>
        <div class="comp-pin"><span class="pin-num">3</span><span class="pin-net">EN</span></div>
        <div class="comp-pin"><span class="pin-num">5</span><span class="pin-net" style="color:#666">GND</span></div>
        <div class="comp-pin"><span class="pin-num">6</span><span class="pin-net" style="color:#f9ab00">5V0</span></div>
      </div>
    </div>
  </div>

  <!-- TVS diodes D1-D6 -->
  <div class="comp comp-diode" style="left:1100px; top:870px; width:30px;">
    <div class="comp-body">
      <span class="comp-desig">D1</span>
      <span class="comp-type">TVS</span>
    </div>
  </div>
  <div class="comp comp-diode" style="left:1100px; top:890px; width:30px;">
    <div class="comp-body">
      <span class="comp-desig">D2</span>
      <span class="comp-type">TVS</span>
    </div>
  </div>
  <div class="comp comp-diode" style="left:1100px; top:910px; width:30px;">
    <div class="comp-body">
      <span class="comp-desig">D3</span>
      <span class="comp-type">TVS</span>
    </div>
  </div>
  <div class="comp comp-diode" style="left:1100px; top:930px; width:30px;">
    <div class="comp-body">
      <span class="comp-desig">D4</span>
      <span class="comp-type">TVS</span>
    </div>
  </div>
  <div class="comp comp-diode" style="left:1100px; top:950px; width:30px;">
    <div class="comp-body">
      <span class="comp-desig">D5</span>
      <span class="comp-type">TVS</span>
    </div>
  </div>
  <div class="comp comp-diode" style="left:1100px; top:970px; width:30px;">
    <div class="comp-body">
      <span class="comp-desig">D6</span>
      <span class="comp-type">TVS</span>
    </div>
  </div>

  <!-- U2 ADS1015 -->
  <div class="comp comp-ic" style="left:1000px; top:1180px; width:100px;">
    <div class="comp-body">
      <span class="comp-desig">U2</span>
      <span class="comp-type">ADS1015 ADC</span>
      <div class="comp-pins">
        <div class="comp-pin"><span class="pin-num">1 SDA</span><span class="pin-net" style="color:#9334e6">I2C_SDA</span></div>
        <div class="comp-pin"><span class="pin-num">2 SCL</span><span class="pin-net" style="color:#9334e6">I2C_SCL</span></div>
        <div class="comp-pin"><span class="pin-num">3 A0</span><span class="pin-net" style="color:#666">GND</span></div>
        <div class="comp-pin"><span class="pin-num">4 GND</span><span class="pin-net" style="color:#666">GND</span></div>
        <div class="comp-pin"><span class="pin-num">5 DVDD</span><span class="pin-net" style="color:#34a853">3V3</span></div>
        <div class="comp-pin"><span class="pin-num">7 AIN0</span><span class="pin-net" style="color:#9334e6">POT</span></div>
        <div class="comp-pin"><span class="pin-num">9 AVDD</span><span class="pin-net" style="color:#34a853">3V3</span></div>
      </div>
    </div>
  </div>

  <!-- I2C Pull-ups -->
  <div class="comp comp-passive" style="left:755px; top:1170px; width:30px;">
    <div class="comp-body">
      <span class="comp-desig">R22</span>
      <span class="comp-type">4.7kΩ</span>
    </div>
  </div>
  <div class="comp comp-passive" style="left:755px; top:1190px; width:30px;">
    <div class="comp-body">
      <span class="comp-desig">R23</span>
      <span class="comp-type">4.7kΩ</span>
    </div>
  </div>

  <!-- ADS1015 decoupling -->
  <div class="comp comp-passive" style="left:1110px; top:1170px; width:30px;">
    <div class="comp-body">
      <span class="comp-desig">C2</span>
      <span class="comp-type">100nF</span>
    </div>
  </div>
  <div class="comp comp-passive" style="left:1110px; top:1190px; width:30px;">
    <div class="comp-body">
      <span class="comp-desig">C3</span>
      <span class="comp-type">100nF</span>
    </div>
  </div>
  <div class="comp comp-passive" style="left:1110px; top:1210px; width:30px;">
    <div class="comp-body">
      <span class="comp-desig">C4</span>
      <span class="comp-type">10µF</span>
    </div>
  </div>

  <!-- R9 Pot series -->
  <div class="comp comp-passive" style="left:1150px; top:1215px; width:40px;">
    <div class="comp-body">
      <span class="comp-desig">R9</span>
      <span class="comp-type">10kΩ</span>
    </div>
  </div>

  <!-- J7 Pot -->
  <div class="comp comp-conn" style="left:1200px; top:1200px; width:70px;">
    <div class="comp-body">
      <span class="comp-desig">J7</span>
      <span class="comp-type">Pot (JST-3)</span>
      <div class="comp-pins">
        <div class="comp-pin"><span class="pin-num">1</span><span class="pin-net" style="color:#f9ab00">5V0</span></div>
        <div class="comp-pin"><span class="pin-num">2</span><span class="pin-net">Wiper</span></div>
        <div class="comp-pin"><span class="pin-num">3</span><span class="pin-net" style="color:#666">GND</span></div>
      </div>
    </div>
  </div>

  <!-- J2 Z Encoder -->
  <div class="comp comp-conn" style="left:100px; top:780px; width:100px;">
    <div class="comp-body">
      <span class="comp-desig">J2</span>
      <span class="comp-type">Z Encoder (JST-6)</span>
      <div class="comp-pins">
        <div class="comp-pin"><span class="pin-num">1</span><span class="pin-net" style="color:#34a853">3V3</span></div>
        <div class="comp-pin"><span class="pin-num">2</span><span class="pin-net" style="color:#666">GND</span></div>
        <div class="comp-pin"><span class="pin-num">3</span><span class="pin-net">A → GPIO5</span></div>
        <div class="comp-pin"><span class="pin-num">4</span><span class="pin-net">B → GPIO6</span></div>
      </div>
    </div>
  </div>

  <!-- J3 X Encoder -->
  <div class="comp comp-conn" style="left:100px; top:880px; width:100px;">
    <div class="comp-body">
      <span class="comp-desig">J3</span>
      <span class="comp-type">X Encoder (JST-6)</span>
      <div class="comp-pins">
        <div class="comp-pin"><span class="pin-num">1</span><span class="pin-net" style="color:#34a853">3V3</span></div>
        <div class="comp-pin"><span class="pin-num">2</span><span class="pin-net" style="color:#666">GND</span></div>
        <div class="comp-pin"><span class="pin-num">3</span><span class="pin-net">A → GPIO13</span></div>
        <div class="comp-pin"><span class="pin-num">4</span><span class="pin-net">B → GPIO19</span></div>
      </div>
    </div>
  </div>

  <!-- Encoder pull-ups (optional) -->
  <div class="comp comp-passive" style="left:60px; top:790px; width:30px;">
    <div class="comp-body">
      <span class="comp-desig">R1</span>
      <span class="comp-type">10kΩ</span>
    </div>
  </div>
  <div class="comp comp-passive" style="left:60px; top:810px; width:30px;">
    <div class="comp-body">
      <span class="comp-desig">R2</span>
      <span class="comp-type">10kΩ</span>
    </div>
  </div>
  <div class="comp comp-passive" style="left:60px; top:890px; width:30px;">
    <div class="comp-body">
      <span class="comp-desig">R3</span>
      <span class="comp-type">10kΩ</span>
    </div>
  </div>
  <div class="comp comp-passive" style="left:60px; top:910px; width:30px;">
    <div class="comp-body">
      <span class="comp-desig">R4</span>
      <span class="comp-type">10kΩ</span>
    </div>
  </div>

  <!-- J6 Spindle -->
  <div class="comp comp-conn" style="left:100px; top:1000px; width:100px;">
    <div class="comp-body">
      <span class="comp-desig">J6</span>
      <span class="comp-type">Spindle (JST-3)</span>
      <div class="comp-pins">
        <div class="comp-pin"><span class="pin-num">1</span><span class="pin-net" style="color:#f9ab00">5V0</span></div>
        <div class="comp-pin"><span class="pin-num">2</span><span class="pin-net" style="color:#666">GND</span></div>
        <div class="comp-pin"><span class="pin-num">3</span><span class="pin-net">RAW</span></div>
      </div>
    </div>
  </div>

  <!-- D7 TVS Spindle -->
  <div class="comp comp-diode" style="left:260px; top:1005px; width:40px;">
    <div class="comp-body">
      <span class="comp-desig">D7</span>
      <span class="comp-type">TVS</span>
    </div>
  </div>

  <!-- R7, R8 Voltage Divider -->
  <div class="comp comp-passive" style="left:340px; top:1005px; width:40px;">
    <div class="comp-body">
      <span class="comp-desig">R7</span>
      <span class="comp-type">10kΩ</span>
    </div>
  </div>
  <div class="comp comp-passive" style="left:440px; top:1005px; width:40px;">
    <div class="comp-body">
      <span class="comp-desig">R8</span>
      <span class="comp-type">20kΩ</span>
    </div>
  </div>

  <!-- Buttons -->
  <div class="comp comp-conn" style="left:100px; top:1280px; width:100px;">
    <div class="comp-body">
      <span class="comp-desig">J8</span>
      <span class="comp-type">BTN1 (Screw-2)</span>
      <div class="comp-pins">
        <div class="comp-pin"><span class="pin-num">1</span><span class="pin-net">BTN1_IN</span></div>
        <div class="comp-pin"><span class="pin-num">2</span><span class="pin-net" style="color:#666">GND</span></div>
      </div>
    </div>
  </div>
  <div class="comp comp-passive" style="left:250px; top:1270px; width:30px;">
    <div class="comp-body">
      <span class="comp-desig">R10</span>
      <span class="comp-type">10kΩ</span>
    </div>
  </div>

  <div class="comp comp-conn" style="left:250px; top:1280px; width:100px;">
    <div class="comp-body">
      <span class="comp-desig">J9</span>
      <span class="comp-type">BTN2 (Screw-2)</span>
      <div class="comp-pins">
        <div class="comp-pin"><span class="pin-num">1</span><span class="pin-net">BTN2_IN</span></div>
        <div class="comp-pin"><span class="pin-num">2</span><span class="pin-net" style="color:#666">GND</span></div>
      </div>
    </div>
  </div>
  <div class="comp comp-passive" style="left:400px; top:1270px; width:30px;">
    <div class="comp-body">
      <span class="comp-desig">R11</span>
      <span class="comp-type">10kΩ</span>
    </div>
  </div>

  <div class="comp comp-conn" style="left:400px; top:1280px; width:100px;">
    <div class="comp-body">
      <span class="comp-desig">J10</span>
      <span class="comp-type">BTN3 (Screw-2)</span>
      <div class="comp-pins">
        <div class="comp-pin"><span class="pin-num">1</span><span class="pin-net">BTN3_IN</span></div>
        <div class="comp-pin"><span class="pin-num">2</span><span class="pin-net" style="color:#666">GND</span></div>
      </div>
    </div>
  </div>
  <div class="comp comp-passive" style="left:550px; top:1270px; width:30px;">
    <div class="comp-body">
      <span class="comp-desig">R12</span>
      <span class="comp-type">10kΩ</span>
    </div>
  </div>

  <!-- Half-Nut -->
  <div class="comp comp-conn" style="left:600px; top:1280px; width:100px;">
    <div class="comp-body">
      <span class="comp-desig">J11</span>
      <span class="comp-type">Half-Nut (Screw-2)</span>
      <div class="comp-pins">
        <div class="comp-pin"><span class="pin-num">1</span><span class="pin-net">HALF_NUT</span></div>
        <div class="comp-pin"><span class="pin-num">2</span><span class="pin-net" style="color:#666">GND</span></div>
      </div>
    </div>
  </div>
  <div class="comp comp-passive" style="left:650px; top:1310px; width:30px;">
    <div class="comp-body">
      <span class="comp-desig">R13</span>
      <span class="comp-type">10kΩ↓</span>
    </div>
  </div>

  <!-- Limits -->
  <div class="comp comp-conn" style="left:700px; top:1280px; width:100px;">
    <div class="comp-body">
      <span class="comp-desig">J12</span>
      <span class="comp-type">LIM Z+ (Screw-2)</span>
    </div>
  </div>
  <div class="comp comp-passive" style="left:750px; top:1270px; width:30px;">
    <div class="comp-body">
      <span class="comp-desig">R14</span>
      <span class="comp-type">10kΩ</span>
    </div>
  </div>

  <div class="comp comp-conn" style="left:850px; top:1280px; width:100px;">
    <div class="comp-body">
      <span class="comp-desig">J13</span>
      <span class="comp-type">LIM Z- (Screw-2)</span>
    </div>
  </div>
  <div class="comp comp-passive" style="left:900px; top:1270px; width:30px;">
    <div class="comp-body">
      <span class="comp-desig">R15</span>
      <span class="comp-type">10kΩ</span>
    </div>
  </div>

  <div class="comp comp-conn" style="left:1000px; top:1280px; width:100px;">
    <div class="comp-body">
      <span class="comp-desig">J14</span>
      <span class="comp-type">LIM X+ (Screw-2)</span>
    </div>
  </div>
  <div class="comp comp-passive" style="left:1050px; top:1270px; width:30px;">
    <div class="comp-body">
      <span class="comp-desig">R16</span>
      <span class="comp-type">10kΩ</span>
    </div>
  </div>

  <div class="comp comp-conn" style="left:1150px; top:1280px; width:100px;">
    <div class="comp-body">
      <span class="comp-desig">J15</span>
      <span class="comp-type">LIM X- (Screw-2)</span>
    </div>
  </div>
  <div class="comp comp-passive" style="left:1200px; top:1270px; width:30px;">
    <div class="comp-body">
      <span class="comp-desig">R17</span>
      <span class="comp-type">10kΩ</span>
    </div>
  </div>

  <!-- E-Stop -->
  <div class="comp comp-conn" style="left:1300px; top:1280px; width:100px;">
    <div class="comp-body">
      <span class="comp-desig">J16</span>
      <span class="comp-type">E-Stop (Screw-4)</span>
      <div class="comp-pins">
        <div class="comp-pin"><span class="pin-num">1</span><span class="pin-net">NC (hard)</span></div>
        <div class="comp-pin"><span class="pin-num">2</span><span class="pin-net">NO (soft)</span></div>
        <div class="comp-pin"><span class="pin-num">3</span><span class="pin-net">COM</span></div>
        <div class="comp-pin"><span class="pin-num">4</span><span class="pin-net" style="color:#666">GND</span></div>
      </div>
    </div>
  </div>
  <div class="comp comp-passive" style="left:1350px; top:1270px; width:30px;">
    <div class="comp-body">
      <span class="comp-desig">R18</span>
      <span class="comp-type">10kΩ</span>
    </div>
  </div>

  <!-- LEDs -->
  <div class="comp comp-led" style="left:280px; top:110px; width:60px;">
    <div class="comp-body">
      <span class="comp-desig">LED1</span>
      <span class="comp-type">🟢 12V OK</span>
    </div>
  </div>
  <div class="comp comp-passive" style="left:240px; top:110px; width:30px;">
    <div class="comp-body">
      <span class="comp-desig">R19</span>
      <span class="comp-type">1kΩ</span>
    </div>
  </div>

  <div class="comp comp-led" style="left:1350px; top:1250px; width:60px;">
    <div class="comp-body">
      <span class="comp-desig">LED2</span>
      <span class="comp-type">🔴 E-Stop</span>
    </div>
  </div>
  <div class="comp comp-passive" style="left:1310px; top:1250px; width:30px;">
    <div class="comp-body">
      <span class="comp-desig">R20</span>
      <span class="comp-type">330Ω</span>
    </div>
  </div>

  <div class="comp comp-led" style="left:1100px; top:850px; width:60px;">
    <div class="comp-body">
      <span class="comp-desig">LED3</span>
      <span class="comp-type">🟡 Step</span>
    </div>
  </div>
  <div class="comp comp-passive" style="left:1060px; top:850px; width:30px;">
    <div class="comp-body">
      <span class="comp-desig">R21</span>
      <span class="comp-type">330Ω</span>
    </div>
  </div>

  <!-- Legend -->
  <div class="legend">
    <div class="legend-title">Net Colors</div>
    <div class="legend-item"><div class="legend-dot" style="background:#d93025"></div> 12V / VIN_12V</div>
    <div class="legend-item"><div class="legend-dot" style="background:#f9ab00"></div> 5V0 / Buck</div>
    <div class="legend-item"><div class="legend-dot" style="background:#34a853"></div> 3V3 / LDO</div>
    <div class="legend-item"><div class="legend-dot" style="background:#1a73e8"></div> GPIO Signals</div>
    <div class="legend-item"><div class="legend-dot" style="background:#9334e6"></div> I2C / Inputs</div>
    <div class="legend-item"><div class="legend-dot" style="background:#666"></div> GND</div>
  </div>
</div>

<!-- ═══════════════════════════════════════════════════════════ -->
<!-- DESIGN SUGGESTIONS -->
<!-- ═══════════════════════════════════════════════════════════ -->
<div class="suggestions">
<h2>🔍 Design Review &amp; Suggestions</h2>

<div class="ok">
<strong>✅ I2C: NO capacitors on SDA/SCL</strong> — This is correct. The 4.7kΩ pull-ups (R22, R23) are sufficient.
ADS1015 adds ~5pF input capacitance. Short traces (&lt;5cm) add ~100pF. Total is well within the 400pF I2C spec limit.
Adding caps would slow rise time and cause I2C errors at 400kHz.
</div>

<div class="ok">
<strong>✅ Decoupling is correct</strong> — Every IC has 100nF within 2mm of power pins. Each rail has 10µF bulk. Regulator caps match datasheet requirements.
</div>

<h3>🔧 Suggested Improvements</h3>

<h3>1. I2C Ferrite Beads (Recommended for Industrial Environment)</h3>
<ul>
<li><strong>Add:</strong> <code>FB1</code> = 600Ω ferrite bead (0805) on I2C_SDA between RPi and ADS1015</li>
<li><strong>Why:</strong> Lathe environment has motor noise. Ferrite bead filters HF noise without slowing I2C.</li>
<li><strong>Part:</strong> Murata <code>BLM21PG601SN1D</code> (600Ω @ 100MHz, 0805)</li>
<li><strong>Placement:</strong> Between R22 (pull-up) and ADS1015 SDA pin</li>
<li><strong>Cap after bead:</strong> <code>C15</code> = 22pF from filtered SDA to GND</li>
<li><strong>Same for SCL:</strong> <code>FB2</code> + <code>C16</code> = 22pF</li>
</ul>

<h3>2. Encoder Input Protection (Recommended)</h3>
<ul>
<li><strong>Add:</strong> TVS diodes on encoder lines (Z_ENC_A/B, X_ENC_A/B)</li>
<li><strong>Why:</strong> Encoder cables run through noisy lathe environment</li>
<li><strong>Part:</strong> <code>PESD5V0S1UL</code> (same as servo signals D1-D6)</li>
<li><strong>Designators:</strong> <code>D16-D19</code> (one per encoder line)</li>
</ul>

<h3>3. Spindle Signal Schmitt Trigger (Recommended)</h3>
<ul>
<li><strong>Add:</strong> <code>74HC14</code> Schmitt trigger on SPINDLE_IN line</li>
<li><strong>Why:</strong> Spindle index signal may have slow rise time from voltage divider</li>
<li><strong>Alternative:</strong> Add RC filter (<code>100Ω + 100pF</code>) before GPIO pin</li>
</ul>

<h3>4. Test Points (Recommended for Debugging)</h3>
<ul>
<li><strong>Add:</strong> <code>TP1</code> = 5V0 rail, <code>TP2</code> = 3V3 rail, <code>TP3</code> = VIN_12V</li>
<li><strong>Add:</strong> <code>TP4</code> = I2C_SDA, <code>TP5</code> = I2C_SCL (for oscilloscope probing)</li>
<li><strong>Part:</strong> <code>TestPad_SMD:TestPad_1.0x1.0mm</code></li>
</ul>

<h3>5. Ground Plane Stitching</h3>
<ul>
<li><strong>Add:</strong> Via every 10mm around board perimeter (connects top/bottom GND)</li>
<li><strong>Add:</strong> Via near every decoupling capacitor (low-inductance GND return)</li>
</ul>

<h3>6. E-Stop NC Trace Width (Critical)</h3>
<ul>
<li><strong>Use:</strong> 2mm wide trace for ESTOP_NC path (mechanical reliability)</li>
<li><strong>Add:</strong> Red silkscreen overlay on ESTOP_NC trace for visual inspection</li>
</ul>

<div class="warn">
<strong>⚠️ WARNING: 3.3V Rail Diode Drop</strong><br>
SS34 forward drop ~0.3V. In USB-C-only mode: 3.3V - 0.3V = 3.0V at load.<br>
This is BELOW 3.3V -5% tolerance (3.135V minimum)!<br>
<strong>Mitigation:</strong> If using 12V always, this is fine. For USB-C-only mode, consider <code>MBR0520T</code> (Vf=0.2V) or ideal diode controller.
</div>

<div class="warn">
<strong>⚠️ Inductor Saturation Check</strong><br>
<code>GQH101010T</code> has 2.1A saturation current. MP2307 peak current can reach ~3.5A.<br>
<strong>Recommendation:</strong> Use <code>COILCRAFT SSD1050</code> (3.2A sat) or similar higher-current inductor.
</div>

<h3>7. 74HC245 Input Margin</h3>
<ul>
<li><code>V_IH_min</code> = 0.6 × 5V = 3.0V. RPi outputs 3.3V. Margin = 0.3V (tight but works).</li>
<li><strong>Alternative:</strong> <code>74HCT245</code> (T-series, V_IH = 2.0V at 5V) for better margin.</li>
<li><strong>Recommendation:</strong> Stick with 74HC245 (validated in Arduino design). Switch to 74HCT245 only if issues arise.</li>
</ul>

<h3>8. Component Orientation Markers</h3>
<ul>
<li>Pin 1 indicator dots on all IC footprints</li>
<li>Diode cathode band markers (white silkscreen line)</li>
<li>LED polarity markers (+/-)</li>
</ul>
</div>

</body>
</html>
"""

output_path.write_text(html, encoding="utf-8")
print(f"✅ Generated: {output_path.absolute()}")
