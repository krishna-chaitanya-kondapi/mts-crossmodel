import hashlib,json,re,unicodedata
from pathlib import Path
import fitz
from ela_teacher import _wrap

from paths import DATA, OUTPUT, WORK, source
import os

root=DATA
out=OUTPUT / 'ela'
out.mkdir(exist_ok=True)
navy=(.12,.22,.35)
regular=os.environ['MTS_2022_FONT_REGULAR']
bold=os.environ['MTS_2022_FONT_BOLD']
fonts={'MTSBody':fitz.Font(fontfile=regular),'MTSBold':fitz.Font(fontfile=bold)}
authors={4:['Monica A. Harris','Robert San Souci','Aesop','Joseph Gaer'],5:['Myrina D. McCullough','NASA','Anonymous'],6:['Mary Kay Carson','Kate Milford','Robert San Souci']}
heads={4:['Suck Them Up and Spit Them Out','Excuse Me, I’ ve Got a Frog in my Throat','Piggyback Nursery','Cold Feet, Big Heart','Sly Teacher'],5:[],6:['From Nature Boy to Batman','From Scientist to Conservationist']}
contexts={(5,0):'In West Africa, the Harmattan is a dry, dust-filled wind.',(6,1):'On a snowy night at his family inn, Milo makes an unusual discovery.'}
snow='''6 All that water picked up from the lake normally travels no farther than about 25 miles away before falling, but it can sometimes travel as far as 100 miles away! That moisture can make for a whole lot of snow. Luckily for people living near large lakes, lake-effect snow generally slows down around February. That’s when the lakes freeze over, making it impossible for the air to steal moisture away from the lake.
7 Not surprisingly, Buffalo is one of the snowiest cities in the country. Conditions are frequently right for lake-effect snow. To many who live there, massive snowstorms are a regular part of life. But don’t think you could get more snow days by moving to an area that experiences lake-effect snow. People there are well trained in snow removal!'''

def norm(s):
    return unicodedata.normalize('NFKC',s.replace('\ue062','Th').replace('\ue09d','ft')).replace('I’ ve','I’ve')

def body(s):
    return re.split(r'^\s*(?:GO ON|STOP)\s*$',s,flags=re.M)[0].strip('\n')

def questions(pages,indices):
    result={}
    for i in indices:
        for chunk in re.split(r'\n(?:[ \t]*\n){3,}',body(pages[i-1])):
            if not chunk.strip():continue
            lines=[norm(l.strip()) for l in chunk.splitlines() if l.strip() and not re.fullmatch(r'_+',l.strip())]
            markers=[(j,int(l)) for j,l in enumerate(lines) if re.fullmatch(r'\d+',l)]
            assert len(markers)==1,(i,lines,markers)
            j,n=markers[0]
            del lines[j]
            for idx in range(len(lines)-1,-1,-1):
                if re.fullmatch(r'[A-D]',lines[idx]):
                    lines[idx-1]=lines[idx]+' '+lines[idx-1]
                    del lines[idx]
            responses=[]
            stem=[]
            for l in lines:
                if re.match(r'^[A-D] ',l) and (not responses or l[0]==chr(65+len(responses))):
                    responses.append(l[2:])
                elif responses:
                    responses[-1]+=' '+l
                else:
                    stem.append(l)
            assert not responses or len(responses)==4,(i,n,responses)
            result[n]=(' '.join(stem),responses)
    return result

def passage_blocks(pages,grade,index,selection):
    pnums=selection['passage_pages']
    text='\n'.join(body(pages[p-1]) if pages[p-1].strip() else snow for p in pnums)
    text=text.split('by '+authors[grade][index],1)[1]
    blocks=[]
    seq=0
    for raw in text.splitlines():
        l=norm(raw.strip())
        if not l or re.fullmatch(r'_+',l):continue
        if re.match(r'^\d+\s+',l):
            seq+=1
            assert int(l.split()[0])==seq,(grade,index,seq,l)
            blocks.append(('para',l))
        elif l in heads[grade]:
            blocks.append(('head',l))
        elif re.match(r'^\w+(?: \w+)? = ',l) or l.startswith('1watermark:'):
            blocks.append(('note',l.replace('1watermark','¹ watermark')))
        else:
            assert blocks,(grade,index,l)
            key,value=blocks[-1]
            blocks[-1]=(key,value+' '+l)
    return blocks

def poem_blocks(pages):
    raw=body(pages[29]).split('by Anonymous',1)[1]+'\n'+body(pages[30])
    lines=[]
    gloss=[]
    for line in raw.splitlines():
        line=norm(line.strip())
        if not line:continue
        if ' = ' in line:
            gloss.append(line);continue
        lines.append(line)
    assert len(lines)==24 and [int(lines[i].split()[0]) for i in (4,9,14,19)]==[5,10,15,20]
    return [[('verse',line) for line in lines[i:i+4]] for i in range(0,24,4)],gloss

class Book:
    def __init__(self):
        self.pdf=fitz.open()
        self.page=None
        self.audit=[]
    def new(self,heading):
        self.page=self.pdf.new_page(width=612,height=792)
        for n,file in [('MTSBody',regular),('MTSBold',bold)]: self.page.insert_font(fontname=n,fontfile=file)
        self.text(36,39,heading,15,'MTSBold',540)
        self.audit.append({'page':len(self.pdf),'heading':heading,'blocks':[]})
    def text(self,x,y,text,size=10,font='MTSBody',width=260):
        lines=_wrap(text,width,fonts[font],size)
        leading=size*1.28
        for line in lines:
            assert y<755 and fonts[font].text_length(line,fontsize=size)<=width+.5,(y,text)
            self.page.insert_text((x,y),line,fontsize=size,fontname=font,color=navy if font=='MTSBold' else (0,0,0))
            y+=leading
        return y
    def mark(self,kind,x,top,end,ids=None,width=260):
        assert 29<=x and x+width<=582 and end<758,(kind,top,end)
        self.audit[-1]['blocks'].append(dict(kind=kind,x=x,top=top,bottom=end,items=ids or [],width=width))
    def finish(self,path):
        for i,p in enumerate(self.pdf,1):
            p.insert_text((555,775),f'{i} / {len(self.pdf)}',fontsize=8,fontname='helv',color=navy)
        self.pdf.save(path,garbage=4,deflate=True)

def dimensions(k):
    return (10.2,'MTSBody',4.5) if k=='para' else ((10,'MTSBold',4) if k=='head' else (8.9,'MTSBody',5))

def pheight(blocks):
    return sum(len(_wrap(t,260,fonts[dimensions(k)[1]],dimensions(k)[0]))*dimensions(k)[0]*1.28+dimensions(k)[2] for k,t in blocks)

def split_at(lst,measure):
    return min(range(1,len(lst)),key=lambda i:abs(measure(lst[:i])-measure(lst[i:])))

def draw_passage(b,blocks,x,y):
    for k,t in blocks:
        size,font,gap=dimensions(k)
        y=b.text(x,y,t,size,font)+gap
    return y

def qheight(rows):
    return sum(11+sum(len(_wrap(t,w,fonts['MTSBody'],9.7))*9.7*1.28+3 for t,w in [(f'{n}. {stem}',260)]+[(t,240) for t in opts]) for n,(stem,opts) in rows)

def draw_mc(b,rows,y):
    split=split_at(rows,qheight)
    peaks=[]
    for x, column in zip((36,316),(rows[:split],rows[split:])):
        top=y
        for n,(stem,opts) in column:
            top=b.text(x,top,f'{n}. {stem}',9.7)+3
            for letter,t in zip('ABCD',opts):
                b.text(x+2,top,letter,9.7,'MTSBold',14)
                top=b.text(x+18,top,t,9.7,width=242)+3
            top+=11
        b.mark('MC column',x,y,top,[r[0] for r in column])
        peaks.append(top)
    return max(peaks)

def draw_wr(b,n,stem,score,y):
    top=y
    # Preserve each bullet in the paired prompt on its own line.
    for i,part in enumerate(stem.split(' | ')):
        y=b.text(36 if i==0 else 51,y,f'{n}. {part}' if i==0 else '• '+part,10,width=540 if i==0 else 525)+2
    y=b.text(36,y,f'{score} points',8.8,'MTSBold',540)+6
    for i in range(10 if score==4 else 4):
        b.page.draw_line((36,y),(576,y),color=(.45,.48,.51),width=.45)
        y+=14
    b.mark('Written response',36,top,y,[n],540)
    return y+14

def figure(b,source,source_page,clip,y,width):
    x=(612-width)/2
    crop=fitz.Rect(clip)
    h=width*crop.height/crop.width
    b.page.show_pdf_page(fitz.Rect(x,y,x+width,y+h),source,source_page-1,clip=crop)
    b.mark('Source figure',x,y,y+h,[],width)
    return y+h+18

def make_student(grade,m,source,pages):
    b=Book()
    dataset={}
    y=62
    limit=746
    def fresh(title):
        nonlocal y
        b.new(title)
        y=64

    def section(title):
        nonlocal y
        y=b.text(36,y,title,13,'MTSBold',540)+6

    def columns(blocks):
        nonlocal y
        while blocks:
            available=limit-y-10
            options=[]
            cumulative=[0]
            for block in blocks:cumulative.append(cumulative[-1]+pheight([block]))
            for end in range(2,len(blocks)+1):
                if len(blocks)-end==1:continue
                for middle in range(1,end):
                    if blocks[middle-1][0]=='head' or blocks[end-1][0]=='head':continue
                    a,c=cumulative[middle],cumulative[end]-cumulative[middle]
                    if max(a,c)<=available:options.append((end,-abs(a-c),middle))
            if not options:
                if y<72: raise ValueError('No readable passage columns fit')
                fresh(title+' · Continued')
                continue
            end,_,split=max(options)
            ends=[]
            for x,seq in zip((36,316),(blocks[:split],blocks[split:end])):
                bottom=draw_passage(b,seq,x,y)
                b.mark('Passage column',x,y,bottom)
                ends.append(bottom)
            y=max(ends)+14
            blocks=blocks[end:]
            if len(blocks)==1:
                raise ValueError('Passage left one block')
            if blocks:fresh(title+' · Continued')

    def mc_flow(rows):
        nonlocal y
        heading='Questions · '+title
        while rows:
            usable=limit-y-22
            fits=[]
            for n in range(2,len(rows)+1):
                if len(rows)-n==1: continue
                split=split_at(rows[:n],qheight)
                height=max(qheight(rows[:split]),qheight(rows[split:n]))
                if height<=usable:fits.append(n)
            if not fits:
                fresh(heading)
                continue
            n=max(fits)
            if not b.audit[-1]['heading'].startswith('Questions ·'):
                section('Questions')
            y=draw_mc(b,rows[:n],y)+10
            rows=rows[n:]
            if rows:fresh(heading)

    def wr_flow(rows,heading):
        nonlocal y
        for n,stem,score in rows:
            prompt_lines=sum(len(_wrap(t,520,fonts['MTSBody'],10)) for t in stem.split(' | '))
            need=prompt_lines*13+29+14*(10 if score==4 else 4)
            if y+need>limit: fresh(heading)
            y=draw_wr(b,n,stem,score,y)

    for index,p in enumerate(m['passages']):
        title=p['passage_title']
        if grade==4 and index>=2:break
        qs=questions(pages,p['question_pages'])
        ids=[x['source'] for x in p['question_map']]
        assert sorted(qs)==sorted(ids)
        dataset.update(qs)
        author='by '+authors[grade][index]
        if index==0:
            fresh(title)
            y=b.text(36,y,author,9.7,width=540)+5
            y=b.text(36,y,f'MTS ELA Mock Test  |  Grade {grade}  |  New York 2022',10,'MTSBold',540)+3
            y=b.text(36,y,'Name ______________________________     Date __________________',9.7,width=540)+10
        elif y<=(490 if p['genre']=='Poetry' else 555):
            section(title)
            y=b.text(36,y,author,9.7,width=540)+8
        else:
            fresh(title)
            y=b.text(36,y,author,9.7,width=540)+8
        if (grade,index) in contexts:
            y=b.text(36,y,contexts[grade,index],9.8,width=540)+8
        if p['genre']=='Poetry':
            stanzas,gloss=poem_blocks(pages)
            ends=[]
            for x,seq in zip((36,316),(stanzas[:3],stanzas[3:])):
                bottom=y
                for stanza in seq:
                    for _,line in stanza:
                        bottom=b.text(x,bottom,line,10.4)
                    bottom+=8
                b.mark('Poetry column',x,y,bottom)
                ends.append(bottom)
            y=max(ends)+3
            for note in gloss: y=b.text(36,y,note,9,width=540)
            y+=22
        else:
            columns(passage_blocks(pages,grade,index,p))
        mc=[(n,qs[n]) for n in ids if qs[n][1]]
        wr=[(n,qs[n][0],r['credit_value']) for n,r in zip(ids,p['question_map']) if not qs[n][1]]
        if mc:
            asset={(4,0):(10,(174,485,445,671),270),(5,1):(22,(130,233,482,470),340)}.get((grade,index))
            if asset:
                pg,clip,w=asset
                if y+w*(clip[3]-clip[1])/(clip[2]-clip[0])>limit-6:
                    fresh('Questions · '+title)
                y=figure(b,source,pg,clip,y,w)
            mc_flow(mc)
        else:
            wr_flow(wr,'Questions · '+title)
    if grade==4:
        fresh('Paired fables')
        wr=[]
        bottoms=[]
        for x,index in zip((36,316),(2,3)):
            p=m['passages'][index]
            top=b.text(x,y,p['passage_title'],12,'MTSBold',260)+4
            top=b.text(x,top,'by '+authors[grade][index],9.7)+7
            bottom=draw_passage(b,passage_blocks(pages,grade,index,p),x,top)
            b.mark('Passage column',x,y,bottom)
            bottoms.append(bottom)
            qs=questions(pages,p['question_pages'])
            dataset.update(qs)
            wr.extend((q['source'],qs[q['source']][0],q['credit_value']) for q in p['question_map'])
        y=max(bottoms)+17
        n=31
        stem=questions(pages,m['paired_questions'][0]['question_pages'])[n][0]
        stem=stem.replace('be sure to explain','be sure to | explain').replace(' describe how',' | describe how').replace(' use details from both stories to support your response',' | use details from both stories to support your response')
        dataset[n]=(stem,[])
        wr_flow(wr+[(31,stem,4)],'Questions · The paired fables')
    b.finish(out/f'Grade-{grade}-ELA-Student.pdf')
    return dataset,b.audit

if __name__=='__main__':
 for grade in (4,5,6):
    m=json.loads((root/f'Grade-{grade}-Content-Review.json').read_text())
    src=source('ELA', grade)
    assert hashlib.sha256(src.read_bytes()).hexdigest()==m['source_sha256']
    pages=(WORK / f'ELA-{grade}.txt').read_text().split('\f')
    with fitz.open(src) as d: dataset,audit=make_student(grade,m,d,pages)
    (out/f'Grade-{grade}-layout.json').write_text(json.dumps(audit,indent=2))
    (WORK/f'questions{grade}.json').write_text(json.dumps(dataset,ensure_ascii=False,indent=2))
