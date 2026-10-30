"""Stream selected ZIP members into compact arrays; never materialize full CSVs."""
import io,json,struct,zlib,hashlib,time
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parent

class DeflateReader(io.RawIOBase):
    def __init__(self,path,entry):
        self.f=open(path,'rb'); h=self.f.read(30)
        fields=struct.unpack('<4s5H3I2H',h);assert fields[0]==b'PK\x03\x04' and fields[3]==8
        self.f.read(fields[-2]+fields[-1]);self.left=entry['compressed']
        self.d=zlib.decompressobj(-15);self.buf=b'';self.crc=0;self.total=0;self.entry=entry
    def readable(self):return True
    def readinto(self,b):
        while not self.buf and self.left:
            inp=self.f.read(min(16384,self.left));assert inp;self.left-=len(inp)
            self.buf=self.d.decompress(inp)
            self.crc=zlib.crc32(self.buf,self.crc);self.total+=len(self.buf)
        if not self.buf:
            assert self.d.eof and self.crc==self.entry['crc32']
            if self.entry['uncompressed']!=2**32-1:assert self.total==self.entry['uncompressed']
            return 0
        n=min(len(b),len(self.buf));b[:n]=self.buf[:n];self.buf=self.buf[n:];return n
    def close(self):self.f.close();super().close()

def prepare():
    entries=json.loads((ROOT/'data/archive_index.json').read_text());report={}
    for policy,campaign in [('random','all'),('random','men'),('random','women'),('bts','men')]:
        key=f'{policy}_{campaign}';file=ROOT/'data'/f'{key}.member'
        entry=next(x for x in entries if x['name']==f'open_bandit_dataset/{policy}/{campaign}/{campaign}.csv')
        stream=DeflateReader(file,entry);buf=io.BufferedReader(stream)
        cols=['timestamp','item_id','position','click','propensity_score']
        pieces=[];rows=0;start=time.time()
        for df in pd.read_csv(buf,usecols=cols,chunksize=100000):
            rows+=len(df)
            # Preserve all positions for diagnostics, but primary analysis uses position 1 only.
            pieces.append(df)
        df=pd.concat(pieces,ignore_index=True)
        ts=pd.to_datetime(df.timestamp,format='ISO8601',utc=True).dt.as_unit('ns').astype('int64').to_numpy()
        arrays=dict(timestamp=ts,action=df.item_id.to_numpy(np.int16),position=df.position.to_numpy(np.int8),
                    reward=df.click.to_numpy(np.int8),pscore=df.propensity_score.to_numpy(float))
        assert set(np.unique(arrays['reward']))<={0,1}
        assert np.isfinite(arrays['pscore']).all() and (arrays['pscore']>0).all() and (arrays['pscore']<=1).all()
        np.savez_compressed(ROOT/'data'/f'{key}.npz',**arrays)
        report[key]=dict(rows=rows,positions=np.unique(arrays['position']).tolist(),actions=np.unique(arrays['action']).tolist(),
            clicks=int(arrays['reward'].sum()),ctr=float(arrays['reward'].mean()),
            min_pscore=float(arrays['pscore'].min()),max_pscore=float(arrays['pscore'].max()),
            timestamp_start=str(df.timestamp.min()),timestamp_end=str(df.timestamp.max()),
            compressed_bytes=file.stat().st_size,uncompressed_bytes_verified=stream.total,crc32_verified=stream.crc,
            member_sha256=hashlib.sha256(file.read_bytes()).hexdigest(),
            compact_bytes=(ROOT/'data'/f'{key}.npz').stat().st_size,seconds=time.time()-start)
        print(key,json.dumps(report[key]),flush=True)
        buf.close()
    (ROOT/'data/data_manifest.json').write_text(json.dumps(dict(source='https://research.zozo.com/data_release/open_bandit_dataset.zip',
        archive_bytes=412931917,archive_etag='4937f713a664ceba17894da22ec0b6c0-25',datasets=report),indent=2))
if __name__=='__main__':prepare()
