#!/usr/bin/env python3
"""Genera recursos y auditores del sitio. Uso: python3 tools/build.py  (desde ciruelacertificada-web/)"""
import re,os,glob,json,html,shutil,unicodedata
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE=os.path.join(ROOT,'site'); PDFSRC=os.path.join(ROOT,'material-nuevo')
cfg=json.load(open(os.path.join(ROOT,'content','config.json')))
def norm(s): return re.sub(r'[^a-z0-9]+','-',unicodedata.normalize('NFD',s.lower()).encode('ascii','ignore').decode()).strip('-')
E_=html.escape

# ---------- plantilla: cabecera/pie del sitio ----------
tpl=open(os.path.join(SITE,'estandar-produccion-primaria','index.html'),encoding='utf8').read()
a=tpl.index('<div data-elementor-type="wp-page"'); b=tpl.index('<div data-elementor-type="footer"')
PRE,POST=tpl[:a],tpl[b:]
PRE=PRE.replace(' aria-current="page"','').replace('elementor-item-active','').replace(' current-menu-item','').replace(' current_page_item','')
PRE=re.sub(r'<title>.*?</title>','<title>@@TITLE@@ – Ciruela Certificada</title>',PRE,flags=re.S)
PRE=PRE.replace('</head>','<link rel="stylesheet" href="../assets-nuevos/extra.css">\n</head>',1)

def page(title,body,slug):
    out=os.path.join(SITE,slug); os.makedirs(out,exist_ok=True)
    open(os.path.join(out,'index.html'),'w',encoding='utf8').write(PRE.replace('@@TITLE@@',E_(title))+'<div class="cc-page">'+body+'</div>\n'+POST)

def hero(h1,sub='',btn='',col='#76236C'):
    return f'<section class="cc-hero" style="background:{col}"><div class="cc-wrap"><h1>{E_(h1)}</h1>'+(f'<p>{sub}</p>' if sub else '')+btn+'</div></section>'
def dl(pdf,txt): return f'<p><a class="cc-btn cc-btn--light" href="../wp-content/uploads/2024/11/{pdf}" download>{txt}</a></p>'

# ---------- videos (planilla) ----------
def videos():
    p=os.path.join(PDFSRC,'planilla-ciruela-videos.xlsx')
    import zipfile; z=zipfile.ZipFile(p); wb=z.read('xl/workbook.xml').decode()
    sheets=re.findall(r'<sheet [^>]*name="([^"]+)"',wb)
    t=z.read('xl/worksheets/sheet1.xml').decode()
    rows=[]
    for r in re.findall(r'<row[^>]*>(.*?)</row>',t,flags=re.S):
        cells=[html.unescape(x) for x in re.findall(r'<t[^>]*>([^<]*)</t>',r)]
        if len(cells)>=5 and cells[0]!='Programa': rows.append(cells[:5])
    d={}
    for prog,curso,lec,yt,pag in rows: d.setdefault(norm(curso),[]).append((lec,yt))
    cur={}
    t2=z.read('xl/worksheets/sheet2.xml').decode()
    for r in re.findall(r'<row[^>]*>(.*?)</row>',t2,flags=re.S):
        c=[html.unescape(x) for x in re.findall(r'<t[^>]*>([^<]*)</t>',r)]
        if len(c)>=3 and c[0]!='Programa': cur[norm(c[1])]=c[-1]
    return d,cur
VID,CURSO=videos()

import urllib.parse
# ================= datos de recursos =================
EST=json.load(open(os.path.join(ROOT,'content','estandar.json')))
PP_COL,AA_COL='#2F7D4F','#76236C'
DIM_COLOR={'Ambiente':'#0F7C86','Calidad':'#1F3A5F','Gestión':'#C8203F','Social':'#E8642C','Ética':'#6B6F76'}
DIM_BG={'Ambiente':'#DDF0F1','Calidad':'#E4E9F1','Gestión':'#F8E3E7','Social':'#FCE9DF','Ética':'#ECEDEF'}
def tname(n): return re.sub(r'\s*\(GEI\)','',n)
FMT={'.docx':'Word','.xlsx':'Excel','.pdf':'PDF'}
def mvname(code,stem,ext):
    t=stem.split(' - ',1)[1] if ' - ' in stem else stem
    return code.replace(' ','-')+'_'+norm(re.sub(r'\(final\)','',t))+ext
def mvtitle(stem):
    t=stem.split(' - ',1)[1] if ' - ' in stem else stem
    t=re.sub(r'\s*\(final\)','',t).replace('-',' ').strip(); return t[:1].upper()+t[1:]
def guide_label(fn):
    b=os.path.splitext(fn)[0]
    if re.search(r'gu[ií]a',b,re.I): return 'Guía'
    m=re.search(r'parte-?(\d)',b,re.I); return f'Parte {m.group(1)}' if m else 'Documento'
def tema_resources(folder):
    import hashlib
    full=os.path.join(PDFSRC,'pdf',folder); dest=os.path.join(SITE,'recursos','pdf',folder); os.makedirs(dest,exist_ok=True)
    seen={}
    for f in sorted(os.listdir(full)):
        h=hashlib.md5(open(os.path.join(full,f),'rb').read()).hexdigest()
        if h not in seen or len(f)>len(seen[h]): seen[h]=f   # duplicados idénticos: se queda el de nombre más descriptivo
    files=sorted(seen.values())
    for f in files:
        if not os.path.exists(os.path.join(dest,f)): shutil.copy2(os.path.join(full,f),dest)
    for f in os.listdir(dest):
        if f not in files: os.remove(os.path.join(dest,f))
    isg=lambda f:bool(re.search(r'gu[ií]a',f,re.I))
    guides=[f for f in files if isg(f)]
    def pn(f):
        m=re.search(r'parte-?(\d)',f,re.I); return int(m.group(1)) if m else 99
    parts=sorted([f for f in files if not isg(f)],key=lambda f:(pn(f),f))
    name=cfg['temas'][folder]; vids=VID.get(norm(name),[])
    lec=[]
    for i in range(max(len(parts),len(vids))):
        v=vids[i] if i<len(vids) else ('','')
        t=re.sub(r'^Parte \d+\s*:?\s*','',v[0]).strip()
        lec.append({'n':i+1,'t':t,'v':v[1],'p':f'../recursos/pdf/{folder}/{parts[i]}' if i<len(parts) else ''})
    gl=lambda f:'Guía' if len(guides)==1 else 'Guía: '+re.sub(r'^gu[ií]a-?(de-la-|de-los-|de-|para-la-|para-el-|para-los-|para-)?','',os.path.splitext(f)[0],flags=re.I).replace('-',' ')
    return {'guias':[{'t':gl(f),'h':f'../recursos/pdf/{folder}/{f}'} for f in guides],'lec':lec,'curso':CURSO.get(norm(name),'')}
def build_data():
    data={}
    for std in ('pp','aa'):
        src=os.path.join(PDFSRC,'MV_por_estandar',std.upper()); by={}
        for f in sorted(os.listdir(src)):
            m=re.match(r'((?:PP|AA) \d+) - (.*)\.(docx|xlsx|pdf)$',f)
            if m: by.setdefault(m.group(1),{}).setdefault(f.rsplit('.',1)[0],{})['.'+m.group(3)]=f
        dims={}
        for code in sorted(k for k in EST if k.startswith(std.upper())):
            e=EST[code]; tn=tname(e['tema'])
            tm=dims.setdefault(e['dimension'],{}).setdefault(tn,{'nombre':tn,'mv':[]})
            tm['mv'].append(code)
        out=[]
        for dim,temas in dims.items():
            tl=[]
            for tn,tm in temas.items():
                folder=cfg['tema_carpeta'].get(tn); res=tema_resources(folder) if folder else {'guias':[],'lec':[],'curso':''}
                slug=norm(tn); mv=[]
                for code in tm['mv']:
                    for stem,exts in by.get(code,{}).items():
                        dest=os.path.join(SITE,'mv',std,slug); os.makedirs(dest,exist_ok=True); files=[]
                        for ext in ('.docx','.xlsx','.pdf'):
                            if ext in exts:
                                nm=mvname(code,stem,ext); sp=os.path.join(dest,nm)
                                if not os.path.exists(sp): shutil.copy2(os.path.join(src,exts[ext]),sp)
                                files.append({'f':FMT[ext],'h':f'../mv/{std}/{slug}/{nm}'})
                        mv.append({'c':code,'n':EST[code]['nivel'],'bp':EST[code]['bp'],'t':mvtitle(stem),'a':files})
                tl.append({'t':tn,'mv':mv,**res})
            out.append({'d':dim,'temas':tl})
        data[std]=out
    return data
DATA=build_data()

# ================= página Recursos (filtro dimensión → temática) =================
body=hero('Recursos','Elige el estándar, la dimensión y la temática: te mostramos todo el material en un solo lugar.')+"""
<section class="cc-sec cc-filter"><div class="cc-wrap"><div class="cc-fbar">
<label>Estándar<select id="f-std"></select></label><label>Dimensión<select id="f-dim"></select></label><label>Temática<select id="f-tema"></select></label>
</div></div></section>
<section class="cc-sec cc-sec--alt"><div class="cc-wrap" id="cc-out"></div></section>
<script>
const DATA=@@DATA@@, PDF={pp:"../wp-content/uploads/2024/11/EstandarPP.pdf",aa:"../wp-content/uploads/2024/11/EstandarAA.pdf"};
const COL=@@COL@@, BG=@@BG@@, NAME={pp:"Producción primaria",aa:"Adecuación agroindustrial"};
const q=new URLSearchParams(location.search); let H=location.hash.slice(1), S=q.get("estandar")==="aa"?"aa":"pp", D=q.get("dim"), T=q.get("tema");
const E=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const opt=(v,l,sel)=>`<option value="${E(v)}"${sel?" selected":""}>${E(l)}</option>`;
function render(){
  const dims=DATA[S]; if(!dims.find(x=>x.d===D)) D=dims[0].d;
  const dm=dims.find(x=>x.d===D); if(!dm.temas.find(x=>x.t===T)) T=dm.temas[0].t;
  document.getElementById("f-std").innerHTML=["pp","aa"].map(k=>opt(k,NAME[k],k===S)).join("");
  document.getElementById("f-dim").innerHTML=dims.map(x=>opt(x.d,x.d,x.d===D)).join("");
  document.getElementById("f-tema").innerHTML=dm.temas.map(x=>opt(x.t,x.t,x.t===T)).join("");
  const t=dm.temas.find(x=>x.t===T), c=COL[D];
  let h=`<div class="cc-head" style="--hc:${c}"><span class="cc-tag" style="background:${BG[D]};color:${c}">Dimensión ${E(D)}</span><h2 style="color:${c}">${E(t.t)}</h2><p class="cc-sub">${NAME[S]}</p></div>`;
  h+=`<div class="cc-block"><h3>Estándar</h3><div class="cc-btns"><a class="cc-btn" style="background:${c}" href="${PDF[S]}" target="_blank" rel="noopener">Ver el estándar completo (PDF)</a></div></div>`;
  if(t.guias.length) h+=`<div class="cc-block"><h3>Guía temática</h3><div class="cc-btns">`+t.guias.map(g=>`<a class="cc-btn" style="background:${c}" href="${E(g.h)}" target="_blank" rel="noopener">${E(g.t)} (PDF)</a>`).join("")+`</div></div>`;
  if(t.lec.length) h+=`<div class="cc-block"><h3>Curso en línea</h3><div class="cc-lec">`+t.lec.map(l=>`<div class="cc-les"><span class="cc-n" style="background:${BG[D]};color:${c}">Parte ${l.n}</span><span class="cc-lt">${E(l.t||"")}</span><span class="cc-btns">`+(l.v?`<a class="cc-btn cc-btn--sm cc-btn--o" style="--c:${c}" href="${E(l.v)}" target="_blank" rel="noopener">▶ Video</a>`:"")+(l.p?`<a class="cc-btn cc-btn--sm cc-btn--o" style="--c:${c}" href="${E(l.p)}" target="_blank" rel="noopener">Presentación (PDF)</a>`:"")+`</span></div>`).join("")+`</div>`+(t.curso?`<div class="cc-btns" style="margin-top:14px"><a class="cc-btn" style="background:${c}" href="${E(t.curso)}" target="_blank" rel="noopener">Ir al curso en línea</a></div>`:"")+`</div>`;
  h+=`<div class="cc-block"><h3>Medios de verificación <em>${t.mv.length} documentos</em></h3>`;
  let last="";
  t.mv.forEach(m=>{ if(m.bp!==last){h+=`<p class="cc-bp" style="color:${c}">${E(m.bp)}</p>`;last=m.bp}
    h+=`<div class="cc-mv" id="${m.c.replace(' ','-')}"><span class="cc-code" style="background:${BG[D]};color:${c}">${E(m.c)}</span><span class="cc-lvl">${E(m.n)}</span><span class="cc-mvt">${E(m.t)}</span><span class="cc-btns">`+m.a.map(a=>`<a class="cc-btn cc-btn--sm" style="background:${c}" href="${E(a.h)}" ${a.f==="PDF"?'target="_blank" rel="noopener"':"download"}>${a.f}</a>`).join("")+`</span></div>`;});
  document.getElementById("cc-out").innerHTML=h+"</div>";
  history.replaceState(null,"",`?estandar=${S}&dim=${encodeURIComponent(D)}&tema=${encodeURIComponent(T)}`+(H?"#"+H:""));
  if(H){const el=document.getElementById(H);if(el){el.classList.add("hl");setTimeout(()=>el.scrollIntoView({block:"center"}),50)}H=""}
}
document.getElementById("f-std").onchange=e=>{S=e.target.value;D=null;T=null;render()};
document.getElementById("f-dim").onchange=e=>{D=e.target.value;T=null;render()};
document.getElementById("f-tema").onchange=e=>{T=e.target.value;render()};
render();
</script>""".replace('@@DATA@@',json.dumps(DATA,ensure_ascii=False)).replace('@@COL@@',json.dumps(DIM_COLOR,ensure_ascii=False)).replace('@@BG@@',json.dumps(DIM_BG,ensure_ascii=False))
page('Recursos',body,'recursos')
for old in ('recursos-produccion-primaria','recursos-adecuacion-agroindustrial'):
    shutil.rmtree(os.path.join(SITE,old),ignore_errors=True)


# ================= pasos para la certificación =================
PASOS=[("Adhesión al APL","Sumarte al Acuerdo de Producción Limpia no tiene costo. Cada instalación (predio o planta) se adhiere y se audita por separado, y cuenta con un año para completar el ciclo."),
("Autodiagnóstico inicial","Haz tu autodiagnóstico en la plataforma virtual y conoce tu nivel de cumplimiento. Las acciones que no aplican a tu instalación se marcan como «No cumplo»."),
("Plan de implementación","Elabora un plan sobre las brechas detectadas, con acompañamiento técnico permanente. Si lo necesitas, puedes hacer una auditoría intermedia antes de la final."),
("Auditoría final","Elige a un auditor o auditora acreditado ante la ASCC, que revisa tus medios de verificación, visita tu instalación y elabora el informe."),
("Validación pública","Los organismos públicos validadores del APL revisan los informes. Las aclaraciones y correcciones se gestionan con la ASCC, en un plazo de 90 días."),
("Certificación ASCC","Obtienes tu certificado por 1, 2 o 3 años, según el nivel alcanzado. Al vencer, se renueva repitiendo el autodiagnóstico y la auditoría.")]
QUIEN=[("Auditores y auditoras","Profesionales independientes acreditados ante la ASCC. Revisan el autodiagnóstico, visitan tu instalación y elaboran el informe de auditoría.","#76236C"),
("ASCC","La Agencia de Sustentabilidad y Cambio Climático acredita a los auditores, gestiona las aclaraciones con los servicios públicos y entrega la certificación.","#1F3A5F"),
("ODEPA · Chile Origen Consciente","Certificarse en el APL es requisito para obtener luego la distinción Chile Origen Consciente, el programa de ODEPA del Ministerio de Agricultura.","#2F7D4F")]
def block_pasos():
    steps=''.join(f'<li class="cc-st"><span class="cc-stn">{i+1}</span><h3>{E_(a)}</h3><p>{E_(b)}</p></li>' for i,(a,b) in enumerate(PASOS))
    who=''.join(f'<div class="cc-who" style="--c:{c}"><h3>{E_(a)}</h3><p>{E_(b)}</p></div>' for a,b,c in QUIEN)
    return f'''<section class="cc-sec" id="pasos"><div class="cc-wrap"><h2>Pasos para la certificación</h2>
<p class="cc-lead">Así es el camino para certificar tu predio o tu planta, desde la autoevaluación hasta la renovación.</p>
<ol class="cc-tl-steps">{steps}</ol>
<h3 class="cc-sub-h">¿Quién certifica?</h3><div class="cc-whos">{who}</div>
<div class="cc-btns cc-cta"><a class="cc-btn" href="{cfg['formulario_url']}" target="_blank" rel="noopener">Quiero iniciar mi certificación</a><a class="cc-btn cc-btn--pdf" href="./auditores/">Ver información para auditores</a></div></div></section>'''
def block_empresas():
    e=cfg['empresas']
    def it(std,pct,lbl):
        c=STDCOL[std]
        return f'<div class="cc-es" style="--c:{c}"><span class="cc-es-tag">{STDNAME[std]}</span><strong><i data-count="{pct}" data-dec="1">{str(pct).replace(".",",")}</i>%</strong><span class="cc-es-l">{lbl}</span></div>'
    return f'''<section class="cc-emp cc-emp--s" id="empresas-certificadas"><div class="cc-wrap"><div class="cc-ess cc-anim2">{it('aa',e['aa']['pct'],'de representatividad de las empresas certificadas')}<span class="cc-es-div"></span>{it('pp',e['pp']['pct'],'de representatividad de las empresas adheridas')}</div></div>
<script>(function(){{var r=document.querySelector('.cc-anim2');if(!r||!('IntersectionObserver' in window))return;function run(){{r.querySelectorAll('[data-count]').forEach(function(el){{var to=parseFloat(el.dataset.count),d=+el.dataset.dec,t0=null;function f(t){{t0=t0||t;var k=Math.min((t-t0)/1300,1);el.textContent=(to*k).toFixed(d).replace('.',',');if(k<1)requestAnimationFrame(f)}}requestAnimationFrame(f)}})}}new IntersectionObserver(function(x,o){{if(x[0].isIntersecting){{o.disconnect();run()}}}},{{threshold:.4}}).observe(r)}})();</script></section>'''

# ================= página Auditores =================
def aud_page():
    A=cfg['auditores']
    pasos=''.join(f'<div class="cc-ap"><span class="cc-stn">{i+1}</span><h3>{E_(a)}</h3><p>{E_(b)}</p></div>' for i,(a,b) in enumerate(A['pasos']))
    reqs=''.join(f'<div class="cc-rq"><h3>{E_(a)}</h3><p>{E_(b)}</p></div>' for a,b in A['requisitos'])
    inh=''.join(f'<li>{E_(x)}</li>' for x in A['inhabilidades'])
    return hero('Auditores',A['intro'])+f'''
<section class="cc-sec"><div class="cc-wrap"><h2>¿Cómo ser auditor o auditora del programa?</h2><div class="cc-aps">{pasos}</div></div></section>
<section class="cc-sec cc-sec--alt"><div class="cc-wrap"><h2>Requisitos para inscribirte en el Registro</h2><p class="cc-lead">{E_(A['req_intro'])}</p><div class="cc-rqs">{reqs}</div></div></section>
<section class="cc-sec cc-sec--alt"><div class="cc-wrap"><h2>Inhabilidades de un auditor</h2><p class="cc-lead">{E_(A['inh_intro'])}</p><ul class="cc-ul cc-ul--x">{inh}</ul>
<div class="cc-btns cc-cta"><a class="cc-btn" href="{cfg['formulario_url']}" target="_blank" rel="noopener">Quiero ser auditor o auditora</a></div></div></section>'''

page('Auditores',aud_page(),'auditores')
# ================= bloques de diseño (estilo del estándar) =================
def temas_por_dim(std):
    d={}
    for code in sorted(k for k in EST if k.startswith(std.upper())):
        e=EST[code]; l=d.setdefault(e['dimension'],[]); n=tname(e['tema'])
        if n not in l: l.append(n)
    return d
STDURL={'pp':'estandar-produccion-primaria','aa':'estandar-adecuacion-agroindustrial'}
STDNAME={'pp':'Producción primaria','aa':'Adecuación agroindustrial'}
STDCOL={'pp':PP_COL,'aa':AA_COL}
def nacc(std,dim=None,tema=None): return sum(1 for k,e in EST.items() if k.startswith(std.upper()) and (dim is None or e['dimension']==dim) and (tema is None or tname(e['tema'])==tema))
def dim_collapsibles(std,base):
    out=''
    for dim,temas in temas_por_dim(std).items():
        links=''.join(f'<a class="cc-tl" style="border-color:{DIM_COLOR[dim]};color:{DIM_COLOR[dim]}" href="{base}{STDURL[std]}/#{std}-{norm(t)}">{E_(t)}<small>{nacc(std,dim,t)} acciones</small></a>' for t in temas)
        out+=f'<details class="cc-dd" style="--c:{DIM_COLOR[dim]};--b:{DIM_BG[dim]}"><summary>Dimensión {E_(dim)}<em>{len(temas)} temática{"s" if len(temas)>1 else ""} · {nacc(std,dim)} acciones</em></summary><div class="cc-tls">{links}</div></details>'
    return out
def block_consiste(base):
    cols=''.join(f'<div><h3 class="cc-h3" style="color:{STDCOL[s]}">{STDNAME[s]}<em>{sum(len(v) for v in temas_por_dim(s).values())} temáticas · {nacc(s)} acciones</em></h3>{dim_collapsibles(s,base)}</div>' for s in ('pp','aa'))
    return f'''<section class="cc-sec cc-wrapw" id="en-que-consiste"><div class="cc-wrap"><h2>¿En qué consiste?</h2>
<p class="cc-lead">Los estándares agrupan sus acciones en <strong>temáticas</strong>, ordenadas en <strong>5 dimensiones</strong>. Abre una dimensión y elige una temática para revisar sus acciones.</p>
<div class="cc-two">{cols}</div>
<div class="cc-btns cc-cta"><a class="cc-btn" href="#estandares">Ver estándares</a><a class="cc-btn cc-btn--pdf" href="#niveles-de-clasificacion">Ver niveles de clasificación</a></div></div></section>'''
def block_niveles():
    lv=[('Fundamental','5 puntos','#DCE6F5','#1F3A5F','Acciones muy relevantes para calificar a una empresa como sustentable, sin importar su complejidad. Su nivel de obligatoriedad es mayor que el del resto.'),
        ('Básico','2 puntos','#FDF3C9','#8A6D00','Acciones con menor impacto para la sustentabilidad y menor complejidad de implementación.'),
        ('Intermedio','3 puntos','#E3F1D9','#3C7A22','Acciones con impacto e implementación de complejidad intermedia.'),
        ('Avanzado','4 puntos','#FCE3D6','#B24A16','Acciones con mayor impacto para la sustentabilidad y mayor complejidad de implementación.')]
    cards=''.join(f'<div class="cc-lv" style="background:{b}"><span class="cc-pts" style="color:{c}">{p}</span><h4 style="color:{c}">{n}</h4><p>{d}</p></div>' for n,p,b,c,d in lv)
    return f'''<section class="cc-sec cc-sec--alt" id="niveles-de-clasificacion"><div class="cc-wrap"><h2>Niveles de clasificación</h2>
<p class="cc-lead">Cada acción se clasifica en 4 niveles y suma un puntaje según su priorización. Una empresa obtiene su puntaje según las acciones que cumple al momento de la auditoría.</p><div class="cc-lvgrid">{cards}</div></div></section>'''

def banner(opt,base):
    F=cfg['formulario_url']; pp=base+'assets-nuevos/agente-pp.png'; aa=base+'assets-nuevos/agente-aa.png'; ph=base+'assets-nuevos/agente.jpg'
    def btn(label,cls='cc-btn--w',col='#76236C'): return f'<a class="cc-btn {cls}" style="color:{col}!important" href="{F}" target="_blank" rel="noopener">{label}</a>'
    if opt=='a':
        card=lambda img,nm,sub,c:f'<div class="cc-ac"><img src="{img}" alt="Agente {nm}"><h3 style="color:{c}">Agente {nm}</h3><p>{sub}</p>{btn("Hablar con el agente","",c).replace("cc-btn ","cc-btn cc-btn--c ").replace("color:"+c+"!important","background:"+c+";color:#fff!important")}</div>'
        return f'<section class="cc-bn cc-bn-a"><div class="cc-wrap cc-bn-grid"><div class="cc-bn-t"><small>TE APOYAMOS EN TU CERTIFICACIÓN</small><h2>Agentes virtuales por WhatsApp</h2><p>Resuelve tus dudas con orientación basada en el contenido oficial de cada estándar, cuando lo necesites.</p></div><div class="cc-acs">{card(pp,"de Producción primaria","Fruta fresca en el huerto","#2F7D4F")}{card(aa,"de Adecuación agroindustrial","Planta deshidratadora","#76236C")}</div></div></section>'
    if opt=='b':
        bub=lambda img,txt,c:f'<div class="cc-chat"><img src="{img}" alt=""><div class="cc-bub" style="border-color:{c}"><b style="color:{c}">{txt[0]}</b><span>{txt[1]}</span></div></div>'
        return f'<section class="cc-bn cc-bn-b"><div class="cc-wrap cc-bn-grid"><div class="cc-bn-t"><small style="color:#76236C">TE APOYAMOS EN TU CERTIFICACIÓN</small><h2 style="color:#222">¿Dudas? Escríbele a nuestros agentes virtuales</h2><p style="color:#444">Respuestas basadas en el contenido oficial del estándar, por WhatsApp.</p>{btn("Hablar con el agente","","#fff")}</div><div class="cc-phone"><div class="cc-phh">WhatsApp</div>{bub(pp,("Agente Producción primaria","Hola 👋 Soy el agente del estándar de Producción primaria. ¿En qué te ayudo?"),"#2F7D4F")}{bub(aa,("Agente Adecuación agroindustrial","Hola 👋 Soy el agente del estándar de Adecuación agroindustrial. ¿Qué necesitas saber?"),"#76236C")}</div></div></section>'
    if opt=='c':
        return f'<section class="cc-bn cc-bn-c"><div class="cc-wrap cc-bn-grid"><div class="cc-pic"><img src="{ph}" alt="Productor consultando el agente virtual"><img class="cc-m1" src="{pp}" alt=""><img class="cc-m2" src="{aa}" alt=""></div><div class="cc-bn-t"><small>TE APOYAMOS EN TU CERTIFICACIÓN</small><h2>Resuelve tus dudas con nuestros agentes virtuales</h2><p>Orientación basada en el contenido oficial del estándar, por WhatsApp.</p><div class="cc-ags2"><a class="cc-ag2 cc-ag2-pp" href="{F}" target="_blank" rel="noopener"><img src="{pp}" alt=""><span>Agente<br><b>Producción primaria</b></span></a><a class="cc-ag2 cc-ag2-aa" href="{F}" target="_blank" rel="noopener"><img src="{aa}" alt=""><span>Agente<br><b>Adecuación agroindustrial</b></span></a></div></div></div></section>'
    return f'<section class="cc-bn cc-bn-d"><div class="cc-wrap cc-bn-d-in"><a class="cc-d1" href="{F}" target="_blank" rel="noopener"><img src="{pp}" alt=""><span><b>Agente PP</b>Producción primaria</span></a><div class="cc-d2"><small>TE APOYAMOS EN TU CERTIFICACIÓN</small><h2>Agentes virtuales por WhatsApp</h2><p>Resuelve tus dudas con orientación basada en el contenido oficial del estándar.</p></div><a class="cc-d3" href="{F}" target="_blank" rel="noopener"><img src="{aa}" alt=""><span><b>Agente AA</b>Adecuación agroindustrial</span></a></div></section>'

def block_periodos():
    def track(marks,final,c,label,sub):
        ms=''.join(f'<div class="cc-mk" style="left:{p}%;--c:{c}"><i></i><span>{l}</span></div>' for p,l in marks)
        return f'<div class="cc-pb"><div class="cc-bl"><span>{label}</span><small>{sub}</small></div><div class="cc-pbar"><div class="cc-track"><div class="cc-fill" style="--p:{final}%;background:{c}"></div></div>{ms}</div></div>'
    def col(s,gen):
        c=STDCOL[s]
        f=track([(80,'80%')],80,c,'Acciones fundamentales','Necesitas cumplir al menos el 80% del puntaje')
        g=track([(g_,f'{y} · {g_}%') for y,g_ in gen],gen[-1][1],c,'Acciones generales','Cada hito alcanzado suma un año de certificación')
        return f'<div class="cc-pcard" style="border-top-color:{c}"><h3 style="color:{c}">{STDNAME[s]}</h3>{f}{g}</div>'
    pp=[('1 año',20),('2 años',40),('3 años',60)]; aa=[('1 año',40),('2 años',60),('3 años',80)]
    def wabtn(std,label,url,col,fg,bd):
        icon='<svg viewBox="0 0 32 32" width="34" height="34" aria-hidden="true"><circle cx="16" cy="16" r="16" fill="#25D366"/><path fill="#fff" d="M16 7a9 9 0 0 0-7.7 13.6L7 25l4.5-1.2A9 9 0 1 0 16 7zm4.7 12.3c-.2.6-1.2 1.1-1.7 1.2-.4.1-1 .1-1.6-.1-.4-.1-.9-.3-1.5-.6-2.6-1.1-4.3-3.8-4.4-4-.1-.2-1-1.3-1-2.5s.6-1.8.9-2c.2-.2.5-.3.7-.3h.5c.2 0 .4 0 .6.5l.8 2c.1.2.1.3 0 .5l-.3.5-.4.4c-.1.2-.3.3-.1.6.2.3.7 1.2 1.5 1.9 1 .9 1.9 1.2 2.2 1.3.3.1.4.1.6-.1l.8-1c.2-.2.4-.2.6-.1l1.9.9c.3.1.5.2.5.3.1.2.1.8-.1 1.4z"/></svg>'
        return f'<a class="cc-ag" style="background:{col};color:{fg};border-color:{bd}" href="{url}" target="_blank" rel="noopener"><span class="cc-agico">{icon}<b style="background:{fg};color:{col}">{std}</b></span><span>{label}</span></a>'
    wpp=cfg.get('whatsapp_pp_url') or cfg['formulario_url']; waa=cfg.get('whatsapp_aa_url') or cfg['formulario_url']
    return f'''<section class="cc-sec" id="periodos"><div class="cc-wrap"><h2>Periodos de certificación</h2>
<p class="cc-lead">Para certificarte debes cumplir dos cosas: <strong>(1)</strong> el 80% del puntaje de las acciones fundamentales y <strong>(2)</strong> un porcentaje del puntaje de las acciones generales (básicas, intermedias y avanzadas). <strong>Mientras más acciones generales cumples, por más años te certificas.</strong></p>
<div class="cc-two cc-anim">{col('pp',pp)}{col('aa',aa)}</div></div>
<script>(function(){{var e=document.querySelector('.cc-anim');if(!e||!('IntersectionObserver' in window))return;e.classList.add('cc-wait');new IntersectionObserver(function(x,o){{if(x[0].isIntersecting){{e.classList.remove('cc-wait');o.disconnect()}}}},{{threshold:.3}}).observe(e)}})();</script></section>
{block_pasos()}{banner(cfg.get('banner','a'),'./')}'''
def block_estandares(base,PLAT):
    def card(std,n,img):
        col=STDCOL[std]; nm=STDNAME[std]
        return f'''<div class="cc-scard" style="background-image:linear-gradient({col}d9,{col}d9),url('{base}wp-content/uploads/2024/03/{img}')"><div><small>ESTÁNDAR DE SUSTENTABILIDAD</small><h3>{nm}</h3><p>La propuesta de estándar para la fase de {nm} cuenta con {n} acciones.</p></div>
<div class="cc-btns"><a class="cc-btn cc-btn--w" style="color:{col}!important" href="{base}{STDURL[std]}/">Ver estándar</a><a class="cc-btn cc-btn--ow" href="{base}recursos/?estandar={std}">Ver recursos</a></div></div>'''
    return f'''<section class="cc-scards" id="estandares">{card('pp',nacc('pp'),'Estandar-de-sustentabilidad-de-produccion-primaria-min-1-1.jpg')}{card('aa',nacc('aa'),'Estandar-de-sustentabilidad-de-adecuacion-industrial-min-1.jpg')}</section>'''
def fmt_txt(s):
    lines=[l.strip() for l in (s or '').split('\n') if l.strip()]; out=''; ul=False
    for l in lines:
        if l.startswith('-'):
            if not ul: out+='<ul>'; ul=True
            out+=f'<li>{E_(l.lstrip("- "))}</li>'
        else:
            if ul: out+='</ul>'; ul=False
            out+=f'<p>{E_(l)}</p>'
    return out+('</ul>' if ul else '')
def block_std(std,base):
    col=STDCOL[std]; nm=STDNAME[std]; nt=sum(len(v) for v in temas_por_dim(std).values()); out=''
    for dim,temas in temas_por_dim(std).items():
        inner=''
        for tn in temas:
            bps={}
            for code in sorted(k for k in EST if k.startswith(std.upper()) and EST[k]['dimension']==dim and tname(EST[k]['tema'])==tn): bps.setdefault(EST[code]['bp'],[]).append(code)
            body=''
            for bp,codes in bps.items():
                body+=f'<h4 class="cc-bph">{E_(bp)}</h4>'
                for c in codes:
                    e=EST[c]; cid=c.replace(' ','-')
                    body+=f'<div class="cc-act" id="{cid}"><div class="cc-acth"><span class="cc-code" style="background:{DIM_BG[dim]};color:{DIM_COLOR[dim]}">{c}</span><span class="cc-lvl">{E_(e["nivel"])}</span></div><div class="cc-atxt">{fmt_txt(e["accion"])}</div><p class="cc-amv"><strong>Medio de verificación:</strong> {E_(e["mv"])}</p><a class="cc-link" style="color:{DIM_COLOR[dim]}" href="{base}recursos/?estandar={std}&amp;dim={urllib.parse.quote(dim)}&amp;tema={urllib.parse.quote(tn)}#{cid}">Ver los recursos de esta acción →</a></div>'
            inner+=f'<details class="cc-td" id="{std}-{norm(tn)}"><summary>{E_(tn)}<em>{nacc(std,dim,tn)} acciones</em></summary>{body}</details>'
        out+=f'<details class="cc-dd cc-dd--big" style="--c:{DIM_COLOR[dim]};--b:{DIM_BG[dim]}"><summary>Dimensión {E_(dim)}<em>{len(temas)} temática{"s" if len(temas)>1 else ""} · {nacc(std,dim)} acciones</em></summary><div class="cc-tdw">{inner}</div></details>'
    js="<script>function ccOpen(){var id=location.hash.slice(1);if(!id)return;var el=document.getElementById(id);if(!el)return;for(var n=el;n;n=n.parentElement){if(n.tagName==='DETAILS')n.open=true}setTimeout(function(){el.scrollIntoView({block:'start'})},50)}addEventListener('hashchange',ccOpen);ccOpen();</script>"
    return hero(nm,f'Estándar de sustentabilidad para la industria de ciruelas deshidratadas · {nt} temáticas · {nacc(std)} acciones',col=col)+f'<section class="cc-sec"><div class="cc-wrap"><p class="cc-lead">Abre una dimensión y luego una temática para ver sus acciones, con su nivel y su medio de verificación. En cada acción encontrarás un enlace a sus recursos.</p>{out}<div class="cc-btns cc-cta"><a class="cc-btn" href="{base}recursos/?estandar={std}">Ver todos los recursos</a></div></div></section>{js}'


def _p(s): return '<p>'+E_(s)+'</p>'
def _ul(items): return '<ul>'+''.join('<li>'+E_(i)+'</li>' for i in items)+'</ul>'
def _tbl(head,rows): return '<div class="cc-tbl cc-tbl--s"><table><thead><tr>'+''.join(f'<th>{E_(h)}</th>' for h in head)+'</tr></thead><tbody>'+''.join('<tr>'+''.join(f'<td>{E_(c)}</td>' for c in r)+'</tr>' for r in rows)+'</tbody></table></div>'
def _flow(items): return '<div class="cc-flow">'+'<span class="cc-fa">→</span>'.join(f'<span class="cc-fs"><b>{i+1}</b>{E_(x)}</span>' for i,x in enumerate(items))+'</div>'
FAQ_CATS=[
("El proceso y sus plazos","proceso",[
 ("¿Cuáles son las etapas del proceso de certificación?",_flow(["Adhesión al APL","Autodiagnóstico inicial","Plan de implementación","Auditoría final","Validación pública","Certificación ASCC"])),
 ("¿Cuánto tiempo toma el proceso completo?",_p("Cada empresa cuenta con un año desde la adhesión al APL para completar el ciclo. El cronograma se adapta a los ciclos productivos de cada empresa, que avanza a su propio ritmo hasta la solicitud de auditoría.")),
 ("¿Cuántas horas de dedicación requiere?",_p("Depende del equipo de cada empresa. El tiempo se minimiza con la orientación permanente del equipo técnico y la plataforma virtual, cuyo agente con IA resuelve dudas sobre los medios de verificación."))]),
("El estándar y sus niveles de certificación","estandar",[
 ("¿Qué contiene el estándar de sustentabilidad?",_tbl(["Estándar","Alcance","Acciones","Temáticas"],[["Adecuación agroindustrial","Plantas de proceso","135","12"],["Producción primaria","Predios (huertos)","129","13 (incluye suelo)"]])+_p("Ambos se organizan en 5 dimensiones (Ambiente, Calidad, Ética, Gestión y Social) y sus acciones se clasifican en fundamentales (5 puntos), básicas (2), intermedias (3) y avanzadas (4).")),
 ("¿Cómo se calcula el puntaje y qué niveles de certificación existen?",_tbl(["Certificación","Agroindustria (máx. 445 pts)","Producción primaria (máx. 459 pts)"],[["1 año","80% fundamentales + 40% generales","80% fundamentales + 20% generales"],["2 años","80% fundamentales + 60% generales","80% fundamentales + 40% generales"],["3 años","80% fundamentales + 80% generales","80% fundamentales + 60% generales"]])),
 ("Además del puntaje, ¿qué otros requisitos del APL debo cumplir?",_ul(["Designar a una persona encargada del APL y su suplente.","Aprobar los cursos del estándar disponibles en Chile Agrícola.","Participar en las capacitaciones dictadas con apoyo de los organismos firmantes.","Reportar a Chileprunes los indicadores de sustentabilidad."])+_p("El auditor o auditora evalúa estos requisitos en su informe.")),
 ("¿Cómo accedo a las capacitaciones y cursos exigidos?",_p("En la plataforma Chile Agrícola del Ministerio de Agricultura, en las capacitaciones que dicta el proyecto con apoyo de los organismos firmantes y en los recursos de ciruelacertificada.cl.")),
 ("¿Sirven las capacitaciones que mi equipo ya realizó con otras instituciones?",_p("Sí: se aceptan certificados de capacitación externa (cursos, seminarios, congresos) con antigüedad no mayor a 3 años. Las capacitaciones internas requieren registro de ejecución (asistencia, tema, relator o relatora y material).")),
 ("¿Qué relación tiene esta certificación con Chile Origen Consciente (ChOC)?",_p("ChOC es un programa de ODEPA (Ministerio de Agricultura) que posiciona la sustentabilidad como valor diferenciador de los alimentos chilenos. Certificarse en el APL es requisito para obtener luego la distinción ChOC."))]),
("Costos y contratación de la auditoría","costos",[
 ("¿Cuánto cuesta certificarse?",_p("El único pago directo es la auditoría, por instalación. Los demás apoyos del proyecto no implican pagos, aunque sí horas de dedicación del equipo de cada empresa.")),
 ("¿Quién define el precio de la auditoría?",_p("Cada auditor o auditora acreditado, según distancia, tamaño de predios y plantas, y número de instalaciones. El precio final se negocia directamente entre empresa y auditor; Chileprunes–IICA no interviene.")),
 ("¿Cómo contrato a un auditor o auditora?",_p("Los valores se presentan en una oferta pública de precios disponible para todas las empresas. Cada una elige a su auditor y acuerda con él o ella las condiciones finales.")),
 ("¿Quiénes son los auditores y qué hacen?",_p("Profesionales independientes acreditados ante la ASCC, cuyo trabajo entrega un respaldo verificable ante los mercados. Sus tareas:")+_ul(["Revisar el autodiagnóstico y preparar la auditoría.","Realizar la visita en terreno y revisar los medios de verificación.","Elaborar el informe en los formatos oficiales.","Gestionar correcciones y aclaratorias ante los servicios públicos."])),
 ("¿La adhesión al APL tiene costo?",_p("No. Sumarse al APL no tiene costo de inscripción.")),
 ("¿Qué apoyos incluye el proyecto?",_ul(["Acompañamiento técnico permanente del equipo Chileprunes–IICA.","Reuniones virtuales de seguimiento para preparar la auditoría.","Capacitaciones en el modelo de certificación y sus contenidos.","Plataforma virtual con IA (ciruelacertificada.cl) para medios de verificación y dudas.","Insumos físicos: manuales y señaléticas."]))]),
("Requisitos y alcance","alcance",[
 ("¿Qué se entiende por «instalación»?",_p("Una unidad física y operativa de producción, delimitada geográficamente y bajo una misma administración: superficies, infraestructura, bodegas, caminos internos y fuentes de agua. Cada instalación se adhiere y se audita por separado.")),
 ("¿Qué pasa si tengo más de una instalación o varios huertos?",_p("La auditoría y su valor se determinan por cada instalación. El trabajo corporativo se simplifica: los manuales, insumos y capacitaciones del proyecto sirven para todas las sedes.")),
 ("Si certifico mi planta, ¿quedan cubiertos también los huertos de mis proveedores?",_p("No. Cada fase tiene su estándar: Adecuación agroindustrial (plantas) y Producción primaria (predios). Para que el sello llegue al producto final, las plantas necesitan fruta de predios certificados.")),
 ("¿Existe un tamaño mínimo de predio para participar?",_p("No. Distintas escalas productivas pueden implementarlo sin barreras de entrada por tamaño o volumen.")),
 ("¿Puedo usar el sello en mis envases y material comercial una vez certificado?",_p("No por el momento: se requiere predio y planta certificados, y aún falta implementar la cadena de custodia. Mientras tanto, el certificado de cumplimiento es el respaldo verificable ante los mercados."))]),
("Implementación y auditoría","implementacion",[
 ("¿Qué pasa si el autodiagnóstico arroja brechas muy grandes?",_p("Se elabora un plan de implementación sobre las brechas detectadas y puede hacerse una auditoría intermedia antes de la auditoría final. Las reuniones virtuales de seguimiento del proyecto apoyan todo el proceso.")),
 ("¿Puedo usar mis propios registros y formatos como medios de verificación?",_p("Sí, si contienen la información mínima que detalla el medio de verificación de cada acción. En la sección Recursos hay formatos tipo referenciales listos para usar.")),
 ("¿Qué pasa si una acción del estándar no aplica a mi instalación?",_p("Debe marcarse como «No cumplo» en el autodiagnóstico. El puntaje se construye únicamente con las acciones efectivamente implementadas y evidenciadas.")),
 ("Si surgen observaciones tras la auditoría, ¿qué sucede?",_flow(["Informes por instalación","Chileprunes","ASCC: aclaraciones y correcciones","Organismos públicos: 90 días","Certificación"])+_p("Las consultas u observaciones se responden con apoyo de la empresa y del auditor o auditora, según corresponda."))]),
("Plataforma e información","plataforma",[
 ("¿Es confidencial la información que subo a la plataforma?",_p("Sí. El manejo de la información es confidencial y los medios de verificación se utilizan exclusivamente para el proceso de certificación.")),
 ("¿Quién revisa los datos y el informe de auditoría?",_p("El auditor o auditora seleccionado procesa los datos y el informe final; luego solo los organismos validadores del APL (servicios públicos firmantes del acuerdo) los revisan para asegurar el cumplimiento.")),
 ("¿Qué pasa si mi equipo no es hábil con la tecnología?",_p("La plataforma está diseñada con foco en la usabilidad y su agente virtual resuelve dudas de forma intuitiva, sin requerir conocimientos avanzados. El equipo técnico también orienta en su uso."))]),
("Pequeños productores y agricultores","pequenos",[
 ("Tengo un solo huerto y le vendo mi fruta a una planta procesadora. ¿Puedo certificarme?",_p("Sí. El estándar es inclusivo con distintas escalas productivas: el predio se adhiere al APL como una instalación y sigue el mismo proceso.")),
 ("¿Necesito contratar asesores externos para implementar el estándar?",_p("No es necesario: el proyecto incluye, sin pago, acompañamiento técnico permanente, reuniones virtuales de seguimiento, capacitaciones y una plataforma virtual que guía el proceso paso a paso.")),
 ("¿El estándar me exige hacer inversiones en infraestructura o equipamiento?",_p("El estándar es voluntario y flexible: cada empresa elige qué acciones incluir. La mayoría son prácticas de gestión, registros y capacitaciones; las inversiones aparecen sobre todo en acciones avanzadas, que no son obligatorias para certificar.")),
 ("¿Puedo agruparme con otros productores para compartir el costo de la auditoría?",_p("No existen esquemas asociativos para el pago de la auditoría: cada instalación se audita individualmente y cada empresa negocia y paga directamente a su auditor o auditora.")),
 ("¿Qué pasa si no apruebo la auditoría? ¿Pierdo lo que pagué?",_p("El proceso está diseñado para llegar preparado: plan de implementación y auditoría intermedia previa a la auditoría final.")),
 ("¿Qué beneficio concreto obtengo al certificarme?",_p("Ya existen plantas certificadas que necesitan fruta de huertos certificados para llevar el sello al producto final, además del respaldo verificable que diferencia a la fruta ante mercados cada vez más exigentes.")),
 ("¿Cada cuánto tiempo debo renovar la certificación?",_p("Según el nivel alcanzado, el certificado tiene una vigencia de 1, 2 o 3 años. Al vencer, se renueva repitiendo el autodiagnóstico y la auditoría."))])]
WA='https://wa.me/56942873202'
def _faq_item(q,a): return f'<details class="cc-fq"><summary>{E_(q)}</summary><div class="cc-fa-body">{a}</div></details>'
def block_faq():
    pick=[("proceso",0),("proceso",1),("costos",0),("costos",3),("alcance",3),("pequenos",6)]
    d={k:v for _,k,v in FAQ_CATS}
    items=''.join(_faq_item(*d[k][i]) for k,i in pick)
    return f'<section class="cc-sec cc-sec--alt" id="preguntas-frecuentes"><div class="cc-wrap"><h2>Preguntas frecuentes</h2><p class="cc-lead">Respuestas rápidas sobre el proceso de certificación, sus plazos y sus costos.</p><div class="cc-fqs">{items}</div><div class="cc-btns cc-cta"><a class="cc-btn" href="./preguntas-frecuentes/">Ver todas las preguntas frecuentes</a></div></div></section>'
def faq_page():
    nav=''.join(f'<a class="cc-chipn" href="#{k}">{E_(c)}</a>' for c,k,_ in FAQ_CATS)
    body=''.join(f'<section class="cc-faqcat" id="{k}"><h2 class="cc-faqh">{E_(c)}</h2>'+''.join(_faq_item(q,a) for q,a in qs)+'</section>' for c,k,qs in FAQ_CATS)
    return hero('Preguntas frecuentes','Certificación del Estándar de Sustentabilidad de la Ciruela Deshidratada · Documento oficial, agosto 2026')+f'<section class="cc-sec"><div class="cc-wrap"><div class="cc-chipsn">{nav}</div><div class="cc-fqs cc-fqs--w">{body}</div><div class="cc-ask"><h3>¿Tienes otra pregunta?</h3><p>Escríbele a Francisca Sepúlveda por WhatsApp al +56 9 4287 3202 o déjanos tus datos en el formulario.</p><div class="cc-btns"><a class="cc-btn" href="{WA}" target="_blank" rel="noopener">Escribir por WhatsApp</a><a class="cc-btn cc-btn--pdf" href="{cfg["formulario_url"]}" target="_blank" rel="noopener">Ir al formulario</a></div></div></div></section>'
page('Preguntas frecuentes',faq_page(),'preguntas-frecuentes')

def swap(path,segs_names,html_new,marker):
    t=open(path,encoding='utf8').read(); m=f'<!--cc:{marker}-->'; e=f'<!--/cc:{marker}-->'
    if m in t: t=re.sub(re.escape(m)+'.*?'+re.escape(e),lambda _:m+html_new+e,t,flags=re.S)
    else:
        sp=[s for s in split_parents(t)]
        top=[s for s in sp if not any(o[0]<s[0] and s[1]<=o[1] for o in sp)]
        pick=segs_names(t,top)
        if not pick: print('sin sección',path,marker); return
        a,b=pick[0][0],pick[-1][1]; t=t[:a]+m+html_new+e+t[b:]
    open(path,'w',encoding='utf8').write(t)
exec(open(os.path.join(ROOT,'tools','sections.py')).read().split("if __name__")[0])
def by_id(i): return lambda t,top:[s for s in top if f' id="{i}"' in t[s[0]:s[0]+700]][:1]
swap(os.path.join(SITE,'index.html'),by_id('en-que-consiste'),block_consiste('./'),'consiste')
_f=os.path.join(SITE,'index.html'); _t=open(_f,encoding='utf8').read()
_t=re.sub(r'<!--cc:empresas-->.*?<!--/cc:empresas-->','',_t,flags=re.S)
if '<!--cc:empresas-->' not in _t:
    _t=_t.replace('<!--cc:consiste-->','<!--cc:empresas-->'+block_empresas()+'<!--/cc:empresas--><!--cc:consiste-->',1)
open(_f,'w',encoding='utf8').write(_t)
swap(os.path.join(SITE,'index.html'),by_id('niveles-de-clasificacion'),block_niveles(),'niveles')
swap(os.path.join(SITE,'index.html'),by_id('periodos'),block_periodos(),'periodos')

swap(os.path.join(SITE,'index.html'),by_id('estandares'),block_estandares('./',cfg.get('plataforma_url') or './#estandares'),'estandares')
_f=os.path.join(SITE,'index.html'); _t=open(_f,encoding='utf8').read(); _m='<!--cc:faq-->'; _e='<!--/cc:faq-->'
if _m in _t: _t=re.sub(re.escape(_m)+'.*?'+re.escape(_e),lambda _:_m+block_faq()+_e,_t,flags=re.S)
else:
    _sp=split_parents(_t); _top=[s for s in _sp if not any(o[0]<s[0] and s[1]<=o[1] for o in _sp)]
    _k=_t.index('<div data-elementor-type="footer"'); _t=_t[:_k]+_m+block_faq()+_e+_t[_k:]
open(_f,'w',encoding='utf8').write(_t)
for std,fol in (('pp','estandar-produccion-primaria'),('aa','estandar-adecuacion-agroindustrial')):
    swap(os.path.join(SITE,fol,'index.html'),lambda t,top:top[:2],block_std(std,'../'),'std')

# ================= opciones de banner (vista previa) =================
lab=lambda n,d:f'<div class="cc-wrap" style="padding:28px 24px 10px"><h2 style="margin:0;color:#76236C">Opción {n.upper()}</h2><p style="margin:4px 0 0;color:#555">{d}</p></div>'
page('Opciones de banner',hero('Opciones de banner','Cuatro diseños para el banner de los agentes virtuales.')+lab('a','Tarjetas de agentes: título a la izquierda y un agente por estándar.')+banner('a','../')+lab('b','Chat de WhatsApp: cada agente saluda en su globo, estilo conversación.')+banner('b','../')+lab('c','Foto del productor con los dos agentes como insignias y botones con su ícono.')+banner('c','../')+lab('d','Franja delgada: un agente a cada lado del mensaje.')+banner('d','../'),'opciones-banner')

# ================= cabecera, menú, formularios, enlaces =================
FORM=cfg['formulario_url']; PLAT=cfg.get('plataforma_url') or './#estandares'
for f in glob.glob(os.path.join(SITE,'**','index.html'),recursive=True):
    t=open(f,encoding='utf8').read(); rel=os.path.relpath(SITE,os.path.dirname(f)); base='' if rel=='.' else rel+'/'; base='./' if base=='' else base
    k=t.find('proyectoseis.cl/diseno-web')
    if k>=0:
        s=max(m.start() for m in re.finditer(r'<div class="elementor-element [^"]*e-parent[^"]*"',t[:k]))
        d=0
        for x in re.finditer(r'<div\b|</div>',t[s:]):
            d+=1 if x.group()=='<div' else -1
            if d==0: t=t[:s]+t[s+x.end():]; break
    # lista del pie ("Certificación"): mismos ítems que el menú
    _svg='<svg aria-hidden="true" class="e-font-icon-svg e-fas-circle" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg"><path d="M256 8C119 8 8 119 8 256s111 248 248 248 248-111 248-248S393 8 256 8z"></path></svg>'
    _items=[('Inicio',base+'index.html'),('Producción primaria',base+'estandar-produccion-primaria/'),('Adecuación agroindustrial',base+'estandar-adecuacion-agroindustrial/'),('Auditores',base+'auditores/'),('Recursos',base+'recursos/')]
    _ul='<ul class="elementor-icon-list-items">'+''.join(f'<li class="elementor-icon-list-item"><a href="{h}"><span class="elementor-icon-list-icon">{_svg}</span><span class="elementor-icon-list-text">{n}</span></a></li>' for n,h in _items)+'</ul>'
    t=re.sub(r'<ul class="elementor-icon-list-items">(?:(?!</ul>).)*?Niveles de Clasificación(?:(?!</ul>).)*?</ul>',lambda m:_ul,t,flags=re.S)
    # menú: Auditores + Recursos
    if 'menu-item-auditores' not in t:
        def _aud(m):
            ti=' tabindex="-1"' if 'tabindex' in m.group(1) else ''
            return m.group(1)+'\n<li class="menu-item menu-item-auditores"><a href="'+base+'auditores/" class="elementor-item"'+ti+'>Auditores</a></li>'
        t=re.sub(r'(<li [^>]*menu-item-987"><a [^>]*>[^<]*</a></li>)',_aud,t)
    if 'menu-item-recursos' not in t:
        t=re.sub(r'(<li class="menu-item menu-item-auditores"><a [^>]*>Auditores</a></li>)',lambda m:m.group(1)+f'\n<li class="menu-item menu-item-recursos"><a href="{base}recursos/" class="elementor-item">Recursos</a></li>',t)
    t=re.sub(r' style="background:#[0-9A-Fa-f]+!important;white-space:normal"','',t)
    t=re.sub(r'<li [^>]*menu-item-(442|1696)"><a [^>]*>[^<]*</a></li>\n?','',t)
    t=re.sub(r'(<a class="elementor-button elementor-button-link elementor-size-sm")( href="[^"]*(?:estandar-produccion-primaria/|EstandarPP\.pdf)")',r'\1 style="background:'+PP_COL+r'!important;white-space:normal"\2',t)
    t=re.sub(r'(<a class="elementor-button elementor-button-link elementor-size-sm")( href="[^"]*(?:estandar-adecuacion-agroindustrial/|EstandarAA\.pdf)")',r'\1 style="background:'+AA_COL+r'!important;white-space:normal"\2',t)
    cur=os.path.basename(os.path.dirname(f))
    for nm,lab in (('auditores','Auditores'),('recursos','Recursos')):
        t=t.replace(f'class="elementor-item elementor-item-active"{" "}','class="elementor-item"')
        if cur==nm: t=re.sub(r'(<a href="[^"]*'+nm+r'/" class="elementor-item)(")',r'\1 elementor-item-active\2',t)
    # botón verde: Recursos -> Plataforma de certificación
    t=re.sub(r'href="[^"]*#estandares">(\s*<span class="elementor-button-content-wrapper">\s*<span class="elementor-button-text">)Recursos',lambda m:f'href="{PLAT if rel!="." else PLAT}">'+m.group(1)+'Plataforma de certificación',t)
    t=t.replace('elementor-button-text">Recursos<','elementor-button-text">Plataforma de certificación<')
    t=re.sub(r'¿Tienes dudas respecto al\s*(?:<br\s*/?>)?\s*Estándar de\s*certificación\?','¿Quieres saber más sobre el proceso?',t)
    t=re.sub(r'Rellena nuestro formulario de contacto con tus datos y detalla tus dudas o consultas en el campo\s*[“"]mensaje[”"], nuestro equipo te contactará a la brevedad\.','Déjanos tus datos y cuéntanos qué te gustaría saber sobre la certificación. Nuestro equipo te contactará a la brevedad.',t)
    t=re.sub(r'<a ([^>]*?)href="[^"]*"([^>]*)>(\s*<span class="elementor-button-content-wrapper">\s*<span class="elementor-button-text">Plataforma de certificación)',lambda m:'<a '+re.sub(r' ?target="[^"]*"| ?rel="[^"]*"','',m.group(1)+m.group(2)).strip()+' href="'+PLAT+'" target="_blank" rel="noopener">'+m.group(3),t)
    # un solo formulario
    t=t.replace('https://forms.gle/7MgyV7GKXY9YBEKv5',FORM).replace('https://forms.gle/bcpuHCxg7zGBdZpz5',FORM)
    t=re.sub(r'(<!--cc-form-->.*?<!--/cc-form-->)|(<form class="elementor-form".*?</form>)',f'<!--cc-form--><div class="cc-formbtn"><a class="cc-btn cc-btn--w" style="color:#76236C!important" href="{FORM}" target="_blank" rel="noopener">Enviar mi consulta</a></div><!--/cc-form-->',t,flags=re.S)
    # "Ver recursos" de la portada
    t=re.sub(r'href="[^"]*recursos-produccion-primaria/"',f'href="{base}recursos/?estandar=pp"',t); t=re.sub(r'href="[^"]*recursos-adecuacion-agroindustrial/"',f'href="{base}recursos/?estandar=aa"',t)
    t=re.sub(r'<link rel="stylesheet" href="[^"]*assets-nuevos/extra.css">\n?','',t); t=t.replace('</head>',f'<link rel="stylesheet" href="{base}assets-nuevos/extra.css">\n</head>',1)
    open(f,'w',encoding='utf8').write(t)
# paleta: verde -> verde azulado del estándar
for f in glob.glob(os.path.join(SITE,'wp-content','uploads','elementor','css','*.css')):
    t=open(f,encoding='utf8').read(); t2=re.sub('(?i)#(469300|1E7F6C|C96510|2F7D4F)','#76236C',t); t2=re.sub('(?i)#(F4FFEA|E3F1EE)','#F3ECF3',t2)
    if t2!=t: open(f,'w',encoding='utf8').write(t2)
print('ok')
