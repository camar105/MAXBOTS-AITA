import os

# Load template
with open("../templates/lecture_summary.md", "r") as f:
    template = f.read()

# Load raw input (textbook or notes)
with open("../examples/raw_textbook_input.md", "r") as f:
    content = f.read()

# Simple "injection" prompt (simulating AI behavior)
output = template.replace(
    "Explain the concept in plain language.",
    f"Generated from input:\n{content[:500]}..."
)

# Save output
output_path = "../examples/generated_summary.md"
with open(output_path, "w") as f:
    f.write(output)

print(f"Generated summary saved to {output_path}")
