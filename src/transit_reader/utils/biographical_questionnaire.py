"""
Biographical Questionnaire Module

Collects voluntary, targeted biographical context to ground astrological interpretations
in the subject's actual life circumstances. Based on the methodology of respected
astrologers like Liz Greene, Dane Rudhyar, Stephen Arroyo, and others who emphasize
grounding symbolic patterns in developmental tasks, active life arenas, emotional tone,
choices under pressure, and long-term narrative arcs.

All questions are optional. Subjects can skip any question or the entire questionnaire.
"""

import json
from pathlib import Path

# ANSI color codes
CYAN = "\033[96m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
RESET = "\033[0m"


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

    print(f"\n{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f"{CYAN}         Biographical Context Questionnaire{RESET}")
    print(f"{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}\n")

    print(f"This optional questionnaire helps ground the transit analysis in {subject_name}'s")
    print("actual life circumstances, developmental stage, and current challenges.")
    print(f"\n{YELLOW}All questions are optional. Press Enter to skip any question.{RESET}\n")

    biographical_context = {}

    # Section 1: Life Stage & Developmental Tasks
    print(f"{GREEN}━━━ Life Stage & Development ━━━{RESET}\n")

    biographical_context['life_stage'] = _ask_question(
        "1. What phase of life are you currently in?",
        "   (e.g., student, early career, established career, major transition, retirement, etc.)"
    )

    biographical_context['developmental_focus'] = _ask_question(
        "2. What are you actively building, developing, or releasing in your life right now?",
        "   (e.g., new career path, ending relationship, establishing home, spiritual practice, etc.)"
    )

    # Section 2: Active Life Arenas
    print(f"\n{GREEN}━━━ Active Life Domains ━━━{RESET}\n")

    biographical_context['active_domains'] = _ask_question(
        "3. Which life domains feel most active or demanding of your attention?",
        "   (e.g., career, intimate relationships, family, health, finances, spirituality, creativity, etc.)"
    )

    biographical_context['primary_challenges'] = _ask_question(
        "4. What are the primary challenges or obstacles you're navigating?",
        "   (Be as specific or general as feels comfortable)"
    )

    # Section 3: Emotional & Psychological Climate
    print(f"\n{GREEN}━━━ Emotional & Psychological Tone ━━━{RESET}\n")

    biographical_context['emotional_themes'] = _ask_question(
        "5. What emotional themes or psychological patterns have been recurring lately?",
        "   (e.g., restlessness, grief, enthusiasm, anxiety, empowerment, confusion, etc.)"
    )

    biographical_context['inner_tension'] = _ask_question(
        "6. What internal tensions, conflicts, or paradoxes are you working with?",
        "   (e.g., security vs. freedom, ambition vs. rest, independence vs. intimacy, etc.)"
    )

    # Section 4: Choices Under Pressure
    print(f"\n{GREEN}━━━ Decisions & Crossroads ━━━{RESET}\n")

    biographical_context['significant_decisions'] = _ask_question(
        "7. Are you facing any significant decisions or life crossroads at this time?",
        "   (If yes, describe the nature of the decision without needing to reveal specifics)"
    )

    # Section 5: Long-term Narrative Arcs
    print(f"\n{GREEN}━━━ Long-term Context & Transitions ━━━{RESET}\n")

    biographical_context['major_transitions'] = _ask_question(
        "8. What major life transitions are currently underway or approaching?",
        "   (e.g., career change, relocation, relationship shift, identity evolution, etc.)"
    )

    biographical_context['recent_history'] = _ask_question(
        "9. Looking back 2-3 years, what significant changes have shaped your current situation?",
        "   (This helps contextualize current transits within your recent developmental arc)"
    )

    # Section 6: Specific Intentions
    print(f"\n{GREEN}━━━ Focus & Intentions ━━━{RESET}\n")

    biographical_context['specific_focus'] = _ask_question(
        "10. Is there anything specific you'd like this transit analysis to address or explore?",
        "    (Optional: areas of particular interest or concern)"
    )

    # Filter out empty responses
    biographical_context = {k: v for k, v in biographical_context.items() if v}

    print(f"\n{GREEN}✓ Biographical context collected.{RESET}")
    print(f"  Responses provided: {len(biographical_context)}/10 questions")

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
        print(f"{hint}")

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
        print(f"\033[91mError saving biographical context: {e}{RESET}")
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
            print(f"\033[91mInvalid choice. Please enter 1 or 2.{RESET}")


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
