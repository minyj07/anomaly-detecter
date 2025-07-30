import React, { useState } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';

function App() {
    const [trainFile, setTrainFile] = useState(null);
    const [detectFile, setDetectFile] = useState(null);
    const [anomalies, setAnomalies] = useState([]);
    const [message, setMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleTrainSubmit = async (e) => {
        e.preventDefault();
        if (!trainFile) {
            setMessage('학습할 로그 파일을 먼저 선택해주세요.');
            return;
        }
        setIsLoading(true);
        setMessage('');
        setAnomalies([]);

        const formData = new FormData();
        formData.append('file', trainFile);

        try {
            const response = await fetch('http://localhost:8000/train/', {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();
            if (response.ok) {
                setMessage(data.message || '모델 학습이 성공적으로 완료되었습니다.');
            } else {
                throw new Error(data.detail || '모델 학습 중 오류가 발생했습니다.');
            }
        } catch (error) {
            setMessage(error.toString());
        } finally {
            setIsLoading(false);
        }
    };

    const handleDetectSubmit = async (e) => {
        e.preventDefault();
        if (!detectFile) {
            setMessage('탐지할 로그 파일을 먼저 선택해주세요.');
            return;
        }
        setIsLoading(true);
        setMessage('');
        setAnomalies([]);

        const formData = new FormData();
        formData.append('file', detectFile);

        try {
            const response = await fetch('http://localhost:8000/detect/', {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();
            if (response.ok) {
                setAnomalies(data.anomalies || []);
                if (data.anomalies && data.anomalies.length > 0) {
                    setMessage(`총 ${data.anomalies.length}개의 비정상 로그가 탐지되었습니다.`);
                } else {
                    setMessage('탐지된 비정상 로그가 없습니다. 모든 로그가 정상 범위입니다.');
                }
            } else {
                throw new Error(data.detail || '이상 탐지 중 오류가 발생했습니다.');
            }
        } catch (error) {
            setMessage(error.toString());
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="container mt-5">
            <h1 className="mb-4">AI 기반 웹 로그 이상 탐지 시스템</h1>
            
            <div className="row">
                <div className="col-md-6">
                    <div className="card">
                        <div className="card-body">
                            <h2 className="card-title">1단계: 모델 학습</h2>
                            <p className="card-text text-muted">정상적인 웹 로그 파일을 업로드하여 AI 모델을 학습시킵니다.</p>
                            <form onSubmit={handleTrainSubmit}>
                                <div className="mb-3">
                                    <label htmlFor="trainFile" className="form-label">학습용 로그 파일 (.log, .txt)</label>
                                    <input type="file" className="form-control" id="trainFile" accept=".log,.txt" onChange={(e) => setTrainFile(e.target.files[0])} />
                                </div>
                                <button type="submit" className="btn btn-primary" disabled={isLoading}>
                                    {isLoading ? (
                                        <>
                                            <span className="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                                            <span className="ms-2">학습 중...</span>
                                        </>
                                    ) : '모델 학습 시작'}
                                </button>
                            </form>
                        </div>
                    </div>
                </div>

                <div className="col-md-6">
                    <div className="card">
                        <div className="card-body">
                            <h2 className="card-title">2단계: 이상 탐지</h2>
                            <p className="card-text text-muted">분석하고 싶은 로그 파일을 업로드하여 비정상 접근을 탐지합니다.</p>
                            <form onSubmit={handleDetectSubmit}>
                                <div className="mb-3">
                                    <label htmlFor="detectFile" className="form-label">탐지용 로그 파일 (.log, .txt)</label>
                                    <input type="file" className="form-control" id="detectFile" accept=".log,.txt" onChange={(e) => setDetectFile(e.target.files[0])} />
                                </div>
                                <button type="submit" className="btn btn-success" disabled={isLoading}>
                                    {isLoading ? (
                                        <>
                                            <span className="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                                            <span className="ms-2">탐지 중...</span>
                                        </>
                                    ) : '이상 탐지 시작'}
                                </button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>

            {(message || anomalies.length > 0) && (
                <div className="mt-5">
                    <h2>처리 결과</h2>
                    {message && <div className={`alert ${anomalies.length > 0 ? 'alert-warning' : 'alert-info'} mt-3`}>{message}</div>}
                    
                    {anomalies.length > 0 && (
                        <div className="mt-4">
                            <h4>탐지된 비정상 로그 목록</h4>
                            <table className="table table-striped table-hover">
                                <thead className="table-dark">
                                    <tr>
                                        <th style={{width: '5%'}}>#</th>
                                        <th>비정상 의심 요청</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {anomalies.map((anomaly, index) => (
                                        <tr key={index}>
                                            <td>{index + 1}</td>
                                            <td><code>{anomaly}</code></td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

export default App;