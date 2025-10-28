const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const axios = require('axios');
const path = require('path');

// Load .env from LL4 root directory (parent directory)
require('dotenv').config({ path: path.join(__dirname, '..', '.env') });

const app = express();
const PORT = process.env.WEBHOOK_PORT || 3001;

// Map env variables to what server.js expects
const CREW_BASE_URL = process.env.CREW_BASE_URL;
const CREW_BEARER_TOKEN = process.env.CREW_BEARER_TOKEN;
const WEBHOOK_BASE_URL = process.env.WEBHOOK_BASE_URL || 'http://localhost:3001';

// Debug: Log loaded environment variables
console.log('🔍 Environment Variables Loaded:');
console.log(`   CREW_BASE_URL: ${process.env.CREW_BASE_URL ? '✅' : '❌ undefined'}`);
console.log(`   CREW_BEARER_TOKEN: ${process.env.CREW_BEARER_TOKEN ? '✅' : '❌ undefined'}`);
console.log(`   WEBHOOK_BASE_URL: ${process.env.WEBHOOK_BASE_URL || 'using default'}`);

// Middleware
app.use(cors());
app.use(bodyParser.json());

// In-memory storage for executions (use database in production)
const executions = new Map();

console.log('🚀 TechCorp Content Crew Backend Starting...');
console.log(`📡 Webhook Base URL: ${WEBHOOK_BASE_URL}`);
console.log(`🤖 Crew URL: ${CREW_BASE_URL}\n`);

// ==================== GET CREW INPUTS ====================
app.get('/api/inputs', async (req, res) => {
    try {
        const inputsResponse = await axios.get(
            `${CREW_BASE_URL}/inputs`,
            {
                headers: {
                    'Authorization': `Bearer ${CREW_BEARER_TOKEN}`
                }
            }
        );

        res.json(inputsResponse.data);
    } catch (error) {
        console.error('❌ Get inputs error:', error.response?.data || error.message);
        res.status(500).json({ 
            error: 'Failed to get crew inputs',
            details: error.response?.data || error.message
        });
    }
});

// ==================== KICKOFF ENDPOINT ====================
app.post('/api/kickoff', async (req, res) => {
    try {
        const { topic } = req.body;
        
        if (!topic) {
            return res.status(400).json({ error: 'Topic is required' });
        }

        console.log(`\n🚀 KICKOFF REQUESTED`);
        console.log(`   Topic: "${topic}"`);

        const kickoffResponse = await axios.post(
            `${CREW_BASE_URL}/kickoff`,
            {
                inputs: { 
                    topic,
                    "approved: boolean, feedback: string, selected_angle: string, additional_requirements: string": "",
                    "final_approved: boolean, revision_notes: string, publish_immediately: boolean, scheduled_date: string": ""
                },
                // CRITICAL: Webhook URLs for HITL
                taskWebhookUrl: `${WEBHOOK_BASE_URL}/api/webhooks/task`,
                stepWebhookUrl: `${WEBHOOK_BASE_URL}/api/webhooks/step`,
                crewWebhookUrl: `${WEBHOOK_BASE_URL}/api/webhooks/crew`
            },
            {
                headers: {
                    'Authorization': `Bearer ${CREW_BEARER_TOKEN}`,
                    'Content-Type': 'application/json'
                }
            }
        );

        const { kickoff_id } = kickoffResponse.data;
        
        // Store execution
        executions.set(kickoff_id, {
            kickoff_id,
            topic,
            status: 'running',
            pending_tasks: [],
            completed_tasks: [],
            created_at: new Date().toISOString()
        });

        console.log(`   ✅ Kickoff successful!`);
        console.log(`   Execution ID: ${kickoff_id}\n`);

        res.json({ 
            success: true,
            kickoff_id,
            message: 'Crew execution started',
            status: 'running'
        });

    } catch (error) {
        console.error('❌ Kickoff error:', error.response?.data || error.message);
        res.status(500).json({ 
            error: 'Failed to kickoff crew',
            details: error.response?.data || error.message
        });
    }
});

// ==================== TASK WEBHOOK ====================
app.post('/api/webhooks/task', (req, res) => {
    try {
        const { kickoff_id, name, description, output, expected_output } = req.body;
        
        console.log(`\n📋 TASK WEBHOOK RECEIVED`);
        console.log(`   Execution ID: ${kickoff_id}`);
        console.log(`   Task name: ${name}`);
        
        const execution = executions.get(kickoff_id);
        
        if (!execution) {
            console.warn(`   ⚠️ Unknown execution ID: ${kickoff_id}`);
            return res.status(200).json({ received: true });
        }

        // Check if this task requires human input based on expected output
        const requiresHumanInput = expected_output && 
            (expected_output.includes('PAUSES FOR HUMAN') || 
             expected_output.includes('PAUSES FOR FINAL') ||
             expected_output.includes('HUMAN REVIEW REQUIRED'));

        if (requiresHumanInput) {
            console.log(`   👤 HUMAN INPUT REQUIRED for task: ${name}`);
            console.log(`   Output preview: ${output?.substring(0, 200)}...\n`);
            
            execution.status = 'pending_human_input';
            execution.pending_tasks.push({
                task_id: name,  // Use task name as ID
                task_name: name,
                task_description: description,
                task_output: output,
                expected_output: expected_output,
                received_at: new Date().toISOString()
            });
            
            executions.set(kickoff_id, execution);
            
        } else {
            console.log(`   ✅ Task completed: ${name}`);
            
            execution.completed_tasks.push({
                task_id: name,
                task_name: name,
                task_output: output,
                completed_at: new Date().toISOString()
            });
        }

        res.status(200).json({ received: true });

    } catch (error) {
        console.error('❌ Task webhook error:', error);
        res.status(500).json({ error: 'Webhook processing failed' });
    }
});

// ==================== STEP WEBHOOK ====================
app.post('/api/webhooks/step', (req, res) => {
    try {
        const { kickoff_id, thought, tool, result } = req.body;
        
        // Optional: Log agent reasoning for debugging
        // console.log(`\n🤔 STEP: ${thought?.substring(0, 100)}...`);
        
        res.status(200).json({ received: true });

    } catch (error) {
        console.error('❌ Step webhook error:', error);
        res.status(500).json({ error: 'Webhook processing failed' });
    }
});

// ==================== CREW WEBHOOK ====================
app.post('/api/webhooks/crew', (req, res) => {
    try {
        const { kickoff_id, result } = req.body;
        
        console.log(`\n🎉 CREW COMPLETED!`);
        console.log(`   Execution ID: ${kickoff_id}`);
        console.log(`   Final output preview: ${result?.substring(0, 300)}...\n`);

        const execution = executions.get(kickoff_id);
        
        if (execution) {
            execution.status = 'completed';
            execution.final_output = result;
            execution.completed_at = new Date().toISOString();
            executions.set(kickoff_id, execution);
        }

        res.status(200).json({ received: true });

    } catch (error) {
        console.error('❌ Crew webhook error:', error);
        res.status(500).json({ error: 'Webhook processing failed' });
    }
});

// ==================== GET STATUS ====================
app.get('/api/status/:kickoff_id', async (req, res) => {
    try {
        const { kickoff_id } = req.params;
        
        // Get from AMP
        const statusResponse = await axios.get(
            `${CREW_BASE_URL}/status/${kickoff_id}`,
            {
                headers: {
                    'Authorization': `Bearer ${CREW_BEARER_TOKEN}`
                }
            }
        );

        // Merge with local data
        const localExecution = executions.get(kickoff_id);
        
        res.json({
            ...statusResponse.data,
            local_data: localExecution
        });

    } catch (error) {
        console.error('❌ Status error:', error.response?.data || error.message);
        res.status(500).json({ 
            error: 'Failed to get status',
            details: error.response?.data || error.message
        });
    }
});

// ==================== GET PENDING TASKS ====================
app.get('/api/pending-tasks/:kickoff_id', (req, res) => {
    try {
        const { kickoff_id } = req.params;
        const execution = executions.get(kickoff_id);
        
        if (!execution) {
            return res.status(404).json({ error: 'Execution not found' });
        }
        
        res.json({
            kickoff_id,
            status: execution.status,
            pending_tasks: execution.pending_tasks,
            completed_tasks: execution.completed_tasks
        });
    } catch (error) {
        console.error('❌ Get pending tasks error:', error);
        res.status(500).json({ error: 'Failed to get pending tasks' });
    }
});

// ==================== SUBMIT FEEDBACK ====================
app.post('/api/feedback', async (req, res) => {
    try {
        const { kickoff_id, task_id, feedback, approved } = req.body;
        
        console.log(`\n💬 HUMAN FEEDBACK RECEIVED`);
        console.log(`   Execution ID: ${kickoff_id}`);
        console.log(`   Task: ${task_id}`);
        console.log(`   Approved: ${approved ? '✅ YES' : '🔄 REVISE'}`);
        console.log(`   Feedback: "${feedback}"\n`);

        // Construct feedback message
        const feedbackMessage = approved 
            ? (feedback || 'Approved and continue')
            : (feedback || 'Request revisions');
        
        // Get the pending task to retrieve its output
        const execData = executions.get(kickoff_id);
        const pendingTask = execData?.pending_tasks?.find(t => t.task_id === task_id);
        
        // Prepare resume payload (according to https://docs.crewai.com/en/enterprise/guides/human-in-the-loop)
        // NOTE: AMP API uses camelCase field names (executionId, taskId)
        const resumePayload = {
            executionId: kickoff_id,  // camelCase, not snake_case
            taskId: task_id,           // camelCase, not snake_case
            human_feedback: feedbackMessage,
            is_approve: approved
        };
        
        // When requesting a revision (is_approve=false), AMP requires output and inputs
        if (!approved && pendingTask) {
            resumePayload.output = pendingTask.task_output;
            resumePayload.inputs = { topic: execData.topic };
        }
        
        // CRITICAL: Must re-provide webhooks
        resumePayload.taskWebhookUrl = `${WEBHOOK_BASE_URL}/api/webhooks/task`;
        resumePayload.stepWebhookUrl = `${WEBHOOK_BASE_URL}/api/webhooks/step`;
        resumePayload.crewWebhookUrl = `${WEBHOOK_BASE_URL}/api/webhooks/crew`;
        
        console.log('📤 Resume payload:', JSON.stringify(resumePayload, null, 2));
        
        // Resume crew with feedback
        const resumeResponse = await axios.post(
            `${CREW_BASE_URL}/resume`,
            resumePayload,
            {
                headers: {
                    'Authorization': `Bearer ${CREW_BEARER_TOKEN}`,
                    'Content-Type': 'application/json'
                }
            }
        );

        // Update execution status
        const execution = executions.get(kickoff_id);
        if (execution) {
            execution.status = 'running';
            execution.pending_tasks = execution.pending_tasks.filter(
                t => t.task_id !== task_id
            );
            executions.set(kickoff_id, execution);
        }

        console.log(`   ✅ Crew resumed successfully\n`);

        res.json({ 
            success: true,
            message: 'Feedback submitted and crew resumed',
            execution_id: kickoff_id
        });

    } catch (error) {
        console.error('❌ Feedback error:', error.response?.data || error.message);
        
        // Debug: Show the detailed error
        if (error.response?.data?.detail) {
            console.error('   Missing fields:', error.response.data.detail);
        }
        
        res.status(500).json({ 
            error: 'Failed to submit feedback',
            details: error.response?.data || error.message
        });
    }
});

// ==================== HEALTH CHECK ====================
app.get('/health', (req, res) => {
    res.json({ 
        status: 'healthy',
        timestamp: new Date().toISOString(),
        crew_url: CREW_BASE_URL,
        webhook_url: WEBHOOK_BASE_URL
    });
});

// Start server
app.listen(PORT, () => {
    console.log(`\n${'='.repeat(60)}`);
    console.log(`🚀 TechCorp Content Crew Backend`);
    console.log(`${'='.repeat(60)}`);
    console.log(`📡 Server running on: http://localhost:${PORT}`);
    console.log(`🌐 Webhook endpoint: ${WEBHOOK_BASE_URL}`);
    console.log(`🤖 Crew API: ${CREW_BASE_URL}`);
    console.log(`${'='.repeat(60)}\n`);
});
