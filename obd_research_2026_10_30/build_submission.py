"""Render the measured abstract and optional one-page approach/evidence supplement."""
import sys,re,json,os
from pathlib import Path
from xml.sax.saxutils import escape
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT/'.deps'))
os.environ['MPLCONFIGDIR']=str(ROOT/'tmp'/'matplotlib')
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor,Color,white
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from PIL import Image
import pymupdf
import matplotlib

OUT=ROOT/'output'/'pdf';OUT.mkdir(parents=True,exist_ok=True)
FONT=Path(matplotlib.get_data_path())/'fonts'/'ttf'
pdfmetrics.registerFont(TTFont('DV',str(FONT/'DejaVuSans.ttf')))
pdfmetrics.registerFont(TTFont('DVB',str(FONT/'DejaVuSans-Bold.ttf')))
pdfmetrics.registerFontFamily('DV',normal='DV',bold='DVB',italic='DV',boldItalic='DVB')
INK=HexColor('#000000');TEAL=INK;MUTED=INK;LINE=HexColor('#dce3e8')
PROJECT='PoliSee';SUBTITLE='Counterfactual Policy Evaluation'
REPO_URL='https://github.com/ayushman4107/Perceptron-Hackathon'
BODY_SIZE=10.2;HEADING_SIZE=17;CAPTION_SIZE=9;CAPTION_LEADING=11.5
W,H=595.276,841.89
def clean(s):
    for old,new in [('—','-'),('–','-'),('−','-'),('‑','-'),('“','"'),('”','"'),('’',"'")]:s=s.replace(old,new)
    return s
def markup(s):return re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',escape(clean(s)))
def para(c,text,x,y,w,size=9.5,leading=12.5,color=INK,bold=False):
    p=Paragraph(markup(text),ParagraphStyle('p',fontName='DVB' if bold else 'DV',fontSize=size,leading=leading,textColor=color))
    _,h=p.wrap(w,1000);p.drawOn(c,x,y-h);return y-h
def footer(c,page):
    c.setStrokeColor(LINE);c.line(42,37,W-42,37);c.setFont('DV',CAPTION_SIZE);c.setFillColor(INK)
    c.drawString(42,23,'PoliSee | Perceptron | Problem 3')
    c.drawRightString(W-42,24,str(page))

def header(c):
    c.setFillColor(INK);c.setFont('DV',9)
    c.drawString(42,H-24,'PERCEPTRON  /  PROBLEM 3  /  THEME 2')

def abstract_page(c,text):
    header(c)
    para(c,PROJECT,42,805,W-84,HEADING_SIZE,21,bold=True)
    para(c,SUBTITLE,42,778,W-84,BODY_SIZE,13.3)
    c.setFont('DV',CAPTION_SIZE);c.setFillColor(INK)
    c.setFont('DVB',BODY_SIZE);c.drawString(42,752,'Team Zero1')
    c.setFont('DV',CAPTION_SIZE)
    label='Code and results: ';url_label='github.com/ayushman4107/Perceptron-Hackathon'
    c.drawString(42,738,label+url_label)
    left=42+pdfmetrics.stringWidth(label,'DV',CAPTION_SIZE)
    right=left+pdfmetrics.stringWidth(url_label,'DV',CAPTION_SIZE)
    c.setStrokeColor(INK);c.setLineWidth(.4);c.line(left,736,right,736)
    c.linkURL(REPO_URL,(left,735,right,748),relative=0)
    c.setStrokeColor(TEAL);c.setLineWidth(1.3);c.line(42,725,W-42,725)
    chunks=[]
    for section in text.split('\n## ')[1:]:
        heading,body=section.split('\n',1);chunks.append(('head',heading.strip()))
        for p in body.strip().split('\n\n'):chunks.append(('body',p.strip()))
    y=716;size=BODY_SIZE;page=1
    for kind,s in chunks:
        if kind=='head' and s=='Novelty and differentiation':
            footer(c,1);c.showPage();page=2;header(c)
            y=805
        y=para(c,s,42,y,W-84,12 if kind=='head' else size,15 if kind=='head' else 13.3,INK,kind=='head')
        y-=5 if kind=='head' else 8
        if y<49:raise RuntimeError(f'Abstract page {page} overflow at {s[:40]}')
    y=chart(c,'02_policy_certificate.png',42,y-2,W-84)
    y=para(c,'Primary OBD split, selected top-20 candidate. Finite-sample methods account for the five-candidate family; DR/Wald is asymptotic. The shaded band describes uncertainty in the independent reference, not counterfactual ground truth.',42,y-6,W-84,10.2,13.3)
    if y<49:raise RuntimeError(f'Certificate figure overflow: {y}')
    footer(c,2);return size

def chart(c,name,x,y_top,width):
    path=ROOT/'figures'/name
    with Image.open(path) as im:iw,ih=im.size
    height=width*ih/iw;c.drawImage(str(path),x,y_top-height,width=width,height=height,mask='auto');return y_top-height
def arrow(c,x1,y1,x2,y2):
    c.setStrokeColor(MUTED);c.setLineWidth(.8);c.line(x1,y1,x2,y2)
    if y2<y1:c.line(x2,y2,x2-3,y2+4);c.line(x2,y2,x2+3,y2+4)
    else:c.line(x2,y2,x2-4,y2-3);c.line(x2,y2,x2-4,y2+3)

def evidence_page(c):
    header(c)
    para(c,'PoliSee | Approach and evidence',42,805,W-84,HEADING_SIZE,21,bold=True)
    para(c,'Optional supplement | Frozen primary split; full campaign files',42,778,W-84,CAPTION_SIZE,CAPTION_LEADING)
    # Explicitly independent data branches, rather than an apparent sequential reference fit.
    c.setFillColor(HexColor('#edf5f3'));c.roundRect(188,733,219,25,5,stroke=0,fill=1)
    para(c,'Random log: action, click, propensity',196,751,204,CAPTION_SIZE,CAPTION_LEADING,bold=True)
    centers=[119,297,475]
    for center in centers:arrow(c,297,733,center,713)
    boxes=[('PILOT / 20%','Rank items; freeze five candidates'),('CERTIFICATION / 40%','Check ratios; construct gain bounds'),('REFERENCE / 40%','Evaluate only; never fit or tune')]
    for x,(title,body) in zip([42,220,398],boxes):
        c.setFillColor(HexColor('#f5f7f9'));c.setStrokeColor(LINE);c.roundRect(x,659,155,54,4,stroke=1,fill=1)
        para(c,title,x+8,702,139,CAPTION_SIZE,CAPTION_LEADING,bold=True);para(c,body,x+8,687,139,CAPTION_SIZE,CAPTION_LEADING)
    para(c,'Exact reduction: Δ = (1-k/A) × (q_top - q_rest). Unequal item rewards are allowed.',42,653,W-84,CAPTION_SIZE,CAPTION_LEADING,bold=True)
    y=chart(c,'01_obd_counterfactual.png',42,634,W-84)
    y=para(c,'A. Men’s campaign, first position: 1,358,878 BTS rows and 150,936 Random rows. Bars: pointwise 95% Wald intervals. Raw BTS CTR is a naive proxy; Random CTR is an independent empirical reference.',42,y-6,W-84,CAPTION_SIZE,CAPTION_LEADING)
    y=chart(c,'03_ablation.png',42,y-16,W-84)
    y=para(c,'B. Random/all: five pilot-learned candidates; 183,450 certification rows. Intervals account for candidate selection. Median paired width reduction: 82.6% versus original item likelihood. Grouped exact is the recommended procedure.',42,y-6,W-84,CAPTION_SIZE,CAPTION_LEADING)
    y=para(c,'Validation: 8,000 synthetic logs × 11 methods; 16 tests. Dependence, drift and slate interference remain limitations. All comparisons are retained.',42,y-9,W-84,CAPTION_SIZE,CAPTION_LEADING)
    y=para(c,'Sources: Saito et al. (2021); Wasserman et al. (2020); Saito & Joachims (2022); Lee et al. (2026). References, code and results: github.com/ayushman4107/Perceptron-Hackathon',42,y-8,W-84,CAPTION_SIZE,CAPTION_LEADING)
    c.linkURL('https://github.com/ayushman4107/Perceptron-Hackathon',(42,y-2,W-42,y+25),relative=0)
    if y<47:raise RuntimeError(f'Evidence page overflow: bottom {y}')
    footer(c,3);return y

def main():
    text=(ROOT/'ABSTRACT.md').read_text(encoding='utf-8');assert 600<=len(text.split())<=900
    pdf=OUT/'Abstract_with_Evidence.pdf';c=canvas.Canvas(str(pdf),pagesize=(W,H))
    c.setTitle(PROJECT+': '+SUBTITLE);c.setAuthor('Team Zero1')
    size=abstract_page(c,text);c.showPage();bottom=evidence_page(c);c.showPage();c.save()
    plain=re.sub(r'^#+\s*','',text,flags=re.M).replace('**','')
    plain=re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)',r'\1: \2',plain)
    (ROOT/'ABSTRACT_plain.txt').write_text(plain,encoding='utf-8')
    render=ROOT/'tmp'/'pdf_preview';render.mkdir(parents=True,exist_ok=True)
    doc=pymupdf.open(pdf);assert len(doc)==3
    # Append the approved architecture as a readable, vector landscape page.
    vector=pymupdf.open(str(ROOT/'figures'/'06_polisee_architecture.pdf'))
    page=doc.new_page(width=H,height=W)
    page.insert_font(fontname='DV',fontfile=str(FONT/'DejaVuSans.ttf'))
    page.insert_font(fontname='DVB',fontfile=str(FONT/'DejaVuSans-Bold.ttf'))
    page.insert_text((42,24),'PERCEPTRON  /  PROBLEM 3  /  THEME 2',fontname='DV',fontsize=9,color=(0,0,0))
    page.insert_text((42,53),'PoliSee | System architecture',fontname='DVB',fontsize=17,color=(0,0,0))
    page.insert_text((42,74),'From logged decisions to evidence about a different policy',fontname='DV',fontsize=10.2,color=(0,0,0))
    clip=pymupdf.Rect(20,110,1132,590)
    figure_height=(H-84)*clip.height/clip.width
    page.show_pdf_page(pymupdf.Rect(42,96,H-42,96+figure_height),vector,0,clip=clip)
    page.draw_line((42,W-37),(H-42,W-37),color=(.86,.89,.91),width=.7)
    page.insert_font(fontname='DV',fontfile=str(FONT/'DejaVuSans.ttf'))
    page.insert_text((42,W-23),'PoliSee | Perceptron | Problem 3',fontname='DV',fontsize=9,color=(0,0,0))
    page.insert_text((H-48,W-23),'4',fontname='DV',fontsize=9,color=(0,0,0))
    final_bytes=doc.tobytes(garbage=4,deflate=True);doc.close();pdf.write_bytes(final_bytes)
    doc=pymupdf.open(pdf);assert len(doc)==4
    for i,page in enumerate(doc):page.get_pixmap(matrix=pymupdf.Matrix(1.6,1.6)).save(render/f'page-{i+1}.png')
    report=dict(words_including_title_headings=len(text.split()),sections=text.count('\n## '),pages=len(doc),body_font_size=size,evidence_bottom=bottom,
        page_text_characters=[len(p.get_text()) for p in doc],pdf_bytes=pdf.stat().st_size)
    (OUT/'layout_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':main()
