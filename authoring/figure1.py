from pathlib import Path
import sys,os
sys.path.insert(0,str(Path('work/figure_runtime').resolve()))
os.environ['MPLCONFIGDIR']=str(Path('work/figure_mpl_cache').resolve())
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,FancyArrowPatch
from matplotlib import font_manager as fm
for n in ['times.ttf','timesbd.ttf','timesi.ttf']:fm.fontManager.addfont('C:/Windows/Fonts/'+n)
plt.rcParams.update({'font.family':'Times New Roman','font.size':20,'pdf.fonttype':42,'svg.fonttype':'none'})
O=Path('outputs/NC_Framework_Revision_v4/figures');O.mkdir(parents=True,exist_ok=True)
A='#326AA1';B='#238A78';T='#BF7448';INK='#253445';GRAY='#596877';PALE='#F2F5F7'
f=plt.figure(figsize=(16,12),facecolor='white');ax=f.add_axes([0,0,1,1]);ax.set(xlim=(0,16),ylim=(0,12));ax.axis('off')
def text(x,y,s,size=20,weight='normal',ha='left',color=INK):return ax.text(x,y,s,fontsize=size,fontweight=weight,ha=ha,va='center',color=color,linespacing=1.35)
def box(x,y,w,h,title,body='',color=GRAY):
 ax.add_patch(Rectangle((x,y),w,h,facecolor='white',edgecolor=color,lw=1.6))
 text(x+w/2,y+h-.32,title,21,'bold','center',color)
 if body:text(x+w/2,y+h/2-.18,body,19,ha='center')
def arrow(x,y,xx,yy,c=GRAY):ax.add_patch(FancyArrowPatch((x,y),(xx,yy),arrowstyle='-|>',mutation_scale=18,lw=1.7,color=c))
def section(y,label,title):
 text(.55,y,label,26,'bold');text(1.02,y,title,25,'bold');ax.plot([.55,15.45],[y-.35,y-.35],color='#CCD6DF',lw=1)
text(.55,11.6,'Paired evaluation of sequential screening',29,'bold')
section(10.85,'a','Define the candidate pool and separate response readouts')
box(.6,8.8,4.1,1.25,'Three perturbation studies','Frangieh  |  Papalexi  |  Tian',A)
box(5.35,8.8,4.6,1.25,'Fixed data processing','RNA counts → programme scores',GRAY)
box(10.6,8.8,4.8,1.25,'15 matched screening tasks','Calibration genes  |  Candidate genes',T)
arrow(4.73,9.43,5.3,9.43);arrow(9.98,9.43,10.55,9.43)
text(.7,8.25,'A: discovery feedback',21,'bold',color=A);text(6.2,8.25,'B: separate archived readout',21,'bold',color=B)
text(15.25,8.25,'Same candidate identities',19,ha='right')
section(7.65,'b','Run policies with matched initial pools and acquisition budgets')
box(.6,5.7,3.6,1.05,'Frozen representation','Geneformer input vectors',A)
text(2.4,5.32,'768 dimensions → 24 PCs',19,ha='center')
box(4.85,5.7,3,1.05,'Select a batch','Unmeasured genes',A)
box(8.55,5.7,3,1.05,'Query readout A','Observed responses',A)
box(12.25,5.7,3.15,1.05,'Update the policy','Continue to budget',A)
arrow(4.22,6.22,4.8,6.22);arrow(7.9,6.22,8.5,6.22);arrow(11.6,6.22,12.2,6.22)
ax.plot([13.82,13.82,6.35],[5.66,5.12,5.12],color=A,lw=1.6);arrow(6.35,5.12,6.35,5.65,A)
text(.7,4.55,'8 policies × 15 tasks × 30 initial pools = 3,600 runs',22,'bold')
text(.7,4.1,'The evaluator scores the same selected genes on B; B does not guide acquisition.',20,color=B)
section(3.45,'c','Separate policy utility from gains introduced by policy selection')
box(.6,1.3,4.45,1.45,'Fixed-policy utility','Compare each policy with random\non both readouts',GRAY)
box(5.75,1.3,4.45,1.45,'Policy-selection contrast','Choose the A winner from 1, 2, 4 or 7\npolicies; retain its selected genes',A)
box(10.9,1.3,4.5,1.45,'Transfer and sensitivity','Score on B; vary selection scope,\nendpoint and policy family',B)
arrow(5.1,2,5.7,2);arrow(10.25,2,10.85,2)
text(.7,.65,'Report the selection rule, paired outcomes, comparison cost and uncertainty unit.',21,'bold')
f.canvas.draw();overflow=[]
for t in ax.texts:
 bb=t.get_window_extent(f.canvas.get_renderer())
 if bb.x0<0 or bb.y0<0 or bb.x1>f.bbox.width or bb.y1>f.bbox.height:overflow.append(t.get_text())
assert not overflow,overflow
for ext in ['svg','pdf','png']:f.savefig(O/('Fig01_Paired_Evaluation_Framework.'+ext),dpi=600 if ext=='png' else 150)
f.savefig(O/'Fig01_preview.jpg',dpi=95)
print('Flat vector framework saved; Times New Roman; minimum font 19 pt at 16 inch canvas')
