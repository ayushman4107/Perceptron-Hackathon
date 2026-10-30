"""Download pinned wheels in bounded parallel ranges; verify PyPI SHA-256."""
import concurrent.futures,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;W=ROOT/'wheels';W.mkdir(exist_ok=True)
PACKAGES={'scipy':'1.16.3','matplotlib':'3.10.7','pymupdf':'1.26.5','contourpy':'1.3.3','cycler':'0.12.1','fonttools':'4.60.1','kiwisolver':'1.4.9','pyparsing':'3.2.5'}
def curl(*args):subprocess.run(['curl.exe','-sS','-L','--fail','--retry','2','--max-time','240',*map(str,args)],check=True)
def main():
    for name,version in PACKAGES.items():
        meta=W/f'{name}.json';curl(f'https://pypi.org/pypi/{name}/{version}/json','-o',meta)
        files=json.loads(meta.read_text())['urls']
        choices=[f for f in files if f['filename'].endswith('.whl') and
            (('cp312-cp312-win_amd64' in f['filename']) or ('cp39-abi3-win_amd64' in f['filename']) or f['filename'].endswith('py3-none-any.whl'))]
        assert choices,(name,[f['filename'] for f in files]);entry=choices[0];dest=W/entry['filename']
        if dest.exists() and hashlib.sha256(dest.read_bytes()).hexdigest()==entry['digests']['sha256']:continue
        chunks=[(i,start,min(start+1024*1024,entry['size'])-1) for i,start in enumerate(range(0,entry['size'],1024*1024))]
        def part(task):
            i,start,end=task;path=W/f'{name}.{i}.part'
            if not path.exists() or path.stat().st_size!=end-start+1:curl('--range',f'{start}-{end}',entry['url'],'-o',path)
            assert path.stat().st_size==end-start+1
            return path
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:paths=list(pool.map(part,chunks))
        with dest.open('wb') as f:
            for p in paths:f.write(p.read_bytes())
        assert hashlib.sha256(dest.read_bytes()).hexdigest()==entry['digests']['sha256']
        for p in paths:p.unlink()
        print('verified',dest.name,entry['size'],flush=True)
    subprocess.run([sys.executable,'-m','pip','install','--no-index','--no-deps','--target',str(ROOT/'.deps'),*map(str,W.glob('*.whl'))],check=True)
if __name__=='__main__':main()
