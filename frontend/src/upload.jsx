import React, { useState, useEffect, useRef } from 'react';

export default function Upload({ label }) {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isGeoTIFF, setIsGeoTIFF] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [zoom, setZoom] = useState(1);
  const missionLogRef = useRef(null);

  const handleFileChange = (event) => {
    const selected = event.target.files[0];
    if (!selected) return;

    setFile(selected);
    setAnalysisResult(null);
    setZoom(1);

    const ext = selected.name.split('.').pop().toLowerCase();
    if (['tiff', 'geotiff'].includes(ext)) {
      setIsGeoTIFF(true);
      if (previewUrl) URL.revokeObjectURL(previewUrl);
      setPreviewUrl(null);
    } else if (['jpg', 'jpeg', 'png'].includes(ext)) {
      setIsGeoTIFF(false);
      if (previewUrl) URL.revokeObjectURL(previewUrl);
      setPreviewUrl(URL.createObjectURL(selected));
    } else {
      setIsGeoTIFF(false);
      if (previewUrl) URL.revokeObjectURL(previewUrl);
      setPreviewUrl(null);
      alert('Unsupported file format. Accepted: JPG, PNG, GeoTIFF.');
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setIsLoading(true);
    setProgress(0);
    setAnalysisResult(null);

    const formData = new FormData();
    formData.append('file', file);

    const fakeInterval = setInterval(() => {
      setProgress((p) => (p >= 90 ? 90 : p + 10));
    }, 300);

    try {
      const res = await fetch('/upload', {
        method: 'POST',
        body: formData,
      });
      const json = await res.json();
      setAnalysisResult(json);
    } catch (err) {
      console.error('Upload error:', err);
      setAnalysisResult({ error: 'Upload/analysis failed.' });
    } finally {
      clearInterval(fakeInterval);
      setProgress(100);
      setIsLoading(false);
    }
  };

  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl);
    };
  }, [previewUrl]);

  useEffect(() => {
    if (analysisResult && missionLogRef.current) {
      missionLogRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }, [analysisResult]);

  const getAnomalies = () => {
    if (!analysisResult) return [];
    if (Array.isArray(analysisResult.anomalies)) return analysisResult.anomalies;
    if (Array.isArray(analysisResult.anomalies_detected?.anomalies_detected))
      return analysisResult.anomalies_detected.anomalies_detected;
    return [];
  };

  const totalDetected = () => {
    const summary = analysisResult?.detections?.summary;
    if (!summary) return 0;
    return Object.values(summary).reduce((a, b) => a + b, 0);
  };

  return (
    <div className="upload-card card">
      <div className="card-header">
        <div className="label">
          <div className="dot" />
          <h2>{label}</h2>
        </div>
        <div className="actions">
          <input
            id="single-file"
            type="file"
            accept=".jpg,.jpeg,.png,.tiff,.geotiff"
            onChange={handleFileChange}
            style={{ display: 'none' }}
          />
          <label htmlFor="single-file" className="btn small">
            Choose Image
          </label>
          <button
            onClick={handleUpload}
            disabled={!file || isLoading}
            className="btn primary"
          >
            {isLoading ? 'Analyzing...' : 'Analyze'}
          </button>
        </div>
      </div>

      {isLoading && (
        <div className="progress-wrapper">
          <div className="progress-bar">
            <div className="fill" style={{ width: `${progress}%` }} />
          </div>
        </div>
      )}

      <div className="preview-zone">
        <div className="image-preview">
          <h3>Preview</h3>
          <div className="zoom-controls">
            <button
              onClick={() => setZoom((z) => Math.max(0.5, +(z - 0.1).toFixed(2)))}
              disabled={!previewUrl}
            >
              -
            </button>
            <span>{Math.round(zoom * 100)}%</span>
            <button
              onClick={() => setZoom((z) => Math.min(3, +(z + 0.1).toFixed(2)))}
              disabled={!previewUrl}
            >
              +
            </button>
          </div>
          <div className="preview-wrapper fixed-preview">
            {previewUrl ? (
              <img
                src={previewUrl}
                alt="upload preview"
                style={{
                  width: '100%',
                  height: '100%',
                  objectFit: 'cover',
                  transform: `scale(${zoom})`,
                  transformOrigin: 'center center',
                  borderRadius: '8px',
                }}
              />
            ) : (
              <div className="placeholder">
                <p>No image selected</p>
                <p style={{ fontSize: '0.8rem', marginTop: 4 }}>
                  Choose an image to preview
                </p>
              </div>
            )}
          </div>
        </div>
        {isGeoTIFF && file && (
          <div className="geotiff-placeholder">
            <p>GeoTIFF preview would render here.</p>
          </div>
        )}
      </div>

      {analysisResult && (
        <div className="mission-log" ref={missionLogRef}>
          <h3>Mission Log: Intelligence Report</h3>
          {analysisResult.error ? (
            <p className="error">{analysisResult.error}</p>
          ) : (
            <>
              {(analysisResult.caption || analysisResult.classification) && (
                <div className="section table-box">
                  <strong>Caption & Classification</strong>
                  <table>
                    <tbody>
                      <tr>
                        <th>Caption</th>
                        <td>{analysisResult.caption?.text || '—'}</td>
                      </tr>

                     <tr>
                       <th>Classification</th>
                       <td>{analysisResult.classification?.label || 'N/A'}</td>
                     </tr>

                    </tbody>
                  </table>
                </div>
              )}

              {analysisResult.detections?.summary && (
                <div className="section summary-box">
                  <strong>Detection Summary:</strong>
                  <ul>
                    {Object.entries(analysisResult.detections.summary).map(([lbl, cnt]) => (
                      <li key={lbl}>
                        {lbl.charAt(0).toUpperCase() + lbl.slice(1)}: {cnt}
                      </li>
                    ))}
                  </ul>
                  <p>
                    <strong>Total:</strong> {totalDetected()}
                  </p>
                </div>
              )}

              {getAnomalies().length > 0 && (
                <div className="section anomaly-box">
                  <strong>Anomalies:</strong>
                  <ul>
                    {getAnomalies().map((a, i) => {
                      if (typeof a === 'string') {
                        return <li key={i}>{a}</li>;
                      } else if (a && typeof a === 'object') {
                        return (
                          <li key={i}>
                            {a.description || JSON.stringify(a)}
                            {a.person_count !== undefined && ` (Persons: ${a.person_count})`}
                            {a.severity && ` [Severity: ${a.severity}]`}
                          </li>
                        );
                      } else {
                        return <li key={i}>{String(a)}</li>;
                      }
                    })}
                  </ul>
                  <p>
                    <strong>Count:</strong>{' '}
                    {analysisResult.anomalies_detected?.count ?? getAnomalies().length}
                  </p>
                </div>
              )}

              {analysisResult.naval_assessment && (
                <div className="section assessment-box">
                  <strong>Naval Assessment:</strong>
                  <p>Status: {analysisResult.naval_assessment.status || 'N/A'}</p>
                  <p>Priority: {analysisResult.naval_assessment.priority || 'N/A'}</p>
                  <p>
                    Recommendation:{' '}
                    {analysisResult.naval_assessment.recommendation || 'N/A'}
                  </p>
                </div>
              )}
            </>
          )}
          <button className="btn secondary" onClick={() => setAnalysisResult(null)}>
            Close
          </button>
        </div>
      )}
    </div>
  );
}
