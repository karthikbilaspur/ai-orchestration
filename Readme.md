# AI Orchestration Lab

A collection of 11 beginner-friendly Python projects that demonstrate
how to build practical AI-powered workflows using multi-agent
orchestration, LLMs, Python tools, rule-based decision-making, and
external APIs.

> Learn by building: turn natural-language requests into structured
> data, coordinate specialized agents, execute reliable Python logic,
> and generate useful outputs.

 About

AI Orchestration Lab is a hands-on learning repository focused on
the fundamentals of AI agents and workflow orchestration. Instead of
relying on one large prompt to do everything, the projects split tasks
into smaller, focused components---such as extraction, classification,
decision-making, calculation, and response generation.

The examples cover sequential, conditional, and parallel agent
workflows, as well as LLM-to-tool patterns and integrations with
external services. Most projects include sample inputs, logging, and
tests to help learners understand and experiment with the
implementation.

 Projects

  --------------------------------------------------------------------------------
                     \ Project          What it does          Main concepts
                      1 E-Commerce     Processes customer    Sequential agents,
                        Support          messages, identifies  intent detection,
                        Orchestrator   intent, retrieves     escalation
                                         mock order            
                                         information, and      
                                         drafts a support      
                                         response.             

                      2 AI Email       Reads and classifies  Multi-agent
                        Assistant      customer emails,      workflow,
                                         recommends an action, confidence checks,
                                         and prepares a reply  human-in-the-loop
                                         for human approval.   

                      3 Expense &      Parses employee       Rule-based
                        Policy Checker expense claims and    decisions,
                                         applies deterministic validation,
                                         policy rules to       auditability
                                         approve, reject, or   
                                         escalate them.        

                      4 AI Expense     Converts a            LLM parsing, Python
                        Split & Tip      natural-language      tools, Streamlit
                        Calculator     bill-splitting        
                                         request into          
                                         structured inputs and 
                                         calculates the final  
                                         share.                

                      5 AI Expense     Demonstrates a        LLM-style parsing,
                        Splitter       command-line          tool execution, CLI
                                         expense-splitting     
                                         workflow with         
                                         parsing, calculation, 
                                         and explanation       
                                         stages.               

                      6 Job            Extracts candidate    Conditional
                        Application      skills, checks        orchestration,
                        Screener       mandatory             structured
                                         requirements, and     extraction
                                         scores a resume       
                                         against a job         
                                         description.          

                      7 Personal       Runs independent      Parallel agents,
                        Meeting Brief    meeting-preparation   threading, result
                        Assistant      tasks in parallel and merging
                                         merges their results  
                                         into a concise brief. 

                      8 AI Recipe      Scales ingredient     Structured
                        Scaler & Grocery quantities for a new  extraction,
                        List Maker     serving size and      deterministic
                                         creates a grocery     calculations
                                         list.                 

                      9 AI Smart       Converts              LLM planning, tool
                        Calculator     plain-English math    calling, input
                                         requests into         validation
                                         validated operations  
                                         executed by a Python  
                                         calculator.           

                     10 AI Travel Time Estimates travel time Gemini integration,
                        & Budget         and cost from         calculation,
                        Estimator      user-provided trip    fallback parsing
                                         details and transport 
                                         assumptions.          

                     11 AI Weather     Uses weather          API integration,
                        Outfit Planner information and       recommendation
                                         activity context to   rules, fallback
                                         suggest clothing and  mode
                                         rain preparation.     
  --------------------------------------------------------------------------------

 Orchestration patterns covered

 1. Sequential orchestration

Agents run one after another, with each stage using the previous stage's
output.

`Input → Extract → Classify → Decide → Respond`

Examples: E-Commerce Support Orchestrator and AI Email Assistant.

 2.Conditional orchestration

The workflow checks conditions and decides whether to continue, branch,
or stop early.

`Input → Extract → Validate → Continue / Escalate / Stop`

Example: Job Application Screener.

 3.Parallel orchestration

Independent tasks run at the same time, and their results are combined.

`Request → Agent A + Agent B → Merge → Final result`

Example: Personal Meeting Brief Assistant.

 4.LLM + Python tool execution

The LLM interprets a request or creates a structured plan, while Python
performs calculations and other deterministic operations.

`Natural language → Structured plan → Python tool → Explanation`

Examples: Smart Calculator, Recipe Scaler, and Expense Splitter.

 5 LLM + external API workflow

The application extracts the required parameters, retrieves external
data, applies application logic, and presents the result.

Examples: Travel Estimator and Weather Outfit Planner.

 Tech stack

- Language: Python
- LLM integrations: Anthropic Claude, Google Gemini, and
- OpenAI-compatible configuration in selected projects
- User interface: Command-line applications and Streamlit
- Data formats: JSON, CSV, and plain text
- HTTP/API integration: Requests and project-specific API clients
- Testing: pytest and project-specific test scripts
- Core techniques: Prompting, structured output, regex extraction,
    validation, rule-based logic, threading, logging, and fallback
    handling

> Dependencies and API providers differ by project. Check the
> `requirements.txt` and README inside the project you want to run.

 Repository structure

ai-orchestration-main/
├── beginner/
│   ├── ecommerce-support-orchestrator/
│   ├── email-assistant/
│   ├── expense-policy-checker/
│   ├── expense-split/
│   ├── expense-splitter/
│   ├── job-application-screener/
│   ├── meeting-brief-assistant/
│   ├── recipe-scaler/
│   ├── smart-calculator/
│   ├── travel-estimator/
│   └── weather-outfit-planner/
├── LICENSE
└── README.md

Each project is self-contained and may have its own agents, tools,
prompts, configuration, sample data, output folder, and tests.

 Getting started

 Prerequisites

- Python 3.9 or newer (check the selected project's documentation for its exact requirement)
Git
- API key only if the selected project and mode require a live LLM or
    external service

 1. Clone the repository

bash
git clone <https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git>
cd YOUR-REPOSITORY

Replace the placeholders with your GitHub username and repository name.

 2.Choose a project

For example:

cd beginner/smart-calculator

 3 Create and activate a virtual environment

bash
python -m venv .venv

Windows PowerShell

powershell
.venv\Scripts\Activate.ps1

macOS / Linux

bash
source .venv/bin/activate

 4 Install that project's dependencies

bash
pip install -r requirements.txt

 5.Configure API keys if required

Use the environment variable names documented by the selected project.
For example:

bash
 macOS / Linux
export ANTHROPIC_API_KEY="your-api-key"

powershell
 Windows PowerShell
$env:ANTHROPIC_API_KEY="your-api-key"

Some projects support mock, rule-based, or offline fallback modes and
can be explored without an API key. Consult their individual README
files for details.

 6.Run the project

The command depends on the project. Common examples include:

bash
python main.py

or, for the Streamlit expense-splitting interface:

bash
streamlit run app.py

 7.Run tests

Where pytest is configured:

bash
pytest -v

Some projects provide their own test commands. Refer to the
project-level README.

 Learning outcomes

By exploring this repository, you can practise how to:

- Design small, specialized agents with clear responsibilities.
- Pass structured data between workflow stages.
- Choose between sequential, conditional, and parallel execution.
- Use LLMs for language understanding while keeping calculations and critical rules in Python.
- Validate model-generated output before using it.
- Integrate external APIs and provide fallback behaviour.
- Add logging, tests, and human approval steps.
- Organize a small AI application into maintainable modules.

 Important notes

- These are educational/demo projects, not production-ready services.
- Some integrations use mock data, sample profiles, simulated parsing,  or fallback logic. Verify the project documentation before assuming
a live integration is enabled.
- Travel costs and times are estimates based on supplied assumptions; they are not guaranteed live fares or traffic predictions.
- The e-commerce tracking example uses sample/mock tracking data.
- The email assistant prepares a draft and approval flow; its send  step is a placeholder and does not send a real email.
- Resume screening, expense decisions, and customer-service actions should have appropriate human review before real-world use.
- Never commit API keys, passwords, personal data, or `.env` files.
    Use environment variables and keep secrets out of Git.

 Contributing

Contributions, bug reports, and learning improvements are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Make a focused change and add or update tests where appropriate.
4. Run the relevant tests.
5. Open a pull request describing the change.

 License

This repository includes an MIT License. See [LICENSE](LICENSE) for the
full terms.

 Topics

Suggested GitHub repository topics:

`ai-orchestration` `ai-agents` `multi-agent-systems` `agentic-ai` `llm`
`python` `generative-ai` `llm-applications` `prompt-engineering`
`tool-calling` `workflow-automation` `anthropic` `gemini` `streamlit`
`beginner-projects`

If this repository helps you learn, consider giving it a star ⭐ and
sharing what you build with it.
