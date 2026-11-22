// Minimal CSS/SVG compositions used as card artwork. Colors come from theme tokens via Tailwind classes / currentColor.
const NODES = [[20, 30], [45, 15], [70, 35], [30, 65], [58, 60], [82, 72], [12, 82]];
const EDGES = [[0, 1], [1, 2], [0, 3], [3, 4], [4, 2], [4, 5], [3, 6]];

export function SemanticVisual() {
  return (
    <svg viewBox="0 0 100 100" className="h-full w-full text-legal-blue" aria-hidden="true" preserveAspectRatio="xMidYMid slice">
      {EDGES.map(([a, b], i) => (
        <line key={i} x1={NODES[a][0]} y1={NODES[a][1]} x2={NODES[b][0]} y2={NODES[b][1]} stroke="currentColor" strokeOpacity="0.3" strokeWidth="0.5" />
      ))}
      {NODES.map(([x, y], i) => <circle key={i} cx={x} cy={y} r={i === 4 ? 4 : 2.5} fill="currentColor" fillOpacity={i === 4 ? 1 : 0.55} />)}
    </svg>
  );
}

export function HybridVisual() {
  return (
    <svg viewBox="0 0 100 100" className="h-full w-full text-legal-blue" aria-hidden="true" preserveAspectRatio="xMidYMid slice">
      <path d="M0 28 C 40 28, 40 50, 70 50" fill="none" stroke="currentColor" strokeWidth="1.5" />
      <path d="M0 72 C 40 72, 40 50, 70 50" fill="none" stroke="currentColor" strokeOpacity="0.45" strokeWidth="1.5" />
      <path d="M70 50 L100 50" fill="none" stroke="currentColor" strokeWidth="3" />
      <circle cx="70" cy="50" r="4" fill="currentColor" />
      <text x="4" y="22" fontSize="5" fill="currentColor">Dense</text>
      <text x="4" y="86" fontSize="5" fill="currentColor">BM25</text>
    </svg>
  );
}

export function ShapVisual() {
  const bars = [["+", 70], ["+", 45], ["+", 30], ["−", 18], ["−", 8]];
  return (
    <div className="flex h-full flex-col justify-center gap-3 px-8" aria-hidden="true">
      {bars.map(([sign, w], i) => (
        <div key={i} className="flex h-3 items-center">
          <div className="flex w-1/2 justify-end">{sign === "−" && <div className="h-3 rounded-sm bg-black/30" style={{ width: `${w}%` }} />}</div>
          <div className="h-5 w-px bg-black/20" />
          <div className="w-1/2">{sign === "+" && <div className="h-3 rounded-sm bg-legal-blue" style={{ width: `${w}%` }} />}</div>
        </div>
      ))}
    </div>
  );
}

export function EvidenceVisual() {
  return (
    <div className="mx-auto flex h-full w-3/5 flex-col justify-center gap-2 px-2" aria-hidden="true">
      {[100, 90, 95].map((w, i) => <div key={i} className="h-2 rounded-sm bg-black/15" style={{ width: `${w}%` }} />)}
      {[100, 80].map((w, i) => <div key={i} className="h-2 rounded-sm bg-legal-blue/40" style={{ width: `${w}%` }} />)}
      {[70, 95].map((w, i) => <div key={i} className="h-2 rounded-sm bg-black/15" style={{ width: `${w}%` }} />)}
    </div>
  );
}

export function ReferenceVisual() {
  return (
    <div className="flex h-full flex-col items-start justify-center gap-1 px-8 text-2xl font-bold tracking-tight md:text-3xl" aria-hidden="true">
      <span className="text-legal-blue">Article 14</span>
      <span className="text-black/60">Article 21</span>
      <span className="text-black/30">Section 302</span>
    </div>
  );
}

export function RankedVisual() {
  return (
    <div className="relative mx-auto h-full w-3/5" aria-hidden="true">
      {[0, 1, 2].map((i) => (
        <div key={i} className="absolute left-0 right-0 flex h-12 items-center justify-between rounded border border-black/10 bg-legal-white px-3 text-sm font-semibold"
          style={{ top: `${20 + i * 22}%`, transform: `translateX(${i * 8}px)`, zIndex: 3 - i }}>
          <span>0{i + 1}</span><span className="h-2 rounded-sm bg-legal-blue/60" style={{ width: `${60 - i * 15}%` }} />
        </div>
      ))}
    </div>
  );
}
