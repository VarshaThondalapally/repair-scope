"""Generate browser data from the same Python catalog, alias and rule loaders."""
from dataclasses import asdict
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from finding_coder.api import describe
from finding_coder.domains import list_domains, load_domain


def build():
    shutil.copy2(ROOT / "examples/forklift/catalog.csv", ROOT / "web/sample_catalog.csv")
    packs = {}
    for name in list_domains():
        pack = load_domain(name)
        packs[name] = {
            **describe(pack), "version": "sample-v2",
            "catalog": [asdict(r) for r in pack.catalog.rows],
            "synonyms": [[p for p, _ in g] for g in pack.matcher.synonyms.groups],
            "rules": [asdict(r) for r in pack.rules],
        }
    (ROOT / "web/data.js").write_text("export default " + json.dumps(packs, ensure_ascii=True, indent=2) + ";\n", encoding="utf-8")
    (ROOT / "dist").mkdir(exist_ok=True)
    for p in (ROOT / "web").iterdir():
        if p.is_file():
            shutil.copy2(p, ROOT / "dist" / p.name)
    # A dependency-free, self-contained build also works as a local file.
    page = (ROOT / "web/index.html").read_text(encoding="utf-8")
    css = (ROOT / "web/styles.css").read_text(encoding="utf-8")
    engine = (ROOT / "web/engine.js").read_text(encoding="utf-8").replace("export ", "")
    data = (ROOT / "web/data.js").read_text(encoding="utf-8").replace("export default ", "const packs = ", 1)
    app = (ROOT / "web/app.js").read_text(encoding="utf-8")
    app = "\n".join(line for line in app.splitlines() if not line.startswith("import "))
    draft = (ROOT / "web/draft.js").read_text(encoding="utf-8").replace("export ", "")
    bundle = "(()=>{\n" + engine + "\n" + draft + "\n" + data + "\n" + app + "\n})();"
    page = page.replace('<link rel="stylesheet" href="styles.css">', "<style>"+css+"</style>")
    page = page.replace('<script type="module" src="app.js"></script>', "")
    page = page.replace("</body>", "<script>"+bundle.replace("</script", "<\\/script")+"</script></body>")
    (ROOT / "dist/index.html").write_text(page, encoding="utf-8")
    print("Built dist/ from web/ and the validated Python domain packs.")


if __name__ == "__main__":
    build()
