"""
Biographical Questionnaire Module

Collects voluntary, targeted biographical context to ground astrological interpretations
in the subject's actual life circumstances. Based on the methodology of respected
astrologers like Liz Greene, Dane Rudhyar, Stephen Arroyo, and others who emphasize
grounding symbolic patterns in developmental tasks, active life arenas, emotional tone,
choices under pressure, and long-term narrative arcs.

All questions are optional. Subjects can skip any question or the entire questionnaire.

Questions are defined in: src/transit_reader/config/biographical_questions.yaml
"""

import json
import yaml
from pathlib import Path

# ANSI color codes
CYAN = "\033[96m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

# Path to questions configuration
QUESTIONS_CONFIG_PATH = Path(__file__).parent.parent / "config" / "biographical_questions.yaml"


def _load_questions_config() -> dict:
    """
    Load questions configuration from YAML file.

    Returns:
        Dictionary containing questions configuration

    Raises:
        FileNotFoundError: If questions config file doesn't exist
        yaml.YAMLError: If YAML is malformed
    """
    try:
        with open(QUESTIONS_CONFIG_PATH, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Questions configuration file not found at {QUESTIONS_CONFIG_PATH}. "
            "Please ensure biographical_questions.yaml exists in src/transit_reader/config/"
        )
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Error parsing questions configuration: {e}")


def get_biographical_context(subject_name: str, skip_questionnaire: bool = False) -> dict:
    """
    Collect biographical context through an interactive questionnaire.

    Args:
        subject_name: Name of the subject for personalized prompts
        skip_questionnaire: If True, skip questionnaire entirely

    Returns:
        Dictionary containing biographical context responses
    """
    if skip_questionnaire:
        print(f"{YELLOW}Skipping biographical questionnaire.{RESET}")
        return {}

    # Load questions from configuration
    try:
        config = _load_questions_config()
    except (FileNotFoundError, yaml.YAMLError) as e:
        print(f"{RED}Error loading questionnaire: {e}{RESET}")
        return {}

    print(f"\n{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f"{CYAN}         Biographical Context Questionnaire{RESET}")
    print(f"{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}\n")

    print(f"This optional questionnaire helps ground the transit analysis in {subject_name}'s")
    print("actual life circumstances, developmental stage, and current challenges.")
    print(f"\n{YELLOW}All questions are optional. Press Enter to skip any question.{RESET}\n")

    biographical_context = {}
    total_questions = 0

    # Iterate through sections and questions
    for section in config.get('sections', []):
        section_name = section.get('section_name', 'Unnamed Section')
        print(f"{GREEN}━━━ {section_name} ━━━{RESET}\n")

        for question_config in section.get('questions', []):
            total_questions += 1
            key = question_config.get('key')
            question = question_config.get('question')
            hint = question_config.get('hint')

            if key and question:
                biographical_context[key] = _ask_question(question, hint)

        # Add spacing between sections (except after last section)
        if section != config['sections'][-1]:
            print()

    # Filter out empty responses
    biographical_context = {k: v for k, v in biographical_context.items() if v}

    print(f"\n{GREEN}✓ Biographical context collected.{RESET}")
    print(f"  Responses provided: {len(biographical_context)}/{total_questions} questions")

    return biographical_context


def _ask_question(question: str, hint: str = None) -> str:
    """
    Ask a single question with optional hint, allow skipping.

    Args:
        question: The question to ask
        hint: Optional hint or examples

    Returns:
        User's response or empty string if skipped
    """
    print(f"{CYAN}{question}{RESET}")
    if hint:
        print(f"   {hint}")

    response = input("   → ").strip()

    if not response:
        print(f"   {YELLOW}(skipped){RESET}")

    return response


def update_subject_biographical_context(subject_file_path: Path, biographical_context: dict) -> bool:
    """
    Update subject's JSON file with biographical context.

    Args:
        subject_file_path: Path to subject's JSON file
        biographical_context: Dictionary of biographical responses

    Returns:
        True if successful, False otherwise
    """
    try:
        # Load existing subject data
        with open(subject_file_path, 'r') as f:
            subject_data = json.load(f)

        # Add or update biographical_context
        subject_data['biographical_context'] = biographical_context

        # Write back to file
        with open(subject_file_path, 'w') as f:
            json.dump(subject_data, f, indent=4)

        print(f"{GREEN}✓ Biographical context saved to {subject_file_path.name}{RESET}\n")
        return True

    except Exception as e:
        print(f"{RED}Error saving biographical context: {e}{RESET}")
        return False


def ask_if_update_biographical_context(subject_name: str) -> bool:
    """
    Ask user if they want to update biographical context.

    Args:
        subject_name: Name of the subject

    Returns:
        True if user wants to update, False otherwise
    """
    print(f"\n{YELLOW}Would you like to provide/update biographical context for {subject_name}?{RESET}")
    print("This helps ground the transit analysis in actual life circumstances.")
    print(f"  1 - Yes, complete the questionnaire")
    print(f"  2 - No, skip (use existing context if available)")

    while True:
        choice = input("→ ").strip()
        if choice == "1":
            return True
        elif choice == "2":
            return False
        else:
            print(f"{RED}Invalid choice. Please enter 1 or 2.{RESET}")


def format_biographical_context_for_prompt(biographical_context: dict) -> str:
    """
    Format biographical context dictionary into a readable string for crew prompts.

    Args:
        biographical_context: Dictionary of biographical responses

    Returns:
        Formatted string suitable for injection into crew task prompts
    """
    if not biographical_context:
        return "No biographical context provided."

    sections = []

    # Map keys to readable labels
    label_map = {
        'life_stage': 'Current Life Stage',
        'developmental_focus': 'Developmental Focus',
        'active_domains': 'Active Life Domains',
        'primary_challenges': 'Primary Challenges',
        'emotional_themes': 'Emotional Themes',
        'inner_tension': 'Internal Tensions',
        'significant_decisions': 'Significant Decisions',
        'major_transitions': 'Major Transitions',
        'recent_history': 'Recent Life History (2-3 years)',
        'specific_focus': 'Specific Areas of Focus'
    }

    for key, value in biographical_context.items():
        label = label_map.get(key, key.replace('_', ' ').title())
        sections.append(f"- **{label}**: {value}")

    return "\n".join(sections)


if __name__ == "__main__":
    # Test the questionnaire
    print("Testing Biographical Questionnaire\n")

    test_name = "Test Subject"
    context = get_biographical_context(test_name)

    print("\n--- Collected Context ---")
    print(json.dumps(context, indent=2))

    print("\n--- Formatted for Prompt ---")
    print(format_biographical_context_for_prompt(context))
