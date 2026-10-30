"""Inspect a remotely downloaded ZIP central-directory tail, without extracting data."""
import json, struct
from pathlib import Path
ROOT=Path(__file__).resolve().parent
b=(ROOT/'data/zip_tail.bin').read_bytes()
end=b.rfind(b'PK\x05\x06')
_,disk,cdisk,ndisk,n,size,offset,comment=struct.unpack_from('<4s4H2IH',b,end)
assert disk==cdisk==0 and ndisk==n
start=end-size
entries=[]
for _ in range(n):
    h=struct.unpack_from('<4s6H3I5H2I',b,start)
    assert h[0]==b'PK\x01\x02'
    namelen,extralen,commentlen=h[10:13]
    name=b[start+46:start+46+namelen].decode()
    entries.append(dict(name=name,method=h[4],crc32=h[7],compressed=h[8],uncompressed=h[9],offset=h[16]))
    start+=46+namelen+extralen+commentlen
(ROOT/'data/archive_index.json').write_text(json.dumps(entries,indent=2))
print(json.dumps(entries,indent=2))
