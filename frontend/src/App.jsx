import React, { useState } from 'react'
import './App.css'

function App() {
  const [ticker, setTicker] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const fetchData = async () => {
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const response = await fetch(
        `https://stock-fear-index-app.onrender.com/api/fear-index?ticker=${ticker}`
      );
      const data = await response.json();
      if (data.error) {
        setError(data.error);
      } else {
        setResult(data);
      }
    } catch (err) {
      setError("요청 실패: " + err.message);
    }
    setLoading(false);
  };

  return (
    <div className="App">
      <h1>📊 공포탐욕지수 조회</h1>
      <input
        type="text"
        placeholder="티커 입력 (예: TSLA)"
        value={ticker}
        onChange={(e) => setTicker(e.target.value)}
      />
      <button onClick={fetchData} disabled={loading}>
        조회
      </button>
      {loading && <p>불러오는 중...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
      {result && (
        <div className="result">
          <h2>{result.name} ({result.ticker})</h2>
          <p><strong>점수:</strong> {result.score}점</p>
          <p><strong>상태:</strong> {result.status}</p>
          <ul>
            {result.details.map((item, idx) => (
              <li key={idx}>{item.label}: {item.value}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;
