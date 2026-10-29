// Tekent het roulettewiel op een canvas en laat het op een bepaald getal stoppen.

import { WHEEL_ORDER, colorOf } from "./config.js";

const SEGMENT_DEG = 360 / WHEEL_ORDER.length;
const EXTRA_TURNS = 5;
const SEGMENT_COLORS = { red: "#b3202a", black: "#17161b", green: "#1d7a46" };
const GOLD = "#c9a24a";

const mod = (n, m) => ((n % m) + m) % m;

export class Wheel {
  constructor(canvas, durationMs) {
    this.canvas = canvas;
    this.durationMs = durationMs;
    this.rotation = 0;
    this.draw();
  }

  draw() {
    const size = 600;
    this.canvas.width = size;
    this.canvas.height = size;

    const ctx = this.canvas.getContext("2d");
    const c = size / 2;
    const outer = c - 10;
    const inner = outer * 0.6;
    const seg = (Math.PI * 2) / WHEEL_ORDER.length;

    ctx.beginPath();
    ctx.arc(c, c, c - 1, 0, Math.PI * 2);
    ctx.fillStyle = GOLD;
    ctx.fill();

    // Vak i ligt gecentreerd op i * seg, met de klok mee vanaf boven.
    WHEEL_ORDER.forEach((number, i) => {
      const start = -Math.PI / 2 + i * seg - seg / 2;
      ctx.beginPath();
      ctx.moveTo(c, c);
      ctx.arc(c, c, outer, start, start + seg);
      ctx.closePath();
      ctx.fillStyle = SEGMENT_COLORS[colorOf(number)];
      ctx.fill();
      ctx.strokeStyle = "rgba(201, 162, 74, 0.65)";
      ctx.lineWidth = 1.5;
      ctx.stroke();

      ctx.save();
      ctx.translate(c, c);
      ctx.rotate(i * seg);
      ctx.fillStyle = "#f5efe0";
      ctx.font = "600 22px system-ui, sans-serif";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(String(number), 0, -outer * 0.86);
      ctx.restore();
    });

    const hub = ctx.createRadialGradient(c, c, inner * 0.1, c, c, inner);
    hub.addColorStop(0, "#3a2c18");
    hub.addColorStop(1, "#140f09");
    ctx.beginPath();
    ctx.arc(c, c, inner, 0, Math.PI * 2);
    ctx.fillStyle = hub;
    ctx.fill();
    ctx.lineWidth = 4;
    ctx.strokeStyle = GOLD;
    ctx.stroke();
  }

  spinTo(number) {
    const index = WHEEL_ORDER.indexOf(number);
    if (index === -1) return Promise.reject(new Error(`Onbekend getal: ${number}`));

    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const duration = reducedMotion ? 400 : this.durationMs;

    // Draai zo ver dat vak `index` onder de wijzer bovenaan eindigt, met wat speling binnen het vak.
    const jitter = (Math.random() - 0.5) * SEGMENT_DEG * 0.6;
    const target = mod(-index * SEGMENT_DEG + jitter, 360);
    const delta = mod(target - mod(this.rotation, 360), 360);
    this.rotation += (reducedMotion ? 0 : EXTRA_TURNS * 360) + delta;

    this.canvas.style.transition = `transform ${duration}ms cubic-bezier(0.12, 0.8, 0.2, 1)`;
    this.canvas.style.transform = `rotate(${this.rotation}deg)`;

    return new Promise((resolve) => setTimeout(resolve, duration));
  }
}
