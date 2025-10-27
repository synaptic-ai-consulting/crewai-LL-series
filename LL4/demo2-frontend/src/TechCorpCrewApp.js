import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import './TechCorpCrewApp.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

function TechCorpCrewApp() {
    const [topic, setTopic] = useState('');
    const [kickoffId, setKickoffId] = useState(null);
    const [status, setStatus] = useState('idle');
    const [pendingTask, setPendingTask] = useState(null);
    const [feedback, setFeedback] = useState('');
    const [executionData, setExecutionData] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const [selectedTask, setSelectedTask] = useState(null);

    // Poll for status updates
    useEffect(() => {
        if (!kickoffId) return;

        const pollInterval = setInterval(async () => {
            try {
                const response = await axios.get(`${API_BASE_URL}/status/${kickoffId}`);
                const data = response.data;
                
                setExecutionData(data);
                setStatus(data.local_data?.status || data.status);

                // Check for pending HITL tasks
                if (data.local_data?.pending_tasks?.length > 0) {
                    const latestPending = data.local_data.pending_tasks[
                        data.local_data.pending_tasks.length - 1
                    ];
                    setPendingTask(latestPending);
                    setStatus('pending_human_input');
                }

                // Stop polling if done
                if (data.status === 'completed' || data.status === 'failed') {
                    clearInterval(pollInterval);
                }

            } catch (err) {
                console.error('Status poll error:', err);
            }
        }, 2000); // Poll every 2 seconds

        return () => clearInterval(pollInterval);
    }, [kickoffId]);

    // Handle kickoff
    const handleKickoff = async (e) => {
        e.preventDefault();
        setError(null);
        setLoading(true);
        setStatus('starting');

        try {
            const response = await axios.post(`${API_BASE_URL}/kickoff`, { topic });
            setKickoffId(response.data.kickoff_id);
            setStatus('running');
        } catch (err) {
            setError(err.response?.data?.error || 'Failed to start crew');
            setStatus('error');
        } finally {
            setLoading(false);
        }
    };

    // Handle feedback submission
    const handleFeedbackSubmit = async (approved) => {
        if (!pendingTask) return;
        
        setLoading(true);

        try {
            await axios.post(`${API_BASE_URL}/feedback`, {
                kickoff_id: kickoffId,
                task_id: pendingTask.task_id,
                feedback: feedback || (approved ? 'Approved' : 'Please revise'),
                approved: approved
            });

            setPendingTask(null);
            setFeedback('');
            setStatus('running');
        } catch (err) {
            setError(err.response?.data?.error || 'Failed to submit feedback');
        } finally {
            setLoading(false);
        }
    };

    // Reset for new execution
    const handleReset = () => {
        setKickoffId(null);
        setTopic('');
        setStatus('idle');
        setPendingTask(null);
        setFeedback('');
        setExecutionData(null);
        setError(null);
    };

    return (
        <div className="app-container">
            <header className="app-header">
                <h1>🚀 TechCorp Content Creation Pipeline</h1>
                <p>AI-powered blog post generation with human oversight</p>
            </header>

            {/* Kickoff Form */}
            {!kickoffId && (
                <div className="card kickoff-section">
                    <h2>Generate New Blog Post</h2>
                    <form onSubmit={handleKickoff}>
                        <input
                            type="text"
                            className="topic-input"
                            placeholder="Enter blog post topic (e.g., 'AI Agent Development Best Practices')..."
                            value={topic}
                            onChange={(e) => setTopic(e.target.value)}
                            required
                            disabled={loading}
                        />
                        <button 
                            type="submit" 
                            className="primary-btn"
                            disabled={loading || !topic.trim()}
                        >
                            {loading ? '⏳ Starting...' : '🚀 Generate Blog Post'}
                        </button>
                    </form>
                </div>
            )}

            {/* Error Display */}
            {error && (
                <div className="card error-card">
                    <strong>❌ Error:</strong> {error}
                    <button onClick={() => setError(null)} className="close-btn">×</button>
                </div>
            )}

            {/* Status Display */}
            {kickoffId && (
                <div className="card status-section">
                    <h2>📊 Execution Status</h2>
                    <div className={`status-badge status-${status}`}>
                        {status === 'running' && '⏳ Crew is working...'}
                        {status === 'pending_human_input' && '👤 Waiting for your review'}
                        {status === 'completed' && '✅ Completed Successfully!'}
                        {status === 'failed' && '❌ Execution Failed'}
                    </div>
                    <div className="info-grid">
                        <div className="info-item">
                            <label>Execution ID:</label>
                            <code>{kickoffId.substring(0, 18)}...</code>
                        </div>
                        <div className="info-item">
                            <label>Topic:</label>
                            <span>{executionData?.local_data?.topic}</span>
                        </div>
                        <div className="info-item">
                            <label>Started:</label>
                            <span>{executionData?.local_data?.created_at ? 
                                new Date(executionData.local_data.created_at).toLocaleString() : 
                                'N/A'}
                            </span>
                        </div>
                    </div>
                </div>
            )}

            {/* Human Input Section */}
            {pendingTask && (
                <div className="card review-section">
                    <h2>📋 Review Required</h2>
                    <div className="task-header">
                        <span className="task-id">{pendingTask.task_id}</span>
                        <span className="task-timestamp">
                            {new Date(pendingTask.received_at).toLocaleTimeString()}
                        </span>
                    </div>
                    
                    <div className="task-output">
                        <h3>Task Output:</h3>
                        <div className="markdown-content">
                            <ReactMarkdown>{pendingTask.task_output}</ReactMarkdown>
                        </div>
                    </div>

                    <div className="feedback-form">
                        <h3>Provide Your Feedback:</h3>
                        <textarea
                            placeholder="Optional: Provide specific feedback or request changes..."
                            value={feedback}
                            onChange={(e) => setFeedback(e.target.value)}
                            rows="4"
                            disabled={loading}
                        />
                        
                        <div className="button-group">
                            <button 
                                className="approve-btn"
                                onClick={() => handleFeedbackSubmit(true)}
                                disabled={loading}
                            >
                                ✅ Approve & Continue
                            </button>
                            <button 
                                className="reject-btn"
                                onClick={() => handleFeedbackSubmit(false)}
                                disabled={loading}
                            >
                                🔄 Request Revisions
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Completed Tasks */}
            {executionData?.local_data?.completed_tasks?.length > 0 && (
                <div className="card completed-section">
                    <h2>✅ Completed Tasks ({executionData.local_data.completed_tasks.length})</h2>
                    <div className="tasks-list">
                        {executionData.local_data.completed_tasks.map((task, index) => (
                            <div 
                                key={index} 
                                className="completed-task clickable"
                                onClick={() => setSelectedTask(task)}
                            >
                                <div className="task-name">{task.task_name || task.task_id}</div>
                                <div className="task-time">
                                    {new Date(task.completed_at).toLocaleString()}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Final Output */}
            {executionData?.final_output && status === 'completed' && (
                <div className="card final-output">
                    <h2>🎉 Final Blog Post Ready!</h2>
                    <div className="output-content markdown-content">
                        <ReactMarkdown>{executionData.final_output}</ReactMarkdown>
                    </div>
                    <div className="button-group">
                        <button 
                            onClick={() => {
                                navigator.clipboard.writeText(executionData.final_output);
                                alert('Blog post copied to clipboard!');
                            }}
                            className="secondary-btn"
                        >
                            📋 Copy to Clipboard
                        </button>
                        <button onClick={handleReset} className="primary-btn">
                            ➕ Create Another Post
                        </button>
                    </div>
                </div>
            )}

            {/* Task Detail Modal */}
            {selectedTask && (
                <div className="modal-overlay" onClick={() => setSelectedTask(null)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2>📄 {selectedTask.task_name || selectedTask.task_id}</h2>
                            <button className="close-btn" onClick={() => setSelectedTask(null)}>×</button>
                        </div>
                        <div className="modal-body markdown-content">
                            <ReactMarkdown>{selectedTask.task_output}</ReactMarkdown>
                        </div>
                        <div className="modal-footer">
                            <button 
                                onClick={() => {
                                    navigator.clipboard.writeText(selectedTask.task_output);
                                    alert('Content copied to clipboard!');
                                }}
                                className="secondary-btn"
                            >
                                📋 Copy Content
                            </button>
                            <button onClick={() => setSelectedTask(null)} className="primary-btn">
                                Close
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default TechCorpCrewApp;
