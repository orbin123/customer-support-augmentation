"""Render the captured Chrome walkthrough. Requires Pillow and ffmpeg.
Run: uv run --with pillow python media/render_demo.py
Raw captures live in ignored media/source; final assets are committed.
"""
from pathlib import Path
import bisect
import json
import subprocess
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'source'
W, H, FPS = 1920, 1080, 24
FONT = '/System/Library/Fonts/Supplemental/Arial.ttf'
font = ImageFont.truetype(FONT, 32)
small = ImageFont.truetype(FONT, 26)
heading = ImageFont.truetype(FONT, 40)
clips = {c['name']: c for c in json.loads((SOURCE/'clips.json').read_text())}
# Durations of captured clips are preserved, rounded to the output frame boundary.
# Still inserts are explicitly identified and held for reading.
sequence = [
 ('still', 'frame-00020.png', 7, '01 / A customer asks a product question',
  ['From orbinsunny7306@gmail.com to orbinsunny7983@gmail.com', 'A 90 kg rider asks for a board recommendation and included accessories.']),
 ('still','received.png',5,'02 / The support mailbox receives it',
  ['The real query arrives in the integrated Gmail account.', 'The worker reads the thread and classifies the latest customer message.']),
 ('clip','support-reply',None,'03 / A grounded reply, sent automatically',
  ['The agent recommends the 11-foot All-round and lists the included accessories.', 'The thread receives ai-processed; this question does not require escalation.']),
 ('clip','customer-reply',None,'04 / The customer receives the answer',
  ['The reply arrives in the original Gmail conversation.', 'Waiting time between sending and delivery has been cut from this walkthrough.']),
 ('clip','ticket',None,'05 / A saved conversation for the support team',
  ['Ticket 102 is answered in the paddle-boards category.', 'The dashboard stores both messages. Unrelated ticket rows are masked.']),
 ('clip','sizes',None,'06 / Product facts come from the knowledge base',
  ['The classifier selects paddle-boards; the agent retrieves the relevant section.', 'For a 90 kg rider, the 11-foot board supports up to 110 kg.']),
 ('clip','accessories',None,'07 / Maintained content shapes the response',
  ['The included-accessories entry supplies the second part of the answer.', 'Operators can edit entries here; this walkthrough leaves their content unchanged.']),
 ('still','events.png',7,'08 / Processing is observable',
  ['Event 137 completed on its first attempt with action=reply.', 'Events show status, attempts, errors and creation time; decisions are stored in the API.']),
 ('still','../evaluation-summary.png',12,'09 / Evals check the output decisions',
  ['Pydantic Evals checks section and action across six golden emails.', 'Supplied run: 11/12 assertions passed (91.7%). One angry-refund assertion failed.']),
]

def load(path, name):
    im = Image.open(path).convert('RGB')
    if name == 'frame-00020.png':
        im = im.crop((0,354,im.width,im.height))
    if name == 'ticket':
        # Redact unrelated subjects and addresses while preserving the selected row.
        d=ImageDraw.Draw(im)
        d.rectangle((165,178,710,287), fill='#171b24')
        d.rectangle((165,330,710,im.height), fill='#171b24')
        d.text((185,355),'Unrelated tickets hidden',font=ImageFont.truetype(FONT,20),fill='#a5b0c2')
    return im

def compose(im,title,lines):
    canvas=Image.new('RGB',(W,H),'#0c1220');d=ImageDraw.Draw(canvas)
    d.rectangle((55,38,63,76),fill='#58dfc0')
    d.text((82,34),title,font=heading,fill='#f1f6fd')
    ratio = min(1810/im.width, 830/im.height)
    im = im.resize((round(im.width*ratio),round(im.height*ratio)),Image.Resampling.LANCZOS)
    canvas.paste(im,((W-im.width)//2,105+(830-im.height)//2))
    d.line((55,957,1865,957),fill='#293448',width=2)
    for y,line in zip((979,1023),lines):
        assert d.textbbox((0,0),line,font=font)[2]<1810
        d.text((W//2,y),line,font=font,fill='#e2eaf5',anchor='mt')
    return canvas

out=ROOT/'customer-support-demo.mp4'
command=['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','21','-pix_fmt','yuv420p','-movflags','+faststart',str(out)]
proc=subprocess.Popen(command,stdin=subprocess.PIPE)
timeline=[];cursor=0
for kind,name,duration,title,lines in sequence:
    if kind=='clip':
        clip=clips[name];duration=clip['duration'];shots=clip['shots'];times=[s['time'] for s in shots]
    count=round(duration*FPS); timeline.append({'start':cursor/FPS,'end':(cursor+count)/FPS,'title':title,'caption':lines,'source':name,'kind':kind})
    prev=None;frame=None
    for i in range(count):
        if kind=='clip':
            j=max(0,bisect.bisect_right(times,i/FPS)-1)
            path=SOURCE/name/Path(shots[j]['file']).name
        else:path=SOURCE/name
        if path!=prev:
            frame=compose(load(path,name),title,lines);prev=path
        if i==0:
            frame.save(SOURCE/(Path(name).stem+'-review.jpg'))
            if name=='support-reply': frame.save(ROOT/'demo-poster.png')
        proc.stdin.write(frame.tobytes())
    cursor+=count
    print(title,round(cursor/FPS,2),flush=True)
proc.stdin.close()
if proc.wait(): raise RuntimeError('ffmpeg failed')
(ROOT/'timeline.json').write_text(json.dumps(timeline,indent=2)+'\n')
print(f'Runtime: {cursor/FPS:.3f}s')
