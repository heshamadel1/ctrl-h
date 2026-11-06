# demo of the three blocks added 2026-10-31: icards, steplist, fixcards  (timings are made up for the demo)
DUR, T_END, TAG1, TAG2 = 46.0, 42.0, 43.4, 44.6
STAGES = ["الفكرة", "الأوامر", "الأخطاء"]
TECH = ["Security", "HTTPS", "Email"]
SC = [
 dict(style="classic", t0=0, t1=14, stage=0, head="Zero Trust", head_t=0.2, blocks=[
   {"k": "icards", "t": 0.4, "cols": 3, "items": [
     {"t": 1.0, "title": "Verify Every Request", "icon": "shield", "caption": "جوه ولا برة، اتحقق"},
     {"t": 4.0, "title": "Strong Identity", "icon": "grid", "caption": "اعرف مين بالظبط"},
     {"t": 7.0, "title": "MFA Everywhere", "icon": "bar", "caption": "الباسورد لوحده مش كفاية"},
     {"t": 9.5, "title": "Just-in-Time Access", "icon": "clock", "caption": "أدمن لساعة مش للأبد"},
     {"t": 11.2, "title": "Encrypt Internally", "icon": "lock", "caption": "حتى بين الخدمات"},
     {"t": 12.7, "title": "Continuous Checks", "icon": "nodes", "caption": "الثقة ممكن تتسحب"}]}]),
 dict(style="classic", t0=14, t1=28, stage=1, head="10 أوامر تفحص HTTPS", head_t=14.2, blocks=[
   {"k": "steplist", "t": 14.4, "items": [
     {"name": "curl", "t": 15.0, "file": "status", "lines": [(0.0, "$ curl -sI https://example.com | head -1", 40), (1.6, "HTTP/2 200", 40, "ok")]},
     {"name": "cert", "t": 17.5, "file": "certificate", "lines": [(0.0, "$ echo | openssl s_client -connect example.com:443", 40), (2.0, "Verify return code: 0 (ok)", 40, "ok")]},
     {"name": "expiry", "t": 20.0, "file": "when it expires", "lines": [(0.0, "$ openssl x509 -in cert.pem -noout -enddate", 40), (2.0, "notAfter=Oct 27 23:59:59 2026 GMT", 40, "bad")]},
     {"name": "issuer", "t": 23.0, "file": "who issued it", "lines": [(0.0, "$ openssl x509 -in cert.pem -noout -issuer", 40), (2.0, "issuer=C=US, O=Let's Encrypt", 40)]},
     {"name": "names", "t": 25.0, "file": "names", "lines": [(0.0, "$ openssl x509 -in cert.pem -noout -ext subjectAltName", 40)]},
     {"name": "redirect", "t": 26.2, "file": "redirect"}, {"name": "hsts", "t": 26.8}, {"name": "tls", "t": 27.3},
     {"name": "server", "t": 27.6}, {"name": "caa", "t": 27.8}]}]),
 dict(style="classic", t0=28, t1=42, stage=2, head="أخطاء الإيميل وحلولها", head_t=28.2, blocks=[
   {"k": "fixcards", "t": 28.4, "items": [
     {"t": 28.8, "title": "Reused Password", "sub": "credential stuffing", "chain": ["Old Site Leak", "Bots Try It", "Inbox Opened"], "fix": "الحل: باسورد مختلف من Password Manager"},
     {"t": 33.0, "title": "No 2-Step Login", "sub": "one factor", "chain": ["Password Leak", "No 2nd Check", "Account Taken"], "fix": "الحل: فعّل التحقق بخطوتين أو Passkey"},
     {"t": 37.0, "title": "SMS-Only Codes", "sub": "number hijack", "chain": ["SIM Swap", "Codes Rerouted", "Inbox Taken"], "fix": "الحل: استخدم Authenticator app"},
     {"t": 39.5, "title": "Clicking Login Links", "sub": "phishing", "chain": ["Fake Email", "Lookalike Page", "Password Given"], "fix": "الحل: اكتب الموقع بنفسك"}]}]),
]
KEYS = []; FLOW = []; HITS = []
