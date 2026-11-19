from pathlib import Path
import fitz
import numpy as np

SCALE=.70
COLUMN_WIDTH=286
SOURCE_WIDTH=272/SCALE

def pixel_ink(page, clip):
    pix=page.get_pixmap(matrix=fitz.Matrix(3,3),clip=clip,colorspace=fitz.csGRAY)
    values=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width)
    return values<215,pix.x,pix.y

def vector_rows(page, clip, allow_image_text=False):
    if clip.width<=SOURCE_WIDTH:
        return [[(clip,0,0)]]
    a,px,py=pixel_ink(page,clip)
    occupied=np.flatnonzero(a.any(axis=1))
    bands=np.split(occupied,np.where(np.diff(occupied)>1)[0]+1)
    lines=[]
    for band in bands:
        cols=np.flatnonzero(a[band[0]:band[-1]+1].any(axis=0))
        l,r=(px+cols[0])/3,(px+cols[-1]+1)/3
        top,bot=(py+band[0])/3,(py+band[-1]+1)/3
        if r-l > SOURCE_WIDTH-6:
            hits=[w for w in page.get_text('words',clip=fitz.Rect(clip.x0,top-7,clip.x1,bot+7)) if w[1]<bot and w[3]>top]
            if bot-top<2 and len(hits)==0:
                lines.append((top,bot,[fitz.Rect(l-1,top-.33,l+SOURCE_WIDTH-4,bot+.33)]))
                continue
            if bot-top>31 or (len(hits)<4 and not (allow_image_text and 3<bot-top<15)):
                return [[(clip,0,0)]]
            mini=np.split(cols,np.where(np.diff(cols)>8)[0]+1)
            starts=[(px+x[0])/3 for x in mini]
            ends=[(px+x[-1]+1)/3 for x in mini]
            if max(e-s for s,e in zip(starts,ends))>SOURCE_WIDTH-8:
                return [[(clip,0,0)]]
            cuts=[(starts[i+1]+ends[i])/2 for i in range(len(starts)-1)]
            cuts=[l-1]+cuts+[r+1]
            groups=[]
            start=cuts[0]
            for i in range(1,len(cuts)):
                if cuts[i]-start>SOURCE_WIDTH-3:
                    end=cuts[i-1]
                    groups.append(fitz.Rect(start,top-.33,end,bot+.33))
                    start=end
            groups.append(fitz.Rect(start,top-.33,cuts[-1],bot+.33))
            lines.append((top,bot,groups))
    if not lines:
        return [[(clip,0,0)]]
    result=[]
    cursor=clip.y0
    for top,bot,groups in lines:
        if top-cursor>0.7:
            before=fitz.Rect(clip.x0,cursor,clip.x1,top-.33)
            result.append([(before,0,0)])
        result.extend([[(group,2,0)] for group in groups])
        cursor=bot+.33
    if clip.y1-cursor>0.7:
        result.append([(fitz.Rect(clip.x0,cursor,clip.x1,clip.y1),0,0)])
    # Tighten untouched bands by ink while preserving their original internal geometry.
    tightened=[]
    for [(rect,indent,_)] in result:
        mask,x,y=pixel_ink(page,rect)
        where=np.where(mask)
        if not len(where[0]): continue
        left=max(rect.x0,(x+int(where[1].min()))/3-3)
        right=min(rect.x1,(x+int(where[1].max())+1)/3+3)
        tightened.append([(fitz.Rect(left,rect.y0,right,rect.y1),indent,0)])
    return tightened

def compose(doc, regions, multiple_choice):
    normalized=fitz.open()
    for region in regions:
        ident=region['id']
        original=doc[region['source_page']-1]
        clips=[fitz.Rect(part) for part in region['parts']]
        if len(doc)==34 and ident==46:
            # The equation underline is blank response space. Shorten its right end.
            section=clips[0]
            clips[0:1]=[
                fitz.Rect(section.x0,section.y0,section.x1,100),
                fitz.Rect(68,100,68+SOURCE_WIDTH-7,section.y1),
            ]
        label=None
        if clips[0].x0<63 and clips[0].width>SOURCE_WIDTH:
            first=clips[0]
            label=fitz.Rect(first.x0,first.y0,64,min(first.y1,first.y0+34))
            clips[0]=fitz.Rect(64,first.y0,first.x1,first.y1)
        rows=[]
        pack_choices=ident in multiple_choice and len(clips)>=5 and all(c.height<=33 for c in clips[-4:]) and sum(c.width+7 for c in clips[-4:])<=SOURCE_WIDTH
        for clip in (clips[:-4] if pack_choices else clips):
            rows.extend(vector_rows(original,clip, allow_image_text=(len(doc)==31 and original.number==23 and ident==41)))
        if pack_choices:
            rows.append([(c,0,7) for c in clips[-4:]])
        if label is not None:
            rows.insert(0,[(label,0,0)])
        width=max(sum(c.width+offset+gap for c,offset,gap in row)-row[-1][2] for row in rows)
        heights=[max(c.height for c,*_ in row)+2 for row in rows]
        if ident not in multiple_choice:
            for index,row in enumerate(rows):
                if len(row)==1 and row[0][0].height<=8 and row[0][0].width>240:
                    heights[index]+=16
        work=23 if ident not in multiple_choice and len(rows)>1 and rows[-1][0][0].height<27 else 0
        height=sum(heights)+work
        p=normalized.new_page(width=width,height=height)
        y=0
        for index,(row,h) in enumerate(zip(rows,heights)):
            if index==len(rows)-1:
                y+=work
            x=0
            for clip,offset,gap in row:
                x+=offset
                p.show_pdf_page(fitz.Rect(x,y,x+clip.width,y+clip.height),doc,original.number,clip=clip)
                x+=clip.width+gap
            y+=h
        region['original_source_page']=region['source_page']
        region['original_parts']=region.pop('parts')
        region['source_page']=len(normalized)
        region['bounds']=list(p.rect)
    return normalized

def render(doc, regions, destination, grade, title):
    entries=[(region,doc[index].rect.width*SCALE,doc[index].rect.height*SCALE) for index,region in enumerate(regions)]
    out=fitz.open()
    placements=[]
    y=68
    gap=8
    page=None
    split={4:31,5:32,6:33}[grade]
    approved_full=[]
    def fresh():
        nonlocal page,y
        page=out.new_page(width=612,height=792)
        page.insert_text((36,33),title,fontsize=12,fontname='hebo',color=(.11,.21,.34))
        if page.number==0:
            page.insert_text((36,50),'Name ___________________________   Date ______________',fontsize=9)
        page.insert_text((555,774),str(len(out)),fontsize=9)
        y=68
    def place(index,x,top):
        region,w,h=entries[index]
        q=region['id']
        if q in (1,split):
            label='SESSION 1' if q==1 else 'SESSION 2'
            if grade==6 and q==split: label+='  |  Calculator available'
            page.insert_text((x,top+7),label,fontsize=8,color=(.1,.22,.36))
            top+=13
        rect=fitz.Rect(x,top,x+w,top+h)
        if rect.x1>594 or rect.y1>754: raise ValueError((grade,q,rect))
        page.show_pdf_page(rect,doc,index)
        placements.append({'id':q,'page':len(out),'bounds':list(rect),'scale':SCALE})
    def height(i):
        return entries[i][2]+gap+(13 if entries[i][0]['id'] in (1,split) else 0)
    fresh()
    i=0
    while i<len(entries):
        if grade==5 and entries[i][0]['id']==41 and y>68:
            fresh()
        if entries[i][1]>COLUMN_WIDTH:
            if y+height(i)>754: fresh()
            place(i,18,y)
            approved_full.append(entries[i][0]['id'])
            y+=height(i)
            i+=1
            continue
        stop=i
        while stop<len(entries) and entries[stop][1]<=COLUMN_WIDTH and (stop==i or grade!=5 or entries[stop][0]['id']!=41):
            stop+=1
        candidates=[]
        for end in range(i+1,stop+1):
            for middle in range(i+1,end+1):
                left=sum(height(k) for k in range(i,middle))
                right=sum(height(k) for k in range(middle,end))
                if y+max(left,right)<=754:
                    candidates.append((end,-max(left,right),middle))
        if not candidates:
            fresh()
            continue
        end,neg_height,middle=max(candidates)
        for x,first,last in ((18,i,middle),(308,middle,end)):
            top=y
            for k in range(first,last):
                place(k,x,top)
                top+=height(k)
        y-=neg_height
        i=end
    if len(out)>4: raise ValueError(f'Grade {grade} needs {len(out)} pages')
    out.save(destination,garbage=4,deflate=True)
    print(grade,len(out),'full-width',approved_full)
    return placements
