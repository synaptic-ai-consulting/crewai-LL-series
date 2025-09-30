# Lightning Lesson 2: CrewAI Prompt Customization & Persona Architecture

## Overview
This demo showcases CrewAI's prompt injection system and advanced prompt customization techniques, demonstrating how to gain full control over what's sent to your LLM and create branded, enterprise-ready solutions.

## Key Concepts Demonstrated
- **CrewAI Prompt Injection**: What CrewAI automatically injects into prompts (transparency)
- **Multiple Customization Approaches**: Custom templates, crew-level JSON, model-specific formatting
- **Enterprise Persona Types**: Legal, Marketing, and Technical personas with distinct characteristics

Note: A full live session recording that walks through these concepts is available here: [Advanced Prompt Engineering & Agent Personas](https://maven.com/p/c5faf1/advanced-prompt-engineering-agent-personas).

## Project Structure
```
LL2/
├── config/                           # YAML configuration files (CrewAI standard)
│   ├── agents.yaml                   # Agent definitions and configurations
│   ├── tasks.yaml                    # Task definitions and scenarios
│   └── crews.yaml                    # Crew definitions and workflows
├── prompts/                          # Prompt customization files
│   ├── legal_compliance_agent.txt    # System template for legal persona
│   ├── creative_marketing_agent.txt  # System template for marketing persona
│   ├── technical_lead_agent.txt      # System template for technical persona
│   └── custom_prompts.json           # Crew-level JSON customization
├── src/                              # Source code
│   ├── agents.py                     # YAML-based agent factory
│   ├── config_loader.py              # YAML configuration loader
│   └── demo_runner.py                # Demo execution logic
├── artifacts/                        # Demo results and outputs
├── requirements.txt                  # Python dependencies
├── env.example                       # Environment variables template
└── run_demo.py                       # Main demo runner script
```

## Quick Start

### 1. Setup Environment
```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp env.example .env

# Edit .env with your OpenAI API key
OPENAI_API_KEY=your_api_key_here
```

### 2. Run Demo
```bash
# Run full demo (all customization approaches)
python run_demo.py

# Run prompt inspection demo only
python run_demo.py --prompt-inspection

# Run customization approaches demo only
python run_demo.py --customization

# Run before/after comparison only
python run_demo.py --comparison

# Run persona showcase only
python run_demo.py --showcase

# Run with specific task from config
python run_demo.py --task "product_launch_email"

# Run specific crew
python run_demo.py --crew "creative_marketing_crew"

# List available configurations
python run_demo.py --list-configs

# Validate YAML configurations
python run_demo.py --validate
```

## Demo Components

### 1. CrewAI Prompt Injection Demo
Demonstrates how CrewAI framework modifies propmpt injections in specific agent configurations
- **Default Agent**: Shows what CrewAI automatically injects
- **Tools-Using Agent**: Shows tool-aware injection behavior
- **Key Insight**: CrewAI injects instructions you might not know about

### 2. Prompt Customization Approaches
```
CrewAI Prompt Customization Options
├── Crew-Level Customization (prompt_file JSON)
├── Custom Templates (system_template)
└── Model-Specific Templates (Llama 3.3, etc.)
```

### 3. Enterprise Persona Types

#### Legal Compliance Agent
- **Characteristics**: Conservative, thorough, cites sources
- **Use Cases**: Compliance reviews, risk assessment, regulatory guidance
- **Key Behaviors**: Always cites regulations, asks probing questions, provides disclaimers

#### Creative Marketing Agent
- **Characteristics**: Bold, trend-aware, brand-aligned
- **Use Cases**: Campaign strategy, content creation, brand positioning
- **Key Behaviors**: Uses action-oriented language, focuses on emotional connection, references trends

#### Technical Lead Agent
- **Characteristics**: Precise, security-focused, solution-oriented
- **Use Cases**: Architecture design, security reviews, technical planning
- **Key Behaviors**: Considers security implications, provides detailed specifications, focuses on scalability

## Sample Tasks

### Marketing Tasks
- "Write a product launch email for our new AI tool"
- "Create a viral marketing campaign for our mobile app"
- "Design a brand positioning strategy for our B2B SaaS product"

### Legal Tasks
- "Review our data privacy policy for compliance issues"
- "Draft a data processing agreement for our EU customers"
- "Assess the legal implications of our new AI feature"

### Technical Tasks
- "Design a microservices architecture for our e-commerce platform"
- "Architect a real-time chat system for our platform"
- "Create a disaster recovery plan for our cloud infrastructure"

### Before/After Comparison
- **Default Agent**: Generic responses using CrewAI's defaults 
- **Persona Agent**: Brand-aligned, professional responses using custom templates
- **Key Insight**: Dramatic quality difference in professional output

## Key Learning Outcomes

### Immediate Takeaways
- Understanding of CrewAI's automatic prompt injection
- Multiple crew behavior customization approaches
- Maintaining brand-aligned responses with enterprise agent personas


## Implementation Details

### Prompt Inspection and Transparency
You can use the Prompts utility to verify the prompt that is actually sent to the LLM

```python
from crewai.utilities.prompts import Prompts

# Inspect what CrewAI actually sends to LLM
prompt_generator = Prompts(
    agent=agent,
    has_tools=len(agent.tools) > 0,
    use_system_prompt=agent.use_system_prompt
)

generated_prompt = prompt_generator.task_execution()

print("System Prompt:", generated_prompt["system"])
print("User Prompt:", generated_prompt["user"])
```


### CrewAI Prompt Customization Approaches

#### 1. Crew-Level Customization (JSON prompt_file)
```python
# Crew with JSON prompt customization
crew = Crew(
    agents=[agent],
    tasks=[task],
    prompt_file="prompts/custom_prompts.json"  # JSON format
)
```

#### 2. Custom Templates (system_template, prompt_template)
```python
# Custom system template
system_template = """You are {role}. {backstory}
Your goal is: {goal}

Respond naturally and conversationally. Focus on providing helpful, accurate information."""

# Custom prompt template  
prompt_template = """Task: {input}

Please complete this task thoughtfully."""

agent = Agent(
    role="Research Assistant",
    goal="Help users find accurate information",
    backstory="You are a helpful research assistant.",
    system_template=system_template,
    prompt_template=prompt_template,
    use_system_prompt=True
)
```

#### 3. Model-Specific Templates (Llama 3.3)
```python
# Llama 3.3 specific formatting
system_template = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>{{ .System }}<|eot_id|>"""
prompt_template = """<|start_header_id|>user<|end_header_id|>{{ .Prompt }}<|eot_id|>"""
response_template = """<|start_header_id|>assistant<|end_header_id|>{{ .Response }}<|eot_id|>"""
```


### Enterprise Agents Personas Demo
Demonstrates side-by-side responses from enterprise personas (Legal, Marketing, Technical) on the same task to highlight tone, focus, and expertise differences.

```python
from src.demo_runner import LightningLesson2Demo

# Run the persona showcase (uses --task if provided, otherwise a default task)
demo = LightningLesson2Demo()
demo.run_persona_showcase()
```

#### Where persona behaviors come from (prompt templates)
Persona-specific behaviors are defined in prompt files under `prompts/` and referenced from YAML. The agent factory loads these templates at runtime.

```yaml
# config/agents.yaml (excerpt)
legal_compliance_agent:
  system_template: "prompts/legal_compliance_agent.txt"

creative_marketing_agent:
  system_template: "prompts/creative_marketing_agent.txt"

technical_lead_agent:
  system_template: "prompts/technical_lead_agent.txt"
```

```python
# src/agents.py (excerpt)
agent_config = self.config_loader.get_agent_config(agent_name)
system_template = agent_config.get("system_template")

# Load custom templates from files if specified
if system_template and system_template.endswith('.txt'):
    system_template = self._load_template_file(system_template)

def _load_template_file(self, template_path: str) -> str:
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read().strip()
```


## Expected Demo Results

### CrewAI Prompt Injection Demo
- **Default Agent**: Shows what CrewAI automatically injects
- **Tools-Using Agent**: Shows tool-aware injection behavior
- **Key Insight**: CrewAI injects instructions you might not know about

### Prompt Customization Approaches Demo
- **Crew-Level JSON**: JSON-based prompt management
- **Custom Templates**: Full control over agent behavior
- **Model-Specific**: Optimized formatting for specific models

### Before/After Comparison Enterprise agents personas
- **Default Agent**: Generic, ChatGPT-like responses
- **Customized Agent**: Brand-aligned, professional tone with full control
- **Key Insight**: Dramatic quality difference with proper customization

### Enterprise Agents Personas Demo
- **Legal Persona**: Compliance-first tone; cites regulations and risks
- **Marketing Persona**: Brand-aligned, audience-focused, action-oriented
- **Technical Persona**: Precise, architecture- and security-focused
- **Key Insight**: Same task yields persona-specific tone and structure

## Troubleshooting

### Common Issues
1. **API Key Not Set**: Ensure `OPENAI_API_KEY` is set in `.env` file
2. **Import Errors**: Make sure all dependencies are installed
3. **Template File Not Found**: Ensure template files are in the correct `prompts/` directory
4. **Prompt Inspection Errors**: Check that CrewAI utilities are properly imported

### Debug Mode
Set `CREWAI_VERBOSE=True` in your `.env` file for detailed logging.


## Related Resources
- [CrewAI Documentation](https://docs.crewai.com/)
- [CrewAI Prompt Customization Guide](https://docs.crewai.com/en/guides/advanced/customizing-prompts)
- [Llama 3.1 Prompt Template](https://www.llama.com/docs/model-cards-and-prompt-formats/llama3_1/#prompt-template)
- [Live session recording: Advanced Prompt Engineering & Agent Personas](https://maven.com/p/c5faf1/advanced-prompt-engineering-agent-personas)

---

**Note**: This demo is designed for educational purposes and showcases CrewAI's prompt customization capabilities from Lightning Lesson 2. For production use, ensure proper error handling, security considerations, and performance optimization. Always inspect what prompts are being sent to your LLM for full transparency.
