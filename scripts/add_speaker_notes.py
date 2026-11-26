"""
Task 8: Add speaker notes to each pitch deck slide.
Run from: C:\JULIEE\Projects\skyguard-ai
Usage: python scripts/add_speaker_notes.py
"""
import sys
from pathlib import Path
from pptx import Presentation
from pptx.util import Pt
from pptx.dml.color import RGBColor

DECK_PATH = Path("docs/pitch_deck.pptx")

# Speaker notes indexed by slide title keywords (case-insensitive substring match)
# Each note is ~30-45 seconds of spoken content
NOTES_BY_KEYWORD = {
    "title": (
        "Good morning / Good afternoon. We are Team SkyGuard. "
        "India operates over 800 Automatic Weather Stations across the country. "
        "Every year, sensor hardware failures cause undetected false extremes that corrupt forecasting data. "
        "Our system, SkyGuard AI, automatically catches these faults in real time — before they reach the forecast pipeline."
    ),
    "problem": (
        "Weather forecasting depends entirely on the quality of sensor data coming from the field. "
        "Currently, when a thermistor fails and reports 55 degrees Celsius in January, "
        "it takes a human observer or a downstream QC pass to flag it — often hours or days later. "
        "Meanwhile, the false reading has already been ingested. "
        "We asked: can a machine distinguish a broken sensor from a real heatwave? The answer is yes."
    ),
    "solution": (
        "SkyGuard AI intercepts every AWS telemetry packet and runs a three-stage pipeline: "
        "spatial corroboration checks whether neighbouring stations agree, "
        "a Hybrid Ensemble ML model scores the anomaly, "
        "and SHAP values explain which features drove the decision. "
        "The result: a confident label — sensor fault or genuine extreme — with a human-readable root cause, "
        "delivered in under one millisecond on a laptop and an estimated 0.4 to 1.2 milliseconds on ESP32 hardware."
    ),
    "architecture": (
        "The system has three deployable layers. "
        "At the edge, an ESP32 MicroPython module runs a lightweight decision tree for immediate local flagging. "
        "In the cloud, a Node.js Fastify backend orchestrates data flow, "
        "and a Python FastAPI ML microservice runs the full Hybrid Ensemble. "
        "Everything is containerised with Docker Compose and deployable in one command. "
        "The React dashboard shows live telemetry, geospatial station health, and SHAP explainability cards."
    ),
    "ml": (
        "Our Hybrid Ensemble combines an Isolation Forest for unsupervised outlier detection, "
        "a Random Forest classifier for rule-based labelling, "
        "and an LSTM sequence model for temporal drift. "
        "On our synthetic benchmark at 1 percent fault injection rate, "
        "the ensemble achieves an Event F1 of 0.65, rising to 0.69 at 3 percent fault rate. "
        "SHAP feature attribution makes every prediction auditable — a critical requirement for a government system."
    ),
    "demo": (
        "Let me show you a live demo. "
        "This is the dashboard running against our synthetic dataset of 200 stations. "
        "I will now inject a simulated sensor fault — watch the orange alert appear instantly on the right feed, "
        "with a SHAP explanation card showing temperature was the dominant feature. "
        "If I stop the ML service, you can see the yellow offline banner appear — no crash, readings are still saved."
    ),
    "result": (
        "To summarise our verified performance numbers: "
        "Hybrid Ensemble Event F1 is 0.65 at 1 percent fault rate and 0.69 at 3 percent fault rate on synthetic data. "
        "Edge inference latency is 0.0007 milliseconds measured on a PC. "
        "The backend handles 100 concurrent WebSocket clients with less than 50 milliseconds latency. "
        "These numbers are from real benchmark runs on our codebase — no extrapolation."
    ),
    "limitation": (
        "We want to be transparent about limitations. "
        "All training and benchmarking used algorithmically-generated synthetic data — not real IMD AWS CSV exports. "
        "The LSTM model requires at least 1 gigabyte of RAM, so we provide an ENABLE_LSTM equals false flag for low-memory environments. "
        "ESP32 latency figures are theoretical estimates, not measured on physical hardware. "
        "Real-world F1 scores may differ from synthetic benchmarks until the model is fine-tuned on actual IMD data."
    ),
    "future": (
        "Our immediate next step is integration with real IMD AWS data feeds — either the CSV or NetCDF export format. "
        "We plan an ESP32 field trial at a university weather station to validate the edge latency estimate. "
        "Longer term, we want to extend the spatial corroboration to a graph neural network "
        "so that the system can learn station neighbourhood structure automatically, rather than relying on fixed Haversine thresholds."
    ),
    "team": (
        "We are a team of final-year engineering students who built this end-to-end in six weeks for Smart India Hackathon 2026. "
        "Every component — the ML pipeline, the backend API, the React dashboard, the ESP32 firmware, and the Docker configuration — "
        "was written and benchmarked by us. "
        "Thank you for your time. We are happy to take questions."
    ),
}

def set_slide_notes(slide, text: str):
    """Set or replace the notes text for a slide."""
    notes_slide = slide.notes_slide
    tf = notes_slide.notes_text_frame
    # Clear existing paragraphs
    for para in tf.paragraphs[1:]:
        p = para._p
        p.getparent().remove(p)
    # Set text in first paragraph
    tf.paragraphs[0].text = text
    for run in tf.paragraphs[0].runs:
        run.font.size = Pt(12)


def get_slide_title(slide) -> str:
    """Extract the title text from a slide, returning empty string if none."""
    for shape in slide.shapes:
        if shape.has_text_frame and shape.shape_type == 13:  # title
            return shape.text_frame.text.lower()
        if hasattr(shape, "placeholder_format") and shape.placeholder_format is not None:
            ph = shape.placeholder_format.idx
            if ph == 0:  # title placeholder
                return shape.text_frame.text.lower() if shape.has_text_frame else ""
    return ""


def get_all_slide_text(slide) -> str:
    """Get all text from a slide (title + body)."""
    texts = []
    for shape in slide.shapes:
        if shape.has_text_frame:
            texts.append(shape.text_frame.text.lower())
    return " ".join(texts)


def find_matching_note(slide_text: str) -> str | None:
    """Find the best matching speaker note for a slide based on keyword matching."""
    best_key = None
    best_score = 0
    for keyword, note in NOTES_BY_KEYWORD.items():
        # Score by how many keywords match
        score = sum(1 for word in keyword.split() if word in slide_text)
        if score > best_score:
            best_score = score
            best_key = keyword
    if best_key and best_score > 0:
        return NOTES_BY_KEYWORD[best_key]
    return None


def add_missing_slides(prs: Presentation) -> Presentation:
    """Check for Limitations and Future Work slides; add if missing."""
    all_text = " ".join(
        get_all_slide_text(s) for s in prs.slides
    )
    
    added = []
    
    if "limitation" not in all_text:
        slide_layout = prs.slide_layouts[1]  # title + content
        slide = prs.slides.add_slide(slide_layout)
        for shape in slide.placeholders:
            if shape.placeholder_format.idx == 0:
                shape.text = "Limitations & Honest Evaluation"
            elif shape.placeholder_format.idx == 1:
                shape.text = (
                    "• All metrics measured on SYNTHETIC data — not real IMD AWS telemetry\n"
                    "• Hybrid Ensemble Event F1: 0.65 (1% fault rate) / 0.69 (3% fault rate)\n"
                    "• LSTM requires ≥1 GB RAM; disabled by default in Docker (ENABLE_LSTM=false)\n"
                    "• ESP32 latency (0.4–1.2 ms) is a theoretical estimate — not yet hardware-verified\n"
                    "• Real-world accuracy will differ until fine-tuned on actual IMD data"
                )
        set_slide_notes(slide, NOTES_BY_KEYWORD["limitation"])
        added.append("Limitations")
    
    if "future" not in all_text and "real imd" not in all_text:
        slide_layout = prs.slide_layouts[1]
        slide = prs.slides.add_slide(slide_layout)
        for shape in slide.placeholders:
            if shape.placeholder_format.idx == 0:
                shape.text = "Future Work"
            elif shape.placeholder_format.idx == 1:
                shape.text = (
                    "• Integrate real IMD AWS CSV / NetCDF data feeds for model fine-tuning\n"
                    "• Hardware field trial: deploy ESP32 at a university weather station\n"
                    "• Graph Neural Network for automatic spatial neighbourhood learning\n"
                    "• Federated learning: train across AWS nodes without centralising raw data\n"
                    "• Partnership with IMD for pilot deployment under SIH26073 mandate"
                )
        set_slide_notes(slide, NOTES_BY_KEYWORD["future"])
        added.append("Future Work")
    
    return prs, added


def main():
    if not DECK_PATH.exists():
        print(f"ERROR: {DECK_PATH} not found")
        sys.exit(1)

    prs = Presentation(str(DECK_PATH))
    print(f"Loaded {DECK_PATH} — {len(prs.slides)} slides")

    # Add missing required slides
    prs, added_slides = add_missing_slides(prs)
    if added_slides:
        print(f"  + Added missing slides: {', '.join(added_slides)}")

    # Add speaker notes to all slides
    noted = 0
    for i, slide in enumerate(prs.slides, 1):
        slide_text = get_all_slide_text(slide)
        note = find_matching_note(slide_text)
        
        if not note:
            # Fallback generic note
            note = (
                f"[Slide {i}] "
                "Talk through the content on this slide. "
                "Reference the diagram or data if present. "
                "Invite questions on specific numbers or design choices."
            )
        
        set_slide_notes(slide, note)
        title_preview = slide_text[:60].replace('\n', ' ').strip()
        print(f"  Slide {i:2d}: notes added — '{title_preview}...'")
        noted += 1

    prs.save(str(DECK_PATH))
    print(f"\n✓ Saved {DECK_PATH} — {len(prs.slides)} slides, {noted} notes written")


if __name__ == "__main__":
    main()
