from pathlib import Path
import pandas as pd, matplotlib.pyplot as plt, numpy as np
B=Path(__file__).parent; OUT=B/'plots';OUT.mkdir(exist_ok=True)
D=B/'results_calibrated'
labels=['TFT','GT','AC','AD','RANDOM'];colors={'TFT':'#00E885','GT':'#E8B75A','AC':'#c8d9d1','AD':'#FF5B50','RANDOM':'#5CA7CD'}
plt.rcParams.update({'font.size':11,'figure.facecolor':'#121416','axes.facecolor':'#121416','axes.edgecolor':'#818984','axes.labelcolor':'#e6e2d9','xtick.color':'#a9a9a1','ytick.color':'#a9a9a1','text.color':'#e6e2d9','grid.color':'#3b4445','savefig.facecolor':'#121416'})
def save(name):plt.tight_layout(pad=2);plt.savefig(OUT/name,dpi=180,bbox_inches='tight');plt.close()
fig,ax=plt.subplots(figsize=(13,5.8));d=pd.read_csv(D/'baseline/noise_free/seed_101.csv')
for l in labels: ax.plot(d.generation,d[l]/d.total*100,label=l,color=colors[l],linewidth=2.3)
ax.set(xlabel='Generation',ylabel='Population share (%)',title='Baseline  |  α=0.50  ε=0  f=0  |  seed 101',ylim=(0,100));ax.grid(alpha=.3);ax.legend(ncol=5,loc='upper center');save('34_baseline_seed101.png')
def aggregate_plot(group,values,title,name,xlabel):
 agg=pd.read_csv(D/'aggregate.csv');df=agg[agg.group==group].set_index('config').loc[values]
 fig,ax=plt.subplots(figsize=(13,5.8));xx=np.arange(len(values))
 for l in labels:
  ax.plot(xx,df[l+'_mean'],marker='o',markersize=7,lw=2.2,label=l,color=colors[l]);ax.fill_between(xx,(df[l+'_mean']-df[l+'_sd']).to_numpy(dtype=float),(df[l+'_mean']+df[l+'_sd']).to_numpy(dtype=float),color=colors[l],alpha=.12)
 ax.set_xticks(xx);ax.set_xticklabels([v.rsplit('_',1)[-1] for v in values]);ax.set(xlabel=xlabel,ylabel='Final population share, mean of 8 seeds (%)',title=title,ylim=(-4,104));ax.legend(ncol=5,loc='upper center');ax.grid(alpha=.3);save(name)
aggregate_plot('errors',[f'error_{x:.2f}' for x in [0,.01,.02,.05,.10,.20]],'Error sweep  |  α=.50  f=0','35_error_sweep.png','Execution error probability ε')
aggregate_plot('forgiveness',[f'forgive_{x:.2f}' for x in [0,.05,.10,.25,.50,.75]],'Forgiveness sweep  |  α=.50  ε=.08','36_forgiveness_sweep.png','Forgiveness probability f')
aggregate_plot('selection',[f'alpha_{x:.2f}' for x in [0,.03,.05,.10,.20,.50,1.0]],'Selection sweep  |  ε=.04  f=.05','37_selection_sweep.png','Selection intensity α')
agg=pd.read_csv(D/'aggregate.csv');vals=['equal','cooperation_heavy','defection_heavy','random_heavy'];dd=agg[agg.group=='initial'].set_index('config').loc[vals]
fig,ax=plt.subplots(figsize=(13,5.8));xs=np.arange(len(vals));bottom=np.zeros(len(vals));
for l in labels:
 y=dd[l+'_mean'].to_numpy(float);ax.bar(xs,y,bottom=bottom,label=l,color=colors[l],width=.65);bottom+=y
ax.set_xticks(xs);ax.set_xticklabels(['Equal','Cooperation-heavy','Defection-heavy','Random-heavy']);ax.set(xlabel='Initial population (N=600)',ylabel='Final population share, mean of 8 seeds (%)',title='Initial conditions  |  α=.50  ε=.04  f=.05',ylim=(0,108));ax.legend(ncol=5,loc='upper center');save('38_initial_conditions.png')
print([p.name for p in OUT.glob('*.png')])
