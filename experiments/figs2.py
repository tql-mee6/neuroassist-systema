import sys; sys.path.insert(0,'.')
from experiments.figlib import *
OUT="docs/"
SKIN="#f2d6bf"; HAIR="#3a3f4f"; GREY="#5b6577"; GOLD="#d9a520"
def callout(ax,xy,xt,yt,txt,n,color=NAVY):
    ax.annotate("",xy=xy,xytext=(xt,yt),arrowprops=dict(arrowstyle="-",color=color,lw=1.1,shrinkA=0,shrinkB=0))
    ax.add_patch(Circle((xt,yt),1.25,fc=color,ec="white",lw=1)); ax.text(xt,yt,str(n),color="white",fontsize=7,ha="center",va="center",fontweight="bold")
# ---------- модель прототипа: гарнитура на голове, вид сверху
def headset_model():
    fig,ax=canvas(7.4,4.2,80,53); ax.set_ylim(8,53)
    cx,cy,R=19,24,12
    # уши, нос
    for sx in(-1,1): ax.add_patch(Ellipse((cx+sx*(R+0.6),cy),2.6,6,fc=SKIN,ec=GREY,lw=1.2))
    ax.add_patch(Polygon([(cx-2.6,cy+R-0.5),(cx,cy+R+3.4),(cx+2.6,cy+R-0.5)],fc=SKIN,ec=GREY,lw=1.2))
    ax.add_patch(Circle((cx,cy),R,fc=HAIR,ec=GREY,lw=1.5))
    # линии системы 10-20
    ax.plot([cx,cx],[cy-R+1,cy+R-1],color="#8793ad",lw=0.8,ls=(0,(3,3)))
    ax.plot([cx-R+1,cx+R-1],[cy,cy],color="#8793ad",lw=0.8,ls=(0,(3,3)))
    ax.text(cx,cy-R-3.2,"ВИД СВЕРХУ (нос вверху)",fontsize=6.5,ha="center",color=MUT)
    # оголовье ухо-ухо через макушку
    ax.add_patch(Rectangle((cx-R-0.4,cy-0.9),2*R+0.8,1.8,fc="#2b3040",ec="#161a26",lw=0.8,zorder=3))
    # электроды
    pos={"C3":(cx-6.6,cy),"Cz":(cx,cy),"C4":(cx+6.6,cy)}
    for n,(x,y) in pos.items():
        ax.add_patch(Circle((x,y),2.1,fc=GOLD,ec="#7a5c0c",lw=1.2,zorder=4))
        for a in np.linspace(0,2*np.pi,7)[:-1]: ax.add_patch(Circle((x+1.0*np.cos(a),y+1.0*np.sin(a)),0.32,fc="#fff3c4",ec="none",zorder=5))
        ax.text(x,y-3.8,n,ha="center",fontsize=7.5,fontweight="bold",color="white",zorder=6)
    # блок электроники у правого уха
    ex,ey=cx+R+1.4,cy-6.5
    ax.add_patch(FancyBboxPatch((ex,ey),5.2,9,boxstyle="round,pad=0,rounding_size=1",fc=SKY,ec=NAVY,lw=1.6,zorder=6))
    ax.plot([ex+0.6,ex+4.6],[ey+6.3,ey+6.3],color="white",lw=1,zorder=7); ax.add_patch(Circle((ex+2.6,ey+2.4),0.7,fc="#9be564",ec="none",zorder=7))
    # кабель оголовья -> блок
    ax.plot([cx+R-0.4,ex+0.5],[cy,ey+7.5],color="#2b3040",lw=2,zorder=5)
    # референс на мочке левого уха
    rx,ry=cx-R-0.6,cy-4.8
    ax.add_patch(Circle((rx,ry),1.6,fc="#c9ced9",ec=GREY,lw=1.2,zorder=6)); ax.plot([rx,cx-R+0.5],[ry,cy-0.5],color=GREY,lw=1,zorder=5)
    # Bluetooth волны
    for r in (3.5,6,8.5): ax.add_patch(Arc((ex+5.4,ey+4.5),r,r,theta1=-40,theta2=40,color=SKY,lw=1.5))
    ax.add_patch(FancyBboxPatch((ex+12,ey+0.5),9.5,7,boxstyle="round,pad=0,rounding_size=0.8",fc="white",ec=NAVY,lw=1.4)); ax.add_patch(Rectangle((ex+12.8,ey+1.4),7.9,4.6,fc=LIGHT,ec=GREY,lw=0.8))
    ax.text(ex+16.75,ey+3.7,"ПК",fontsize=8,ha="center",va="center",color=NAVY,fontweight="bold")
    ax.plot([ex+5.5,ex+11.8],[ey+4.5,ey+4.2],color=SKY,lw=1.5,ls=(0,(2,2)))
    # обозначения
    callout(ax,pos["C3"],cx-R+1,cy+R+4.5,"",1,TEAL); callout(ax,pos["Cz"],cx,cy+R+8.0,"",2,TEAL); callout(ax,pos["C4"],cx+R-1,cy+R+4.5,"",3,TEAL)
    callout(ax,(cx-R-0.5,cy+0.5),cx-R-4.5,cy+4.5,"",4,NAVY)
    callout(ax,(rx,ry),rx-2.5,ry-5,"",5,CORAL)
    callout(ax,(ex+2.6,ey+9),ex+8.8,ey+12.5,"",6,AMBER)
    callout(ax,(ex+8.5,ey+4.4),ex+9,ey-3.5,"",7,SKY)
    callout(ax,(ex+16.7,ey+7.5),ex+17.5,ey+12,"",8,CORAL)
    # легенда справа
    lx=55
    ax.text(lx,50.0,"Модель прототипа\n(3-канальная гарнитура)",fontsize=8.4,va="top",linespacing=1.2,fontweight="bold",color=NAVY)
    L=[("1·2·3","Сухие электроды C3, Cz, C4 над моторной корой: пружинные штыри,\nне требуют геля (сигнал руки/ног)",TEAL),
       ("4","Оголовье с регулировкой размера — прижим электродов ≈ 1–2 Н",NAVY),
       ("5","Референсный электрод-клипса на мочке уха (A1) и заземление",CORAL),
       ("6","Блок электроники: усилитель, АЦП 24 бит, 250 Гц, аккумулятор",AMBER),
       ("7","Канал Bluetooth LE (или кабель USB) — пакеты данных",SKY),
       ("8","Компьютер с ПО «НейроАссистент»: фильтры, ИИ, интерфейс",CORAL)]
    import textwrap
    y=42.5
    for n,t,c in L:
        t=textwrap.fill(t.replace("\n"," "),38)
        ax.add_patch(Circle((lx+1.2,y-0.9),1.25,fc=c,ec="white")); ax.text(lx+1.2,y-0.9,n[0] if len(n)==1 else "1–3",color="white",fontsize=5.6 if len(n)>1 else 7,ha="center",va="center",fontweight="bold")
        ax.text(lx+3.4,y,t,fontsize=6.2,va="top",color=INK,linespacing=1.25); y-=1.5*(t.count("\n")+1)+2.6
    fig.savefig(OUT+"fig_headset_model.png"); plt.close(fig)
# ---------- иллюстрации датчиков и типов гарнитур
def pin_electrode(ax,x,y,s=1.0):
    ax.add_patch(Circle((x,y),5.2*s,fc="#c9ced9",ec=GREY,lw=1.3))
    ax.add_patch(Circle((x,y),4.2*s,fc="#e8ebf2",ec=GREY,lw=0.8))
    for a in np.linspace(0,2*np.pi,7)[:-1]:
        for r in (2.6,):
            ax.add_patch(Circle((x+r*s*np.cos(a),y+r*s*np.sin(a)),0.85*s,fc=GOLD,ec="#7a5c0c",lw=0.9))
    ax.add_patch(Circle((x,y),0.9*s,fc=GOLD,ec="#7a5c0c",lw=0.9))
def electrode_types():
    fig,ax=canvas(7.4,5.8,80,48); ax.set_ylim(-15,48)
    # верхний ряд — датчики
    ax.text(40,46,"Датчики (электроды) для записи ЭЭГ — схематично",ha="center",fontsize=8.6,fontweight="bold",color=NAVY)
    cols=[13,40,67]
    # 1 пружинный штыревой
    x=cols[0]; pin_electrode(ax,x,35,1.2)
    ax.add_patch(Rectangle((x-4,23.5),8,2.2,fc="#c9ced9",ec=GREY)); ax.add_patch(Rectangle((x-0.7,19.8),1.4,3.7,fc=GREY))
    ax.text(x,16.6,"Сухой штыревой электрод",ha="center",fontsize=7.2,fontweight="bold",color=INK)
    ax.text(x,13.4,"(позолоченные штыри на пружине,\nпроходят через волосы; для\nC3, Cz, C4 — основной вариант)",ha="center",va="top",fontsize=6.3,color=MUT,linespacing=1.25)
    # 2 мягкий полимерный
    x=cols[1]
    ax.add_patch(Rectangle((x-5.5,29.5),11,3,fc="#c9ced9",ec=GREY))
    for dx in np.linspace(-4.5,4.5,6): ax.add_patch(Polygon([(x+dx-0.9,29.5),(x+dx+0.9,29.5),(x+dx+0.4,22.5),(x+dx-0.4,22.5)],fc="#3b4254",ec="#222735",lw=0.8))
    ax.add_patch(FancyBboxPatch((x-5.5,32.5),11,3,boxstyle="round,pad=0,rounding_size=0.6",fc=NAVY,ec=NAVY))
    ax.text(x,16.6,"Мягкий полимерный электрод",ha="center",fontsize=7.2,fontweight="bold",color=INK)
    ax.text(x,13.4,"(токопроводящие «пальцы» из\nсиликона; удобнее на длинной\nсессии, но чувствительнее к волосам)",ha="center",va="top",fontsize=6.3,color=MUT,linespacing=1.25)
    # 3 мокрый Ag/AgCl
    x=cols[2]
    ax.add_patch(Wedge((x,30.5),6,180,360,fc=GOLD,ec="#7a5c0c",lw=1.2)); ax.add_patch(Rectangle((x-6,30.5),12,0.01,fc=GOLD))
    ax.add_patch(Ellipse((x,30.5),12,2.6,fc="#f6e7a8",ec="#7a5c0c",lw=1.1)); ax.add_patch(Rectangle((x-0.6,30.5),1.2,5.2,fc="#c04a3a"))
    ax.plot([x,x+3,x+6],[35.7,38,36.5],color="#c04a3a",lw=1.4)
    ax.text(x,16.6,"Чашечный Ag/AgCl с гелем",ha="center",fontsize=7.2,fontweight="bold",color=INK)
    ax.text(x,13.4,"(клинический стандарт; точнее, но\nнужен гель и мытьё головы — для\nдома неудобно, в проекте не берём)",ha="center",va="top",fontsize=6.3,color=MUT,linespacing=1.25)
    ax.plot([2,78],[8.4,8.4],color="#c9d4e8",lw=1)
    ax.text(2,5.6,"Типы гарнитур по форм-фактору (на российском рынке):",fontsize=7.4,fontweight="bold",color=NAVY,va="center")
    b=-2.6
    x=13; ax.add_patch(Arc((x,b+1),12,11,theta1=0,theta2=180,color="#2b3040",lw=3))
    for dx in(-6,6): ax.add_patch(FancyBboxPatch((x+dx-1.5,b-2.4),3,4.6,boxstyle="round,pad=0,rounding_size=0.8",fc=SKY,ec=NAVY))
    for a in(150,30): ax.add_patch(Circle((x+6*np.cos(np.radians(a)),b+1+5.5*np.sin(np.radians(a))),0.85,fc=GOLD,ec="#7a5c0c"))
    ax.text(x,-9.6,"Наушники с электродами (C3, C4)\nтип Neiry Headphones — подходит",fontsize=6.2,va="top",ha="center",color=INK,linespacing=1.25)
    x=40; ax.add_patch(Wedge((x,b-2),7,0,180,fc="#dfe6f5",ec=NAVY,lw=1.3))
    for a in(30,60,90,120,150): ax.add_patch(Circle((x+4.6*np.cos(np.radians(a)),b-2+4.6*np.sin(np.radians(a))),0.7,fc=GOLD,ec="#7a5c0c"))
    for a in(75,105): ax.add_patch(Circle((x+2.3*np.cos(np.radians(a)),b-2+2.3*np.sin(np.radians(a))),0.65,fc=GOLD,ec="#7a5c0c"))
    ax.text(x,-9.6,"Шапочка на 8 каналов (есть C3, Cz, C4)\nтип NeuroPlay-8Cap — подходит",fontsize=6.2,va="top",ha="center",color=INK,linespacing=1.25)
    x=67; ax.add_patch(FancyBboxPatch((x-5.5,b-1),11,3.2,boxstyle="round,pad=0,rounding_size=1.4",fc="#d3d9e6",ec=GREY,lw=1.2))
    for dx in(-3.2,0,3.2): ax.add_patch(Circle((x+dx,b+0.6),0.65,fc=GOLD,ec="#7a5c0c"))
    ax.text(x,-9.6,"Лобная повязка — не покрывает\nмоторную кору, не подходит",fontsize=6.2,va="top",ha="center",color=CORAL,linespacing=1.25)
    fig.savefig(OUT+"fig_electrodes.png"); plt.close(fig)
if __name__=="__main__":
    headset_model(); electrode_types()
