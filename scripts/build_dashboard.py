"""Build index.html (the dashboard, served by GitHub Pages) from reports/findings.json."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

findings = json.loads((ROOT / "reports" / "findings.json").read_text())
template = (Path(__file__).with_name("dashboard_template.html")).read_text(encoding="utf-8")
html = template.replace("__DATA__", json.dumps(findings).replace("</", "<\\/"))
(ROOT / "index.html").write_text(html, encoding="utf-8")
print(f"Wrote {ROOT / 'index.html'}")
