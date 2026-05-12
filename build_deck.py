"""build_deck.py
=====================================================================
Generates `deck.pptx` for the Boeing / Chomsky 5-minute presentation.

Rebuilds the existing Canva slides 1-3 in matching style and extends
the deck to the full 9-slide rhetorical arc specified in
`Boeing slide outline.txt`, backed by `Boeing Project master.txt`.

Run:
    python3 build_deck.py

Fonts: targets "Inter" (the Canva default).  PowerPoint will substitute
gracefully if Inter is not installed (typically with Calibri/Aptos).
=====================================================================
"""

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Emu, Inches, Pt

ROOT = Path(__file__).resolve().parent
IMG = ROOT / "deck" / "images"
OUT = ROOT / "deck.pptx"

# ---------------- design tokens (match existing Canva deck) ----------------

BG        = RGBColor(0xD6, 0xDC, 0xE0)   # light blue-gray background
INK       = RGBColor(0x10, 0x10, 0x10)   # near-black titles + body
INK_MUTED = RGBColor(0x55, 0x5B, 0x60)   # secondary text
LINE      = RGBColor(0x0B, 0x24, 0x47)   # dark navy for timeline + rules
ACCENT    = RGBColor(0xC8, 0x10, 0x2E)   # red for fatality counts + counterfactual
SLAB      = RGBColor(0xC4, 0xCC, 0xD2)   # quote slab (slightly darker than BG)
PLACEHOLD = RGBColor(0xB8, 0xBF, 0xC6)   # image placeholder fill

TITLE_FONT = "Inter"
BODY_FONT  = "Inter"
SERIF_FONT = "Cambria"  # used for the mocked WSJ headline on slide 9

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)


# ---------------- low-level helpers ----------------

def make_prs() -> Presentation:
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H
    return prs


def blank(prs: Presentation):
    """Add a blank slide with the deck's background color."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, SLIDE_H)
    bg.line.fill.background()
    bg.fill.solid()
    bg.fill.fore_color.rgb = BG
    return slide


def text(slide, body, x, y, w, h, *,
         font=BODY_FONT, size=18, bold=False, italic=False,
         color=INK, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
         line_spacing=1.15):
    """Add a multi-line textbox. `body` may contain newlines."""
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Emu(0)
    tf.margin_top = tf.margin_bottom = Emu(0)
    tf.vertical_anchor = anchor
    for i, line in enumerate(body.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = line_spacing
        run = p.add_run()
        run.text = line
        run.font.name = font
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.italic = italic
        run.font.color.rgb = color
    return tb


def rich_text(slide, runs, x, y, w, h, *, align=PP_ALIGN.LEFT,
              anchor=MSO_ANCHOR.TOP, line_spacing=1.15):
    """Multi-run textbox. `runs` is a list of paragraphs; each paragraph is a
    list of (text, style_dict) tuples.  style_dict keys: font, size, bold,
    italic, color, underline."""
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Emu(0)
    tf.margin_top = tf.margin_bottom = Emu(0)
    tf.vertical_anchor = anchor
    for i, para in enumerate(runs):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = line_spacing
        for chunk, style in para:
            run = p.add_run()
            run.text = chunk
            run.font.name      = style.get("font", BODY_FONT)
            run.font.size      = Pt(style.get("size", 18))
            run.font.bold      = style.get("bold", False)
            run.font.italic    = style.get("italic", False)
            run.font.underline = style.get("underline", False)
            run.font.color.rgb = style.get("color", INK)
    return tb


def image(slide, name, x, y, w=None, h=None):
    return slide.shapes.add_picture(str(IMG / name), x, y, width=w, height=h)


def rect(slide, x, y, w, h, *, fill=None, line=None, line_width=None):
    r = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    if fill is None:
        r.fill.background()
    else:
        r.fill.solid()
        r.fill.fore_color.rgb = fill
    if line is None:
        r.line.fill.background()
    else:
        r.line.color.rgb = line
        if line_width is not None:
            r.line.width = line_width
    return r


def oval(slide, x, y, w, h, fill):
    o = slide.shapes.add_shape(MSO_SHAPE.OVAL, x, y, w, h)
    o.fill.solid(); o.fill.fore_color.rgb = fill
    o.line.fill.background()
    return o


def notes(slide, body: str):
    slide.notes_slide.notes_text_frame.text = body


def placeholder(slide, label, x, y, w, h):
    """Image placeholder box with a centered label — for assets the user
    still needs to source (advertiser logos, KAL 007 NYT page, etc.)."""
    rect(slide, x, y, w, h, fill=PLACEHOLD, line=INK_MUTED)
    text(slide, label, x, y, w, h,
         font=BODY_FONT, size=14, italic=True, color=INK_MUTED,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)


# ---------------- slides ----------------

def slide_1_hook(prs):
    """Opening hook (~25s): WSJ headline + date."""
    s = blank(prs)
    # Headline screenshot — larger, centered horizontally.  The screenshot's
    # aspect ratio is 803:297 ≈ 2.70:1.
    hw = Inches(11.5)
    hh = Inches(11.5 * 297 / 803)   # ≈ 4.25"
    image(s, "wsj_headline_march11.png",
          (SLIDE_W - hw) / 2, Inches(1.0), w=hw)
    # Date underneath
    text(s, "March 11, 2019",
         Inches(0), Inches(1.0) + hh + Inches(0.35), SLIDE_W, Inches(0.6),
         font=TITLE_FONT, size=28, bold=False, color=INK,
         align=PP_ALIGN.CENTER)
    # Subtle attribution at the bottom
    text(s, "Robert Wall  ·  Andrew Tangel  ·  Andy Pasztor   |   The Wall Street Journal",
         Inches(0), Inches(6.65), SLIDE_W, Inches(0.4),
         font=BODY_FONT, size=14, color=INK_MUTED,
         align=PP_ALIGN.CENTER)
    notes(s,
        "Hook (~25 sec). On October 29, 2018, Lion Air Flight 610 crashed. "
        "189 dead. On March 10, 2019, Ethiopian Airlines Flight 302 crashed. "
        "157 dead. Same aircraft. Same MCAS system. The next morning, the "
        "Wall Street Journal — America's paper of business record — chose to "
        "frame the news this way. (Pause. Let the audience read the headline.)")


def slide_2_timeline(prs):
    """Article in context (~35s): the timeline."""
    s = blank(prs)
    # Title
    text(s, "Same aircraft; no changes.",
         Inches(0.7), Inches(0.5), Inches(9.5), Inches(1),
         font=TITLE_FONT, size=40, bold=True, color=INK)
    # Ethiopian wreckage thumbnail (matches existing slide layout)
    image(s, "ethiopian_302_wreckage.png",
          Inches(9.4), Inches(0.45), w=Inches(3.5))
    # Horizontal timeline axis
    axis_y = Inches(4.05)
    rect(s, Inches(0.7), axis_y, Inches(11.93), Emu(38100), fill=LINE)
    # Five dots along the axis
    xs = [Inches(1.0), Inches(4.0), Inches(6.6), Inches(9.0), Inches(12.0)]
    for xp in xs:
        oval(s, xp - Inches(0.11), axis_y - Inches(0.11),
             Inches(0.22), Inches(0.22), LINE)

    # Date labels (above the line, anchored to dots)
    headers = [
        ("Oct 29, 2018",      "Lion Air 610",                 "189 dead",     xs[0]),
        ("Nov 13, 2018",      "MCAS revealed",                "WSJ breaks it", xs[1]),
        ("Mar 10, 2019",      "Ethiopian 302",                "157 dead",     xs[2]),
        ("Mar 11, 2019 (AM)", "China grounds 737 MAX",        None,           xs[3]),
        ("Mar 13, 2019",      "FAA finally grounds",          "(last major)", xs[4]),
    ]
    for date_str, line1, line2, xp in headers:
        # Date — bold, above the line
        text(s, date_str,
             xp - Inches(1.25), Inches(3.0), Inches(2.5), Inches(0.4),
             font=TITLE_FONT, size=14, bold=True, color=INK,
             align=PP_ALIGN.CENTER)
        text(s, line1,
             xp - Inches(1.25), Inches(3.4), Inches(2.5), Inches(0.4),
             font=BODY_FONT, size=12, color=INK,
             align=PP_ALIGN.CENTER)
        if line2:
            text(s, line2,
                 xp - Inches(1.25), Inches(3.7), Inches(2.5), Inches(0.4),
                 font=BODY_FONT, size=11, italic=True, color=ACCENT,
                 align=PP_ALIGN.CENTER)

    # Below the line: the wreckage photo + the two key WSJ headlines
    image(s, "lion_air_610_wreckage.png",
          Inches(0.7), Inches(4.6), w=Inches(2.6))
    image(s, "wsj_headline_nov21.png",
          Inches(3.6), Inches(4.9), w=Inches(4.6))
    image(s, "wsj_headline_march11.png",
          Inches(8.5), Inches(4.9), w=Inches(4.4))

    notes(s,
        "Timeline (~35 sec). By the time this article ran, China had already "
        "grounded the plane. Within 72 hours, 51 regulators worldwide grounded "
        "it. The FAA stood alone. The WSJ chose to frame the FAA's reluctance "
        "as the news — not the converging global consensus that this aircraft "
        "was killing people. Why? That's what the propaganda model explains.")


def slide_3_five_filters(prs):
    """Chomsky's five filters (~25s): funnel + canonical quote."""
    s = blank(prs)
    text(s, "Chomsky's Five Filters",
         Inches(0.7), Inches(0.5), Inches(12), Inches(0.9),
         font=TITLE_FONT, size=40, bold=True, color=INK)
    text(s, "Herman & Chomsky, Manufacturing Consent (1988 / 2002)",
         Inches(0.7), Inches(1.35), Inches(12), Inches(0.4),
         font=BODY_FONT, size=16, italic=True, color=INK_MUTED)

    # Five sequential gates, drawn as labeled rounded rectangles
    filters = [
        ("1", "Ownership",       "& profit orientation"),
        ("2", "Advertising",     "the reader economy"),
        ("3", "Sourcing",        "the beat & access economy"),
        ("4", "Flak",            "as anticipatory discipline"),
        ("5", "Unifying ideology", "anticommunism → ?"),
    ]
    box_w = Inches(2.25)
    box_h = Inches(2.0)
    gap = Inches(0.18)
    total_w = box_w * len(filters) + gap * (len(filters) - 1)
    start_x = (SLIDE_W - total_w) / 2
    y = Inches(2.3)
    for i, (num, name, sub) in enumerate(filters):
        x = start_x + (box_w + gap) * i
        r = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, box_w, box_h)
        r.fill.solid(); r.fill.fore_color.rgb = LINE
        r.line.fill.background()
        text(s, num, x, y + Inches(0.18), box_w, Inches(0.6),
             font=TITLE_FONT, size=28, bold=True,
             color=RGBColor(0xFF, 0xFF, 0xFF), align=PP_ALIGN.CENTER)
        text(s, name, x, y + Inches(0.9), box_w, Inches(0.5),
             font=TITLE_FONT, size=18, bold=True,
             color=RGBColor(0xFF, 0xFF, 0xFF), align=PP_ALIGN.CENTER)
        text(s, sub, x, y + Inches(1.40), box_w, Inches(0.5),
             font=BODY_FONT, size=12, italic=True,
             color=RGBColor(0xCF, 0xD6, 0xDE), align=PP_ALIGN.CENTER)
        # Arrow between boxes (skip after last)
        if i < len(filters) - 1:
            ax = x + box_w + Inches(0.02)
            ay = y + box_h / 2 - Inches(0.07)
            tri = s.shapes.add_shape(MSO_SHAPE.RIGHT_TRIANGLE,
                                     ax, ay, gap - Inches(0.04), Inches(0.14))
            tri.fill.solid(); tri.fill.fore_color.rgb = INK_MUTED
            tri.line.fill.background()

    # Quote slab below
    quote_y = Inches(4.85)
    rect(s, Inches(0.7), quote_y, Inches(11.93), Inches(2.1), fill=SLAB)
    rich_text(s, [
        [("“The constraints are so powerful, and are built into the system "
          "in such a fundamental way, that alternative bases of news choices "
          "are hardly imaginable.”",
          {"font": SERIF_FONT, "size": 22, "italic": True, "color": INK})],
        [(" ", {"size": 8})],
        [("— Herman & Chomsky, Manufacturing Consent, p. 2",
          {"font": BODY_FONT, "size": 14, "color": INK_MUTED})],
    ], Inches(1.1), quote_y + Inches(0.3), Inches(11.13), Inches(1.7))

    notes(s,
        "Five filters (~25 sec). Chomsky's argument is structural, not moral. "
        "The journalists in this case are not bad. Pasztor and Tangel actually "
        "broke the MCAS self-certification story. The propaganda model isn't a "
        "claim about individual bias. It's a claim about what survives passage "
        "through five structural filters.")


def slide_4_filter1_ownership(prs):
    """Filter 1: Ownership & class identity."""
    s = blank(prs)
    text(s, "Filter 1: Ownership & Profit Orientation",
         Inches(0.7), Inches(0.5), Inches(12), Inches(0.9),
         font=TITLE_FONT, size=36, bold=True, color=INK)

    # Two-column comparison.  Left = WSJ; Right = Boeing.  Headers as colored
    # slabs, then a bullet list under each.
    col_w = Inches(5.95)
    col_h = Inches(4.4)
    left_x = Inches(0.7)
    right_x = Inches(6.7)
    col_y = Inches(1.7)

    # Headers
    rect(s, left_x, col_y, col_w, Inches(0.7), fill=LINE)
    rect(s, right_x, col_y, col_w, Inches(0.7), fill=LINE)
    text(s, "WSJ  —  owner class", left_x, col_y, col_w, Inches(0.7),
         font=TITLE_FONT, size=20, bold=True,
         color=RGBColor(0xFF, 0xFF, 0xFF),
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    text(s, "Boeing  —  same class", right_x, col_y, col_w, Inches(0.7),
         font=TITLE_FONT, size=20, bold=True,
         color=RGBColor(0xFF, 0xFF, 0xFF),
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    # Column backgrounds (slab fill, below header)
    rect(s, left_x, col_y + Inches(0.7), col_w, col_h - Inches(0.7), fill=SLAB)
    rect(s, right_x, col_y + Inches(0.7), col_w, col_h - Inches(0.7), fill=SLAB)

    left_items = [
        "Owned by News Corp (Murdoch family)",
        "One of the world's largest media conglomerates",
        "Calculates the Dow Jones Industrial Average",
        "Reader base: corporate-financial elite",
    ]
    right_items = [
        "Top 30 U.S. corporation (~$240B market cap, 2019)",
        "Largest American exporter",
        "Dow Jones Industrial Average component",
        "Pentagon prime defense contractor",
        "Anchor employer for Washington + South Carolina",
    ]
    def bullets(items, x):
        body = "\n".join("•   " + it for it in items)
        text(s, body,
             x + Inches(0.4), col_y + Inches(0.95), col_w - Inches(0.6), Inches(3.2),
             font=BODY_FONT, size=16, color=INK, line_spacing=1.45)
    bullets(left_items, left_x)
    bullets(right_items, right_x)

    # Bottom line
    rect(s, Inches(0.7), Inches(6.35), Inches(11.93), Inches(0.7), fill=LINE)
    text(s, "Same elite.  Same interlocks.  Same class position.",
         Inches(0.7), Inches(6.35), Inches(11.93), Inches(0.7),
         font=TITLE_FONT, size=20, bold=True,
         color=RGBColor(0xFF, 0xFF, 0xFF),
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    notes(s,
        "Filter 1 (~35 sec). Filter 1 is not about Murdoch giving orders. "
        "It's about structural class identity. The WSJ exists as the paper of "
        "corporate America. Boeing is corporate America. The publication "
        "doesn't have to be told to cover Boeing carefully — it covers Boeing "
        "the way a class member covers another class member: critically "
        "interested, not adversarial.")


def slide_4b_news_corp_chart(prs):
    """Optional companion to slide 4 — the News Corp chart from the existing
    Canva deck.  Drop this slide if you want to keep the deck to 9.
    Currently included so the structural-class point is visually grounded
    the way the existing deck already does."""
    s = blank(prs)
    text(s, "Filter 1: Ownership & Profit Orientation",
         Inches(0.7), Inches(0.4), Inches(12), Inches(0.9),
         font=TITLE_FONT, size=36, bold=True, color=INK)
    # Constrain by height (image aspect ratio is 568 x 474 ≈ 1.20:1)
    chart_h = Inches(4.6)
    chart_w = Inches(4.6 * 568 / 474)   # ≈ 5.51"
    chart_x = (SLIDE_W - chart_w) / 2
    image(s, "news_corp_chart.png", chart_x, Inches(1.55), h=chart_h)
    text(s, "News Corp portfolio, 2019.   The WSJ sits inside the same elite "
            "structure it covers.",
         Inches(0.7), Inches(6.6), Inches(11.93), Inches(0.5),
         font=BODY_FONT, size=14, italic=True, color=INK_MUTED,
         align=PP_ALIGN.CENTER)
    notes(s,
        "Visual reinforcement of filter 1. The WSJ is one node in News Corp's "
        "global portfolio — the same conglomerate logic that Chomsky documents "
        "in Manufacturing Consent table 1-3 (p. 11).")


def slide_5_filter2_advertising(prs):
    """Filter 2: Advertising."""
    s = blank(prs)
    text(s, "Filter 2: Advertising",
         Inches(0.7), Inches(0.5), Inches(12), Inches(0.9),
         font=TITLE_FONT, size=36, bold=True, color=INK)
    text(s, "WSJ's advertiser ecology in 2019.",
         Inches(0.7), Inches(1.35), Inches(12), Inches(0.5),
         font=BODY_FONT, size=18, italic=True, color=INK_MUTED)

    # 4 × 3 logo placeholder grid
    advertisers = [
        ["Boeing",        "Lockheed Martin", "Northrop Grumman", "GE Aerospace"],
        ["Honeywell",     "Southwest",       "American",         "United"],
        ["Delta",         "JPMorgan",        "Goldman Sachs",    "BlackRock"],
    ]
    grid_x = Inches(0.7)
    grid_y = Inches(2.1)
    cell_w = Inches(2.95)
    cell_h = Inches(1.05)
    gap = Inches(0.10)
    for r, row in enumerate(advertisers):
        for c, name in enumerate(row):
            x = grid_x + (cell_w + gap) * c
            y = grid_y + (cell_h + gap) * r
            placeholder(s, name, x, y, cell_w, cell_h)

    # Bottom takeaway
    rect(s, Inches(0.7), Inches(6.05), Inches(11.93), Inches(1.05), fill=LINE)
    text(s, "Filter 2 doesn't kill individual articles.\nIt kills sustained campaigns.",
         Inches(0.7), Inches(6.05), Inches(11.93), Inches(1.05),
         font=TITLE_FONT, size=22, bold=True,
         color=RGBColor(0xFF, 0xFF, 0xFF),
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    notes(s,
        "Filter 2 (~30 sec). WSJ's reader base — corporate executives, "
        "institutional investors, money managers — holds Boeing in their "
        "portfolios, their pension funds, their company stock plans. The "
        "advertiser ecology is the same ecology. A single critical article? "
        "Fine. A multi-month campaign reframing American manufacturing as "
        "systemically unsafe? That would shift the publication's relationship "
        "to its entire reader-advertiser ecology. So it doesn't happen.")


def slide_6_filter3_sourcing(prs):
    """Filter 3: Sourcing — two-column voice breakdown + Fishman quote."""
    s = blank(prs)
    text(s, "Filter 3: Sourcing",
         Inches(0.7), Inches(0.5), Inches(12), Inches(0.9),
         font=TITLE_FONT, size=36, bold=True, color=INK)
    text(s, "Whose voices structure the article — and whose appear only as reactions.",
         Inches(0.7), Inches(1.35), Inches(12), Inches(0.5),
         font=BODY_FONT, size=16, italic=True, color=INK_MUTED)

    col_w = Inches(5.95)
    left_x = Inches(0.7)
    right_x = Inches(6.7)
    col_y = Inches(2.0)
    col_h = Inches(3.2)

    rect(s, left_x, col_y, col_w, Inches(0.65), fill=LINE)
    rect(s, right_x, col_y, col_w, Inches(0.65), fill=ACCENT)
    text(s, "Voices that structure the story",
         left_x, col_y, col_w, Inches(0.65),
         font=TITLE_FONT, size=16, bold=True,
         color=RGBColor(0xFF, 0xFF, 0xFF),
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    text(s, "Voices that appear only as reactions  (or not at all)",
         right_x, col_y, col_w, Inches(0.65),
         font=TITLE_FONT, size=16, bold=True,
         color=RGBColor(0xFF, 0xFF, 0xFF),
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    rect(s, left_x,  col_y + Inches(0.65), col_w, col_h - Inches(0.65), fill=SLAB)
    rect(s, right_x, col_y + Inches(0.65), col_w, col_h - Inches(0.65), fill=SLAB)

    left_voices = [
        "The FAA — authoritative on its own decision",
        "Boeing — authoritative on its own aircraft",
        "U.S. airline executives (Southwest, American, United)",
        "Anonymous “industry officials”",
    ]
    right_voices = [
        "Mitt Romney (calling for grounding)",
        "Foreign regulators (China, EU) — reactive framing",
        "Victims' families — absent",
        "Ethiopian / Indonesian regulators — absent",
    ]
    def bullets(items, x):
        body = "\n".join("•  " + it for it in items)
        text(s, body,
             x + Inches(0.35), col_y + Inches(0.85), col_w - Inches(0.5), Inches(2.4),
             font=BODY_FONT, size=14, color=INK, line_spacing=1.50)
    bullets(left_voices, left_x)
    bullets(right_voices, right_x)

    # Quote slab
    quote_y = Inches(5.55)
    rect(s, Inches(0.7), quote_y, Inches(11.93), Inches(1.55), fill=LINE)
    rich_text(s, [
        [("“Officials have and give the facts; reporters merely get them.”",
          {"font": SERIF_FONT, "size": 22, "italic": True,
           "color": RGBColor(0xFF, 0xFF, 0xFF)})],
        [(" ", {"size": 6})],
        [("— Mark Fishman, quoted in Manufacturing Consent, p. 19",
          {"font": BODY_FONT, "size": 13, "color": RGBColor(0xCF, 0xD6, 0xDE)})],
    ], Inches(1.1), quote_y + Inches(0.22), Inches(11.13), Inches(1.2))

    notes(s,
        "Filter 3 (~40 sec — give this one extra time). This is filter 3 in "
        "operation, visible inside the article. The FAA gets framed as "
        "authority, not as a regulator that delegated certification to Boeing "
        "employees. The captured-regulator story was reportable — Dominic "
        "Gates at the Seattle Times broke it six days later. The WSJ team "
        "knew the issue existed. They didn't lead with it. Why? Because "
        "reframing the FAA from 'authoritative source' to 'captured "
        "regulator' breaks the aviation beat. The beat is how aviation "
        "reporters survive commercially. So the frame stays.")


def slide_7_filter4_flak(prs):
    """Filter 4: Flak — Boeing's apparatus, anticipatory."""
    s = blank(prs)
    text(s, "Filter 4: Flak",
         Inches(0.7), Inches(0.5), Inches(12), Inches(0.9),
         font=TITLE_FONT, size=36, bold=True, color=INK)
    text(s, "Boeing's flak apparatus, March 2019.",
         Inches(0.7), Inches(1.35), Inches(12), Inches(0.5),
         font=BODY_FONT, size=18, italic=True, color=INK_MUTED)

    flak_items = [
        ("White-shoe PR firms on retainer",
         "Multi-firm crisis-communications stack."),
        ("Defamation lawyers ready to issue letters",
         "Cease-and-desist as a routine instrument."),
        ("Pentagon relationships",
         "Top-tier U.S. defense contractor; revolving-door access."),
        ("Acting Defense Secretary Patrick Shanahan",
         "Former Boeing executive of 30+ years."),
        ("Congressional offices in every Boeing state",
         "Direct political channels in WA, SC, MO, KS, AL, CA, …"),
    ]
    list_x = Inches(0.7)
    list_y = Inches(2.0)
    row_h = Inches(0.8)
    for i, (head, sub) in enumerate(flak_items):
        y = list_y + row_h * i
        # Red dot
        oval(s, list_x, y + Inches(0.18), Inches(0.28), Inches(0.28), ACCENT)
        text(s, head,
             list_x + Inches(0.55), y, Inches(11.3), Inches(0.4),
             font=TITLE_FONT, size=18, bold=True, color=INK)
        text(s, sub,
             list_x + Inches(0.55), y + Inches(0.38), Inches(11.3), Inches(0.4),
             font=BODY_FONT, size=14, italic=True, color=INK_MUTED)

    # Bottom takeaway slab
    rect(s, Inches(0.7), Inches(6.35), Inches(11.93), Inches(0.75), fill=ACCENT)
    text(s, "Flak doesn't have to land.  It has to be anticipated.",
         Inches(0.7), Inches(6.35), Inches(11.93), Inches(0.75),
         font=TITLE_FONT, size=20, bold=True,
         color=RGBColor(0xFF, 0xFF, 0xFF),
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    notes(s,
        "Filter 4 (~30 sec). Chomsky's insight here is that flak is most "
        "powerful when invisible. There's no record of Boeing threatening "
        "Pasztor or Tangel over this article. But they had been covering "
        "Boeing for years. They knew which framings generate calls to the "
        "publisher, which ones lose access to the media office, which ones "
        "cost the beat. The softening choices — 'deadly crash' rather than "
        "'second mass-fatality crash,' 'the FAA's decision' rather than 'the "
        "regulator that let Boeing certify itself' — are filter 4 working "
        "without anyone having to make a threat.")


def slide_8_filter5_ideology(prs):
    """Filter 5: The updated ideology — the paper's analytical move."""
    s = blank(prs)
    text(s, "Filter 5: The Updated Ideology",
         Inches(0.7), Inches(0.5), Inches(12), Inches(0.9),
         font=TITLE_FONT, size=36, bold=True, color=INK)

    # Three eras, large
    eras = [
        ("Chomsky 1988",     "Anticommunism"),
        ("Chomsky 2002",     "The religion of the market"),
        ("2019 aviation",    "Techno-industrial nationalism"),
    ]
    era_y = Inches(1.55)
    era_h = Inches(0.55)
    for i, (when, label) in enumerate(eras):
        y = era_y + (era_h + Inches(0.05)) * i
        text(s, when,
             Inches(0.7), y, Inches(3.8), era_h,
             font=BODY_FONT, size=20, italic=True, color=INK_MUTED,
             anchor=MSO_ANCHOR.MIDDLE)
        text(s, label,
             Inches(4.5), y, Inches(8.5), era_h,
             font=TITLE_FONT, size=26, bold=True,
             color=ACCENT if i == 2 else INK,
             anchor=MSO_ANCHOR.MIDDLE)

    # Two-column worthy / unworthy victim table
    tbl_y = Inches(3.55)
    col_w = Inches(5.95)
    left_x = Inches(0.7)
    right_x = Inches(6.7)
    rect(s, left_x,  tbl_y, col_w, Inches(0.55), fill=LINE)
    rect(s, right_x, tbl_y, col_w, Inches(0.55), fill=ACCENT)
    text(s, "Worthy victims  (1983)",
         left_x, tbl_y, col_w, Inches(0.55),
         font=TITLE_FONT, size=16, bold=True,
         color=RGBColor(0xFF, 0xFF, 0xFF),
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    text(s, "Unworthy victims  (2018–19)",
         right_x, tbl_y, col_w, Inches(0.55),
         font=TITLE_FONT, size=16, bold=True,
         color=RGBColor(0xFF, 0xFF, 0xFF),
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    rows = [
        ("KAL 007 passengers (Soviet shootdown)",  "Lion Air 610 — 189 Indonesians"),
        ("Sustained moral outrage; years of coverage", "“Pilot training” framing"),
        ("Reagan: “cold-blooded murder”",   "Ethiopian 302 — 157 dead, 35 nations"),
        ("Front-page treatment for years",            "132 days before grounding"),
    ]
    row_h = Inches(0.55)
    for i, (l, r) in enumerate(rows):
        y = tbl_y + Inches(0.55) + row_h * i
        rect(s, left_x,  y, col_w, row_h, fill=SLAB)
        rect(s, right_x, y, col_w, row_h, fill=SLAB)
        text(s, l, left_x + Inches(0.25), y, col_w - Inches(0.4), row_h,
             font=BODY_FONT, size=13, color=INK, anchor=MSO_ANCHOR.MIDDLE)
        text(s, r, right_x + Inches(0.25), y, col_w - Inches(0.4), row_h,
             font=BODY_FONT, size=13, color=INK, anchor=MSO_ANCHOR.MIDDLE)

    # Quote slab at the bottom
    quote_y = Inches(6.45)
    rect(s, Inches(0.7), quote_y, Inches(11.93), Inches(0.75), fill=LINE)
    rich_text(s, [
        [("“Concentrate on the victims of enemy powers and forget "
          "about the victims of friends.”     ",
          {"font": SERIF_FONT, "size": 16, "italic": True,
           "color": RGBColor(0xFF, 0xFF, 0xFF)}),
         ("— Herman & Chomsky, p. 32",
          {"font": BODY_FONT, "size": 12,
           "color": RGBColor(0xCF, 0xD6, 0xDE)})],
    ], Inches(0.9), quote_y, Inches(11.5), Inches(0.75),
        align=PP_ALIGN.CENTER)
    # Vertically center the quote within the slab by anchoring the textbox.
    # (Done via the rich_text body wrapper; if it reads off, nudge by hand.)

    notes(s,
        "Filter 5 (~40 sec — your analytical move). Chomsky's original filter "
        "5 was anticommunism — the binary that defined worthy and unworthy "
        "victims. He updated it in 2002 to 'the religion of the market.' For "
        "2019 aviation coverage, I'd argue the operative filter 5 is "
        "techno-industrial nationalism: American manufacturing supremacy as "
        "quasi-religious national interest. The worthy/unworthy victims "
        "structure is identical to 1983 KAL 007. Different ideology, same "
        "filter. The dead were Indonesian, Indian, Ethiopian, Kenyan. The "
        "initial framing leaned on 'foreign pilot training.' Imagine the "
        "alternative.")


def slide_9_counterfactual(prs):
    """Counterfactual close: the headline that would have run."""
    s = blank(prs)
    text(s, "The Counterfactual",
         Inches(0.7), Inches(0.4), Inches(12), Inches(0.7),
         font=TITLE_FONT, size=28, bold=True, color=INK_MUTED)

    # Mocked WSJ headline — typeset in a serif, centered, large.  Frame it
    # in a white slab to mimic newsprint.
    headline_y = Inches(1.6)
    rect(s, Inches(0.9), headline_y, Inches(11.5), Inches(3.2),
         fill=RGBColor(0xFF, 0xFF, 0xFF), line=INK_MUTED)
    rich_text(s, [
        [("BUSINESS",
          {"font": BODY_FONT, "size": 14, "bold": True,
           "color": INK_MUTED})],
        [(" ", {"size": 10})],
        [("Pressure Mounts on FAA to Ground 737 MAX",
          {"font": SERIF_FONT, "size": 36, "bold": True, "color": INK})],
        [("as Second Crash Kills 157 Americans",
          {"font": SERIF_FONT, "size": 36, "bold": True, "color": INK})],
        [(" ", {"size": 8})],
        [("Lawmakers, victims' families, and foreign regulators "
          "demand immediate suspension; FAA's certification process under scrutiny.",
          {"font": SERIF_FONT, "size": 16, "italic": True, "color": INK_MUTED})],
        [(" ", {"size": 12})],
        [("By [byline]    |    Updated March 11, 2019",
          {"font": BODY_FONT, "size": 13, "bold": True, "color": INK})],
    ], Inches(1.25), headline_y + Inches(0.25), Inches(10.8), Inches(2.7),
       align=PP_ALIGN.LEFT, line_spacing=1.05)

    # Two stacked taglines under the mock headline
    text(s, "This is the headline if 346 Americans had died.",
         Inches(0.7), Inches(5.15), Inches(11.93), Inches(0.55),
         font=TITLE_FONT, size=22, bold=True, color=INK,
         align=PP_ALIGN.CENTER)
    # Final landing line, in red
    rect(s, Inches(0.7), Inches(6.05), Inches(11.93), Inches(1.05), fill=ACCENT)
    text(s, "The filters didn't lie.  They selected.",
         Inches(0.7), Inches(6.05), Inches(11.93), Inches(1.05),
         font=TITLE_FONT, size=28, bold=True,
         color=RGBColor(0xFF, 0xFF, 0xFF),
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    notes(s,
        "Close (~30 sec). If 346 Americans had died on two domestic flights "
        "of the same aircraft in five months, this would have been the "
        "headline. Same facts, different victims, different filter output. "
        "The propaganda model isn't a claim that this article lied. It's a "
        "claim that the structural conditions of its production — Murdoch's "
        "WSJ covering a major American manufacturer, Boeing's flak apparatus, "
        "the access economy on the aviation beat, the techno-nationalist "
        "common sense — selected for the framing we got. Chomsky's model "
        "holds. Filter 5 has just rotated from anticommunism to "
        "techno-industrial nationalism. (End. Don't trail off. Pause, then "
        "thank them.)")


# ---------------- driver ----------------

def main():
    prs = make_prs()
    slide_1_hook(prs)
    slide_2_timeline(prs)
    slide_3_five_filters(prs)
    slide_4_filter1_ownership(prs)
    slide_4b_news_corp_chart(prs)
    slide_5_filter2_advertising(prs)
    slide_6_filter3_sourcing(prs)
    slide_7_filter4_flak(prs)
    slide_8_filter5_ideology(prs)
    slide_9_counterfactual(prs)
    prs.save(OUT)
    print(f"wrote {OUT} ({OUT.stat().st_size:,} bytes, {len(prs.slides)} slides)")


if __name__ == "__main__":
    main()
