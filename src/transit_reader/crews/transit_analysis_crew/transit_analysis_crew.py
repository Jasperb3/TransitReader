import os
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from transit_reader.tools.google_search_tool import GoogleSearchTool
from transit_reader.tools.gemini_search_tool import GeminiSearchTool
from transit_reader.tools.qdrant_search_tool import QdrantSearchTool
from transit_reader.utils.constants import TIMESTAMP
from dotenv import load_dotenv

load_dotenv()

google_search_tool = GoogleSearchTool(api_key=os.getenv("GOOGLE_SEARCH_API_KEY"), cx=os.getenv("SEARCH_ENGINE_ID"))


gpt41 = LLM(
	model="gpt-4.1",
	api_key = os.getenv("OPENAI_API_KEY"),
	temperature=0.7
)

gpt41mini = LLM(
	model="gpt-4.1-mini",
	api_key = os.getenv("OPENAI_API_KEY"),
	temperature=0.7
)


@CrewBase
class TransitAnalysisCrew():
	"""TransitAnalysisCrew crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	@agent
	def current_transits_reader(self) -> Agent:
		return Agent(
			config=self.agents_config['current_transits_reader'],
			llm=gpt41,
			tools=[google_search_tool, GeminiSearchTool(), QdrantSearchTool()],
			verbose=True
		)
	
	@agent
	def current_transits_interpreter(self) -> Agent:
		return Agent(
			config=self.agents_config['current_transits_interpreter'],
			llm=gpt41,
			verbose=True
		)
	
	
	@task
	def current_transits_task(self) -> Task:
		return Task(
			config=self.tasks_config['current_transits_task'],
			output_file=f"crew_outputs/{TIMESTAMP}/current_transits_task.md"
		)
	
	@task
	def current_transits_interpretation_task(self) -> Task:
		return Task(
			config=self.tasks_config['current_transits_interpretation_task'],
			output_file=f"crew_outputs/{TIMESTAMP}/current_transits_interpretation_task.md"
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the TransitAnalysisCrew crew"""
		# To learn how to add knowledge sources to your crew, check out the documentation:
		# https://docs.crewai.com/concepts/knowledge#what-is-knowledge

		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True
		)
