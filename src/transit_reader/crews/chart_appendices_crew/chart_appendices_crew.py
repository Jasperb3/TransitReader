import os
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from transit_reader.tools.qdrant_search_tool import QdrantSearchTool
from transit_reader.utils.constants import TIMESTAMP
from transit_reader.utils.llm_manager import get_llm_for_agent
from dotenv import load_dotenv

load_dotenv()


@CrewBase
class ChartAppendicesCrew():
	"""ChartAppendicesCrew - generates structured appendices from chart analyses"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	@agent
	def chart_data_synthesizer(self) -> Agent:
		return Agent(
			config=self.agents_config['chart_data_synthesizer'],
			llm=get_llm_for_agent('chart_data_synthesizer'),
			tools=[QdrantSearchTool()],
			verbose=True
		)

	@task
	def transit_chart_appendix_task(self) -> Task:
		return Task(
			config=self.tasks_config['transit_chart_appendix_task'],
			output_file=f"crew_outputs/{TIMESTAMP}/transit_chart_appendix.md"
		)

	@task
	def natal_chart_appendix_task(self) -> Task:
		return Task(
			config=self.tasks_config['natal_chart_appendix_task'],
			output_file=f"crew_outputs/{TIMESTAMP}/natal_chart_appendix.md"
		)

	@task
	def transit_to_natal_appendix_task(self) -> Task:
		return Task(
			config=self.tasks_config['transit_to_natal_appendix_task'],
			output_file=f"crew_outputs/{TIMESTAMP}/transit_to_natal_appendix.md"
		)

	@task
	def combined_appendices_task(self) -> Task:
		return Task(
			config=self.tasks_config['combined_appendices_task'],
			output_file=f"crew_outputs/{TIMESTAMP}/combined_appendices.md",
			context=[
				self.transit_chart_appendix_task(),
				self.natal_chart_appendix_task(),
				self.transit_to_natal_appendix_task()
			]
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the ChartAppendicesCrew crew"""
		return Crew(
			agents=self.agents,  # Automatically created by the @agent decorator
			tasks=self.tasks,  # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True
		)
