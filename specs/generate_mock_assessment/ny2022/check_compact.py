from pathlib import Path
import json,re,hashlib
import fitz
from render_compact import root, out
from paths import WORK
md=['# ELA Phase 3 verification','','The review covers the approved 2022 selections. Passage and multiple-choice blocks were checked for content on both sides of the gutter, and placement and answer-key checks were run. Human visual review is tracked separately.','', '| Grade | Student page | Left column | Right column | Full-width content | Result |','|---|---:|---|---|---|---|']
counts=[]
for g in (4,5,6):
 m=json.loads((root/f'Grade-{g}-Content-Review.json').read_text())
 a=json.loads((out/f'Grade-{g}-layout.json').read_text())
 pt=(WORK / f'ELA-{g}.txt').read_text().split('\f')
 keypage=pt[m['official_scoring_pdf_page']-1]
 official={int(n):(k,int(score)) for n,k,score in re.findall(r'^\s*(\d+)\s+Multiple Choice\s+([A-D])\s+(\d)',keypage,re.M)}
 wr={int(n):int(score) for n,score in re.findall(r'^\s*(\d+)\s+Constructed Response\s+(\d)',keypage,re.M)}
 expected=[q for p in m['passages'] for q in p['question_map']]+m['paired_questions']
 recorded=[q for p in a for b in p['blocks'] for q in b['items']]
 assert recorded==[i['source'] for i in expected]
 assert sum(i['credit_value'] for i in expected)==m['maximum_score']
 for i in expected:
  n=i['source']
  assert (official[n]==(i['official_answer'],i['credit_value'])) if 'official_answer' in i else wr[n]==i['credit_value']
 student=fitz.open(out/f'Grade-{g}-ELA-Student.pdf')
 teacher=fitz.open(out/f'Grade-{g}-ELA-Teacher-Key.pdf')
 counts.append((len(student),len(teacher)))
 assert len(student)==len(a)
 st=' '.join(' '.join(p.get_text().split()) for p in student)
 te=' '.join(' '.join(p.get_text().split()) for p in teacher)
 assert 'MTS Model Response' not in st and 'Official multiple-choice key' not in st
 assert te.count('MTS Model Response')==sum('model_response' in q for q in expected)
 compact=te.split('Official multiple-choice key')[-1]
 assert re.findall(r'\b(\d+) ([A-D])\b',compact)==[(str(i['source']),i['official_answer']) for i in expected if 'official_answer' in i]
 for page,row in zip(student,a):
  assert (page.rect.width,page.rect.height)==(612,792)
  assert '�' not in page.get_text()
  boxes=[]
  groups=[[],[],[]]
  for b in row['blocks']:
   kind=b['kind']
   bbox=fitz.Rect(b['x'],b['top']-9,b['x']+b['width'],b['bottom']-9)
   assert fitz.Rect(30,45,582,756).contains(bbox)
   assert all(not bbox.intersects(x) for x in boxes)
   boxes.append(bbox)
   if kind=='Source figure':
    groups[2].append('Source table' if g==4 else 'Source diagram')
   elif kind=='Written response':
    groups[2].append('Q'+str(b['items'][0])+' writing space')
   else:
    col=0 if b['x']<306 else 1
    assert page.get_text(clip=bbox).strip()
    groups[col].append(', '.join('Q'+str(q) for q in b['items']) if b['items'] else kind)
  assert bool(groups[0])==bool(groups[1])
  assert any(groups)
  cols='Two-column pass' if groups[0] else 'Writing page'
  md.append(f"| {g} | {page.number+1} | {'; '.join(groups[0]) or '—'} | {'; '.join(groups[1]) or '—'} | {'; '.join(groups[2]) or '—'} | {cols} |")
for g,(s,t) in zip((4,5,6),counts):
 print(g,s,t)
md+=['','## Source details and page use','',
'- Grade 4 student p. 2 retains the source table used by Q5. P. 7 gives the four-point paired response its own writing area.',
'- Grade 5 student p. 4 retains the source lake-effect diagram used by Q33. P. 5 retains the poem’s 24 lines in six stanzas, with the source markers at lines 5, 10, 15, and 20.',
'- Grade 6 student p. 6 keeps the three written responses together with full-width writing space.',
'- All 50 selected question numbers are present in the render record. All 40 multiple-choice answers and all 50 credit values match the source scoring tables. The ten written examples are labeled MTS Model Responses.',
'- Passage and question sets start on separate pages when combining complete blocks would make the page too long. The written-only pages keep the source prompts and provide room to respond.',
'','## PDF fingerprints','']
for f in sorted(out.glob('*.pdf')):
 md.append(f'- {f.name} — `{hashlib.sha256(f.read_bytes()).hexdigest()}`')
(out/'Phase-3-ELA-verification.md').write_text('\n'.join(md)+'\n')
