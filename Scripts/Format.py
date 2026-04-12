import re

file_path = "../examples/generated_summary.md"

with open(file_path, "r") as f:
    content = f.read()

# Fix spacing issues
content = re.sub(r'\n{3,}', '\n\n', content)

# Ensure headers have spacing
content = re.sub(r'(## .*)\n([^\n])', r'\1\n\n\2', content)

# Trim whitespace
content = content.strip()

# Save cleaned version
with open(file_path, "w") as f:
    f.write(content)

print("✅ Markdown formatted successfully")
