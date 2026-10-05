"""Draw original, matching vector views of the workshop square in three eras."""
from pathlib import Path

ASSETS = Path(__file__).resolve().parents[1] / "assets"


def clocktower(accent, frontier=False):
    roof = '<path d="M438 158L520 102L602 158Z" fill="#513c2b"/>' if frontier else '<path d="M438 158L520 110L602 158Z" fill="#243748"/>'
    return f'''<g stroke="{accent}" stroke-width="2" stroke-linejoin="round">
      <path d="M380 350V246L414 224H626L660 246V350Z" fill="#182735"/>
      <path d="M454 350V158H586V350Z" fill="#203443"/>{roof}
      <path d="M435 162H605M444 234H596M374 352H667"/>
      <circle cx="520" cy="193" r="26" fill="#0c1924"/>
      <path d="M520 175V193L535 202M520 168V172M520 214V218M495 193H499M541 193H545"/>
      <path d="M476 253H492V305H476ZM511 253H528V305H511ZM548 253H564V305H548Z" fill="#101d29"/>
      <path d="M404 261H421V291H404ZM619 261H636V291H619Z" fill="{accent}" opacity=".45"/>
      <path d="M501 350V321Q520 302 539 321V350" fill="#0a1420"/>
    </g>'''


def machine(accent):
    return f'''<g transform="translate(220 346)" stroke="#b7cad6" stroke-width="2" stroke-linejoin="round">
      <path d="M0 28L20 13L39 11L62 -10H116L141 14L161 20V39H0Z" fill="#425765"/>
      <path d="M66 -5H91V12H48ZM97 -5H113L133 12H97Z" fill="#0b1c29" stroke="{accent}"/>
      <path d="M15 24H149M44 15L38 32M97 16V33M146 21V32"/>
      <path d="M5 26H20M145 25H157" stroke="{accent}" stroke-width="5"/>
      <circle cx="32" cy="39" r="13" fill="#080f16"/><circle cx="127" cy="39" r="13" fill="#080f16"/>
      <circle cx="32" cy="39" r="5"/><circle cx="127" cy="39" r="5"/>
      <path d="M58 33H95" stroke="{accent}"/>
    </g>'''


def draw(era, accent, sky, scenery, foreground):
    stars = ''.join(f'<circle cx="{x}" cy="{y}" r="1.4"/>' for x, y in [(90,85),(152,135),(240,66),(350,115),(715,80),(807,139),(899,71),(680,141)])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="960" height="520" viewBox="0 0 960 520">
    <title>The workshop square · {era}</title><desc>An original clocktower square, workshop and time machine, viewed in the {era} setting.</desc>
    <defs><linearGradient id="sky" x2="0" y2="1"><stop stop-color="{sky}"/><stop offset="1" stop-color="#07131e"/></linearGradient>
    <radialGradient id="halo"><stop stop-color="{accent}" stop-opacity=".22"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></radialGradient>
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="#9dc5dc" stroke-opacity=".06"/></pattern></defs>
    <rect width="960" height="520" fill="url(#sky)"/><ellipse cx="520" cy="230" rx="360" ry="250" fill="url(#halo)"/>
    <rect width="960" height="520" fill="url(#grid)"/><g fill="#c5dfed" opacity=".55">{stars}</g>
    <path d="M0 332L75 309L170 326L239 294L344 312L428 287L625 311L728 282L814 317L960 291V520H0Z" fill="#0a1923"/>
    {scenery}{clocktower(accent, era == 'frontier')}
    <path d="M0 352H960V520H0Z" fill="#0d1d28"/><path d="M0 352H960M83 520L403 352M877 520L636 352" stroke="{accent}" stroke-opacity=".25" fill="none"/>
    <g stroke="{accent}" fill="none" opacity=".25"><path d="M0 426H960M0 480H960M105 352L-70 520M754 352L1030 520"/></g>
    {foreground}{machine(accent)}
    <g stroke="{accent}" fill="none" stroke-width="1.5" opacity=".7"><path d="M28 60V28H60M900 28H932V60M932 460V492H900M60 492H28V460"/>
    <path d="M520 88V64H710M376 383H429V435H530" stroke-dasharray="4 6"/></g>
    <g font-family="monospace" font-size="10" letter-spacing="2" fill="#c4dae4"><text x="724" y="68">CLOCKTOWER / FIXED POINT</text><text x="546" y="439">WORKSHOP / MOBILE LAB</text></g>
    </svg>'''


workshop = '''<g stroke="#6394ad" stroke-width="2" fill="#132532">
  <path d="M95 352V267L192 219L282 267V352Z"/><path d="M87 268H290M118 283H263V352H118Z"/>
  <path d="M138 294H167V320H138ZM210 294H240V320H210Z" fill="#dfb86a" opacity=".65"/>
  <path d="M743 351V249H878V351M732 249H887"/><path d="M765 271H855V310H765Z" fill="#254350"/>
  <path d="M689 350V238M675 241H703"/><circle cx="689" cy="239" r="7" fill="#ffe5a1"/>
  <path d="M64 198H334M86 184V352M302 184V352" opacity=".45"/>
  </g><g font-family="monospace" fill="#d4e8ef" font-size="12" letter-spacing="3"><text x="128" y="274">WORKSHOP</text><text x="769" y="296">SERVICE</text></g>'''

future = '''<g fill="#142d3e" stroke="#47718c" stroke-width="2">
  <path d="M76 352V188H140V352M153 352V142H204V352M237 352V207H320V352M709 352V153H770V352M797 352V199H895V352"/>
  <path d="M83 213H132M83 238H132M161 168H197M161 198H197M719 174H760M719 201H760M810 222H882" stroke="#69dfec" opacity=".65"/>
  <path d="M68 302H316V351H68Z" fill="#203b49"/><path d="M81 315H299" stroke="#f4c471"/>
  </g><g stroke="#63dfff" fill="none"><path d="M10 126Q280 56 367 174T941 135" stroke-dasharray="4 8" opacity=".5"/>
  <path d="M749 88L801 82L821 96H744Z" fill="#38586e"/><path d="M750 109H813" opacity=".6"/>
  <path d="M78 337H305" stroke-width="4"/></g><text x="111" y="329" fill="#f4c471" font-family="monospace" font-size="12" letter-spacing="3">TRANSIT BAY</text>'''

frontier = '''<path d="M0 270L72 232L144 268L222 197L320 284L391 270M659 276L735 222L789 252L870 192L960 260V352H0" fill="#342d28"/>
  <g stroke="#b88c59" stroke-width="2" fill="#352d27"><path d="M80 352V267H258V352M70 267H269V253H70Z"/>
  <path d="M105 285H143V324H105ZM198 285H236V324H198Z" fill="#d4a65d" opacity=".7"/>
  <path d="M160 352V285H183V352M288 352V269M276 268H302M714 352V244H890V352M703 244H901V230H703Z"/>
  <path d="M73 326H264M73 338H264" opacity=".5"/></g>
  <text x="100" y="263" fill="#f4ce8a" font-family="monospace" font-size="11" letter-spacing="3">FIELD WORKSHOP</text>'''

railway = '''<g stroke="#8e745a" fill="none" stroke-width="4"><path d="M477 520L755 352M561 520L790 352"/>
  <path d="M491 497L592 497M532 469H623M574 443H657M616 418H690M658 393H722M700 368H755" stroke-width="7"/></g>
  <g transform="translate(726 291)" stroke="#c3975c" stroke-width="2" fill="#302b25"><path d="M0 30H96V51H0ZM8 16H65V30H8ZM15 -2H27V16H15ZM68 -14H95V30H68Z"/>
  <circle cx="19" cy="54" r="11"/><circle cx="50" cy="54" r="11"/><circle cx="81" cy="54" r="11"/><path d="M0 54H91"/></g>'''

if __name__ == "__main__":
    views = [
        ("analogue", "#76e2ff", "#112d43", workshop, '<path d="M24 393H199M24 406H192" stroke="#ffad45" stroke-width="3" opacity=".7"/>'),
        ("future", "#f4c471", "#142b43", future, '<path d="M26 388H198M26 402H190" stroke="#63dfff" stroke-width="3" opacity=".7"/>'),
        ("frontier", "#e3ad68", "#46372d", frontier, railway),
    ]
    for era, accent, sky, scene, foreground in views:
        (ASSETS / f"workshop-{era}.svg").write_text(draw(era, accent, sky, scene, foreground), encoding="utf-8")
