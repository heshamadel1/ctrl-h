NB=" "
def c(t,text,ok=None,tag=None,key=None):
    b={"k":"card","t":t,"text":text,"ok":ok}
    if tag:b["tag"]=tag
    if key:b["key"]=key
    return b
DUR,T_END,TAG1,TAG2=40.0,36.0,37.0,38.5
STAGES=["أ","ب","ج"]; TECH=["Next.js","React"]
C4=lambda t:[c(t,"تجهّز حلول للـ"+NB+"Routing"),c(t+.3,"وتفكر في ظهور موقعك في محركات البحث"),c(t+.6,"وتنظم تحميل البيانات"),c(t+.9,"وبيختلف حسب الأدوات")]
SC=[
 dict(style="numbers",t0=0,t1=9,stage=0,head="تلقائي ١",head_t=.1,dims=[5.0],blocks=C4(.5)+[{"k":"corner","abs":True,"t0":.5,"t1":9,"labels":("React","Next.js"),"switch":[4.0]}]),
 dict(style="glass",t0=9,t1=18,stage=1,head="تلقائي ٢",head_t=9.1,blocks=C4(9.5)+[{"k":"note","t":14,"text":"لاحظ: غلطة شائعة"}]),
 dict(style="proposed",t0=18,t1=27,stage=1,head="تلقائي ٣",head_t=18.1,blocks=[dict(b,tag="TAG",key="حلول") for b in C4(18.5)]+[{"k":"chips","abs":True,"t0":23,"t1":27,"items":["Routing","SSR","SSG","RSC"]}]),
 dict(style="classic",t0=27,t1=36,stage=2,head="تلقائي ٤",head_t=27.1,blocks=C4(27.5)),
]
