const recordBtn = document.getElementById("recordBtn");
const subtitleDiv = document.getElementById("subtitle");
const responseDiv = document.getElementById("responseText");
const audioPlayer = document.getElementById("audioPlayer");
const subtitleToggle = document.getElementById("subtitleToggle");

let mediaRecorder;
let audioChunks = [];

recordBtn.onclick = async () => {
  if (!mediaRecorder || mediaRecorder.state === "inactive") {
    startRecording();
  } else {
    stopRecording();
  }
};

async function startRecording() {
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

  mediaRecorder.ondataavailable = (event) => {
    audioChunks.push(event.data);
  };

  mediaRecorder.onstop = sendAudioToBackend;

  mediaRecorder.start();
  recordBtn.innerText = "Stop Recording";
}

function stopRecording() {
  mediaRecorder.stop();
  recordBtn.innerText = "Start Recording";
}

async function sendAudioToBackend() {
  const blob = new Blob(audioChunks, { type: "audio/webm" });

  const formData = new FormData();
  formData.append("audio", blob);

  const response = await fetch("/voice", {
    method: "POST",
    body: formData,
  });

  const audioBlob = await response.blob();

  // Play audio
  const audioURL = URL.createObjectURL(audioBlob);
  audioPlayer.src = audioURL;
  audioPlayer.play();

  // Subtitles
  const transcription = response.headers.get("X-Transcription");
  const answerText = response.headers.get("X-Response-Text");

  if (subtitleToggle.checked) {
    subtitleDiv.innerText = "You: " + transcription;
    responseDiv.innerText = "AI: " + answerText;
  } else {
    subtitleDiv.innerText = "";
    responseDiv.innerText = "";
  }
}
