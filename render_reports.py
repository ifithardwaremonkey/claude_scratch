import markdown, re, sys
css = """
body{font-family:Helvetica,Arial,sans-serif;font-size:10.5pt;line-height:1.35;margin:28px 40px;color:#111}
h1{font-size:20pt;margin-bottom:4px} h2{font-size:14pt;border-bottom:1px solid #999;padding-bottom:3px;margin-top:26px}
h3{font-size:11.5pt;margin-top:18px}
table{border-collapse:collapse;width:100%;margin:8px 0 14px;font-size:9.2pt}
th,td{border:1px solid #bbb;padding:4px 6px;vertical-align:top;text-align:left}
th{background:#eee} tr{page-break-inside:avoid}
code{font-family:Menlo,Consolas,monospace;font-size:9pt;background:#f3f3f3;padding:0 2px}
li{margin:3px 0}
hr{border:0;border-top:1px solid #ccc;margin:20px 0}
"""
def badge(txt,color): return f'<span style="background:{color};color:#fff;padding:1px 6px;border-radius:3px;font-weight:bold;white-space:nowrap">{txt}</span>'
RED,AMB,BLU,GRN="#c62828","#ef6c00","#1565c0","#2e7d32"
def colorize(h):
    h=re.sub(r'(?<!bold">)(?<![\w-])STOP-SHIP(?![\w-])', badge("STOP-SHIP",RED), h)
    h=re.sub(r'(?<!bold">)(?<![\w-])GATE(?![\w-])', badge("GATE",AMB), h)
    for t,c in [("Not ready",RED),("Low",AMB),("Medium",BLU),("High",GRN)]:
        h=h.replace(f"<td><strong>{t}</strong></td>", f"<td>{badge(t,c)}</td>")
    h=re.sub(r"<strong>(Closed[^<]*|Confirmed[^<]*|Resolved[^<]*|Answered[^<]*|Partly answered[^<]*|Partly closed[^<]*)</strong>", lambda m: badge("CLOSED",GRN)+" <strong>"+m.group(1)+"</strong>", h)
    h=re.sub(r"<strong>(Status 15 Sep[^<]*|Added r1\.12, closed 16 Sep\.|Forced BROM download failed|No MediaTek device enumerated|Not yet requested|E5 and P2 remain open\.)</strong>", lambda m: badge("ACTION",BLU)+" <strong>"+m.group(1)+"</strong>", h)
    h=h.replace("<strong>4. Four items must start today</strong>", badge("ACTION",BLU)+" <strong>4. Four items must start today</strong>")
    h=h.replace("<strong>Fail</strong>", badge("Fail",RED)).replace("<strong>Fail:</strong>", badge("Fail",RED)+":").replace("<strong>Pass:</strong>", badge("Pass",GRN)+":")
    return h
for md_file,html in [("Cesium_HW_RoT_eFuse_Authorization_Plan.md","report.html"),("Cesium_Cohort_Release_Test_Plan_S1-S6.md","testplan.html")]:
    body = markdown.markdown(open(md_file).read(), extensions=["tables","sane_lists"]).replace("<li>[ ] ",'<li>&#9744; ')
    body = colorize(body)
    open("/tmp/claude-0/-home-user-claude-scratch/ccc0ce66-12b7-5ef7-9ce4-c08f41e58f82/scratchpad/"+html,"w").write(f"<html><head><meta charset='utf-8'><style>{css}</style></head><body>{body}</body></html>")
print("ok")
