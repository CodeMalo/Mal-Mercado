"""
imagenes_post.py — Imágenes REALES del tema, libres para uso comercial.
======================================================================
Trae fotos relevantes de Openverse (agregador de imágenes con licencia:
Wikimedia, rawpixel, Flickr CC...), filtrando a uso comercial y prefiriendo
CC0/dominio público (sin necesidad de crédito). Las que sí piden crédito guardan
la atribución para mostrarla. Es "el scraper", apuntado a fuentes donde SÍ se
puede tomar — mismo resultado que quieres, sin riesgo legal para el negocio.
"""
import json
import ssl
import urllib.parse
import urllib.request
from io import BytesIO
from pathlib import Path

from PIL import Image

_CTX = ssl.create_default_context()
_CTX.check_hostname = False
_CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "MalMercado/1.0 (contenido educativo)"}
API = "https://api.openverse.org/v1/images/"
# CC0 y dominio público NO requieren crédito; el resto sí.
SIN_CREDITO = {"cc0", "pdm"}


def buscar(query, n=4, excluir=None):
    excluir = excluir or set()
    params = urllib.parse.urlencode({
        "q": query, "license_type": "commercial", "size": "large",
        "page_size": 12, "mature": "false"})
    try:
        req = urllib.request.Request(API + "?" + params, headers=UA)
        d = json.loads(urllib.request.urlopen(req, timeout=15, context=_CTX).read())
    except Exception as e:
        print(f"  [aviso] Openverse falló ({query}): {str(e)[:70]}")
        return []
    # prioriza CC0/PDM (sin crédito), luego el resto
    resultados = sorted(d.get("results", []),
                        key=lambda r: 0 if (r.get("license") or "").lower() in SIN_CREDITO else 1)
    out = []
    for r in resultados:
        url = r.get("url")
        if not url or url in excluir:
            continue
        lic = (r.get("license") or "").lower()
        credito = None
        if lic not in SIN_CREDITO:
            autor = r.get("creator") or r.get("source") or "fuente"
            credito = f"{autor} · {lic.upper()} · vía {r.get('source', 'Openverse')}"
        out.append({"url": url, "license": lic, "credito": credito})
        if len(out) >= n:
            break
    return out


def descargar(url, dest, max_w=1400):
    """Descarga y normaliza (RGB, ancho máx). Devuelve True si quedó."""
    try:
        req = urllib.request.Request(url, headers=UA)
        data = urllib.request.urlopen(req, timeout=20, context=_CTX).read(8_000_000)
        im = Image.open(BytesIO(data)).convert("RGB")
        if im.width > max_w:
            im = im.resize((max_w, round(im.height * max_w / im.width)))
        dest = Path(dest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        im.save(dest, quality=88)
        return True
    except Exception as e:
        print(f"  [aviso] descarga falló: {str(e)[:60]}")
        return False


def fotos_reales(queries, slug, carpeta, n=2):
    """Baja hasta n fotos reales relevantes para el post. Devuelve
    [(ruta_relativa, credito)]. Reutiliza las ya descargadas (evita re-pegarle a
    Openverse y su rate limit)."""
    def _cred_lee(p):
        c = p.with_suffix(".credit.txt")
        return c.read_text(encoding="utf-8").strip() or None if c.exists() else None

    existentes = sorted(Path(carpeta).glob(f"{slug}-foto*.jpg"))
    if len(existentes) >= n:
        return [(f"public/media/blog/{p.name}", _cred_lee(p)) for p in existentes[:n]]
    vistos, out = set(), []
    for q in queries:
        if len(out) >= n:
            break
        for cand in buscar(q, n=3, excluir=vistos):
            vistos.add(cand["url"])
            dst = carpeta / f"{slug}-foto{len(out) + 1}.jpg"
            if descargar(cand["url"], dst):
                if cand["credito"]:
                    dst.with_suffix(".credit.txt").write_text(cand["credito"], encoding="utf-8")
                out.append((f"public/media/blog/{dst.name}", cand["credito"]))
                break
    return out
