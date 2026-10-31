# showcase: every card style, every card shape, every infographic block  (used to make docs/images)
NB=" "
def c(t,text,ok=None,tag=None,key=None):
    b={"k":"card","t":t,"text":text,"ok":ok}
    if tag:b["tag"]=tag
    if key:b["key"]=key
    return b
DUR,T_END,TAG1,TAG2=60.0,56.0,57.0,58.5
STAGES=["Styles","Shapes","Blocks"]; TECH=["Demo"]
def C(t,tag=None,key=None): return [c(t,"استخدم Cache للقراءة الكتير",True,tag,key),c(t+.3,"متخزنش الـ Password كنص",False,tag,key),c(t+.6,"راجع الـ Logs كل يوم",None,tag,key)]
SC=[
 dict(style="classic",t0=0,t1=6,stage=0,head="Style 1 · classic",head_t=.1,blocks=C(.5)),
 dict(style="proposed",t0=6,t1=12,stage=0,head="Style 2 · proposed",head_t=6.1,blocks=C(6.5,"RULE","Cache")),
 dict(style="glass",t0=12,t1=18,stage=0,head="Style 3 · glass",head_t=12.1,blocks=C(12.5)),
 dict(style="numbers",t0=18,t1=24,stage=0,head="Style 4 · numbers",head_t=18.1,blocks=C(18.5)),
 dict(style="classic",t0=24,t1=30,stage=1,head="Shape B · squares",head_t=24.1,grid="squares",blocks=C(24.5)),
 dict(style="classic",t0=30,t1=36,stage=1,head="Shape C · pairs",head_t=30.1,grid="pairs",blocks=C(30.5)),
 dict(style="classic",t0=36,t1=42,stage=1,head="Shape D · narrow",head_t=36.1,cw=0.6,blocks=C(36.5)),
 dict(style="classic",t0=42,t1=46,stage=2,head="Block · icards",head_t=42.1,blocks=[{"k":"icards","t":42.3,"cols":3,"items":[
   {"t":42.5,"title":"Verify Every Request","icon":"shield","caption":"جوه ولا برة، اتحقق"},
   {"t":42.8,"title":"Strong Identity","icon":"key","caption":"اعرف مين بالظبط"},
   {"t":43.1,"title":"MFA Everywhere","icon":"lock","caption":"الباسورد مش كفاية"}]}]),
 dict(style="classic",t0=46,t1=51,stage=2,head="Block · steplist",head_t=46.1,blocks=[{"k":"steplist","t":46.3,"items":[
   {"name":"curl","t":46.6,"file":"status","lines":[(0.0,"$ curl -sI https://example.com | head -1",40),(1.0,"HTTP/2 200",40,"ok")]},
   {"name":"cert","t":48.5,"file":"certificate","lines":[(0.0,"$ openssl s_client -connect example.com:443",40)]},
   {"name":"expiry","t":49.8}]}]),
 dict(style="classic",t0=51,t1=56,stage=2,head="Block · fixcards",head_t=51.1,blocks=[{"k":"fixcards","t":51.3,"items":[
   {"t":51.5,"title":"Reused Password","sub":"credential stuffing","chain":["Old Site Leak","Bots Try It","Inbox Opened"],"fix":"الحل: باسورد مختلف من Password Manager"},
   {"t":53.5,"title":"No 2-Step Login","sub":"one factor","chain":["Password Leak","No 2nd Check","Account Taken"],"fix":"الحل: فعّل التحقق بخطوتين"}]}]),
]
KEYS=[];FLOW=[];HITS=[]
