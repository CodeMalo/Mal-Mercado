"""
build.py — Motor del sitio Mal Mercado (independiente de malo_ia).
=================================================================
    cd mal-mercado-site
    python tools/build.py               # MOCK (sin keys)
    (con ANTHROPIC_API_KEY + GEMINI_API_KEY en el entorno) -> real

Lee content/blog/<slug>/item.md, genera cada artículo con su handler y escribe
public/content.json, que la página lee y arma sola.
"""
import json, sys, hashlib, os
from datetime import datetime, timezone
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

sys.path.insert(0, str(Path(__file__).resolve().parent))
import content, sections, providers

ROOT = Path(__file__).resolve().parents[1]


def _item_hash(it):
    # OJO: excluye lo que el PROPIO handler escribe (social_*.txt) — si entra al
    # hash, cada build ve el dir "cambiado" y re-genera el post aunque el item.md
    # sea idéntico (y un build sin keys lo sobrescribe con MOCK — pasó 2026-07-12).
    h = hashlib.sha256()
    h.update((it["dir"] / "item.md").read_bytes())
    for f in sorted(it["dir"].glob("*")):
        if (f.is_file() and f.name not in ("item.md", ".cache.json")
                and not f.name.startswith("social_")):
            h.update(f"{f.name}:{f.stat().st_size}".encode())
    return h.hexdigest()[:16]


def main():
    cfg = json.loads((ROOT / "site.config.json").read_text(encoding="utf-8"))
    print(f"== build mal-mercado-site · texto={'MOCK' if providers.TEXT_MOCK else 'Claude'} "
          f"· imágenes={'MOCK' if providers.IMAGE_MOCK else 'Gemini'} ==")
    regen = os.environ.get("MALO_REGEN", "") in ("1", "true", "True")
    today = datetime.now().strftime("%Y-%m-%d")
    cards = []
    for it in content.load_items():
        meta = it["meta"]
        if str(meta.get("status", "published")).lower() == "draft":
            continue
        handler = sections.HANDLERS.get(it["section"])
        if not handler:
            continue
        cache_f = it["dir"] / ".cache.json"
        ih = _item_hash(it)
        card = None
        if cache_f.exists() and not regen:
            try:
                c = json.loads(cache_f.read_text(encoding="utf-8"))
                if c.get("hash") == ih:
                    card = c.get("card")
            except Exception:
                pass
        if card is None:
            print(f"  → {it['section']}/{it['slug']} (generando)")
            card = handler(it, cfg)
            try:
                cache_f.write_text(json.dumps({"hash": ih, "card": card}, ensure_ascii=False), encoding="utf-8")
            except Exception:
                pass
        pub = str(meta.get("publish", "")).strip()
        if pub and pub > today:
            continue
        print(f"  ✓ {it['section']}/{it['slug']}")
        cards.append(card)

    cards.sort(key=lambda c: (c.get("date", ""), c.get("id", "")), reverse=True)
    out = {"generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "config": cfg, "items": cards}
    dest = ROOT / "public" / "content.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nListo: {len(cards)} item(s) → public/content.json")
    write_sitemap()


BASE_URL = "https://malmercado.com"


def write_sitemap():
    """sitemap.xml + robots.txt para Search Console. Se regenera en cada build,
    así cada post nuevo entra solo. Lee public/content.json (la verdad publicada)."""
    cj = ROOT / "public" / "content.json"
    items = json.loads(cj.read_text(encoding="utf-8")).get("items", []) if cj.exists() else []
    hoy = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    urls = [(f"{BASE_URL}/", hoy, "daily", "1.0"),
            (f"{BASE_URL}/blog.html", hoy, "daily", "0.9"),
            (f"{BASE_URL}/track.html", hoy, "daily", "0.8"),
            (f"{BASE_URL}/radar.html", hoy, "daily", "0.8")]
    for it in items:
        if it.get("type") == "blog" and it.get("id"):
            urls.append((f"{BASE_URL}/post.html?id={it['id']}",
                         it.get("date") or hoy, "monthly", "0.7"))
    cuerpo = "\n".join(
        f"  <url><loc>{u}</loc><lastmod>{lm}</lastmod>"
        f"<changefreq>{cf}</changefreq><priority>{pr}</priority></url>"
        for u, lm, cf, pr in urls)
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{cuerpo}\n</urlset>\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {BASE_URL}/sitemap.xml\n",
        encoding="utf-8")
    print(f"  ✓ sitemap.xml ({len(urls)} URLs) + robots.txt")


if __name__ == "__main__":
    main()
