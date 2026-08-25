# DRC Fix - Quick Reference

## 🚨 Critical Issues

**POWER TRACES (+5V):** 0.15mm → 1.0mm ⚠️ FIX IMMEDIATELY

## 📊 Error Count

- **Total:** 16 errors
- **Track Width:** 12 errors
- **Silkscreen:** 4 errors

## ⚡ Quick Fix

### In KiCad Pcbnew:

```python
# Open Tools → Scripting Console, then:
exec(open('fix_all_drc_errors.py').read())
```

**Then:**
1. Save board (Ctrl+S)
2. Run DRC (Ctrl+Shift+I)
3. Verify 0 errors

## 📝 Track Width Fixes

| Net | Current | Required |
|-----|---------|----------|
| +5V | 0.15mm | 1.0mm |
| GPIO2/SDA1 | 0.15mm | 0.3mm |
| Q1-G (gate) | 0.15mm | 0.3mm |
| Q2A-B1 (base) | 0.15mm | 0.25mm |
| J6-Pin_2 | 0.15mm | 0.25mm |

## 🎨 Silkscreen Fixes

Move these references:
- **R7:** Up 2mm
- **R5:** Right 2mm
- **R6:** Up 2mm
- **C4:** Down 2mm

## 📚 Full Documentation

- **Analysis:** [DRC_Analysis_and_Resolution.md](DRC_Analysis_and_Resolution.md)
- **Manual Procedure:** [DRC_FIX_PROCEDURE.md](DRC_FIX_PROCEDURE.md)
- **Complete Guide:** [README_DRC_FIXES.md](README_DRC_FIXES.md)

## ⏱️ Time Estimate

- **Automated:** 5-10 minutes
- **Manual:** 1-3 hours

## ✅ Success Criteria

- [ ] DRC shows 0 errors
- [ ] Power traces ≥ 1.0mm
- [ ] All traces ≥ 0.2mm
- [ ] No silkscreen overlaps
- [ ] 3D view looks correct
