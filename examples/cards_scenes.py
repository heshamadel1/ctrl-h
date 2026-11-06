NB=" "
def c(t,text,ok=None,tag=None,key=None):
    b={"k":"card","t":t,"text":text,"ok":ok}
    if key:b["key"]=key
    return b
DUR,T_END,TAG1,TAG2=80.0,76.0,77.0,78.5
STAGES=["Styles"]; TECH=["Demo"]
def C(t): return [c(t,"استخدم Cache للقراءة الكتير",True,key="Cache"),c(t+.2,"متخزنش الـ Password كنص",False),c(t+.4,"راجع الـ Logs كل يوم",None)]
SC=[dict(style=s,t0=i*6,t1=i*6+6,stage=0,head="Style · "+s,head_t=i*6+.1,blocks=C(i*6+.4)) for i,s in enumerate(["classic","proposed","glass","numbers","outline","solid","neon","paper","soft","terminal","steps","iconbox"])]
KEYS=[];FLOW=[];HITS=[]
