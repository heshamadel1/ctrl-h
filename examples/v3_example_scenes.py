NB=" "
def c(t,text,ok=None,tag=None,key=None,size=None):
    b={"k":"card","t":t,"text":text,"ok":ok}
    if tag:b["tag"]=tag
    if key:b["key"]=key
    if size:b["size"]=size
    return b
DUR,T_END,TAG1,TAG2=40.0,36.0,37.0,38.5
STAGES=["أ","ب","ج"]; TECH=["Next.js","React"]
SC=[
 dict(style="classic",t0=0,t1=8,stage=0,head="هوك صادم",head_t=0.2,blocks=[
   {"k":"shock","t":0.3,"lines":[("90% بيغلطوا",84,(255,92,92)),("في الحاجة دي",60,(240,240,240))]},
   {"k":"promise","abs":True,"t0":0.5,"t_unlock":30,"t1":33,"locked":"هتعرف السر في الآخر","open":"السر اتفك"}]),
 dict(style="numbers",t0=8,t1=16,stage=1,head="تجربة grid",head_t=8.2,grid="pairs",reserve=170,reserve_reel=230,blocks=[
   c(8.5,"الملفات بتحدد المسارات",True),c(9.5,"من غير Routing كامل",True),c(10.5,"تجهّز حلول كتير"),c(11.5,"وتفكر في الـ"+NB+"SEO"),
   {"k":"button","abs":True,"kind":"subscribe","t0":12.0,"t1":16}]),
 dict(style="glass",t0=16,t1=24,stage=1,head="Tiles",head_t=16.2,grid="tiles",reserve=170,reserve_reel=230,blocks=[
   c(16.5,"Framework على React"),c(17.5,"أدوات جاهزة"),c(18.5,"SSR أو SSG"),
   {"k":"button","abs":True,"kind":"follow","t0":20.0,"t1":24}]),
 dict(style="proposed",t0=24,t1=30,stage=2,head="Strike",head_t=24.2,blocks=[
   {"k":"strike","t":24.5,"t_strike":26,"t_right":26.6,"wrong":"useEffect لكل حاجة","right":"Server Component"}]),
 dict(style="classic",t0=30,t1=36,stage=2,head="Before After",head_t=30.2,blocks=[
   {"k":"ba","t":30.5,"t_slide":32,"before":["useEffect(()=>{","  fetch(url)","},[])"],"after":["const d = await","  fetch(url)",""]}]),
]
