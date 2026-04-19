# Max's Bots: StatAI-TA

## Team Members

- Lily Urbanczyk - lurbancz@asu.edu
- Kolter Nelson - knels104@asu.edu
- Edward Bernstein - egbernst@asu.edu
- Carlos Martinez - camar105@asu.edu
- Oscar Barrera - oabarre2@asu.edu
- Carter Baldwin - cdbaldw4@asu.edu

## Problem Statement

### Who is the user?

The primary users are undergraduate students in introductory statistics courses, especially students who do not have a strong math background but still need to succeed in a required statistics class.

The secondary user is the professor who wants students to have reliable course-grounded support outside of office hours.

### What problem do they experience today?

Students already use large AI systems such as ChatGPT, Claude, and Gemini, but those tools are not grounded in the student's class timeline, instructor expectations, or current weak spots. Students often need to repeat context such as:

- do not use advanced jargon
- only explain material covered so far
- remember which topics I already struggle with

This makes the learning experience less efficient and less trustworthy, even when the answer is technically correct.

## Why Now?

### Why does this problem matter in the next 3-5 years?

AI study tools are rapidly becoming normal in higher education. Students who know how to prompt them well will have a major advantage over students who do not. A guided, course-aware tool can reduce that gap and make AI support more consistent.

### What changed that makes this possible now?

- Retrieval-augmented workflows are now accessible to student developers.
- Hosted AI APIs are cheap enough for prototype-scale experimentation.
- Students already expect AI to be part of their academic workflow.

## Proposed AI-Powered Solution

### What does the product do?

StatAI-TA is a personalized statistics teaching assistant that stays aligned with a student's course materials and class progress. The target interaction model is a simple study interface with three core commands:

- `daily quiz`
- `summary`
- `explain`

The system should use uploaded class resources such as syllabi, lecture notes, slides, textbook excerpts, and worked examples to generate course-grounded help in plain language.

### Where does AI/ML add unique value?

AI is useful here because it can:

- generate targeted quiz questions from course content
- adapt explanations to the student's weak areas
- rewrite difficult ideas into plain language
- stay grounded in the same resources the student is using

## Initial Technical Concept

### What data is needed?

- student- or professor-uploaded course materials, especially PDFs and text notes
- quiz history and topic-level progress data stored locally
- optional textbook images or diagram-heavy slides for multimodal support

### What models might be used?

- a GPT-style language model for summaries, explanations, and quiz generation
- embeddings or local retrieval for matching questions to source material
- a simple progress tracker for weak-topic detection
- a vision-capable model for image-heavy slides when available

### How could the nanoGPT work feed into this?

The nanoGPT phase helps the team understand how generative models behave, what they do well, and where they fail. That informs prompt design, evaluation, and future model choices for the MVP.

## Scope For MVP

### What can realistically be built in about 6 weeks?

A practical MVP is a single-user web app where a student uploads their own course materials and then uses `daily quiz`, `summary`, and `explain` to get grounded responses. The initial version does not need a shared classroom deployment or a persistent remote database.

### Concrete v1 feature

A user can upload statistics course materials and the system returns either:

- a plain-language topic summary
- a concise explanation of a topic from uploaded material
- a 10-question study quiz based on uploaded material

The system also stores lightweight local progress data so it can highlight weak topics.

## Risks And Open Questions

1. PDF quality and extraction reliability
2. Keeping the system grounded in course material instead of drifting outward
3. Measuring whether explanations are truly plain-language and student-friendly

## Planned Data Sources

- student-uploaded PDFs
- lecture notes and slides
- textbook excerpts
- local retrieval index built from uploaded materials
- locally stored quiz history
