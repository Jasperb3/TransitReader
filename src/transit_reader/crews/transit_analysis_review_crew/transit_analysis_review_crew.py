from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from transit_reader.utils.constants import TIMESTAMP
from transit_reader.utils.llm_manager import get_llm_for_agent
from dotenv import load_dotenv

load_dotenv()


@CrewBase
class TransitAnalysisReviewCrew():
	"""TransitAnalysisReviewCrew crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	
	@agent
	def transits_interpretation_critic(self) -> Agent:
		return Agent(
			config=self.agents_config['transits_interpretation_critic'],
			llm=get_llm_for_agent('transits_interpretation_critic'),
			verbose=True
		)

	@agent
	def transits_interpretation_enhancer(self) -> Agent:
		return Agent(
			config=self.agents_config['transits_interpretation_enhancer'],
			llm=get_llm_for_agent('transits_interpretation_enhancer'),
			verbose=True
		)


	@task
	def transits_interpretation_critic_task(self) -> Task:
		return Task(
			config=self.tasks_config['transits_interpretation_critic_task'],
			output_file=f"crew_outputs/{TIMESTAMP}/transits_interpretation_critic_task.md"
		)

	@task
	def transits_interpretation_enhancement_task(self) -> Task:
		return Task(
			config=self.tasks_config['transits_interpretation_enhancement_task'],
			output_file=f"crew_outputs/{TIMESTAMP}/transits_interpretation_enhancement_task.md"
		)


	@crew
	def crew(self) -> Crew:
		"""Creates the TransitAnalysisReviewCrew crew"""
		# To learn how to add knowledge sources to your crew, check out the documentation:
		# https://docs.crewai.com/concepts/knowledge#what-is-knowledge

		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True
		)
