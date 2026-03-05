// ── DOM refs ──────────────────────────────────────────────
const recordBtn = document.getElementById("recordBtn");
const audioPlayer = document.getElementById("audioPlayer");
const subtitleToggle = document.getElementById("subtitleToggle");
const conversationArea = document.getElementById("conversationArea");
const emptyState = document.getElementById("emptyState");
const statusDot = document.getElementById("statusDot");
const statusText = document.getElementById("statusText");
const waveform = document.getElementById("waveform");

// Upload zone refs
const uploadZone = document.getElementById("uploadZone");
const fileInput = document.getElementById("fileInput");
const uploadBtn = document.getElementById("uploadBtn");
const replaceBtn = document.getElementById("replaceBtn");
const uploadIdle = document.getElementById("uploadIdle");
const uploadTextIdle = document.getElementById("uploadTextIdle");
const uploadProgress = document.getElementById("uploadProgress");
const uploadProgressText = document.getElementById("uploadProgressText");
const uploadLoaded = document.getElementById("uploadLoaded");
const docName = document.getElementById("docName");
const docMeta = document.getElementById("docMeta");
const chunkBadge = document.getElementById("chunkBadge");
const ingestTabs = document.getElementById("ingestTabs");
const textTitle = document.getElementById("textTitle");
const textContent = document.getElementById("textContent");
const indexTextBtn = document.getElementById("indexTextBtn");
const textCharCount = document.getElementById("textCharCount");

const togglePdf = document.getElementById("togglePdf");
const toggleText = document.getElementById("toggleText");
const sourceKnob = document.getElementById("sourceKnob");

let mediaRecorder;
let audioChunks = [];
let docLoaded = false;
let activeTab = "pdf";

// ── Pill toggle helpers ───────────────────────────────────
function positionKnob() {
  const active = activeTab === "pdf" ? togglePdf : toggleText;
  sourceKnob.style.width = active.offsetWidth + "px";
  sourceKnob.style.transform = `translateX(${active.offsetLeft - 3}px)`;
}
// Run once after layout so the knob starts in the right place
requestAnimationFrame(positionKnob);
window.addEventListener("resize", positionKnob);

// ── Upload zone ───────────────────────────────────────────

function setUploadState(state, info = {}) {
  uploadIdle.style.display = "none";
  uploadTextIdle.style.display = "none";
  uploadProgress.style.display = state === "progress" ? "flex" : "none";
  uploadLoaded.style.display = state === "loaded" ? "flex" : "none";
  ingestTabs.style.display = state === "loaded" ? "none" : "flex";

  if (state === "idle") {
    // show correct idle panel based on active tab
    if (activeTab === "pdf") {
      uploadIdle.style.display = "flex";
    } else {
      uploadTextIdle.style.display = "flex";
    }
  }

  uploadZone.classList.toggle("loaded", state === "loaded");

  if (state === "loaded") {
    docName.textContent = info.filename || info.title || "document";
    if (info.pages) {
      docMeta.textContent = `${info.pages} pages · ${info.chunks ?? "?"} chunks indexed`;
    } else {
      docMeta.textContent = `${info.characters ? info.characters.toLocaleString() + " chars · " : ""}${info.chunks ?? "?"} chunks indexed`;
    }
    docLoaded = true;
  } else {
    docLoaded = false;
  }

  // Enable mic only when a doc is loaded
  recordBtn.disabled = !docLoaded;
  document.getElementById("micHint").textContent = docLoaded
    ? "Click to start recording"
    : "Upload a PDF or paste text first";
}

async function handleFileUpload(file) {
  if (!file || !file.name.toLowerCase().endsWith(".pdf")) {
    showToast("Please choose a PDF file.");
    return;
  }

  setUploadState("progress");

  const estimatedChunks = Math.max(1, Math.ceil(file.size / 15000));
  chunkBadge.textContent = `~${estimatedChunks} chunks`;

  if (estimatedChunks < 30)
    uploadProgressText.textContent = "Processing… (~30s)";
  else if (estimatedChunks < 50)
    uploadProgressText.textContent = "Processing… (~60s)";
  else if (estimatedChunks < 100)
    uploadProgressText.textContent = "Processing… (~90s)";
  else if (estimatedChunks < 200)
    uploadProgressText.textContent = "Processing… (~2 min)";
  else uploadProgressText.textContent = "Processing… (~3 min)";

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch("/ingest", { method: "POST", body: formData });
    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.error || "Ingestion failed");
    }

    chunkBadge.textContent = `${data.chunks} chunks`;
    setUploadState("loaded", data);
    showToast("✓ Document indexed successfully!", "success");
  } catch (err) {
    setUploadState("idle");
    showToast("Error: " + err.message);
    console.error(err);
  }
}

// Click to pick file
uploadBtn.onclick = () => fileInput.click();
replaceBtn.onclick = () => {
  setUploadState("idle");
  if (activeTab === "pdf") fileInput.click();
};
fileInput.onchange = () => {
  if (fileInput.files[0]) handleFileUpload(fileInput.files[0]);
  fileInput.value = ""; // reset so same file can be re-uploaded
};

// ── Toggle switching ──────────────────────────────────────
function switchTab(tab) {
  activeTab = tab;
  togglePdf.classList.toggle("active", tab === "pdf");
  toggleText.classList.toggle("active", tab === "text");
  positionKnob();
  uploadIdle.style.display = tab === "pdf" ? "flex" : "none";
  uploadTextIdle.style.display = tab === "text" ? "flex" : "none";
}
togglePdf.onclick = () => switchTab("pdf");
toggleText.onclick = () => switchTab("text");

// ── Text char counter ──────────────────────────────────────
textContent.oninput = () => {
  const n = textContent.value.length;
  textCharCount.textContent =
    n.toLocaleString() + " character" + (n !== 1 ? "s" : "");
};

// ── Text ingestion ─────────────────────────────────────────
async function handleTextIngest() {
  const content = textContent.value.trim();
  const title = textTitle.value.trim() || "Pasted Text";

  if (!content) {
    showToast("Please paste some text first.");
    return;
  }
  if (content.length < 50) {
    showToast("Text is too short (minimum 50 characters).");
    return;
  }

  setUploadState("progress");
  const estimatedChunks = Math.max(1, Math.ceil(content.length / 350));
  chunkBadge.textContent = `~${estimatedChunks} chunks`;
  uploadProgressText.textContent =
    estimatedChunks < 50
      ? "Processing… (~30s)"
      : estimatedChunks < 100
        ? "Processing… (~60s)"
        : "Processing… (~90s)";

  try {
    const res = await fetch("/ingest/text", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: content, title }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Ingestion failed");
    chunkBadge.textContent = `${data.chunks} chunks`;
    setUploadState("loaded", data);
    showToast("✓ Text indexed successfully!", "success");
  } catch (err) {
    setUploadState("idle");
    showToast("Error: " + err.message);
    console.error(err);
  }
}

indexTextBtn.onclick = handleTextIngest;

// Drag & drop
uploadZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  uploadZone.classList.add("drag-over");
});
uploadZone.addEventListener("dragleave", () =>
  uploadZone.classList.remove("drag-over"),
);
uploadZone.addEventListener("drop", (e) => {
  e.preventDefault();
  uploadZone.classList.remove("drag-over");
  const file = e.dataTransfer.files[0];
  if (file) handleFileUpload(file);
});

// ── State helpers ──────────────────────────────────────────
function setStatus(state, text) {
  statusDot.className = "status-dot " + state;
  statusText.textContent = text;
  recordBtn.className =
    "mic-btn" +
    (state === "recording"
      ? " recording"
      : state === "processing" || state === "speaking"
        ? " " + state
        : "");
  waveform.className = "waveform" + (state === "recording" ? " active" : "");
  if (state !== "idle") {
    recordBtn.disabled = state === "processing" || state === "speaking";
  }
}

function showToast(msg, type = "error") {
  let toast = document.querySelector(".toast");
  if (!toast) {
    toast = document.createElement("div");
    toast.className = "toast";
    document.body.appendChild(toast);
  }
  toast.textContent = msg;
  toast.style.background = type === "success" ? "#2e7d32" : "#c62828";
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 3500);
}

function getTime() {
  return new Date().toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
}

// ── Chat bubble builder ────────────────────────────────────
function addBubble(role, text) {
  if (emptyState) emptyState.style.display = "none";

  const wrap = document.createElement("div");
  wrap.className = "chat-bubble " + role;

  const avatar = document.createElement("div");
  avatar.className = "bubble-avatar";
  avatar.textContent = role === "user" ? "You" : "AI";

  const body = document.createElement("div");
  body.className = "bubble-body";

  const bubble = document.createElement("div");
  bubble.className = "bubble-text";
  bubble.textContent = text;

  const time = document.createElement("div");
  time.className = "bubble-time";
  time.textContent = getTime();

  body.appendChild(bubble);
  body.appendChild(time);
  wrap.appendChild(avatar);
  wrap.appendChild(body);
  conversationArea.appendChild(wrap);
  conversationArea.scrollTop = conversationArea.scrollHeight;
  return wrap;
}

function addThinkingBubble() {
  if (emptyState) emptyState.style.display = "none";

  const wrap = document.createElement("div");
  wrap.className = "chat-bubble ai thinking-bubble";

  const avatar = document.createElement("div");
  avatar.className = "bubble-avatar";
  avatar.textContent = "AI";

  const body = document.createElement("div");
  body.className = "bubble-body";

  const bubble = document.createElement("div");
  bubble.className = "bubble-text";
  bubble.innerHTML =
    '<div class="dots"><span></span><span></span><span></span></div>';

  body.appendChild(bubble);
  wrap.appendChild(avatar);
  wrap.appendChild(body);
  conversationArea.appendChild(wrap);
  conversationArea.scrollTop = conversationArea.scrollHeight;
  return wrap;
}

// ── Recording ─────────────────────────────────────────────
recordBtn.onclick = async () => {
  if (!docLoaded) {
    showToast("Upload a PDF first.");
    return;
  }
  if (!mediaRecorder || mediaRecorder.state === "inactive") {
    await startRecording();
  } else {
    stopRecording();
  }
};

async function startRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        sampleRate: 16000,
        channelCount: 1,
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
      },
    });

    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];

    mediaRecorder.ondataavailable = (e) => audioChunks.push(e.data);
    mediaRecorder.onstop = sendAudioToBackend;
    mediaRecorder.start();

    setStatus("recording", "Recording…");
  } catch (err) {
    showToast("Microphone access denied.");
    console.error(err);
  }
}

function stopRecording() {
  mediaRecorder.stop();
  mediaRecorder.stream.getTracks().forEach((t) => t.stop());
  setStatus("processing", "Transcribing…");
}

// ── Send to backend ────────────────────────────────────────
async function sendAudioToBackend() {
  const blob = new Blob(audioChunks, { type: "audio/webm" });
  const formData = new FormData();
  formData.append("audio", blob);

  const thinkingEl = addThinkingBubble();

  try {
    const response = await fetch("/voice", { method: "POST", body: formData });

    if (!response.ok) throw new Error("Server error: " + response.status);

    const transcription = response.headers.get("X-Transcription") || "";
    const answerText = response.headers.get("X-Response-Text") || "";
    const audioBlob = await response.blob();

    thinkingEl.remove();

    if (subtitleToggle.checked) {
      if (transcription) addBubble("user", transcription);
      if (answerText) addBubble("ai", answerText);
    }

    setStatus("speaking", "Speaking…");
    const audioURL = URL.createObjectURL(audioBlob);
    audioPlayer.src = audioURL;
    audioPlayer.play();

    audioPlayer.onended = () => {
      setStatus("ready", "Ready");
      URL.revokeObjectURL(audioURL);
    };
  } catch (err) {
    thinkingEl.remove();
    showToast("Error: " + err.message);
    setStatus("ready", "Ready");
    console.error(err);
  }
}

// ── Init ──────────────────────────────────────────────────
(async () => {
  setStatus("idle", "Checking…");
  try {
    const res = await fetch("/api/document");
    const data = await res.json();
    if (data.loaded) {
      setUploadState("loaded", {
        filename: "Previous document",
        pages: "?",
        chunks: "?",
      });
      setStatus("ready", "Ready");
    } else {
      setUploadState("idle");
      setStatus("idle", "No document loaded");
    }
  } catch {
    setUploadState("idle");
    setStatus("idle", "No document loaded");
  }
})();
