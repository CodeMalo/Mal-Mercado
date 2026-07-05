"""
grid_color.py — El color de cada post, en armonía para el grid de la cuenta.
===========================================================================
Cada post/video recibe UN acento distinto. La secuencia rota por la rueda de
color con un paso fijo (teoría del color): posts consecutivos quedan a una
distancia armónica, así el grid (feed de Instagram/TikTok) "salta" de color en
color de forma bonita conforme subes contenido, sobre la misma base oscura
Mal Mercado.

Devuelve, por índice de post:
  - acento: color vivo principal (para títulos/palabras destacadas/portada)
  - acento2: análogo (a +32°) para degradados y secundarios
  - hue: el matiz en grados (por si se necesita)
"""
import colorsys

BASE_HUE = 152      # arranca en el verde del logo (#3ef08c ≈ 152°)
PASO = 43           # grados que "salta" cada post: distinto pero armónico
SAT = 0.82
LUZ = 0.62


def _hex(h, s, l):
    r, g, b = colorsys.hls_to_rgb((h % 360) / 360.0, l, s)
    return "#{:02x}{:02x}{:02x}".format(round(r * 255), round(g * 255), round(b * 255))


def color_por_indice(i):
    hue = (BASE_HUE + i * PASO) % 360
    return {
        "hue": round(hue, 1),
        "acento": _hex(hue, SAT, LUZ),
        "acento2": _hex(hue + 32, SAT * 0.9, LUZ - 0.06),
        # descripción del matiz para el prompt de imagen (que combine con el post)
        "nombre_en": _nombre_hue(hue),
    }


def _nombre_hue(h):
    tabla = [
        (15, "red"), (45, "orange"), (70, "amber-yellow"), (95, "lime-green"),
        (150, "emerald-green"), (185, "teal-cyan"), (215, "sky-blue"),
        (255, "indigo-blue"), (285, "violet"), (320, "magenta"), (350, "pink-red"),
    ]
    for lim, nom in tabla:
        if h <= lim:
            return nom
    return "red"


if __name__ == "__main__":
    print("Secuencia del grid (post 0..9):")
    for i in range(10):
        c = color_por_indice(i)
        print(f"  post {i}: {c['acento']}  (+ {c['acento2']})  hue {c['hue']:>5}  {c['nombre_en']}")
