import json
from render_compact import Book, out, root
from paths import WORK
notes={
4:{
1:('Author’s support','¶1–7','Expect examples of different caregiving behaviors.','The article gives several different jobs, from carrying young to teaching them to hunt. The other choices focus on size, appearance, or growth.'),
2:('Compare details','¶4 and ¶6','Look for a way both fathers physically protect young.','The frog holds babies in its throat and the penguin shelters its egg beneath its skin. The other choices are absent from one or both examples.'),
3:('Vocabulary in context','¶6','Look for what the skin does to the egg.','Belly skin covers the egg to keep it warm. It is neither a fastener, fabric, nor a book part.'),
4:('Explicit detail','¶7','Look for how the fox teaches the kits.','He buries meat and hides it under twigs. The others misstate who does what or when.'),
5:('Text feature','Table and article','Expect new examples of the same behavior pattern.','The table adds seahorse, owl, rhea, and jacana examples. It does not chiefly compare parents, counts, or sizes.'),
6:('Central idea','Entire article','Expect a statement broad enough to cover every example.','Each paragraph shows an unusual caregiving behavior. The other options narrow the article to one animal or one kind of care.'),
19:('Motivation','¶4','Find what the author thought of the story he sent.','He thought the story was funny and good enough for a book. Illustrations and other details do not explain the decision as directly.'),
20:('Evidence','¶5','Find an example of trying again before success.','The four submissions show perseverance until acceptance. A single rejection or success alone does not demonstrate the repeated effort.'),
21:('Vocabulary in context','¶6','Look for where the writing appeared and who could read it.','His story appeared in a newspaper. The term refers to work made available to readers, beyond simply writing it.'),
22:('Structure','¶6','Check the sequence of events.','The paragraph traces writing milestones as they happened. It does not principally compare, classify, or explain a cause.'),
23:('Author’s purpose','¶7','Find what the author values after becoming a writer.','He still enjoys seeing his work appear in print and on screen. Other options miss that continuing satisfaction.'),
24:('Evidence for central idea','Entire memoir and ¶7','Expect a detail linking persistence and reward.','The sentence about rewards after waiting captures the lesson. The other quotations recount individual events.')},
5:{
1:('Theme','Whole narrative','Expect a lesson about Sali’s efforts and resourcefulness.','She works for the cloth and seeks help making her garment. The other options elevate secrecy, fear, or cost beyond their role.'),
2:('Figurative language','¶1','Look for visual features of a flame.','A flame suggests vivid color and motion. The comparison does not identify how the cloth feels, how it is made, or what it costs.'),
3:('Character inference','¶3','Infer a trait from how Sali imagines using the fabric.','Her imaginative use of the cloth shows thoughtfulness and creativity. The other traits fit the details less directly.'),
4:('Point of view','¶13','Locate what Sali has yet to figure out.','Having earned the cloth, Sali is unsure how to get the garment made. The other options give her stronger plans or motives than she expresses.'),
5:('Character inference','Shopkeeper and tailor episodes','Compare how both adults respond to Sali.','The shopkeeper rewards her work and the tailor helps her make the garment. Their actions show generosity and fairness.'),
6:('Structure','¶7 and ¶17','Identify the action in each scene that moves Sali toward her goal.','She asks to work for cloth and later asks the tailor for help. Both paragraphs develop her solution.'),
7:('Evidence for theme','¶11 and whole story','Look for a line connecting her effort to progress.','The shopkeeper directly credits Sali’s work when awarding cloth. The other quotations do not link sustained effort to a result as clearly.'),
29:('Vocabulary in context','¶1','Expect a word meaning beginning to form.','The storm is developing as the temperature drops and wind strengthens. The alternatives do not fit that sequence.'),
30:('Vocabulary in context','¶5','Use the sponge comparison.','A sponge absorbs water, matching the way the air takes in moisture. Other meanings do not fit the process.'),
31:('Cause and effect','¶5','Look for what changes when the wind crosses more lake water.','Air picks up more water if it travels over more of the lake. The other options do not express that relationship.'),
32:('Author’s purpose','¶7','Expect a description of how Buffalo deals with frequent storms.','The paragraph presents storms and snow removal as familiar parts of life. It gives no detailed removal method or comparison of cities.'),
33:('Diagram evidence','Diagram and ¶4','Identify a visual detail that adds to the text.','The staged diagram explicitly shows clouds increasing in size. The other options describe information the article already supplies.'),
34:('Summary','¶3–5','Choose the core conditions over a local example.','Cold air passing over warm water explains the mechanism. Buffalo and seasonal details illustrate it.'),
35:('Central idea','Entire article','Choose the explanation that covers wind, water, and temperature.','The article describes a set of conditions that creates lake-effect snow. The other choices are too narrow or make unsupported claims.')},
6:{
8:('Central claim','¶3–5','Expect a claim about why bats need protection.','Misunderstandings cause people to harm bats, and Tuttle works to educate them. The other choices shift attention to careers or narrower facts.'),
9:('Inference from detail','¶3','Infer what the debris means after the bats disappear.','The cartridges and firework wrappers point to human interference. The paragraph does not say the bats left for a natural reason.'),
10:('Word choice','¶3–4','Look for what the two words imply about people’s beliefs.','Both terms show that fear and myths drove people’s behavior. They do not suggest that bats deserved their reputation.'),
11:('Text evidence','¶3','Find the quotation that supplies a reason for the ignorance.','Fear helps explain why people misunderstood and harmed bats. The other quotations show a research result, Tuttle’s reaction, or bat habits.'),
12:('Paragraph function','¶5','Ask what Tuttle’s photographs accomplish.','His natural photographs let people see bats at ease. The paragraph centers on changing public understanding.'),
13:('Summary','Entire article','Choose a detail that joins Tuttle’s research with conservation.','Studying bats and educating the public covers both halves of the excerpt. The other options isolate narrower facts.'),
14:('Development of ideas','¶4–5','Look for a sequence that supports the value of education.','Tuttle starts an organization and publishes photos to correct misconceptions. Other choices isolate examples or draw a less central lesson.'),
22:('Vocabulary in context','¶3','Use the clue that the paper might not withstand folding.','The old paper can break easily. Its value, temperature, or readability is separate.'),
23:('Character response','¶3–7','Expect a trait shown by repeated examination.','Milo studies the watermark and turns the chart to recognize the waterway. These actions show curiosity.'),
24:('Plot development','¶8–10','Identify the new event that interrupts his examination.','An unidentified guest enters and appears to search for the wallet. Milo’s discovery occurred earlier.'),
25:('Tone','¶10','Notice what the character and the reader cannot see or know.','The shadow and Milo’s decision to hide heighten mystery. The scene does not resolve the uncertainty or turn it into humor.'),
26:('Plot development','¶9–11','Track what Milo does instead of returning the wallet.','He hides, waits, and pockets the wallet before leaving. This implies he intends to keep it for now.'),
27:('Point of view','¶3–11','Look at how the narration gives access to Milo’s interpretation.','It reveals what he thinks about the chart and why he suspects the guest wants it. The guest’s private thoughts are unavailable.'),
28:('Summary','¶8–11','Choose the event that advances the conflict.','Hiding until the person leaves is central to the encounter. Other details describe narrower parts of examining the chart.')}}
big={
4:[('Animal fathers care for their young in varied and surprising ways.','¶1–2 introduce the idea. ¶3–7 give examples. The table extends the list.'),('Practice and persistence helped the author become a published writer.','¶1–4 trace early storytelling and submissions. ¶5–8 trace setbacks, publication, and rewards.'),('The Fox uses flattery to get the Crow’s cheese.','¶1–2 establish the prize. ¶3–5 build the trick. ¶6–7 show the result.'),('The otters’ quarrel lets a self-serving judge take their catch.','¶1–4 present the dispute. ¶5–11 stage the division. ¶12–13 reveal the trick.')],
5:[('Sali uses imagination and determination to turn a scrap of cloth into a garment.','¶1–5 establish the goal. ¶6–12 show her work. ¶13–21 follow her effort to get the garment made.'),('Lake-effect snow forms when cold air takes up moisture from warmer lake water.','¶1–3 introduce a storm. ¶4–6 explain the mechanism and conditions. ¶7 shows life in Buffalo.'),('The raindrops’ transformation turns frustration into delight.','Lines 1–8 show discontent. Lines 9–16 show the promise and changed mood. Lines 17–24 reveal snow.')],
6:[('Tuttle’s research and outreach teach people why bats are worth protecting.','¶1–2 establish his research. ¶3–4 show harm and response. ¶5 shows the value of photography.'),('A strange chart and an unidentified guest turn Milo’s discovery into a mystery.','¶1–3 reveal the wallet and map. ¶4–7 show his investigation. ¶8–11 introduce the searcher and concealment.'),('The carpenter discovers that the oaks can still help people through a new use for their wood.','¶1–3 establish the loss. ¶4–16 introduce the promise and magic. ¶17–20 show the shoes and prosperity.')]}
for g in (4,5,6):
    m=json.loads((root/f'Grade-{g}-Content-Review.json').read_text())
    questions_data=json.loads((WORK / f'questions{g}.json').read_text())
    b=Book()
    b.new(f'MTS ELA Teacher Key · Grade {g}')
    y=62
    key=[]
    for index,p in enumerate(m['passages']+([dict(passage_title='Paired fable response',question_map=m['paired_questions'])] if m['paired_questions'] else [])):
        if y>580: b.new(f'Teacher Key · Grade {g}');y=65
        y=b.text(36,y,p['passage_title'],13,'MTSBold',540)+6
        if index<len(big[g]):
            overview,outline=big[g][index]
            y=b.text(36,y,'Big picture · '+overview,10,width=540)+3
            y=b.text(36,y,'Passage map · '+outline,10,width=540)+12
        for q in p['question_map']:
            n=q['source']
            if y>635: b.new(f'Teacher Key · Grade {g}');y=65
            if q['response_type']=='multiple_choice':
                typ,scope,pred,reason=notes[g][n]
                letter=q['official_answer']
                answer=questions_data[str(n)][1][ord(letter)-65].strip()
                key.append(f'{n} {letter}')
                y=b.text(36,y,f'Q{n}  ·  {typ}  ·  {scope}',10.5,'MTSBold',540)+2
                y=b.text(36,y,'Prediction · '+pred,10,width=540)+2
                y=b.text(36,y,'Evidence and elimination · '+reason,10,width=540)+2
                y=b.text(36,y,f'Answer {letter} · {answer}',10,width=540)+13
            else:
                y=b.text(36,y,f'Q{n}  ·  {q["credit_value"]} points  ·  MTS Model Response',10.5,'MTSBold',540)+3
                y=b.text(36,y,q['model_response'],10,width=540)+13
    if y>660: b.new(f'Teacher Key · Grade {g}');y=65
    y=b.text(36,y,'Official multiple-choice key',11,'MTSBold',540)+3
    b.text(36,y,'   |   '.join(key),10,width=540)
    b.finish(out/f'Grade-{g}-ELA-Teacher-Key.pdf')
