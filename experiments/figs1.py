import sys; sys.path.insert(0,'.')
from experiments.figlib import *
OUT="docs/"
# ---- Рис: численность инвалидов
def disability():
    fig,ax=plt.subplots(figsize=(7.2,3.0),dpi=200)
    yrs=["2011","2016","2020","2022","2023","2024"]; v=[13.21,12.75,11.87,10.93,11.04,11.12]
    cols=[SKY]*5+[TEAL]
    b=ax.bar(yrs,v,color=cols,width=0.62)
    for r,x in zip(b,v): ax.text(r.get_x()+r.get_width()/2,x+0.2,f"{x:.2f}".replace(".",","),ha="center",fontsize=9,color=INK,fontweight="bold")
    ax.set_ylim(0,15.5); ax.set_ylabel("млн человек",fontsize=9,color=MUT)
    for s in("top","right"): ax.spines[s].set_visible(False)
    ax.tick_params(labelsize=9,colors=INK); ax.grid(axis="y",alpha=.25); ax.set_axisbelow(True)
    ax.annotate("≈ 11,1 млн человек\nна конец 2024 г.",xy=(5,11.12),xytext=(3.6,14.0),fontsize=9,color=NAVY,arrowprops=dict(arrowstyle="->",color=NAVY))
    fig.tight_layout(); fig.savefig(OUT+"fig_disability.png"); plt.close(fig)
# ---- Рис: принцип работы
def principle():
    fig,ax=canvas(7.4,2.8,80,28)
    steps=[("1. Воображение\nдвижения","левая рука /\nправая рука / ноги",SKY),("2. Датчики\nна голове","3 сухих электрода\nC3 · Cz · C4",TEAL),
           ("3. Программа\nна компьютере","фильтрация →\nклассификатор",NAVY),("4. Команда\nинтерфейсу","← назад · вперёд →\nвыбрать",AMBER),("5. Экран\nи обратная связь","клавиатура,\nподсказки слов",CORAL)]
    w=13.7; gap=2.4
    for i,(t,s,c) in enumerate(steps):
        x=1+i*(w+gap); ax.add_patch(FancyBboxPatch((x,10),w,15,boxstyle="round,pad=0,rounding_size=1",fc="white",ec=c,lw=2.2))
        ax.add_patch(FancyBboxPatch((x,18.2),w,6.8,boxstyle="round,pad=0,rounding_size=1",fc=c,ec=c))
        ax.text(x+w/2,21.6,t,ha="center",va="center",fontsize=7.3,color="white",fontweight="bold",linespacing=1.2)
        ax.text(x+w/2,14.2,s,ha="center",va="center",fontsize=7.3,color=MUT,linespacing=1.25)
        if i<4: arrow(ax,(x+w+0.2,17.5),(x+w+gap-0.2,17.5))
    arrow(ax,(1+4*(w+gap)+w/2,9.6),(1+w/2,9.6),color=CORAL,rad=0.0)
    ax.plot([1+4*(w+gap)+w/2]*2,[10,9.6],color=CORAL,lw=1.8); ax.plot([1+w/2]*2,[10,9.6],color=CORAL,lw=1.8)
    ax.text(40,6.6,"обратная связь: пользователь видит результат и корректирует усилие",ha="center",fontsize=8.2,color=CORAL,style="italic")
    ax.text(40,2.2,"Без операции: электроды лежат на коже головы и только считывают сигнал",ha="center",fontsize=8,color=MUT)
    fig.savefig(OUT+"fig_principle.png"); plt.close(fig)
# ---- Рис: конвейер ПО
def pipeline():
    fig,ax=canvas(7.4,3.1,80,31)
    A=[("Источник\nсигнала","имитатор,\nзапись, гарнитура",SKY),("Фильтры","режекция 50 Гц\n8–30 Гц",TEAL),("Окно 2 с,\nшаг 0,25 с","скользящее\nокно ЭЭГ",TEAL),
       ("CSP\n(2 диапазона)","мю 8–13 Гц\nбета 13–30 Гц",NAVY),("LDA","вероятности\n4 классов",NAVY),("Решение","среднее 6 окон,\nпорог 80 %",AMBER),("Сканер\nклавиатуры","команда →\nсимвол",CORAL)]
    w=9.7;g=1.5
    for i,(t,s,c) in enumerate(A):
        x=0.8+i*(w+g)
        ax.add_patch(FancyBboxPatch((x,14),w,13,boxstyle="round,pad=0,rounding_size=0.8",fc="white",ec=c,lw=2))
        ax.text(x+w/2,23,t,ha="center",va="center",fontsize=6.9,fontweight="bold",color=c if c!=AMBER else "#9a6a00",linespacing=1.2)
        ax.text(x+w/2,17.4,s,ha="center",va="center",fontsize=6.0,color=MUT,linespacing=1.2)
        if i<6: arrow(ax,(x+w+0.1,20.5),(x+w+g-0.1,20.5),lw=1.5)
    ax.add_patch(FancyBboxPatch((0.8,2),31,9,boxstyle="round,pad=0,rounding_size=0.8",fc=LIGHT,ec=MUT,lw=1,ls="--"))
    ax.text(16.3,6.5,"Калибровка (≈10 мин): по подсказке\nпользователь представляет движения,\nмодель обучается именно на нём",ha="center",va="center",fontsize=6.6,color=INK)
    ax.add_patch(FancyBboxPatch((33.5,2),45.5,9,boxstyle="round,pad=0,rounding_size=0.8",fc=LIGHT,ec=MUT,lw=1,ls="--"))
    ax.text(56.2,6.5,"Защита от ложных команд: порог уверенности,\nусреднение окон, пауза 1 с после команды,\nотбраковка артефактов (моргание, плохой контакт)",ha="center",va="center",fontsize=6.6,color=INK)
    fig.savefig(OUT+"fig_pipeline.png"); plt.close(fig)
# ---- Рис: тракт передачи сигнала
def signal_path():
    fig,ax=canvas(7.4,3.9,80,39)
    P=[("Электроды\nC3 · Cz · C4","сухие, на коже;\nсигнал 10–100 мкВ",TEAL),("Усилитель\nи АЦП","усиление ×24,\n250 отсчётов/с",NAVY),("Модуль связи\nBluetooth LE / USB","пакеты по\n~20 отсчётов",SKY),
       ("SDK / BrainFlow","драйвер\nна ПК",AMBER),("ПО\n«НейроАссистент»","фильтры →\nкоманды",CORAL)]
    w=13.7;g=2.4
    for i,(t,s,c) in enumerate(P):
        x=1+i*(w+g)
        ax.add_patch(FancyBboxPatch((x,22),w,13,boxstyle="round,pad=0,rounding_size=0.9",fc="white",ec=c,lw=2.2))
        ax.text(x+w/2,31,t,ha="center",va="center",fontsize=7.6,fontweight="bold",color=INK,linespacing=1.2)
        ax.text(x+w/2,25.2,s,ha="center",va="center",fontsize=6.8,color=MUT,linespacing=1.2)
        if i<4: arrow(ax,(x+w+0.1,28.5),(x+w+g-0.1,28.5))
    ax.add_patch(Rectangle((1,21),12.6+2.7+12.6+2.7+12.6,0.0))
    ax.text(1,37.6,"В гарнитуре (на голове)",fontsize=8,color=TEAL,fontweight="bold")
    ax.plot([1,1+3*w+2*g],[36.4,36.4],color=TEAL,lw=2)
    ax.text(1+3*(w+g),37.6,"На компьютере",fontsize=8,color=CORAL,fontweight="bold")
    ax.plot([1+3*(w+g),79],[36.4,36.4],color=CORAL,lw=2)
    ax.add_patch(FancyBboxPatch((1,2),78,15,boxstyle="round,pad=0,rounding_size=0.9",fc=LIGHT,ec=MUT,lw=1))
    ax.text(3,14.4,"Что передаётся по каналу связи (пакет данных):",fontsize=7.8,fontweight="bold",color=NAVY,va="center")
    ax.text(3,10.2,"• номер пакета и метка времени;  • по каждому каналу C3, Cz, C4 — число в мкВ, 250 раз в секунду;",fontsize=7.2,color=INK,va="center")
    ax.text(3,6.6,"• индикатор контакта электродов и заряд батареи.  Поток ≈ 2,2 кбайт/с — для Bluetooth это ничтожная нагрузка",fontsize=7.2,color=INK,va="center")
    fig.savefig(OUT+"fig_signal_path.png"); plt.close(fig)
# ---- Рис: кто и как подключает
def roles():
    fig,ax=canvas(7.4,4.1,80,44)
    lanes=[("ИТ-специалист\nтехникума",TEAL),("Педагог /\nспециалист",NAVY),("Пользователь",CORAL),("Помощник\n(родственник)",AMBER)]
    for i,(n,c) in enumerate(lanes):
        y=33-i*10.5
        ax.add_patch(Rectangle((0.5,y),79,9.5,fc=LIGHT if i%2==0 else "white",ec="#c9d4e8",lw=0.8))
        ax.add_patch(Rectangle((0.5,y),12,9.5,fc=c,ec=c)); ax.text(6.5,y+4.75,n,color="white",fontsize=6.3,fontweight="bold",ha="center",va="center",linespacing=1.2)
    def step(lane,col,t,num):
        y=33-lane*10.5+1.2; x=13.8+col*11.0
        box(ax,x,y,10.2,7.1,t,fc="white",ec=lanes[lane][1],fs=5.9,lw=1.5,r=0.5)
        ax.add_patch(Circle((x+0.2,y+7.0),1.15,fc=lanes[lane][1],ec="white")); ax.text(x+0.2,y+7.0,str(num),color="white",fontsize=6.5,ha="center",va="center",fontweight="bold")
    step(0,0,"Установка ПО,\nпроверка связи\nс гарнитурой",1)
    step(1,1,"Выбор гарнитуры,\nпосадка, чистка\nэлектродов",2)
    step(3,1,"Помогает надеть\nгарнитуру",3)
    step(1,2,"Проверка контакта\n(зелёные\nиндикаторы)",4)
    step(2,3,"Калибровка:\nпредставляет\nдвижения ≈10 мин",5)
    step(1,3,"Запускает\nкалибровку,\nследит за метками",6)
    step(2,4,"Тренировка:\nнабор слов,\nигры",7)
    step(1,4,"Подбирает порог,\nпауз, скорость",8)
    step(2,5,"Самостоятельная\nработа за ПК",9)
    step(0,5,"Обновления,\nрезервные копии\nпрофиля",10)
    fig.savefig(OUT+"fig_roles.png"); plt.close(fig)
disability(); principle(); pipeline(); signal_path(); roles()
