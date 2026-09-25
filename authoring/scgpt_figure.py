from pathlib import Path
import sys,os,json
sys.path.insert(0,str(Path('work/figure_runtime').resolve()))
os.environ['MPLCONFIGDIR']=str(Path('work/figure_mpl_cache').resolve())
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
import pandas as pd
for n in ['times.ttf','timesbd.ttf']:fm.fontManager.addfont('C:/Windows/Fonts/'+n)
plt.rcParams.update({'font.family':'Times New Roman','font.size':19,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'svg.fonttype':'none'})
O=Path('outputs/NC_Framework_Revision_v4');df=pd.read_csv(O/'scGPT_extension/summary.csv');v=json.loads((O/'scGPT_extension/verification.json').read_text())
f,axs=plt.subplots(1,3,figsize=(18,7.7));f.subplots_adjust(left=.19,right=.97,bottom=.22,top=.72,wspace=.55)
f.text(.04,.95,'A controlled scGPT representation example',fontsize=28,weight='bold',color='#253445')
f.text(.04,.885,'Updating ridge with matched tasks, acquisition budgets and initial pools',fontsize=20,color='#596877')
for ax,study,lab in zip(axs[:2],['Frangieh','Papalexi'],'ab'):
 z=df[df.study==study];rows=[('geneformer_updating','a'),('geneformer_updating','b'),('scgpt_updating','a'),('scgpt_updating','b')]
 for i,(policy,metric) in enumerate(rows):
  r=z[(z.policy==policy)&(z.metric==metric)].iloc[0];c='#326AA1' if metric=='a' else '#238A78'
  ax.errorbar(r.mean_pp,3-i,xerr=[[r.mean_pp-r.low_pp],[r.high_pp-r.mean_pp]],fmt='o' if metric=='a' else 's',color=c,capsize=3,ms=7)
 ax.axvline(0,color='#8996A0',lw=1);ax.set(xlim=(-5,12),ylim=(-.5,3.5),yticks=[3,2,1,0],yticklabels=['Geneformer A','Geneformer B','scGPT A','scGPT B']);ax.set_title(study,fontsize=23,pad=15);ax.set_xlabel('Uplift over random (pp)',fontsize=19);ax.text(-.2,1.17,lab,transform=ax.transAxes,weight='bold',fontsize=25)
ax=axs[2]
for i,study in enumerate(['Frangieh','Papalexi']):
 r=df[(df.study==study)&(df.policy=='scgpt_minus_geneformer')].iloc[0];ax.errorbar(r.mean_pp,1-i,xerr=[[r.mean_pp-r.low_pp],[r.high_pp-r.mean_pp]],fmt='o',color='#253445',capsize=3,ms=7)
ax.axvline(0,color='#8996A0',lw=1);ax.set(xlim=(-5,5),ylim=(-.6,1.6),yticks=[1,0],yticklabels=['Frangieh','Papalexi']);ax.set_title('Representation contrast',fontsize=23,pad=15);ax.set_xlabel('scGPT − Geneformer on B (pp)',fontsize=18);ax.text(-.2,1.17,'c',transform=ax.transAxes,weight='bold',fontsize=25)
f.text(.04,.085,'Static gene-token representations; 30 matched initial pools. Intervals describe conditional algorithmic variability.',fontsize=18,color='#596877')
for ext in ['png','pdf','svg']:f.savefig(O/'figures'/('FigS04_scGPT_Representation.'+ext),dpi=600)
f.savefig(O/'figures/FigS04_preview.jpg',dpi=90)
ex={'main_results':'''### A controlled scGPT representation example extends the paired comparison

We replaced the candidate feature map in updating ridge with static gene-token representations from the scGPT whole-human checkpoint [14], retaining the original tasks, initial-pool seeds, budgets and response thresholds wherever vocabulary coverage was complete (Supplementary Fig. 4). This supplementary analysis added 360 scGPT policy runs across nine Frangieh and three Papalexi tasks. In Frangieh, replication uplift over random was 0.58 percentage points (95% conditional interval, −0.33 to 1.54), compared with −0.97 for the original Geneformer representation. The direct paired difference was 1.55 points (1.00–2.11). In Papalexi, scGPT and Geneformer replication uplifts were 1.85 and 1.67 points; their paired difference was 0.19 points (−3.15 to 3.52). The example shows that representation choice can change fixed-policy utility while leaving the paired evaluation procedure applicable. It does not establish superiority over random in both studies or evaluate the full contextual scGPT transformer.''',
'main_methods':'''### Supplementary scGPT representation comparison

We used the scGPT whole-human checkpoint from wanglab/scGPT-human, revision a24c237737a40f3720f75abb555489e9fe753be6 [14]. Its 512-dimensional input gene embeddings were passed through the checkpoint's encoder layer normalization. A standard scaler and whitened 24-component PCA were fitted on a deterministic vocabulary subset excluding all original screening-candidate symbols; no response labels were used. Updating ridge retained its penalty of 10, acquisition rule and the original seeds and budgets. All original candidate symbols were covered in Frangieh and Papalexi. Tian was omitted from this extension because GARS and YARS did not match the checkpoint vocabulary directly; no alias substitution or candidate-pool reduction was introduced. The complete protocol, projection and candidate-coverage record accompany the source data. Supplementary Methods 6 provides checkpoint hashes, preprocessing and numerical verification.''',
'si_methods':'''### Supplementary Methods 6 scGPT fixed-policy representation experiment

The scGPT whole-human checkpoint was downloaded from the model publisher's repository, https://huggingface.co/wanglab/scGPT-human, at revision a24c237737a40f3720f75abb555489e9fe753be6. The SHA256 digest of best_model.pt is 6cb5d451ab5c4b33eb673adbe4fddc61d2389df1b89b7651a9fe2e557572b922. The experiment used encoder.embedding.weight (60,697 tokens × 512 features), followed by encoder.enc_norm with the stored weight and bias and epsilon 10⁻⁵. No contextual transformer inference or fine-tuning was performed.

Projection fitting used %d vocabulary symbols after excluding every archived decision-candidate symbol and special tokens starting with '<', then retaining symbols whose SHA256 first eight hexadecimal digits modulo five equalled zero. StandardScaler was followed by PCA with 24 whitened components, randomized SVD, iterated_power=2 and random_state=20260923. This model-specific feature preprocessing differs from the original Geneformer projection; the comparison concerns the resulting representation pipelines, not an isolated causal effect of pretraining. The projection arrays and development symbols are supplied.

Eligibility was determined by complete direct symbol coverage before running the new policy. All nine Frangieh tasks and all three Papalexi tasks were retained with their original candidate sets, thresholds and budgets. Each Tian task had 141 of 143 directly matched symbols, with GARS and YARS unmatched; these three tasks were not run in this extension. The original Tian results remain in the main benchmark. No aliases were guessed and no response-based candidate filtering was used.

For each retained task and each of the original 30 initial-pool seeds, we ran scGPT updating ridge, original Geneformer updating ridge and paired random sampling. The 1,080 runs comprised 360 new scGPT trajectories and 720 comparator replays. Comparator endpoints reproduced the archived values to a maximum absolute difference below 10⁻¹². Every trajectory preserved the original initialization and selected unique candidates to the exact budget. The protocol was recorded before the extension runs; it is a supplementary analysis developed after the main study results were known.

We subtracted matched random hit rates within task and seed, then averaged related tasks within each study. For each reported uplift and the direct scGPT-minus-Geneformer contrast on B, pointwise percentile intervals used 10,000 resamples of the 30 seed-level means with bootstrap seed 20260923. No confirmatory p values or policy-selection claims were derived from this example. The complete A and B results, trajectories, coverage records and checks are supplied in scGPT_extension/.''' % v['development_tokens'],
'caption':'''Supplementary Fig. 4. A controlled scGPT representation example. (a,b) Updating-ridge hit-rate uplift over matched random sampling using the original Geneformer feature map or the scGPT static gene-token representation pipeline, on discovery A (blue circles) and replication B (green squares). All nine Frangieh and three Papalexi tasks are retained. (c) Direct paired difference between the two representation pipelines on B: 1.55 [1.00, 2.11] percentage points in Frangieh and 0.19 [−3.15, 3.52] in Papalexi. Points average tasks within study and then 30 matched initial pools; bars are pointwise percentile intervals from 10,000 seed resamples. The intervals describe algorithmic variability conditional on the archive. Tian is excluded only from this extension owing to two unmatched gene symbols; its original benchmark results remain unchanged. This comparison uses static gene features, not full contextual transformer inference.'''}
Path('work/nc_framework_v4/experiment_content.json').write_text(json.dumps(ex,indent=2),encoding='utf-8')
print(v)
