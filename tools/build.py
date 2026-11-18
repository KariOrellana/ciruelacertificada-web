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

def hero(h1,sub=''):
    return f'<section class="cc-hero"><div class="cc-wrap"><h1>{E_(h1)}</h1>'+(f'<p>{sub}</p>' if sub else '')+'</div></section>'

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

# ---------- recursos PP ----------
def label(fn):
    b=os.path.splitext(fn)[0]
    if re.search(r'gu[ií]a',b,re.I): return 'Guía'
    m=re.search(r'parte-?(\d)',b,re.I); return f'Parte {m.group(1)}' if m else b.replace('-',' ')
def theme_cards():
    cards=[]
    pdfdir=os.path.join(PDFSRC,'pdf')
    for d in sorted(os.listdir(pdfdir)):
        full=os.path.join(pdfdir,d)
        if not os.path.isdir(full): continue
        dest=os.path.join(SITE,'recursos','pdf',d); os.makedirs(dest,exist_ok=True)
        files=sorted(os.listdir(full),key=lambda f:(label(f)!='Guía',label(f)))
        for f in files:
            if not os.path.exists(os.path.join(dest,f)): shutil.copy2(os.path.join(full,f),dest)
        name=cfg['temas'].get(d,d.replace('-',' ').capitalize())
        links=''.join(f'<a class="cc-btn cc-btn--pdf" href="../recursos/pdf/{d}/{E_(f)}" target="_blank" rel="noopener">{E_(label(f))}</a>' for f in files)
        vids=VID.get(norm(name),[])
        vl=''.join(f'<li><a href="{E_(u)}" target="_blank" rel="noopener">{E_(l)}</a></li>' for l,u in vids)
        curso=CURSO.get(norm(name))
        cards.append(f'<article class="cc-card"><h3>{E_(name)}</h3><p class="cc-lbl">Guías y material (PDF)</p><div class="cc-btns">{links}</div>'
          +(f'<p class="cc-lbl">Videos</p><ul class="cc-vid">{vl}</ul>' if vl else '')
          +(f'<a class="cc-link" href="{E_(curso)}" target="_blank" rel="noopener">Ir al curso en línea →</a>' if curso else '')+'</article>')
    return ''.join(cards)
def mv_block(std):
    url=cfg['mv'][std]['url']; txt=cfg['mv'][std]['texto']
    if url: btn=f'<a class="cc-btn" href="{E_(url)}" target="_blank" rel="noopener">Descargar medios de verificación</a>'
    else: btn='<span class="cc-btn cc-btn--off">Descarga disponible pronto</span>'
    return f'<section class="cc-sec"><div class="cc-wrap"><h2>Medios de verificación</h2><p>{txt}</p>{btn}</div></section>'

page('Recursos – Producción primaria',
  hero('Recursos del estándar de Producción primaria','Guías, videos y medios de verificación para implementar cada temática del estándar.')
  +mv_block('pp')+f'<section class="cc-sec cc-sec--alt"><div class="cc-wrap"><h2>Material por temática</h2><div class="cc-grid">{theme_cards()}</div></div></section>',
  'recursos-produccion-primaria')
page('Recursos – Adecuación agroindustrial',
  hero('Recursos del estándar de Adecuación agroindustrial','Medios de verificación para cada acción del estándar.')+mv_block('aa'),
  'recursos-adecuacion-agroindustrial')
page('Auditores',
  hero('Auditores','Información para auditores del estándar.')
  +'<section class="cc-sec"><div class="cc-wrap"><p>'+E_(cfg['auditores_texto'])+'</p></div></section>','auditores')

# ---------- menú: pestaña Auditores en todas las páginas ----------
for f in glob.glob(os.path.join(SITE,'**','index.html'),recursive=True):
    t=open(f,encoding='utf8').read()
    if 'class="elementor-item">Auditores' in t or 'elementor-item" tabindex="-1">Auditores' in t: continue
    def add(m):
        li,pre,ti=m.group(0),m.group(1),m.group(3)
        new=f'<li class="menu-item menu-item-auditores"><a href="{pre}auditores/" class="elementor-item"{ti}>Auditores</a></li>'
        return li+'\n'+new
    t2=re.sub(r'<li [^>]*menu-item-987"><a href="((?:\.\./|\./)?)(estandar-adecuacion-agroindustrial/)" class="elementor-item"( tabindex="-1")?>[^<]*</a></li>',
              lambda m:add(m) if False else m.group(0)+'\n'+f'<li class="menu-item menu-item-auditores"><a href="{m.group(1)}auditores/" class="elementor-item"{m.group(3) or ""}>Auditores</a></li>',t)
    t2=t2.replace('<a href="" ','<a href="./" ')
    if t2!=t: open(f,'w',encoding='utf8').write(t2)
print('ok')
