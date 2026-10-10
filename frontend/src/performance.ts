export type BenchmarkResult = {
  instances: number; seconds: number; deckFrames: number; averageFps: number;
  p95FrameMs: number; renderer: string; viewport: string;
  declutterP95Ms?: number;
};

// Count actual deck draw callbacks during camera motion, not an idle requestAnimationFrame loop.
export class RenderMeter {
  frames: number[] = [];
  running = false;
  onDraw = () => { if (this.running) this.frames.push(performance.now()); };
  start() { this.frames = []; this.running = true; }
  finish(instances: number, started: number, renderer: string): BenchmarkResult {
    this.running = false;
    const seconds = (performance.now() - started) / 1000;
    const gaps = this.frames.slice(1).map((t, i) => t - this.frames[i]).sort((a, b) => a - b);
    return { instances, seconds: +seconds.toFixed(2), deckFrames: this.frames.length,
      averageFps: +(this.frames.length / seconds).toFixed(1),
      p95FrameMs: +(gaps[Math.floor(gaps.length * 0.95)] || 0).toFixed(1),
      renderer, viewport: `${innerWidth}×${innerHeight} @ DPR ${devicePixelRatio} (render cap 1.5)`,
    };
  }
}
