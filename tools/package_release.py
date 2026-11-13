"""Package tracked public source plus the built demo, without Git or private notes."""
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]
destination=Path(sys.argv[1]).resolve()
destination.parent.mkdir(parents=True,exist_ok=True)
files=subprocess.check_output(["git","ls-files","-z"],cwd=ROOT).decode().split("\0")
files=[p for p in files if p and (ROOT/p).is_file()]
if any("NOTES_FOR_OWNER" in p or p.startswith(".env") for p in files):
    raise SystemExit("Private notes or environment files must not be packaged.")
with zipfile.ZipFile(destination,"w",zipfile.ZIP_DEFLATED) as archive:
    for name in files:
        archive.write(ROOT/name,"repair-scope/"+name)
    for path in sorted((ROOT/"dist").iterdir()):
        if path.is_file():
            archive.write(path,"repair-scope/dist/"+path.name)
with zipfile.ZipFile(destination,"r") as archive:
    bad=archive.testzip()
    if bad:
        raise SystemExit("Corrupt ZIP entry: "+bad)
print(str(destination))
print(str(destination.stat().st_size)+" bytes; "+str(len(files))+" source files plus built demo")
