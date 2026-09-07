from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parent
SCREENSHOTS = ROOT / "screenshots"
OUTPUT = ROOT / "deliverables" / "OpsPilot_AI_War_Room.pptx"

NAVY = RGBColor(11, 18, 31)
PANEL = RGBColor(23, 34, 53)
PANEL_2 = RGBColor(29, 45, 70)
WHITE = RGBColor(242, 247, 252)
MUTED = RGBColor(166, 185, 204)
CYAN = RGBColor(74, 190, 232)
GREEN = RGBColor(42, 211, 157)
AMBER = RGBColor(246, 190, 64)
RED = RGBColor(238, 107, 107)
BLUE = RGBColor(65, 128, 236)
FONT = "Aptos"
MONO = "Aptos Mono"

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank = prs.slide_layouts[6]


def set_bg(slide, color=NAVY):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_rect(slide, x, y, w, h, fill, radius=False, line=None, transparency=0):
    kind = MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE if radius else MSO_AUTO_SHAPE_TYPE.RECTANGLE
    shape = slide.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.fill.transparency = transparency
    shape.line.color.rgb = line or fill
    shape.line.transparency = 0 if line else 100
    return shape


def add_text(slide, text, x, y, w, h, size=18, color=WHITE, bold=False, font=FONT,
             align=PP_ALIGN.LEFT, valign=MSO_ANCHOR.TOP, margin=0.04, italic=False):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = Inches(margin)
    tf.margin_right = Inches(margin)
    tf.margin_top = Inches(margin)
    tf.margin_bottom = Inches(margin)
    tf.vertical_anchor = valign
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    return box


def add_rich_text(slide, runs, x, y, w, h, size=16, color=WHITE, font=FONT, margin=0.06):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = Inches(margin)
    tf.margin_right = Inches(margin)
    tf.margin_top = Inches(margin)
    tf.margin_bottom = Inches(margin)
    for index, item in enumerate(runs):
        p = tf.paragraphs[0] if index == 0 else tf.add_paragraph()
        p.space_after = Pt(5)
        if isinstance(item, str):
            item = (item, False, color)
        text, is_bold, run_color = item
        run = p.add_run()
        run.text = text
        run.font.name = font
        run.font.size = Pt(size)
        run.font.bold = is_bold
        run.font.color.rgb = run_color
    return box


def add_title(slide, kicker, title, subtitle=None, number=None):
    add_text(slide, kicker.upper(), 0.65, 0.35, 3.2, 0.28, 10, CYAN, True)
    add_text(slide, title, 0.65, 0.70, 11.8, 0.55, 27, WHITE, True)
    if subtitle:
        add_text(slide, subtitle, 0.68, 1.30, 11.6, 0.35, 12, MUTED)
    add_rect(slide, 0.65, 1.78, 12.0, 0.015, CYAN)
    if number is not None:
        add_text(slide, f"{number:02d}", 12.0, 0.38, 0.65, 0.3, 11, MUTED, True, align=PP_ALIGN.RIGHT)


def add_footer(slide, source="OpsPilot | Neuro SAN Studio"):
    add_text(slide, source, 0.68, 7.14, 7.0, 0.18, 8, MUTED)
    add_text(slide, "AI Incident War Room", 10.0, 7.14, 2.65, 0.18, 8, MUTED, align=PP_ALIGN.RIGHT)


def add_bullet_list(slide, items, x, y, w, h, size=17, color=WHITE, bullet_color=GREEN, gap=0.47):
    for index, item in enumerate(items):
        yy = y + index * gap
        add_text(slide, "•", x, yy, 0.25, 0.28, size, bullet_color, True)
        add_text(slide, item, x + 0.30, yy - 0.01, w - 0.30, 0.38, size, color)


def add_image_cover(slide, path, x, y, w, h, border=CYAN):
    from PIL import Image
    image = Image.open(path)
    image_ratio = image.width / image.height
    box_ratio = w / h
    pic = slide.shapes.add_picture(str(path), Inches(x), Inches(y), width=Inches(w), height=Inches(h))
    if image_ratio > box_ratio:
        visible = box_ratio / image_ratio
        pic.crop_left = pic.crop_right = (1 - visible) / 2
    else:
        visible = image_ratio / box_ratio
        pic.crop_top = pic.crop_bottom = (1 - visible) / 2
    if border:
        frame = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
        frame.fill.background()
        frame.line.color.rgb = border
        frame.line.width = Pt(1.2)
    return pic


def add_card(slide, x, y, w, h, title, body, accent=CYAN, body_size=14):
    add_rect(slide, x, y, w, h, PANEL, True, line=PANEL_2)
    add_rect(slide, x, y, 0.08, h, accent)
    add_text(slide, title, x + 0.22, y + 0.16, w - 0.4, 0.28, 14, WHITE, True)
    add_text(slide, body, x + 0.22, y + 0.54, w - 0.38, h - 0.67, body_size, MUTED)


def add_node(slide, label, x, y, w=1.65, h=0.56, fill=BLUE, text_color=WHITE):
    add_rect(slide, x, y, w, h, fill, True, line=CYAN)
    add_text(slide, label, x + 0.06, y + 0.16, w - 0.12, 0.22, 12, text_color, True, align=PP_ALIGN.CENTER)


def add_arrow(slide, x1, y1, x2, y2, color=MUTED, width=1.5):
    line = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    line.line.color.rgb = color
    line.line.width = Pt(width)
    line.line.end_arrowhead = True


# 1. Cover
slide = prs.slides.add_slide(blank)
set_bg(slide)
add_rect(slide, 0, 0, 13.333, 0.16, CYAN)
add_text(slide, "OPSPILOT", 0.72, 0.75, 3.0, 0.35, 14, CYAN, True)
add_text(slide, "AI Incident\nWar Room", 0.68, 1.35, 5.4, 1.55, 40, WHITE, True)
add_text(slide, "Grounded multi-agent investigation for faster, safer operational response", 0.72, 3.25, 5.0, 0.7, 19, MUTED)
add_rect(slide, 0.72, 4.25, 2.0, 0.04, GREEN)
add_text(slide, "A Neuro SAN Studio project", 0.72, 4.55, 4.6, 0.35, 14, WHITE, True)
add_text(slide, "Synthetic incidents, local logs, runbooks, and an evidence-bounded response path", 0.72, 5.0, 5.3, 0.55, 13, MUTED)
add_image_cover(slide, SCREENSHOTS / "01_agent_registry.png", 6.18, 0.85, 6.45, 5.75, border=BLUE)
add_text(slide, "OpsPilot network view", 6.25, 6.72, 3.0, 0.25, 10, MUTED)
add_footer(slide)

# 2. Problem
slide = prs.slides.add_slide(blank)
set_bg(slide)
add_title(slide, "01 | Problem Statement", "Incident response is a correlation problem", "Critical context is spread across logs, runbooks, and human memory.", 1)
add_card(slide, 0.72, 2.20, 3.75, 2.20, "SEARCH", "Find the right log lines across noisy operational files and timelines.", CYAN, 15)
add_card(slide, 4.78, 2.20, 3.75, 2.20, "CORRELATE", "Connect symptoms to the right documented runbook and failure pattern.", AMBER, 15)
add_card(slide, 8.84, 2.20, 3.75, 2.20, "DECIDE", "Know whether the available evidence is sufficient to recommend next steps.", GREEN, 15)
add_text(slide, "The cost of a weak handoff", 0.72, 5.05, 3.3, 0.34, 15, WHITE, True)
add_bullet_list(slide, [
    "Triage slows down when evidence is gathered manually.",
    "Runbook guidance can be missed or applied out of context.",
    "Unsupported certainty is dangerous during an active incident.",
], 0.80, 5.55, 7.0, 1.4, 15)
add_rect(slide, 8.55, 5.02, 3.95, 1.38, PANEL_2, True, line=AMBER)
add_text(slide, "Design goal", 8.82, 5.22, 2.0, 0.28, 13, AMBER, True)
add_text(slide, "Make the investigation explainable, reviewable, and fail-closed when evidence is missing.", 8.82, 5.60, 3.25, 0.60, 14, WHITE)
add_footer(slide)

# 3. Solution
slide = prs.slides.add_slide(blank)
set_bg(slide)
add_title(slide, "02 | OpsPilot Solution", "A digital war room with a clear evidence boundary", "Specialists do one job each; the commander turns their outputs into an operational narrative.", 2)
add_rect(slide, 0.72, 2.10, 5.15, 4.55, PANEL, True, line=PANEL_2)
add_text(slide, "Four stages, one accountable response", 1.0, 2.42, 4.4, 0.35, 18, WHITE, True)
stages = [("01", "Observe", "Incident record + local log evidence", CYAN), ("02", "Understand", "Matching KB and documented cause", AMBER), ("03", "Prepare", "Traceable recovery and validation actions", GREEN), ("04", "Review", "Grounding check + stakeholder summary", BLUE)]
for i, (num, title, body, color) in enumerate(stages):
    yy = 3.05 + i * 0.78
    add_text(slide, num, 1.0, yy, 0.4, 0.25, 11, color, True)
    add_text(slide, title, 1.55, yy - 0.02, 1.35, 0.28, 15, WHITE, True)
    add_text(slide, body, 2.80, yy - 0.02, 2.65, 0.30, 13, MUTED)
    if i < 3:
        add_rect(slide, 1.18, yy + 0.38, 0.02, 0.37, PANEL_2)
add_text(slide, "The response is not just an answer.\nIt is a chain of evidence, guidance, review, and communication.", 1.0, 6.15, 4.35, 0.42, 13, CYAN, True)
add_image_cover(slide, SCREENSHOTS / "01_agent_registry.png", 6.25, 2.10, 6.35, 4.55, border=GREEN)
add_footer(slide, "Source: local OpsPilot fixtures and registry")

# 4. Architecture
slide = prs.slides.add_slide(blank)
set_bg(slide)
add_title(slide, "03 | Architecture", "From request to evidence-bounded response", "Validation is the gate; local coded tools are the evidence boundary.", 3)
add_text(slide, "USER REQUEST", 0.82, 2.18, 1.35, 0.25, 10, MUTED, True, align=PP_ALIGN.CENTER)
add_text(slide, "COORDINATION", 5.10, 2.18, 1.55, 0.25, 10, MUTED, True, align=PP_ALIGN.CENTER)
add_text(slide, "SPECIALISTS", 8.40, 2.18, 1.45, 0.25, 10, MUTED, True, align=PP_ALIGN.CENTER)
add_text(slide, "SOURCES", 11.18, 2.18, 1.1, 0.25, 10, MUTED, True, align=PP_ALIGN.CENTER)
add_node(slide, "Incident request", 0.72, 3.05, 1.7, 0.62, fill=PANEL_2)
add_node(slide, "IncidentCommander", 4.70, 3.05, 2.25, 0.62, fill=AMBER, text_color=NAVY)
add_node(slide, "LogInvestigator", 7.65, 2.48, 1.85, 0.56)
add_node(slide, "KnowledgeAgent", 7.65, 3.23, 1.85, 0.56)
add_node(slide, "ResolutionPlanner", 7.65, 3.98, 1.85, 0.56)
add_node(slide, "QualityReviewer", 7.65, 4.73, 1.85, 0.56)
add_node(slide, "ExecutiveReporter", 7.65, 5.48, 1.85, 0.56)
add_node(slide, "local logs", 10.65, 2.48, 1.55, 0.56, fill=PANEL_2)
add_node(slide, "Markdown KB", 10.65, 3.23, 1.55, 0.56, fill=PANEL_2)
add_node(slide, "reviewed plan", 10.65, 3.98, 1.55, 0.56, fill=PANEL_2)
add_node(slide, "summary", 10.65, 4.73, 1.55, 0.56, fill=PANEL_2)
add_node(slide, "exec summary", 10.65, 5.48, 1.55, 0.56, fill=PANEL_2)
add_arrow(slide, 2.42, 3.36, 4.65, 3.36, CYAN)
add_arrow(slide, 6.98, 3.36, 7.58, 2.78, MUTED)
add_arrow(slide, 6.98, 3.36, 7.58, 3.51, MUTED)
add_arrow(slide, 6.98, 3.36, 7.58, 4.26, MUTED)
add_arrow(slide, 6.98, 3.36, 7.58, 5.01, MUTED)
add_arrow(slide, 6.98, 3.36, 7.58, 5.76, MUTED)
add_arrow(slide, 9.55, 2.76, 10.58, 2.76, CYAN)
add_arrow(slide, 9.55, 3.51, 10.58, 3.51, AMBER)
add_arrow(slide, 9.55, 4.26, 10.58, 4.26, GREEN)
add_arrow(slide, 9.55, 5.01, 10.58, 5.01, BLUE)
add_arrow(slide, 9.55, 5.76, 10.58, 5.76, AMBER)
add_rect(slide, 0.72, 6.25, 11.48, 0.48, PANEL, True, line=GREEN)
add_text(slide, "Fail-closed rule: validate the incident before downstream investigation begins.", 1.0, 6.39, 10.9, 0.25, 14, GREEN, True, align=PP_ALIGN.CENTER)
add_footer(slide, "Architecture reflects the active basic/opspilot registry")

# 5. Agent network
slide = prs.slides.add_slide(blank)
set_bg(slide)
add_title(slide, "04 | Agent Network", "Six roles, one operating picture", "The active registry exposes the full network; each specialist has a bounded responsibility.", 4)
add_image_cover(slide, SCREENSHOTS / "01_agent_registry.png", 0.72, 2.10, 7.05, 4.55, border=BLUE)
roles = [
    ("IncidentCommander", "Coordinates validation, delegation, and the user-facing response.", AMBER),
    ("LogInvestigator", "Retrieves source-referenced operational evidence.", CYAN),
    ("KnowledgeAgent", "Finds documented runbooks and their key fields.", CYAN),
    ("ResolutionPlanner", "Structures recovery and validation actions.", GREEN),
    ("QualityReviewer", "Checks completeness and grounding.", BLUE),
    ("ExecutiveReporter", "Prepares the stakeholder summary.", AMBER),
]
for i, (title, body, accent) in enumerate(roles):
    yy = 2.18 + i * 0.73
    add_rect(slide, 8.10, yy, 4.48, 0.56, PANEL, True, line=PANEL_2)
    add_rect(slide, 8.10, yy, 0.07, 0.56, accent)
    add_text(slide, title, 8.32, yy + 0.09, 1.75, 0.20, 11, WHITE, True)
    add_text(slide, body, 10.05, yy + 0.09, 2.25, 0.28, 10, MUTED)
add_footer(slide, "Screenshot: active six-agent registry")

# 6. Coded tools
slide = prs.slides.add_slide(blank)
set_bg(slide)
add_title(slide, "05 | Coded Tools", "Deterministic tools make the investigation auditable", "The model synthesizes; local tools retrieve and structure bounded evidence.", 5)
for i, (name, role, sample, accent) in enumerate([
    ("incident_validator", "Gate the workflow", "Known incident?\nUnknown -> stop", GREEN),
    ("log_search", "Retrieve evidence", "Files + line references\nBounded matches", CYAN),
    ("kb_search", "Find knowledge", "Title + cause + steps\nParsed KB fields", AMBER),
    ("resolution_plan_builder", "Structure guidance", "Recovery + validation\nTrace to KB source", BLUE),
]):
    x = 0.72 + (i % 2) * 6.05
    y = 2.15 + (i // 2) * 1.65
    add_rect(slide, x, y, 5.55, 1.28, PANEL, True, line=PANEL_2)
    add_rect(slide, x, y, 0.10, 1.28, accent)
    add_text(slide, name, x + 0.28, y + 0.19, 4.8, 0.25, 17, WHITE, True, font=MONO)
    add_text(slide, role, x + 0.28, y + 0.58, 1.8, 0.25, 12, accent, True)
    add_text(slide, sample, x + 2.12, y + 0.56, 3.0, 0.43, 12, MUTED)
add_rect(slide, 0.72, 5.78, 11.60, 0.62, PANEL_2, True, line=GREEN)
add_text(slide, "Proof point", 1.0, 5.98, 1.15, 0.25, 13, GREEN, True)
add_text(slide, "Focused OpsPilot tests: 38 passed. Coverage includes retrieval, grounding, registry structure, validation, and KB-traceable plan construction.", 2.28, 5.93, 9.45, 0.34, 13, WHITE)
add_footer(slide, "Tools are local; complete workflow uses the configured LLM for synthesis")

# 7. Live demo
slide = prs.slides.add_slide(blank)
set_bg(slide)
add_title(slide, "06 | Live Demo Flow", "A three-query story that shows capability and restraint", "Start with a grounded investigation, then show direct retrieval and the no-match path.", 6)
steps = [("01", "Investigate INC008381005", "Full war-room flow", "Logs -> KB-1023 -> plan -> review -> summary", CYAN), ("02", "Retrieve runbook for INC008381110", "Intent-aware route", "KnowledgeAgent -> KB-1101", AMBER), ("03", "Investigate INC999999999", "Responsible no-match", "Validator -> Not Found -> further investigation", RED)]
for i, (num, query, label, route, accent) in enumerate(steps):
    x = 0.72 + i * 4.08
    add_rect(slide, x, 2.20, 3.70, 2.28, PANEL, True, line=PANEL_2)
    add_text(slide, num, x + 0.24, 2.44, 0.5, 0.27, 13, accent, True)
    add_text(slide, label, x + 0.92, 2.44, 2.45, 0.25, 11, accent, True)
    add_text(slide, query, x + 0.24, 2.98, 3.15, 0.52, 19, WHITE, True)
    add_text(slide, route, x + 0.24, 3.80, 3.1, 0.37, 12, MUTED)
add_image_cover(slide, SCREENSHOTS / "10_Focused OpsPilot Tests.png", 0.72, 4.88, 6.20, 1.80, border=BLUE)
add_image_cover(slide, SCREENSHOTS / "12_Responsible_AI.png", 7.18, 4.88, 5.42, 1.80, border=RED)
add_footer(slide, "Captured from a local OpsPilot run")

# 8. Responsible AI
slide = prs.slides.add_slide(blank)
set_bg(slide)
add_title(slide, "07 | Responsible AI & Grounding", "The system is designed to say 'not enough evidence'", "Guardrails protect the incident response process from plausible but unsupported conclusions.", 7)
add_image_cover(slide, SCREENSHOTS / "12_Responsible_AI.png", 0.72, 2.10, 5.55, 4.55, border=RED)
add_text(slide, "Grounding rules", 6.78, 2.16, 2.4, 0.30, 18, WHITE, True)
add_bullet_list(slide, [
    "Validate incident IDs against local source data first.",
    "Keep observed log evidence separate from KB recommendations.",
    "Treat recovery actions as plans for human review, not executed remediation.",
    "Never turn missing evidence into a cause, status, plan, or confidence claim.",
    "Unknown incidents return REQUIRES FURTHER INVESTIGATION.",
], 6.86, 2.72, 5.35, 2.65, 15, WHITE, RED, 0.63)
add_rect(slide, 6.80, 5.92, 5.40, 0.62, PANEL_2, True, line=RED)
add_text(slide, "INC999999999 -> Not Found -> no downstream investigation", 7.03, 6.12, 4.95, 0.24, 13, RED, True, align=PP_ALIGN.CENTER)
add_footer(slide, "Responsible-AI claims align with EVIDENCE_AUDIT.md")

# 9. Business impact
slide = prs.slides.add_slide(blank)
set_bg(slide)
add_title(slide, "08 | Business Impact", "Turn incident response into a repeatable operating capability", "OpsPilot improves the path from signal to decision without pretending the machine has authority it does not have.", 8)
metrics = [("FASTER", "Initial triage", "Reduce manual searching across logs and runbooks.", CYAN), ("CONSISTENT", "Runbook use", "Bring documented guidance into the same workflow every time.", GREEN), ("EXPLAINABLE", "Root-cause narrative", "Show how evidence supports the conclusion and the next action.", AMBER), ("SAFER", "Operational decisions", "Surface evidence gaps before unsupported recommendations spread.", RED)]
for i, (label, title, body, accent) in enumerate(metrics):
    x = 0.72 + (i % 2) * 6.05
    y = 2.15 + (i // 2) * 1.55
    add_rect(slide, x, y, 5.55, 1.18, PANEL, True, line=PANEL_2)
    add_text(slide, label, x + 0.26, y + 0.20, 1.15, 0.24, 11, accent, True)
    add_text(slide, title, x + 1.62, y + 0.18, 3.5, 0.25, 17, WHITE, True)
    add_text(slide, body, x + 1.62, y + 0.58, 3.55, 0.30, 12, MUTED)
add_rect(slide, 0.72, 5.60, 11.60, 0.78, PANEL_2, True, line=CYAN)
add_text(slide, "The outcome", 1.02, 5.84, 1.35, 0.25, 14, CYAN, True)
add_text(slide, "A faster first response, a clearer audit trail, and a disciplined handoff to human operators.", 2.50, 5.82, 9.10, 0.28, 16, WHITE, True)
add_text(slide, "Current scope: synthetic local data; no production remediation, incident-system updates, or recovery verification.", 0.72, 6.65, 11.60, 0.22, 10, MUTED, italic=True)
add_footer(slide)

# Remove any default blank paragraphs that could cause corruption in some viewers.
for slide in prs.slides:
    for shape in slide.shapes:
        if not hasattr(shape, "text_frame"):
            continue
        for paragraph in shape.text_frame.paragraphs:
            for run in paragraph.runs:
                run.font.name = run.font.name or FONT

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
prs.save(OUTPUT)
print(OUTPUT)
