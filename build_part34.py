from pathlib import Path
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN,MSO_ANCHOR
from pptx.enum.dml import MSO_LINE_DASH_STYLE
import csv
O=Path('/mnt/data/EPD_Research')
prs=Presentation();prs.slide_width=Inches(13.333);prs.slide_height=Inches(7.5)
C=lambda x: RGBColor.from_string(x)
BG=C('121416'); P=C('1D2022'); TXT=C('E6E2D9'); MUT=C('A9A9A1'); GRID=C('515653'); G=C('00E885'); R=C('FF5B50'); Y=C('E8B75A')
def rect(s,x,y,w,h,col=P,line=GRID):
 z=s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h));z.fill.solid();z.fill.fore_color.rgb=col;z.line.color.rgb=line;z.line.width=Pt(.7);return z
def line(s,x1,y1,x2,y2,c=GRID,w=1):
 z=s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2));z.line.color.rgb=c;z.line.width=Pt(w);return z
def text(s,x,y,w,h,string,sz=18,col=TXT,font='Aptos',bold=False,align=None):
 z=s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h));tf=z.text_frame;tf.clear();tf.word_wrap=True;tf.margin_left=Inches(.02);tf.margin_top=Inches(.01)
 for i,t in enumerate(string.split('\n')):
  p=tf.paragraphs[0] if i==0 else tf.add_paragraph(); p.text=t;p.space_after=Pt(6)
  if align:p.alignment=align
  for run in p.runs:run.font.name=font;run.font.size=Pt(sz);run.font.bold=bold;run.font.color.rgb=col
 return z
def slide(n,title,sub,section):
 s=prs.slides.add_slide(prs.slide_layouts[6]);s.background.fill.solid();s.background.fill.fore_color.rgb=BG
 rect(s,.35,.3,.09,.43,G,G);text(s,.56,.27,10,.26,f'{section.upper()}  /  {n:02d}',11,Y,'Consolas',True)
 text(s,.58,.72,12,.70,title,29,TXT,'Aptos Display',True)
 text(s,.60,1.49,11,.43,sub,14,MUT,'Consolas')
 line(s,.58,6.99,12.75,6.99);text(s,.6,7.08,8,.2,'EVOLUTIONARY PRISONER’S DILEMMA  //  IMPLEMENTATION & EXPERIMENTS',9,MUT,'Consolas')
 text(s,12,7.08,.7,.2,f'{n:02d}',10,G,'Consolas',True,PP_ALIGN.RIGHT)
 return s
def box(s,x,y,w,h,heading,body,accent=G,sz=16):
 rect(s,x,y,w,h);rect(s,x,y,.055,h,accent,accent);text(s,x+.20,y+.15,w-.37,.27,heading,13,accent,'Consolas',True)
 text(s,x+.20,y+.54,w-.38,h-.66,body,sz,TXT)
def arrow(s,x1,y1,x2,y2):
 line(s,x1,y1,x2,y2,Y,2); rect(s,x2-.04,y2-.04,.08,.08,Y,Y)
def spacerow(s,items,y=2.45):
 for i,(title,body) in enumerate(items):
  x=.62+i*(12.2/len(items)); w=12.2/len(items)-.22
  box(s,x,y,w,2.95,title,body,G if i%2==0 else Y,14)
# 24
s=slide(24,'Architecture / one generation at a time','The code separates interaction, scoring, selection, and recording.','03 architecture')
flow=[('01','INITIALISE','seed + parameters'),('02','MATCH','100 trials per pairing'),('03','SCORE','aggregate payoffs'),('04','SELECT','average payoff → weight'),('05','UPDATE','fixed total population'),('06','RECORD','history → plot')]
for i,(num,name,desc) in enumerate(flow):
 x=.7+(i%3)*4.25;y=2.1+(i//3)*2.02
 rect(s,x,y,3.95,1.60);text(s,x+.15,y+.12,.44,.27,num,15,G,'Consolas',True);text(s,x+.64,y+.10,3.1,.29,name,19,TXT,'Aptos Display',True);text(s,x+.64,y+.64,3.0,.68,desc,14,MUT)
 if i%3!=2:arrow(s,x+3.95,y+.8,x+4.22,y+.8)
text(s,.75,6.47,11,.28,'LOOP until generation limit   •   interaction state resets per match   •   population size is conserved',13,Y,'Consolas')
#25
s=slide(25,'Single match / 30 rounds of memory','Two strategies interact. The program records what actually happened—not what was intended.','03 match mechanics')
spacerow(s,[('STATE','Start with previous action = C. Each Grim Trigger player has a separate trigger state.'),('ACTION','chooseMove() proposes an action. Then execution error may flip it.'),('PAYOFF','payoff() updates scores. Executed moves update history and triggers.')],2.22)
box(s,.82,5.52,11.60,.96,'CODE WALKTHROUGH','chooseMove()  →  playGame()  →  payoff()  →  previousMove / grimTriggered',Y,16)
#26
s=slide(26,'Generation / converting payoff to survival','Representative matchups estimate per-strategy fitness; relative performance changes the population.','03 evolutionary update')
box(s,.7,2.08,5.58,2.16,'MATCH COUNTS','i ≠ j : Nᵢ × Nⱼ\ni = j : Nᵢ(Nᵢ − 1) / 2',G,23)
box(s,6.57,2.08,6.00,2.16,'SELECTION FACTOR','Fᵢ = (1 − α) + α · (π̄ᵢ / π̄)',Y,21)
box(s,.7,4.58,11.86,1.55,'INTEGER POPULATIONS','Normalise weighted counts → floor → allocate remaining individuals by largest fractional remainder. Total N stays constant.',G,17)
#27
s=slide(27,'Recording / one row per generation','The research runner removes only the plotting dependency and writes CSV history.','03 output')
box(s,.7,2.10,5.6,3.5,'DATA SCHEMA','generation | TFT | GT | AC | AD | RANDOM\nseed | rounds | α | error | forgiveness\n\nThe interactive version still uses Matplot++.',G,17)
box(s,6.6,2.10,5.9,3.5,'HOW TO READ A CURVE','x: generation (0–250)\ny: strategy share of population (%)\nEach line: one strategy\nEvery experiment records its seed and settings.',Y,17)
text(s,.75,6.10,11.5,.46,'RECORD → COMPARE → TEST REPEATABILITY  /  Do not confuse a flat line with equal fitness.',17,R,'Consolas',True)
#28
s=slide(28,'Methodology / what stays fixed','A controlled computational experiment, not a collection of cherry-picked screenshots.','04 methodology')
spacerow(s,[('GAME','Weak PD matrix: CC = 3/3; CD = 0/5; DD = 0/0. 5 strategies.'),('SAMPLING','100 simulations per strategy matchup, per generation. Pseudorandom MT19937.'),('BASELINE','600 individuals, initially 120 per strategy. 30 rounds, 250 generations.')],2.2)
box(s,.73,5.55,11.85,.99,'MAIN OBSERVABLE','Population share (%) by generation; final share across seeds; standard deviation across repeated runs.',Y,16)
#29
s=slide(29,'Experiment matrix / change one thing','Each family varies one factor and holds the rest constant.','04 methodology')
rows=[('ERROR','0 / .01 / .02 / .05 / .10 / .20','α=.50, forgiveness=0'),('FORGIVENESS','0 / .05 / .10 / .25 / .50 / .75','α=.50, error=.08'),('SELECTION α','0 / .03 / .05 / .10 / .20 / .50 / 1','error=.04, forgiveness=.05'),('INITIAL POP.','equal / C-heavy / D-heavy / R-heavy','α=.50, error=.04, forgiveness=.05'),('ROUNDS','20 / 30 / 50','α=.50, error=.04, forgiveness=.05')]
for i,(name,values,control) in enumerate(rows):
 y=2.12+i*.79;rect(s,.73,y,11.8,.7,P);text(s,.95,y+.1,2.5,.24,name,15,G,'Consolas',True);text(s,3.5,y+.09,4.4,.48,values,13,TXT,'Consolas');text(s,8.15,y+.08,4.12,.47,control,12,MUT,'Consolas')
#30
s=slide(30,'Replication / what 466 runs revealed','250 initial sweeps + 216 calibrated runs. The calibrated comparisons use eight distinct seeds.','04 methodology')
box(s,.7,2.13,5.72,3.37,'THE PITFALL','At weak selection, integer rounding can freeze all 600 population counts even when payoffs differ. That is a numerical plateau—not proof of equilibrium.',R,18)
box(s,6.7,2.13,5.80,3.37,'THE RESPONSE','Use α=.50 for the principal comparisons. Retain a separate α sweep to show what selection intensity and rounding actually do.',G,18)
text(s,.78,5.95,11,.58,'Report: mean ± sample SD of final strategy share across 8 seeds. Figures: show example runs with exact seeds.',15,Y,'Consolas')
#31
s=slide(31,'Live demo 01 / begin with a clean game','Purpose: establish a baseline before introducing any noise.','04 live demo')
box(s,.72,2.22,5.44,3.67,'TYPE THESE SETTINGS','seed 101\nrounds 30  |  generations 250\npopulation 120 / 120 / 120 / 120 / 120\nα = .50  |  error = 0  |  forgiveness = 0',G,17)
box(s,6.45,2.22,5.93,3.67,'WHAT TO POINT OUT','The plot changes by generation. TFT, GT and AC retain most of the population; AD and Random become rare. Do not call this a universal winner.',Y,18)
#32
s=slide(32,'Live demo 02 / a small mistake changes the world','Run the exact same starting population and seed; vary only the error rate.','04 live demo')
box(s,.72,2.2,5.52,3.7,'RUN THIS PAIR','seed 101; α=.50; forgiveness=0\n\nRUN A: error = 0.00\nRUN B: error = 0.10\n\nSame rounds and initial population.',R,17)
box(s,6.53,2.2,5.85,3.7,'DISCUSSION PROMPT','What happens to retaliatory behaviour? Compare the final Grim Trigger share and the disappearance of TFT. Mention how the result changes again at error=.20.',Y,17)
#33
s=slide(33,'Live demo 03 / forgiveness has a tipping point','At fixed error, try mild, moderate and high forgiveness—not just zero vs one.','04 live demo')
box(s,.72,2.2,5.5,3.7,'RUN THREE VALUES','seed 101; α=.50; error=.08\n\nforgiveness = 0.00\nforgiveness = 0.25\nforgiveness = 0.50',G,18)
box(s,6.53,2.2,5.83,3.7,'WHAT TO DISCUSS','Why can modest forgiveness help TFT, while very high forgiveness may make exploitation easier? Point out the change in dominant strategy rather than reading all five lines.',Y,17)
# placeholder slides
def blank(n,title,subtitle,request,one_liner):
 s=slide(n,title,subtitle,'04 results / insert plot')
 rect(s,.73,2.03,11.8,3.86,BG,GRID)
 # keep big truly empty area
 text(s,1.1,3.28,11,.38,'DROP A FULL-WIDTH PLOT HERE',22,MUT,'Consolas',False,PP_ALIGN.CENTER)
 text(s,1.25,3.88,10.75,.5,request,13,Y,'Consolas',False,PP_ALIGN.CENTER)
 text(s,.79,6.07,11.6,.56,one_liner,15,TXT,'Aptos')
blank(34,'Results / baseline population trajectories','Plot 1: no error, no forgiveness; equal starting population.','Use plots/34_baseline_seed101.png  •  seed 101, α=.50','Narrate: under these settings, GT, TFT and AC survive; AD and Random decline.')
blank(35,'Results / execution error sweep','Plot 2: compare outcomes at ε=0, .02, .05, .10, .20.','Use plots/35_error_sweep.png  •  mean over 8 seeds','Highlight: ε=.10 favours GT here; ε=.20 produces a different composition.')
blank(36,'Results / forgiveness is not monotonic','Plot 3: fixed error ε=.08; sweep forgiveness f.','Use plots/36_forgiveness_sweep.png  •  mean over 8 seeds','Emphasise: results at f=.25 and f=.50 are dramatically different.')
blank(37,'Results / selection intensity and rounding','Plot 4: vary α while keeping error and forgiveness fixed.','Use plots/37_selection_sweep.png  •  mean over 8 seeds','Explain: low α can be frozen by integer rounding; higher α produces large shifts.')
blank(38,'Results / effect of starting population','Plot 5: compare equal, cooperation-heavy and defection-heavy starts.','Use plots/38_initial_conditions.png  •  mean over 8 seeds','Interpret outcomes cautiously: starting composition and selection both matter.')
out=O/'Game_Theory_Parts_3_4_Slides_24_to_38.pptx';prs.save(out);print(out, len(prs.slides))
