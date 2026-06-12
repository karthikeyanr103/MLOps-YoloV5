const taskConfig = {
  "object-detection": {
    label: "object detection",
    title: "Detected objects",
    sample: "/static/samples/object-detection.jpg",
    sampleName: "Street scene",
  },
  counting: {
    label: "object counting",
    title: "Object counts",
    sample: "/static/samples/counting.jpg",
    sampleName: "Eight apples",
  },
  classification: {
    label: "scene classification",
    title: "Ranked scene labels",
    sample: "/static/samples/classification.jpg",
    sampleName: "Golden retriever",
  },
  segmentation: {
    label: "instance segmentation",
    title: "Segmented regions",
    sample: "/static/samples/segmentation.jpg",
    sampleName: "Person and dog",
  },
};

const colors = ["#00d19a", "#3f8cff", "#ff7a59", "#9471ff", "#f2b632", "#ee5f89"];
const state = { task: "object-detection", file: null, image: null, result: null };
const $ = (selector) => document.querySelector(selector);
const imageInput = $("#image");
const dropZone = $("#drop-zone");
const inputStage = $("#input-stage");
const inputCanvas = $("#input-canvas");
const outputCanvas = $("#output-canvas");
const inputContext = inputCanvas.getContext("2d");
const outputContext = outputCanvas.getContext("2d");
const runButton = $("#run-button");

function setTask(task) {
  state.task = task;
  state.result = null;
  document.querySelectorAll(".task-card").forEach((card) => {
    const active = card.dataset.task === task;
    card.classList.toggle("active", active);
    card.setAttribute("aria-checked", String(active));
  });
  const config = taskConfig[task];
  $("#result-title").textContent = config.title;
  $("#run-label").textContent = `Run ${config.label}`;
  $("#sample-thumbnail").src = config.sample;
  $("#sample-title").textContent = config.sampleName;
  drawInput();
  showPanel("empty");
}

function formatBytes(bytes) {
  return bytes < 1024 * 1024
    ? `${Math.round(bytes / 1024)} KB`
    : `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function fitCanvas(canvas, image) {
  const maxWidth = canvas.parentElement.clientWidth || 560;
  const maxHeight = 390;
  const scale = Math.min(maxWidth / image.naturalWidth, maxHeight / image.naturalHeight, 1);
  canvas.width = Math.round(image.naturalWidth * scale);
  canvas.height = Math.round(image.naturalHeight * scale);
  return { scale, width: canvas.width, height: canvas.height };
}

function drawInput() {
  if (!state.image) return;
  const size = fitCanvas(inputCanvas, state.image);
  inputContext.clearRect(0, 0, size.width, size.height);
  inputContext.drawImage(state.image, 0, 0, size.width, size.height);
}

function drawBoxes(context, detections, scale) {
  detections.forEach((item, index) => {
    const box = item.box;
    if (!box) return;
    const color = colors[index % colors.length];
    const x = box.x_min * scale;
    const y = box.y_min * scale;
    const width = (box.x_max - box.x_min) * scale;
    const height = (box.y_max - box.y_min) * scale;
    const label = `${item.label} ${Math.round(item.confidence * 100)}%`;
    context.strokeStyle = color;
    context.lineWidth = Math.max(2, outputCanvas.width / 360);
    context.strokeRect(x, y, width, height);
    context.font = `700 ${Math.max(11, outputCanvas.width / 52)}px Inter, sans-serif`;
    const labelHeight = Math.max(22, outputCanvas.width / 28);
    const labelWidth = context.measureText(label).width + 14;
    const labelY = Math.max(0, y - labelHeight);
    context.fillStyle = color;
    context.fillRect(x, labelY, labelWidth, labelHeight);
    context.fillStyle = "#ffffff";
    context.fillText(label, x + 7, labelY + labelHeight * 0.7);
  });
}

async function drawPrediction(payload) {
  const size = fitCanvas(outputCanvas, state.image);
  outputContext.clearRect(0, 0, size.width, size.height);
  outputContext.drawImage(state.image, 0, 0, size.width, size.height);
  if (state.task === "segmentation" && payload.overlay) {
    const overlay = new Image();
    await new Promise((resolve) => {
      overlay.onload = resolve;
      overlay.onerror = resolve;
      overlay.src = payload.overlay;
    });
    if (overlay.naturalWidth) outputContext.drawImage(overlay, 0, 0, size.width, size.height);
  }
  drawBoxes(outputContext, payload.detections || payload.segments || [], size.scale);
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
    inputStage.classList.remove("hidden");
    $("#file-meta").classList.remove("hidden");
    $("#file-name").textContent = file.name;
    $("#file-size").textContent = `${formatBytes(file.size)} · ${image.naturalWidth} × ${image.naturalHeight}`;
    runButton.disabled = false;
    drawInput();
    showPanel("empty");
    URL.revokeObjectURL(image.src);
  };
  image.src = URL.createObjectURL(file);
}

async function loadSample() {
  const config = taskConfig[state.task];
  const response = await fetch(config.sample);
  if (!response.ok) {
    showError("The sample image could not be loaded.");
    return;
  }
  const blob = await response.blob();
  acceptFile(new File([blob], `${state.task}-sample.jpg`, { type: blob.type || "image/jpeg" }));
}

function showPanel(panel) {
  $("#result-empty").classList.toggle("hidden", panel !== "empty");
  $("#loading-state").classList.toggle("hidden", panel !== "loading");
  $("#result-content").classList.toggle("hidden", panel !== "result");
  $("#error-state").classList.toggle("hidden", panel !== "error");
  $("#latency").classList.toggle("hidden", panel !== "result");
}

function showError(message) {
  $("#error-message").textContent = message;
  showPanel("error");
}

function metric(label, value) {
  return `<article class="metric"><span>${label}</span><strong>${value}</strong></article>`;
}

function resultRows(items, detail) {
  if (!items.length) {
    return `<div class="notice-card"><strong>No objects detected</strong>
      <p>Try a clearer image containing common COCO objects such as people, vehicles, animals, or food.</p></div>`;
  }
  return `<div class="result-list">${items.map((item, index) => `
    <article class="result-row">
      <i style="background:${colors[index % colors.length]}"></i>
      <span><strong>${item.label}</strong><small>${detail(item)}</small></span>
      <b>${Math.round(item.confidence * 100)}%</b>
    </article>`).join("")}</div>`;
}

function buildResult(payload) {
  if (state.task === "counting") {
    const entries = Object.entries(payload.counts_by_class || {}).sort((a, b) => b[1] - a[1]);
    return {
      metrics: metric("Total objects", payload.total_count || 0) + metric("Classes", entries.length) + metric("Model", "YOLOv5s"),
      visual: entries.length ? `<div class="result-list">${entries.map(([label, count], index) => `
        <article class="result-row"><i style="background:${colors[index % colors.length]}"></i>
        <span><strong>${label}</strong><small>Detected instances</small></span><b>${count}</b></article>`).join("")}</div>` : resultRows([], () => ""),
    };
  }
  if (state.task === "classification") {
    const predictions = payload.predictions || [];
    return {
      metrics: metric("Labels", predictions.length) + metric("Top label", predictions[0]?.label || "None") + metric("Model", "YOLOv5s"),
      visual: predictions.length ? `<div class="confidence-chart">${predictions.slice(0, 8).map((item) => `
        <div><strong>${item.label}</strong><span><i style="width:${item.confidence * 100}%"></i></span><b>${Math.round(item.confidence * 100)}%</b></div>`).join("")}</div>` : resultRows([], () => ""),
    };
  }
  if (state.task === "segmentation") {
    const segments = payload.segments || [];
    const coverage = segments.reduce((sum, item) => sum + (item.coverage_percent || 0), 0).toFixed(1);
    return {
      metrics: metric("Masks", segments.length) + metric("Coverage", `${coverage}%`) + metric("Model", "YOLOv5s-seg"),
      visual: resultRows(segments, (item) => `${item.coverage_percent || 0}% image coverage · class ${item.class_id}`),
    };
  }
  const detections = payload.detections || [];
  const unique = new Set(detections.map((item) => item.label)).size;
  return {
    metrics: metric("Objects", detections.length) + metric("Classes", unique) +
      metric("Top confidence", detections.length ? `${Math.round(detections[0].confidence * 100)}%` : "—"),
    visual: resultRows(detections, (item) => `COCO class ${item.class_id} · bounding box`),
  };
}

async function renderResult(payload, elapsed) {
  state.result = payload;
  await drawPrediction(payload);
  const rendered = buildResult(payload);
  $("#metrics").innerHTML = rendered.metrics;
  $("#visual-result").innerHTML = rendered.visual;
  $("#json-result").textContent = JSON.stringify(payload, null, 2);
  $("#latency").textContent = `${elapsed} ms`;
  showPanel("result");
}

async function runInference() {
  if (!state.file) return;
  runButton.disabled = true;
  $("#run-label").textContent = "Running inference...";
  showPanel("loading");
  const body = new FormData();
  body.append("file", state.file);
  const started = performance.now();
  try {
    const response = await fetch(`/api/v1/${state.task}/predict`, { method: "POST", body });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail || "The API returned an error.");
    if (["not_installed", "not_configured"].includes(payload.model_status)) {
      throw new Error(payload.message || "The required YOLOv5 model is not installed.");
    }
    await renderResult(payload, Math.round(performance.now() - started));
  } catch (error) {
    showError(error.message || "Unable to reach the inference API.");
  } finally {
    runButton.disabled = false;
    $("#run-label").textContent = `Run ${taskConfig[state.task].label}`;
  }
}

document.querySelectorAll(".task-card").forEach((card) => card.addEventListener("click", () => setTask(card.dataset.task)));
imageInput.addEventListener("change", () => acceptFile(imageInput.files[0]));
runButton.addEventListener("click", runInference);
$("#sample-button").addEventListener("click", loadSample);
$("#replace-button").addEventListener("click", () => { imageInput.value = ""; imageInput.click(); });
dropZone.addEventListener("dragover", (event) => { event.preventDefault(); dropZone.classList.add("dragging"); });
dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragging"));
dropZone.addEventListener("drop", (event) => {
  event.preventDefault();
  dropZone.classList.remove("dragging");
  acceptFile(event.dataTransfer.files[0]);
});
window.addEventListener("resize", () => { drawInput(); if (state.result) drawPrediction(state.result); });
