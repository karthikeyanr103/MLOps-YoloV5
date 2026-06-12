const taskConfig = {
  "object-detection": {
    label: "object detection",
    title: "Detection results",
  },
  counting: {
    label: "object counting",
    title: "Counting results",
  },
  classification: {
    label: "scene labels",
    title: "Scene labels",
  },
  segmentation: {
    label: "segmentation",
    title: "Segmentation status",
  },
};

const colors = ["#0a9f73", "#3e8df5", "#ff7b4e", "#8467e8", "#e6aa20", "#df4f72"];
const state = { task: "object-detection", file: null, image: null, result: null };

const imageInput = document.querySelector("#image");
const dropZone = document.querySelector("#drop-zone");
const previewShell = document.querySelector("#preview-shell");
const previewCanvas = document.querySelector("#preview-canvas");
const context = previewCanvas.getContext("2d");
const runButton = document.querySelector("#run-button");
const runLabel = document.querySelector("#run-label");
const resultTitle = document.querySelector("#result-title");
const emptyState = document.querySelector("#result-empty");
const loadingState = document.querySelector("#loading-state");
const resultContent = document.querySelector("#result-content");
const errorState = document.querySelector("#error-state");
const latency = document.querySelector("#latency");

function setTask(task) {
  state.task = task;
  document.querySelectorAll(".task-card").forEach((card) => {
    const active = card.dataset.task === task;
    card.classList.toggle("active", active);
    card.setAttribute("aria-checked", String(active));
  });
  runLabel.textContent = `Run ${taskConfig[task].label}`;
  resultTitle.textContent = taskConfig[task].title;
  state.result = null;
  drawPreview();
  showPanel("empty");
}

function formatBytes(bytes) {
  if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function acceptFile(file) {
  if (!file || !["image/jpeg", "image/png", "image/webp"].includes(file.type)) {
    showError("Choose a JPEG, PNG, or WebP image.");
    return;
  }
  if (file.size > 10 * 1024 * 1024) {
    showError("The image must be 10 MB or smaller.");
    return;
  }

  const image = new Image();
  image.onload = () => {
    state.file = file;
    state.image = image;
    state.result = null;
    dropZone.classList.add("hidden");
    previewShell.classList.remove("hidden");
    document.querySelector("#file-meta").classList.remove("hidden");
    document.querySelector("#file-name").textContent = file.name;
    document.querySelector("#file-size").textContent =
      `${formatBytes(file.size)} · ${image.naturalWidth} × ${image.naturalHeight}`;
    runButton.disabled = false;
    drawPreview();
    showPanel("empty");
    URL.revokeObjectURL(image.src);
  };
  image.src = URL.createObjectURL(file);
}

function canvasSize() {
  const maxWidth = previewShell.clientWidth || 560;
  const maxHeight = 420;
  const scale = Math.min(maxWidth / state.image.naturalWidth, maxHeight / state.image.naturalHeight, 1);
  return {
    width: Math.round(state.image.naturalWidth * scale),
    height: Math.round(state.image.naturalHeight * scale),
    scale,
  };
}

function drawPreview() {
  if (!state.image) return;
  const size = canvasSize();
  previewCanvas.width = size.width;
  previewCanvas.height = size.height;
  context.drawImage(state.image, 0, 0, size.width, size.height);

  const detections = state.result?.detections || [];
  detections.forEach((detection, index) => {
    const color = colors[index % colors.length];
    const box = detection.box;
    const x = box.x_min * size.scale;
    const y = box.y_min * size.scale;
    const width = (box.x_max - box.x_min) * size.scale;
    const height = (box.y_max - box.y_min) * size.scale;
    const label = `${detection.label} ${Math.round(detection.confidence * 100)}%`;

    context.strokeStyle = color;
    context.lineWidth = Math.max(2, size.width / 320);
    context.strokeRect(x, y, width, height);
    context.font = `700 ${Math.max(10, size.width / 48)}px Inter, sans-serif`;
    const textWidth = context.measureText(label).width + 12;
    const labelHeight = Math.max(20, size.width / 26);
    const labelY = Math.max(0, y - labelHeight);
    context.fillStyle = color;
    context.fillRect(x, labelY, textWidth, labelHeight);
    context.fillStyle = "#ffffff";
    context.fillText(label, x + 6, labelY + labelHeight * .7);
  });
}

function showPanel(panel) {
  emptyState.classList.toggle("hidden", panel !== "empty");
  loadingState.classList.toggle("hidden", panel !== "loading");
  resultContent.classList.toggle("hidden", panel !== "result");
  errorState.classList.toggle("hidden", panel !== "error");
  latency.classList.toggle("hidden", panel !== "result");
}

function showError(message) {
  document.querySelector("#error-message").textContent = message;
  showPanel("error");
}

function metric(label, value) {
  return `<article class="metric"><span>${label}</span><strong>${value}</strong></article>`;
}

function detectionList(detections) {
  if (!detections.length) {
    return `<div class="notice-card"><strong>No objects detected</strong>
      <p>Try a clearer image or one containing common COCO objects such as people, vehicles, or animals.</p></div>`;
  }
  return `<div class="result-list">${detections.map((item, index) => `
    <article class="result-row">
      <i class="color-dot" style="background:${colors[index % colors.length]}"></i>
      <span><strong>${item.label}</strong><small>Class ${item.class_id} · bounding box</small></span>
      <span class="confidence">${Math.round(item.confidence * 100)}%</span>
    </article>`).join("")}</div>`;
}

function renderDetection(payload) {
  const detections = payload.detections || [];
  const unique = new Set(detections.map((item) => item.label)).size;
  const best = detections.length ? `${Math.round(detections[0].confidence * 100)}%` : "—";
  return {
    metrics: metric("Objects", detections.length) + metric("Classes", unique) + metric("Top confidence", best),
    visual: detectionList(detections),
  };
}

function renderCounting(payload) {
  const entries = Object.entries(payload.counts_by_class || {}).sort((a, b) => b[1] - a[1]);
  const visual = entries.length
    ? `<div class="result-list">${entries.map(([label, count], index) => `
        <article class="result-row">
          <i class="color-dot" style="background:${colors[index % colors.length]}"></i>
          <span><strong>${label}</strong><small>Detected instances</small></span>
          <span class="count-chip">${count}</span>
        </article>`).join("")}</div>`
    : detectionList([]);
  return {
    metrics: metric("Total objects", payload.total_count || 0) +
      metric("Object classes", entries.length) +
      metric("Model", "YOLOv5s"),
    visual,
  };
}

function renderClassification(payload) {
  const predictions = payload.predictions || [];
  const visual = predictions.length
    ? `<div class="confidence-chart">${predictions.slice(0, 8).map((item) => `
        <div class="bar-row">
          <strong>${item.label}</strong>
          <div class="bar-track"><div class="bar-fill" style="width:${item.confidence * 100}%"></div></div>
          <span>${Math.round(item.confidence * 100)}%</span>
        </div>`).join("")}</div>`
    : detectionList([]);
  return {
    metrics: metric("Scene labels", predictions.length) +
      metric("Top label", predictions[0]?.label || "None") +
      metric("Model", "YOLOv5s"),
    visual,
  };
}

function renderSegmentation(payload) {
  return {
    metrics: metric("Status", "Roadmap") + metric("Required model", "YOLOv5-seg"),
    visual: `<div class="notice-card"><strong>Segmentation is intentionally transparent</strong>
      <p>${payload.message || "The deployed YOLOv5s detector produces boxes, not pixel masks. This task will activate when YOLOv5-seg mask decoding is added."}</p></div>`,
  };
}

function renderResult(payload, elapsed) {
  state.result = payload;
  drawPreview();
  let rendered;
  if (state.task === "counting") rendered = renderCounting(payload);
  else if (state.task === "classification") rendered = renderClassification(payload);
  else if (state.task === "segmentation") rendered = renderSegmentation(payload);
  else rendered = renderDetection(payload);

  document.querySelector("#metrics").innerHTML = rendered.metrics;
  document.querySelector("#visual-result").innerHTML = rendered.visual;
  document.querySelector("#json-result").textContent = JSON.stringify(payload, null, 2);
  latency.textContent = `${elapsed} ms`;
  showPanel("result");
}

async function runInference() {
  if (!state.file) return;
  runButton.disabled = true;
  runLabel.textContent = "Running inference…";
  showPanel("loading");
  const body = new FormData();
  body.append("file", state.file);
  const started = performance.now();

  try {
    const response = await fetch(`/api/v1/${state.task}/predict`, { method: "POST", body });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail || "The API returned an error.");
    if (payload.model_status === "not_installed") {
      throw new Error(payload.message || "The YOLOv5 model is not installed in this deployment.");
    }
    renderResult(payload, Math.round(performance.now() - started));
  } catch (error) {
    showError(error.message || "Unable to reach the inference API.");
  } finally {
    runButton.disabled = false;
    runLabel.textContent = `Run ${taskConfig[state.task].label}`;
  }
}

document.querySelectorAll(".task-card").forEach((card) => {
  card.addEventListener("click", () => setTask(card.dataset.task));
});
imageInput.addEventListener("change", () => acceptFile(imageInput.files[0]));
runButton.addEventListener("click", runInference);
document.querySelector("#replace-button").addEventListener("click", () => {
  imageInput.value = "";
  imageInput.click();
});
dropZone.addEventListener("dragover", (event) => {
  event.preventDefault();
  dropZone.classList.add("dragging");
});
dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragging"));
dropZone.addEventListener("drop", (event) => {
  event.preventDefault();
  dropZone.classList.remove("dragging");
  acceptFile(event.dataTransfer.files[0]);
});
window.addEventListener("resize", drawPreview);
