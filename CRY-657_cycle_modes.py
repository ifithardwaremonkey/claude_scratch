import re, datetime as dt
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

BLUE, ORANGE, AQUA = '#2a78d6', '#eb6834', '#1baf7a'
INK, INK2, SURF, GRID = '#0b0b0b', '#52514e', '#fcfcfb', '#e6e5e0'

def load(f, day):
    ev=[]
    for l in open(f, errors='replace'):
        m=re.match(day+r' (\d\d:\d\d:\d\d\.\d{3}) D/UsbHostManager\(\s*\d+\): (USB device attached|Removed device at /dev/bus/usb/001/(\d+)( was already gone)?)', l)
        if m:
            t=dt.datetime.strptime('2026-'+day+' '+m.group(1), '%Y-%m-%d %H:%M:%S.%f')
            ev.append((t, 'ATT' if m.group(2).startswith('USB') else ('GONE' if m.group(4) else 'REM')))
    return ev

def cycles(ev):
    """one row per cycle: (start, kind) kind in FULL (Android saw it) / GONE / HELD"""
    out=[]; i=0
    while i<len(ev):
        t,k=ev[i]
        if k=='ATT' and i+1<len(ev) and ev[i+1][1]=='REM':
            held=(ev[i+1][0]-t).total_seconds()
            out.append((t, 'HELD' if held>5 else 'FULL')); i+=2
        elif k=='ATT': out.append((t,'HELD')); i+=1
        elif k=='GONE': out.append((t,'GONE')); i+=1
        else: i+=1
    return out

def panel(ax, cyc, t0, t1, title, holds):
    xs={'FULL':[], 'GONE':[]}; ys={'FULL':[], 'GONE':[]}
    for (t,k),(tn,_) in zip(cyc, cyc[1:]):
        if k in xs and t0<=t<=t1:
            d=(tn-t).total_seconds()
            if d<=1.45: xs[k].append(t); ys[k].append(d)
    ax.scatter(xs['GONE'], ys['GONE'], s=9, c=BLUE, lw=0, label='Loop mode: enumerated, gone before Android could open it', zorder=3)
    ax.scatter(xs['FULL'], ys['FULL'], s=14, c=ORANGE, lw=0, label='Cluster mode: Android saw the device, dropped 5-20 ms later', zorder=4)
    hx=[t for t,k in cyc if k=='HELD' and t0<=t<=t1]
    ax.scatter(hx, [1.38]*len(hx), marker='v', s=46, c=AQUA, lw=0, label='Enumeration held (link recovered)', zorder=5)
    # shade cluster spans (generator dwell)
    i=0; spans=[]
    full=[t for t,k in cyc if k=='FULL' and t0<=t<=t1]
    while i<len(full):
        j=i
        while j+1<len(full) and (full[j+1]-full[j]).total_seconds()<3: j+=1
        if j-i>=1: spans.append((full[i], full[j]))
        i=j+1
    for a,b in spans:
        ax.axvspan(a-dt.timedelta(seconds=2), b+dt.timedelta(seconds=2), color=ORANGE, alpha=0.10, lw=0, zorder=1)
    # spacing arrows between cluster starts
    starts=[a for a,b in spans if (b-a).total_seconds()>=4]
    for a,b in zip(starts, starts[1:]):
        gap=(b-a).total_seconds()
        if 150<gap<260:
            y=0.30
            ax.annotate('', xy=(b,y), xytext=(a,y), arrowprops=dict(arrowstyle='<->', color=INK2, lw=0.8))
            ax.text(a+(b-a)/2, y+0.03, f'{gap:.0f} s', ha='center', va='bottom', fontsize=7.5, color=INK2)
    for (t,txt) in holds:
        ax.annotate(txt, xy=(t,1.38), xytext=(0,-14), textcoords='offset points', ha='center', va='top', fontsize=7.5, color=INK2)
    ax.axhline(1.0025, color=BLUE, lw=0.6, ls=':', zorder=2); ax.axhline(0.600, color=ORANGE, lw=0.6, ls=':', zorder=2)
    ax.text(t1, 1.0025, ' 1.0025 s', va='center', ha='left', fontsize=8, color=INK, clip_on=False)
    ax.text(t1, 0.600, ' 0.600 s', va='center', ha='left', fontsize=8, color=INK, clip_on=False)
    ax.set_xlim(t0,t1); ax.set_ylim(0.2,1.5)
    ax.set_yticks([0.4,0.6,0.8,1.0,1.2,1.4]); ax.set_ylabel('seconds to next cycle', fontsize=8.5, color=INK2)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M')); ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=5))
    ax.tick_params(labelsize=8, colors=INK2, length=0); ax.grid(axis='y', color=GRID, lw=0.6); ax.set_axisbelow(True)
    for s in ax.spines.values(): s.set_visible(False)
    ax.set_facecolor(SURF); ax.set_title(title, loc='left', fontsize=10, color=INK, pad=6)

c11=cycles(load('cvte0511/logcat.log','05-11'))
c06=cycles(load('logcat.log.txt','05-06'))

fig=plt.figure(figsize=(12.5,10.2), facecolor=SURF)
gs=fig.add_gridspec(3,1, height_ratios=[1,1,0.62], hspace=0.55, left=0.07, right=0.90, top=0.90, bottom=0.07)
ax1=fig.add_subplot(gs[0]); ax2=fig.add_subplot(gs[1]); ax3=fig.add_subplot(gs[2])
D=lambda s: dt.datetime.strptime('2026-'+s,'%Y-%m-%d %H:%M:%S')
panel(ax1, c11, D('05-11 10:40:00'), D('05-11 11:27:00'), '05-11 run, glassos 8.47.4.1896, 1.0 / 1.4 kV (attachment 242591 logcat)',
      [(D('05-11 11:00:11'),'held 136 s\nuntil test 2'),(D('05-11 11:25:20'),'recovered')])
panel(ax2, c06, D('05-06 11:32:30'), D('05-06 11:59:30'), '05-06 run, glassos 8.37.2 (attachment 242132 logcat; coverage ends 11:59)',
      [(D('05-06 11:33:18'),'held 303 s'),(D('05-06 11:38:47'),'held 60 s')])

# zoom: event strip around the 10:45:51 cluster->loop transition
z0,z1=D('05-11 10:45:44'), D('05-11 10:46:04')
ev=load('cvte0511/logcat.log','05-11')
for t,k in ev:
    if z0<=t<=z1:
        if k=='ATT': ax3.vlines(t,0.55,1.0,color=ORANGE,lw=1.6)
        elif k=='REM': ax3.vlines(t,0.55,0.78,color=ORANGE,lw=0.9,alpha=0.6)
        else: ax3.vlines(t,0.0,0.45,color=BLUE,lw=1.6)
ax3.text(z0+dt.timedelta(seconds=0.3),1.03,'Cluster mode: attach (tall) and removal 5-20 ms later (short), every 0.600 s', fontsize=8, color=INK, va='bottom')
ax3.text(z0+dt.timedelta(seconds=0.3),-0.07,'Loop mode: "Removed device … was already gone", every 1.0025 s', fontsize=8, color=INK, va='top')
ax3.set_xlim(z0,z1); ax3.set_ylim(-0.3,1.25); ax3.set_yticks([])
ax3.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S')); ax3.xaxis.set_major_locator(mdates.SecondLocator(interval=2))
ax3.tick_params(labelsize=8, colors=INK2, length=0)
for s in ax3.spines.values(): s.set_visible(False)
ax3.set_facecolor(SURF)
ax3.set_title('Zoom, 05-11 10:45:44 to 10:46:04: the cadence changes the moment the generator dwell ends', loc='left', fontsize=10, color=INK, pad=6)

h,l=ax1.get_legend_handles_labels()
h.append(Patch(facecolor=ORANGE, alpha=0.18, lw=0)); l.append('Generator dwell (cluster span)')
fig.legend(h,l,loc='upper left', bbox_to_anchor=(0.07,0.975), ncol=2, fontsize=8.5, frameon=False, handletextpad=0.5, columnspacing=1.6)
fig.suptitle('Stannite USB link under EFT: two fixed cycle periods, locked to the burst generator', x=0.07, y=0.995, ha='left', fontsize=13, color=INK, weight='bold')
fig.text(0.07,0.012,'Each dot is one kernel enumeration of the Stannite (213c:0006), plotted at the time it happened and the delay to the next one. Source: UsbHostManager lines in the CVTE logcat bundles. Device time (UTC-4).', fontsize=8, color=INK2)
out='/home/user/claude_scratch/CRY-657_cycle_modes.png'
fig.savefig(out, dpi=170, facecolor=SURF); print(out)
