import struct, sys, io, os
from PIL import Image
def read_vtf(path):
    d=open(path,'rb').read()
    hs=struct.unpack_from('<I',d,12)[0]; w,h=struct.unpack_from('<HH',d,16); fmt=struct.unpack_from('<I',d,52)[0]; mips=d[56]
    lrf=struct.unpack_from('<I',d,57)[0]; lw,lh=d[61],d[62]; ver=struct.unpack_from('<II',d,4)
    bpp={0:4,1:4,2:3,3:3,12:4,13:0.5,14:1,15:1,16:4}
    def size(fm,W,H):
        if fm in(13,14,15): return max(1,(W+3)//4)*max(1,(H+3)//4)*(8 if fm==13 else 16)
        return int(W*H*bpp[fm])
    off=hs
    if ver[1]<3:
        off+= size(lrf,lw,lh) if lrf!=0xFFFFFFFF else 0
    else:
        # resources
        n=struct.unpack_from('<I',d,68)[0]
        for i in range(n):
            tag,flags,o=struct.unpack_from('<3sBI',d,80+8*i)
            if tag==b'\x30\x00\x00': off=o
    for i in range(mips-1,0,-1): off+=size(fmt,max(1,w>>i),max(1,h>>i))
    data=d[off:off+size(fmt,w,h)]
    if fmt in (13,14,15):
        four={13:b'DXT1',14:b'DXT3',15:b'DXT5'}[fmt]
        hdr=struct.pack('<4sI I I I I I I 11I I I 4s 5I I I I I I','DDS '.encode(),124,0x1007,h,w,len(data),0,0,*([0]*11),32,4,four,0,0,0,0,0,0x1000,0,0,0,0)
        return Image.open(io.BytesIO(hdr+data)).convert('RGBA')
    import numpy as np
    a=np.frombuffer(data,np.uint8)
    if fmt==12: a=a.reshape(h,w,4)[...,[2,1,0,3]]
    elif fmt==0: a=a.reshape(h,w,4)
    elif fmt==3: a=np.concatenate([a.reshape(h,w,3)[...,[2,1,0]],np.full((h,w,1),255,np.uint8)],-1)
    elif fmt==2: a=np.concatenate([a.reshape(h,w,3),np.full((h,w,1),255,np.uint8)],-1)
    else: raise Exception('fmt %d'%fmt)
    return Image.fromarray(a.copy(),'RGBA')
if __name__=='__main__':
    out=sys.argv[1]
    for p in sys.argv[2:]:
        im=read_vtf(p); im.save(out+'/'+os.path.basename(p).replace('.vtf','.png')); print(p.split('/')[-1], im.size)
