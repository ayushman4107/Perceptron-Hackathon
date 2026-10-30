"""Render the measured abstract and optional one-page approach/evidence supplement."""
import sys,re,json
from pathlib import Path
from xml.sax.saxutils import escape
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT/'.deps'))
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
INK=HexColor('#1f2b3b');TEAL=HexColor('#087f70');MUTED=HexColor('#586578');LINE=HexColor('#dce3e8')
W,H=595.276,841.89
def clean(s):
    for old,new in [('—','-'),('–','-'),('−','-'),('‑','-'),('“','"'),('”','"'),('’',"'")]:s=s.replace(old,new)
    return s
def markup(s):return re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',escape(clean(s)))
def para(c,text,x,y,w,size=9.5,leading=12.5,color=INK,bold=False):
    p=Paragraph(markup(text),ParagraphStyle('p',fontName='DVB' if bold else 'DV',fontSize=size,leading=leading,textColor=color))
    _,h=p.wrap(w,1000);p.drawOn(c,x,y-h);return y-h
def footer(c,page):
    c.setStrokeColor(LINE);c.line(42,37,W-42,37);c.setFont('DV',7);c.setFillColor(MUTED)
    c.drawString(42,24,'Perceptron | Problem 3 | Research prototype and preliminary evaluation')
    c.drawRightString(W-42,24,str(page))

def abstract_page(c,text):
    c.setFillColor(TEAL);c.setFont('DVB',8);c.drawString(42,806,'PERCEPTRON  /  PROBLEM 3  /  THEME 2')
    para(c,'From 80 Items to Two Reward Groups',42,790,W-84,19,23,bold=True)
    para(c,'Auditable Policy Evaluation',42,765,W-84,16,20,bold=True)
    c.setStrokeColor(TEAL);c.setLineWidth(1.3);c.line(42,731,W-42,731)
    chunks=[]
    for section in text.split('\n## ')[1:]:
        heading,body=section.split('\n',1);chunks.append(('head',heading.strip()))
        for p in body.strip().split('\n\n'):chunks.append(('body',p.strip()))
    y=716;size=10.2;page=1
    for kind,s in chunks:
        if kind=='head' and s=='Novelty and differentiation':
            footer(c,1);c.showPage();page=2
            para(c,'Contribution, evaluation and delivery',42,805,W-84,17,21,bold=True)
            y=771
        y=para(c,s,42,y,W-84,size+.1 if kind=='head' else size,13.3,TEAL if kind=='head' else INK,kind=='head')
        y-=7 if kind=='head' else 10
        if y<49:raise RuntimeError(f'Abstract page {page} overflow at {s[:40]}')
    y=chart(c,'02_policy_certificate.png',42,y-2,W-84)
    y=para(c,'Primary OBD split, selected top-20 candidate. Finite-sample methods account for the five-candidate family; DR/Wald is asymptotic. The shaded band describes uncertainty in the independent reference, not counterfactual ground truth.',42,y-4,W-84,7.5,9.7,color=MUTED)
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
    para(c,'Approach and preliminary evidence',42,805,W-84,17,21,bold=True)
    para(c,'Optional one-page supplement | Frozen primary split; full campaign files',42,778,W-84,8.5,11,color=MUTED)
    # Explicitly independent data branches, rather than an apparent sequential reference fit.
    c.setFillColor(HexColor('#edf5f3'));c.roundRect(188,733,219,25,5,stroke=0,fill=1)
    para(c,'Random log: action, click, propensity',196,751,204,8.5,10,bold=True)
    centers=[119,297,475]
    for center in centers:arrow(c,297,733,center,713)
    boxes=[('PILOT / 20%','Rank items; freeze five candidates'),('CERTIFICATION / 40%','Check ratios; construct gain bounds'),('REFERENCE / 40%','Evaluate only; never fit or tune')]
    for x,(title,body) in zip([42,220,398],boxes):
        c.setFillColor(HexColor('#f5f7f9'));c.setStrokeColor(LINE);c.roundRect(x,667,155,46,4,stroke=1,fill=1)
        para(c,title,x+8,702,139,8,10,color=TEAL,bold=True);para(c,body,x+8,687,139,7.6,9.5)
    para(c,'Exact reduction: Δ = (1-k/A) × (q_top - q_rest). Unequal item rewards are allowed.',42,653,W-84,8.5,11,bold=True)
    y=chart(c,'01_obd_counterfactual.png',42,634,W-84)
    y=para(c,'A. Men’s campaign, first position: 1,358,878 BTS rows and 150,936 independent Random rows. Bars show pointwise 95% Wald intervals. The raw BTS average is a naive proxy for the target policy; the Random mean is an empirical reference.',42,y-5,W-84,7.6,10,color=MUTED)
    y=chart(c,'03_ablation.png',42,y-16,W-84)
    y=para(c,'B. Random/all: five pilot-learned candidate sets, 183,450 certification rows. Finite-sample intervals account for candidate selection. The median paired width reduction is 82.6% versus the original item likelihood; the grouped exact baseline is the recommended procedure.',42,y-4,W-84,7.6,10,color=MUTED)
    y=para(c,'Validation: 8,000 independent synthetic logs × 11 methods; 16 implementation tests. Real-world dependence, drift and slate interference remain limitations. Wider intervals can still be more reliable; all baselines and failures are retained.',42,y-9,W-84,7.8,10.2,bold=True)
    y=para(c,'Sources: Saito et al., Open Bandit Dataset (NeurIPS 2021); Wasserman et al., Universal Inference (PNAS 2020); Saito & Joachims, MIPS (ICML 2022); Lee et al., evaluation-weight-preserving coarsening (2026 preprint). Code, full results and scope: github.com/ayushman4107/Perceptron-Hackathon',42,y-8,W-84,7.1,9.2,color=MUTED)
    c.linkURL('https://github.com/ayushman4107/Perceptron-Hackathon',(42,y-2,W-42,y+25),relative=0)
    if y<47:raise RuntimeError(f'Evidence page overflow: bottom {y}')
    footer(c,3);return y

def main():
    text=(ROOT/'ABSTRACT.md').read_text(encoding='utf-8');assert 600<=len(text.split())<=900
    pdf=OUT/'Abstract_with_Evidence.pdf';c=canvas.Canvas(str(pdf),pagesize=(W,H))
    c.setTitle('From 80 Items to Two Reward Groups: Auditable Policy Evaluation');c.setAuthor('Perceptron hackathon team')
    size=abstract_page(c,text);c.showPage();bottom=evidence_page(c);c.showPage();c.save()
    plain=re.sub(r'^#+\s*','',text,flags=re.M).replace('**','');(ROOT/'ABSTRACT_plain.txt').write_text(plain,encoding='utf-8')
    render=ROOT/'tmp'/'pdf_preview';render.mkdir(parents=True,exist_ok=True)
    doc=pymupdf.open(pdf);assert len(doc)==3
    for i,page in enumerate(doc):page.get_pixmap(matrix=pymupdf.Matrix(1.6,1.6)).save(render/f'page-{i+1}.png')
    report=dict(words_including_title_headings=len(text.split()),sections=text.count('\n## '),pages=len(doc),body_font_size=size,evidence_bottom=bottom,
        page_text_characters=[len(p.get_text()) for p in doc],pdf_bytes=pdf.stat().st_size)
    (OUT/'layout_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':main()
