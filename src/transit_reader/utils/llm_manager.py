"""
LLM Manager Module

Centralized management of Language Model configurations for all agents.
Loads LLM configuration from llm_config.yaml and provides LLM instances
for agents based on their assignments.

This module enables easy swapping of LLM providers without modifying crew code.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Optional
from crewai import LLM
from dotenv import load_dotenv

load_dotenv()

# Path to LLM configuration
LLM_CONFIG_PATH = Path(__file__).parent.parent / "config" / "llm_config.yaml"

# Cache for loaded configuration
_config_cache: Optional[Dict] = None


def _load_llm_config() -> Dict:
    """
    Load LLM configuration from YAML file.

    Returns:
        Dictionary containing LLM configuration

    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If YAML is malformed
    """
    global _config_cache

    # Return cached config if available
    if _config_cache is not None:
        return _config_cache

    try:
        with open(LLM_CONFIG_PATH, 'r') as f:
            _config_cache = yaml.safe_load(f)
        return _config_cache
    except FileNotFoundError:
        raise FileNotFoundError(
            f"LLM configuration file not found at {LLM_CONFIG_PATH}. "
            "Please ensure llm_config.yaml exists in src/transit_reader/config/"
        )
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Error parsing LLM configuration: {e}")


def get_llm_for_agent(agent_name: str) -> LLM:
    """
    Get configured LLM instance for a specific agent.

    Args:
        agent_name: Name of the agent (must match key in llm_config.yaml agents section)

    Returns:
        Configured LLM instance

    Raises:
        ValueError: If agent not found in config or provider not configured
        KeyError: If required configuration keys are missing
    """
    config = _load_llm_config()

    # Get agent configuration
    agents = config.get('agents', {})
    if agent_name not in agents:
        raise ValueError(
            f"Agent '{agent_name}' not found in LLM configuration. "
            f"Available agents: {', '.join(agents.keys())}"
        )

    agent_config = agents[agent_name]
    provider_name = agent_config.get('provider')
    temperature_preset = agent_config.get('temperature')

    if not provider_name:
        raise ValueError(f"No provider specified for agent '{agent_name}'")
    if not temperature_preset:
        raise ValueError(f"No temperature preset specified for agent '{agent_name}'")

    # Get provider configuration
    providers = config.get('providers', {})
    if provider_name not in providers:
        raise ValueError(
            f"Provider '{provider_name}' not found in LLM configuration. "
            f"Available providers: {', '.join(providers.keys())}"
        )

    provider_config = providers[provider_name]

    # Get temperature value
    temperatures = config.get('temperatures', {})
    if temperature_preset not in temperatures:
        raise ValueError(
            f"Temperature preset '{temperature_preset}' not found in LLM configuration. "
            f"Available presets: {', '.join(temperatures.keys())}"
        )

    temperature = temperatures[temperature_preset]

    # Build LLM instance based on provider
    return _create_llm_instance(provider_name, provider_config, temperature, agent_name)


def _create_llm_instance(
    provider_name: str,
    provider_config: Dict,
    temperature: float,
    agent_name: str
) -> LLM:
    """
    Create LLM instance based on provider configuration.

    Args:
        provider_name: Name of the provider
        provider_config: Provider configuration dictionary
        temperature: Temperature value
        agent_name: Name of the agent (for error messages)

    Returns:
        Configured LLM instance

    Raises:
        ValueError: If API key is missing or provider is invalid
    """
    model = provider_config.get('model')
    if not model:
        raise ValueError(f"No model specified for provider '{provider_name}'")

    # Handle provider-specific configurations
    llm_kwargs = {
        'model': model,
        'temperature': temperature
    }

    # Get API key if required
    api_key_env = provider_config.get('api_key_env')
    if api_key_env:
        api_key = os.getenv(api_key_env)
        if not api_key:
            raise ValueError(
                f"API key not found for provider '{provider_name}'. "
                f"Please set {api_key_env} in your .env file."
            )
        llm_kwargs['api_key'] = api_key

    # Handle base_url (for Ollama and custom endpoints)
    base_url = provider_config.get('base_url')
    if base_url:
        llm_kwargs['base_url'] = base_url

    # Provider-specific adjustments
    if provider_name.startswith('ollama'):
        # Ollama doesn't require API key
        llm_kwargs.pop('api_key', None)

    try:
        return LLM(**llm_kwargs)
    except Exception as e:
        raise ValueError(
            f"Error creating LLM instance for agent '{agent_name}' "
            f"using provider '{provider_name}': {e}"
        )


def list_available_providers() -> Dict[str, str]:
    """
    List all available LLM providers with their descriptions.

    Returns:
        Dictionary mapping provider names to descriptions
    """
    config = _load_llm_config()
    providers = config.get('providers', {})

    return {
        name: provider.get('description', 'No description')
        for name, provider in providers.items()
    }


def list_agent_assignments() -> Dict[str, Dict[str, str]]:
    """
    List all agents and their LLM assignments.

    Returns:
        Dictionary mapping agent names to their provider and temperature
    """
    config = _load_llm_config()
    agents = config.get('agents', {})

    return {
        name: {
            'provider': agent.get('provider', 'unknown'),
            'temperature': agent.get('temperature', 'unknown'),
            'notes': agent.get('notes', '')
        }
        for name, agent in agents.items()
    }


def get_temperature_presets() -> Dict[str, float]:
    """
    Get all temperature presets defined in configuration.

    Returns:
        Dictionary mapping preset names to temperature values
    """
    config = _load_llm_config()
    return config.get('temperatures', {})


# Legacy compatibility - create preset LLM instances
# These can be imported by crews that haven't been refactored yet
def _create_legacy_llms():
    """Create legacy LLM instances for backward compatibility."""
    try:
        config = _load_llm_config()
        temps = config.get('temperatures', {})

        # Find a gpt provider
        providers = config.get('providers', {})
        gpt_provider = None
        for name, provider in providers.items():
            if name.startswith('gpt') and provider.get('model') == 'gpt-4.1':
                gpt_provider = provider
                break

        if not gpt_provider:
            # Fallback to hardcoded if config fails
            return _create_fallback_llms()

        api_key = os.getenv(gpt_provider.get('api_key_env', 'OPENAI_API_KEY'))

        return {
            'gpt41_deterministic': LLM(
                model=gpt_provider['model'],
                api_key=api_key,
                temperature=temps.get('deterministic', 0.1)
            ),
            'gpt41_creative': LLM(
                model=gpt_provider['model'],
                api_key=api_key,
                temperature=temps.get('creative', 0.9)
            ),
            'gpt41': LLM(
                model=gpt_provider['model'],
                api_key=api_key,
                temperature=temps.get('creative', 0.9)
            )
        }
    except:
        return _create_fallback_llms()


def _create_fallback_llms():
    """Fallback LLM creation if config fails."""
    api_key = os.getenv('OPENAI_API_KEY')
    return {
        'gpt41_deterministic': LLM(model="gpt-4.1", api_key=api_key, temperature=0.1),
        'gpt41_creative': LLM(model="gpt-4.1", api_key=api_key, temperature=0.9),
        'gpt41': LLM(model="gpt-4.1", api_key=api_key, temperature=0.9)
    }


# Create legacy instances
_legacy = _create_legacy_llms()
gpt41_deterministic = _legacy['gpt41_deterministic']
gpt41_creative = _legacy['gpt41_creative']
gpt41 = _legacy['gpt41']


if __name__ == "__main__":
    # Test the LLM manager
    print("Testing LLM Manager\n")

    print("Available Providers:")
    for name, desc in list_available_providers().items():
        print(f"  {name}: {desc}")

    print("\nTemperature Presets:")
    for name, temp in get_temperature_presets().items():
        print(f"  {name}: {temp}")

    print("\nAgent Assignments:")
    for agent, config in list_agent_assignments().items():
        print(f"  {agent}:")
        print(f"    Provider: {config['provider']}")
        print(f"    Temperature: {config['temperature']}")
        if config['notes']:
            print(f"    Notes: {config['notes']}")

    print("\nTesting LLM instantiation for 'current_transits_reader'...")
    try:
        llm = get_llm_for_agent('current_transits_reader')
        print(f"✓ LLM created successfully: {llm.model}")
    except Exception as e:
        print(f"✗ Error: {e}")
