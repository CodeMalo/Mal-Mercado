"""
sections.py — Handler del blog de Mal Mercado (sitio independiente).
===================================================================
Un solo apartado: 'blog'. Voz financiera en español, identidad Mal Mercado,
lenguaje NO imperativo, disclaimer CNBV, ilustración Nano Banana, copys por red.
"""
import re
from pathlib import Path

import providers, mm_cover, grid_color, imagenes_post

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

MM_DISCLAIMER = (
    "\n\n---\n\n"
    "*Mal Mercado es contenido educativo e informativo de análisis general de "
    "mercados: la misma información para todos los lectores. No es asesoría de "
    "inversión personalizada ni recomendación individualizada; no somos asesores "
    "registrados ante la CNBV. Invertir implica riesgo de pérdida. Los rendimientos "
    "pasados no garantizan rendimientos futuros. Cada quien es responsable de sus "
    "propias decisiones.*"
)
MM_PLATAFORMAS = ["youtube", "instagram", "facebook", "tiktok", "x", "threads", "linkedin"]


def mm_social(d, title, summary, body_md, cfg):
    url = cfg.get("blog", {}).get("blog_url", "malmercado")

    def _mock():
        base = f"{title}\n\n{summary}\n\nLee el análisis completo en {url}."
        return {p: base for p in MM_PLATAFORMAS}

    soc = providers.write_text(
        system=(
            "Eres el copywriter de Mal Mercado, análisis de mercados con IA. Español "
            "claro, tono confiable y tech, SIN emojis. NUNCA lenguaje imperativo de "
            "inversión ('compra', 'vende'): hablas de lo que el análisis observa. "
            "Devuelves SIEMPRE un único JSON válido."),
        prompt=(
            f"Título: {title}\nResumen: {summary}\nTexto:\n{body_md[:4000]}\nBlog: {url}\n\n"
            "Devuelve SOLO este JSON con un copy nativo por plataforma (español, sin emojis, "
            "sin órdenes de compra/venta):\n"
            '{"youtube":"título + descripción de Short","instagram":"caption + 5-8 hashtags",'
            '"facebook":"2-3 párrafos","tiktok":"gancho + 3-5 hashtags","x":"1 tuit <=270",'
            '"threads":"post breve","linkedin":"post profesional 2-3 párrafos"}'),
        mock_fn=_mock,
    )
    for p in MM_PLATAFORMAS:
        try:
            (d / f"social_{p}.txt").write_text(soc.get(p, ""), encoding="utf-8")
        except Exception:
            pass
    return soc


def _queries_imagen(topic, tickers):
    """Búsquedas de fotos reales relevantes al tema (Openverse)."""
    cripto = any(str(t).endswith("-USD") for t in tickers)
    base = [topic, f"{topic} technology"]
    base.append("cryptocurrency bitcoin" if cripto else "stock market finance")
    return base


def _imagenes(slug, topic, tickers, acento_nombre):
    """3+ imágenes: 2 fotos REALES del tema (scraper Openverse, libres) + 1 imagen
    Nano Banana de alto impacto (estilo Super Bowl: clara, ingeniosa, 3s de gancho).
    Devuelve (rutas, creditos)."""
    carpeta = PUBLIC / "media" / "blog"
    reales = imagenes_post.fotos_reales(_queries_imagen(topic, tickers), slug, carpeta, n=2)
    imgs = [r for r, _ in reales]
    creditos = [c for _, c in reales if c]

    # Imagen hero Nano Banana: foto editorial de alto impacto del tema.
    hero_rel = f"public/media/blog/{slug}-hero.png"
    hero_abs = carpeta / f"{slug}-hero.png"
    brief = (
        f"A bold, high-impact editorial photograph representing {topic} for a finance media cover. "
        f"A clear, clever visual metaphor that grabs attention in 3 seconds — Super Bowl ad energy. "
        f"Cinematic dramatic lighting with a subtle {acento_nombre} accent glow, magazine-cover quality, "
        f"photorealistic, shallow depth of field. The subject is clearly and directly about {topic}. "
        f"NO text, NO words, NO letters, NO numbers, NO watermarks, NO logos.")
    try:
        if providers.make_illustration(brief, hero_abs):
            imgs.insert(0, hero_rel)   # el hero va primero
    except Exception as e:
        print(f"  (hero Nano Banana omitido: {e})")
    return imgs, creditos


def handle_blog(item, cfg):
    meta, slug, d = item["meta"], item["slug"], item["dir"]
    title = meta.get("title", slug.replace("-", " ").title())
    topic = meta.get("cover_topic", title)
    sources = meta.get("sources", []) if isinstance(meta.get("sources"), list) else []
    tickers = meta.get("tickers", []) if isinstance(meta.get("tickers"), list) else []

    def _mock():
        return {"title": title,
                "summary": f"{title}: qué observan las señales del mercado.",
                "body": item["body"] or "(brief vacío)",
                "category": "Mercados",
                "tags": tickers[:5] or ["mercados", "inversión"]}
    txt = providers.write_text(
        system=(
            "Eres el redactor del blog de Mal Mercado. Escribes como una persona real con "
            "criterio, no como un modelo. Audiencia: gente en México que quiere entender los "
            "mercados sin ser experta. Español, SIN emojis. Contenido EDUCATIVO original y SEO.\n"
            "1. Abre con lo concreto (dato/hecho/cifra del brief). Explica DESPUÉS del ejemplo.\n"
            "2. Frases cortas. Prueba en vez de adjetivos.\n"
            "3. Cada sección hace UN trabajo. Sin relleno.\n"
            "4. PROHIBIDO: 'en el vertiginoso mundo', 'cambio de paradigma', 'revolucionario', "
            "'esto es importante porque' vacío, y cerrar con pregunta de engagement.\n"
            "LEGAL ABSOLUTO: NUNCA instrucciones de compra/venta. Describe lo que se OBSERVA. "
            "No inventes cifras. Devuelves SIEMPRE un único JSON válido, sin fences."),
        prompt=(
            f"Artículo para Mal Mercado.\nTítulo de trabajo: {title}\nTema: {topic}\n"
            f"Activos: {', '.join(tickers) or '(mercado general)'}\n"
            f"Fuentes:\n{chr(10).join(sources) or '(ninguna)'}\n"
            f"BRIEF de noticias (reescribe y EXPANDE en artículo original):\n{item['body'][:6000]}\n\n"
            'Devuelve SOLO este JSON: {'
            '"title":"título SEO en español, con gancho (~70 chars), sin comillas",'
            '"summary":"meta-descripción SEO ~155 chars",'
            '"body":"artículo en Markdown: intro breve, ## subtítulos, párrafos cortos, listas, '
            'un ## Preguntas frecuentes con 2-3 Q&A, y un ## En resumen. Sin H1. Sin órdenes.",'
            '"category":"categoría (Acciones/Cripto/Macro/IA y mercados)",'
            '"tags":["4-6 etiquetas SEO minúsculas"]}'),
        mock_fn=_mock,
    )

    title = (txt.get("title") or "").strip() or title
    body_md = (txt.get("body") or item["body"]) + MM_DISCLAIMER
    read_min = max(1, round(len(re.findall(r"\w+", body_md)) / 200))

    # Color del grid: cada post salta a un acento distinto (teoría del color).
    try:
        gidx = int(meta.get("grid_index", 0))
    except Exception:
        gidx = 0
    color = grid_color.color_por_indice(gidx)

    # Portada on-brand con el acento del post
    cover_rel = f"public/media/blog/{slug}.png"
    cover_abs = PUBLIC / "media" / "blog" / f"{slug}.png"
    if not cover_abs.exists() or providers._REGEN:
        mm_cover.render(title, cover_abs, kicker=meta.get("kicker", "SEÑAL DEL MERCADO"),
                        tickers=[t for t in tickers[:6]] or None, acento=color["acento"])

    # Imágenes REALES del tema (scraper) + hero Nano Banana de alto impacto
    images, creditos = _imagenes(slug, topic, tickers, color["nombre_en"])

    social = mm_social(d, title, txt.get("summary", ""), body_md, cfg)
    tags = txt.get("tags") if isinstance(txt.get("tags"), list) else []

    return {
        "id": slug, "type": "blog", "title": title, "date": meta.get("date", ""),
        "summary": txt.get("summary", ""),
        "cover": cover_rel, "accent": color["acento"], "accent2": color["acento2"],
        "body": body_md, "images": images, "image_credits": creditos,
        "sources": sources, "read_min": read_min,
        "category": txt.get("category", "Mercados"), "tags": tags, "social": social,
    }


HANDLERS = {"blog": handle_blog}
