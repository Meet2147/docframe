const canvas = document.getElementById("doc-scene");
const context = canvas.getContext("2d");
let width = 0;
let height = 0;
let documents = [];

function resize() {
  const ratio = window.devicePixelRatio || 1;
  width = canvas.clientWidth;
  height = canvas.clientHeight;
  canvas.width = Math.floor(width * ratio);
  canvas.height = Math.floor(height * ratio);
  context.setTransform(ratio, 0, 0, ratio, 0, 0);
  documents = Array.from({ length: Math.max(18, Math.floor(width / 52)) }, (_, index) => ({
    x: Math.random() * width,
    y: Math.random() * height,
    speed: 0.28 + Math.random() * 0.42,
    size: 36 + Math.random() * 34,
    angle: -0.25 + Math.random() * 0.5,
    phase: index * 0.7,
    color: ["#f7f3ea", "#47c2a8", "#e96d4c", "#e7b85a"][index % 4],
  }));
}

function drawDocument(doc, time) {
  const drift = Math.sin(time * 0.001 + doc.phase) * 9;
  context.save();
  context.translate(doc.x + drift, doc.y);
  context.rotate(doc.angle);
  context.globalAlpha = 0.22;
  context.fillStyle = doc.color;
  context.strokeStyle = "rgba(255, 253, 248, 0.48)";
  context.lineWidth = 1;
  roundRect(-doc.size / 2, -doc.size * 0.64, doc.size, doc.size * 1.28, 5);
  context.fill();
  context.stroke();
  context.globalAlpha = 0.28;
  context.fillStyle = "#101418";
  context.fillRect(-doc.size * 0.32, -doc.size * 0.26, doc.size * 0.64, 2);
  context.fillRect(-doc.size * 0.32, -doc.size * 0.08, doc.size * 0.52, 2);
  context.fillRect(-doc.size * 0.32, doc.size * 0.1, doc.size * 0.42, 2);
  context.restore();
}

function drawConnectors(time) {
  context.save();
  context.globalAlpha = 0.18;
  context.strokeStyle = "#47c2a8";
  context.lineWidth = 1;
  for (let i = 0; i < documents.length - 1; i += 2) {
    const a = documents[i];
    const b = documents[i + 1];
    context.beginPath();
    context.moveTo(a.x, a.y);
    context.lineTo((a.x + b.x) / 2 + Math.sin(time * 0.001 + i) * 16, (a.y + b.y) / 2);
    context.lineTo(b.x, b.y);
    context.stroke();
  }
  context.restore();
}

function draw(time) {
  context.clearRect(0, 0, width, height);
  drawConnectors(time);
  for (const doc of documents) {
    doc.x += doc.speed;
    doc.y += Math.sin(time * 0.001 + doc.phase) * 0.03;
    if (doc.x - doc.size > width) {
      doc.x = -doc.size;
      doc.y = Math.random() * height;
    }
    drawDocument(doc, time);
  }
  requestAnimationFrame(draw);
}

function roundRect(x, y, w, h, r) {
  context.beginPath();
  context.moveTo(x + r, y);
  context.lineTo(x + w - r, y);
  context.quadraticCurveTo(x + w, y, x + w, y + r);
  context.lineTo(x + w, y + h - r);
  context.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
  context.lineTo(x + r, y + h);
  context.quadraticCurveTo(x, y + h, x, y + h - r);
  context.lineTo(x, y + r);
  context.quadraticCurveTo(x, y, x + r, y);
  context.closePath();
}

window.addEventListener("resize", resize);
resize();
requestAnimationFrame(draw);

