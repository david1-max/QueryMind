import React, { useState, useEffect } from 'react';
import { 
  Database, 
  Play, 
  History, 
  CheckCircle, 
  AlertTriangle, 
  Clock, 
  Layers, 
  TrendingUp, 
  Cpu, 
  ArrowRight,
  RefreshCw
} from 'lucide-react';

const API_BASE = 'http://127.0.0.1:8000';

const TEST_TEMPLATES = [
  {
    name: "User Lookup by Email",
    query: "SELECT * FROM users WHERE email = 'neha.yadav100@gmail.com'"
  },
  {
    name: "Join Users and Orders",
    query: "SELECT * FROM users JOIN orders ON users.id = orders.user_id WHERE users.name = 'Divyanshu Yadav'"
  },
  {
    name: "Filter & Sort Orders",
    query: "SELECT * FROM orders WHERE status = 'PENDING' ORDER BY ordered_at DESC LIMIT 10"
  }
];

function App() {
  const [activeTab, setActiveTab] = useState('console');
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [backendStatus, setBackendStatus] = useState('connecting');
  const [analysis, setAnalysis] = useState(null);
  const [benchmark, setBenchmark] = useState(null);
  const [history, setHistory] = useState([]);
  const [errorMsg, setErrorMsg] = useState('');

  // Check backend status on load
  useEffect(() => {
    checkStatus();
    loadHistory();
  }, []);

  const checkStatus = async () => {
    try {
      const res = await fetch(`${API_BASE}/`);
      const data = await res.json();
      if (data.status === 'healthy') {
        setBackendStatus('online');
      } else {
        setBackendStatus('error');
      }
    } catch (e) {
      setBackendStatus('offline');
    }
  };

  const loadHistory = async () => {
    try {
      const res = await fetch(`${API_BASE}/history`);
      const data = await res.json();
      setHistory(data);
    } catch (e) {
      console.error("Failed to load history:", e);
    }
  };

  const handleAnalyze = async () => {
    if (!query.trim()) {
      setErrorMsg("Please enter a SQL query first.");
      return;
    }
    setErrorMsg('');
    setLoading(true);
    setAnalysis(null);
    setBenchmark(null);
    
    try {
      const res = await fetch(`${API_BASE}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      });
      const data = await res.json();
      
      if (!res.ok) {
        throw new Error(data.detail || "Analysis failed");
      }
      
      setAnalysis(data);
    } catch (e) {
      setErrorMsg(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleApplyIndex = async (indexSql) => {
    setErrorMsg('');
    setLoading(true);
    
    try {
      const res = await fetch(`${API_BASE}/apply`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, index_sql: indexSql })
      });
      const data = await res.json();
      
      if (!res.ok) {
        throw new Error(data.detail || "Optimization failed");
      }
      
      setBenchmark(data);
      loadHistory(); // reload logs
    } catch (e) {
      setErrorMsg(e.message);
    } finally {
      setLoading(false);
    }
  };

  const selectTemplate = (q) => {
    setQuery(q);
    setAnalysis(null);
    setBenchmark(null);
    setErrorMsg('');
  };

  return (
    <div className="dashboard-layout">
      {/* Sidebar Navigation */}
      <aside className="sidebar">
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '40px' }}>
          <Database size={32} color="#6366F1" style={{ filter: 'drop-shadow(0 0 8px rgba(99, 102, 241, 0.4))' }} />
          <h2 style={{ fontSize: '22px', fontWeight: '800', letterSpacing: '-0.5px' }}>
            Query<span style={{ color: '#A855F7' }}>Mind</span>
          </h2>
        </div>

        <nav style={{ display: 'flex', flexDirection: 'column', gap: '8px', flex: 1 }}>
          <button 
            className={`btn ${activeTab === 'console' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ width: '100%', justifyContent: 'flex-start' }}
            onClick={() => setActiveTab('console')}
          >
            <Play size={18} />
            Optimization Console
          </button>
          
          <button 
            className={`btn ${activeTab === 'history' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ width: '100%', justifyContent: 'flex-start' }}
            onClick={() => setActiveTab('history')}
          >
            <History size={18} />
            Optimization History
          </button>
        </nav>

        {/* Status Indicator */}
        <div style={{ borderTop: '1px solid rgba(255, 255, 255, 0.06)', paddingTop: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px' }}>
            <span style={{ 
              width: '10px', 
              height: '10px', 
              borderRadius: '50%', 
              backgroundColor: backendStatus === 'online' ? '#10B981' : '#EF4444',
              boxShadow: backendStatus === 'online' ? '0 0 10px #10B981' : '0 0 10px #EF4444'
            }} />
            <span style={{ textTransform: 'capitalize', color: '#9CA3AF' }}>
              Database Sandbox: {backendStatus}
            </span>
            <button 
              onClick={checkStatus} 
              style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#9CA3AF', padding: 0 }}
              title="Refresh connection"
            >
              <RefreshCw size={14} />
            </button>
          </div>
        </div>
      </aside>

      {/* Main Panel Content */}
      <main className="main-content">
        {activeTab === 'console' ? (
          <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '30px' }}>
            
            {/* Page Header */}
            <div>
              <h1 className="gradient-title" style={{ fontSize: '36px', marginBottom: '6px' }}>AI-Powered SQL Optimizer</h1>
              <p style={{ color: '#9CA3AF', fontSize: '15px' }}>
                Analyze SQLite execution plans, isolate slow full-table scans, and benchmark performance improvements instantly.
              </p>
            </div>

            {/* Input Panel */}
            <section className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h3 style={{ fontSize: '18px', fontWeight: '600' }}>Enter SQL Query</h3>
                <span style={{ fontSize: '12px', color: '#6366F1', fontWeight: '500' }}>Target: Sandbox DB (300k Rows)</span>
              </div>

              <textarea 
                className="sql-textarea"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="SELECT * FROM users WHERE email = '...'"
              />

              {/* Test Templates */}
              <div>
                <span style={{ fontSize: '13px', color: '#9CA3AF', display: 'block', marginBottom: '8px' }}>
                  Quick Templates (Click to load):
                </span>
                <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                  {TEST_TEMPLATES.map((t, idx) => (
                    <button 
                      key={idx} 
                      className="template-pill"
                      onClick={() => selectTemplate(t.query)}
                    >
                      {t.name}
                    </button>
                  ))}
                </div>
              </div>

              <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end', marginTop: '10px' }}>
                <button 
                  className="btn btn-primary"
                  onClick={handleAnalyze}
                  disabled={loading}
                >
                  {loading ? 'Processing...' : 'Run Plan Analysis'}
                  <Play size={16} />
                </button>
              </div>

              {errorMsg && (
                <div style={{ 
                  background: 'rgba(239, 68, 68, 0.1)', 
                  border: '1px solid rgba(239, 68, 68, 0.25)', 
                  color: '#F87171', 
                  padding: '12px 16px', 
                  borderRadius: '8px', 
                  fontSize: '14px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  <AlertTriangle size={18} />
                  {errorMsg}
                </div>
              )}
            </section>

            {/* Analysis Results Panel */}
            {analysis && (
              <section className="glass-card fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                <h3 style={{ fontSize: '18px', fontWeight: '600', borderBottom: '1px solid rgba(255, 255, 255, 0.06)', paddingBottom: '12px' }}>
                  Execution Plan Analysis
                </h3>

                {/* Table Scans */}
                <div>
                  <h4 style={{ fontSize: '14px', color: '#9CA3AF', marginBottom: '8px' }}>Detected Table Scans:</h4>
                  <div style={{ display: 'flex', gap: '10px' }}>
                    {analysis.scanned_tables.length > 0 ? (
                      analysis.scanned_tables.map((t, i) => (
                        <span key={i} className="badge badge-warning">
                          <AlertTriangle size={12} style={{ marginRight: '6px' }} />
                          Unoptimized SCAN: {t}
                        </span>
                      ))
                    ) : (
                      <span className="badge badge-success">
                        <CheckCircle size={12} style={{ marginRight: '6px' }} />
                        No full table scans detected (Optimal Indexing)
                      </span>
                    )}
                  </div>
                </div>

                {/* Raw Plan */}
                <div>
                  <h4 style={{ fontSize: '14px', color: '#9CA3AF', marginBottom: '6px' }}>SQLite Raw Execution Steps:</h4>
                  <div style={{ 
                    background: '#0D1117', 
                    borderRadius: '8px', 
                    padding: '12px 16px', 
                    fontFamily: 'Fira Code, monospace', 
                    fontSize: '13px',
                    color: '#8B949E'
                  }}>
                    {analysis.explain_plan.map((step, idx) => (
                      <div key={idx} style={{ marginBottom: '4px' }}>
                        <span style={{ color: '#58A6FF' }}>{idx + 1}.</span> {step}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Recommendations */}
                <div>
                  <h4 style={{ fontSize: '14px', color: '#9CA3AF', marginBottom: '12px' }}>Index Recommendations:</h4>
                  {analysis.recommendations.length > 0 ? (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                      {analysis.recommendations.map((rec, idx) => (
                        <div key={idx} style={{ 
                          background: 'rgba(99, 102, 241, 0.04)', 
                          border: '1px solid rgba(99, 102, 241, 0.15)', 
                          borderRadius: '10px', 
                          padding: '16px',
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          gap: '20px'
                        }}>
                          <div style={{ flex: 1 }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                              <span style={{ fontWeight: '700', fontSize: '14px', color: '#818CF8' }}>{rec.table}.{rec.column}</span>
                              <span style={{ fontSize: '12px', color: '#9CA3AF' }}>({rec.reason})</span>
                            </div>
                            <code style={{ 
                              fontFamily: 'Fira Code, monospace', 
                              fontSize: '13px', 
                              background: 'rgba(0, 0, 0, 0.2)', 
                              padding: '4px 8px', 
                              borderRadius: '4px',
                              color: '#C9D1D9'
                            }}>
                              {rec.sql}
                            </code>
                          </div>
                          
                          <button 
                            className="btn btn-success"
                            onClick={() => handleApplyIndex(rec.sql)}
                            disabled={loading}
                          >
                            Apply Index & Benchmark
                            <ArrowRight size={16} />
                          </button>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p style={{ fontSize: '14px', color: '#9CA3AF', fontStyle: 'italic' }}>
                      No index recommendations needed for this query.
                    </p>
                  )}
                </div>
              </section>
            )}

            {/* Benchmarking Report Panel */}
            {benchmark && (
              <section className="glass-card fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '24px', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#10B981', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <TrendingUp size={22} />
                    Optimization Benchmarking Report
                  </h3>
                  <div className="badge badge-success" style={{ fontSize: '16px', padding: '6px 14px', borderRadius: '8px' }}>
                    {benchmark.speedup} SPEEDUP
                  </div>
                </div>

                {/* Graphical comparison bar */}
                <div>
                  <h4 style={{ fontSize: '14px', color: '#9CA3AF', marginBottom: '8px' }}>Latency Profile (Lower is Better):</h4>
                  
                  {/* Bar 1: Before */}
                  <div className="bar-container">
                    <span className="bar-label">Before Index</span>
                    <div className="bar-track">
                      <div className="bar-fill-before" style={{ width: '100%' }} />
                      <span className="bar-time-val">{benchmark.time_before_ms.toFixed(3)} ms</span>
                    </div>
                  </div>

                  {/* Bar 2: After */}
                  <div className="bar-container">
                    <span className="bar-label">After Index</span>
                    {/* Calculate proportional width to show latency reduction */}
                    <div className="bar-track">
                      <div 
                        className="bar-fill-after" 
                        style={{ width: `${Math.max(2, (benchmark.time_after_ms / benchmark.time_before_ms) * 100)}%` }} 
                      />
                      <span className="bar-time-val">{benchmark.time_after_ms.toFixed(3)} ms</span>
                    </div>
                  </div>
                </div>

                {/* Plan comparison side-by-side */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginTop: '10px' }}>
                  <div>
                    <h4 style={{ fontSize: '13px', color: '#EF4444', marginBottom: '6px', fontWeight: '600' }}>Plan Before Optimization:</h4>
                    <div style={{ 
                      background: 'rgba(239, 68, 68, 0.04)', 
                      border: '1px solid rgba(239, 68, 68, 0.15)', 
                      borderRadius: '8px', 
                      padding: '12px',
                      fontFamily: 'Fira Code, monospace',
                      fontSize: '12px',
                      color: '#FCA5A5'
                    }}>
                      {benchmark.plan_before.map((p, idx) => (
                        <div key={idx}>{p}</div>
                      ))}
                    </div>
                  </div>

                  <div>
                    <h4 style={{ fontSize: '13px', color: '#10B981', marginBottom: '6px', fontWeight: '600' }}>Plan After Optimization:</h4>
                    <div style={{ 
                      background: 'rgba(16, 185, 129, 0.04)', 
                      border: '1px solid rgba(16, 185, 129, 0.15)', 
                      borderRadius: '8px', 
                      padding: '12px',
                      fontFamily: 'Fira Code, monospace',
                      fontSize: '12px',
                      color: '#6EE7B7'
                    }}>
                      {benchmark.plan_after.map((p, idx) => (
                        <div key={idx}>{p}</div>
                      ))}
                    </div>
                  </div>
                </div>
              </section>
            )}
          </div>
        ) : (
          <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '30px' }}>
            
            {/* Page Header */}
            <div>
              <h1 className="gradient-title" style={{ fontSize: '36px', marginBottom: '6px' }}>Optimization Logs</h1>
              <p style={{ color: '#9CA3AF', fontSize: '15px' }}>
                Review database optimization history, index mappings, and the aggregate performance improvements.
              </p>
            </div>

            {/* History Table */}
            <section className="glass-card">
              {history.length > 0 ? (
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '14px' }}>
                    <thead>
                      <tr style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.08)', color: '#9CA3AF' }}>
                        <th style={{ padding: '12px 16px', fontWeight: '600' }}>Scenario / SQL Query</th>
                        <th style={{ padding: '12px 16px', fontWeight: '600' }}>Created Index</th>
                        <th style={{ padding: '12px 16px', fontWeight: '600' }}>Before Latency</th>
                        <th style={{ padding: '12px 16px', fontWeight: '600' }}>After Latency</th>
                        <th style={{ padding: '12px 16px', fontWeight: '600' }}>Speedup Ratio</th>
                      </tr>
                    </thead>
                    <tbody>
                      {history.map((row) => (
                        <tr key={row.id} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.04)' }} className="glass-card-hover">
                          <td style={{ padding: '16px', fontFamily: 'Fira Code, monospace', fontSize: '12px', maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                            {row.query_text}
                          </td>
                          <td style={{ padding: '16px' }}>
                            <code style={{ fontFamily: 'Fira Code, monospace', fontSize: '12px', color: '#818CF8', background: 'rgba(129, 140, 248, 0.08)', padding: '2px 6px', borderRadius: '4px' }}>
                              {row.index_sql}
                            </code>
                          </td>
                          <td style={{ padding: '16px', color: '#EF4444' }}>{row.time_before.toFixed(2)} ms</td>
                          <td style={{ padding: '16px', color: '#10B981' }}>{row.time_after.toFixed(2)} ms</td>
                          <td style={{ padding: '16px', fontWeight: '700', color: '#34D399' }}>
                            {row.speedup.toFixed(2)}x
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div style={{ textAlign: 'center', padding: '40px', color: '#9CA3AF' }}>
                  <Clock size={48} style={{ marginBottom: '16px', color: '#4B5563' }} />
                  <p style={{ fontSize: '16px', fontWeight: '500', marginBottom: '4px' }}>No History Yet</p>
                  <p style={{ fontSize: '14px', color: '#6B7280' }}>Optimize queries in the console tab to build your performance benchmark history.</p>
                </div>
              )}
            </section>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
