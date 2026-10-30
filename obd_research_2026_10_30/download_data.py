"""Fetch only four ZIP members (~94 MiB), with byte ranges and checksum verification."""
import hashlib,json,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent;DATA=ROOT/'data';DATA.mkdir(exist_ok=True)
def main():
    manifest=json.loads((DATA/'data_manifest.json').read_text());entries=json.loads((DATA/'archive_index.json').read_text())
    for key,info in manifest['datasets'].items():
        path=DATA/f'{key}.member'
        if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest()==info['member_sha256']:
            print('already verified',key);continue
        policy,campaign=key.split('_');entry=next(e for e in entries if e['name']==f'open_bandit_dataset/{policy}/{campaign}/{campaign}.csv')
        start=entry['offset'];end=start+info['compressed_bytes']-1
        request=urllib.request.Request(manifest['source'],headers={'Range':f'bytes={start}-{end}','If-Match':'"'+manifest['archive_etag']+'"'})
        temp=path.with_suffix('.part')
        with urllib.request.urlopen(request,timeout=120) as response:
            if response.status!=206:raise RuntimeError('Server did not honor range request; refusing full-archive download')
            if response.headers.get('Content-Range')!=f'bytes {start}-{end}/{manifest["archive_bytes"]}':raise RuntimeError('Unexpected archive/range')
            h=hashlib.sha256();total=0
            with temp.open('wb') as f:
                while block:=response.read(1024*1024):
                    total+=len(block)
                    if total>info['compressed_bytes']:raise RuntimeError('Unexpected download size')
                    f.write(block);h.update(block)
        if total!=info['compressed_bytes'] or h.hexdigest()!=info['member_sha256']:raise RuntimeError('Data checksum mismatch')
        temp.replace(path);print('verified',key,total,flush=True)
    from prepare_data import prepare
    prepare()
if __name__=='__main__':main()
