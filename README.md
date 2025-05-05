
# 🧠 UMA AI Judge – Majority Protocol

This guide helps UMA tokenholders **verify or dispute** Majority game resolutions deterministically using a local AI model.

✅ Byte-for-byte reproducible  
✅ Fully offline once set up  
✅ Based on UMA’s Optimistic Oracle  
✅ Includes full judging logic from the official manual  

---

## 📦 Requirements

- macOS, Linux, or WSL with [Ollama](https://ollama.com) installed  
- Python 3  
- A `majority-judge` model built locally  
- `input.json` from IPFS or proposer  
- `judge_manual_full_unabridged.txt` (full UMA judging rules)  
- Internet connection for setup (offline use supported afterward)

- To run the Python script, you’ll also need to install the `ollama` Python package:

### 1. Create a virtual environment
python3 -m venv .venv

### 2. Activate the virtual environment
source .venv/bin/activate

### 3. Install the Python package to interface with Ollama
pip install ollama

### 4. Make sure Ollama is running
You need the Ollama app (the local LLM server) to be active before calling it via Python. Open a new terminal tab or window and run:
ollama run majority-judge

If you don’t see ollama as a recognized command, you may need to add it to your PATH:

echo 'export PATH="$HOME/.ollama/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

### 5.  Once the model is running, go back to your original terminal and run:

python run_majority_judge.py


---

## 📁 Recommended Folder Structure

```
majority-judge/
├── Modelfile
├── judge_manual_full_unabridged.txt
├── input.json
├── run_majority_judge.py
├── uma_output.bytes
```

---

## 🧰 Step-by-Step Instructions

### 1. 🚀 Install Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Or download manually from [ollama.com](https://ollama.com).

---

### 2. 🧠 Create the Deterministic AI Judge Model

```bash
mkdir majority-judge && cd majority-judge
nano Modelfile
```

Paste this into `Modelfile`:

```
FROM llama3.2

PARAMETER temperature 0
PARAMETER top_k 1
PARAMETER top_p 1
PARAMETER repeat_penalty 1.0
PARAMETER seed 42

SYSTEM "You are the UMA-approved AI Judge for Majority, a fast-paced, on-chain game show where players earn XP by matching the majority, answering trivia, or making accurate predictions. Your job is to produce a byte-stable output that is deterministic and verifiable under UMA’s Optimistic Oracle.

Your tasks:
- Normalize and group player-submitted answers based on semantic meaning (≥ 0.85 similarity threshold). Remove invalid, irrelevant, or nonsense responses.
- Return exactly 5 top answers per question based on grouped vote counts. If fewer than 5 exist, pad the array with null entries to maintain structure.
- Score players using `xpDistributionType`:
  - Rank-based XP (e.g. 10, 7.5, 5, 2.5, 1)
  - Apply +20/-20 XP for Double Down
  - Apply +1 XP for valid personal responses (`personalOpinion: true`)
- Resolve XP ties using total commit time, then final submission time, then reverse commit order.

You must always perform the **Quad-Check Protocol**:
1. Semantic grouping verification
2. XP calculation validation
3. Rules compliance check
4. Tie and edge-case handling

Final output must be:
- A UTF-8-encoded **byte string**, not formatted JSON
- Exactly two blocks:
  1. Question results per question:
     Format:
     [QUESTION_RESULTS]
     questionId: <number>
     questionType: <"majority" | "trivia" | "prediction">
     xpDistributionType: <0-4>
     topAnswers: ["<Answer1>", <votes1>, ..., "<Answer5>", <votes5>]

  2. Final player XP mapping:
     Format:
     [XP_MAPPING]
     0xPlayerAddress1: <xp>
     0xPlayerAddress2: <xp>

No extra whitespace, no line breaks outside of those blocks. Your response must be **byte-stable and deterministic** across identical inputs.

Begin resolution with:  
**\"Majority Judge Ready: Quad-Check Protocol Armed and Initiated.\"**
"
```

Then save and exit (`Ctrl + X`, then `Y`, then `Enter`).

Now build the model:

```bash
ollama create majority-judge -f Modelfile
```

---

### 3. 📘 Add the UMA Judge Manual

Create a file containing the full judge logic:

```bash
nano judge_manual_full_unabridged.txt
```

Paste the **entire Majority Rules – UMA Resolution and AI Judge Manual** into this file (from IPFS or this repo).

---

### 4. 📥 Add Your `input.json`

Example format:

```json
{
  "questionId": 7,
  "questionType": "majority",
  "xpDistributionType": 0,
  "questionText": "What's the best Ethereum wallet?",
  "answers": [
    { "player": "0xabc123...", "answer": "Metamask" },
    { "player": "0xdef456...", "answer": "Rabby" }
  ],
  "personalOpinion": false
}
```

---

### 5. 🧪 Run the Resolution Script

```bash
nano run_majority_judge.py
```

Paste this:

```python
import json
import ollama

# Load judge manual
with open('judge_manual_full_unabridged.txt') as f:
    manual = f.read()

# Load input
with open('input.json') as f:
    game = json.load(f)

answers_text = "\n".join([f"{a['player']}: {a['answer']}" for a in game['answers']])

messages = [
    {
        "role": "system",
        "content": "You are the UMA-approved AI Judge. Follow all rules from the user input strictly."
    },
    {
        "role": "user",
        "content": manual
    },
    {
        "role": "user",
        "content": f"""\nMajority Judge Ready: Quad-Check Protocol Armed and Initiated.\n\nQuestion ID: {game['questionId']}\nQuestion Type: {game['questionType']}\nXP Distribution Type: {game['xpDistributionType']}\nPersonal Opinion: {game['personalOpinion']}\nQuestion: {game['questionText']}\n\nPlayer Answers:\n{answers_text}"""
    }
]

response = ollama.chat(
    model='majority-judge',
    messages=messages,
    options={
        'temperature': 0,
        'top_k': 1,
        'top_p': 1,
        'repeat_penalty': 1.0,
        'seed': 42
    }
)

with open('uma_output.bytes', 'wb') as f:
    f.write(response['message']['content'].encode('utf-8'))

print("✅ Resolution complete. Saved to uma_output.bytes")
```

Then run it:

```bash
python3 run_majority_judge.py
```

---

## 🔍 6. Verify or Dispute

- Compare `uma_output.bytes` to the proposer’s submission.
- If identical (including whitespace), the result is valid.
- If different, and all inputs + model setup match, submit an on-chain dispute.

---

## ✅ Audit Checklist

Include in your dispute or validation report:

- 📁 SHA-256 hash of `input.json`
- 📘 SHA-256 hash of `judge_manual_full_unabridged.txt`
- 🔒 Contents of your `Modelfile`
- 💾 Byte-for-byte output or its hash (`uma_output.bytes`)
- 🧠 Prompt (including player answers)

---

## 📎 Resources

- UMA Oracle Docs: [docs.uma.xyz](https://docs.uma.xyz/)
- Majority Game Info: [majority.games](https://majority.games/)
- Ollama AI Setup: [ollama.com](https://ollama.com)
