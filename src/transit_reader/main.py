import os
import json
from datetime import datetime
from typing import Tuple
from crewai.flow import Flow, listen, start, and_
from transit_reader.utils.models import TransitState, create_transit_state
from transit_reader.utils.qdrant_setup import Setup
from transit_reader.utils.immanuel_transit_chart import get_transit_chart
from transit_reader.utils.immanuel_natal_chart import get_natal_chart
from transit_reader.utils.immanuel_natal_to_transit_chart import get_transit_natal_aspects
from transit_reader.utils.kerykeion_chart_utils import get_kerykeion_subject, get_kerykeion_transit_chart
from transit_reader.utils.convert_to_pdf import convert_md_to_pdf
from transit_reader.utils.constants import NOW_DT, OUTPUT_DIR, TIMESTAMP, CHARTS_DIR
from transit_reader.crews.transit_analysis_crew.transit_analysis_crew import TransitAnalysisCrew
from transit_reader.crews.transit_analysis_review_crew.transit_analysis_review_crew import TransitAnalysisReviewCrew
from transit_reader.crews.natal_analysis_crew.natal_analysis_crew import NatalAnalysisCrew
from transit_reader.crews.natal_analysis_review_crew.natal_analysis_review_crew import NatalAnalysisReviewCrew
from transit_reader.crews.transit_to_natal_analysis_crew.transit_to_natal_analysis_crew import TransitToNatalAnalysisCrew
from transit_reader.crews.transit_to_natal_review_crew.transit_to_natal_review_crew import TransitToNatalReviewCrew
from transit_reader.crews.report_writing_crew.report_writing_crew import ReportWritingCrew
from transit_reader.crews.review_crew.review_crew import ReviewCrew
from transit_reader.crews.gmail_crew.gmail_crew import GmailCrew


class TransitFlow(Flow[TransitState]):

    @start()
    def setup_qdrant(self):
        print("Setting up Qdrant")
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
        self.state.transit_to_natal_chart = transit_to_natal_chart

    # WAIT FOR ALL CHARTS - Use and_() to wait for all three chart generations
    @listen(and_(generate_current_transits, get_natal_chart_data, get_transit_to_natal_chart_data))
    def generate_transit_analysis(self):
        print("Generating transit analysis")
        inputs = {
            "current_transits": self.state.current_transits,
            "name": self.state.name,
            "today": self.state.today,
            "location": self.state.current_location
        }

        transit_analysis = (
            TransitAnalysisCrew()
            .crew()
            .kickoff(inputs=inputs)
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
            "today": self.state.today
        }

        natal_analysis = (
            NatalAnalysisCrew()
            .crew()
            .kickoff(inputs=inputs)
        )

        self.state.natal_analysis = natal_analysis.raw

    @listen(and_(generate_current_transits, get_natal_chart_data, get_transit_to_natal_chart_data))
    def generate_transit_to_natal_analysis(self):
        print("Generating transit to natal analysis (parallel)")
        inputs = {
            "transit_to_natal_chart": self.state.transit_to_natal_chart,
            "name": self.state.name,
            "today": self.state.today,
            "date_of_birth": self.state.dob,
            "birthplace": self.state.birthplace,
            "current_location": self.state.current_location
        }

        transit_to_natal_analysis = (
            TransitToNatalAnalysisCrew()
            .crew()
            .kickoff(inputs=inputs)
        )

        self.state.transit_to_natal_analysis = transit_to_natal_analysis.raw

    # PARALLEL REVIEW - All three reviews can run simultaneously after their analyses complete
    @listen(generate_transit_analysis)
    def review_transit_analysis(self):
        print("Reviewing transit analysis (parallel)")
        inputs = {
            "transit_analysis": self.state.transit_analysis,
            "current_transits": self.state.current_transits,
            "today": self.state.today,
            "name": self.state.name,
            "location": self.state.current_location
        }

        enhanced_transit_analysis = (
            TransitAnalysisReviewCrew()
            .crew()
            .kickoff(inputs=inputs)
        )

        self.state.transit_analysis = enhanced_transit_analysis.raw

    @listen(generate_natal_analysis)
    def review_natal_analysis(self):
        print("Reviewing natal analysis (parallel)")
        inputs = {
            "natal_analysis": self.state.natal_analysis,
            "natal_chart": self.state.natal_chart,
            "name": self.state.name,
            "today": self.state.today,
            "date_of_birth": self.state.dob,
            "birthplace": self.state.birthplace
        }

        enhanced_natal_analysis = (
            NatalAnalysisReviewCrew()
            .crew()
            .kickoff(inputs=inputs)
        )

        self.state.natal_analysis = enhanced_natal_analysis.raw

    @listen(generate_transit_to_natal_analysis)
    def review_transit_to_natal_analysis(self):
        print("Reviewing transit to natal analysis (parallel)")

        inputs = {
            "transit_to_natal_analysis": self.state.transit_to_natal_analysis,
            "transit_to_natal_chart": self.state.transit_to_natal_chart,
            "name": self.state.name,
            "today": self.state.today,
            "date_of_birth": self.state.dob,
            "birthplace": self.state.birthplace,
            "current_location": self.state.current_location
        }

        enhanced_transit_to_natal_analysis = (
            TransitToNatalReviewCrew()
            .crew()
            .kickoff(inputs=inputs)
        )

        self.state.transit_to_natal_analysis = enhanced_transit_to_natal_analysis.raw

    # WAIT FOR ALL REVIEWS - Report generation needs all three enhanced analyses
    @listen(and_(review_transit_analysis, review_natal_analysis, review_transit_to_natal_analysis))
    def generate_report_draft(self):
        print("Generating report draft")
        inputs = {
            "transit_analysis": self.state.transit_analysis,
            "natal_analysis": self.state.natal_analysis,
            "transit_to_natal_analysis": self.state.transit_to_natal_analysis,
            "name": self.state.name,
            "today": self.state.today,
            "transit_date": self.state.transit_date_formatted,
            "is_custom_transit": self.state.is_custom_transit,
            "location": self.state.current_location,
            "date_of_birth": self.state.dob,
            "birthplace": self.state.birthplace,
            "current_location": self.state.current_location
        }

        report_draft = (
            ReportWritingCrew()
            .crew()
            .kickoff(inputs=inputs)
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
            "today": self.state.today,
            "name": self.state.name,
            "location": self.state.current_location,
            "date_of_birth": self.state.dob,
            "birthplace": self.state.birthplace
        }

        enhanced_report_draft = (
            ReviewCrew()
            .crew()
            .kickoff(inputs=inputs)
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

        self.state.report_markdown = self.state.report_markdown.replace("[transit_chart]", f"![Transit Chart]({self.state.kerykeion_transit_chart})")
        with open(markdown_file_path, "w") as f:
            f.write(self.state.report_markdown)

        print(f"Final report markdown saved to {markdown_file_path}")

        pdf_file_path = convert_md_to_pdf(markdown_file_path)
        self.state.report_pdf = pdf_file_path
        print(f"Report pdf saved to {pdf_file_path}")


    @listen(save_transit_analysis)
    def send_transit_analysis(self):
        print("Drafting email...")

        try:
            token_file_path = "src/transit_reader/utils/token.json"
            with open(token_file_path, "r") as f:
                token_data = json.load(f)
                expiry_date = token_data.get("expiry")
                if expiry_date:
                    expiry_date = datetime.fromisoformat(expiry_date)
                    if expiry_date < NOW_DT:
                        print("Token expired. Re-authentication required.")
                        os.remove(token_file_path)

        except FileNotFoundError:
            print("Token file not found. Re-authentication required.")
        except json.JSONDecodeError:
            print("Error decoding token file. Re-authentication required.")
            os.remove(token_file_path)
        except Exception as e:
            print(f"Unexpected error: {str(e)}")


        inputs = {
            "report_text": self.state.transit_analysis,
            "report_pdf": str(self.state.report_pdf),
            "client": self.state.name,
            "sender": "Ben Jasper",
            "email_address": self.state.email,
            "today": self.state.today
        }

        email_result = (
            GmailCrew()
            .crew()
            .kickoff(inputs=inputs)
        )

        if email_result.raw:
            print("Email draft complete")
        else:
            print("Email draft failed")


def kickoff():
    # Create state with interactive prompts for subject and transit parameters
    state = create_transit_state()
    transit_flow = TransitFlow()
    transit_flow._state = state
    transit_flow.kickoff()


def plot():
    transit_flow = TransitFlow()
    transit_flow.plot()


if __name__ == "__main__":
    kickoff()
