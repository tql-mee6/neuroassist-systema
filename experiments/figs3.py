import sys,json; sys.path.insert(0,'.')
from experiments.figlib import *
from scipy import signal
from neuroassist.config import *
from neuroassist.sources import SimulatedHeadset
OUT="docs/"; GREY="#5b6577"
R=json.load(open("experiments/results/results.json")); N=json.load(open("experiments/results/noise.json"))
# ---- ЭЭГ и ERD
def erd():
    cfg=Config(); fs=cfg.fs; env={}
    for lab,name in ((LEFT,"left"),(RIGHT,"right")):
        acc=[]
        for tr in range(40):
            s=SimulatedHeadset(cfg,seed=100+tr); s.set_intent(REST); a=s.read(fs*2); s.set_intent(lab); b=s.read(fs*4)
            x=np.hstack([a,b]); bb,aa=signal.butter(3,[8,13],btype="band",fs=fs); y=signal.filtfilt(bb,aa,x,axis=1)
            e=np.abs(signal.hilbert(y,axis=1))**2; acc.append(e)
        m=np.mean(acc,axis=0); base=m[:,fs//2:fs*2-fs//4].mean(axis=1,keepdims=True)
        win=int(0.4*fs); sm=np.apply_along_axis(lambda v:np.convolve(v,np.ones(win)/win,mode="same"),1,m)
        env[name]=(sm/base-1)*100
    t=np.arange(fs*6)/fs-2
    fig,axs=plt.subplots(1,3,figsize=(7.4,2.5),dpi=200,gridspec_kw={"width_ratios":[1,1,1.1]})
    for ax,name,ttl in((axs[0],"left","Воображение ЛЕВОЙ руки"),(axs[1],"right","Воображение ПРАВОЙ руки")):
        ax.plot(t,env[name][0],color=SKY,lw=1.6,label="C3 (левое полушарие)"); ax.plot(t,env[name][2],color=CORAL,lw=1.6,label="C4 (правое)")
        ax.axvline(0,color=MUT,ls="--",lw=0.8); ax.axhline(0,color=MUT,lw=0.6); ax.set_title(ttl,fontsize=8,color=NAVY,fontweight="bold")
        ax.set_xlim(-1.2,3.6); ax.set_ylim(-70,45); ax.set_xlabel("время, с (0 — начало воображения)",fontsize=6.5,color=MUT)
        ax.tick_params(labelsize=7); [ax.spines[k].set_visible(False) for k in("top","right")]
    axs[0].set_ylabel("изменение мощности\nмю-ритма, %",fontsize=7,color=MUT); axs[0].legend(fontsize=6,frameon=False,loc="lower right")
    # спектр
    ax=axs[2]; s=SimulatedHeadset(cfg,seed=5); s.set_intent(REST); r=s.read(fs*30); s2=SimulatedHeadset(cfg,seed=5); s2.set_intent(RIGHT); i2=s2.read(fs*30)
    for x,c,l in((r,GREY,"покой"),(i2,TEAL,"правая рука")):
        f,p=signal.welch(x[0],fs=fs,nperseg=fs*2); ax.semilogy(f,p,color=c,lw=1.5,label=l+", C3")
    ax.axvspan(8,13,color=AMBER,alpha=.18); ax.set_xlim(4,40); ym=[];
    [ym.extend(l.get_ydata()[(l.get_xdata()>=4)]) for l in ax.lines]; ax.set_ylim(0.04,8); ax.text(10.5,3.5,"мю",ha="center",fontsize=7,color="#8a6200")
    ax.set_title("Спектр канала C3",fontsize=8,color=NAVY,fontweight="bold"); ax.set_xlabel("частота, Гц",fontsize=6.5,color=MUT); ax.tick_params(labelsize=7); ax.legend(fontsize=6,frameon=False)
    [ax.spines[k].set_visible(False) for k in("top","right")]
    fig.tight_layout(); fig.savefig(OUT+"fig_erd.png"); plt.close(fig)
# ---- результаты
def results():
    fig,axs=plt.subplots(1,3,figsize=(7.4,2.6),dpi=200,gridspec_kw={"width_ratios":[1.25,1.1,0.9]})
    ax=axs[0]; u=np.arange(1,9); w=0.38
    ax.bar(u-w/2,np.array(R["cv3_noRest"])*100,w,color=TEAL,label="3 команды"); ax.bar(u+w/2,np.array(R["cv4"])*100,w,color=SKY,label="3 команды + покой")
    ax.axhline(75,color=CORAL,ls="--",lw=1); ax.text(8.6,60,"цель ≥75 %",ha="right",fontsize=6.3,color=CORAL,bbox=dict(fc="white",ec="none",pad=1))
    ax.set_ylim(0,125); ax.set_xticks(u); ax.set_xlabel("виртуальный пользователь",fontsize=6.8,color=MUT); ax.set_ylabel("точность, %",fontsize=7,color=MUT); ax.legend(fontsize=6,frameon=False,loc="upper left",ncol=2)
    ax.set_title("Точность по окнам (перекрёстная проверка)",fontsize=7.4,color=NAVY,fontweight="bold")
    ax=axs[1]; xs=[0,10,20,30,45]
    ax.plot(xs,[N[f"3cmd_{x}"]*100 for x in xs],"o-",color=TEAL,lw=1.8,label="3 команды"); ax.plot(xs,[N[f"4cls_{x}"]*100 for x in xs],"s-",color=SKY,lw=1.8,label="+ покой")
    ax.axhline(33.3,color=MUT,ls=":",lw=1); ax.text(45,36,"случайно",ha="right",fontsize=6,color=MUT)
    ax.set_ylim(0,100); ax.set_xlabel("добавочный шум (плохой контакт), усл. мкВ",fontsize=6.3,color=MUT); ax.legend(fontsize=6,frameon=False)
    ax.set_title("Влияние шума и контакта",fontsize=7.4,color=NAVY,fontweight="bold")
    ax=axs[2]; ax.axis("off"); o=R["online"]; t=R["typing"]
    items=[(f"{o['correct']*100:.0f} %","верных команд\nв онлайн-режиме",TEAL),(f"{o['fp_per_min']:.1f} /мин","ложных срабатываний\nв покое",CORAL),(f"{o['latency_s']:.1f} с","задержка команды",SKY),(f"≈{t['chars_per_min']:.0f} симв./мин","скорость набора\nс клавиатурой",AMBER)]
    for i,(v,l,c) in enumerate(items):
        y=0.78-i*0.26; ax.text(0.02,y+0.06,v,fontsize=10.5,fontweight="bold",color=c,transform=ax.transAxes,va="center"); ax.text(0.02,y-0.07,l,fontsize=6,color=MUT,transform=ax.transAxes,va="center",linespacing=1.15)
    for ax in axs[:2]:
        [ax.spines[k].set_visible(False) for k in("top","right")]; ax.tick_params(labelsize=7)
    fig.tight_layout(); fig.savefig(OUT+"fig_results.png"); plt.close(fig)
# ---- сканирование
def scanning():
    fig,ax=canvas(7.4,2.5,80,27)
    box(ax,2,9,25,13,"ВЫБОР СТРОКИ\\nподсвечена строка клавиатуры".replace("\\n","\n"),fc="#fff4d1",ec=AMBER,fs=8,bold=True)
    box(ax,53,9,25,13,"ВЫБОР СИМВОЛА\nподсвечен символ в строке",fc="#d7f3ef",ec=TEAL,fs=8,bold=True)
    arrow(ax,(27.4,19),(52.6,19),color=TEAL,lw=2); ax.text(40,21.2,"НОГИ — войти в строку",ha="center",fontsize=7.2,color=TEAL,fontweight="bold")
    arrow(ax,(52.6,12),(27.4,12),color=AMBER,lw=2); ax.text(40,14.6,"символ выбран → снова строки",ha="center",fontsize=7,color="#8a6200",fontweight="bold")
    for x0,tx in((2,"ПРАВАЯ рука → следующая строка\nЛЕВАЯ рука ← предыдущая"),(53,"ПРАВАЯ рука → следующий символ\nЛЕВАЯ рука ← предыдущий")):
        ax.text(x0+12.5,5.2,tx,ha="center",va="center",fontsize=6.6,color=INK,linespacing=1.25)
    ax.text(40,25.2,"Три мысленные команды управляют всей клавиатурой: «привет» — ≈29 команд, подсказки слов сокращают путь",ha="center",fontsize=7.2,color=NAVY,fontweight="bold")
    fig.savefig(OUT+"fig_scanning.png"); plt.close(fig)
# ---- аналоги (вместо таблиц 1 и 2)
def analogs():
    fig,ax=canvas(7.4,3.7,80,40)
    cols=["Neuralink\n(США)","Emotiv\n(Австралия)","OpenBCI\n(США)","Neiry / NeuroPlay\n(Россия)","Наш проект"]
    rows=[("Вмешательство",["хирургия","нет","нет","нет","нет"],[0,2,2,2,2]),
          ("Цена","От $100 000|От $500–2000|От $199|74–120 тыс. руб.|0 руб. (симуляция)".split("|"),[0,1,1,1,2]),
          ("Программы","закрытые|по подписке|открытые|только для науки|открытые, для ПК".split("|"),[0,0,2,1,2]),
          ("Для чего","медицина,\nроботы|игры,\nисследования|исследования|нейротренинг,\nнаука|управление ПК\nбез рук".split("|"),[1,1,1,1,2]),
          ("Язык, поддержка","английский|английский|английский|русский|русский".split("|"),[0,0,0,2,2])]
    C={0:"#f9d9d2",1:"#fdf0c8",2:"#d4efdc"}; E={0:CORAL,1:AMBER,2:GREEN}
    x0=13.5; cw=13.3; y0=33
    for j,c in enumerate(cols):
        fc=NAVY if j==4 else "#e4eaf6"; tc="white" if j==4 else NAVY
        box(ax,x0+j*cw+0.3,y0+0.5,cw-0.6,6,c,fc=fc,ec=fc,tc=tc,fs=6.6,bold=True,r=0.5)
    for i,(n,vals,sc) in enumerate(rows):
        y=y0-(i+1)*6.1
        ax.text(0.5,y+2.7,n,fontsize=7,fontweight="bold",color=NAVY,va="center")
        for j,(v,s) in enumerate(zip(vals,sc)):
            box(ax,x0+j*cw+0.3,y+0.3,cw-0.6,5.4,v,fc=C[s],ec=E[s],fs=5.8,lw=1.0,r=0.5)
    for xx,cc,tt in((0.5,CORAL,"■ неудобно или недоступно"),(26,AMBER,"■ частично"),(40,GREEN,"■ подходит для задачи")): ax.text(xx,1.6,tt,fontsize=6.4,color=cc)
    ax.add_patch(Rectangle((0.5,1.2),0,0)); 
    fig.savefig(OUT+"fig_analogs.png"); plt.close(fig)
# ---- дорожная карта и стоимость
def roadmap():
    fig,(a1,a2)=plt.subplots(1,2,figsize=(7.4,2.5),dpi=200,gridspec_kw={"width_ratios":[2.0,1]})
    st=[("Конвейер сигналов\nна открытых данных",0,2,SKY),("Интерфейс и сканирование\n(прототип без датчиков)",1,2,TEAL),("Подключение гарнитуры",3,2,AMBER),("Сбор собственного набора",4,2,CORAL),("Пилот в техникуме",6,3,NAVY)]
    for i,(n,s,d,c) in enumerate(st):
        a1.barh(len(st)-1-i,d,left=s,color=c,height=0.55); a1.text(-0.2,len(st)-1-i,n,ha="right",va="center",fontsize=6.3,color=INK,linespacing=1.15)
    a1.set_xlim(0,9); a1.set_yticks([]); a1.set_xticks(range(0,9)); a1.set_xticklabels(["окт\n2026","ноя","дек","янв\n2027","фев","мар","апр","май","июн"],fontsize=6)
    [a1.spines[k].set_visible(False) for k in("top","right","left")]; a1.set_title("План апробации",fontsize=7.8,color=NAVY,fontweight="bold",loc="right")
    a1.set_position([0.28,0.2,0.4,0.68])
    names=["Симуляция","Neiry\nLite","NeuroPlay\n8Cap"]; v=[0,74,119.9]
    b=a2.bar(names,v,color=[GREEN,AMBER,CORAL],width=0.6)
    for r,x in zip(b,v): a2.text(r.get_x()+r.get_width()/2,x+3,("0 руб." if x==0 else f"{x:,.0f} тыс.".replace(",",".")),ha="center",fontsize=7,fontweight="bold",color=INK)
    a2.set_ylim(0,140); a2.tick_params(labelsize=6); a2.set_ylabel("тыс. руб.",fontsize=6.5,color=MUT); a2.set_title("Затраты по режимам",fontsize=7.8,color=NAVY,fontweight="bold")
    [a2.spines[k].set_visible(False) for k in("top","right")]
    a2.set_position([0.74,0.2,0.25,0.68])
    fig.savefig(OUT+"fig_roadmap.png"); plt.close(fig)
erd(); results(); scanning(); analogs(); roadmap()
