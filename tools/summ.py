import sys,kv,os
def summary(path, depth=2):
    t=open(path,encoding='utf-8',errors='replace').read()
    root=kv.parse(t)
    body=next(e[1] for e in root if isinstance(e[1],list))
    print('==',path[-60:], [e[1] for e in root if not isinstance(e[1],list)])
    def rec(node,ind):
        for e in node:
            if isinstance(e[1],list) and kv.get(e[1],'ControlName') or (isinstance(e[1],list) and kv.get(e[1],'fieldName')):
                g=lambda k: kv.get(e[1],k,'')
                print(f"{'  '*ind}{e[0]:30} {g('ControlName'):20} x={g('xpos'):8} y={g('ypos'):8} w={g('wide'):6} t={g('tall'):6} v={g('visible')} pin={g('pin_to_sibling')} img={g('image')} font={g('font')} bg={g('bgcolor_override')} brd={g('border')} txt={g('labelText') or g('labeltext')}")
                if ind<depth: rec(e[1],ind+1)
    rec(body,1)
for p in sys.argv[1:]: summary(p)
