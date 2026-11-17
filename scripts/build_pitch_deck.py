"""
Phase 9: Generate SkyGuard AI pitch deck (10-12 slides) for SIH26073.
Requires: pip install python-pptx
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
import os

# Color palette
NAVY = RGBColor(0x0D, 0x1B, 0x2A)
TEAL = RGBColor(0x17, 0xAB, 0xC0)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_GRAY = RGBColor(0xF0, 0xF4, 0xF8)
DARK_GRAY = RGBColor(0x33, 0x33, 0x33)
AMBER = RGBColor(0xFF, 0xAB, 0x00)

SLIDE_WIDTH = Inches(13.33)
SLIDE_HEIGHT = Inches(7.5)


def add_background(slide, color=NAVY):
    from pptx.util import Emu
    background = slide.shapes.add_shape(
        1,  # MSO_SHAPE_TYPE.RECTANGLE
        0, 0, SLIDE_WIDTH, SLIDE_HEIGHT
    )
    background.fill.solid()
    background.fill.fore_color.rgb = color
    background.line.fill.background()


def add_text_box(slide, text, left, top, width, height, font_size=18, bold=False, color=WHITE, align=PP_ALIGN.LEFT, italic=False):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    return txBox


def add_title_accent_bar(slide):
    bar = slide.shapes.add_shape(1, 0, Inches(7.1), SLIDE_WIDTH, Inches(0.08))
    bar.fill.solid()
    bar.fill.fore_color.rgb = TEAL
    bar.line.fill.background()


def slide_1_title(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide, NAVY)
    add_title_accent_bar(slide)
    add_text_box(slide, "SkyGuard AI", Inches(1), Inches(1.5), Inches(11), Inches(1.2), font_size=54, bold=True, color=TEAL, align=PP_ALIGN.CENTER)
    add_text_box(slide, "AI/ML-Based Intelligent Anomaly Detection for Automatic Weather Stations", Inches(1), Inches(2.9), Inches(11), Inches(0.9), font_size=22, bold=False, color=WHITE, align=PP_ALIGN.CENTER)
    add_text_box(slide, "SIH26073 | Ministry of Earth Sciences, Government of India", Inches(1), Inches(3.9), Inches(11), Inches(0.6), font_size=16, bold=False, color=TEAL, align=PP_ALIGN.CENTER)
    add_text_box(slide, "Team SkyGuard | Smart India Hackathon 2026", Inches(1), Inches(5.5), Inches(11), Inches(0.5), font_size=14, italic=True, color=LIGHT_GRAY, align=PP_ALIGN.CENTER)


def slide_2_problem(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide, NAVY)
    add_text_box(slide, "THE PROBLEM", Inches(0.5), Inches(0.3), Inches(12), Inches(0.6), font_size=11, bold=True, color=TEAL)
    add_text_box(slide, "India's Weather Stations Cannot Tell Sensor Failure from Disaster", Inches(0.5), Inches(0.9), Inches(12), Inches(1.0), font_size=28, bold=True, color=WHITE)
    bullets = [
        "🌡️  1,000+ IMD Automatic Weather Stations transmit sensor readings every 10 minutes",
        "⚠️  Faulty sensors routinely report impossible values (55°C spikes, -99 hPa dropouts)",
        "🚨  Meteorologists cannot distinguish hardware faults from genuine extreme weather events",
        "🔴  False alarms waste emergency resources; missed events endanger lives",
        "📡  No existing system provides real-time, spatially-aware, explainable anomaly classification",
    ]
    for i, b in enumerate(bullets):
        add_text_box(slide, b, Inches(0.7), Inches(2.1) + Inches(i * 0.9), Inches(11.5), Inches(0.8), font_size=17, color=WHITE if i % 2 == 0 else LIGHT_GRAY)


def slide_3_solution(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide, NAVY)
    add_text_box(slide, "OUR SOLUTION", Inches(0.5), Inches(0.3), Inches(12), Inches(0.6), font_size=11, bold=True, color=TEAL)
    add_text_box(slide, "SkyGuard AI — The 3-Layer Intelligence Stack", Inches(0.5), Inches(0.9), Inches(12), Inches(1.0), font_size=28, bold=True, color=WHITE)
    layers = [
        ("Layer 1: Instant Statistical Gate", "Z-score + IQR detection in < 1 ms. Scores every reading before it hits the database."),
        ("Layer 2: Hybrid ML Ensemble", "Isolation Forest + PyTorch LSTM Autoencoder — trained on synthetic AWS sensor patterns, ensemble-weighted for maximum event recall."),
        ("Layer 3: Haversine Spatial Corroboration", "Automatically cross-validates any extreme reading against geographically nearest stations. 55°C with zero neighbor agreement = SENSOR_FAULT. With agreement = GENUINE_EXTREME."),
    ]
    for i, (title, body) in enumerate(layers):
        add_text_box(slide, title, Inches(0.7), Inches(2.0) + Inches(i * 1.6), Inches(11), Inches(0.5), font_size=17, bold=True, color=TEAL)
        add_text_box(slide, body, Inches(0.9), Inches(2.5) + Inches(i * 1.6), Inches(11), Inches(0.9), font_size=15, color=LIGHT_GRAY)


def slide_4_architecture(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide, NAVY)
    add_text_box(slide, "ARCHITECTURE", Inches(0.5), Inches(0.3), Inches(12), Inches(0.6), font_size=11, bold=True, color=TEAL)
    add_text_box(slide, "Intentional Microservice Separation", Inches(0.5), Inches(0.9), Inches(12), Inches(0.8), font_size=28, bold=True, color=WHITE)
    boxes = [
        (Inches(0.4), "AWS / ESP32\nEdge Sensor", TEAL),
        (Inches(3.3), "Node.js Fastify\nBackend :3000\n(Orchestrator)", RGBColor(0x20, 0x60, 0x90)),
        (Inches(6.2), "Python FastAPI\nML Service :8000\n(Inference Engine)", RGBColor(0x20, 0x80, 0x60)),
        (Inches(9.1), "React / Vite\nDashboard :5173\n(Ops UI)", RGBColor(0x60, 0x40, 0x90)),
    ]
    for x, label, color in boxes:
        box = slide.shapes.add_shape(1, x, Inches(2.2), Inches(2.6), Inches(1.5))
        box.fill.solid()
        box.fill.fore_color.rgb = color
        box.line.color.rgb = WHITE
        tf = box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        run = p.add_run()
        run.text = label
        run.font.size = Pt(13)
        run.font.bold = True
        run.font.color.rgb = WHITE
    add_text_box(slide, "→ HTTP Ingest → REST /predict → WebSocket Stream →", Inches(0.4), Inches(4.1), Inches(12), Inches(0.5), font_size=14, color=TEAL, align=PP_ALIGN.CENTER)
    add_text_box(slide, "TimescaleDB / SQLite persists every reading — backend NEVER drops data, even when ML service is offline", Inches(0.5), Inches(5.0), Inches(12), Inches(0.6), font_size=14, italic=True, color=LIGHT_GRAY, align=PP_ALIGN.CENTER)


def slide_5_hybrid_detection(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide, NAVY)
    add_text_box(slide, "HYBRID DETECTION", Inches(0.5), Inches(0.3), Inches(12), Inches(0.6), font_size=11, bold=True, color=TEAL)
    add_text_box(slide, "Four Models, One Consensus Decision", Inches(0.5), Inches(0.9), Inches(12), Inches(0.8), font_size=28, bold=True, color=WHITE)
    models = [
        ("Statistical (Z+IQR)", "< 1 ms", "High precision, low recall on dense anomalies"),
        ("Isolation Forest", "< 5 ms", "Unsupervised; detects multivariate outlier clusters"),
        ("LSTM Autoencoder", "~20 ms", "Temporal sequence model; catches drift and stuck sensors"),
        ("Hybrid Ensemble", "< 30 ms", "Weighted consensus — best of all three; F1 0.65 at 1% fault rate"),
    ]
    headers = ["Model", "Latency", "Strength"]
    col_widths = [Inches(3.5), Inches(2), Inches(5.5)]
    col_lefts = [Inches(0.5), Inches(4.0), Inches(6.1)]
    for c, h in enumerate(headers):
        add_text_box(slide, h, col_lefts[c], Inches(2.0), col_widths[c], Inches(0.4), font_size=14, bold=True, color=TEAL)
    for r, (model, latency, strength) in enumerate(models):
        vals = [model, latency, strength]
        row_color = WHITE if r % 2 == 0 else LIGHT_GRAY
        for c in range(3):
            add_text_box(slide, vals[c], col_lefts[c], Inches(2.5) + Inches(r * 0.8), col_widths[c], Inches(0.7), font_size=14, color=row_color)


def slide_6_spatial(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide, NAVY)
    add_text_box(slide, "SPATIAL VALIDATION", Inches(0.5), Inches(0.3), Inches(12), Inches(0.6), font_size=11, bold=True, color=TEAL)
    add_text_box(slide, "Haversine Geospatial Corroboration", Inches(0.5), Inches(0.9), Inches(12), Inches(0.8), font_size=28, bold=True, color=WHITE)
    add_text_box(slide, "The core innovation: every statistical anomaly is cross-validated against geographically nearest AWS stations using the Haversine formula.", Inches(0.5), Inches(2.0), Inches(12), Inches(0.8), font_size=17, color=LIGHT_GRAY)
    cases = [
        ("SENSOR_FAULT", AMBER, "AWS001 reports 55°C\nNoida (12 km): 29°C  |  Gurgaon (15 km): 30°C\n→ No spatial agreement → SENSOR_FAULT\n→ Self-healed correction: 27.9°C"),
        ("GENUINE_EXTREME", TEAL, "AWS004 reports 48°C\nNearby stations also 45–49°C\n→ Spatial agreement → GENUINE_EXTREME\n→ Heatwave alert issued"),
    ]
    for i, (label, color, text) in enumerate(cases):
        box = slide.shapes.add_shape(1, Inches(0.5) + Inches(i * 6.4), Inches(3.1), Inches(5.9), Inches(3.5))
        box.fill.solid()
        box.fill.fore_color.rgb = RGBColor(0x0F, 0x28, 0x40)
        box.line.color.rgb = color
        box.line.width = Emu(20000)
        tf = box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        run = p.add_run()
        run.text = label
        run.font.size = Pt(16)
        run.font.bold = True
        run.font.color.rgb = color
        p2 = tf.add_paragraph()
        r2 = p2.add_run()
        r2.text = "\n" + text
        r2.font.size = Pt(14)
        r2.font.color.rgb = WHITE


def slide_7_explainability(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide, NAVY)
    add_text_box(slide, "EXPLAINABILITY", Inches(0.5), Inches(0.3), Inches(12), Inches(0.6), font_size=11, bold=True, color=TEAL)
    add_text_box(slide, "Every Alert Explained in Plain English with SHAP", Inches(0.5), Inches(0.9), Inches(12), Inches(0.8), font_size=28, bold=True, color=WHITE)
    points = [
        "SHAP (SHapley Additive exPlanations) computes feature-level attribution for every anomaly decision",
        "Dashboard renders bar chart: temperature_z_score, pressure_z_score, humidity_z_score contributions",
        "Root cause classifier maps SHAP to plain-English label: SENSOR_FAULT, GENUINE_EXTREME, COMMS_DROPOUT, CALIBRATION_DRIFT",
        "Meteorologist sees: reason, confidence, triggering feature, neighbor readings, corrected estimate — all in one panel",
        "Full SHAP explanation completes in < 200 ms (measured in automated test suite)",
    ]
    for i, p in enumerate(points):
        add_text_box(slide, f"✓  {p}", Inches(0.7), Inches(2.1) + Inches(i * 0.95), Inches(11.5), Inches(0.8), font_size=16, color=WHITE if i % 2 == 0 else LIGHT_GRAY)


def slide_8_edge(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide, NAVY)
    add_text_box(slide, "EDGE DEPLOYMENT", Inches(0.5), Inches(0.3), Inches(12), Inches(0.6), font_size=11, bold=True, color=TEAL)
    add_text_box(slide, "ESP32 MicroPython Edge Screener", Inches(0.5), Inches(0.9), Inches(12), Inches(0.8), font_size=28, bold=True, color=WHITE)
    add_text_box(slide, "Standalone anomaly detector runs locally on the ESP32 microcontroller — no cloud connection required for initial spike screening.", Inches(0.5), Inches(2.0), Inches(12), Inches(0.7), font_size=16, color=LIGHT_GRAY)
    stats = [
        ("Detection Latency\n(PC Python 3.13)", "0.0007 ms\nper call", "Measured: 10,000 iterations\nNote: PC hardware, not ESP32"),
        ("Estimated ESP32\nMicroPython Latency", "~0.4–1.2 ms\n(estimated)", "Not hardware-measured;\nestimated from Python overhead"),
        ("Energy per Check\n(ESP32 @ 240 MHz)", "~0.11 mJ\n(estimated)", "Based on spec sheet\ncurrent draw"),
        ("Telemetry Reduction", "~85%\n(estimated)", "Only anomalous readings\ntransmitted to cloud"),
    ]
    for i, (label, value, note) in enumerate(stats):
        x = Inches(0.4) + Inches(i * 3.2)
        box = slide.shapes.add_shape(1, x, Inches(3.0), Inches(2.9), Inches(2.8))
        box.fill.solid()
        box.fill.fore_color.rgb = RGBColor(0x0F, 0x28, 0x40)
        box.line.color.rgb = TEAL
        tf = box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        r = p.add_run()
        r.text = label
        r.font.size = Pt(12)
        r.font.color.rgb = TEAL
        r.font.bold = True
        p2 = tf.add_paragraph()
        r2 = p2.add_run()
        r2.text = value
        r2.font.size = Pt(20)
        r2.font.bold = True
        r2.font.color.rgb = WHITE
        p3 = tf.add_paragraph()
        r3 = p3.add_run()
        r3.text = note
        r3.font.size = Pt(10)
        r3.font.color.rgb = LIGHT_GRAY
        r3.font.italic = True


def slide_9_results(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide, NAVY)
    add_text_box(slide, "RESULTS (VERIFIED — SYNTHETIC DATA)", Inches(0.5), Inches(0.3), Inches(12), Inches(0.6), font_size=11, bold=True, color=AMBER)
    add_text_box(slide, "Benchmark on Synthetic IMD-Pattern AWS Datasets", Inches(0.5), Inches(0.9), Inches(12), Inches(0.8), font_size=26, bold=True, color=WHITE)
    add_text_box(slide, "⚠  All data is SYNTHETIC — generated with diurnal/seasonal equations. Real IMD AWS CSV/NetCDF data would replace these CSVs.", Inches(0.5), Inches(1.75), Inches(12), Inches(0.5), font_size=13, color=AMBER, italic=True)
    rows = [
        ("1% fault rate", "Hybrid Ensemble", "0.65", "0.46", "0.52"),
        ("3% fault rate", "Hybrid Ensemble", "0.69", "0.55", "0.20"),
        ("8% fault rate", "Hybrid Ensemble", "0.53", "0.40", "0.09"),
        ("1% fault rate", "Statistical (Z+IQR)", "0.53", "0.36", "0.14"),
    ]
    headers = ["Dataset", "Model", "Event F1", "Point Prec", "Point F1"]
    col_lefts = [Inches(0.5), Inches(3.0), Inches(6.0), Inches(8.5), Inches(10.5)]
    col_widths = [Inches(2.4), Inches(2.8), Inches(2.3), Inches(2.3), Inches(2.3)]
    for c, h in enumerate(headers):
        add_text_box(slide, h, col_lefts[c], Inches(2.4), col_widths[c], Inches(0.4), font_size=13, bold=True, color=TEAL)
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            color = AMBER if (r == 0 and c == 2) else (WHITE if r % 2 == 0 else LIGHT_GRAY)
            add_text_box(slide, val, col_lefts[c], Inches(2.9) + Inches(r * 0.7), col_widths[c], Inches(0.6), font_size=13, color=color)
    add_text_box(slide, "Best Event F1: 0.6916 (Hybrid Ensemble, 3% dataset) | SHAP latency < 200 ms (measured)", Inches(0.5), Inches(6.6), Inches(12), Inches(0.4), font_size=13, color=TEAL, italic=True)


def slide_10_impact(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide, NAVY)
    add_text_box(slide, "IMPACT & LIMITATIONS", Inches(0.5), Inches(0.3), Inches(12), Inches(0.6), font_size=11, bold=True, color=TEAL)
    add_text_box(slide, "Real-World Potential & Honest Limitations", Inches(0.5), Inches(0.9), Inches(12), Inches(0.8), font_size=28, bold=True, color=WHITE)
    impacts = [
        "🌍 Protects 1,000+ IMD AWS stations from silent data corruption entering national weather models",
        "🚒 Prevents false civil emergency alerts triggered by sensor faults during extreme weather monitoring",
        "📊 Provides meteorologists with one-click SHAP audit trails for every alert (regulatory compliance)",
        "⚡ ESP32 edge module reduces AWS telemetry costs by pre-screening locally on solar-powered hardware",
    ]
    limits = [
        "⚠  All training data is SYNTHETIC. Real IMD AWS performance requires validation with field data.",
        "⚠  LSTM latency not measured on ESP32. PC benchmark (0.0007 ms) is not hardware-validated.",
        "⚠  Render free-tier RAM (512 MB) requires ENABLE_LSTM=false. Use paid tier for full ensemble.",
        "⚠  Telegram alerts and TimescaleDB require additional configuration for production deployment.",
    ]
    add_text_box(slide, "✅ Impact", Inches(0.5), Inches(2.0), Inches(5.8), Inches(0.4), font_size=14, bold=True, color=TEAL)
    add_text_box(slide, "⚠  Limitations", Inches(6.8), Inches(2.0), Inches(5.8), Inches(0.4), font_size=14, bold=True, color=AMBER)
    for i, t in enumerate(impacts):
        add_text_box(slide, t, Inches(0.5), Inches(2.5) + Inches(i * 0.9), Inches(6.0), Inches(0.8), font_size=13, color=WHITE if i % 2 == 0 else LIGHT_GRAY)
    for i, t in enumerate(limits):
        add_text_box(slide, t, Inches(6.8), Inches(2.5) + Inches(i * 0.9), Inches(6.0), Inches(0.8), font_size=13, color=LIGHT_GRAY)


def slide_11_future(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide, NAVY)
    add_text_box(slide, "FUTURE WORK", Inches(0.5), Inches(0.3), Inches(12), Inches(0.6), font_size=11, bold=True, color=TEAL)
    add_text_box(slide, "Road to Real IMD Data Integration", Inches(0.5), Inches(0.9), Inches(12), Inches(0.8), font_size=28, bold=True, color=WHITE)
    steps = [
        ("Phase 1 — IMD Data Ingestion", "Replace synthetic CSVs with real IMD AWS CSV / NetCDF telemetry.\nMap IMD column schema to SkyGuard's (temperature_c, pressure_hpa, humidity_pct, station_id, timestamp)."),
        ("Phase 2 — Recalibration", "Re-run run_benchmark.py with real data to measure true F1/precision/recall.\nExpect lower recall initially; tune ensemble weights against labelled IMD anomaly ground truth."),
        ("Phase 3 — Microcontroller Validation", "Deploy edge_detector.py on actual ESP32 hardware.\nMeasure real latency and energy under field conditions."),
        ("Phase 4 — Production Hardening", "TimescaleDB continuous aggregates for hypertable partitioning.\nKafka ingestion pipeline for 5,000+ concurrent station streams.\nPrometheus + Grafana observability stack."),
    ]
    for i, (title, body) in enumerate(steps):
        add_text_box(slide, f"{title}", Inches(0.7), Inches(2.0) + Inches(i * 1.3), Inches(12), Inches(0.4), font_size=16, bold=True, color=TEAL)
        add_text_box(slide, body, Inches(1.0), Inches(2.4) + Inches(i * 1.3), Inches(11.5), Inches(0.8), font_size=13, color=LIGHT_GRAY)


def slide_12_closing(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide, NAVY)
    add_title_accent_bar(slide)
    add_text_box(slide, "Thank You", Inches(1), Inches(1.8), Inches(11), Inches(1.2), font_size=52, bold=True, color=TEAL, align=PP_ALIGN.CENTER)
    add_text_box(slide, "SkyGuard AI — SIH26073", Inches(1), Inches(3.2), Inches(11), Inches(0.7), font_size=22, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_text_box(slide, "GitHub: https://github.com/julie249/skyguard-ai", Inches(1), Inches(4.1), Inches(11), Inches(0.5), font_size=16, color=TEAL, align=PP_ALIGN.CENTER)
    add_text_box(slide, "Dashboard: http://localhost:5173  |  API: http://localhost:3000/docs  |  ML: http://localhost:8000/docs", Inches(1), Inches(4.8), Inches(11), Inches(0.5), font_size=14, color=LIGHT_GRAY, align=PP_ALIGN.CENTER)
    add_text_box(slide, "Questions? Ask us to inject a 55°C spike live!", Inches(1), Inches(5.7), Inches(11), Inches(0.5), font_size=15, italic=True, color=AMBER, align=PP_ALIGN.CENTER)


def build_pitch_deck(output_path="docs/pitch_deck.pptx"):
    prs = Presentation()
    prs.slide_width = SLIDE_WIDTH
    prs.slide_height = SLIDE_HEIGHT

    slide_1_title(prs)
    slide_2_problem(prs)
    slide_3_solution(prs)
    slide_4_architecture(prs)
    slide_5_hybrid_detection(prs)
    slide_6_spatial(prs)
    slide_7_explainability(prs)
    slide_8_edge(prs)
    slide_9_results(prs)
    slide_10_impact(prs)
    slide_11_future(prs)
    slide_12_closing(prs)

    prs.save(output_path)
    print(f"✅ Pitch deck saved to: {output_path}  ({prs.slides.__len__()} slides)")
    return output_path


if __name__ == "__main__":
    build_pitch_deck()
