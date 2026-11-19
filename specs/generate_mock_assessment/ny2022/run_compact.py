from pathlib import Path
from hashlib import sha256
import json,re
import fitz
import numpy as np
from teacher_key import render_teacher_key
from reflow_compact import compose, render
from paths import OUTPUT, WORK, source
sets={
4:([1,2,8,9,13,14,16,17,21,22,23,27,28,31,35,37],[39,40,41,45]),
5:([1,2,3,6,7,13,15,18,19,21,23,32,33,34,37,38],[39,41,43,45]),
6:([1,2,3,4,5,11,12,15,17,22,26,28,33,35,37,38],[40,42,44,46])}
solutions={
4:{'39':'54 divided by 9 = 6 tickets.','40':'180 degrees minus 143 degrees = 37 degrees.','41':'Figure B. Folding the square on any dotted line makes the two halves coincide.','45':'(9 - 5) times 3/4 = 3 inches.'},
5:{'39':'12 times 20 = 240 quarts, or 60 gallons. At 1 teaspoon per 10 gallons, use 6 teaspoons.','41':'4 ones is 10 times 4 tenths.','43':'Each tower has 2 times 2 times 5 = 20 unit cubes. Four towers have a volume of 80 cubic units.','45':'Add the top volume (2 times 5 times 3 = 30) and bottom volume (3 times 5 times 4 = 60) to get 90 cubic inches. The taller top adds 2 times 5 times 1 = 10 cubic inches.'},
6:{'40':'Travel 7 units south and 10 units west. At 3 yards per unit the distance is 51 yards.','42':'The cereal box is 186 cubic inches. The pastry box is 539/18 cubic inches. The difference is 2,809/18 = 156 1/18 cubic inches.','44':'40 times 12/60 = 8 miles. 50 times 15/60 = 12.5 miles. Total: 20.5 miles.','46':'y = 160x. At x = 12, y = 160 times 12 = 1,920 pencils.'}}
def ink(page, rect):
 pix=page.get_pixmap(clip=rect, colorspace=fitz.csGRAY)
 a=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width)
 return a<235,pix.x,pix.y
for grade,(mc,cr) in sets.items():
 path=source('Math', grade)
 doc=fitz.open(path)
 source_text=(WORK / f'Math-{grade}.txt').read_text()
 keys={int(k):v for k,v in re.findall(r'^\s*(\d+)\s+Multiple Choice\s+([A-D])',source_text,re.M)}
 points={int(k):int(v) for k,v in re.findall(r'^\s*(\d+)\s+Constructed Response\s+(\d)',source_text,re.M)}
 positions={}
 for page in doc:
  if page.number<6 or page.number>=len(doc)-2: continue
  labels=[]
  for block in page.get_text('dict')['blocks']:
   for line in block.get('lines',[]):
    for span in line['spans']:
     x,y=span['bbox'][:2]
     if 39<x<51 and y>=62 and re.fullmatch(r'\d{1,2}',span['text'].strip()):
      labels.append((int(span['text']),y-7))
  if (grade,page.number+1) in {(4,24),(6,25)}: labels=[(41 if grade==4 else 40,57)]
  labels.sort(key=lambda x:x[1])
  for (q,y),(_,end) in zip(labels,labels[1:]+[(0,695)]):
   if q in mc+cr: positions[q]=(page.number+1,y,end-2)
 regions=[]
 for q in mc+cr:
  n,top,bot=positions[q]
  pix,x,y=ink(doc[n-1],fitz.Rect(35,top,577,bot))
  if q in cr:
   # Split only the largest empty vertical gaps, retaining all printed ink.
   threshold=44 if grade==4 else 27
  else: threshold=16
  rows=np.where(pix.any(axis=1))[0]
  # Last-page STOP and navigation are outside the assessment region.
  groups=np.split(rows,np.where(np.diff(rows)>threshold)[0]+1)
  parts=[]
  for group in groups:
   if group.size==0:continue
   cols=np.where(pix[group[0]:group[-1]+1].any(axis=0))[0]
   parts.append([float(x+cols[0]-6),float(y+group[0]-2),float(x+cols[-1]+7),float(y+group[-1]+3)])
  regions.append({'id':q,'source_page':n,'parts':parts,'part_gap_pt':0 if q in mc else 7})
 normalized=compose(doc,regions,mc)
 print([(r["id"],round(r["bounds"][2]*.75)) for r in regions])
 normalized_path=WORK / f'vector-{grade}.pdf'
 normalized.save(normalized_path)
 title=f'MTS Math Mock Assessment | Grade {grade} | New York 2022'
 manifest={'title':title,'source_sha256':sha256(normalized_path.read_bytes()).hexdigest(),'original_source_sha256':sha256(path.read_bytes()).hexdigest(),'regions':regions,'scale':0.70,'maximum_pages':4}
 # print(grade,[(r["id"],[(round(p[2]-p[0]),round(p[3]-p[1])) for p in r["parts"]]) for r in regions])
 out=OUTPUT / 'math'
 placement=render(normalized,regions,out/f'Grade-{grade}-Student.pdf',grade,title)
 items=[{'output_number':q,'type':'multiple_choice','official_key':keys[q],'points':1} for q in mc]+[{'output_number':q,'type':'constructed_response','official_key':None,'points':points[q]} for q in cr]
 render_teacher_key(items,solutions[grade],out/f'Grade-{grade}-Teacher-Key.pdf',title=title)
 (out/f'Grade-{grade}-Review.json').write_text(json.dumps({'manifest':manifest,'placements':placement,'items':items},indent=2))
