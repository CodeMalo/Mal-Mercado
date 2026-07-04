"""
sections.py — Handler del blog de Mal Mercado (sitio independiente).
===================================================================
Un solo apartado: 'blog'. Voz financiera en español, identidad Mal Mercado,
lenguaje NO imperativo, disclaimer CNBV, ilustración Nano Banana, copys por red.
"""
import re
from pathlib import Path

import providers, mm_cover

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

    # Portada on-brand (PIL, sin API)
    cover_rel = f"public/media/blog/{slug}.png"
    cover_abs = PUBLIC / "media" / "blog" / f"{slug}.png"
    if not cover_abs.exists() or providers._REGEN:
        mm_cover.render(title, cover_abs, kicker=meta.get("kicker", "SEÑAL DEL MERCADO"),
                        tickers=[t for t in tickers[:6]] or None)

    # Ilustración Nano Banana (Gemini)
    images = []
    ilus_rel = f"public/media/blog/{slug}-ilustracion.png"
    ilus_abs = PUBLIC / "media" / "blog" / f"{slug}-ilustracion.png"
    brief_ilus = (
        f"Editorial financial illustration for a markets article titled '{title}'. Theme: {topic}. "
        f"Style: premium dark fintech, near-black background (#0b0d10), electric mint-green accent "
        f"(#3ef08c), subtle violet. Abstract, data-driven: candlesticks, glowing trend lines, "
        f"network nodes, soft glow. NO text, NO letters, NO human faces, NO logos. Wide 16:9.")
    try:
        if providers.make_illustration(brief_ilus, ilus_abs):
            images.append(ilus_rel)
    except Exception as e:
        print(f"  (ilustración omitida: {e})")

    social = mm_social(d, title, txt.get("summary", ""), body_md, cfg)
    tags = txt.get("tags") if isinstance(txt.get("tags"), list) else []

    return {
        "id": slug, "type": "blog", "title": title, "date": meta.get("date", ""),
        "summary": txt.get("summary", ""),
        "cover": cover_rel, "accent": "#3ef08c", "body": body_md,
        "images": images, "sources": sources, "read_min": read_min,
        "category": txt.get("category", "Mercados"), "tags": tags, "social": social,
    }


HANDLERS = {"blog": handle_blog}
