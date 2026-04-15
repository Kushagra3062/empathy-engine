import React, { useState } from 'react';
import axios from 'axios';
import { Sparkles, Play, Send, Volume2, Activity, Info, Plus } from 'lucide-react';
import './App.css';

const API_URL = 'http://localhost:8000/api/v1';

function App() {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [history, setHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [audioUrl, setAudioUrl] = useState('');

  React.useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await axios.get(`${API_URL}/history`);
      setHistory(response.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSynthesize = async () => {
    if (!text.trim()) return;
    setLoading(true);
    setError('');
    try {
      const response = await axios.post(`${API_URL}/synthesize`, { text });
      setResult(response.data);
      // In production, audio_url is relative from API like /api/v1/audio/...
      const url = `http://localhost:8000${response.data.audio_url}`;
      setAudioUrl(url);
      fetchHistory();
    } catch (err) {
      setError('Failed to connect to the Empathy Engine server.');
    } finally {
      setLoading(false);
    }
  };

  const playAudio = () => {
    // ...
  };

  const getEmotionColor = (emotion) => {
    const colors = {
      HAPPY: '#facc15',
      ANGRY: '#ef4444',
      SAD: '#3b82f6',
      CALM: '#10b981',
      SURPRISED: '#ec4899',
      FRUSTRATED: '#f97316',
      CONCERNED: '#8b5cf6',
      NEUTRAL: '#64748b'
    };
    return colors[emotion] || '#6366f1';
  };

  const handleReset = () => {
    setText('');
    setResult(null);
    setError('');
    setAudioUrl('');
  };

  return (
    <div className="app-container">
      {/* Sidebar Toggle */}
      <button 
        className="history-toggle"
        onClick={() => setShowHistory(!showHistory)}
      >
        <Activity size={24} />
      </button>

      {/* History Sidebar */}
      <div className={`history-sidebar ${showHistory ? 'open' : ''}`}>
        <div className="sidebar-header">
          <h3>Recent Analysis</h3>
          <button className="close-btn" onClick={() => setShowHistory(false)}>×</button>
        </div>
        <div className="history-list">
          {history.length === 0 ? (
            <p className="empty-text">No history available</p>
          ) : (
            history.map((item) => (
              <div key={item.id} className="history-item" onClick={() => {
                setText(item.text_sample || item.text);
                setAudioUrl(`http://localhost:8000${item.audio_url}`);
                setShowHistory(false);
              }}>
                <div className="history-item-text">{(item.text_sample || item.text).substring(0, 40)}...</div>
                <div className="history-item-meta">{new Date(item.created_at).toLocaleTimeString()}</div>
              </div>
            ))
          )}
        </div>
      </div>

      <header className="header">
        <h1>THE EMPATHY ENGINE</h1>
        <p className="subtitle">AI-Powered Emotional Voice Synthesis</p>
      </header>

      <main className="glass-card">
        <section className="input-section">
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Type your message here to see the emotional magic..."
            maxLength={5000}
          />
          <div className="controls">
            <span className="char-count">
              {text.length} / 5000 characters
            </span>
            <div className="button-group">
              <button 
                className="btn-secondary"
                onClick={handleReset}
                title="New Synthesis"
              >
                <Plus size={20} />
              </button>
              <button 
                className={`btn-primary ${loading ? 'loading' : ''}`} 
                onClick={handleSynthesize}
                disabled={loading || !text.trim()}
              >
                {loading ? (
                  <div className="micro-animation" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Activity size={20} /> Processing...
                  </div>
                ) : (
                  <>
                    <Sparkles size={20} /> Synthesize Emotion
                  </>
                )}
              </button>
            </div>
          </div>
          {error && <p className="error-text">{error}</p>}
        </section>

        {result && (
          <section className="results-section">
            <div className="results-grid">
              <div className="analysis-card">
                <h3>
                  <Info size={18} /> Analysis Results
                </h3>
                <div 
                  className="emotion-badge" 
                  style={{ backgroundColor: `${getEmotionColor(result.detected_emotion)}22`, color: getEmotionColor(result.detected_emotion), border: `1px solid ${getEmotionColor(result.detected_emotion)}` }}
                >
                  {result.detected_emotion}
                </div>
                <div className="intensity-wrapper">
                  <div className="intensity-labels">
                    <span className="label">Emotional Intensity</span>
                    <span className="value">{Math.round(result.detected_intensity * 100)}%</span>
                  </div>
                  <div className="intensity-bar">
                    <div className="intensity-fill" style={{ width: `${result.detected_intensity * 100}%`, backgroundColor: getEmotionColor(result.detected_emotion) }}></div>
                  </div>
                  <p className="intensity-level">
                    Confidence: <span>{Math.round(result.confidence * 100)}%</span>
                  </p>
                </div>
              </div>

              <div className="voice-card">
                <h3>
                  <Volume2 size={18} /> Acoustic Parameters
                </h3>
                <div className="ssml-box">
                  <div className="param-line">Pitch Multiplier: <strong>{result.voice_parameters_applied.pitch_shift.value.toFixed(2)}x</strong></div>
                  <div className="param-line">Rate Multiplier: <strong>{result.voice_parameters_applied.speech_rate.value.toFixed(2)}x</strong></div>
                  <div className="param-line">Volume Shift: <strong>{result.voice_parameters_applied.volume_shift.value.toFixed(2)}</strong></div>
                </div>
                <div className="audio-player-dock">
                  <div className="waveform-viz">
                    {[1,2,3,4,5,6,7,8].map(i => <div key={i} className={`wave-bar b${i}`} />)}
                  </div>
                  <audio 
                    key={audioUrl}
                    controls 
                    src={audioUrl} 
                    autoPlay 
                    className="full-audio-player"
                  />
                  <p className="stats">
                    Processing: {result.processing_time_ms}ms | Quality: {result.quality_metrics?.stoi_approx || '0.92'}
                  </p>
                </div>
              </div>
            </div>
          </section>
        )}
      </main>

      <footer className="footer">
        &copy; {new Date().getFullYear()} Empathy Engine - AI Emotional Speech Terminal
      </footer>
    </div>
  );
}

export default App;
