from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import google.generativeai as genai
import json
import re

app = Flask(__name__)
CORS(app)

# 1. Gemini API Key Configuration
GEMINI_API_KEY = "AQ.Ab8RN6Iq3kIPSXR_Xou8mEnvUah9iwFdgY0A95ld7WvewR6Seg"
genai.configure(api_key=GEMINI_API_KEY)

# 2. Integrated Clean Glassmorphism UI
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI Meeting Notes Summarizer Pro</title>
  <style>
    :root {
      --primary: #3b82f6;
      --primary-hover: #2563eb;
      --bg: #0f172a;
      --card-bg: rgba(30, 41, 59, 0.7);
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --accent-green: #10b981;
      --border: rgba(255, 255, 255, 0.1);
      --accent-purple: #8b5cf6;
      --danger: #ef4444;
    }

    body {
      font-family: 'Inter', system-ui, -apple-system, sans-serif;
      background: var(--bg);
      background-image: radial-gradient(at 0% 0%, rgba(59, 130, 246, 0.25) 0px, transparent 50%),
                        radial-gradient(at 100% 100%, rgba(139, 92, 246, 0.25) 0px, transparent 50%);
      color: var(--text-main);
      margin: 0;
      padding: 40px 20px;
      min-height: 100vh;
      box-sizing: border-box;
    }

    .container { max-width: 850px; margin: 0 auto; }

    .badge {
      display: inline-block;
      background: rgba(139, 92, 246, 0.15);
      color: var(--accent-purple);
      border: 1px solid rgba(139, 92, 246, 0.4);
      padding: 6px 16px;
      border-radius: 20px;
      font-size: 0.85rem;
      font-weight: 600;
      margin-bottom: 12px;
      letter-spacing: 0.5px;
    }

    .app-header { text-align: center; margin-bottom: 35px; }
    .app-header h1 { font-size: 2.6rem; margin: 0 0 10px 0; font-weight: 800; letter-spacing: -0.5px; }
    .app-header p { color: var(--text-muted); font-size: 1.1rem; margin: 0; }

    .input-section {
      background: var(--card-bg);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      padding: 28px;
      border-radius: 20px;
      border: 1px solid var(--border);
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
      margin-bottom: 28px;
    }

    .section-top {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 14px;
    }

    .btn-group-top { display: flex; gap: 10px; }

    .action-btn {
      background: rgba(255, 255, 255, 0.05);
      color: #e2e8f0;
      border: 1px solid var(--border);
      padding: 9px 16px;
      font-size: 0.88rem;
      border-radius: 10px;
      cursor: pointer;
      font-weight: 600;
      transition: all 0.2s ease;
    }

    .action-btn:hover {
      background: rgba(59, 130, 246, 0.2);
      border-color: var(--primary);
      color: #fff;
    }

    .mic-active {
      background: rgba(239, 68, 68, 0.25) !important;
      color: var(--danger) !important;
      border-color: var(--danger) !important;
      animation: pulse 1.5s infinite;
    }

    @keyframes pulse {
      0% { opacity: 1; }
      50% { opacity: 0.5; }
      100% { opacity: 1; }
    }

    textarea {
      width: 100%;
      height: 180px;
      padding: 16px;
      background: rgba(15, 23, 42, 0.8);
      color: var(--text-main);
      border: 1px solid var(--border);
      border-radius: 12px;
      font-size: 1rem;
      line-height: 1.5;
      box-sizing: border-box;
      outline: none;
      resize: vertical;
      transition: border-color 0.2s ease;
    }

    textarea:focus { border-color: var(--primary); }

    .button-group-bottom { text-align: right; margin-top: 18px; }

    .primary-btn {
      background: linear-gradient(135deg, var(--primary), var(--accent-purple));
      color: white;
      border: none;
      padding: 14px 32px;
      font-size: 1rem;
      font-weight: 700;
      border-radius: 10px;
      cursor: pointer;
      box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
      transition: transform 0.1s ease, box-shadow 0.2s ease;
    }

    .primary-btn:hover {
      transform: translateY(-1px);
      box-shadow: 0 6px 20px rgba(59, 130, 246, 0.6);
    }

    .results-card {
      background: var(--card-bg);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      padding: 32px;
      border-radius: 20px;
      border: 1px solid var(--border);
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
    }

    .styled-list { padding-left: 20px; margin: 12px 0 0 0; }
    .styled-list li { margin-bottom: 10px; color: #cbd5e1; line-height: 1.5; }
    
    .task-list li {
      background: rgba(15, 23, 42, 0.6);
      list-style-type: none;
      padding: 12px 18px;
      border-radius: 10px;
      margin-bottom: 10px;
      margin-left: -20px;
      border-left: 4px solid var(--accent-green);
    }

    h2 { font-size: 1.25rem; margin: 0 0 8px 0; color: #f1f5f9; }
  </style>
</head>
<body>
  <div class="container">
    <header class="app-header">
      <div class="badge">✨ Gemini AI Powered</div>
      <h1>📝 Meeting Intelligence Hub</h1>
      <p>Transform raw meeting audio & transcripts into executive summaries, key decisions, and actionable tasks.</p>
    </header>

    <main class="input-section">
      <div class="section-top">
        <label for="transcript-input"><strong>Meeting Transcript / Speak Into Mic:</strong></label>
        <div class="btn-group-top">
          <button type="button" id="mic-btn" class="action-btn" onclick="toggleVoiceInput()">🎙️ Voice Input</button>
          <button type="button" class="action-btn" onclick="loadSampleData()">⚡ Load Demo Preset</button>
        </div>
      </div>

      <textarea id="transcript-input" placeholder="Click 'Voice Input' and speak into your mic, or type/paste any custom meeting transcript here..."></textarea>
      
      <div class="button-group-bottom">
        <button id="submit-btn" class="primary-btn" onclick="generateSummary()">🚀 Process & Summarize</button>
      </div>
    </main>

    <section id="results" class="results-card" style="display: none;">
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <h2>📌 Executive Summary</h2>
        <button type="button" id="speak-btn" class="action-btn" onclick="toggleTextToSpeech()">🔊 Read Out Loud</button>
      </div>
      <p id="summary-text" style="line-height: 1.6; color: #cbd5e1; margin-top: 10px;"></p>
      <hr style="border:0; height:1px; background:var(--border); margin: 24px 0;">
      <h2>💡 Key Decisions Made</h2>
      <ul id="decisions-list" class="styled-list"></ul>
      <hr style="border:0; height:1px; background:var(--border); margin: 24px 0;">
      <h2>✅ Action Items & Assignments</h2>
      <ul id="action-list" class="styled-list task-list"></ul>
    </section>
  </div>

  <script>
    let recognition = null;
    let isListening = false;
    let isSpeaking = false;

    function loadSampleData() {
      document.getElementById('transcript-input').value = "The client approved the new landing page wireframes during today's sync. Rahul will write the content copy for the homepage by Wednesday. Priya handles setting up Google Analytics and tracking tags before launch. We agreed to allocate an extra $500 to the social media ad campaign next week.";
    }

    function toggleVoiceInput() {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const micBtn = document.getElementById('mic-btn');
      const textarea = document.getElementById('transcript-input');

      if (!SpeechRecognition) {
        alert("Please open this link in Google Chrome!");
        return;
      }

      if (isListening) {
        recognition.stop();
        return;
      }

      recognition = new SpeechRecognition();
      recognition.lang = 'en-US';
      recognition.continuous = true;

      recognition.onstart = function() {
        isListening = true;
        micBtn.innerText = "🔴 Listening... (Click to Stop)";
        micBtn.classList.add('mic-active');
      };

      recognition.onresult = function(event) {
        const current = event.resultIndex;
        const transcript = event.results[current][0].transcript;
        textarea.value += (textarea.value ? " " : "") + transcript;
      };

      recognition.onend = function() {
        isListening = false;
        micBtn.innerText = "🎙️ Voice Input";
        micBtn.classList.remove('mic-active');
      };

      recognition.start();
    }

    function generateSummary() {
      const transcript = document.getElementById('transcript-input').value.trim();
      const btn = document.getElementById('submit-btn');

      if (!transcript) {
        alert("Please speak or type a transcript first!");
        return;
      }

      btn.innerText = "⚡ Processing with Gemini AI...";

      fetch('/summarize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ transcript: transcript })
      })
      .then(res => res.json())
      .then(data => {
        if (data.error) {
          alert("AI Error: " + data.error);
          return;
        }
        renderResults(data);
      })
      .catch(err => alert("Connection error: " + err))
      .finally(() => btn.innerText = "🚀 Process & Summarize");
    }

    function renderResults(data) {
      document.getElementById('results').style.display = 'block';
      document.getElementById('summary-text').innerText = data.summary;

      const decisionsList = document.getElementById('decisions-list');
      decisionsList.innerHTML = '';
      (data.decisions || []).forEach(item => {
        let li = document.createElement('li');
        li.innerText = item;
        decisionsList.appendChild(li);
      });

      const actionList = document.getElementById('action-list');
      actionList.innerHTML = '';
      (data.action_items || []).forEach(item => {
        let li = document.createElement('li');
        li.innerText = item;
        actionList.appendChild(li);
      });

      document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
    }

    function toggleTextToSpeech() {
      const speakBtn = document.getElementById('speak-btn');

      if (!('speechSynthesis' in window)) {
        alert("Text-to-speech is not supported in this browser.");
        return;
      }

      if (isSpeaking) {
        window.speechSynthesis.cancel();
        isSpeaking = false;
        speakBtn.innerText = "🔊 Read Out Loud";
        return;
      }

      const summary = document.getElementById('summary-text').innerText;
      const decisions = Array.from(document.querySelectorAll('#decisions-list li')).map(li => li.innerText).join('. ');
      const actions = Array.from(document.querySelectorAll('#action-list li')).map(li => li.innerText).join('. ');

      const textToRead = `Executive Summary. ${summary}. Key Decisions. ${decisions}. Action Items. ${actions}.`;

      const utterance = new SpeechSynthesisUtterance(textToRead);
      utterance.rate = 0.95;

      utterance.onstart = function() {
        isSpeaking = true;
        speakBtn.innerText = "⏹️ Stop Speaking";
      };

      utterance.onend = function() {
        isSpeaking = false;
        speakBtn.innerText = "🔊 Read Out Loud";
      };

      utterance.onerror = function() {
        isSpeaking = false;
        speakBtn.innerText = "🔊 Read Out Loud";
      };

      window.speechSynthesis.speak(utterance);
    }
  </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/summarize', methods=['POST'])
def summarize_meeting():
    data = request.get_json() or {}
    transcript = data.get('transcript', '').strip()

    if not transcript:
        return jsonify({'error': 'Transcript text is empty'}), 400

    prompt = f"""
    Analyze this meeting transcript and output valid JSON ONLY:
    {{
      "summary": "a short clear summary string",
      "decisions": ["list of key decision strings"],
      "action_items": ["list of action item strings"]
    }}

    Transcript: "{transcript}"
    """

    candidate_models = ['gemini-2.5-flash', 'gemini-1.5-flash-8b', 'gemini-1.5-pro']
    
    for name in candidate_models:
        try:
            model = genai.GenerativeModel(name)
            response = model.generate_content(prompt)
            if response and response.text:
                json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                clean_json = json_match.group(0) if json_match else response.text
                result_data = json.loads(clean_json)
                return jsonify({
                    'status': 'success',
                    'summary': result_data.get('summary', ''),
                    'decisions': result_data.get('decisions', []),
                    'action_items': result_data.get('action_items', [])
                }), 200
        except Exception:
            continue

    # Rule-Based Fallback Engine
    sentences = [s.strip() for s in re.split(r'[.!?]', transcript) if s.strip()]
    summary_text = sentences[0] if sentences else transcript
    
    return jsonify({
        'status': 'success',
        'summary': f"Key Discussion Point: {summary_text}.",
        'decisions': [s for s in sentences if any(w in s.lower() for w in ['agree', 'approved', 'decide', 'ok', 'yes', 'final']) or len(sentences) <= 2],
        'action_items': [s for s in sentences if any(w in s.lower() for w in ['will', 'handle', 'by', 'need', 'task', 'assigned', 'should'])] or sentences
    }), 200

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)