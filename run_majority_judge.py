import json
import ollama

# Load full judge manual
with open("judge_manual_full_unabridged.txt", "r") as f:
    manual = f.read()

# Load game input
with open("input.json", "r") as f:
    game_data = json.load(f)

# Build prompt
messages = [
    {
        "role": "system",
        "content": (
            "You are the UMA-approved AI Judge for Majority. Follow the judging protocol from the user exactly. "
            "Always return deterministic results in byte-stable format, matching the UMA resolution spec."
        )
    },
    {
        "role": "user",
        "content": manual
    },
    {
        "role": "user",
        "content": (
            "Resolve the following game:\n\n"
            + json.dumps(game_data, indent=2) +
            "\n\nStart with: Majority Judge Ready: Quad-Check Protocol Armed and Initiated."
        )
    }
]

# Call the model
response = ollama.chat(
    model="majority-judge",  # use your created model if built with Modelfile
    messages=messages,
    options={
        "temperature": 0,
        "top_k": 1,
        "top_p": 1,
        "repeat_penalty": 1.0,
        "seed": 42
    }
)

# Save output as bytes
output = response["message"]["content"]
with open("uma_output.bytes", "wb") as f:
    f.write(output.encode("utf-8"))

print("✅ Resolution complete. Result saved to uma_output.bytes")
