import os
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from transit_reader.tools.google_search_tool import GoogleSearchTool
from transit_reader.tools.gemini_search_tool import GeminiSearchTool
from transit_reader.tools.qdrant_search_tool import QdrantSearchTool
from transit_reader.utils.constants import TIMESTAMP
from transit_reader.utils.llm_manager import get_llm_for_agent
from dotenv import load_dotenv

load_dotenv()


@CrewBase
class ReportWritingCrew:
    """ReportWritingCrew crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def astrological_data_interpreter(self) -> Agent:
        return Agent(
            config=self.agents_config["astrological_data_interpreter"],
            llm=get_llm_for_agent('astrological_data_interpreter'),
            verbose=True,
        )

    @agent
    def astrological_report_writer(self) -> Agent:
        return Agent(
            config=self.agents_config["astrological_report_writer"],
            llm=get_llm_for_agent('astrological_data_interpreter'),
            verbose=True,
        )

    @task
    def data_interpretation_task(self) -> Task:
        return Task(
            config=self.tasks_config["data_interpretation_task"],
            output_file=f"crew_outputs/{TIMESTAMP}/data_interpretation_task.md",
        )

    @task
    def report_writing_task(self) -> Task:
        return Task(
            config=self.tasks_config["report_writing_task"],
            output_file=f"crew_outputs/{TIMESTAMP}/report_writing_task.md",
        )

    @crew
    def crew(self) -> Crew:
        """Creates the ReportWritingCrew crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )
