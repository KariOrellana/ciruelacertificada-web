import re,html,sys
def split_parents(t):
    a=t.index('<div data-elementor-type="wp-page"'); b=t.index('<div data-elementor-type="footer"')
    body=t[a:b]; res=[]
    for m in re.finditer(r'<div class="elementor-element [^"]*e-parent[^"]*"[^>]*>',body):
        s=m.start(); d=0
        for x in re.finditer(r'<div\b|</div>',body[s:]):
            d+= 1 if x.group()=='<div' else -1
            if d==0: res.append((a+s,a+s+x.end())); break
    return res
if __name__=='__main__':
    t=open(sys.argv[1],encoding='utf8').read()
    for i,(s,e) in enumerate(split_parents(t)):
        seg=t[s:e]; tx=re.sub(r'<[^>]+>',' ',re.sub(r'(?s)<(script|style).*?</\1>','',seg)); tx=re.sub(r'\s+',' ',html.unescape(tx)).strip()
        idm=re.search(r' id="([^"]+)"',seg[:600])
        print(i,s,e,e-s,idm.group(1) if idm else '-',tx[:110])
