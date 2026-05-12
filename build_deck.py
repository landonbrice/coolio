"""build_deck.py — v4
=====================================================================
Generates Boeing-WSJ-Propaganda-Model-v4.pptx.

v4 merges v3's intellectual posture (degree-of-fit assessment, NOT-claim
/ CAN-claim pedagogy, verdict matrix close) with v1/v2's missing
presentation elements (WSJ headline screenshot, structural-facts
timeline, verbatim Chomsky quotes on every filter slide, Pasztor +
Tangel as good reporters, Patrick Shanahan, KAL 007 / Lion Air
worthy / unworthy strip).

Visual language: matched to v3 — Helvetica Neue everywhere (Georgia
for newspaper-style content), 0.13" blue rail on the left edge,
Tailwind-style palette (ink #111827, blue #1D4ED8, red #B91C1C,
slate #64748B, off-white cards #F9FAFB on #E5E7EB borders), 8pt
bold page number bottom right.

Run:
    python3 build_deck.py
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
OUT = ROOT / "Boeing-WSJ-Propaganda-Model-v4.pptx"

# ---------------- tokens (matched to v3 by inspection) ----------------

BG       = RGBColor(0xFF, 0xFF, 0xFF)
RAIL     = RGBColor(0x1D, 0x4E, 0xD8)   # blue-700, left-edge rail
INK      = RGBColor(0x11, 0x18, 0x27)   # slate-900
KICKER   = RGBColor(0x1D, 0x4E, 0xD8)   # blue-700
RED      = RGBColor(0xB9, 0x1C, 0x1C)   # red-700
SLATE    = RGBColor(0x64, 0x74, 0x8B)   # slate-500
CARD     = RGBColor(0xF9, 0xFA, 0xFB)   # off-white card fill
CARD_2   = RGBColor(0xF8, 0xFA, 0xFC)   # slightly cooler card fill
BORDER   = RGBColor(0xE5, 0xE7, 0xEB)   # gray-200 border
GREEN    = RGBColor(0x05, 0x96, 0x69)   # emerald-600 for "LOW COST"
GREEN_BG = RGBColor(0xEC, 0xFD, 0xF5)   # emerald-50
ORANGE   = RGBColor(0xC2, 0x41, 0x0C)   # orange-700 for MEDIUM
ORANGE_BG= RGBColor(0xFF, 0xF7, 0xED)   # orange-50
RED_BG   = RGBColor(0xFE, 0xF2, 0xF2)   # red-50

SANS  = "Helvetica Neue"
SERIF = "Georgia"

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)


# ---------------- low-level helpers ----------------

def make_prs():
    p = Presentation()
    p.slide_width = SLIDE_W
    p.slide_height = SLIDE_H
    return p


def chrome(prs, idx):
    """Blank slide + blue left rail + page-number footer."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, SLIDE_H)
    bg.line.fill.background(); bg.fill.solid(); bg.fill.fore_color.rgb = BG
    rail = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(0.13), SLIDE_H)
    rail.line.fill.background(); rail.fill.solid(); rail.fill.fore_color.rgb = RAIL
    # bottom-right page number
    text(slide, f"{idx:02d}",
         SLIDE_W - Inches(1.0), Inches(7.15), Inches(0.5), Inches(0.3),
         font=SANS, size=8, bold=True, color=SLATE,
         align=PP_ALIGN.RIGHT)
    return slide


def text(slide, body, x, y, w, h, *,
         font=SANS, size=12, bold=False, italic=False,
         color=INK, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
         line_spacing=1.2, strike=False):
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
        r = p.add_run()
        r.text = line
        r.font.name = font; r.font.size = Pt(size)
        r.font.bold = bold; r.font.italic = italic
        r.font.color.rgb = color
        if strike:
            # apply strikethrough via XML
            rPr = r._r.get_or_add_rPr()
            rPr.set("strike", "sngStrike")
    return tb


def rich(slide, paras, x, y, w, h, *, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, line_spacing=1.2):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Emu(0)
    tf.margin_top = tf.margin_bottom = Emu(0)
    tf.vertical_anchor = anchor
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = line_spacing
        for chunk, st in para:
            r = p.add_run()
            r.text = chunk
            r.font.name = st.get("font", SANS)
            r.font.size = Pt(st.get("size", 12))
            r.font.bold = st.get("bold", False)
            r.font.italic = st.get("italic", False)
            r.font.color.rgb = st.get("color", INK)
            if st.get("strike"):
                rPr = r._r.get_or_add_rPr()
                rPr.set("strike", "sngStrike")
    return tb


def card(slide, x, y, w, h, *, fill=CARD, border=BORDER, border_w=Pt(0.75)):
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    s.fill.solid(); s.fill.fore_color.rgb = fill
    s.line.color.rgb = border; s.line.width = border_w
    return s


def rect(slide, x, y, w, h, *, fill, line=None):
    r = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    r.fill.solid(); r.fill.fore_color.rgb = fill
    if line is None: r.line.fill.background()
    else:
        r.line.color.rgb = line
    return r


def dot(slide, x, y, d, color):
    o = slide.shapes.add_shape(MSO_SHAPE.OVAL, x, y, d, d)
    o.fill.solid(); o.fill.fore_color.rgb = color
    o.line.fill.background()
    return o


def kicker_title(slide, kicker, title, sub=None):
    """v3-style header: small blue kicker, large bold title, optional
    slate subtitle."""
    text(slide, kicker.upper(),
         Inches(0.55), Inches(0.5), Inches(12), Inches(0.3),
         font=SANS, size=9, bold=True, color=KICKER)
    text(slide, title,
         Inches(0.55), Inches(0.83), Inches(12.5), Inches(0.85),
         font=SANS, size=30, bold=True, color=INK, line_spacing=1.1)
    if sub:
        text(slide, sub,
             Inches(0.55), Inches(1.78), Inches(12.5), Inches(0.45),
             font=SANS, size=13, color=SLATE, line_spacing=1.3)


def quote_footer(slide, body, attribution, y=Inches(6.35)):
    """Compact verbatim-quote footer for the bottom of filter slides.
    Italics serif body + sans attribution.  Sits above the source-footer
    band (y=7.15) with ~0.35" clearance."""
    rich(slide, [
        [("“" + body + "”   ",
          {"font": SERIF, "size": 11, "italic": True, "color": INK}),
         (attribution,
          {"font": SANS, "size": 9, "color": SLATE})],
    ], Inches(0.55), y, Inches(12.2), Inches(0.65))


def image(slide, name, x, y, w=None, h=None):
    return slide.shapes.add_picture(str(IMG / name), x, y, width=w, height=h)


def notes(slide, outline, script):
    parts = []
    parts.append("OUTLINE")
    for i, beat in enumerate(outline, 1):
        parts.append(f"  {i}. {beat}")
    parts.append("")
    parts.append("SCRIPT")
    parts.append(script)
    slide.notes_slide.notes_text_frame.text = "\n".join(parts)


def footer(slide, body):
    """Source / context footer.  Smaller and slightly higher than v3 so it
    doesn't fight the quote_footer above it."""
    text(slide, body,
         Inches(0.55), Inches(7.15), Inches(11.0), Inches(0.3),
         font=SANS, size=7, color=SLATE, line_spacing=1.2)


# ---------------- slide builders ----------------

def slide_1_puzzle(prs):
    s = chrome(prs, 1)
    kicker_title(s, "The puzzle",
                 "A mass-death crisis became an FAA patience story.",
                 sub="The deck measures how strongly the propaganda model fits "
                     "one WSJ article, not whether every filter is equally proven.")

    # Left: actual WSJ headline screenshot inside a paper card
    card_x = Inches(0.55); card_y = Inches(2.55)
    card_w = Inches(7.85); card_h = Inches(3.5)
    card(s, card_x, card_y, card_w, card_h)
    # Image fits inside the card with margins.  WSJ headline is ~803x297 ≈ 2.7:1
    img_w = card_w - Inches(0.8)
    img_h = img_w * 297 / 803
    image(s, "wsj_headline_march11.png",
          card_x + Inches(0.4), card_y + (card_h - img_h) / 2, w=img_w)

    # Right: three labeled fact cards (v3 layout, preserved)
    right_x = Inches(8.75); right_w = Inches(4.05)
    facts = [
        ("OBSERVED FRAME",
         "FAA reluctance is the organizing fact.", KICKER),
        ("UNDERLYING FACTS",
         "189 + 157 = 346 dead.  Same aircraft.  Same MCAS.  132 days.", RED),
        ("QUESTION",
         "Why did this frame feel professionally natural?", INK),
    ]
    for i, (label, body, label_color) in enumerate(facts):
        ry = Inches(2.55) + Inches(1.18) * i
        card(s, right_x, ry, right_w, Inches(1.0))
        text(s, label,
             right_x + Inches(0.25), ry + Inches(0.15),
             right_w - Inches(0.4), Inches(0.25),
             font=SANS, size=8, bold=True, color=label_color)
        text(s, body,
             right_x + Inches(0.25), ry + Inches(0.40),
             right_w - Inches(0.4), Inches(0.55),
             font=SANS, size=13, bold=True, color=INK, line_spacing=1.2)

    footer(s, "WSJ headline reproduced from the article under analysis "
              "(Wall, Tangel, Pasztor — Mar 11, 2019). "
              "Citation corroborated in House Transportation Committee 737 MAX report.")

    notes(s,
        outline=[
            "Open with the distinction: test case, not conspiracy claim.",
            "The article did not have to lie to matter.",
            "Frame the puzzle: why does this read as FAA patience, not mass-death scandal?",
            "Pause and let the audience read the headline.",
        ],
        script=(
            "On October 29, 2018, Lion Air Flight 610 crashed. 189 dead. On March "
            "10, 2019, Ethiopian Airlines Flight 302 crashed. 157 more dead. Same "
            "aircraft. Same MCAS system. 346 people across two crashes of the same "
            "aircraft in 132 days. The morning after the second crash, the Wall "
            "Street Journal — America's paper of business record — chose to frame "
            "the news this way. This deck measures how strongly Chomsky's "
            "propaganda model fits that framing. Not whether every filter is "
            "equally proven — degree of fit. The puzzle is why a mass-death crisis "
            "became an FAA patience story."
        ),
    )


def slide_2_structural_facts(prs):
    """NEW — restores the timeline that v3 dropped."""
    s = chrome(prs, 2)
    kicker_title(s, "The structural facts",
                 "Within 72 hours, the world grounded the aircraft. The FAA didn’t.",
                 sub="Before the model: hold the timeline in mind. "
                     "China grounded the 737 MAX before the WSJ article ran.")

    # Horizontal timeline axis
    axis_x = Inches(0.85); axis_y = Inches(3.55)
    axis_w = Inches(11.6)
    rect(s, axis_x, axis_y, axis_w, Emu(28000), fill=SLATE)

    events = [
        ("Oct 29, 2018",  "Lion Air 610",            "189 dead",            0.06),
        ("Nov 13, 2018",  "MCAS revealed (WSJ)",     "Pasztor / Tangel",    0.25),
        ("Mar 10, 2019",  "Ethiopian 302",           "157 dead",            0.50),
        ("Mar 11 AM",     "China grounds 737 MAX",   "before WSJ article",  0.72),
        ("Mar 13",        "FAA finally grounds",     "(last major)",        0.95),
    ]
    for date, line1, line2, frac in events:
        cx = axis_x + axis_w * frac
        dot(s, cx - Inches(0.10), axis_y - Inches(0.10),
            Inches(0.20), RAIL)
        # date above
        text(s, date,
             cx - Inches(1.0), Inches(2.50), Inches(2.0), Inches(0.3),
             font=SANS, size=10, bold=True, color=INK,
             align=PP_ALIGN.CENTER)
        # event name below the dot
        text(s, line1,
             cx - Inches(1.1), axis_y + Inches(0.18), Inches(2.2), Inches(0.35),
             font=SANS, size=11, bold=True, color=INK,
             align=PP_ALIGN.CENTER)
        text(s, line2,
             cx - Inches(1.1), axis_y + Inches(0.55), Inches(2.2), Inches(0.3),
             font=SANS, size=9, italic=True, color=RED,
             align=PP_ALIGN.CENTER)

    # Three fact strips below the timeline
    strip_y = Inches(5.10)
    strip_w = Inches(3.95); strip_h = Inches(1.25)
    gap = Inches(0.15)
    strips = [
        ("132", "days separated Lion Air and Ethiopian", INK),
        ("51",  "regulators grounded the 737 MAX within 72 hours of Ethiopian", RAIL),
        ("72",  "hours the FAA stood alone among major regulators", RED),
    ]
    for i, (n, body, color) in enumerate(strips):
        x = Inches(0.55) + (strip_w + gap) * i
        card(s, x, strip_y, strip_w, strip_h)
        text(s, n,
             x + Inches(0.3), strip_y + Inches(0.15), Inches(1.5), Inches(0.9),
             font=SANS, size=50, bold=True, color=color, line_spacing=1.0)
        text(s, body,
             x + Inches(2.0), strip_y + Inches(0.25),
             strip_w - Inches(2.15), strip_h - Inches(0.3),
             font=SANS, size=11, color=INK, line_spacing=1.3)

    # Claim line
    text(s,
         "The article’s organizing fact is the FAA’s reluctance — "
         "not the worldwide consensus.",
         Inches(0.55), Inches(6.55), Inches(11.5), Inches(0.35),
         font=SANS, size=13, bold=True, color=INK, align=PP_ALIGN.CENTER)

    footer(s, "Timeline corroborated in the House Transportation Committee 737 MAX "
              "report; grounding sequence per FAA / EASA / CAAC contemporaneous statements.")

    notes(s,
        outline=[
            "Hold the structural facts before you invoke the model.",
            "132 days; 51 regulators in 72 hours; FAA last.",
            "China grounded BEFORE the WSJ article ran — central to the puzzle.",
            "Land the claim: organizing fact = FAA reluctance, not global consensus.",
            "Transition: 'Now — what does Chomsky predict, and what does this prove?'",
        ],
        script=(
            "Before the model, hold the structural facts. 132 days separated Lion "
            "Air and Ethiopian — the same aircraft killing people again on the "
            "same flight profile. Within 72 hours of Ethiopian, 51 regulators "
            "worldwide grounded the 737 MAX. China grounded the aircraft on the "
            "morning of March 11 — BEFORE the Wall Street Journal article ran. "
            "By the time the FAA finally grounded on March 13, it was the LAST "
            "major regulator to do so. The article’s organizing fact is the "
            "FAA’s reluctance, not the worldwide consensus. That choice of "
            "frame is what the propaganda model is going to help us see."
        ),
    )


def slide_3_model(prs):
    s = chrome(prs, 3)
    kicker_title(s, "The model",
                 "Chomsky predicts selection, not puppetry.",
                 sub="The useful question is degree of fit — which filters are "
                     "article-level evidence, and which are background conditions.")

    # Five-filter chain across the slide
    chain_y = Inches(2.55)
    box_w   = Inches(2.30); box_h = Inches(1.40)
    gap     = Inches(0.12)
    start_x = Inches(0.55)
    filters = [
        ("1", "Ownership",   "background"),
        ("2", "Advertising", "background"),
        ("3", "Sourcing",    "article-level"),
        ("4", "Flak",        "anticipated cost"),
        ("5", "Ideology",    "article-level"),
    ]
    for i, (num, name, tag) in enumerate(filters):
        x = start_x + (box_w + gap) * i
        # Filter-3 and filter-5 get a stronger highlight (load-bearing)
        highlight = i in (2, 4)
        card(s, x, chain_y, box_w, box_h,
             fill=CARD_2 if highlight else CARD,
             border=RAIL if highlight else BORDER,
             border_w=Pt(1.25 if highlight else 0.75))
        text(s, num,
             x + Inches(0.25), chain_y + Inches(0.18), Inches(0.4), Inches(0.35),
             font=SANS, size=14, bold=True, color=RAIL)
        text(s, name,
             x + Inches(0.7), chain_y + Inches(0.18), box_w - Inches(0.85), Inches(0.4),
             font=SANS, size=15, bold=True, color=INK)
        text(s, tag,
             x + Inches(0.25), chain_y + Inches(0.85), box_w - Inches(0.5), Inches(0.4),
             font=SANS, size=10, italic=True, color=SLATE)
        # Chevron between boxes
        if i < len(filters) - 1:
            ax = x + box_w + Inches(0.01)
            ay = chain_y + box_h / 2 - Inches(0.05)
            tri = s.shapes.add_shape(MSO_SHAPE.RIGHT_TRIANGLE,
                                     ax, ay, gap - Inches(0.02), Inches(0.1))
            tri.fill.solid(); tri.fill.fore_color.rgb = SLATE
            tri.line.fill.background()

    # Working-standard callout (v3's strongest move on this slide; preserved)
    cs_y = Inches(4.55); cs_w = Inches(12.2); cs_h = Inches(1.45)
    card(s, Inches(0.55), cs_y, cs_w, cs_h)
    text(s, "WORKING STANDARD",
         Inches(0.85), cs_y + Inches(0.20), Inches(11), Inches(0.3),
         font=SANS, size=9, bold=True, color=KICKER)
    text(s, "Partial filters still matter if they help explain why the "
            "stronger filters can operate.",
         Inches(0.85), cs_y + Inches(0.50), Inches(11.5), Inches(0.85),
         font=SANS, size=18, bold=True, color=INK, line_spacing=1.25)

    quote_footer(s,
        "the constraints are so powerful … that alternative bases of news "
        "choices are hardly imaginable.",
        "— Herman & Chomsky, Manufacturing Consent, p. 2")

    footer(s, "Filter taxonomy from Manufacturing Consent (Pantheon, 1988 / 2002). "
              "Filter labels ‘article-level’ vs ‘background’ "
              "are this paper’s degree-of-fit annotation.")

    notes(s,
        outline=[
            "Structural, not moral: the journalists are not the explanatory variable.",
            "Filters reinforce; no single filter is decisive.",
            "Distinguish article-level proof (3, 5) from background conditions (1, 2, 4).",
            "Working standard: partial filters explain why the stronger ones can operate.",
            "Transition: 'Start with the textual evidence on slide 4.'",
        ],
        script=(
            "Chomsky’s claim is structural, not moral. He is not saying the "
            "press is fake or that journalists are corrupt. The filters select "
            "what survives. Pasztor and Tangel — the WSJ team on this "
            "article — had broken the MCAS self-certification story four "
            "months earlier. They are not bad reporters. The propaganda model is "
            "most powerful when the journalism is competent. In this deck I treat "
            "filters 3 and 5 as article-level evidence, filters 1 and 2 as "
            "structural background, and filter 4 as anticipated cost — "
            "indirect but reinforcing. Partial filters still matter if they help "
            "explain why the stronger filters can operate."
        ),
    )


def slide_4_frame(prs):
    s = chrome(prs, 4)
    kicker_title(s, "The frame",
                 "The article makes the FAA the fact-giver.",
                 sub="Before theory, the text itself has a center of gravity: "
                     "official U.S. authority.")

    col_h = Inches(3.6)
    col_w = Inches(3.95)
    col_y = Inches(2.40)
    gap = Inches(0.15)
    headers = [
        ("Organizing authority",       RAIL),
        ("Secondary in the article",   ORANGE),
        ("Missing as knowers",         RED),
    ]
    bodies = [
        ["FAA", "Boeing", "U.S. airlines", "Industry officials (anonymous)"],
        ["China grounding", "EASA / foreign regulators", "U.S. politicians"],
        ["Victims’ families", "Ethiopian / Indonesian safety authorities",
         "Captured-regulator frame"],
    ]
    for i, ((label, color), items) in enumerate(zip(headers, bodies)):
        x = Inches(0.55) + (col_w + gap) * i
        text(s, label,
             x, col_y, col_w, Inches(0.3),
             font=SANS, size=12, bold=True, color=color)
        for j, item in enumerate(items):
            iy = col_y + Inches(0.45) + Inches(0.65) * j
            card(s, x, iy, col_w, Inches(0.55),
                 fill=CARD, border=BORDER, border_w=Pt(0.75))
            text(s, item,
                 x + Inches(0.25), iy, col_w - Inches(0.4), Inches(0.55),
                 font=SANS, size=12, bold=True, color=color,
                 anchor=MSO_ANCHOR.MIDDLE)

    # Implication band
    imp_y = Inches(6.20); imp_h = Inches(0.6)
    card(s, Inches(0.55), imp_y, Inches(12.2), imp_h)
    text(s, "IMPLICATION",
         Inches(0.80), imp_y + Inches(0.07), Inches(2), Inches(0.2),
         font=SANS, size=8, bold=True, color=KICKER)
    text(s, "The frame is institutional reassurance under scrutiny  —  "
            "not regulatory failure after mass death.",
         Inches(0.80), imp_y + Inches(0.25), Inches(11.7), Inches(0.3),
         font=SANS, size=13, bold=True, color=INK)

    footer(s, "Article frame from WSJ citation; source categories based on "
              "project outline and article analysis. "
              "Pasztor & Tangel had broken the MCAS self-certification story (Nov 13, 2018) — "
              "the framing here is structural, not authorial bias.")

    notes(s,
        outline=[
            "Read the article BEFORE you invoke the model.",
            "The FAA is positioned as fact-giver, not as the institution under scrutiny.",
            "Foreign regulators and victims are not absent from reality — they are absent as ORGANIZING authorities.",
            "Pasztor + Tangel had broken MCAS in November — the journalists are not the variable.",
        ],
        script=(
            "Before any theoretical move: read the article. The text itself has a "
            "center of gravity. The FAA is the organizing authority. Boeing speaks "
            "about its own aircraft. U.S. airlines speak operationally. Anonymous "
            "industry officials supply framing in the background. China’s "
            "grounding, EASA, U.S. politicians — secondary, reactive. The "
            "victims’ families, the Ethiopian and Indonesian regulators, the "
            "captured-regulator frame itself — absent as knowers. The frame "
            "is institutional reassurance under scrutiny, not regulatory failure "
            "after mass death. And remember: this WSJ team had broken the MCAS "
            "self-certification story four months earlier. The framing is "
            "structural, not authorial."
        ),
    )


def slide_5_filters_1_2(prs):
    s = chrome(prs, 5)
    kicker_title(s, "Filters 1 and 2",
                 "Ownership and advertising fit as conditions, not proof.",
                 sub="These filters explain viability: why a sustained anti-Boeing "
                     "campaign would be costly for a business paper.")

    # Two condition cards
    card_y = Inches(2.40); card_w = Inches(6.0); card_h = Inches(1.75)
    card(s, Inches(0.55), card_y, card_w, card_h)
    card(s, Inches(6.80), card_y, card_w, card_h)
    text(s, "FILTER 1: OWNERSHIP / CLASS",
         Inches(0.80), card_y + Inches(0.20), card_w, Inches(0.3),
         font=SANS, size=8, bold=True, color=KICKER)
    text(s, "WSJ is corporate-financial America’s paper of record. "
            "Boeing is corporate America: Dow component, largest exporter, "
            "Pentagon prime, anchor employer for WA + SC.",
         Inches(0.80), card_y + Inches(0.55), card_w - Inches(0.4), Inches(1.15),
         font=SANS, size=13, bold=True, color=INK, line_spacing=1.30)

    text(s, "FILTER 2: READER-AD ECOLOGY",
         Inches(7.05), card_y + Inches(0.20), card_w, Inches(0.3),
         font=SANS, size=8, bold=True, color=ORANGE)
    text(s, "Aerospace, airlines, finance, law, and consulting form the same "
            "commercial world the WSJ serves — and WSJ readers hold "
            "Boeing in their portfolios.",
         Inches(7.05), card_y + Inches(0.55), card_w - Inches(0.4), Inches(1.15),
         font=SANS, size=13, bold=True, color=INK, line_spacing=1.30)

    # NOT-claim / CAN-claim pedagogy (v3's best slide-level move)
    ped_y = Inches(4.55); ped_w = Inches(6.0); ped_h = Inches(2.0)
    card(s, Inches(0.55), ped_y, ped_w, ped_h, fill=RED_BG, border=RED, border_w=Pt(1.0))
    text(s, "✕  WHAT THIS SLIDE DOES NOT CLAIM",
         Inches(0.80), ped_y + Inches(0.18), ped_w, Inches(0.3),
         font=SANS, size=9, bold=True, color=RED)
    text(s, "Murdoch called the newsroom.\n"
            "Boeing bought the headline.\n"
            "Advertisers killed the story.",
         Inches(0.80), ped_y + Inches(0.52), ped_w - Inches(0.4), Inches(1.4),
         font=SANS, size=15, bold=True, color=RED, line_spacing=1.40,
         strike=True)

    card(s, Inches(6.80), ped_y, ped_w, ped_h, fill=GREEN_BG, border=GREEN, border_w=Pt(1.0))
    text(s, "✓  WHAT IT CAN CLAIM",
         Inches(7.05), ped_y + Inches(0.18), ped_w, Inches(0.3),
         font=SANS, size=9, bold=True, color=GREEN)
    text(s, "A single critical article is tolerable. A sustained structural "
            "campaign against Boeing is institutionally expensive.",
         Inches(7.05), ped_y + Inches(0.52), ped_w - Inches(0.4), Inches(1.4),
         font=SANS, size=15, bold=True, color=INK, line_spacing=1.40)

    quote_footer(s,
        "the dominant media firms … are closely interlocked … "
        "with other major corporations, banks, and government.",
        "— Herman & Chomsky, p. 14")

    footer(s, "Use as structural context; avoid unsupported claims about direct "
              "advertiser or owner intervention.")

    notes(s,
        outline=[
            "Filters 1 + 2 explain viability, not proof.",
            "WSJ is corporate-financial America; Boeing is corporate America.",
            "Be precise about what these filters DON'T license you to claim.",
            "What they DO license: a sustained campaign is institutionally expensive.",
        ],
        script=(
            "Filters 1 and 2 are background conditions, not direct evidence. The "
            "WSJ is corporate-financial America’s paper of record. It is "
            "owned by News Corp. It calculates the Dow Jones Industrial Average, "
            "which includes Boeing. Boeing is corporate America. Same class, same "
            "interlocks. The advertiser ecology — aerospace, airlines, "
            "finance, law, consulting — is the same commercial world the WSJ "
            "serves. Be careful about what this licenses you to claim. It does "
            "NOT support the claim that Murdoch called the newsroom or Boeing "
            "bought the headline. What it DOES support is the structural point "
            "that a single critical article is tolerable, but a sustained "
            "structural campaign against Boeing is institutionally expensive. "
            "These filters explain why the stronger filters can operate."
        ),
    )


def slide_6_sourcing(prs):
    s = chrome(prs, 6)
    kicker_title(s, "Filter 3",
                 "Sourcing is where the model becomes visible.",
                 sub="The cheap, official, recurring sources determine what the "
                     "story can easily become.")

    # Center oval — "FAA as authorized knower"
    cx = SLIDE_W / 2; cy = Inches(3.85)
    ov_w = Inches(4.0); ov_h = Inches(1.4)
    ov = s.shapes.add_shape(MSO_SHAPE.OVAL,
                            cx - ov_w / 2, cy - ov_h / 2, ov_w, ov_h)
    ov.fill.solid(); ov.fill.fore_color.rgb = CARD_2
    ov.line.color.rgb = RAIL; ov.line.width = Pt(1.25)
    text(s, "FAA as authorized knower",
         cx - ov_w / 2, cy - ov_h / 2, ov_w, ov_h,
         font=SANS, size=15, bold=True, color=RAIL,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    # Left flanks (feeding voices)
    lefts = [("Boeing", Inches(2.80)), ("U.S. airlines", Inches(4.50))]
    for label, y in lefts:
        card(s, Inches(0.55), y, Inches(2.6), Inches(0.55))
        text(s, label,
             Inches(0.55), y, Inches(2.6), Inches(0.55),
             font=SANS, size=12, bold=True, color=RAIL,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        # Arrow toward the oval
        a = s.shapes.add_connector(1, Inches(3.15), y + Inches(0.28),
                                   cx - ov_w/2, cy)
        a.line.color.rgb = SLATE; a.line.width = Pt(1.0)

    rights = [("Industry officials", Inches(2.80)),
              ("Official notices",  Inches(4.50))]
    for label, y in rights:
        card(s, Inches(10.20), y, Inches(2.6), Inches(0.55))
        text(s, label,
             Inches(10.20), y, Inches(2.6), Inches(0.55),
             font=SANS, size=12, bold=True, color=RAIL,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        a = s.shapes.add_connector(1, Inches(10.20), y + Inches(0.28),
                                   cx + ov_w/2, cy)
        a.line.color.rgb = SLATE; a.line.width = Pt(1.0)

    # Bottom two contrast / implication cards
    bot_y = Inches(5.55); bot_w = Inches(6.0); bot_h = Inches(1.05)
    card(s, Inches(0.55), bot_y, bot_w, bot_h)
    text(s, "CONTRAST OBJECT",
         Inches(0.80), bot_y + Inches(0.13), bot_w, Inches(0.25),
         font=SANS, size=8, bold=True, color=RED)
    text(s, "Six days later, Dominic Gates (Seattle Times) reframed FAA "
            "as a delegated, compromised regulator.  Won the 2020 Pulitzer.",
         Inches(0.80), bot_y + Inches(0.38), bot_w - Inches(0.4), Inches(0.65),
         font=SANS, size=12, bold=True, color=INK, line_spacing=1.30)

    card(s, Inches(6.80), bot_y, bot_w, bot_h)
    text(s, "WHY IT MATTERS",
         Inches(7.05), bot_y + Inches(0.13), bot_w, Inches(0.25),
         font=SANS, size=8, bold=True, color=KICKER)
    text(s, "A frame that indicts the source relationship costs more "
            "than a frame that quotes it.",
         Inches(7.05), bot_y + Inches(0.38), bot_w - Inches(0.4), Inches(0.65),
         font=SANS, size=12, bold=True, color=INK, line_spacing=1.30)

    quote_footer(s,
        "Officials have and give the facts; reporters merely get them.",
        "— Mark Fishman, quoted in Manufacturing Consent, p. 19")

    footer(s, "Dominic Gates, Seattle Times, “Flawed analysis, failed "
              "oversight,” Mar 17, 2019 — same beat, different "
              "publication structure, captured-regulator framing in the lead.")

    notes(s,
        outline=[
            "This is the first load-bearing slide — article-level proof.",
            "Fishman in plain English: officials give facts, reporters get them.",
            "Source ARCHITECTURE: the FAA is the authorizer of what counts as fact.",
            "Gates is the same-beat contrast: the story was reportable.",
        ],
        script=(
            "Filter 3 — sourcing — is the first load-bearing slide and "
            "the one you can verify directly inside the article. The Fishman idea, "
            "which Chomsky uses on p. 19, is: officials have and give the facts, "
            "reporters merely get them. In this article, the FAA is treated as "
            "the institution that authorizes what counts as fact. Not as the "
            "institution under indictment. Six days later, Dominic Gates at the "
            "Seattle Times reframed the FAA as a delegated, compromised regulator "
            "— the captured-regulator framing — and won a Pulitzer for "
            "it. Same beat, different publication structure. The frame WSJ "
            "selected costs less. The frame Gates selected costs more. That cost "
            "asymmetry is filter 3."
        ),
    )


def slide_7_flak(prs):
    s = chrome(prs, 7)
    kicker_title(s, "Filter 4",
                 "Flak fits best as anticipated cost.",
                 sub="Do not argue Boeing threatened this article. Argue that "
                     "certain frames were predictably expensive.")

    # Three-step cost ladder (v3's strongest visual)
    ladder_x_base = Inches(0.55)
    ladder_y = Inches(2.40)
    rung_h = Inches(0.8)
    rung_w = Inches(11.0)
    rungs = [
        ("LOW COST",    "FAA decision under scrutiny",                           GREEN,  GREEN_BG,  Inches(0)),
        ("MEDIUM COST", "Boeing design choices under scrutiny",                  ORANGE, ORANGE_BG, Inches(0.65)),
        ("HIGH COST",   "FAA captured by Boeing; certification failed",          RED,    RED_BG,    Inches(1.30)),
    ]
    for i, (label, claim, accent, bg, indent) in enumerate(rungs):
        y = ladder_y + (rung_h + Inches(0.18)) * i
        card(s, ladder_x_base + indent, y, rung_w, rung_h,
             fill=bg, border=accent, border_w=Pt(1.0))
        text(s, label,
             ladder_x_base + indent + Inches(0.25),
             y + Inches(0.10), Inches(1.6), Inches(0.6),
             font=SANS, size=10, bold=True, color=accent,
             anchor=MSO_ANCHOR.MIDDLE)
        text(s, claim,
             ladder_x_base + indent + Inches(1.95),
             y, rung_w - Inches(2.20), rung_h,
             font=SANS, size=14, bold=True, color=INK,
             anchor=MSO_ANCHOR.MIDDLE)

    # Mechanism box — restored Patrick Shanahan
    mech_y = Inches(5.65); mech_w = Inches(12.2); mech_h = Inches(0.95)
    card(s, Inches(0.55), mech_y, mech_w, mech_h)
    text(s, "MECHANISM",
         Inches(0.80), mech_y + Inches(0.12), mech_w, Inches(0.25),
         font=SANS, size=8, bold=True, color=KICKER)
    text(s, "Access, PR response, legal complaint, editor pressure, and "
            "future sourcing all live in the reporter’s cost calculation. "
            "Acting Defense Secretary Patrick Shanahan was a 30-year Boeing executive.",
         Inches(0.80), mech_y + Inches(0.36), mech_w - Inches(0.4), mech_h - Inches(0.4),
         font=SANS, size=12, bold=True, color=INK, line_spacing=1.30)

    quote_footer(s,
        "If certain kinds of fact, position, or program are thought likely to "
        "elicit flak, this prospect can be a deterrent.",
        "— Herman & Chomsky, p. 26")

    footer(s, "Filter 4 is presented as indirect / partial fit; stronger later "
              "evidence appears in Frontline / NYT 'Boeing’s Fatal Flaw' "
              "(2021) and post-2019 reporting on Boeing pressure.")

    notes(s,
        outline=[
            "Frame this honestly: PARTIAL fit, anticipated cost.",
            "Three rungs: FAA under scrutiny (cheap) → Boeing design (medium) → captured-regulator (expensive).",
            "Mechanism: access, PR, legal, editor, future sourcing.",
            "Shanahan as concrete: Acting DefSec was a 30-year Boeing exec.",
        ],
        script=(
            "Filter 4 is partial fit — don’t overreach. Don’t "
            "argue Boeing threatened this specific article. Argue that certain "
            "frames were predictably expensive. There’s a cost ladder. The "
            "cheapest frame: the FAA’s decision is under scrutiny. The "
            "next cost up: Boeing’s design choices are under scrutiny. The "
            "expensive frame: the FAA was captured by Boeing, and certification "
            "failed. The mechanism that produces that cost is access, PR "
            "response, legal complaint, editor pressure, and the future sourcing "
            "relationship that the reporter depends on. As one concrete example: "
            "the Acting Defense Secretary at the time of these crashes, Patrick "
            "Shanahan, was a 30-year Boeing executive. The flak apparatus is "
            "anticipatory, not retaliatory."
        ),
    )


def slide_8_ideology(prs):
    s = chrome(prs, 8)
    kicker_title(s, "Filter 5",
                 "The fifth filter is the analytical upgrade.",
                 sub="The content changes from anticommunism to techno-industrial "
                     "nationalism; the function stays the same.")

    # Left: era ladder
    eras = [("1988", "Anticommunism", INK),
            ("2002", "Religion of the market", INK),
            ("2019", "Techno-industrial nationalism", RED)]
    era_y = Inches(2.45)
    for i, (year, label, color) in enumerate(eras):
        y = era_y + Inches(0.85) * i
        text(s, year,
             Inches(0.55), y, Inches(1.0), Inches(0.3),
             font=SANS, size=11, bold=True, color=SLATE)
        text(s, label,
             Inches(0.55), y + Inches(0.27), Inches(6.0), Inches(0.55),
             font=SANS, size=22, bold=True, color=color)

    # Right top: worthy / unworthy strip (RESTORED from v2)
    rt_y = Inches(2.40); rt_w = Inches(5.4); rt_h = Inches(0.55)
    card(s, Inches(7.40), rt_y, rt_w, rt_h, fill=CARD_2, border=KICKER)
    text(s, "WORTHY  /  UNWORTHY  VICTIMS — CHOMSKY’S CANONICAL TEST",
         Inches(7.40), rt_y, rt_w, rt_h,
         font=SANS, size=9, bold=True, color=KICKER,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    pairs = [
        ("KAL 007 (1983)", "Lion Air + Ethiopian (2018-19)"),
        ("Sustained moral outrage", "“Pilot training” framing"),
        ("Reagan: “cold-blooded murder”", "132 days before grounding"),
    ]
    for i, (l, r) in enumerate(pairs):
        y = rt_y + rt_h + Inches(0.08) + Inches(0.50) * i
        card(s, Inches(7.40), y, Inches(2.65), Inches(0.45),
             fill=CARD, border=BORDER)
        card(s, Inches(10.10), y, Inches(2.70), Inches(0.45),
             fill=RED_BG, border=BORDER)
        text(s, l, Inches(7.55), y, Inches(2.5), Inches(0.45),
             font=SANS, size=10, color=INK, anchor=MSO_ANCHOR.MIDDLE)
        text(s, r, Inches(10.25), y, Inches(2.5), Inches(0.45),
             font=SANS, size=10, color=RED, anchor=MSO_ANCHOR.MIDDLE)

    # Right bottom: frame effect
    fe_y = Inches(5.65); fe_w = Inches(5.4); fe_h = Inches(0.95)
    card(s, Inches(7.40), fe_y, fe_w, fe_h)
    text(s, "FRAME EFFECT",
         Inches(7.60), fe_y + Inches(0.12), fe_w, Inches(0.25),
         font=SANS, size=8, bold=True, color=KICKER)
    text(s, "FAA reads as default authority. Foreign regulators read as "
            "pressure, reaction, or politics.",
         Inches(7.60), fe_y + Inches(0.34), fe_w - Inches(0.4), fe_h - Inches(0.4),
         font=SANS, size=12, bold=True, color=INK, line_spacing=1.30)

    # Left bottom: how-it-works callout
    hw_y = Inches(5.65); hw_w = Inches(6.45); hw_h = Inches(0.95)
    card(s, Inches(0.55), hw_y, hw_w, hw_h)
    text(s, "HOW IT WORKS HERE",
         Inches(0.80), hw_y + Inches(0.12), hw_w, Inches(0.25),
         font=SANS, size=8, bold=True, color=RED)
    text(s, "Boeing stands in for U.S. aviation, manufacturing, exports, "
            "defense, jobs, and national prestige.",
         Inches(0.80), hw_y + Inches(0.34), hw_w - Inches(0.4), hw_h - Inches(0.4),
         font=SANS, size=12, bold=True, color=INK, line_spacing=1.30)

    quote_footer(s,
        "Concentrate on the victims of enemy powers and forget about the "
        "victims of friends.",
        "— Herman & Chomsky, p. 32  (paraphrasing the structural function)")

    footer(s, "Herman & Chomsky on filter 5; Boeing status from House report "
              "and public record.")

    notes(s,
        outline=[
            "Second load-bearing slide; the paper’s original analytical contribution.",
            "Content rotates: anticommunism → religion of market → techno-industrial nationalism.",
            "FUNCTION is identical: worthy / unworthy victims, organized by friendship.",
            "KAL 007 (1983) is Chomsky’s canonical case; Lion Air + Ethiopian fit the unworthy column.",
        ],
        script=(
            "Filter 5 is the paper’s original analytical contribution. "
            "Chomsky’s 1988 filter 5 was anticommunism. In 2002 he updated "
            "it to the religion of the market. For 2019 aviation, I argue the "
            "operative content is techno-industrial nationalism — Boeing "
            "stands in for U.S. aviation, manufacturing, exports, defense, jobs, "
            "national prestige. The content has rotated. The function is "
            "identical. In 1983, the Soviets shot down KAL 007. Sustained moral "
            "outrage. Years of front-page coverage. Reagan: ‘cold-blooded "
            "murder.’ In 2018-19, an American aircraft killed 346 civilians "
            "— Indonesians, Indians, Ethiopians, Kenyans, Chinese. Initial "
            "framing: pilot training. 132 days before grounding. Different "
            "ideology. Identical filter."
        ),
    )


def slide_9_counterfactual(prs):
    s = chrome(prs, 9)
    kicker_title(s, "The victim test",
                 "Same facts, different victims, different output.",
                 sub="This counterfactual tests the model without needing to "
                     "prove author intent.")

    # Two newsprint cards side by side
    card_y = Inches(2.55); card_h = Inches(3.25)
    lw = Inches(6.0); rw = Inches(6.0); gap = Inches(0.20)
    left_x = Inches(0.55); right_x = left_x + lw + gap

    card(s, left_x, card_y, lw, card_h)
    text(s, "ACTUAL FRAME",
         left_x + Inches(0.30), card_y + Inches(0.20), lw, Inches(0.3),
         font=SANS, size=10, bold=True, color=KICKER)
    text(s, "FAA has no current plans to ground Boeing’s 737 MAX "
            "after deadly crash",
         left_x + Inches(0.30), card_y + Inches(0.60), lw - Inches(0.55), Inches(1.85),
         font=SERIF, size=22, bold=True, color=INK, line_spacing=1.20)
    text(s, "Authority first.  Victims unnamed.  Global alarm secondary.",
         left_x + Inches(0.30), card_y + card_h - Inches(0.55),
         lw - Inches(0.55), Inches(0.4),
         font=SANS, size=11, italic=True, color=SLATE)

    card(s, right_x, card_y, rw, card_h, fill=RED_BG, border=RED, border_w=Pt(1.0))
    text(s, "COUNTERFACTUAL FRAME",
         right_x + Inches(0.30), card_y + Inches(0.20), rw, Inches(0.3),
         font=SANS, size=10, bold=True, color=RED)
    text(s, "Pressure mounts on FAA to ground 737 MAX after second crash "
            "kills 157 Americans",
         right_x + Inches(0.30), card_y + Inches(0.60), rw - Inches(0.55), Inches(1.85),
         font=SERIF, size=22, bold=True, color=INK, line_spacing=1.20)
    text(s, "Victims first.  Outrage visible.  FAA under indictment.",
         right_x + Inches(0.30), card_y + card_h - Inches(0.55),
         rw - Inches(0.55), Inches(0.4),
         font=SANS, size=11, italic=True, color=RED)

    # Finding
    f_y = Inches(6.20); f_w = Inches(12.2); f_h = Inches(0.65)
    card(s, Inches(0.55), f_y, f_w, f_h)
    text(s, "FINDING",
         Inches(0.80), f_y + Inches(0.08), f_w, Inches(0.25),
         font=SANS, size=8, bold=True, color=RED)
    text(s, "The model fits if victim status changes the natural frame. "
            "That is the worthy/unworthy victim logic.",
         Inches(0.80), f_y + Inches(0.30), f_w - Inches(0.4), Inches(0.35),
         font=SANS, size=13, bold=True, color=INK)

    footer(s, "Counterfactual based on Chomsky’s worthy/unworthy victim "
              "distinction and the Boeing crash timeline.")

    notes(s,
        outline=[
            "Don’t make this melodramatic. Let the counterfactual carry it.",
            "Same aircraft, same facts, different victims.",
            "If the headline changes, the frame was not neutral; it was filtered.",
        ],
        script=(
            "Here is the test. Same facts. Different victims. Different output. "
            "If 346 Americans had died on two domestic flights of the same "
            "aircraft in five months, the Wall Street Journal headline on March "
            "11, 2019 would not have read ‘FAA Has No Current Plans to "
            "Ground.’ It would have read something like the right column. "
            "Victims first. Outrage visible. FAA under indictment. The model "
            "fits if victim status changes what the natural frame is. That is "
            "the worthy / unworthy victim logic operating in 2019."
        ),
    )


def slide_10_verdict(prs):
    s = chrome(prs, 10)
    kicker_title(s, "Final finding",
                 "The model applies substantially, but unevenly.",
                 sub="That unevenness makes the argument stronger: it separates "
                     "proof from context.")

    # Verdict matrix
    rows = [
        ("Filters 1 + 2", "MODERATE FIT", "Structural background: class and commercial ecology",   SLATE),
        ("Filter 3",      "STRONG FIT",   "Article-level proof: source architecture makes FAA authoritative", KICKER),
        ("Filter 4",      "PARTIAL FIT",  "Anticipated cost: expensive frames discipline the beat", ORANGE),
        ("Filter 5",      "STRONG FIT",   "Ideological proof: foreign victims remain morally peripheral to the frame", KICKER),
    ]
    m_x = Inches(0.55); m_w = Inches(12.2)
    m_y = Inches(2.50); row_h = Inches(0.65); gap = Inches(0.10)
    for i, (label, verdict, claim, vcolor) in enumerate(rows):
        y = m_y + (row_h + gap) * i
        card(s, m_x, y, m_w, row_h, fill=CARD if i % 2 == 0 else CARD_2)
        text(s, label,
             m_x + Inches(0.30), y, Inches(2.0), row_h,
             font=SANS, size=13, bold=True, color=INK,
             anchor=MSO_ANCHOR.MIDDLE)
        text(s, verdict,
             m_x + Inches(2.30), y, Inches(2.2), row_h,
             font=SANS, size=12, bold=True, color=vcolor,
             anchor=MSO_ANCHOR.MIDDLE)
        text(s, claim,
             m_x + Inches(4.60), y, m_w - Inches(4.85), row_h,
             font=SANS, size=12, color=INK,
             anchor=MSO_ANCHOR.MIDDLE)

    # Closing two-line landing — fixed line break
    rich(s, [
        [("The article is not propaganda-model evidence because it lies.",
          {"font": SANS, "size": 18, "bold": True, "color": INK})],
        [("It is propaganda-model evidence because normal journalism "
          "selected the institutionally comfortable frame.",
          {"font": SANS, "size": 18, "bold": True, "color": RED})],
    ], Inches(0.55), Inches(5.85), Inches(12.2), Inches(1.05),
       align=PP_ALIGN.LEFT, line_spacing=1.30)

    footer(s, "Close line: the filters did not fabricate the news; "
              "they selected the version fit to print.")

    notes(s,
        outline=[
            "End cleanly — verdict, not recap.",
            "Match each filter to a degree of fit you can defend in Q&A.",
            "Land the close: selection, not fabrication.",
        ],
        script=(
            "Final finding. The propaganda model applies substantially, but "
            "unevenly. Filters 1 and 2 — moderate fit — structural "
            "background. Filter 3 — strong fit — article-level "
            "proof in the source architecture. Filter 4 — partial fit "
            "— the anticipated cost of expensive frames. Filter 5 "
            "— strong fit — ideological proof in the moral framing of "
            "foreign victims. The article is not propaganda-model evidence "
            "because it lies. It is propaganda-model evidence because normal "
            "journalism selected the institutionally comfortable frame. The "
            "filters did not fabricate the news. They selected the version "
            "fit to print."
        ),
    )


# ---------------- driver ----------------

def main():
    prs = make_prs()
    slide_1_puzzle(prs)
    slide_2_structural_facts(prs)
    slide_3_model(prs)
    slide_4_frame(prs)
    slide_5_filters_1_2(prs)
    slide_6_sourcing(prs)
    slide_7_flak(prs)
    slide_8_ideology(prs)
    slide_9_counterfactual(prs)
    slide_10_verdict(prs)
    prs.save(OUT)
    print(f"wrote {OUT.name} ({OUT.stat().st_size:,} bytes, {len(prs.slides)} slides)")


if __name__ == "__main__":
    main()
