required_sections = [
    "## 1. Topic Overview",
    "## 2. Key Concepts",
    "## 3. Simplified Explanation",
    "## 4. Important Formulas",
    "## 5. Step-by-Step Logic",
    "## 6. Example Application",
    "## 7. Common Mistakes",
    "## 8. Key Takeaways"
]

file_path = "../examples/generated_summary.md"

with open(file_path, "r") as f:
    content = f.read()

missing = []

for section in required_sections:
    if section not in content:
        missing.append(section)

if not missing:
    print("✅ Output is VALID: all sections present")
else:
    print("❌ Missing sections:")
    for m in missing:
        print(f" - {m}")
