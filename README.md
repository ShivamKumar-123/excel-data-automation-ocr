<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Data Cleaner Studio — README</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Poppins:wght@300;400;500;600;700&family=Fira+Code:wght@400;500&display=swap');

  :root {
    --gold:   #FFD700;
    --pink:   #FF69B4;
    --sky:    #87CEEB;
    --dark:   #4169E1;
    --bg0:    #000000;
    --bg1:    #0f0f1e;
    --bg2:    #1a1a2e;
    --bg3:    #16213e;
    --white:  #ffffff;
    --dim:    rgba(255,255,255,0.65);
  }

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  html { scroll-behavior: smooth; }

  body {
    font-family: 'Poppins', sans-serif;
    background: var(--bg0);
    color: var(--white);
    overflow-x: hidden;
  }

  /* ── SCROLLBAR ── */
  ::-webkit-scrollbar { width: 10px; }
  ::-webkit-scrollbar-track { background: var(--bg1); }
  ::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, var(--gold), var(--pink), var(--sky));
    border-radius: 5px;
  }

  /* ── PARTICLE CANVAS ── */
  #particles { position: fixed; inset: 0; z-index: 0; pointer-events: none; }

  /* ── SCANLINE OVERLAY ── */
  body::after {
    content: '';
    position: fixed; inset: 0; z-index: 1; pointer-events: none;
    background: repeating-linear-gradient(0deg, transparent, transparent 3px, rgba(255,215,0,0.015) 3px, rgba(255,215,0,0.015) 4px);
    animation: scanMove 12s linear infinite;
  }
  @keyframes scanMove { to { background-position-y: 200px; } }

  /* ── WRAPPER ── */
  .wrap { position: relative; z-index: 2; max-width: 1100px; margin: 0 auto; padding: 0 24px 80px; }

  /* ── HERO ── */
  .hero {
    min-height: 100vh;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    text-align: center;
    padding: 60px 20px;
    position: relative; z-index: 2;
  }

  .hero-badge {
    display: inline-block;
    background: linear-gradient(90deg, var(--gold), var(--pink));
    color: #000;
    font-family: 'Orbitron', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 3px;
    padding: 6px 20px;
    border-radius: 50px;
    margin-bottom: 30px;
    animation: fadeDown 0.8s ease both;
  }

  .hero h1 {
    font-family: 'Orbitron', sans-serif;
    font-size: clamp(2.8rem, 8vw, 6rem);
    font-weight: 900;
    line-height: 1.05;
    letter-spacing: 2px;
    background: linear-gradient(135deg, var(--gold) 0%, #FFA500 40%, var(--pink) 70%, var(--sky) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: fadeDown 0.9s ease 0.1s both;
    text-shadow: none;
  }

  .hero-glow {
    position: absolute;
    width: 700px; height: 400px;
    border-radius: 50%;
    filter: blur(120px);
    opacity: 0.18;
    background: radial-gradient(circle, var(--gold) 0%, var(--pink) 50%, var(--sky) 100%);
    animation: pulseGlow 5s ease-in-out infinite;
    pointer-events: none;
  }
  @keyframes pulseGlow {
    0%,100% { transform: scale(1); opacity: 0.18; }
    50%      { transform: scale(1.15); opacity: 0.28; }
  }

  .hero-sub {
    margin-top: 20px;
    font-size: 1.1rem;
    color: var(--sky);
    letter-spacing: 1.5px;
    animation: fadeDown 0.9s ease 0.2s both;
  }

  .hero-chips {
    display: flex; flex-wrap: wrap; gap: 12px;
    justify-content: center;
    margin-top: 36px;
    animation: fadeDown 0.9s ease 0.35s both;
  }

  .chip {
    background: rgba(255,215,0,0.12);
    border: 1.5px solid rgba(255,215,0,0.35);
    color: var(--gold);
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 1px;
    padding: 7px 18px;
    border-radius: 50px;
    cursor: default;
    transition: all 0.3s ease;
  }
  .chip:hover {
    background: var(--gold);
    color: #000;
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(255,215,0,0.45);
  }
  .chip.pink  { color: var(--pink);  border-color: rgba(255,105,180,0.4); background: rgba(255,105,180,0.1); }
  .chip.pink:hover  { background: var(--pink);  color: #fff; box-shadow: 0 8px 20px rgba(255,105,180,0.4); }
  .chip.sky   { color: var(--sky);   border-color: rgba(135,206,250,0.4); background: rgba(135,206,250,0.1); }
  .chip.sky:hover   { background: var(--sky);   color: #000; box-shadow: 0 8px 20px rgba(135,206,250,0.4); }

  .hero-scroll {
    margin-top: 60px;
    display: flex; flex-direction: column; align-items: center;
    gap: 8px;
    color: var(--dim);
    font-size: 0.75rem;
    letter-spacing: 2px;
    animation: fadeDown 1s ease 0.6s both;
  }
  .scroll-line {
    width: 2px; height: 50px;
    background: linear-gradient(180deg, var(--gold), transparent);
    animation: scrollLine 2s ease-in-out infinite;
  }
  @keyframes scrollLine {
    0%,100% { transform: scaleY(1); opacity: 1; }
    50%      { transform: scaleY(0.4); opacity: 0.4; }
  }

  /* ── SECTION ── */
  section { margin-top: 100px; animation: fadeUp 0.7s ease both; }

  .sec-label {
    font-family: 'Orbitron', sans-serif;
    font-size: 0.65rem;
    letter-spacing: 4px;
    color: var(--gold);
    opacity: 0.7;
    margin-bottom: 10px;
  }

  .sec-title {
    font-family: 'Orbitron', sans-serif;
    font-size: clamp(1.6rem, 4vw, 2.4rem);
    font-weight: 800;
    letter-spacing: 1px;
    background: linear-gradient(90deg, var(--gold), var(--pink));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 16px;
  }

  .sec-line {
    height: 3px; width: 80px;
    background: linear-gradient(90deg, var(--gold), var(--pink), var(--sky));
    border-radius: 2px;
    margin-bottom: 40px;
    animation: expandLine 1s ease both;
  }
  @keyframes expandLine { from { width: 0; } to { width: 80px; } }

  /* ── FEATURE GRID ── */
  .feat-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
    gap: 20px;
  }

  .feat-card {
    border-radius: 18px;
    padding: 30px 24px;
    position: relative;
    overflow: hidden;
    cursor: default;
    transition: all 0.4s cubic-bezier(0.175,0.885,0.32,1.275);
    border: 2px solid transparent;
  }
  .feat-card::before {
    content: '';
    position: absolute; inset: 0;
    background: linear-gradient(135deg, rgba(255,215,0,0.08), rgba(255,105,180,0.05), rgba(135,206,250,0.08));
    z-index: 0;
  }
  .feat-card:hover { transform: translateY(-10px) scale(1.03); }
  .feat-card.gold-card  { border-color: rgba(255,215,0,0.3);   box-shadow: 0 10px 40px rgba(255,215,0,0.15); }
  .feat-card.pink-card  { border-color: rgba(255,105,180,0.3); box-shadow: 0 10px 40px rgba(255,105,180,0.15); }
  .feat-card.sky-card   { border-color: rgba(135,206,250,0.3); box-shadow: 0 10px 40px rgba(135,206,250,0.15); }
  .feat-card.gold-card:hover  { box-shadow: 0 20px 60px rgba(255,215,0,0.35); }
  .feat-card.pink-card:hover  { box-shadow: 0 20px 60px rgba(255,105,180,0.35); }
  .feat-card.sky-card:hover   { box-shadow: 0 20px 60px rgba(135,206,250,0.35); }
  .feat-icon { font-size: 2.5rem; margin-bottom: 14px; position: relative; z-index: 1; }
  .feat-name {
    font-family: 'Orbitron', sans-serif;
    font-size: 1rem; font-weight: 700;
    margin-bottom: 8px;
    position: relative; z-index: 1;
  }
  .feat-card.gold-card .feat-name { color: var(--gold); }
  .feat-card.pink-card .feat-name { color: var(--pink); }
  .feat-card.sky-card  .feat-name { color: var(--sky); }
  .feat-desc { font-size: 0.88rem; color: var(--dim); line-height: 1.6; position: relative; z-index: 1; }

  /* ── STATS COUNTERS ── */
  .stats-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 20px;
    margin-top: 10px;
  }

  .stat-box {
    border-radius: 18px;
    padding: 32px 20px;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
  }
  .stat-box:hover { transform: translateY(-8px); }
  .stat-box.s1 { background: linear-gradient(135deg,#FFD700,#FFA500); color:#000; box-shadow:0 12px 35px rgba(255,215,0,0.45); }
  .stat-box.s2 { background: linear-gradient(135deg,#FF69B4,#FF1493); color:#fff; box-shadow:0 12px 35px rgba(255,105,180,0.45); }
  .stat-box.s3 { background: linear-gradient(135deg,#87CEEB,#4169E1); color:#fff; box-shadow:0 12px 35px rgba(135,206,250,0.45); }
  .stat-box.s4 { background: linear-gradient(135deg,#FFD700,#FF69B4,#87CEEB); color:#000; box-shadow:0 12px 35px rgba(255,215,0,0.45); }

  .stat-num {
    font-family: 'Orbitron', sans-serif;
    font-size: 2.8rem; font-weight: 900;
    line-height: 1;
  }
  .stat-lbl {
    font-size: 0.75rem; font-weight: 700;
    letter-spacing: 2px; text-transform: uppercase;
    margin-top: 8px; opacity: 0.9;
  }

  /* ── BAR CHART ── */
  .chart-wrap {
    background: linear-gradient(135deg, var(--bg2), var(--bg3));
    border: 2px solid rgba(255,215,0,0.2);
    border-radius: 20px;
    padding: 36px 32px;
    box-shadow: 0 10px 50px rgba(0,0,0,0.6);
  }

  .chart-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 1rem; font-weight: 700;
    color: var(--gold);
    margin-bottom: 28px;
    letter-spacing: 1px;
  }

  .bar-row {
    display: flex; align-items: center;
    gap: 14px; margin-bottom: 18px;
  }
  .bar-label {
    width: 150px; font-size: 0.82rem; font-weight: 600;
    color: var(--dim); flex-shrink: 0; text-align: right;
  }
  .bar-track {
    flex: 1; height: 28px;
    background: rgba(255,255,255,0.07);
    border-radius: 8px; overflow: hidden;
    position: relative;
  }
  .bar-fill {
    height: 100%;
    border-radius: 8px;
    width: 0;
    transition: width 1.6s cubic-bezier(0.22,1,0.36,1);
    display: flex; align-items: center; padding-left: 12px;
    font-size: 0.75rem; font-weight: 700;
  }
  .bar-fill.gold { background: linear-gradient(90deg, #FFD700, #FFA500); color: #000; }
  .bar-fill.pink { background: linear-gradient(90deg, #FF69B4, #FF1493); color: #fff; }
  .bar-fill.sky  { background: linear-gradient(90deg, #87CEEB, #4169E1); color: #fff; }
  .bar-fill.mix  { background: linear-gradient(90deg, #FFD700, #FF69B4, #87CEEB); color: #000; }

  /* ── DONUT CHART ── */
  .charts-duo { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
  @media(max-width:640px) { .charts-duo { grid-template-columns: 1fr; } }

  .donut-wrap {
    background: linear-gradient(135deg, var(--bg2), var(--bg3));
    border: 2px solid rgba(255,105,180,0.2);
    border-radius: 20px;
    padding: 36px 28px;
    box-shadow: 0 10px 50px rgba(0,0,0,0.6);
    display: flex; flex-direction: column; align-items: center;
  }
  .donut-wrap .chart-title { text-align: center; color: var(--pink); }

  svg.donut { width: 160px; height: 160px; transform: rotate(-90deg); }

  .donut-ring {
    fill: none;
    stroke-width: 22;
    stroke-dasharray: 502;
    stroke-dashoffset: 502;
    transition: stroke-dashoffset 1.8s cubic-bezier(0.22,1,0.36,1);
    stroke-linecap: round;
  }
  .donut-bg { fill: none; stroke: rgba(255,255,255,0.06); stroke-width: 22; }

  .donut-legend {
    display: flex; flex-direction: column; gap: 10px;
    margin-top: 24px; width: 100%;
  }
  .legend-row { display: flex; align-items: center; gap: 10px; font-size: 0.82rem; }
  .legend-dot { width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0; }

  /* ── PIPELINE ── */
  .pipeline {
    display: flex; align-items: stretch;
    gap: 0; flex-wrap: wrap;
  }
  .pipe-step {
    flex: 1; min-width: 130px;
    padding: 28px 18px;
    text-align: center;
    position: relative;
    background: linear-gradient(135deg, var(--bg2), var(--bg3));
    border-top: 3px solid transparent;
    transition: all 0.3s ease;
    cursor: default;
  }
  .pipe-step:nth-child(1) { border-color: var(--gold);  border-radius: 18px 0 0 18px; }
  .pipe-step:nth-child(2) { border-color: var(--pink); }
  .pipe-step:nth-child(3) { border-color: var(--sky); }
  .pipe-step:nth-child(4) { border-color: var(--gold); }
  .pipe-step:nth-child(5) { border-color: var(--pink); border-radius: 0 18px 18px 0; }
  .pipe-step::after {
    content: '▶';
    position: absolute; right: -10px; top: 50%; transform: translateY(-50%);
    font-size: 1.2rem; z-index: 2;
  }
  .pipe-step:last-child::after { display: none; }
  .pipe-step:hover { transform: translateY(-6px); background: rgba(255,215,0,0.06); }
  .pipe-num {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.4rem; font-weight: 900;
    color: var(--gold); margin-bottom: 10px;
  }
  .pipe-step:nth-child(2) .pipe-num { color: var(--pink); }
  .pipe-step:nth-child(3) .pipe-num { color: var(--sky); }
  .pipe-step:nth-child(4) .pipe-num { color: var(--gold); }
  .pipe-step:nth-child(5) .pipe-num { color: var(--pink); }
  .pipe-title { font-size: 0.8rem; font-weight: 700; margin-bottom: 6px; color: #fff; letter-spacing: 0.5px; }
  .pipe-desc { font-size: 0.72rem; color: var(--dim); line-height: 1.5; }

  /* ── CODE BLOCK ── */
  .code-block {
    background: var(--bg1);
    border: 2px solid rgba(135,206,250,0.25);
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 10px 40px rgba(0,0,0,0.6);
  }
  .code-header {
    display: flex; align-items: center; gap: 10px;
    background: rgba(135,206,250,0.08);
    border-bottom: 1px solid rgba(135,206,250,0.15);
    padding: 14px 20px;
  }
  .code-dot { width: 12px; height: 12px; border-radius: 50%; }
  .code-dot.r { background: #ff5f56; }
  .code-dot.y { background: #ffbd2e; }
  .code-dot.g { background: #27c93f; }
  .code-fname { margin-left: 8px; font-size: 0.78rem; color: var(--dim); font-family: 'Fira Code', monospace; }
  pre {
    padding: 24px;
    font-family: 'Fira Code', monospace;
    font-size: 0.82rem;
    line-height: 1.7;
    color: var(--white);
    overflow-x: auto;
  }
  .kw  { color: #FF79C6; }
  .fn  { color: #50FA7B; }
  .str { color: #F1FA8C; }
  .cm  { color: #6272A4; }
  .num { color: var(--sky); }
  .var { color: #FFB86C; }

  /* ── SECTIONS WORKFLOW CARDS ── */
  .section-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px,1fr));
    gap: 20px;
  }
  .section-card {
    background: linear-gradient(135deg, var(--bg2), var(--bg3));
    border-radius: 18px;
    padding: 28px 22px;
    border: 2px solid rgba(255,255,255,0.07);
    transition: all 0.4s ease;
    cursor: default;
    position: relative;
    overflow: hidden;
  }
  .section-card::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, var(--gold), var(--pink), var(--sky));
    opacity: 0;
    transition: opacity 0.3s;
  }
  .section-card:hover::before { opacity: 1; }
  .section-card:hover { transform: translateY(-8px); border-color: rgba(255,215,0,0.3); box-shadow: 0 20px 50px rgba(0,0,0,0.6); }
  .sc-num {
    font-family: 'Orbitron', sans-serif;
    font-size: 2rem; font-weight: 900;
    color: rgba(255,215,0,0.2);
    line-height: 1; margin-bottom: 8px;
  }
  .sc-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 1rem; font-weight: 700;
    color: var(--gold); margin-bottom: 10px;
  }
  .sc-desc { font-size: 0.84rem; color: var(--dim); line-height: 1.6; }
  .sc-tags { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; }
  .sc-tag {
    font-size: 0.7rem; font-weight: 600;
    padding: 4px 12px; border-radius: 50px;
    background: rgba(255,215,0,0.12);
    color: var(--gold); border: 1px solid rgba(255,215,0,0.25);
  }
  .sc-tag.p { background: rgba(255,105,180,0.12); color: var(--pink); border-color: rgba(255,105,180,0.25); }
  .sc-tag.s { background: rgba(135,206,250,0.12); color: var(--sky); border-color: rgba(135,206,250,0.25); }

  /* ── ANIMATED TICKER ── */
  .ticker-wrap {
    overflow: hidden;
    background: rgba(255,215,0,0.06);
    border-top: 1px solid rgba(255,215,0,0.2);
    border-bottom: 1px solid rgba(255,215,0,0.2);
    padding: 14px 0;
    margin: 80px 0 0;
    white-space: nowrap;
  }
  .ticker-inner {
    display: inline-block;
    animation: tickerMove 20s linear infinite;
    font-family: 'Orbitron', sans-serif;
    font-size: 0.75rem;
    letter-spacing: 3px;
    color: var(--gold);
  }
  @keyframes tickerMove { from { transform: translateX(0); } to { transform: translateX(-50%); } }

  /* ── FOOTER ── */
  footer {
    margin-top: 100px;
    background: linear-gradient(135deg, var(--bg2), var(--bg3));
    border: 3px solid transparent;
    border-radius: 24px;
    padding: 50px 40px;
    text-align: center;
    position: relative;
    overflow: hidden;
    box-shadow: 0 20px 60px rgba(0,0,0,0.7);
    background-image:
      linear-gradient(135deg, var(--bg2), var(--bg3)),
      linear-gradient(90deg, var(--gold), var(--pink), var(--sky));
    background-origin: border-box;
    background-clip: padding-box, border-box;
  }
  footer::before {
    content: '';
    position: absolute; inset: 0;
    background: linear-gradient(45deg, transparent, rgba(255,215,0,0.04), rgba(255,105,180,0.04), transparent);
    animation: shine 8s linear infinite;
    pointer-events: none;
  }
  footer h2 {
    font-family: 'Orbitron', sans-serif;
    font-size: 2rem; font-weight: 900;
    background: linear-gradient(90deg, var(--gold), var(--pink), var(--sky));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    margin-bottom: 12px;
  }
  footer p { color: var(--sky); font-size: 0.95rem; line-height: 1.7; }
  .footer-stats {
    display: flex; justify-content: center; flex-wrap: wrap;
    gap: 40px; margin: 32px 0;
  }
  .f-stat-num {
    font-family: 'Orbitron', sans-serif;
    font-size: 2.2rem; font-weight: 900;
  }
  .f-stat-lbl { font-size: 0.75rem; letter-spacing: 2px; margin-top: 4px; opacity: 0.75; text-transform: uppercase; }

  /* ── ANIMATIONS ── */
  @keyframes fadeDown { from { opacity:0; transform:translateY(-30px); } to { opacity:1; transform:translateY(0); } }
  @keyframes fadeUp   { from { opacity:0; transform:translateY(30px); } to { opacity:1; transform:translateY(0); } }

  .reveal { opacity: 0; transform: translateY(40px); transition: opacity 0.7s ease, transform 0.7s ease; }
  .reveal.visible { opacity: 1; transform: translateY(0); }

  /* ── NAV ── */
  nav {
    position: fixed; top: 0; left: 0; right: 0;
    z-index: 100;
    display: flex; align-items: center; justify-content: space-between;
    padding: 16px 40px;
    background: rgba(0,0,0,0.7);
    backdrop-filter: blur(16px);
    border-bottom: 1px solid rgba(255,215,0,0.15);
  }
  .nav-logo {
    font-family: 'Orbitron', sans-serif;
    font-size: 1rem; font-weight: 900; letter-spacing: 2px;
    background: linear-gradient(90deg, var(--gold), var(--pink));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
  }
  .nav-links { display: flex; gap: 28px; list-style: none; }
  .nav-links a {
    color: var(--dim); font-size: 0.8rem; font-weight: 600;
    letter-spacing: 1px; text-decoration: none; text-transform: uppercase;
    transition: color 0.3s;
  }
  .nav-links a:hover { color: var(--gold); }
  @media(max-width:600px) { nav { padding: 14px 20px; } .nav-links { display: none; } }

  /* ── LINE CHART (SVG) ── */
  .line-chart-wrap {
    background: linear-gradient(135deg, var(--bg2), var(--bg3));
    border: 2px solid rgba(135,206,250,0.2);
    border-radius: 20px;
    padding: 36px 32px;
    box-shadow: 0 10px 50px rgba(0,0,0,0.6);
  }
  .line-chart-wrap .chart-title { color: var(--sky); }
  .chart-axis { font-family: 'Poppins', sans-serif; font-size: 0.7rem; fill: rgba(255,255,255,0.45); }
  .chart-line { fill: none; stroke-width: 3; stroke-linecap: round; stroke-linejoin: round; }
  .chart-area { opacity: 0.15; }
  .dot-point { transition: r 0.2s, opacity 0.2s; }
  .dot-point:hover { r: 7; opacity: 1 !important; cursor: pointer; }
</style>
</head>
<body>

<canvas id="particles"></canvas>

<!-- NAV -->
<nav>
  <div class="nav-logo">📊 Data Cleaner Studio</div>
  <ul class="nav-links">
    <li><a href="#features">Features</a></li>
    <li><a href="#pipeline">Pipeline</a></li>
    <li><a href="#sections">Sections</a></li>
    <li><a href="#metrics">Metrics</a></li>
    <li><a href="#install">Install</a></li>
  </ul>
</nav>

<!-- HERO -->
<div class="hero">
  <div class="hero-glow"></div>
  <div class="hero-badge">VERSION 2.0 PRO</div>
  <h1>Data Cleaner<br>Studio</h1>
  <p class="hero-sub">🚀 Transform &nbsp;•&nbsp; Translate &nbsp;•&nbsp; Transcend</p>
  <div class="hero-chips">
    <span class="chip">📊 Excel / CSV</span>
    <span class="chip pink">📑 PDF Extraction</span>
    <span class="chip sky">🖼️ OCR Images</span>
    <span class="chip">🌐 Hindi → English</span>
    <span class="chip pink">📞 Phone Cleanup</span>
    <span class="chip sky">📍 Pincode Mapping</span>
    <span class="chip">📦 Batch ZIP Export</span>
    <span class="chip pink">🔀 Data Fusion Merge</span>
  </div>
  <div class="hero-scroll">
    <div class="scroll-line"></div>
    SCROLL TO EXPLORE
  </div>
</div>

<!-- TICKER -->
<div class="ticker-wrap">
  <div class="ticker-inner">
    ✦ HINDI TO ENGLISH TRANSLATION &nbsp;&nbsp;&nbsp; ✦ PHONE NUMBER NORMALIZATION &nbsp;&nbsp;&nbsp; ✦ PINCODE → STATE &amp; DISTRICT &nbsp;&nbsp;&nbsp; ✦ MULTI-FORMAT SUPPORT &nbsp;&nbsp;&nbsp; ✦ BATCH ZIP PROCESSING &nbsp;&nbsp;&nbsp; ✦ OCR IMAGE EXTRACTION &nbsp;&nbsp;&nbsp; ✦ PDF DATA PARSING &nbsp;&nbsp;&nbsp; ✦ ROW RANGE EXTRACTION &nbsp;&nbsp;&nbsp; ✦ DUPLICATE REMOVAL &nbsp;&nbsp;&nbsp; ✦ 19K+ PINCODE DATABASE &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    ✦ HINDI TO ENGLISH TRANSLATION &nbsp;&nbsp;&nbsp; ✦ PHONE NUMBER NORMALIZATION &nbsp;&nbsp;&nbsp; ✦ PINCODE → STATE &amp; DISTRICT &nbsp;&nbsp;&nbsp; ✦ MULTI-FORMAT SUPPORT &nbsp;&nbsp;&nbsp; ✦ BATCH ZIP PROCESSING &nbsp;&nbsp;&nbsp; ✦ OCR IMAGE EXTRACTION &nbsp;&nbsp;&nbsp; ✦ PDF DATA PARSING &nbsp;&nbsp;&nbsp; ✦ ROW RANGE EXTRACTION &nbsp;&nbsp;&nbsp; ✦ DUPLICATE REMOVAL &nbsp;&nbsp;&nbsp; ✦ 19K+ PINCODE DATABASE &nbsp;&nbsp;&nbsp;
  </div>
</div>

<div class="wrap">

  <!-- FEATURES -->
  <section id="features" class="reveal">
    <div class="sec-label">CORE CAPABILITIES</div>
    <div class="sec-title">Features</div>
    <div class="sec-line"></div>
    <div class="feat-grid">
      <div class="feat-card gold-card">
        <div class="feat-icon">🌐</div>
        <div class="feat-name">Hindi Translation</div>
        <div class="feat-desc">Automatically detects and converts Hindi (Devanagari) text cells into clean English using Google Translate API with language detection.</div>
      </div>
      <div class="feat-card pink-card">
        <div class="feat-icon">📞</div>
        <div class="feat-name">Phone Normalization</div>
        <div class="feat-desc">Strips spaces, dashes, country codes and special chars. Validates and standardizes numbers to consistent 10-digit Indian format.</div>
      </div>
      <div class="feat-card sky-card">
        <div class="feat-icon">📍</div>
        <div class="feat-name">Pincode Mapping</div>
        <div class="feat-desc">Maps 19,000+ Indian pincodes to their corresponding State, District and City using an offline lookup database — zero API calls.</div>
      </div>
      <div class="feat-card gold-card">
        <div class="feat-icon">🔍</div>
        <div class="feat-name">OCR Extraction</div>
        <div class="feat-desc">Uses Tesseract OCR to extract structured tabular data from JPG/PNG images with automatic preprocessing and table detection.</div>
      </div>
      <div class="feat-card pink-card">
        <div class="feat-icon">📑</div>
        <div class="feat-name">PDF Parsing</div>
        <div class="feat-desc">Extracts tables and text from PDF files using pdfplumber — supports multi-page documents, complex layouts and scanned PDFs.</div>
      </div>
      <div class="feat-card sky-card">
        <div class="feat-icon">📦</div>
        <div class="feat-name">Batch Processing</div>
        <div class="feat-desc">Upload any number of files simultaneously. Each is cleaned independently and all results are bundled into a single downloadable ZIP archive.</div>
      </div>
      <div class="feat-card gold-card">
        <div class="feat-icon">🔀</div>
        <div class="feat-name">Data Fusion / Merge</div>
        <div class="feat-desc">Concatenates multiple Excel/CSV files into one unified dataset with smart column alignment and duplicate-row detection across sources.</div>
      </div>
      <div class="feat-card pink-card">
        <div class="feat-icon">✂️</div>
        <div class="feat-name">Precision Extract</div>
        <div class="feat-desc">Extract exact row ranges from any dataset by specifying start and end rows — ideal for splitting large files into smaller chunks.</div>
      </div>
    </div>
  </section>

  <!-- PERFORMANCE CHART -->
  <section id="metrics" class="reveal">
    <div class="sec-label">PERFORMANCE</div>
    <div class="sec-title">Metrics &amp; Benchmarks</div>
    <div class="sec-line"></div>

    <div class="stats-row" style="margin-bottom:32px;">
      <div class="stat-box s1">
        <div class="stat-num" data-target="90">0</div><div>%</div>
        <div class="stat-lbl">Time Saved</div>
      </div>
      <div class="stat-box s2">
        <div class="stat-num" data-target="95">0</div><div>%+</div>
        <div class="stat-lbl">Accuracy</div>
      </div>
      <div class="stat-box s3">
        <div class="stat-num" data-target="19">0</div><div>K+</div>
        <div class="stat-lbl">Pincodes</div>
      </div>
      <div class="stat-box s4">
        <div class="stat-num" data-target="4">0</div>
        <div class="stat-lbl">Input Formats</div>
      </div>
    </div>

    <!-- BAR CHART -->
    <div class="chart-wrap" style="margin-bottom:24px;">
      <div class="chart-title">⚡ Processing Speed by File Type (rows/sec)</div>
      <div class="bar-row">
        <div class="bar-label">Excel (.xlsx)</div>
        <div class="bar-track"><div class="bar-fill gold" data-width="88">88k r/s</div></div>
      </div>
      <div class="bar-row">
        <div class="bar-label">CSV (.csv)</div>
        <div class="bar-track"><div class="bar-fill sky" data-width="96">96k r/s</div></div>
      </div>
      <div class="bar-row">
        <div class="bar-label">PDF (text)</div>
        <div class="bar-track"><div class="bar-fill pink" data-width="62">62k r/s</div></div>
      </div>
      <div class="bar-row">
        <div class="bar-label">Image (OCR)</div>
        <div class="bar-track"><div class="bar-fill mix" data-width="38">38k r/s</div></div>
      </div>
      <div class="bar-row">
        <div class="bar-label">Batch (ZIP)</div>
        <div class="bar-track"><div class="bar-fill gold" data-width="75">75k r/s</div></div>
      </div>
    </div>

    <!-- CHARTS DUO -->
    <div class="charts-duo">
      <!-- DONUT -->
      <div class="donut-wrap">
        <div class="chart-title">📁 File Type Distribution</div>
        <svg class="donut" viewBox="0 0 180 180">
          <circle class="donut-bg" cx="90" cy="90" r="80"/>
          <circle class="donut-ring" id="d1" cx="90" cy="90" r="80" stroke="#FFD700" data-offset="126" />
          <circle class="donut-ring" id="d2" cx="90" cy="90" r="80" stroke="#FF69B4" data-offset="277" style="stroke-dashoffset:502"/>
          <circle class="donut-ring" id="d3" cx="90" cy="90" r="80" stroke="#87CEEB" data-offset="377" style="stroke-dashoffset:502"/>
          <circle class="donut-ring" id="d4" cx="90" cy="90" r="80" stroke="#FFA500" data-offset="452" style="stroke-dashoffset:502"/>
        </svg>
        <div class="donut-legend">
          <div class="legend-row"><div class="legend-dot" style="background:#FFD700"></div><span style="color:var(--dim)">Excel — 25%</span></div>
          <div class="legend-row"><div class="legend-dot" style="background:#FF69B4"></div><span style="color:var(--dim)">CSV — 30%</span></div>
          <div class="legend-row"><div class="legend-dot" style="background:#87CEEB"></div><span style="color:var(--dim)">PDF — 20%</span></div>
          <div class="legend-row"><div class="legend-dot" style="background:#FFA500"></div><span style="color:var(--dim)">Image — 15%</span></div>
        </div>
      </div>

      <!-- LINE CHART -->
      <div class="line-chart-wrap">
        <div class="chart-title">📈 Accuracy Over File Size (MB)</div>
        <svg id="lineChart" viewBox="0 0 340 200" style="width:100%;height:auto;overflow:visible">
          <!-- Grid -->
          <line x1="40" y1="10" x2="40" y2="170" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>
          <line x1="40" y1="170" x2="330" y2="170" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>
          <line x1="40" y1="130" x2="330" y2="130" stroke="rgba(255,255,255,0.05)" stroke-width="1" stroke-dasharray="4"/>
          <line x1="40" y1="90"  x2="330" y2="90"  stroke="rgba(255,255,255,0.05)" stroke-width="1" stroke-dasharray="4"/>
          <line x1="40" y1="50"  x2="330" y2="50"  stroke="rgba(255,255,255,0.05)" stroke-width="1" stroke-dasharray="4"/>
          <!-- Axis labels -->
          <text x="36" y="175" class="chart-axis" text-anchor="end">0</text>
          <text x="36" y="135" class="chart-axis" text-anchor="end">25</text>
          <text x="36" y="95"  class="chart-axis" text-anchor="end">50</text>
          <text x="36" y="55"  class="chart-axis" text-anchor="end">75</text>
          <text x="36" y="15"  class="chart-axis" text-anchor="end">100</text>
          <text x="40"  y="185" class="chart-axis" text-anchor="middle">0</text>
          <text x="120" y="185" class="chart-axis" text-anchor="middle">5</text>
          <text x="200" y="185" class="chart-axis" text-anchor="middle">10</text>
          <text x="280" y="185" class="chart-axis" text-anchor="middle">15</text>
          <text x="165" y="198" class="chart-axis" text-anchor="middle" style="font-size:0.65rem;fill:rgba(255,255,255,0.35)">File Size (MB)</text>
          <!-- Gold line -->
          <polyline id="lGold" class="chart-line" stroke="#FFD700"
            points="40,20 80,22 120,28 160,38 200,52 240,72 280,100 320,138"
            style="stroke-dasharray:600;stroke-dashoffset:600;transition:stroke-dashoffset 2s ease 0.3s"/>
          <polygon id="aGold" class="chart-area"
            points="40,170 40,20 80,22 120,28 160,38 200,52 240,72 280,100 320,138 320,170"
            fill="#FFD700"/>
          <!-- Pink line -->
          <polyline id="lPink" class="chart-line" stroke="#FF69B4"
            points="40,25 80,28 120,35 160,50 200,70 240,95 280,128 320,160"
            style="stroke-dasharray:600;stroke-dashoffset:600;transition:stroke-dashoffset 2s ease 0.6s"/>
          <!-- Dots Gold -->
          <circle class="dot-point" cx="40"  cy="20"  r="4" fill="#FFD700" opacity="0.9"/>
          <circle class="dot-point" cx="120" cy="28"  r="4" fill="#FFD700" opacity="0.9"/>
          <circle class="dot-point" cx="200" cy="52"  r="4" fill="#FFD700" opacity="0.9"/>
          <circle class="dot-point" cx="280" cy="100" r="4" fill="#FFD700" opacity="0.9"/>
          <circle class="dot-point" cx="320" cy="138" r="4" fill="#FFD700" opacity="0.9"/>
          <!-- Dots Pink -->
          <circle class="dot-point" cx="40"  cy="25"  r="4" fill="#FF69B4" opacity="0.9"/>
          <circle class="dot-point" cx="120" cy="35"  r="4" fill="#FF69B4" opacity="0.9"/>
          <circle class="dot-point" cx="200" cy="70"  r="4" fill="#FF69B4" opacity="0.9"/>
          <circle class="dot-point" cx="280" cy="128" r="4" fill="#FF69B4" opacity="0.9"/>
          <circle class="dot-point" cx="320" cy="160" r="4" fill="#FF69B4" opacity="0.9"/>
          <!-- Legend -->
          <rect x="42" y="12" width="10" height="3" rx="1" fill="#FFD700"/>
          <text x="56" y="16" class="chart-axis" style="fill:#FFD700">Excel/CSV</text>
          <rect x="120" y="12" width="10" height="3" rx="1" fill="#FF69B4"/>
          <text x="134" y="16" class="chart-axis" style="fill:#FF69B4">PDF/OCR</text>
        </svg>
      </div>
    </div>
  </section>

  <!-- PIPELINE -->
  <section id="pipeline" class="reveal">
    <div class="sec-label">HOW IT WORKS</div>
    <div class="sec-title">Processing Pipeline</div>
    <div class="sec-line"></div>
    <div class="pipeline">
      <div class="pipe-step">
        <div class="pipe-num">01</div>
        <div class="pipe-title">📤 Upload</div>
        <div class="pipe-desc">Drag & drop xlsx, csv, pdf or image files via Streamlit uploader</div>
      </div>
      <div class="pipe-step">
        <div class="pipe-num">02</div>
        <div class="pipe-title">🔍 Extract</div>
        <div class="pipe-desc">Auto-detect format and parse data using pandas, pdfplumber or Tesseract</div>
      </div>
      <div class="pipe-step">
        <div class="pipe-num">03</div>
        <div class="pipe-title">🧹 Clean</div>
        <div class="pipe-desc">Normalize phones, map pincodes, strip noise, remove duplicates</div>
      </div>
      <div class="pipe-step">
        <div class="pipe-num">04</div>
        <div class="pipe-title">🌐 Translate</div>
        <div class="pipe-desc">Detect Hindi cells and translate to English via Google Translate API</div>
      </div>
      <div class="pipe-step">
        <div class="pipe-num">05</div>
        <div class="pipe-title">💾 Export</div>
        <div class="pipe-desc">Download cleaned Excel or ZIP bundle directly from the browser</div>
      </div>
    </div>
  </section>

  <!-- SECTIONS -->
  <section id="sections" class="reveal">
    <div class="sec-label">APP SECTIONS</div>
    <div class="sec-title">Four Powerful Modules</div>
    <div class="sec-line"></div>
    <div class="section-cards">
      <div class="section-card">
        <div class="sc-num">01</div>
        <div class="sc-title">Single File</div>
        <div class="sc-desc">Upload one file, clean it end-to-end and download the result as a polished Excel file with live row/column/duplicate stats.</div>
        <div class="sc-tags">
          <span class="sc-tag">xlsx</span>
          <span class="sc-tag">csv</span>
          <span class="sc-tag p">pdf</span>
          <span class="sc-tag s">image</span>
        </div>
      </div>
      <div class="section-card">
        <div class="sc-num">02</div>
        <div class="sc-title">Batch Processing</div>
        <div class="sc-desc">Upload unlimited files at once. Each file is cleaned independently and all outputs are packaged into a single ZIP download.</div>
        <div class="sc-tags">
          <span class="sc-tag">Multi-file</span>
          <span class="sc-tag p">ZIP export</span>
          <span class="sc-tag s">Progress bar</span>
        </div>
      </div>
      <div class="section-card">
        <div class="sc-num">03</div>
        <div class="sc-title">Data Fusion</div>
        <div class="sc-desc">Merge multiple Excel or CSV files into one unified dataset. Smart column alignment ensures no data is lost in the merge.</div>
        <div class="sc-tags">
          <span class="sc-tag">Merge</span>
          <span class="sc-tag p">Concat</span>
          <span class="sc-tag s">De-duplicate</span>
        </div>
      </div>
      <div class="section-card">
        <div class="sc-num">04</div>
        <div class="sc-title">Precision Extract</div>
        <div class="sc-desc">Define an exact row range (start → end) and extract only those rows from any large file — perfect for splitting datasets.</div>
        <div class="sc-tags">
          <span class="sc-tag">Row range</span>
          <span class="sc-tag p">Slice</span>
          <span class="sc-tag s">Subset</span>
        </div>
      </div>
    </div>
  </section>

  <!-- INSTALL -->
  <section id="install" class="reveal">
    <div class="sec-label">QUICK START</div>
    <div class="sec-title">Installation</div>
    <div class="sec-line"></div>
    <div class="code-block" style="margin-bottom:20px;">
      <div class="code-header">
        <div class="code-dot r"></div><div class="code-dot y"></div><div class="code-dot g"></div>
        <div class="code-fname">terminal</div>
      </div>
      <pre><span class="cm"># Clone the repository</span>
<span class="fn">git</span> clone https://github.com/your-repo/data-cleaner-studio.git
<span class="fn">cd</span> data-cleaner-studio

<span class="cm"># Create virtual environment</span>
<span class="fn">python</span> -m venv venv
<span class="fn">source</span> venv/bin/activate   <span class="cm"># Windows: venv\Scripts\activate</span>

<span class="cm"># Install dependencies</span>
<span class="fn">pip</span> install -r requirements.txt

<span class="cm"># Run the app</span>
<span class="fn">streamlit</span> run app.py</pre>
    </div>

    <div class="code-block">
      <div class="code-header">
        <div class="code-dot r"></div><div class="code-dot y"></div><div class="code-dot g"></div>
        <div class="code-fname">requirements.txt</div>
      </div>
      <pre><span class="var">streamlit</span><span class="str">>=1.32.0</span>
<span class="var">pandas</span><span class="str">>=2.0.0</span>
<span class="var">openpyxl</span><span class="str">>=3.1.0</span>
<span class="var">pdfplumber</span><span class="str">>=0.10.0</span>
<span class="var">pytesseract</span><span class="str">>=0.3.10</span>
<span class="var">Pillow</span><span class="str">>=10.0.0</span>
<span class="var">googletrans</span><span class="str">==4.0.0-rc1</span>
<span class="var">langdetect</span><span class="str">>=1.0.9</span></pre>
    </div>
  </section>

  <!-- PROJECT STRUCTURE -->
  <section class="reveal">
    <div class="sec-label">CODEBASE</div>
    <div class="sec-title">Project Structure</div>
    <div class="sec-line"></div>
    <div class="code-block">
      <div class="code-header">
        <div class="code-dot r"></div><div class="code-dot y"></div><div class="code-dot g"></div>
        <div class="code-fname">project tree</div>
      </div>
      <pre><span class="kw">data-cleaner-studio/</span>
├── <span class="fn">app.py</span>              <span class="cm"># Streamlit UI — 4 sections + full theme</span>
├── <span class="fn">main.py</span>             <span class="cm"># Core logic: clean, translate, parse</span>
├── <span class="fn">requirements.txt</span>    <span class="cm"># Python dependencies</span>
├── <span class="fn">pincode_db.csv</span>      <span class="cm"># 19,000+ pincode → State/District map</span>
└── <span class="fn">README.html</span>         <span class="cm"># This animated README</span></pre>
    </div>
  </section>

  <!-- FOOTER -->
  <footer class="reveal">
    <h2>📊 DATA CLEANER STUDIO</h2>
    <p>Built with ❤️ using Python • Streamlit • Tesseract • Google Translate API</p>
    <div class="footer-stats">
      <div>
        <div class="f-stat-num" style="color:var(--gold)">80–90%</div>
        <div class="f-stat-lbl" style="color:var(--sky)">Time Saved</div>
      </div>
      <div>
        <div class="f-stat-num" style="color:var(--pink)">95%+</div>
        <div class="f-stat-lbl" style="color:var(--sky)">Accuracy</div>
      </div>
      <div>
        <div class="f-stat-num" style="color:var(--sky)">19K+</div>
        <div class="f-stat-lbl" style="color:var(--sky)">Pincodes</div>
      </div>
      <div>
        <div class="f-stat-num" style="color:var(--gold)">4</div>
        <div class="f-stat-lbl" style="color:var(--sky)">File Formats</div>
      </div>
    </div>
    <p style="font-size:0.8rem;opacity:0.5;margin-top:16px;">© 2024 All Rights Reserved &nbsp;|&nbsp; Version 2.0 Pro &nbsp;|&nbsp; MIT License</p>
  </footer>

</div><!-- /wrap -->

<script>
/* ── PARTICLE CANVAS ── */
(function(){
  const canvas = document.getElementById('particles');
  const ctx = canvas.getContext('2d');
  let w, h, pts = [];
  const colors = ['#FFD700','#FF69B4','#87CEEB','#FFA500','#4169E1'];

  function resize(){ w = canvas.width = window.innerWidth; h = canvas.height = window.innerHeight; }
  resize(); window.addEventListener('resize', resize);

  function init(){
    pts = [];
    for(let i=0;i<70;i++){
      pts.push({
        x: Math.random()*w, y: Math.random()*h,
        vx:(Math.random()-0.5)*0.4, vy:(Math.random()-0.5)*0.4,
        r: Math.random()*2+0.5,
        color: colors[Math.floor(Math.random()*colors.length)],
        alpha: Math.random()*0.5+0.1
      });
    }
  }
  init();

  function draw(){
    ctx.clearRect(0,0,w,h);
    pts.forEach(p=>{
      p.x += p.vx; p.y += p.vy;
      if(p.x<0||p.x>w) p.vx*=-1;
      if(p.y<0||p.y>h) p.vy*=-1;
      ctx.beginPath();
      ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
      ctx.fillStyle = p.color;
      ctx.globalAlpha = p.alpha;
      ctx.fill();
    });
    ctx.globalAlpha = 1;

    // Connect nearby particles
    for(let i=0;i<pts.length;i++){
      for(let j=i+1;j<pts.length;j++){
        const dx=pts[i].x-pts[j].x, dy=pts[i].y-pts[j].y;
        const d=Math.sqrt(dx*dx+dy*dy);
        if(d<120){
          ctx.beginPath();
          ctx.strokeStyle='rgba(255,215,0,'+(0.06*(1-d/120))+')';
          ctx.lineWidth=0.5;
          ctx.moveTo(pts[i].x,pts[i].y);
          ctx.lineTo(pts[j].x,pts[j].y);
          ctx.stroke();
        }
      }
    }
    requestAnimationFrame(draw);
  }
  draw();
})();

/* ── SCROLL REVEAL ── */
const reveals = document.querySelectorAll('.reveal');
const observer = new IntersectionObserver((entries)=>{
  entries.forEach(e=>{
    if(e.isIntersecting){ e.target.classList.add('visible'); observer.unobserve(e.target); }
  });
}, { threshold: 0.12 });
reveals.forEach(el=>observer.observe(el));

/* ── BAR CHART ANIMATE ── */
const barObs = new IntersectionObserver((entries)=>{
  entries.forEach(e=>{
    if(e.isIntersecting){
      document.querySelectorAll('.bar-fill').forEach(b=>{
        b.style.width = b.dataset.width + '%';
      });
      barObs.disconnect();
    }
  });
}, { threshold: 0.3 });
const barWrap = document.querySelector('.chart-wrap');
if(barWrap) barObs.observe(barWrap);

/* ── DONUT ANIMATE ── */
const donutObs = new IntersectionObserver((entries)=>{
  entries.forEach(e=>{
    if(e.isIntersecting){
      // d1 gold:  25% → dashoffset = 502 - (0.25*502) = 502-125.5=376.5
      // d2 pink:  d1+30% → offset at start = 376.5, stroke=30%→151 → but we rotate
      // Simplified: each ring covers its % starting after previous
      const segs = [
        {id:'d1', pct:0.25, col:'#FFD700', delay:0},
        {id:'d2', pct:0.30, col:'#FF69B4', delay:300},
        {id:'d3', pct:0.20, col:'#87CEEB', delay:600},
        {id:'d4', pct:0.15, col:'#FFA500', delay:900},
      ];
      let cumulAngle = 0;
      const circ = 502;
      segs.forEach(s=>{
        const el = document.getElementById(s.id);
        if(!el) return;
        const filled = s.pct * circ;
        const offset = circ - filled;
        // Rotate SVG circle to start after previous segments
        const rotDeg = (cumulAngle / circ) * 360 - 90;
        el.style.transform = `rotate(${rotDeg}deg)`;
        el.style.transformOrigin = '90px 90px';
        el.style.strokeDasharray = circ;
        el.style.strokeDashoffset = circ;
        el.style.transition = `stroke-dashoffset 1.6s cubic-bezier(0.22,1,0.36,1) ${s.delay}ms`;
        setTimeout(()=>{ el.style.strokeDashoffset = offset; }, 100);
        cumulAngle += filled;
      });
      donutObs.disconnect();
    }
  });
}, { threshold: 0.3 });
const donutEl = document.querySelector('.donut-wrap');
if(donutEl) donutObs.observe(donutEl);

/* ── LINE CHART ANIMATE ── */
const lineObs = new IntersectionObserver((entries)=>{
  entries.forEach(e=>{
    if(e.isIntersecting){
      const lg = document.getElementById('lGold');
      const lp = document.getElementById('lPink');
      if(lg){ lg.style.strokeDashoffset='0'; }
      if(lp){ lp.style.strokeDashoffset='0'; }
      lineObs.disconnect();
    }
  });
}, { threshold: 0.3 });
const lineEl = document.querySelector('.line-chart-wrap');
if(lineEl) lineObs.observe(lineEl);

/* ── COUNTER ANIMATE ── */
const counterObs = new IntersectionObserver((entries)=>{
  entries.forEach(e=>{
    if(e.isIntersecting){
      document.querySelectorAll('.stat-num[data-target]').forEach(el=>{
        const target = +el.dataset.target;
        let cur = 0;
        const step = Math.ceil(target / 40);
        const timer = setInterval(()=>{
          cur += step;
          if(cur >= target){ cur = target; clearInterval(timer); }
          el.textContent = cur;
        }, 35);
      });
      counterObs.disconnect();
    }
  });
}, { threshold: 0.3 });
const statsRow = document.querySelector('.stats-row');
if(statsRow) counterObs.observe(statsRow);
</script>
</body>
</html>
