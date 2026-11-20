# Versión en inglés de la portada. Se ejecuta desde build.py (usa sus funciones y variables).
EN_DIM={'Ambiente':'Environment','Calidad':'Quality','Gestión':'Management','Social':'Social','Ética':'Ethics'}
EN_TEMA={'Agua':'Water','Suelo':'Soil','Biodiversidad':'Biodiversity','Insumos':'Inputs','Residuos':'Waste','Energía':'Energy','Gases de Efecto Invernadero':'Greenhouse gases',
 'Gestión de la Calidad':'Quality management','Gestión de la Inocuidad':'Food safety management','Viabilidad Económica':'Economic viability','Comunidades Locales':'Local communities',
 'Condiciones de Trabajo y Protección Social':'Working conditions and social protection','Debida Diligencia de la Legislación':'Due diligence of the law'}
EN_STEPS=[("Join the APL","Joining the Clean Production Agreement (APL) is free of charge. Each facility (orchard or plant) joins and is audited separately, and has one year to complete the cycle."),
("Initial self-assessment","Complete your self-assessment on the online platform and see your level of compliance. Actions that do not apply to your facility are marked “Not compliant”."),
("Implementation plan","Draw up a plan to close the gaps found, with ongoing technical support. If you need to, you can request an intermediate audit before the final one."),
("Final audit","Choose an auditor accredited by the ASCC, who reviews your means of verification, visits your facility and writes the report."),
("Public validation","The public bodies that validate the APL review the reports. Clarifications and corrections are handled with the ASCC within 90 days."),
("ASCC certification","You obtain your certificate for 1, 2 or 3 years, depending on the level reached. When it expires, it is renewed by repeating the self-assessment and the audit.")]
EN_LV=[('Fundamental','5 points','#DCE6F5','#1F3A5F','Actions that are essential to qualify a company as sustainable, regardless of their complexity. Their mandatory nature is higher than the rest.'),
('Basic','2 points','#FDF3C9','#8A6D00','Actions with lower impact on sustainability and lower implementation complexity.'),
('Intermediate','3 points','#E3F1D9','#3C7A22','Actions with intermediate impact and implementation complexity.'),
('Advanced','4 points','#FCE3D6','#B24A16','Actions with the greatest impact on sustainability and the greatest implementation complexity.')]
EN_REPL=(('Inicio','Home'),('Producción primaria','Primary production'),('Adecuación agroindustrial','Agro-industrial adaptation'),('Auditores','Auditors'),('Recursos','Resources'),
 ('Plataforma de certificación','Certification platform'),('¿Quieres saber más sobre el proceso?','Want to know more about the process?'),
 ('Déjanos tus datos y cuéntanos qué te gustaría saber sobre la certificación. Nuestro equipo te contactará a la brevedad.','Leave us your details and tell us what you would like to know about certification. Our team will contact you shortly.'),
 ('Enviar mi consulta','Send my enquiry'),('Apoyado por:','Supported by:'),('Colaboran:','Partners:'),('>Certificación<','>Certification<'),('Datos de contacto','Contact details'),
 ('Dirección','Address'),('Horario de atención','Opening hours'),('Lunes a Viernes de 09:00 a 19:00hrs','Monday to Friday, 09:00–19:00'),('>Estándares<','>Standards<'),
 ('estándar de producción primaria','primary production standard'),('estándar de adecuación agroindustrial','agro-industrial adaptation standard'))

def en_page():
    F=cfg['formulario_url']; e=cfg['empresas']; tpd=temas_por_dim('pp')
    dims=''.join(f'<div class="cc-endim" style="border-color:{DIM_COLOR[d]}"><h3 style="color:{DIM_COLOR[d]}">{EN_DIM[d]}</h3><p>'+', '.join(EN_TEMA.get(t,t) for t in tpd[d])+'</p></div>' for d in tpd)
    def card(std,nm,n,desc):
        c=STDCOL[std]
        return (f'<div class="cc-pcard" style="border-top-color:{c}"><h3 style="color:{c}">{nm}</h3><p><strong>{n} actions</strong></p><p>{desc}</p>'
                f'<div class="cc-btns"><a class="cc-btn" style="background:{c}" href="../{STDURL[std]}/">View standard (Spanish)</a><a class="cc-btn cc-btn--pdf" href="../recursos/?estandar={std}">View resources</a></div></div>')
    cards=(card('pp','Primary production',nacc('pp'),'For orchards: sustainable management of water, soil, biodiversity, inputs, waste, energy and climate.')
          +card('aa','Agro-industrial adaptation',nacc('aa'),'For dehydration plants: the same dimensions, adapted to industrial processes.'))
    lv=''.join(f'<div class="cc-lv" style="background:{b}"><span class="cc-pts" style="color:{c}">{p}</span><h4 style="color:{c}">{n}</h4><p>{d}</p></div>' for n,p,b,c,d in EN_LV)
    steps=''.join(f'<li class="cc-st"><span class="cc-stn">{i+1}</span><h3>{E_(a)}</h3><p>{E_(b)}</p></li>' for i,(a,b) in enumerate(EN_STEPS))
    def per(std,nm,rows):
        c=STDCOL[std]
        li=''.join(f'<li><strong>{y}:</strong> 80% of fundamental actions + {g}% of general actions</li>' for y,g in rows)
        return f'<div class="cc-pcard" style="border-top-color:{c}"><h3 style="color:{c}">{nm}</h3><ul class="cc-ul">{li}</ul></div>'
    periods=per('pp','Primary production',[('1 year',20),('2 years',40),('3 years',60)])+per('aa','Agro-industrial adaptation',[('1 year',40),('2 years',60),('3 years',80)])
    emp=(f'<section class="cc-emp cc-emp--s"><div class="cc-wrap"><div class="cc-ess">'
         f'<div class="cc-es" style="--c:{AA_COL}"><span class="cc-es-tag">Agro-industrial adaptation</span><strong>{e["aa"]["pct"]}%</strong><span class="cc-es-l">share of certified companies</span></div>'
         f'<span class="cc-es-div"></span>'
         f'<div class="cc-es" style="--c:{PP_COL}"><span class="cc-es-tag">Primary production</span><strong>{e["pp"]["pct"]}%</strong><span class="cc-es-l">share of adhered companies</span></div></div></div></section>')
    btn=f'<div class="cc-btns"><a class="cc-btn cc-btn--w" style="color:#76236C!important" href="{F}" target="_blank" rel="noopener">Join now</a></div>'
    body=(hero('Sustainability standard for the dehydrated prune industry','A management tool for companies in the sector to identify good practices and actions that can be implemented in the short and medium term, making their processes more sustainable.',btn)+emp
     +f'<section class="cc-sec"><div class="cc-wrap"><h2>What is it about?</h2><p class="cc-lead">The standards group their actions into <strong>topics</strong>, organised in <strong>5 dimensions</strong>.</p><div class="cc-endims">{dims}</div></div></section>'
     +f'<section class="cc-sec cc-sec--alt" id="standards"><div class="cc-wrap"><h2>The standards</h2><div class="cc-two">{cards}</div><p class="cc-lead">The standards and their resources are currently available in Spanish.</p></div></section>'
     +f'<section class="cc-sec" id="levels"><div class="cc-wrap"><h2>Classification levels</h2><p class="cc-lead">Each action is classified into 4 levels and earns points according to its priority. A company’s score depends on the actions it complies with at the time of the audit.</p><div class="cc-lvgrid">{lv}</div></div></section>'
     +f'<section class="cc-sec cc-sec--alt" id="periods"><div class="cc-wrap"><h2>Certification periods</h2><p class="cc-lead">To be certified you must meet two conditions: <strong>(1)</strong> 80% of the score of the fundamental actions and <strong>(2)</strong> a percentage of the score of the general actions (basic, intermediate and advanced). <strong>The more general actions you comply with, the longer your certification.</strong></p><div class="cc-two">{periods}</div></div></section>'
     +f'<section class="cc-sec" id="steps"><div class="cc-wrap"><h2>Steps to certification</h2><p class="cc-lead">The path to certify your orchard or plant, from self-assessment to renewal.</p><ol class="cc-tl-steps">{steps}</ol><div class="cc-btns cc-cta"><a class="cc-btn" href="{F}" target="_blank" rel="noopener">I want to start my certification</a><a class="cc-btn cc-btn--pdf" href="../auditores/">Information for auditors (Spanish)</a></div></div></section>')
    page('Sustainability standard for the prune industry',body,'en')
    f=os.path.join(SITE,'en','index.html'); t=open(f,encoding='utf8').read()
    t=t.replace('<html lang="es-ES">','<html lang="en">')
    for a,b in EN_REPL: t=t.replace(a,b)
    # selector de idioma: English es el actual; Español vuelve a la portada
    t=t.replace('wpml-ls-item-es wpml-ls-current-language','wpml-ls-item-es',1)
    t=t.replace('<span class="wpml-ls-native">Español</span>','<span class="wpml-ls-native" lang="en">English</span>',1)
    t=re.sub(r'(<a href=")[^"]*(" class="wpml-ls-link">.*?flags/)en(\.svg.*?lang=")en(">)English',r'\1../\2es\3es\4Español',t,1,flags=re.S)
    t=re.sub(r'<link rel="alternate" hreflang="[^"]*" href="[^"]*" />\n?','',t)
    open(f,'w',encoding='utf8').write(t)
en_page()
