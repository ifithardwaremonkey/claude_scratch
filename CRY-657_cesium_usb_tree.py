import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
BLUE, ORANGE, AQUA, INK, INK2, SURF, GRID = '#2a78d6', '#eb6834', '#1baf7a', '#0b0b0b', '#52514e', '#fcfcfb', '#e6e5e0'
fig, ax = plt.subplots(figsize=(13, 7.6), facecolor=SURF); ax.set_facecolor(SURF); ax.set_xlim(0,13); ax.set_ylim(0,7.6); ax.axis('off')
def box(x,y,w,h,title,sub='',hi=False,dash=False):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.04',fc='#fff3ec' if hi else 'white',ec=ORANGE if hi else (INK2 if dash else INK),lw=1.4 if hi else 0.9,ls=(0,(3,2)) if dash else 'solid'))
    ax.text(x+w/2,y+h/2+(0.13 if sub else 0),title,ha='center',va='center',fontsize=9.5,weight='bold' if hi else 'normal',color=INK)
    if sub: ax.text(x+w/2,y+h/2-0.17,sub,ha='center',va='center',fontsize=7.6,color=ORANGE if hi else INK2)
def arrow(x0,y0,x1,y1,c=BLUE,ls='solid'):
    ax.add_patch(FancyArrowPatch((x0,y0),(x1,y1),arrowstyle='-|>',mutation_scale=11,color=c,lw=1.3,ls=ls))
fig.text(0.04,0.95,'Cesium USB tree, from sysfs (2026-10-02) and schematic C.G520.702B rev 0303',fontsize=13,weight='bold',color=INK)
fig.text(0.04,0.915,'Blue = USB data. Orange = power. The brainboard path lands on different hub ports depending on the board.',fontsize=9,color=INK2)
# SoC
ax.add_patch(FancyBboxPatch((0.3,0.6),3.0,6.0,boxstyle='round,pad=0.05',fc='#f3f3f0',ec=GRID,lw=1))
ax.text(1.8,6.3,'MT8371 (Genio 520) USB ports',ha='center',fontsize=9.5,weight='bold',color=INK)
box(0.55,5.1,2.5,0.75,'P0: dual-role (usb0)','Mini-B JU2, ADB/OTG')
box(0.55,4.0,2.5,0.75,'P1: host, direct pair','USB2 pair unpopulated (R312/R313)',dash=True)
box(0.55,2.9,2.5,0.75,'P3: host → VL122 upstream','sysfs bus usb6, root port 1',hi=True)
box(0.55,1.8,2.5,0.75,'other host ports','sysfs usb2, usb3, usb7: empty',dash=True)
# hub
box(4.3,2.75,3.3,1.05,'VL122-Q2 hub at 6-1','on tablet PCB, GPIO reset HUB_RESET_IC',hi=True)
arrow(3.1,3.27,4.25,3.27)
# downstream
box(8.6,5.3,4.0,0.95,'port 4 (6-1.4): USB-C JU1','Stannite (STM32) or Mica (nRF52); HUSB238 PD sink on CC',hi=True)
box(8.6,3.9,4.0,0.95,'port 3 (6-1.3): JST USB CN2','Quartz (nRF52); 5 V switched by USB_HOST1_CTL',hi=True)
box(8.6,2.5,4.0,0.95,'port 2: Type-A JU4','5 V switched by USB_HOST2_CTL')
box(8.6,1.1,4.0,0.95,'port 1: unconnected','',dash=True)
for y in (5.77,4.37,2.97,1.57):
    ax.plot([7.65,8.1],[3.27,3.27],color=BLUE,lw=1.3); ax.plot([8.1,8.1],[1.57,5.77],color=BLUE,lw=1.3); arrow(8.1,y,8.55,y)
# power notes
ax.text(0.3,0.25,'Power: tablet runs from 12 V JST CN1, diode-ORed with USB-C VBUS (Mica PD only). The Type-C port never sources VBUS; JST USB and Type-A do, through TMI6263 switches.',fontsize=8.5,color=ORANGE)
ax.text(0.3,0.0,'Corona Wolf: external dongle hub on USB-C JU1, so dongle + VL122 in series. Android UsbPortManager port0 (Type-C, husb238) is this JU1, not the OTG Mini-B.',fontsize=8.5,color=INK2)
out='/home/user/claude_scratch/CRY-657_cesium_usb_tree.png'; fig.savefig(out,dpi=170,facecolor=SURF); print(out)
