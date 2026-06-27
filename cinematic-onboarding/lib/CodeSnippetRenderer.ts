import * as THREE from "three";

export class CodeSnippetRenderer {
  private canvas: HTMLCanvasElement;
  private ctx: CanvasRenderingContext2D;

  constructor() {
    if (typeof window !== "undefined") {
      this.canvas = document.createElement("canvas");
      this.canvas.width = 400;
      this.canvas.height = 300;
      this.ctx = this.canvas.getContext("2d")!;
    } else {
      // Server-side fallback placeholder
      this.canvas = {} as any;
      this.ctx = {} as any;
    }
  }

  // Draw rounded rectangles helper
  private drawRoundRect(x: number, y: number, w: number, h: number, r: number) {
    const ctx = this.ctx;
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + w, y, x + w, y + h, r);
    ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r);
    ctx.arcTo(x, y, x + w, y, r);
    ctx.closePath();
  }

  public renderCodeSnippet(filename: string, code: string[], language: string): THREE.CanvasTexture {
    const ctx = this.ctx;
    const w = this.canvas.width;
    const h = this.canvas.height;

    ctx.clearRect(0, 0, w, h);

    // 1. Editor Window Background
    ctx.fillStyle = "rgba(15, 15, 22, 0.95)";
    this.drawRoundRect(0, 0, w, h, 14);
    ctx.fill();

    // Border Glow
    ctx.strokeStyle = "rgba(139, 92, 246, 0.3)";
    ctx.lineWidth = 2.5;
    ctx.stroke();

    // 2. Title Bar Header
    ctx.save();
    ctx.beginPath();
    this.drawRoundRect(0, 0, w, h, 14);
    ctx.clip();
    ctx.fillStyle = "rgba(26, 26, 34, 1.0)";
    ctx.fillRect(0, 0, w, 36);
    ctx.restore();

    // 3. Window Control Dots (VSCode Style)
    const colors = ["#ff5f56", "#ffbd2e", "#27c93f"];
    colors.forEach((col, idx) => {
      ctx.beginPath();
      ctx.arc(18 + idx * 14, 18, 4.5, 0, Math.PI * 2);
      ctx.fillStyle = col;
      ctx.fill();
    });

    // 4. File Tab Filename
    ctx.fillStyle = "#A78BFA";
    ctx.font = "bold 11px monospace";
    ctx.fillText(filename, 70, 22);

    // 5. Code Lines with Tokenized Highlighting
    let y = 62;
    code.forEach((line, idx) => {
      // Line Numbers Gutter
      ctx.fillStyle = "rgba(100, 100, 120, 0.4)";
      ctx.font = "10px monospace";
      ctx.fillText(String(idx + 1).padStart(2, "0"), 16, y);

      // Line Tokens
      const tokens = this.tokenize(line, language);
      let x = 42;
      tokens.forEach((token) => {
        ctx.fillStyle = this.getTokenColor(token.type);
        ctx.fillText(token.text, x, y);
        x += ctx.measureText(token.text).width;
      });
      y += 18;
    });

    const texture = new THREE.CanvasTexture(this.canvas);
    texture.colorSpace = THREE.SRGBColorSpace;
    texture.needsUpdate = true;
    return texture;
  }

  public renderFilenameBadge(filename: string): THREE.CanvasTexture {
    const canvas = document.createElement("canvas");
    canvas.width = 192;
    canvas.height = 48;
    const ctx = canvas.getContext("2d")!;

    ctx.clearRect(0, 0, 192, 48);

    // Badge Background
    ctx.fillStyle = "rgba(22, 22, 28, 0.85)";
    ctx.beginPath();
    ctx.roundRect ? ctx.roundRect(0, 0, 192, 48, 8) : ctx.rect(0, 0, 192, 48);
    ctx.fill();

    ctx.strokeStyle = "rgba(0, 229, 255, 0.3)";
    ctx.lineWidth = 1.5;
    ctx.stroke();

    // Icon Placeholder Shape (Document rectangle)
    ctx.fillStyle = this.getFileIconColor(filename);
    ctx.beginPath();
    ctx.roundRect ? ctx.roundRect(14, 15, 12, 18, 2) : ctx.rect(14, 15, 12, 18);
    ctx.fill();

    // Text Filename
    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 13px sans-serif";
    ctx.fillText(filename, 36, 28);

    const texture = new THREE.CanvasTexture(canvas);
    texture.colorSpace = THREE.SRGBColorSpace;
    texture.needsUpdate = true;
    return texture;
  }

  private tokenize(line: string, _lang: string): Array<{ type: string; text: string }> {
    const tokens: Array<{ type: string; text: string }> = [];
    const regex = /(".*?")|('.*?')|(\/\/.*$)|(function|const|let|var|return|if|else|class|import|from|export|async|await|def)|(\w+)|(\s+|[^\w\s])/g;
    let match;
    while ((match = regex.exec(line)) !== null) {
      if (match[1] || match[2]) tokens.push({ type: "string", text: match[0] });
      else if (match[3]) tokens.push({ type: "comment", text: match[0] });
      else if (match[4]) tokens.push({ type: "keyword", text: match[0] });
      else if (match[5]) tokens.push({ type: "identifier", text: match[0] });
      else tokens.push({ type: "default", text: match[0] });
    }
    return tokens;
  }

  private getTokenColor(type: string): string {
    const colors: Record<string, string> = {
      keyword: "#C586C0",     // Lavender purple
      string: "#CE9178",      // Warm orange
      comment: "#6A9955",     // Muted comment green
      identifier: "#9CDCFE",  // Standard light blue
      default: "#D4D4D4"      // Gray text
    };
    return colors[type] || colors.default;
  }

  private getFileIconColor(filename: string): string {
    const ext = filename.split(".").pop();
    const colorMap: Record<string, string> = {
      js: "#F7DF1E",   // JavaScript yellow
      ts: "#3178C6",   // TypeScript blue
      py: "#3776AB",   // Python blue
      java: "#E76F00", // Java orange
      css: "#1572B6",  // CSS blue
      html: "#E34F26", // HTML orange
      yml: "#CB171E",  // YAML red
      sql: "#E38A00"   // SQL orange
    };
    return colorMap[ext || ""] || "#9CA3AF";
  }
}
