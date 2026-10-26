import os
import sys
import json
import base64
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

from game_engine import GameEngine

PORT = 8080
engine = GameEngine()

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>IndicVani — Sarvam AI Language & Listening Game</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-dark: #060818;
      --bg-card: rgba(15, 19, 44, 0.78);
      --bg-card-border: rgba(147, 51, 234, 0.28);
      --neon-violet: #a855f7;
      --neon-indigo: #6366f1;
      --neon-cyan: #38bdf8;
      --accent-gradient: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
      --text-main: #f1f5f9;
      --text-muted: #94a3b8;
      --success: #10b981;
      --fail: #ef4444;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      background-color: var(--bg-dark);
      background-image: 
        radial-gradient(ellipse at 80% 0%, rgba(168, 85, 247, 0.16) 0%, transparent 55%),
        radial-gradient(ellipse at 15% 90%, rgba(56, 189, 248, 0.14) 0%, transparent 55%),
        radial-gradient(circle at 50% 45%, rgba(99, 102, 241, 0.09) 0%, transparent 65%);
      color: var(--text-main);
      font-family: 'Plus Jakarta Sans', sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 24px 16px;
      overflow-x: hidden;
      position: relative;
    }

    /* Ambient Celestial Side Elements (Slowly Moving) */
    .cosmic-side {
      position: fixed;
      top: 0;
      bottom: 0;
      width: 280px;
      pointer-events: none;
      z-index: 1;
      overflow: hidden;
    }

    .cosmic-side.left {
      left: 0;
    }

    .cosmic-side.right {
      right: 0;
    }

    /* Floating Orbs */
    .celestial-orb {
      position: absolute;
      border-radius: 50%;
      filter: blur(1px);
    }

    .orb-planet {
      width: 140px;
      height: 140px;
      top: 15%;
      left: 25px;
      background: radial-gradient(circle at 35% 35%, #8b5cf6, #3b0764 70%, #090218);
      box-shadow: 0 0 45px rgba(139, 92, 246, 0.4), inset -8px -8px 20px rgba(0, 0, 0, 0.8);
      animation: floatSlow1 24s infinite ease-in-out alternate;
    }

    .orb-ring {
      position: absolute;
      width: 210px;
      height: 55px;
      top: 42px;
      left: -35px;
      border: 3px solid rgba(192, 132, 252, 0.45);
      border-radius: 50%;
      transform: rotate(-24deg);
      box-shadow: 0 0 25px rgba(168, 85, 247, 0.35);
      animation: ringGlow 12s infinite ease-in-out alternate;
    }

    .orb-moon {
      width: 110px;
      height: 110px;
      bottom: 20%;
      right: 35px;
      background: radial-gradient(circle at 40% 40%, #38bdf8, #1e1b4b 75%, #050414);
      box-shadow: 0 0 40px rgba(56, 189, 248, 0.35), inset -6px -6px 18px rgba(0, 0, 0, 0.75);
      animation: floatSlow2 28s infinite ease-in-out alternate;
    }

    .orb-mini {
      width: 55px;
      height: 55px;
      top: 65%;
      left: 60px;
      background: radial-gradient(circle at 30% 30%, #ec4899, #4c0519 80%);
      box-shadow: 0 0 25px rgba(236, 72, 153, 0.4);
      animation: floatSlow3 20s infinite ease-in-out alternate;
    }

    /* Floating Indic Celestial Glyphs */
    .celestial-glyph {
      position: absolute;
      font-weight: 800;
      user-select: none;
      opacity: 0.22;
      transition: opacity 0.5s ease;
    }

    .glyph-1 {
      top: 8%;
      left: 60px;
      font-size: 3.2rem;
      color: #c084fc;
      text-shadow: 0 0 20px rgba(168, 85, 247, 0.6);
      animation: floatSlow1 22s infinite ease-in-out alternate;
    }

    .glyph-2 {
      top: 42%;
      left: 140px;
      font-size: 3.6rem;
      color: #38bdf8;
      text-shadow: 0 0 22px rgba(56, 189, 248, 0.5);
      animation: floatSlow2 26s infinite ease-in-out alternate;
    }

    .glyph-3 {
      top: 75%;
      left: 40px;
      font-size: 3rem;
      color: #a855f7;
      text-shadow: 0 0 20px rgba(168, 85, 247, 0.5);
      animation: floatSlow3 19s infinite ease-in-out alternate;
    }

    .glyph-4 {
      top: 12%;
      right: 70px;
      font-size: 3.4rem;
      color: #38bdf8;
      text-shadow: 0 0 20px rgba(56, 189, 248, 0.6);
      animation: floatSlow2 24s infinite ease-in-out alternate;
    }

    .glyph-5 {
      top: 48%;
      right: 130px;
      font-size: 3.2rem;
      color: #c084fc;
      text-shadow: 0 0 22px rgba(192, 132, 252, 0.5);
      animation: floatSlow1 27s infinite ease-in-out alternate;
    }

    .glyph-6 {
      bottom: 10%;
      right: 50px;
      font-size: 3.5rem;
      color: #ec4899;
      text-shadow: 0 0 20px rgba(236, 72, 153, 0.5);
      animation: floatSlow3 23s infinite ease-in-out alternate;
    }

    /* Constellation SVG Lines */
    .constellation-svg {
      position: absolute;
      width: 100%;
      height: 100%;
      opacity: 0.35;
      animation: constellationPulse 10s infinite ease-in-out alternate;
    }

    .star-dot {
      fill: #38bdf8;
      filter: drop-shadow(0 0 4px #38bdf8);
      animation: starBlink 4s infinite ease-in-out alternate;
    }

    @keyframes floatSlow1 {
      0% { transform: translateY(0px) rotate(0deg); }
      50% { transform: translateY(-38px) rotate(5deg); }
      100% { transform: translateY(22px) rotate(-4deg); }
    }

    @keyframes floatSlow2 {
      0% { transform: translateY(0px) rotate(0deg); }
      50% { transform: translateY(42px) rotate(-6deg); }
      100% { transform: translateY(-28px) rotate(4deg); }
    }

    @keyframes floatSlow3 {
      0% { transform: translateY(0px) rotate(0deg) scale(1); }
      50% { transform: translateY(-32px) rotate(8deg) scale(1.08); }
      100% { transform: translateY(18px) rotate(-5deg) scale(0.96); }
    }

    @keyframes ringGlow {
      0% { opacity: 0.4; transform: rotate(-24deg) scale(0.98); }
      100% { opacity: 0.75; transform: rotate(-20deg) scale(1.04); }
    }

    @keyframes constellationPulse {
      0% { opacity: 0.2; }
      100% { opacity: 0.45; }
    }

    @keyframes starBlink {
      0%, 100% { opacity: 0.3; r: 2; }
      50% { opacity: 1; r: 3.5; }
    }

    /* Main Container */
    .container {
      width: 100%;
      max-width: 780px;
      margin: 0 auto;
      position: relative;
      z-index: 10;
    }

    /* Header */
    header {
      text-align: center;
      margin-bottom: 24px;
    }

    .badge-tag {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 16px;
      background: rgba(147, 51, 234, 0.16);
      border: 1px solid rgba(168, 85, 247, 0.35);
      border-radius: 999px;
      font-size: 0.8rem;
      font-weight: 600;
      color: #c084fc;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 12px;
      box-shadow: 0 0 15px rgba(168, 85, 247, 0.2);
    }

    h1 {
      font-family: 'Space Grotesk', sans-serif;
      font-size: 2.6rem;
      font-weight: 700;
      background: var(--accent-gradient);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 8px;
      letter-spacing: -0.02em;
    }

    p.subtitle {
      color: var(--text-muted);
      font-size: 1rem;
      max-width: 600px;
      margin: 0 auto;
      line-height: 1.5;
    }

    /* Score Bar */
    .top-stats {
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: rgba(15, 19, 44, 0.65);
      border: 1px solid rgba(147, 51, 234, 0.22);
      border-radius: 16px;
      padding: 12px 24px;
      margin-bottom: 22px;
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4);
    }

    .stat-pill {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 0.92rem;
      font-weight: 600;
    }

    .stat-val {
      color: var(--neon-cyan);
      font-family: 'Space Grotesk', sans-serif;
      font-size: 1.25rem;
    }

    /* Main Card */
    .game-card {
      background: var(--bg-card);
      backdrop-filter: blur(24px);
      -webkit-backdrop-filter: blur(24px);
      border: 1px solid var(--bg-card-border);
      border-radius: 26px;
      padding: 32px;
      box-shadow: 0 30px 60px -15px rgba(5, 7, 24, 0.85), 0 0 35px rgba(147, 51, 234, 0.16);
      position: relative;
    }

    /* Section Step */
    .step-header {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 14px;
      margin-top: 10px;
    }

    .step-number {
      width: 30px;
      height: 30px;
      border-radius: 50%;
      background: linear-gradient(135deg, var(--neon-indigo), var(--neon-violet));
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 0.88rem;
      box-shadow: 0 0 12px rgba(168, 85, 247, 0.4);
    }

    .step-title {
      font-size: 1.12rem;
      font-weight: 700;
      color: #f1f5f9;
    }

    /* Audio Player Section */
    .audio-box {
      background: rgba(9, 12, 34, 0.65);
      border: 1px solid rgba(99, 102, 241, 0.28);
      border-radius: 18px;
      padding: 24px;
      text-align: center;
      margin-bottom: 26px;
    }

    .play-btn {
      background: var(--accent-gradient);
      color: white;
      border: none;
      border-radius: 50px;
      padding: 14px 34px;
      font-size: 1.05rem;
      font-weight: 700;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 10px;
      box-shadow: 0 10px 25px rgba(168, 85, 247, 0.38);
      transition: all 0.2s ease;
    }

    .play-btn:hover {
      transform: translateY(-2px);
      box-shadow: 0 14px 32px rgba(168, 85, 247, 0.55);
    }

    .play-btn:active {
      transform: translateY(0);
    }

    .wave-bars {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 5px;
      height: 26px;
      margin-top: 16px;
    }

    .bar {
      width: 4px;
      height: 6px;
      background: var(--neon-violet);
      border-radius: 3px;
      transition: height 0.15s ease;
    }

    .playing .bar {
      animation: pulseWave 0.8s infinite ease-in-out alternate;
    }

    .playing .bar:nth-child(2) { animation-delay: 0.1s; }
    .playing .bar:nth-child(3) { animation-delay: 0.2s; }
    .playing .bar:nth-child(4) { animation-delay: 0.3s; }
    .playing .bar:nth-child(5) { animation-delay: 0.4s; }

    @keyframes pulseWave {
      from { height: 6px; }
      to { height: 26px; background: var(--neon-cyan); }
    }

    /* Language Selection Grid */
    .languages-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
      gap: 10px;
      margin-bottom: 24px;
    }

    .lang-chip {
      background: rgba(13, 17, 44, 0.65);
      border: 1px solid rgba(147, 51, 234, 0.22);
      border-radius: 12px;
      padding: 10px;
      text-align: center;
      cursor: pointer;
      transition: all 0.2s ease;
      user-select: none;
    }

    .lang-chip:hover {
      border-color: var(--neon-violet);
      background: rgba(147, 51, 234, 0.18);
    }

    .lang-chip.selected {
      border-color: var(--neon-cyan);
      background: linear-gradient(135deg, rgba(99, 102, 241, 0.32), rgba(56, 189, 248, 0.22));
      box-shadow: 0 0 16px rgba(56, 189, 248, 0.35);
    }

    .lang-chip-name {
      font-weight: 700;
      font-size: 0.95rem;
      color: #f8fafc;
    }

    .lang-chip-native {
      font-size: 0.78rem;
      color: var(--text-muted);
      margin-top: 2px;
    }

    /* Response Language Grid Variant */
    .response-grid .lang-chip.selected {
      border-color: #ec4899;
      background: linear-gradient(135deg, rgba(168, 85, 247, 0.32), rgba(236, 72, 153, 0.25));
      box-shadow: 0 0 16px rgba(236, 72, 153, 0.35);
    }

    /* Dictation Section */
    .dictate-box {
      background: rgba(9, 12, 34, 0.65);
      border: 1px solid rgba(99, 102, 241, 0.28);
      border-radius: 18px;
      padding: 20px;
      margin-bottom: 26px;
    }

    .dictate-controls {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 14px;
      flex-wrap: wrap;
    }

    .record-btn {
      background: rgba(239, 68, 68, 0.18);
      border: 1px solid rgba(239, 68, 68, 0.45);
      color: #fca5a5;
      border-radius: 50px;
      padding: 10px 24px;
      font-weight: 700;
      font-size: 0.94rem;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      transition: all 0.2s ease;
    }

    .record-btn.recording {
      background: #ef4444;
      color: white;
      animation: pulseRed 1s infinite alternate;
    }

    @keyframes pulseRed {
      from { box-shadow: 0 0 10px rgba(239, 68, 68, 0.5); }
      to { box-shadow: 0 0 25px rgba(239, 68, 68, 0.95); }
    }

    .rec-status {
      font-size: 0.9rem;
      color: var(--text-muted);
    }

    textarea.meaning-input {
      width: 100%;
      height: 95px;
      background: rgba(6, 8, 22, 0.75);
      border: 1px solid rgba(147, 51, 234, 0.28);
      border-radius: 12px;
      padding: 12px;
      color: #f1f5f9;
      font-family: inherit;
      font-size: 0.95rem;
      resize: vertical;
      outline: none;
      transition: border-color 0.2s ease;
    }

    textarea.meaning-input:focus {
      border-color: var(--neon-cyan);
    }

    /* Submit Button */
    .submit-btn {
      width: 100%;
      background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
      color: white;
      border: none;
      border-radius: 16px;
      padding: 16px;
      font-size: 1.1rem;
      font-weight: 700;
      cursor: pointer;
      box-shadow: 0 10px 25px rgba(124, 58, 237, 0.35);
      transition: all 0.2s ease;
    }

    .submit-btn:hover {
      background: linear-gradient(135deg, #4338ca 0%, #6d28d9 100%);
      transform: translateY(-2px);
      box-shadow: 0 14px 30px rgba(124, 58, 237, 0.5);
    }

    .submit-btn:disabled {
      opacity: 0.5;
      cursor: not-allowed;
      transform: none;
    }

    /* Result Overlay Modal / Card */
    .result-card {
      display: none;
      margin-top: 28px;
      background: rgba(12, 16, 42, 0.92);
      border: 1px solid var(--neon-violet);
      border-radius: 22px;
      padding: 28px;
      animation: fadeIn 0.3s ease;
      box-shadow: 0 20px 45px rgba(0, 0, 0, 0.6);
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(12px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .score-banner {
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: rgba(147, 51, 234, 0.16);
      border-radius: 16px;
      padding: 18px 24px;
      margin-bottom: 20px;
    }

    .score-total-text {
      font-size: 0.9rem;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .score-total-val {
      font-family: 'Space Grotesk', sans-serif;
      font-size: 2.8rem;
      font-weight: 700;
      background: var(--accent-gradient);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .breakdown-row {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
      margin-bottom: 20px;
    }

    .score-chip {
      background: rgba(9, 12, 34, 0.65);
      border-radius: 12px;
      padding: 14px;
      border: 1px solid rgba(255, 255, 255, 0.08);
    }

    .score-chip-title {
      font-size: 0.82rem;
      color: var(--text-muted);
    }

    .score-chip-pts {
      font-size: 1.3rem;
      font-weight: 700;
      margin-top: 4px;
    }

    .pts-correct { color: var(--success); }
    .pts-wrong { color: var(--fail); }

    .reveal-box {
      background: rgba(6, 8, 22, 0.55);
      border-radius: 14px;
      padding: 18px;
      margin-bottom: 20px;
      border-left: 3px solid var(--neon-cyan);
    }

    .reveal-label {
      font-size: 0.78rem;
      color: var(--text-muted);
      text-transform: uppercase;
      margin-bottom: 4px;
      letter-spacing: 0.04em;
    }

    .reveal-text {
      font-size: 1.05rem;
      font-weight: 600;
      color: #f8fafc;
      margin-bottom: 8px;
    }

    .reveal-sub {
      font-size: 0.88rem;
      color: #cbd5e1;
      font-style: italic;
    }

    .feedback-box {
      font-size: 0.94rem;
      color: #cbd5e1;
      padding: 14px;
      background: rgba(147, 51, 234, 0.12);
      border-radius: 12px;
      margin-bottom: 22px;
      line-height: 1.5;
    }

    .next-btn {
      width: 100%;
      background: var(--accent-gradient);
      color: white;
      border: none;
      border-radius: 16px;
      padding: 15px;
      font-size: 1.05rem;
      font-weight: 700;
      cursor: pointer;
      box-shadow: 0 10px 22px rgba(168, 85, 247, 0.35);
    }

    .api-note {
      font-size: 0.76rem;
      color: #64748b;
      text-align: center;
      margin-top: 26px;
    }
  </style>
</head>
<body>

  <!-- Ambient Slowly Moving Cosmic Side Designs -->
  <aside class="cosmic-side left" aria-hidden="true">
    <div class="celestial-orb orb-planet">
      <div class="orb-ring"></div>
    </div>
    <div class="celestial-orb orb-mini"></div>
    <div class="celestial-glyph glyph-1">अ</div>
    <div class="celestial-glyph glyph-2">த</div>
    <div class="celestial-glyph glyph-3">తె</div>

    <!-- Constellation SVG Left -->
    <svg class="constellation-svg" viewBox="0 0 280 800" fill="none">
      <path d="M 50 120 L 140 210 L 80 340 L 160 480 L 70 650" stroke="rgba(168, 85, 247, 0.3)" stroke-width="1.5" stroke-dasharray="4 6"/>
      <circle cx="50" cy="120" r="3" class="star-dot"/>
      <circle cx="140" cy="210" r="2.5" class="star-dot"/>
      <circle cx="80" cy="340" r="3.5" class="star-dot"/>
      <circle cx="160" cy="480" r="2.5" class="star-dot"/>
      <circle cx="70" cy="650" r="3" class="star-dot"/>
    </svg>
  </aside>

  <aside class="cosmic-side right" aria-hidden="true">
    <div class="celestial-orb orb-moon"></div>
    <div class="celestial-glyph glyph-4">ক</div>
    <div class="celestial-glyph glyph-5">म</div>
    <div class="celestial-glyph glyph-6">ਪ</div>

    <!-- Constellation SVG Right -->
    <svg class="constellation-svg" viewBox="0 0 280 800" fill="none">
      <path d="M 220 150 L 130 270 L 210 410 L 110 560 L 200 700" stroke="rgba(56, 189, 248, 0.3)" stroke-width="1.5" stroke-dasharray="4 6"/>
      <circle cx="220" cy="150" r="3" class="star-dot"/>
      <circle cx="130" cy="270" r="3.5" class="star-dot"/>
      <circle cx="210" cy="410" r="2.5" class="star-dot"/>
      <circle cx="110" cy="560" r="3" class="star-dot"/>
      <circle cx="200" cy="700" r="2.5" class="star-dot"/>
    </svg>
  </aside>

  <!-- Main Container -->
  <div class="container">
    <header>
      <div class="badge-tag">⚡ Powered by Sarvam AI</div>
      <h1>IndicVani</h1>
      <p class="subtitle">Listen to an authentic sentence dictated in an Indian language. Guess the language and dictate your translation in your chosen response language!</p>
    </header>

    <div class="top-stats">
      <div class="stat-pill">
        <span>🏆 Total Score:</span>
        <span class="stat-val" id="cumulativeScore">0</span>
      </div>
      <div class="stat-pill">
        <span>🎯 Round:</span>
        <span class="stat-val" id="roundNum">1</span>
      </div>
    </div>

    <div class="game-card">
      <!-- Step 1: Listen to Dictation -->
      <div class="step-header">
        <div class="step-number">1</div>
        <div class="step-title">Listen to the Sentence (Sarvam Bulbul TTS)</div>
      </div>
      <div class="audio-box">
        <button class="play-btn" id="playBtn" onclick="playAudio()">
          <span id="playIcon">🔊</span>
          <span id="playText">Play Dictation</span>
        </button>
        <div class="wave-bars" id="waveBars">
          <div class="bar"></div>
          <div class="bar"></div>
          <div class="bar"></div>
          <div class="bar"></div>
          <div class="bar"></div>
        </div>
        <div id="audioStatus" style="margin-top: 10px; font-size: 0.85rem; color: #94a3b8;">
          Loading audio...
        </div>
      </div>

      <!-- Step 2: Guess the Spoken Language (20 pts) -->
      <div class="step-header">
        <div class="step-number">2</div>
        <div class="step-title">Guess Which Language Was Spoken <span style="font-weight: 500; font-size: 0.85rem; color: #a855f7;">(20 Points)</span></div>
      </div>
      <div class="languages-grid" id="languagesGrid">
        <!-- Rendered by JS -->
      </div>

      <!-- Step 3: Choose Response Language -->
      <div class="step-header">
        <div class="step-number">3</div>
        <div class="step-title">Choose Your Response Language</div>
      </div>
      <div style="margin-bottom: 12px; font-size: 0.88rem; color: #94a3b8;">
        Select the language you will dictate or write your guessed translation in:
      </div>
      <div class="languages-grid response-grid" id="responseLanguagesGrid">
        <!-- Rendered by JS -->
      </div>

      <!-- Step 4: Dictate Translation (80 pts) -->
      <div class="step-header">
        <div class="step-number">4</div>
        <div class="step-title">Dictate What Was Said <span style="font-weight: 500; font-size: 0.85rem; color: #a855f7;">(80 Points)</span></div>
      </div>
      <div class="dictate-box">
        <div class="dictate-controls">
          <button class="record-btn" id="recordBtn" onclick="toggleRecording()">
            <span id="recordIcon">🎙️</span>
            <span id="recordText">Dictate with Voice</span>
          </button>
          <span class="rec-status" id="recStatus">Speak in your chosen response language (<strong id="activeRespName" style="color: #38bdf8;">English</strong>)</span>
        </div>
        <textarea class="meaning-input" id="meaningInput" placeholder="Dictate with voice or type what you understood the sentence to mean..."></textarea>
      </div>

      <button class="submit-btn" id="submitBtn" onclick="submitGuess()">
        Submit Guess & Get Score ✨
      </button>

      <!-- Step 5: Results Card -->
      <div class="result-card" id="resultCard">
        <div class="score-banner">
          <div>
            <div class="score-total-text">Round Score</div>
            <div style="font-size: 0.85rem; color: #cbd5e1;" id="scoreTier">Great job!</div>
          </div>
          <div class="score-total-val" id="resultScore">0<span style="font-size: 1.4rem; color: #94a3b8;">/100</span></div>
        </div>

        <div class="breakdown-row">
          <div class="score-chip">
            <div class="score-chip-title">Language Guess (Max 20)</div>
            <div class="score-chip-pts" id="langScoreChip">+0 pts</div>
          </div>
          <div class="score-chip">
            <div class="score-chip-title">Translation Closeness (Max 80)</div>
            <div class="score-chip-pts" id="meaningScoreChip">+0 pts</div>
          </div>
        </div>

        <div class="reveal-box">
          <div class="reveal-label">Target Spoken Language</div>
          <div class="reveal-text" id="revealLang">Hindi (हिन्दी)</div>
          
          <div class="reveal-label">Iconic Movie & Character</div>
          <div class="reveal-text" style="color: #ec4899;" id="revealMovie">🎬 ...</div>

          <div class="reveal-label">Original Dialogue Spoken</div>
          <div class="reveal-text" id="revealOriginal">...</div>
          <div class="reveal-sub" id="revealRoman">...</div>
          
          <div class="reveal-label" style="margin-top: 10px;">Actual Meaning</div>
          <div class="reveal-text" style="color: #38bdf8;" id="revealMeaning">...</div>
        </div>

        <div class="feedback-box" id="resultFeedback">
          ...
        </div>

        <button class="next-btn" onclick="startNewRound()">
          Next Sentence 🚀
        </button>
      </div>
    </div>

    <div class="api-note">
      Powered by Sarvam AI (Text-to-Speech Bulbul, Speech-to-Text Saaras, and Indic Reasoning LLM)
    </div>
  </div>

  <script>
    let currentRound = null;
    let selectedLang = null;
    let selectedRespLang = 'en-IN';
    let audioObj = null;
    let mediaRecorder = null;
    let audioChunks = [];
    let isRecording = false;
    let cumulativePoints = 0;
    let currentRoundNum = 1;

    // SpeechRecognition fallback for instant live dictation
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    let browserSpeechRec = null;

    async function startNewRound() {
      document.getElementById('resultCard').style.display = 'none';
      document.getElementById('submitBtn').disabled = false;
      document.getElementById('meaningInput').value = '';
      selectedLang = null;
      document.querySelectorAll('#languagesGrid .lang-chip').forEach(el => el.classList.remove('selected'));
      document.getElementById('audioStatus').innerText = 'Loading Indic voice dictation...';

      try {
        const res = await fetch('/api/new-round');
        const data = await res.json();
        currentRound = data;

        // 1. Render Language Guess Chips (Step 2)
        const grid = document.getElementById('languagesGrid');
        grid.innerHTML = '';
        data.languages.forEach(lang => {
          const chip = document.createElement('div');
          chip.className = 'lang-chip';
          chip.onclick = () => selectLanguage(lang.code, chip);
          chip.innerHTML = `
            <div class="lang-chip-name">${lang.name}</div>
            <div class="lang-chip-native">${lang.native}</div>
          `;
          grid.appendChild(chip);
        });

        // 2. Render Response Language Chips (Step 3)
        const respGrid = document.getElementById('responseLanguagesGrid');
        respGrid.innerHTML = '';
        data.response_languages.forEach(lang => {
          const chip = document.createElement('div');
          chip.className = 'lang-chip' + (lang.code === selectedRespLang ? ' selected' : '');
          chip.onclick = () => selectResponseLanguage(lang.code, lang.name, chip);
          chip.innerHTML = `
            <div class="lang-chip-name">${lang.name}</div>
            <div class="lang-chip-native">${lang.native}</div>
          `;
          respGrid.appendChild(chip);
        });

        updateResponseLangUI();

        // 3. Setup audio
        if (data.has_audio && data.audio_base64) {
          audioObj = new Audio('data:audio/wav;base64,' + data.audio_base64);
          audioObj.onended = () => stopWave();
          audioObj.onerror = (e) => {
            console.error('Audio playback error', e);
            stopWave();
            document.getElementById('audioStatus').innerText = 'Audio error: ' + (e.message || 'Browser permission issue');
          };
          document.getElementById('audioStatus').innerHTML = '<span style="color: #10b981; font-weight: 600;">✓ Authentic Indic Speech Ready (Sarvam Bulbul:v3)</span>';
        } else {
          // Fallback if 0 quota
          audioObj = null;
          document.getElementById('audioStatus').innerHTML = 
            `<span style="color: #f59e0b;">${data.error_msg || 'Audio preview'}</span> ` +
            `<button onclick="playFallbackSpeech()" style="background:#4f46e5;color:white;border:none;padding:4px 8px;border-radius:6px;cursor:pointer;margin-left:6px;">Play Local Audio</button>`;
        }
      } catch (err) {
        document.getElementById('audioStatus').innerText = 'Failed to load round: ' + err.message;
      }
    }

    function selectLanguage(code, element) {
      selectedLang = code;
      document.querySelectorAll('#languagesGrid .lang-chip').forEach(el => el.classList.remove('selected'));
      element.classList.add('selected');
    }

    function selectResponseLanguage(code, name, element) {
      selectedRespLang = code;
      document.querySelectorAll('#responseLanguagesGrid .lang-chip').forEach(el => el.classList.remove('selected'));
      element.classList.add('selected');
      updateResponseLangUI(name);
    }

    function updateResponseLangUI(name) {
      const activeName = name || (selectedRespLang === 'en-IN' ? 'English' : selectedRespLang);
      document.getElementById('activeRespName').innerText = activeName;
      document.getElementById('recordText').innerText = `Dictate in ${activeName}`;
      document.getElementById('meaningInput').placeholder = `Dictate with voice or type your translation in ${activeName}...`;
    }

    function playAudio() {
      if (audioObj) {
        audioObj.pause();
        audioObj.currentTime = 0;
        const p = audioObj.play();
        if (p !== undefined) {
          p.then(() => startWave()).catch(err => {
            console.warn('Playback error:', err);
            stopWave();
          });
        } else {
          startWave();
        }
      } else if (currentRound && currentRound.fallback_text) {
        playFallbackSpeech();
      }
    }

    function playFallbackSpeech() {
      if ('speechSynthesis' in window && currentRound && currentRound.fallback_text) {
        window.speechSynthesis.cancel();
        const u = new SpeechSynthesisUtterance(currentRound.fallback_text);
        u.lang = currentRound.fallback_lang || 'hi-IN';
        u.onstart = () => startWave();
        u.onend = () => stopWave();
        window.speechSynthesis.speak(u);
      }
    }

    function startWave() {
      document.getElementById('waveBars').classList.add('playing');
      document.getElementById('playText').innerText = 'Playing...';
    }

    function stopWave() {
      document.getElementById('waveBars').classList.remove('playing');
      document.getElementById('playText').innerText = 'Play Again';
    }

    // Voice Dictation in chosen response language
    async function toggleRecording() {
      const recBtn = document.getElementById('recordBtn');
      const recText = document.getElementById('recordText');
      const status = document.getElementById('recStatus');

      if (!isRecording) {
        // Start Recording
        try {
          const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
          audioChunks = [];
          mediaRecorder = new MediaRecorder(stream);
          mediaRecorder.ondataavailable = e => { if (e.data.size > 0) audioChunks.push(e.data); };
          mediaRecorder.onstop = async () => {
            const blob = new Blob(audioChunks, { type: 'audio/webm' });
            stream.getTracks().forEach(t => t.stop());
            await sendAudioToSarvamSTT(blob);
          };
          mediaRecorder.start();

          // Web Speech Recognition configured to the user's response language!
          if (SpeechRecognition) {
            browserSpeechRec = new SpeechRecognition();
            browserSpeechRec.lang = selectedRespLang || 'en-IN';
            browserSpeechRec.continuous = true;
            browserSpeechRec.interimResults = true;
            browserSpeechRec.onresult = (e) => {
              let text = '';
              for (let i = 0; i < e.results.length; i++) {
                text += e.results[i][0].transcript + ' ';
              }
              if (text.trim()) {
                document.getElementById('meaningInput').value = text.trim();
              }
            };
            browserSpeechRec.start();
          }

          isRecording = true;
          recBtn.classList.add('recording');
          recText.innerText = 'Stop Recording';
          status.innerHTML = `Listening in <strong style="color:#38bdf8;">${document.getElementById('activeRespName').innerText}</strong>... Speak your translation now!`;
        } catch (err) {
          status.innerText = 'Mic access blocked: Please type your interpretation below.';
        }
      } else {
        // Stop Recording
        isRecording = false;
        recBtn.classList.remove('recording');
        recText.innerText = `Dictate in ${document.getElementById('activeRespName').innerText}`;
        status.innerText = 'Transcribing with Sarvam Saaras STT...';
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
          mediaRecorder.stop();
        }
        if (browserSpeechRec) {
          try { browserSpeechRec.stop(); } catch(e){}
        }
      }
    }

    async function sendAudioToSarvamSTT(blob) {
      const status = document.getElementById('recStatus');
      const formData = new FormData();
      formData.append('audio', blob, 'dictation.webm');

      try {
        const res = await fetch('/api/transcribe?lang=' + encodeURIComponent(selectedRespLang), {
          method: 'POST',
          body: formData,
        });
        const data = await res.json();
        if (data.transcript) {
          document.getElementById('meaningInput').value = data.transcript;
          status.innerText = `Transcribed via Sarvam Saaras STT (${document.getElementById('activeRespName').innerText})! Edit if needed.`;
        } else if (data.error) {
          status.innerText = data.error;
        }
      } catch (err) {
        status.innerText = 'Transcription completed.';
      }
    }

    async function submitGuess() {
      if (!selectedLang) {
        alert('Please select which Indian language you think was spoken in Step 2!');
        return;
      }

      const meaning = document.getElementById('meaningInput').value.trim();
      if (!meaning) {
        alert('Please dictate or type your translation in your chosen response language in Step 4!');
        return;
      }

      document.getElementById('submitBtn').disabled = true;
      document.getElementById('submitBtn').innerText = 'Evaluating with Sarvam AI...';

      try {
        const res = await fetch('/api/submit-guess', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            round_id: currentRound.round_id,
            guessed_lang: selectedLang,
            guessed_meaning: meaning,
            response_lang: selectedRespLang,
          })
        });
        const data = await res.json();
        renderResult(data);
      } catch (err) {
        alert('Error scoring round: ' + err.message);
      } finally {
        document.getElementById('submitBtn').innerText = 'Submit Guess & Get Score ✨';
      }
    }

    function renderResult(data) {
      const card = document.getElementById('resultCard');
      card.style.display = 'block';

      // Scores
      document.getElementById('resultScore').innerHTML = `${data.total_score}<span style="font-size: 1.4rem; color: #94a3b8;">/100</span>`;
      
      const langChip = document.getElementById('langScoreChip');
      langChip.innerText = `+${data.breakdown.language_score} pts`;
      langChip.className = 'score-chip-pts ' + (data.breakdown.language_correct ? 'pts-correct' : 'pts-wrong');

      const meaningChip = document.getElementById('meaningScoreChip');
      meaningChip.innerText = `+${data.breakdown.meaning_score} pts`;
      meaningChip.className = 'score-chip-pts ' + (data.breakdown.meaning_score >= 40 ? 'pts-correct' : 'pts-wrong');

      // Tiers
      const tier = document.getElementById('scoreTier');
      if (data.total_score >= 80) tier.innerText = '🌟 Master Linguist! Outstanding!';
      else if (data.total_score >= 50) tier.innerText = '🎉 Good intuition! You caught the essence.';
      else tier.innerText = '💪 Nice attempt! Indic languages are rich and subtle.';

      // Reveal
      document.getElementById('revealLang').innerText = `${data.ground_truth.language_name} (${data.ground_truth.language_native})`;
      const charStr = data.ground_truth.character ? ` (${data.ground_truth.character})` : '';
      document.getElementById('revealMovie').innerText = `🎬 ${data.ground_truth.movie}${charStr}`;
      document.getElementById('revealOriginal').innerText = data.ground_truth.original_text;
      document.getElementById('revealRoman').innerText = data.ground_truth.roman;
      document.getElementById('revealMeaning').innerText = data.ground_truth.true_meaning;
      document.getElementById('resultFeedback').innerHTML = `<strong>Feedback:</strong> ${data.feedback} <br><small style="color: #94a3b8;">(Graded by: ${data.engine} | Response Language: ${data.breakdown.response_language})</small>`;

      // Update Cumulative stats
      cumulativePoints += data.total_score;
      currentRoundNum += 1;
      document.getElementById('cumulativeScore').innerText = cumulativePoints;
      document.getElementById('roundNum').innerText = currentRoundNum;

      card.scrollIntoView({ behavior: 'smooth' });
    }

    // Initialize round on load
    window.onload = startNewRound;
  </script>
</body>
</html>
"""

class GameHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/" or parsed.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
        elif parsed.path == "/api/new-round":
            round_data = engine.start_round()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(round_data).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))

        if parsed.path == "/api/submit-guess":
            body = self.rfile.read(content_length)
            payload = json.loads(body.decode("utf-8"))
            result = engine.evaluate(
                round_id=payload.get("round_id"),
                guessed_lang_code=payload.get("guessed_lang"),
                guessed_meaning=payload.get("guessed_meaning"),
                response_lang_code=payload.get("response_lang", "en-IN"),
            )
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode("utf-8"))

        elif parsed.path == "/api/transcribe":
            # Read multipart or raw audio data
            content_type = self.headers.get("Content-Type", "")
            raw_body = self.rfile.read(content_length)

            query_params = parse_qs(parsed.query)
            lang_code = query_params.get("lang", ["en-IN"])[0]

            # Extract audio bytes from multipart payload or raw bytes
            audio_bytes = raw_body
            if "multipart/form-data" in content_type and b"\r\n\r\n" in raw_body:
                header_end = raw_body.find(b"\r\n\r\n") + 4
                boundary = content_type.split("boundary=")[-1].strip()
                footer_pos = raw_body.rfind(f"\r\n--{boundary}".encode())
                if footer_pos != -1:
                    audio_bytes = raw_body[header_end:footer_pos]
                else:
                    audio_bytes = raw_body[header_end:]

            result = engine.transcribe_dictation(audio_bytes, language_code=lang_code)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Clean logging
        sys.stderr.write("%s - - [%s] %s\n" % (self.address_string(), self.log_date_time_string(), format % args))

def run_server(port=PORT):
    server_address = ("127.0.0.1", port)
    httpd = HTTPServer(server_address, GameHandler)
    print(f"IndicVani Game Server running at http://localhost:{port}/")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        httpd.server_close()

if __name__ == "__main__":
    run_server()
