from pathlib import Path
from docx import Document
from docx.shared import Pt,Cm
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH
import re,json,copy,shutil
from prose import *
O=Path('outputs/NC_Framework_Revision_v4');S=Path('outputs/NC_Second_Edition_Six_Figures')
d=Document(S/'Main_Manuscript_Second_Edition.docx');si=Document(S/'Supplementary_Information_Second_Edition.docx')
def fill(p,text,size=11):
 p.clear()
 for part in re.split(r'(\[\d[\d,–-]*\])',text):
  r=p.add_run(part.strip('[]') if re.fullmatch(r'\[\d[\d,–-]*\]',part) else part)
  r.font.name='Times New Roman';r.font.size=Pt(size)
  if part.startswith('[') and re.fullmatch(r'\[\d[\d,–-]*\]',part):r.font.superscript=True
 return p
def add(doc,text,head=False,page=False):
 p=doc.add_paragraph(style='Heading 2' if head else 'Normal');fill(p,text,11)
 if head:
  for r in p.runs:r.bold=True
  p.paragraph_format.keep_with_next=True
 if page:p.paragraph_format.page_break_before=True
 return p
def insert(doc,anchor,text):
 for block in text.strip().split('\n\n'):
  h=block.startswith('### ');p=add(doc,block[4:] if h else block,h);anchor.addprevious(p._p)
def get(doc,title):return next(p for p in doc.paragraphs if p.text==title)
oldtitle=d.paragraphs[0].text;fill(d.paragraphs[0],TITLE,18)
for r in d.paragraphs[0].runs:r.bold=True
p=d.paragraphs[3] if d.paragraphs[2].text=='Abstract' else None
idx=next(i for i,p in enumerate(d.paragraphs) if p.text=='Abstract');fill(d.paragraphs[idx+1],ABSTRACT)
results=get(d,'Results')._p
intro_end=next(p for p in d.paragraphs if p.text.startswith('Here we use paired retrospective'))
insert(d,intro_end._p,INTRO_ADDITIONS);fill(intro_end,INTRO_END)
# Insert operational framework before the original replay results.
i=d.paragraphs.index(get(d,'Results')) if False else next(i for i,p in enumerate(d.paragraphs) if p.text=='Results')
insert(d,d.paragraphs[i+1]._p,FRAMEWORK_RESULTS)
# Add interpretation at the end of each result subsection, before the next heading.
for heading,body in RESULTS_EXTRA.items():
 ps=d.paragraphs;i=next(i for i,p in enumerate(ps) if p.text==heading)
 anchor=next(p._p for p in ps[i+1:] if p.style.name.startswith('Heading'))
 insert(d,anchor,body)
# Replace discussion as a connected academic argument, preserving all required citations.
ps=d.paragraphs;i=next(i for i,p in enumerate(ps) if p.text=='Discussion');j=next(i for i,p in enumerate(ps) if p.text=='Methods')
for p in ps[i+1:j]:p._p.getparent().remove(p._p)
insert(d,get(d,'Methods')._p,DISCUSSION)
insert(d,get(d,'Data availability')._p,METHODS_ADD)
# Update title in supporting information.
for p in si.paragraphs:
 if p.text==oldtitle:fill(p,TITLE,11)
# Redraw Fig. 1 from explicit vector primitives, preserving the scientific caption.
shape=d.inline_shapes[0];oldrid=shape._inline.xpath('.//a:blip')[0].get(qn('r:embed'));shape._inline.getparent().remove(shape._inline)
ps=d.paragraphs;i=next(i for i,p in enumerate(ps) if p.text.startswith('Fig. 1 Retrospective'))
fill(ps[i],'Fig. 1 A paired evaluation framework for sequential perturbation screening',12)
for r in ps[i].runs:r.bold=True
p=ps[i+1];p.clear();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.add_run().add_picture(str(O/'figures/Fig01_Paired_Evaluation_Framework.png'),width=Cm(17.5))
if oldrid not in [x.get(qn('r:embed')) for x in d._element.xpath('.//a:blip')]:d.part.drop_rel(oldrid)
fill(ps[i+2],'''Fig. 1. (a) RNA counts from three public perturbation studies are converted into programme-response scores under fixed processing rules. Threshold-calibration genes are separated from decision candidates. Discovery A and replication B retain the same candidate identities. (b) Static Geneformer input vectors are projected to 24 principal components. Eight numerical policies select batches using only queried A responses, with matched initial pools and acquisition budgets. B responses are reserved for evaluation of the selected genes. (c) Fixed-policy utility, gains from retrospective policy selection and transfer across readouts are evaluated separately. The diagram specifies the information available at each step. Separate archived guide or sample readouts do not constitute independent-donor replication.''',10.5)
# Include reporting and representation protocol in SI, without adding unperformed results.
text='### '+SI_METHODS
insert(si,get(si,'Supplementary Fig. 1')._p,text)
add(si,'Supplementary Table 9',True,True)
add(si,'Reporting specification for paired evaluation of sequential screening.',True)
rows=[('Data and partitions','Identify studies, candidate identities, A/B partition rules and the biological unit represented by each readout.'),('Representation','Record model checkpoint, feature extraction, vocabulary coverage, projection fit set and information available before acquisition.'),('Acquisition','Specify policy updates, queried feedback, initial pool, batch size, stopping rule and per-trajectory budget.'),('Policy selection','List all available policies and define the endpoint, tie handling and whether selection is per run, per task or held out.'),('Paired outcomes','Score the same selected interventions on both readouts. Report fixed-policy utility separately from the multiplicity contrast.'),('Comparison cost','Report the cost of obtaining the outcomes used to choose a winner, including shared measurements and computation.'),('Uncertainty','State the resampling unit, task aggregation, biological replication, multiplicity adjustment and interval construction.'),('Chronology','Distinguish prespecified comparisons from analyses introduced after inspection. Retain the evaluated policy set and trajectories.')]
t=si.add_table(rows=1,cols=2);t.style='Table Grid';t.cell(0,0).text='Component';t.cell(0,1).text='Required information'
for a,b in rows:
 cells=t.add_row().cells;cells[0].text=a;cells[1].text=b
for row in t.rows:
 for cell in row.cells:
  for p in cell.paragraphs:
   for r in p.runs:r.font.name='Times New Roman';r.font.size=Pt(10.5)
for cell in t.rows[0].cells:
 for r in cell.paragraphs[0].runs:r.bold=True
 tcPr=cell._tc.get_or_add_tcPr();shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'E8EDF1');tcPr.append(shade)
add(si,'The specification records an evaluation design; it is not a numerical validation criterion or a claim of community consensus.',False)
# Supplementary counts include the reporting table; methods expanded to 5 pending experiment section.
for doc in [d,si]:
 for p in doc.paragraphs:
  for r in p.runs:
   z=r.text.replace('eight supporting tables','nine supporting tables').replace('Supplementary Methods 1–4','Supplementary Methods 1–5')
   if z!=r.text:r.text=z
# Add a controlled model example only after its numerical evidence is available.
exp=Path('work/nc_framework_v4/experiment_content.json')
if exp.exists():
 ex=json.loads(exp.read_text());insert(d,get(d,'Discussion')._p,ex['main_results']);insert(d,get(d,'Data availability')._p,ex['main_methods'])
 insert(si,get(si,'Supplementary Fig. 1')._p,ex['si_methods'])
 add(si,'Supplementary Fig. 4',True,True);p=si.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.add_run().add_picture(str(O/'figures/FigS04_scGPT_Representation.png'),width=Cm(17.5));p.paragraph_format.keep_with_next=True
 fill(si.add_paragraph(),ex['caption'],10.5)
 for doc in [d,si]:
  for p in doc.paragraphs:
   for r in p.runs:
    z=r.text.replace('Three supporting figures','Four supporting figures').replace('Supplementary Methods 1–5','Supplementary Methods 1–6')
    if z!=r.text:r.text=z
for doc,name in [(d,'Main_Manuscript.docx'),(si,'Supplementary_Information.docx')]:doc.save(O/name)
# Match the cover letter to the final framework framing.
c=Document('outputs/manuscript_author_v3/Nature_Communications/Cover_Letter.docx')
for p in c.paragraphs:
 if oldtitle in p.text:fill(p,p.text.replace(oldtitle,TITLE))
 if p.text.startswith('The manuscript presents a paired evaluation framework'):
  fill(p,'The manuscript combines an operational evaluation framework with three-study replay evidence, an exact decomposition of selection gains and a reporting protocol for sequential screening. The six main figures connect the information flow to paired outcomes, selection scope, task heterogeneity and policy-family sensitivity. The supporting information provides the complete comparisons and analysis chronology.'+(' A supplementary scGPT representation example extends the fixed-policy analysis under matched acquisition conditions.' if exp.exists() else ''))
c.save(O/'Cover_Letter.docx')
# Publish editable vector/print assets and a version-specific figure map.
for p in Path('outputs/manuscript_focus_v2/figures').glob('Fig0[234]*'):
 shutil.copy2(p,O/'figures'/p.name)
for p in (S/'figures').glob('*'):shutil.copy2(p,O/'figures'/p.name)
sections={};current='front'
for p in d.paragraphs:
 if p.text in ['Abstract','Introduction','Results','Discussion','Methods','Data availability','References']:current=p.text
 sections[current]=sections.get(current,0)+len(re.findall(r"\b[\w'-]+\b",p.text))
(O/'word_counts.json').write_text(json.dumps(sections,indent=2))
print(json.dumps(sections,indent=2));print('main images',len(d.inline_shapes),'SI images',len(si.inline_shapes))
