from src.maxbots_mvp.engine import StudyEngine, build_chunks


def build_demo_chunks():
    documents = [
        (
            "lecture.md",
            "The central limit theorem says that when sample size increases, the distribution of sample means tends toward a normal shape. The mean of the sample means stays close to the population mean. The spread of the sample means becomes smaller as sample size increases.",
        ),
        (
            "homework.md",
            "For a one-sample z-test, compare the sample mean to the claimed population mean and use the population standard deviation when it is known. A smaller p-value gives stronger evidence against the null hypothesis.",
        ),
    ]
    return build_chunks(documents, chunk_size=60, overlap=10)


def test_summary_contains_expected_sections():
    engine = StudyEngine()
    response = engine.run_command("summary", "central limit theorem", build_demo_chunks(), {})
    assert "## Topic Overview" in response.markdown
    assert "## Key Points" in response.markdown
    assert "## Quick Recap" in response.markdown
    assert response.sources


def test_quiz_returns_ten_questions():
    engine = StudyEngine()
    response = engine.run_command("daily quiz", "central limit theorem", build_demo_chunks(), {})
    assert len(response.questions) == 10
    assert all(question.prompt for question in response.questions)
    assert all(question.answer for question in response.questions)


def test_relevant_topic_is_reflected_in_explanation_title():
    engine = StudyEngine()
    response = engine.run_command("explain", "z-test", build_demo_chunks(), {"weakTopics": ["p-value"]})
    assert response.title == "Explain: z-test"
    assert "weakest recorded topic" in response.markdown
