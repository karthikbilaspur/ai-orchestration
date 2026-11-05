# AI Email Assistant

A beginner-friendly multi-agent AI workflow for an online laptop store. It reads a customer email, classifies it, decides the next step based on store policy, and drafts a reply. A human approves the reply before anything is sent.

## Workflow

Incoming Email
      |
Email Reader      extracts order ID, price, issue, request, urgency
      |
Classifier        delivery / refund / damage / product_enquiry / other
      |           (confidence < 0.7 -> stop and send to a human)
Problem Solver    checks store policy, recommends next step
      |
Reply Writer      drafts a polite reply
      |
Human approves -> Reply sent

Each agent receives the previous agent's JSON output as its input. The orchestrator (`main.py`) connects them.

## Project structure

ai_email_assistant/
├── main.py               # orchestrator: runs agents, error check, human approval
├── agents/
│   ├── llm.py            # shared helper that calls the model and returns JSON
│   ├── email_reader.py   # Agent 1
│   ├── classifier.py     # Agent 2
│   ├── problem_solver.py # Agent 3
│   └── reply_writer.py   # Agent 4
├── sample_emails.json    # test emails
├── log.txt               # all four prompts, in one place
├── run_log.txt           # created on first run: every step's output
├── requirements.txt
└── README.md

## Requirements

- Python 3.9 or newer
- An Anthropic API key (get one at https://console.anthropic.com). API usage is billed separately from a Claude.ai chat subscription.

## Setup

1. Open a terminal inside the project folder:
   cd ai_email_assistant  

2. Install the dependency:

   pip install -r requirements.txt

3. Set your API key (once per terminal window):
   - Windows (Command Prompt): `set ANTHROPIC_API_KEY=your_key_here`
   - Windows (PowerShell): `$env:ANTHROPIC_API_KEY="your_key_here"`
   - Mac/Linux: `export ANTHROPIC_API_KEY=your_key_here`

## Run

python main.py        # email 0: damaged laptop
python main.py 1      # email 1: delivery problem
python main.py 2      # email 2: vague email (should trigger human fallback)

You will see each agent's output, then the draft reply, then:

Send this reply? (y/n):

Type `y` to approve or `n` to reject. Nothing is actually emailed; the send step is a placeholder.

## Example output (damaged laptop)

Email Reader  -> order_id: #45821, price: ₹65,000, request: Replacement, urgency: high
Classifier    -> category: damage, confidence: 0.97
Problem Solver-> recommend replacement once damage photo is verified, needs_human: true
Reply Writer  -> asks the customer for a photo, does not promise a replacement yet

## Safety checks built in

- **Confidence check:** if the Classifier's confidence is below 0.7, the pipeline stops and the email goes to a human. This limits the damage if the Classifier mislabels an email (for example, damage as delivery).
- **Policy rules:** the Problem Solver only recommends actions. It never promises a refund or replacement.
- **Human approval:** the Reply Writer only drafts. A person must approve before sending.

## Adding your own emails

Edit `sample_emails.json` and add an entry:

json
{
  "sender": "you@example.com",
  "subject": "Subject here",
  "body": "Email text here."
}

Then run `python main.py 3` (the number is the position in the list, starting from 0).

## Changing the prompts

Each prompt lives inside its agent file in `agents/`. `log.txt` is a readable copy of the prompts for reference. If you edit a prompt in the code, update `log.txt` too.

## Troubleshooting

| Problem | Fix |

|---|---|
| `ModuleNotFoundError: anthropic` | Run `pip install -r requirements.txt` |
| Authentication error | Set `ANTHROPIC_API_KEY` again in the same terminal window |
| `Agent did not return valid JSON` | Run again; the model occasionally adds extra text |
| Model not found error | Check the model name in `agents/llm.py` |

## Ideas for next steps

- Connect to a real inbox (Gmail API) instead of `sample_emails.json`
- Replace the `y/n` prompt with a real send step
- Add a product catalog lookup for the Problem Solver
- Add automated tests for each agent
