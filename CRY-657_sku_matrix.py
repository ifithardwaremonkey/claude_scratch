import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
BLUE, ORANGE, AQUA, INK, INK2, SURF, GRID = '#2a78d6', '#eb6834', '#1baf7a', '#0b0b0b', '#52514e', '#fcfcfb', '#e6e5e0'
RED='#e34948'

rows = [
 ('Stannite\n(USB audio + FitPro2)',
  dict(pw='no PD on Stannite (BOM)\ntablet: 12 V JST CN1', data='USB-C JU1 → VL122 hub port 4\n(6-1.4)', path='sch 702B-0303: D+/D- via choke LU2, no mux; HUSB238 PD sink on CC', state='ok'),
  dict(pw='no PD on Stannite (BOM)\ntablet: 12 V JST 4-pin', data='USB-C → xhci1 root port 1\n(usb 1-1)', path='direct, no hub, FS; tablet PD/CC logic outside kernel', state='ok')),
 ('Quartz\n(FitPro2 only,\nX30 audio over SPI)',
  dict(pw='JST power (CN1 12 V)\n5 V on JST USB switched', data='JST USB CN2 → VL122 hub\nport 3 (6-1.3)', path='sch: 5V_USB2.0_A via TMI6263 switch, GPIO USB_HOST1_CTL', state='ok'),
  dict(pw='JST power', data='JST USB → "USB-2 JST" port', path='PHY Vterm tuned 2024 (BRAIN-402)', state='ok')),
 ('Corona Wolf\n(via external dongle hub)',
  dict(pw='hub: JST power, no PD\ntablet: 12 V JST CN1', data='USB-C → dongle hub → JST USB', path='two hubs in series: dongle + VL122 (USB-C is hub port 4)', state='ok'),
  dict(pw='hub: JST power, no PD\ntablet: 12 V JST 4-pin', data='USB-C → dongle hub → JST USB', path='dongle hub on the root port', state='unk')),
 ('Mica\n(Ultra3 on Xenon\n= same tablet)',
  dict(pw='PD source → tablet sink', data='USB-C JU1 → VL122 hub port 4\n(6-1.4)', path='sch: VBUS_TYPEC0 → D2 → DC_12V, diode-OR with JST', state='ok'),
  dict(pw='PD source → tablet sink', data='USB-C → xhci1 root port 1\n(same receptacle as Stannite)', path='USB-C chosen over JST for EMI margin; no Xenon schematic (CVTE IP)', state='unk')),
]
cols = ['Cesium\nMT8371 / Genio 520, Android 15, kernel 6.1\non-board VL122 hub, upstream on SoC port P3',
        'Xenon\nMT8390 / Genio 700, Android 13, kernel 5.15\nno hub on the USB-C path']

fig, ax = plt.subplots(figsize=(14, 9.6), facecolor=SURF); ax.set_facecolor(SURF)
ax.set_xlim(0, 14); ax.set_ylim(0, 9.6); ax.axis('off')
fig.text(0.04, 0.955, 'Tablet × brainboard combinations, and what each one means for USB recovery', fontsize=14, weight='bold', color=INK)
fig.text(0.04, 0.925, 'Orange = power direction. Blue = USB data path and where it lands in the tablet. Grey dashed = not confirmed by any log or schematic read in this analysis.', fontsize=9, color=INK2)

x0 = 3.0; cw = 5.35; rh = 1.95; ytop = 8.15
for ci, c in enumerate(cols):
    ax.text(x0 + ci*cw + cw/2, ytop + 0.42, c.split('\n')[0], ha='center', va='bottom', fontsize=11, weight='bold', color=INK)
    ax.text(x0 + ci*cw + cw/2, ytop + 0.40, '\n'+'\n'.join(c.split('\n')[1:]), ha='center', va='top', fontsize=8, color=INK2)
for ri, (name, ces, xen) in enumerate(rows):
    y = ytop - ri*rh - rh
    ax.text(0.25, y + rh/2, name, ha='left', va='center', fontsize=9, weight='bold', color=INK)
    if ri: ax.plot([0.2, 13.8], [y + rh, y + rh], color=GRID, lw=0.8)
    for ci, cell in enumerate((ces, xen)):
        x = x0 + ci*cw
        unk = cell['state'] == 'unk'
        ec = INK2 if unk else INK
        ls = (0, (3, 2)) if unk else 'solid'
        # boxes
        bb = FancyBboxPatch((x+0.2, y+0.95), 1.0, 0.55, boxstyle='round,pad=0.03', fc='white', ec=ec, lw=0.9, ls=ls); ax.add_patch(bb)
        ax.text(x+0.7, y+1.225, 'brainboard', ha='center', va='center', fontsize=8, color=INK)
        tb = FancyBboxPatch((x+cw-1.35, y+0.95), 1.0, 0.55, boxstyle='round,pad=0.03', fc='white', ec=ec, lw=0.9, ls=ls); ax.add_patch(tb)
        ax.text(x+cw-0.85, y+1.225, 'tablet', ha='center', va='center', fontsize=8, color=INK)
        # power arrow (above) and data arrow (below)
        xa, xb = x+1.3, x+cw-1.45
        if cell['pw'].startswith('PD source'):
            ax.add_patch(FancyArrowPatch((xa, y+1.4), (xb, y+1.4), arrowstyle='-|>', mutation_scale=10, color=ORANGE, lw=1.6))
        else:
            ax.add_patch(FancyArrowPatch((xa, y+1.4), (xb, y+1.4), arrowstyle='-', color=ORANGE, lw=1.6, ls=(0,(2,2))))
        ax.add_patch(FancyArrowPatch((xb, y+1.05), (xa, y+1.05), arrowstyle='<|-|>', mutation_scale=10, color=BLUE, lw=1.6, ls=ls))
        ax.text((xa+xb)/2, y+1.47, cell['pw'], ha='center', va='bottom', fontsize=7.6, color=ORANGE if not unk else INK2)
        ax.text((xa+xb)/2, y+0.98, cell['data'], ha='center', va='top', fontsize=7.6, color=BLUE if not unk else INK2)
        ax.text(x+0.2, y+0.42, cell['path'], ha='left', va='top', fontsize=7.6, color=INK2, style='italic')
        if unk:
            ax.text(x+cw-0.3, y+0.42, '?', ha='right', va='top', fontsize=12, weight='bold', color=INK2)
ax.plot([x0-0.1, x0-0.1], [0.55, ytop+0.05], color=GRID, lw=0.8)
ax.plot([x0+cw-0.05, x0+cw-0.05], [0.55, ytop+0.05], color=GRID, lw=0.8)
fig.text(0.04, 0.02, 'Confirmed: Xenon+Stannite (05-06/05-11 bugreports); all Cesium cells from schematic C.G520.702B rev 0303 (old; production may differ) plus the 09-11 bugreport and sysfs. \nXenon cells from Allen\'s 2026-10-03 notes; iFIT has no rights to the Xenon schematic, so they stay dashed.\nNot shown: the separate OTG/ADB dual-role port on each tablet, and USB audio boards (Zylux/Bowie on Athena) that share a bus on some SKUs.', fontsize=8, color=INK2)
out='/home/user/claude_scratch/CRY-657_sku_matrix.png'; fig.savefig(out, dpi=170, facecolor=SURF); print(out)
