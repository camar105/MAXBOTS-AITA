const state = {
  sessionId: null,
  lastQuizTopic: "Uploaded Material",
};

const uploadForm = document.querySelector("#upload-form");
const commandForm = document.querySelector("#command-form");
const scoreForm = document.querySelector("#score-form");

const uploadFeedback = document.querySelector("#upload-feedback");
const fileList = document.querySelector("#file-list");
const sessionBadge = document.querySelector("#session-badge");
const responseTitle = document.querySelector("#response-title");
const responseBody = document.querySelector("#response-body");
const sourcesList = document.querySelector("#sources-list");
const answerKey = document.querySelector("#answer-key");
const quizPanel = document.querySelector("#quiz-panel");
const progressSummary = document.querySelector("#progress-summary");
const progressList = document.querySelector("#progress-list");
const commandSelect = document.querySelector("#command");
const topicInput = document.querySelector("#topic");
const scoreInput = document.querySelector("#quiz-score");


function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}


function renderInlineMarkdown(text) {
  return escapeHtml(text).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
}


function renderMarkdown(markdown) {
  const lines = markdown.split(/\r?\n/);
  const html = [];
  let listMode = null;

  const closeList = () => {
    if (listMode === "ul") {
      html.push("</ul>");
    }
    if (listMode === "ol") {
      html.push("</ol>");
    }
    listMode = null;
  };

  for (const rawLine of lines) {
    const line = rawLine.trim();
    if (!line) {
      closeList();
      continue;
    }

    if (line.startsWith("### ")) {
      closeList();
      html.push(`<h3>${renderInlineMarkdown(line.slice(4))}</h3>`);
      continue;
    }

    if (line.startsWith("## ")) {
      closeList();
      html.push(`<h2>${renderInlineMarkdown(line.slice(3))}</h2>`);
      continue;
    }

    if (line.startsWith("# ")) {
      closeList();
      html.push(`<h1>${renderInlineMarkdown(line.slice(2))}</h1>`);
      continue;
    }

    if (line.startsWith("- ")) {
      if (listMode !== "ul") {
        closeList();
        html.push("<ul>");
        listMode = "ul";
      }
      html.push(`<li>${renderInlineMarkdown(line.slice(2))}</li>`);
      continue;
    }

    const numbered = line.match(/^(\d+)\.\s+(.*)$/);
    if (numbered) {
      if (listMode !== "ol") {
        closeList();
        html.push("<ol>");
        listMode = "ol";
      }
      html.push(`<li>${renderInlineMarkdown(numbered[2])}</li>`);
      continue;
    }

    closeList();
    html.push(`<p>${renderInlineMarkdown(line)}</p>`);
  }

  closeList();
  return html.join("");
}


function renderSources(sources) {
  if (!sources || !sources.length) {
    sourcesList.innerHTML = "<li class='muted'>No source excerpts available yet.</li>";
    return;
  }

  sourcesList.innerHTML = sources
    .map((item) => `<li><strong>${escapeHtml(item.source)}</strong><br><span class="muted">${escapeHtml(item.excerpt)}</span></li>`)
    .join("");
}


function renderProgress(progress) {
  if (!progress || !progress.attemptCount) {
    progressSummary.textContent = "No quiz attempts recorded yet.";
    progressList.innerHTML = "";
    return;
  }

  progressSummary.textContent = `Attempts: ${progress.attemptCount} | Overall average: ${progress.overallPercentage}%`;
  progressList.innerHTML = progress.topicStats
    .map((item) => `<li><strong>${escapeHtml(item.topic)}</strong> - ${item.averagePercentage}% over ${item.attempts} attempt(s)</li>`)
    .join("");
}


uploadForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(uploadForm);

  uploadFeedback.textContent = "Building study session...";
  fileList.innerHTML = "";

  const response = await fetch("/api/upload", {
    method: "POST",
    body: formData,
  });

  const payload = await response.json();
  if (!response.ok) {
    uploadFeedback.textContent = payload.error || "Upload failed.";
    return;
  }

  state.sessionId = payload.sessionId;
  sessionBadge.textContent = `Session ${payload.sessionId}`;
  uploadFeedback.textContent = `Loaded ${payload.fileCount} file(s) into ${payload.chunkCount} study chunk(s).`;
  fileList.innerHTML = payload.files
    .map((item) => `<li>${escapeHtml(item.name)} - ${item.characters} characters extracted</li>`)
    .join("");
  renderProgress(payload.progress);
});


commandForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!state.sessionId) {
    uploadFeedback.textContent = "Upload course material before running a command.";
    return;
  }

  const command = commandSelect.value;
  const topic = topicInput.value.trim();
  responseTitle.textContent = "Working...";
  responseBody.innerHTML = "<p>Generating grounded response...</p>";
  quizPanel.classList.add("hidden");

  const response = await fetch("/api/command", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      sessionId: state.sessionId,
      command,
      topic,
    }),
  });

  const payload = await response.json();
  if (!response.ok) {
    responseTitle.textContent = "Request failed";
    responseBody.innerHTML = `<p>${escapeHtml(payload.error || "The command could not be completed.")}</p>`;
    return;
  }

  state.lastQuizTopic = topic || payload.title;
  responseTitle.textContent = payload.title;
  responseBody.innerHTML = renderMarkdown(payload.markdown);
  renderSources(payload.sources);
  renderProgress(payload.progress);

  if (payload.quiz && payload.answerKey) {
    answerKey.innerHTML = payload.answerKey
      .map((item) => `<li><strong>${item.number}.</strong> ${escapeHtml(item.answer)}</li>`)
      .join("");
    quizPanel.classList.remove("hidden");
  }
});


scoreForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!state.sessionId) {
    return;
  }

  const response = await fetch("/api/progress", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      sessionId: state.sessionId,
      topic: state.lastQuizTopic,
      score: Number(scoreInput.value),
      total: 10,
    }),
  });

  const payload = await response.json();
  if (!response.ok) {
    progressSummary.textContent = payload.error || "Could not save quiz score.";
    return;
  }

  renderProgress(payload.progress);
  progressSummary.textContent = `Saved quiz score for ${state.lastQuizTopic}. Overall average: ${payload.progress.overallPercentage}%`;
});
