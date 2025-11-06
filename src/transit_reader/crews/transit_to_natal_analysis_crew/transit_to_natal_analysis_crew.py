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
class TransitToNatalAnalysisCrew():
	"""TransitToNatalAnalysisCrew crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	@agent
	def transits_to_natal_chart_reader(self) -> Agent:
		return Agent(
			config=self.agents_config['transits_to_natal_chart_reader'],
			llm=get_llm_for_agent('transits_to_natal_chart_reader'),  # Technical extraction needs low temperature
			tools=[google_search_tool, GeminiSearchTool(), QdrantSearchTool()],
			verbose=True
		)

	@agent
	def transits_to_natal_chart_interpreter(self) -> Agent:
		return Agent(
			config=self.agents_config['transits_to_natal_chart_interpreter'],
			llm=get_llm_for_agent('transits_to_natal_chart_reader'),  # Interpretation benefits from moderate temperature
			verbose=True
		)
	
	
	@task
	def transits_to_natal_chart_reading_task(self) -> Task:
		return Task(
			config=self.tasks_config['transits_to_natal_chart_reading_task'],
			output_file=f"crew_outputs/{TIMESTAMP}/transits_to_natal_chart_reading_task.md"
		)
	
	@task
	def transits_to_natal_chart_interpretation_task(self) -> Task:
		return Task(
			config=self.tasks_config['transits_to_natal_chart_interpretation_task'],
			output_file=f"crew_outputs/{TIMESTAMP}/transits_to_natal_chart_interpretation_task.md"
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the TransitToNatalAnalysisCrew crew"""
		# To learn how to add knowledge sources to your crew, check out the documentation:
		# https://docs.crewai.com/concepts/knowledge#what-is-knowledge

		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True
		)
