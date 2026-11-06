import wave, sys, json, re, numpy as np
def segments(path, thr=-42, gap=0.14):
    w=wave.open(path); sr=w.getframerate(); x=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
    if w.getnchannels()>1: x=x.reshape(-1,w.getnchannels()).mean(1)
    hop=int(sr*0.01); n=len(x)//hop
    db=20*np.log10(np.sqrt((x[:n*hop].reshape(n,hop)**2).mean(1)+1e-12)); sp=db>thr
    segs=[];i=0
    while i<n:
        if sp[i]:
            j=i
            while j<n and sp[j:j+int(gap*100)].any(): j+=1
            segs.append([i/100,j/100]); i=j
        else: i+=1
    return [s for s in segs if s[1]-s[0]>0.12], n/100
def align(phrases, segs, snap=0.4):
    wts=np.array([len(re.sub(r"[\s،؟:.,;!?\-]","",p)) for p in phrases],float)
    cum=np.concatenate([[0],np.cumsum(wts)])/wts.sum()
    dur=np.array([b-a for a,b in segs]); cs=np.concatenate([[0],np.cumsum(dur)]); total=cs[-1]
    def to_abs(sp_t):
        k=np.searchsorted(cs,sp_t,side="right")-1; k=min(k,len(segs)-1)
        return segs[k][0]+(sp_t-cs[k])
    starts=[]
    bounds=[a for a,b in segs]+[segs[-1][1]]
    for i in range(len(phrases)):
        t=to_abs(cum[i]*total)
        cand=min(bounds,key=lambda b:abs(b-t))
        starts.append(cand if abs(cand-t)<=snap else t)
    return starts
if __name__=="__main__":
    segs,D=segments(sys.argv[1]); print(len(segs),D)

import itertools
def align_blocks(blocks, segs, mingap=0.45, snap=0.35, lam=25.0):
    """blocks: list of lists of phrases. Choose block boundaries at big gaps by DP, then align phrases inside each block."""
    wt=lambda p: len(re.sub(r"[\s،؟:.,;!?\-]","",p))
    bw=np.array([sum(wt(p) for p in b) for b in blocks],float); frac=bw/bw.sum()
    dur=np.array([b-a for a,b in segs]); total=dur.sum()
    cs=np.concatenate([[0],np.cumsum(dur)])
    cand=[i+1 for i in range(len(segs)-1) if segs[i+1][0]-segs[i][1]>=mingap]   # boundary before segment index i+1
    K=len(blocks)
    INF=1e18
    # dp[k][j] = best cost with first k blocks ending exactly before candidate j (cand idx), use index into segment list
    pts=[0]+cand+[len(segs)]
    P=len(pts)
    dp=[[INF]*P for _ in range(K+1)]; bk=[[None]*P for _ in range(K+1)]
    dp[0][0]=0
    for k in range(1,K+1):
        for j in range(1,P):
            for i in range(j):
                if dp[k-1][i]>=INF: continue
                sp=cs[pts[j]]-cs[pts[i]]
                gp=(segs[pts[j]][0]-segs[pts[j]-1][1]) if pts[j]<len(segs) else 0.9
                c=dp[k-1][i]+(sp-frac[k-1]*total)**2+lam*max(0,0.9-gp)**2
                if c<dp[k][j]: dp[k][j]=c; bk[k][j]=i
    j=P-1; chain=[j]
    for k in range(K,0,-1):
        j=bk[k][j]; chain.append(j)
    chain=chain[::-1]
    out=[]
    for k,b in enumerate(blocks):
        s0,s1=pts[chain[k]],pts[chain[k+1]]
        sub=segs[s0:s1]
        st=align(b,sub,snap)
        out.append(st)
    return out, [segs[pts[c]][0] if pts[c]<len(segs) else segs[-1][1] for c in chain]


if __name__ == "__main__":
    # usage: python3 align_vo.py <voice.wav> <name>   -> writes <name>_segs.txt (input for run_asr.sh and for your scene timings)
    segs, dur = segments(sys.argv[1])
    name = sys.argv[2] if len(sys.argv) > 2 else "voice"
    open(f"{name}_segs.txt", "w").write(f"{name} {dur:.2f} {len(segs)}\n" + ", ".join(f"{a:.2f}-{b:.2f}" for a, b in segs))
    print(f"{len(segs)} segments, {dur:.2f} s -> {name}_segs.txt")
