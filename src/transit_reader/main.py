import os
from typing import Tuple
from crewai.flow import Flow, listen, start, and_
from transit_reader.utils.models import TransitState, create_transit_state
from transit_reader.utils.qdrant_setup import Setup
from transit_reader.utils.immanuel_transit_chart import get_transit_chart
from transit_reader.utils.immanuel_natal_chart import get_natal_chart
from transit_reader.utils.immanuel_natal_to_transit_chart import get_transit_natal_aspects
from transit_reader.utils.transit_timing import build_timing_table
from transit_reader.utils.crew_runner import run_crew_with_retry
from transit_reader.utils.kerykeion_chart_utils import get_kerykeion_subject, get_kerykeion_transit_chart
from transit_reader.utils.convert_to_pdf import convert_md_to_pdf
from transit_reader.utils.constants import OUTPUT_DIR, TIMESTAMP, CHARTS_DIR, ensure_output_dirs
from transit_reader.crews.transit_analysis_crew.transit_analysis_crew import TransitAnalysisCrew
from transit_reader.crews.transit_analysis_review_crew.transit_analysis_review_crew import TransitAnalysisReviewCrew
from transit_reader.crews.natal_analysis_crew.natal_analysis_crew import NatalAnalysisCrew
from transit_reader.crews.natal_analysis_review_crew.natal_analysis_review_crew import NatalAnalysisReviewCrew
from transit_reader.crews.transit_to_natal_analysis_crew.transit_to_natal_analysis_crew import TransitToNatalAnalysisCrew
from transit_reader.crews.transit_to_natal_review_crew.transit_to_natal_review_crew import TransitToNatalReviewCrew
from transit_reader.crews.chart_appendices_crew.chart_appendices_crew import ChartAppendicesCrew
from transit_reader.crews.report_writing_crew.report_writing_crew import ReportWritingCrew
from transit_reader.crews.review_crew.review_crew import ReviewCrew
from transit_reader.crews.gmail_crew.gmail_crew import GmailCrew


DISCLAIMER_BLOCK = """
## About This Report

This report is a symbolic and reflective tool for self-exploration. It is not a
substitute for professional medical, psychological, legal, or financial advice.
The practices offered under "Working With This Energy" are general wellbeing
suggestions, not clinical guidance. If you are experiencing significant
distress, please reach out to a qualified professional or support service.
"""


def _insert_chart_if_missing(report_markdown: str, chart_image_markdown: str) -> str:
    """
    Ensure the transit chart image appears in the report even if the
    '[transit_chart]' placeholder was dropped by the enhancer LLM.

    Args:
        report_markdown: The report markdown to check
        chart_image_markdown: The chart image markdown to insert if missing

    Returns:
        str: report_markdown unchanged if the placeholder is present,
            otherwise with the chart image inserted after the first H1
            (or prepended if there's no H1)
    """
    if "[transit_chart]" in report_markdown:
        return report_markdown

    print("Warning: '[transit_chart]' placeholder not found in report; inserting chart image manually.")

    lines = report_markdown.split("\n", 1)
    if lines[0].startswith("# "):
        rest = lines[1] if len(lines) > 1 else ""
        return f"{lines[0]}\n\n{chart_image_markdown}\n\n{rest}"

    return f"{chart_image_markdown}\n\n{report_markdown}"


class TransitFlow(Flow[TransitState]):

    @start()
    def setup_qdrant(self):
        print("Setting up Qdrant")
        ensure_output_dirs()
        setup = Setup(self.state)
        setup.process_new_markdown_files()

    # PARALLEL CHART GENERATION - All three charts can be generated simultaneously
    @listen(setup_qdrant)
    def generate_current_transits(self):
        print("Generating current transits (parallel)")
        current_location: Tuple[float, float] = (
            self.state.current_location_latitude,
            self.state.current_location_longitude
        )

        self.state.current_transits = get_transit_chart(
            current_location[0],
            current_location[1],
            self.state.transit_datetime
        )

    @listen(setup_qdrant)
    def get_natal_chart_data(self):
        print("Getting natal chart data (parallel)")
        natal_chart = get_natal_chart(self.state.date_of_birth, self.state.birthplace_latitude, self.state.birthplace_longitude)
        self.state.natal_chart = natal_chart

    @listen(setup_qdrant)
    def get_transit_to_natal_chart_data(self):
        print("Getting transit to natal chart data (parallel)")
        transit_to_natal_chart = get_transit_natal_aspects(
            self.state.current_location_latitude,
            self.state.current_location_longitude,
            self.state.date_of_birth,
            self.state.birthplace_latitude,
            self.state.birthplace_longitude,
            self.state.transit_datetime
        )
        timing_table = build_timing_table(
            self.state.date_of_birth,
            self.state.birthplace_latitude,
            self.state.birthplace_longitude,
            self.state.current_location_latitude,
            self.state.current_location_longitude,
            self.state.transit_datetime
        )
        self.state.transit_to_natal_chart = transit_to_natal_chart + "\n\n" + timing_table

    # WAIT FOR ALL CHARTS - Use and_() to wait for all three chart generations
    @listen(and_(generate_current_transits, get_natal_chart_data, get_transit_to_natal_chart_data))
    def generate_transit_analysis(self):
        print("Generating transit analysis")
        inputs = {
            "current_transits": self.state.current_transits,
            "name": self.state.name,
            "transit_date": self.state.transit_date_formatted,
            "location": self.state.current_location,
            "biographical_context": self.state.biographical_context
        }

        transit_analysis = run_crew_with_retry(
            lambda: TransitAnalysisCrew().crew(), inputs, "generate_transit_analysis"
        )

        self.state.transit_analysis = transit_analysis.raw


    # PARALLEL ANALYSIS GENERATION - All three analyses can run simultaneously after charts are ready
    @listen(and_(generate_current_transits, get_natal_chart_data, get_transit_to_natal_chart_data))
    def generate_natal_analysis(self):
        print("Generating natal analysis (parallel)")

        inputs = {
            "natal_chart": self.state.natal_chart,
            "name": self.state.name,
            "date_of_birth": self.state.dob,
            "birthplace": self.state.birthplace,
            "analysis_date": self.state.today,  # Date report is being generated
            "biographical_context": self.state.biographical_context
        }

        natal_analysis = run_crew_with_retry(
            lambda: NatalAnalysisCrew().crew(), inputs, "generate_natal_analysis"
        )

        self.state.natal_analysis = natal_analysis.raw

    @listen(and_(generate_current_transits, get_natal_chart_data, get_transit_to_natal_chart_data))
    def generate_transit_to_natal_analysis(self):
        print("Generating transit to natal analysis (parallel)")
        inputs = {
            "transit_to_natal_chart": self.state.transit_to_natal_chart,
            "name": self.state.name,
            "transit_date": self.state.transit_date_formatted,
            "date_of_birth": self.state.dob,
            "birthplace": self.state.birthplace,
            "transit_location": self.state.current_location,
            "biographical_context": self.state.biographical_context
        }

        transit_to_natal_analysis = run_crew_with_retry(
            lambda: TransitToNatalAnalysisCrew().crew(), inputs, "generate_transit_to_natal_analysis"
        )

        self.state.transit_to_natal_analysis = transit_to_natal_analysis.raw

    # PARALLEL REVIEW - All three reviews can run simultaneously after their analyses complete
    @listen(generate_transit_analysis)
    def review_transit_analysis(self):
        print("Reviewing transit analysis (parallel)")
        inputs = {
            "transit_analysis": self.state.transit_analysis,
            "current_transits": self.state.current_transits,
            "transit_date": self.state.transit_date_formatted,
            "name": self.state.name,
            "location": self.state.current_location
        }

        enhanced_transit_analysis = run_crew_with_retry(
            lambda: TransitAnalysisReviewCrew().crew(), inputs, "review_transit_analysis"
        )

        self.state.transit_analysis = enhanced_transit_analysis.raw

    @listen(generate_natal_analysis)
    def review_natal_analysis(self):
        print("Reviewing natal analysis (parallel)")
        inputs = {
            "natal_analysis": self.state.natal_analysis,
            "natal_chart": self.state.natal_chart,
            "name": self.state.name,
            "analysis_date": self.state.today,
            "date_of_birth": self.state.dob,
            "birthplace": self.state.birthplace
        }

        enhanced_natal_analysis = run_crew_with_retry(
            lambda: NatalAnalysisReviewCrew().crew(), inputs, "review_natal_analysis"
        )

        self.state.natal_analysis = enhanced_natal_analysis.raw

    @listen(generate_transit_to_natal_analysis)
    def review_transit_to_natal_analysis(self):
        print("Reviewing transit to natal analysis (parallel)")

        inputs = {
            "transit_to_natal_analysis": self.state.transit_to_natal_analysis,
            "transit_to_natal_chart": self.state.transit_to_natal_chart,
            "name": self.state.name,
            "transit_date": self.state.transit_date_formatted,
            "date_of_birth": self.state.dob,
            "birthplace": self.state.birthplace,
            "transit_location": self.state.current_location
        }

        enhanced_transit_to_natal_analysis = run_crew_with_retry(
            lambda: TransitToNatalReviewCrew().crew(), inputs, "review_transit_to_natal_analysis"
        )

        self.state.transit_to_natal_analysis = enhanced_transit_to_natal_analysis.raw

    # GENERATE APPENDICES - Create structured appendices from all three analyses
    @listen(and_(review_transit_analysis, review_natal_analysis, review_transit_to_natal_analysis))
    def generate_chart_appendices(self):
        # Check if user wants appendices
        if not self.state.include_appendices:
            print("⏭️  Skipping chart appendices generation (user preference)")
            self.state.chart_appendices = ""  # Set to empty string
            return self.state

        print("Generating chart appendices")
        inputs = {
            "transit_analysis": self.state.transit_analysis,
            "current_transits": self.state.current_transits,
            "natal_analysis": self.state.natal_analysis,
            "natal_chart": self.state.natal_chart,
            "transit_to_natal_analysis": self.state.transit_to_natal_analysis,
            "transit_to_natal_chart": self.state.transit_to_natal_chart,
            "name": self.state.name,
            "transit_date": self.state.transit_date_formatted,
            "date_of_birth": self.state.dob,
            "birthplace": self.state.birthplace,
            "location": self.state.current_location,
            "transit_location": self.state.current_location
        }

        appendices_result = run_crew_with_retry(
            lambda: ChartAppendicesCrew().crew(), inputs, "generate_chart_appendices"
        )

        self.state.chart_appendices = appendices_result.raw

    # WAIT FOR APPENDICES - Report generation needs all three enhanced analyses AND appendices
    @listen(generate_chart_appendices)
    def generate_report_draft(self):
        print("Generating report draft")
        inputs = {
            "transit_analysis": self.state.transit_analysis,
            "natal_analysis": self.state.natal_analysis,
            "transit_to_natal_analysis": self.state.transit_to_natal_analysis,
            "name": self.state.name,
            "report_date": self.state.today,  # Date report is being generated
            "transit_date": self.state.transit_date_formatted,  # Date of transits being analyzed
            "is_custom_transit": self.state.is_custom_transit,
            "transit_location": self.state.current_location,
            "date_of_birth": self.state.dob,
            "birthplace": self.state.birthplace,
            "biographical_context": self.state.biographical_context
        }

        report_draft = run_crew_with_retry(
            lambda: ReportWritingCrew().crew(), inputs, "generate_report_draft"
        )

        self.state.report_markdown = report_draft.raw


    @listen(generate_report_draft)
    def interrogate_report_draft(self):
        print("Interrogating report draft")

        inputs = {
            "report": self.state.report_markdown,
            "transit_analysis": self.state.transit_analysis,
            "natal_analysis": self.state.natal_analysis,
            "transit_to_natal_analysis": self.state.transit_to_natal_analysis,
            "transit_chart": self.state.current_transits,
            "natal_chart": self.state.natal_chart,
            "transit_to_natal_chart": self.state.transit_to_natal_chart,
            "report_date": self.state.today,
            "transit_date": self.state.transit_date_formatted,
            "name": self.state.name,
            "transit_location": self.state.current_location,
            "date_of_birth": self.state.dob,
            "birthplace": self.state.birthplace
        }

        enhanced_report_draft = run_crew_with_retry(
            lambda: ReviewCrew().crew(), inputs, "interrogate_report_draft"
        )

        self.state.report_markdown = enhanced_report_draft.raw
        

    @listen(interrogate_report_draft)
    def generate_kerykeion_transit_chart(self):
        print("Generating kerykeion transit chart")

        main_subject = get_kerykeion_subject(
            self.state.name,
            self.state.date_of_birth.year,
            self.state.date_of_birth.month,
            self.state.date_of_birth.day,
            self.state.date_of_birth.hour,
            self.state.date_of_birth.minute,
            self.state.birthplace_city,
            self.state.birthplace_country,
            self.state.birthplace_longitude,
            self.state.birthplace_latitude,
            self.state.birthplace_timezone
        )

        # Use transit_datetime instead of NOW_DT
        transit_dt = self.state.transit_datetime
        transit_subject = get_kerykeion_subject(
            "Transits" if not self.state.is_custom_transit else f"Custom Transits ({transit_dt.strftime('%Y-%m-%d %H:%M')})",
            transit_dt.year,
            transit_dt.month,
            transit_dt.day,
            transit_dt.hour,
            transit_dt.minute,
            self.state.current_location_city,
            self.state.current_location_country,
            self.state.current_location_longitude,
            self.state.current_location_latitude,
            self.state.current_location_timezone
        )
        
        kerykeion_transit_chart = get_kerykeion_transit_chart(main_subject, transit_subject, CHARTS_DIR)
        
        self.state.kerykeion_transit_chart = kerykeion_transit_chart


    @listen(generate_kerykeion_transit_chart)
    def save_transit_analysis(self):
        print("Saving transit analysis")
        markdown_file_path = OUTPUT_DIR / f"{self.state.name.replace(' ', '_')}_{TIMESTAMP}.md"

        # Replace chart placeholder (inserting it if the LLM dropped it) and append the appendices
        chart_image_markdown = f"![Transit Chart]({self.state.kerykeion_transit_chart})"
        self.state.report_markdown = _insert_chart_if_missing(self.state.report_markdown, chart_image_markdown)
        self.state.report_markdown = self.state.report_markdown.replace("[transit_chart]", chart_image_markdown)

        # Insert appendices at the end of the report (before writing to file)
        if self.state.chart_appendices:
            # Add page break and appendices section
            full_markdown = self.state.report_markdown + "\n\n---\n\n" + self.state.chart_appendices
        else:
            full_markdown = self.state.report_markdown

        full_markdown = full_markdown + "\n\n---\n" + DISCLAIMER_BLOCK

        with open(markdown_file_path, "w") as f:
            f.write(full_markdown)

        print(f"Final report markdown saved to {markdown_file_path}")

        pdf_file_path = convert_md_to_pdf(markdown_file_path)
        self.state.report_pdf = pdf_file_path
        print(f"Report pdf saved to {pdf_file_path}")


    @listen(save_transit_analysis)
    def send_transit_analysis(self):
        print("Drafting email...")

        inputs = {
            "report_text": self.state.report_markdown[:4000],
            "report_pdf": str(self.state.report_pdf),
            "client": self.state.name,
            "sender": os.getenv("REPORT_SENDER_NAME", "TransitReader"),
            "email_address": self.state.email,
            "report_date": self.state.today,
            "transit_date": self.state.transit_date_formatted
        }

        email_result = run_crew_with_retry(
            lambda: GmailCrew().crew(), inputs, "send_transit_analysis"
        )

        if email_result.raw:
            print("Email draft complete")
        else:
            print("Email draft failed")


def kickoff():
    state = create_transit_state()
    transit_flow = TransitFlow()
    transit_flow.kickoff(inputs=state.model_dump())


def plot():
    transit_flow = TransitFlow()
    transit_flow.plot()


if __name__ == "__main__":
    kickoff()
