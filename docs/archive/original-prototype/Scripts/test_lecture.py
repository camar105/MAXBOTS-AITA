import sys

# ===== CONFIG =====
# Run like: python test_lecture.py ../examples/sample_lecture.md
if len(sys.argv) < 2:
    print("❌ Usage: python test_lecture.py <path_to_lecture_file>")
    sys.exit()

file_path = sys.argv[1]

# Required sections (based on your template)
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

# ===== LOAD FILE =====
try:
    with open(file_path, "r") as f:
        content = f.read()
except FileNotFoundError:
    print(f"❌ File not found: {file_path}")
    sys.exit()

print(f"\n🔍 Testing Lecture File: {file_path}\n")

# ===== SECTION CHECK =====
missing_sections = []
for section in required_sections:
    if section not in content:
        missing_sections.append(section)

# ===== BASIC QUALITY CHECKS =====
score = 100

# Check length (too short = bad summary)
if len(content) < 500:
    print("⚠️ Warning: Output is very short")
    score -= 15

# Check if formulas exist
if "|" not in content:
    print("⚠️ Warning: No formula table detected")
    score -= 10

# Check for bullet points
if "-" not in content:
    print("⚠️ Warning: No bullet points detected")
    score -= 10

# Check for example section content
if "Final Answer" not in content:
    print("⚠️ Warning: Example section may be incomplete")
    score -= 10

# ===== RESULTS =====
if not missing_sections:
    print("✅ All required sections present")
else:
    print("❌ Missing Sections:")
    for sec in missing_sections:
        print(f"   - {sec}")
    score -= 20 * len(missing_sections)

# Clamp score
score = max(score, 0)

print(f"\n📊 Quality Score: {score}/100")

# Final verdict
if score >= 85:
    print("🟢 Status: STRONG output")
elif score >= 60:
    print("🟡 Status: NEEDS IMPROVEMENT")
else:
    print("🔴 Status: WEAK output")

print("\n----------------------------------\n")
