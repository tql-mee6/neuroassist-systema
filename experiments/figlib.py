import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Ellipse, Polygon, Arc, FancyArrowPatch, Rectangle, Wedge
import numpy as np
plt.rcParams["font.family"] = "DejaVu Sans"
NAVY="#12285a"; TEAL="#17a398"; AMBER="#f2a900"; CORAL="#e4572e"; SKY="#4f8ef7"; INK="#1b2437"; MUT="#6b778f"; LIGHT="#eef3fb"; GREEN="#5aa469"
def box(ax,x,y,w,h,text,fc=LIGHT,ec=NAVY,tc=INK,fs=9,lw=1.5,bold=False,r=0.15,**k):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle=f"round,pad=0,rounding_size={r}",fc=fc,ec=ec,lw=lw,**k))
    ax.text(x+w/2,y+h/2,text,ha="center",va="center",fontsize=fs,color=tc,fontweight="bold" if bold else "normal",linespacing=1.25)
def arrow(ax,p,q,color=NAVY,lw=1.8,style="-|>",rad=0,**k):
    ax.add_patch(FancyArrowPatch(p,q,arrowstyle=style,mutation_scale=14,color=color,lw=lw,connectionstyle=f"arc3,rad={rad}",**k))
def canvas(w,h,xl,yl):
    fig=plt.figure(figsize=(w,h),dpi=200); ax=fig.add_axes([0,0,1,1]); ax.set_xlim(0,xl); ax.set_ylim(0,yl); ax.axis("off"); return fig,ax
