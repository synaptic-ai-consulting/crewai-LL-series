# Lightning Lesson 2: YAML Configuration Guide

## Overview
This guide explains the YAML configuration structure used in Lightning Lesson 2, following CrewAI documentation guidelines for defining agents, tasks, and crews through configuration files.

## Configuration Structure

### 1. Agents Configuration (`config/agents.yaml`)

```yaml
# Agent definitions with persona-specific configurations
agent_name:
  role: "Agent Role Description"
  goal: "Primary goal of the agent"
  backstory: "Detailed background and expertise"
  prompt_file: "path/to/prompt/template.txt"  # Optional
  verbose: true
  allow_delegation: false
  max_iter: 3
  memory: true
```

**Key Features:**
- **Default Agents**: Generic agents using CrewAI's default prompts
- **Persona-Engineered Agents**: Agents with custom prompt templates
- **Flexible Configuration**: All CrewAI agent parameters supported
- **Prompt File Integration**: Custom persona templates via `prompt_file`

### 2. Tasks Configuration (`config/tasks.yaml`)

```yaml
# Task definitions with context and expected outputs
task_name:
  description: "What the task should accomplish"
  expected_output: "Expected deliverable format"
  context: "Additional context and constraints"
  agent: "agent_name"  # Optional - can be assigned to specific agent
```

**Key Features:**
- **Context-Rich Tasks**: Detailed descriptions and expected outputs
- **Agent Assignment**: Tasks can be pre-assigned to specific agents
- **Flexible Structure**: Supports all CrewAI task parameters
- **Demo-Ready**: Tasks designed for Lightning Lesson demonstrations

### 3. Crews Configuration (`config/crews.yaml`)

```yaml
# Crew definitions with agent and task assignments
crew_name:
  agents:
    - "agent_name_1"
    - "agent_name_2"
  tasks:
    - "task_name_1"
    - "task_name_2"
  process: "sequential"  # or "hierarchical"
  verbose: true
  memory: true
```

**Key Features:**
- **Multi-Agent Crews**: Combine multiple personas for complex workflows
- **Task Orchestration**: Define task execution order and dependencies
- **Process Control**: Sequential or hierarchical execution patterns
- **Demo Scenarios**: Pre-configured crews for different demo types

## Configuration Examples

### Agent Configuration Examples

#### Default Marketing Agent
```yaml
default_marketing_agent:
  role: "Marketing Specialist"
  goal: "Create compelling marketing content"
  backstory: "You are a marketing professional who creates content and strategies."
  verbose: true
  allow_delegation: false
  max_iter: 3
  memory: true
```

#### Persona-Engineered Legal Agent
```yaml
legal_compliance_agent:
  role: "Senior Legal Compliance Specialist"
  goal: "Ensure regulatory compliance and mitigate legal risks"
  backstory: "You are a senior legal professional with 15+ years of experience..."
  prompt_file: "prompts/legal_compliance_agent.txt"
  verbose: true
  allow_delegation: false
  max_iter: 3
  memory: true
```

### Task Configuration Examples

#### Marketing Task
```yaml
product_launch_email:
  description: "Write a product launch email for our new AI-powered customer service tool"
  expected_output: "A compelling, brand-aligned product launch email that drives engagement"
  context: "Target audience: B2B SaaS companies, Budget: $50K, Timeline: 2 weeks"
  agent: "creative_marketing_agent"
```

#### Legal Task
```yaml
privacy_policy_review:
  description: "Review our data privacy policy for compliance issues"
  expected_output: "A comprehensive compliance review with identified risks and recommendations"
  context: "Company: Tech startup, Data: User behavior analytics, Jurisdiction: EU + US"
  agent: "legal_compliance_agent"
```

### Crew Configuration Examples

#### Comparison Crew (Before/After Demo)
```yaml
default_marketing_crew:
  agents:
    - "default_marketing_agent"
  tasks:
    - "comparison_email_task"
  process: "sequential"
  verbose: true
  memory: true

persona_marketing_crew:
  agents:
    - "creative_marketing_agent"
  tasks:
    - "comparison_persona_task"
  process: "sequential"
  verbose: true
  memory: true
```

#### Multi-Persona Crew
```yaml
multi_persona_crew:
  agents:
    - "legal_compliance_agent"
    - "creative_marketing_agent"
    - "technical_lead_agent"
  tasks:
    - "product_launch_email"
    - "privacy_policy_review"
    - "microservices_architecture"
  process: "sequential"
  verbose: true
  memory: true
```

## Configuration Management

### Loading Configurations
```python
from src.agents import LightningLesson2Agents

# Create agents manager with YAML configurations
agents_manager = LightningLesson2Agents("config")

# Get available configurations
agents = agents_manager.get_available_agents()
tasks = agents_manager.get_available_tasks()
crews = agents_manager.get_available_crews()

# Create agents from configuration
agent = agents_manager.factory.create_agent("legal_compliance_agent")
crew = agents_manager.factory.create_crew("multi_persona_crew")
```

### Configuration Validation
```python
# Validate all configurations
validation_results = agents_manager.validate_configurations()

if validation_results["errors"]:
    print("Configuration errors found:")
    for error in validation_results["errors"]:
        print(f"  - {error}")

if validation_results["warnings"]:
    print("Configuration warnings:")
    for warning in validation_results["warnings"]:
        print(f"  - {warning}")
```

### Dynamic Configuration Updates
```python
from src.config_loader import ConfigLoader

config_loader = ConfigLoader("config")

# Save new agent configuration
new_agent_config = {
    "role": "Data Analyst",
    "goal": "Analyze data and provide insights",
    "backstory": "Expert in data analysis and visualization"
}

config_loader.save_config("agents", "data_analyst_agent", new_agent_config)
```

## Best Practices

### 1. Agent Configuration
- **Clear Roles**: Define specific, actionable roles
- **Detailed Backstories**: Provide rich context for persona consistency
- **Prompt Files**: Use custom prompt templates for persona-engineered agents
- **Consistent Parameters**: Maintain consistent verbose, memory, and iteration settings

### 2. Task Configuration
- **Specific Descriptions**: Clear, actionable task descriptions
- **Expected Outputs**: Define deliverable format and quality standards
- **Rich Context**: Provide business context and constraints
- **Agent Assignment**: Pre-assign tasks to appropriate agents when possible

### 3. Crew Configuration
- **Logical Groupings**: Group agents and tasks that work well together
- **Process Selection**: Choose appropriate execution patterns (sequential vs hierarchical)
- **Demo Scenarios**: Create crews specifically for demonstration purposes
- **Scalability**: Design crews that can handle different task combinations

### 4. File Organization
- **Separate Files**: Keep agents, tasks, and crews in separate YAML files
- **Consistent Naming**: Use descriptive, consistent naming conventions
- **Version Control**: Track configuration changes in version control
- **Documentation**: Document complex configurations and their purposes

## Demo Integration

### Lightning Lesson 2 Demo Commands
```bash
# List all available configurations
python run_demo.py --list-configs

# Validate configurations
python run_demo.py --validate

# Run specific crew
python run_demo.py --crew "creative_marketing_crew"

# Run with specific task
python run_demo.py --task "product_launch_email"

# Run comparison demo
python run_demo.py --comparison

# Run persona showcase
python run_demo.py --showcase
```

### Configuration-Driven Demo Flow
1. **Load Configurations**: Read YAML files for agents, tasks, and crews
2. **Validate Setup**: Check for missing files, invalid references, and configuration errors
3. **Create Instances**: Instantiate agents, tasks, and crews from configurations
4. **Execute Demo**: Run configured scenarios for demonstration
5. **Capture Results**: Save demo outputs and analysis

## Troubleshooting

### Common Issues
1. **Missing Prompt Files**: Ensure prompt files exist and are accessible
2. **Invalid References**: Check that agent/task references in crews are valid
3. **YAML Syntax**: Validate YAML syntax and indentation
4. **File Permissions**: Ensure configuration files are readable

### Debug Commands
```bash
# Validate configurations
python run_demo.py --validate

# Test specific configuration
python test_demo.py

# Check file structure
python -c "from src.agents import LightningLesson2Agents; print(LightningLesson2Agents().get_available_agents())"
```

## Migration from Python Scripts

### Before (Python-based)
```python
# Old approach - hardcoded in Python
agent = Agent(
    role="Marketing Specialist",
    goal="Create compelling marketing content",
    backstory="You are a marketing professional...",
    prompt_file="prompts/marketing_agent.txt"
)
```

### After (YAML-based)
```yaml
# New approach - configuration-driven
creative_marketing_agent:
  role: "Creative Marketing Specialist"
  goal: "Create compelling, brand-aligned marketing strategies"
  backstory: "You are a creative marketing professional..."
  prompt_file: "prompts/creative_marketing_agent.txt"
  verbose: true
  allow_delegation: false
  max_iter: 3
  memory: true
```

### Benefits of YAML Configuration
- **Separation of Concerns**: Configuration separate from code
- **Easy Modification**: Change behavior without code changes
- **Version Control**: Track configuration changes independently
- **Reusability**: Share configurations across projects
- **Validation**: Built-in configuration validation
- **CrewAI Standard**: Follows official CrewAI documentation guidelines

---

This YAML configuration approach provides a flexible, maintainable, and standards-compliant way to manage CrewAI agents, tasks, and crews for the Lightning Lesson 2 demo.
