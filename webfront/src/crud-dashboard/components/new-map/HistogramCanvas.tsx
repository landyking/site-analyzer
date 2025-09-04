import React, { useRef, useEffect } from 'react';

type HistogramCanvasProps = {
  frequency: number[];
  edges: number[];
  width?: number;
  height?: number;
  color?: string;
};

const HistogramCanvas: React.FC<HistogramCanvasProps> = ({ frequency, edges, width = 600, height = 140, color = '#1976d2' }) => {
  const PAD_LEFT = 24;
  const PAD_RIGHT = 20;
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    ctx.clearRect(0, 0, width, height);

    // Find max frequency for scaling
    const maxY = Math.max(...frequency, 1);

    // Draw bars
    for (let i = 0; i < frequency.length; i++) {
      const x0 = PAD_LEFT + ((edges[i] - edges[0]) / (edges[edges.length - 1] - edges[0])) * (width - PAD_LEFT - PAD_RIGHT);
      const x1 = PAD_LEFT + ((edges[i + 1] - edges[0]) / (edges[edges.length - 1] - edges[0])) * (width - PAD_LEFT - PAD_RIGHT);
      const barW = x1 - x0;
      const barH = (frequency[i] / maxY) * (height - 28); // leave more space for labels
      ctx.fillStyle = color;
      ctx.globalAlpha = 0.7;
      ctx.fillRect(x0, height - 20 - barH, barW, barH);
    }

    // Draw axes (simple)
    ctx.globalAlpha = 1;
    ctx.strokeStyle = '#888';
    ctx.lineWidth = 1;
    // x axis
    ctx.beginPath();
    ctx.moveTo(PAD_LEFT, height - 20.5);
    ctx.lineTo(width - PAD_RIGHT, height - 20.5);
    ctx.stroke();

    // y axis
    ctx.beginPath();
    ctx.moveTo(PAD_LEFT + 0.5, height - 20);
    ctx.lineTo(PAD_LEFT + 0.5, 10);
    ctx.stroke();

    // y axis title (count)
  ctx.save();
  ctx.font = '12px sans-serif';
  ctx.fillStyle = '#444';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'bottom';
  // Move the title closer to the y-axis (smaller offset)
  ctx.translate(PAD_LEFT - 8, height / 2);
  ctx.rotate(-Math.PI / 2);
  ctx.fillText('frequency', 0, 0);
  ctx.restore();

    // Draw x-axis labels (bin edges)
    ctx.font = '11px sans-serif';
    ctx.fillStyle = '#444';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    for (let i = 0; i < edges.length; i++) {
      const x = PAD_LEFT + ((edges[i] - edges[0]) / (edges[edges.length - 1] - edges[0])) * (width - PAD_LEFT - PAD_RIGHT);
      // Only show every Nth label if too many
      let show = true;
      if (edges.length > 16 && i % 2 !== 0) show = false;
      if (edges.length > 32 && i % 4 !== 0) show = false;
      if (show) {
        ctx.fillText(edges[i].toFixed(2), x, height - 18);
      }
    }
  }, [frequency, edges, width, height, color]);

  return <canvas ref={canvasRef} width={width} height={height} style={{ display: 'block', maxWidth: '100%' }} />;
};

export default HistogramCanvas;
