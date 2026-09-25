from pathlib import Path
import sys,os
sys.path.insert(0,str(Path('work/figure_runtime').resolve()))
os.environ['MPLCONFIGDIR']=str(Path('work/figure_mpl_cache').resolve())
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,FancyBboxPatch,FancyArrowPatch,Circle
from matplotlib import font_manager as fm
for n in ['times.ttf','timesbd.ttf','timesi.ttf']:fm.fontManager.addfont('C:/Windows/Fonts/'+n)
plt.rcParams.update({'font.family':'Times New Roman','font.size':20,'svg.fonttype':'none','pdf.fonttype':42})
O=Path('outputs/Fig1_Refined_v5');O.mkdir(exist_ok=True)
A='#326AA1';B='#238A78';T='#BF7448';INK='#253445';GRAY='#677583';LINE='#D9E1E7';PALE='#F4F7F9'
f=plt.figure(figsize=(17,12));ax=f.add_axes([0,0,1,1]);ax.set(xlim=(0,17),ylim=(0,12));ax.axis('off')
def txt(x,y,s,size=20,bold=False,color=INK,ha='left'):
 return ax.text(x,y,s,fontsize=size,fontweight='bold' if bold else 'normal',color=color,ha=ha,va='center',linespacing=1.3)
def arr(x,y,xx,yy,color=GRAY,rad=0):
 ax.add_patch(FancyArrowPatch((x,y),(xx,yy),arrowstyle='-|>',mutation_scale=18,lw=1.7,color=color,connectionstyle=f'arc3,rad={rad}'))
def pill(x,y,w,h,s,color,fs=18):
 ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.02,rounding_size=0.08',facecolor='white',edgecolor=color,lw=1.3));txt(x+w/2,y+h/2,s,fs,True,color,'center')
def grid(x,y,rows,cols,cell=.18,color=A,pattern=False):
 for i in range(rows):
  for j in range(cols):
   alpha=[.18,.38,.65,.9][(i*3+j*2)%4] if pattern else .65
   ax.add_patch(Rectangle((x+j*cell,y+i*cell),cell*.82,cell*.82,facecolor=color,alpha=alpha,edgecolor='none'))
def band(y,label,title):
 ax.add_patch(Circle((.65,y),.22,facecolor=INK,edgecolor='none'));txt(.65,y,label,22,True,'white','center');txt(1.08,y,title,25,True)
 ax.plot([.43,16.55],[y-.38,y-.38],color=LINE,lw=1)
text=txt(.48,11.65,'Paired evaluation of sequential screening',29,True)
band(10.95,'a','Align interventions across separate response readouts')
# Three archived studies with subtle source markers.
for i,(s,c) in enumerate([('Frangieh',A),('Papalexi',B),('Tian',T)]):
 y=9.88-i*.47;ax.add_patch(Rectangle((.62,y-.15),.08,.3,facecolor=c,edgecolor='none'));txt(.9,y,s,21,True,c)
txt(.62,8.33,'Three public studies',18,color=GRAY)
arr(3.2,9.39,3.82,9.39)
grid(4.05,8.93,5,7,.17,A,True);txt(4.6,10.18,'RNA counts',20,True,ha='center');txt(4.6,8.56,'Fixed processing',18,color=GRAY,ha='center')
arr(5.47,9.39,6.1,9.39)
# Paired strips are identical identities, independent response colors.
txt(6.4,10.18,'Paired response scores',20,True)
for y,c,lab in [(9.57,A,'A  Discovery'),(8.99,B,'B  Replication')]:
 txt(6.4,y+.13,lab,19,True,c);grid(8.65,y,1,8,.2,c,True)
txt(6.4,8.33,'Same gene identities on A and B',18,color=GRAY)
arr(10.52,9.39,11.03,9.39)
txt(11.35,10.18,'Fixed gene partition',20,True)
grid(11.4,8.99,3,3,.21,T);grid(13.25,8.99,3,7,.21,A)
txt(11.65,8.62,'Calibration',18,ha='center',color=T);txt(13.9,8.62,'Candidates',18,ha='center',color=A)
pill(15.14,8.96,1.25,.91,'15\ntasks',INK,19)
band(7.76,'b','Acquire on A and evaluate the same selected genes on B')
# Representation module.
grid(.68,5.8,5,6,.17,A,True);txt(.68,7.03,'Frozen features',21,True);txt(.68,5.35,'Geneformer input vectors',16);txt(.68,4.98,'768 → 24 PCs',19,color=A)
arr(2.06,6.25,3.35,6.25)
# Distinct operations connected along one horizontal path.
for x,title,subtitle,c in [(3.65,'Select','Unmeasured batch',A),(6.9,'Query A','Observed responses',A),(10.15,'Update','Next decision',A)]:
 txt(x,7.03,title,22,True,c);txt(x,5.72,subtitle,18,color=GRAY)
 if title=='Select':
  for j in range(4):ax.add_patch(Rectangle((x+j*.33,6.17),.23,.23,facecolor=A if j<2 else 'white',edgecolor=A,lw=1.2))
 elif title=='Query A':
  for j,h in enumerate([.17,.43,.29,.55]):ax.add_patch(Rectangle((x+j*.3,6.1),.17,h,facecolor=A,alpha=.35+j*.17,edgecolor='none'))
 else:
  for j in range(3):
   ax.plot([x,x+1.1],[6.2+j*.22]*2,color=LINE,lw=2);ax.add_patch(Circle((x+[.3,.75,.52][j],6.2+j*.22),.065,facecolor=A,edgecolor='none'))
arr(5.17,6.37,6.57,6.37,A);arr(8.45,6.37,9.82,6.37,A)
# Explicit feedback loop under the steps.
ax.plot([10.83,10.83,3.25,3.25],[5.37,4.87,4.87,6.02],color=A,lw=1.5);arr(3.25,6.02,3.59,6.18,A)
txt(7.54,4.62,'Repeat until budget is exhausted',18,color=A,ha='center')
# Terminal selected set has a one-way branch to the evaluator.
arr(11.55,6.37,12.68,6.37,GRAY)
ax.add_patch(FancyBboxPatch((13.03,5.1),3.25,2.12,boxstyle='round,pad=0.03,rounding_size=0.1',fc='#EEF6F3',ec='#C8DDD5',lw=1))
txt(14.65,6.84,'Evaluate on B',21,True,B,'center');grid(13.45,6.18,1,7,.25,B)
txt(14.65,5.7,'Same selected genes',19,ha='center');txt(14.65,5.32,'No feedback to acquisition',17,ha='center',color=B)
txt(.68,4.19,'8 policies × 15 tasks × 30 matched initial pools = 3,600 runs',21,True)
band(3.51,'c','Distinguish policy utility from retrospective selection gains')
# Three balanced analytical questions, restrained tinted backgrounds.
for x,w,c in [(.62,4.7,GRAY),(5.8,5.25,A),(11.53,4.75,B)]:
 ax.add_patch(FancyBboxPatch((x,.92),w,1.98,boxstyle='round,pad=.03,rounding_size=.1',fc=PALE,ec='none'));ax.plot([x+.13,x+w-.13],[2.83,2.83],color=c,lw=2)
txt(.87,2.49,'Fixed-policy utility',22,True)
pill(.92,1.73,1.32,.4,'Policy',GRAY,17);arr(2.35,1.93,2.82,1.93);pill(2.94,1.73,.62,.4,'A',A,17);pill(3.77,1.73,.62,.4,'B',B,17)
txt(.87,1.29,'Compare with matched random',18,color=GRAY)
txt(6.05,2.49,'Policy-selection contrast',22,True,A)
for j,n in enumerate(['1','2','4','7']):pill(6.11+j*.7,1.72,.48,.42,n,A,18)
arr(8.95,1.94,9.38,1.94,A);pill(9.5,1.64,1.2,.58,'A winner',A,17)
txt(6.05,1.29,'Vary the number of available policies',18,color=GRAY)
txt(11.78,2.49,'Transfer and sensitivity',22,True,B)
for j,s in enumerate(['Scope','Endpoint','Policy set']):pill(11.81+j*1.43,1.72,1.3,.43,s,B,16)
txt(11.78,1.29,'Measure which gains persist on B',18,color=GRAY)
txt(.67,.47,'Report the selection rule, paired outcomes, comparison cost and uncertainty unit.',20,True)
txt(16.3,.47,'Schematic',16,color=GRAY,ha='right')
f.canvas.draw();assert all(t.get_window_extent(f.canvas.get_renderer()).x1<=f.bbox.width for t in ax.texts)
for ext in ['png','svg','pdf']:f.savefig(O/('Fig01_Refined_Framework.'+ext),dpi=600)
f.savefig(O/'Fig01_preview.jpg',dpi=95)
print('Figure saved')

