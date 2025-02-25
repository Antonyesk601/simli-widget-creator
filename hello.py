from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from typing import List, Optional
import httpx
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Simli Face Selection API")

# Get API keys from environment variables
SIMLI_API_KEY = os.getenv("SIMLI_API_KEY")
TTS_API_KEY = os.getenv("TTS_API_KEY")

if not SIMLI_API_KEY:
    print("Warning: SIMLI_API_KEY not found in environment variables. Using default value for testing.")
    SIMLI_API_KEY = "YOUR_API_KEY_HERE"  # Replace with your actual API key for testing

if not TTS_API_KEY:
    print("Warning: TTS_API_KEY not found in environment variables. Using default value for testing.")
    TTS_API_KEY = "YOUR_TTS_API_KEY_HERE"  # Replace with your actual TTS API key for testing

# Model for our face options
class FaceOption(BaseModel):
    id: str
    name: str
    previewImage: str
    previewVideo: Optional[str] = None
    createdAt: Optional[int] = None

# Pydantic models for agent creation
class AgentCreate(BaseModel):
    face_id: str
    name: str
    first_message: Optional[str] = "The first message you want the agent to say"
    prompt: Optional[str] = "The persona of the agent and the context of the conversation"
    voice_provider: Optional[str] = None
    voice_id: Optional[str] = None
    voice_model: Optional[str] = None
    language: Optional[str] = None
    llm_endpoint: Optional[str] = None
    max_idle_time: Optional[int] = 300
    max_session_length: Optional[int] = 3600

class AgentResponse(BaseModel):
    id: str
    face_id: str
    name: str

# Session token request model
class SessionTokenRequest(BaseModel):
    simliAPIKey: str
    ttsAPIKey: str

# Session token response model
class SessionTokenResponse(BaseModel):
    session_token: str

# API routes
@app.get("/api/faces", response_model=List[FaceOption])
async def get_faces():
    """
    Fetch face IDs from the Simli API
    """
    async with httpx.AsyncClient() as client:
        headers = {"api-key": SIMLI_API_KEY}
        response = await client.get("https://api.simli.ai/getFaceIDs?getPublic=false", headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, 
                                detail=f"Error fetching faces from Simli API: {response.text}")
        
        return response.json()

@app.post("/api/agent", response_model=AgentResponse, status_code=201)
async def create_agent(agent: AgentCreate):
    """
    Create a new agent with the Simli API
    """
    # In a real implementation, you would forward this to the Simli API
    # For now, we'll simulate a successful response
    
    # Validate that the face_id exists
    # You might want to check this against the faces from the Simli API
    
    # Return a mock response
    return AgentResponse(
        id=f"agent-{agent.face_id[:8]}",
        face_id=agent.face_id,
        name=agent.name
    )

@app.post("/api/createE2ESessionToken", response_model=SessionTokenResponse)
async def create_e2e_session_token(request: SessionTokenRequest):
    """
    Create a new end-to-end session token
    """
    # In a real implementation, you would forward this to the endpoint
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.simli.ai/createE2ESessionToken",
            json={
                "simliAPIKey": request.simliAPIKey,
                "ttsAPIKey": request.ttsAPIKey
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code, 
                detail=f"Error creating session token: {response.text}"
            )
        
        return response.json()

# Serve HTML for frontend
@app.get("/", response_class=HTMLResponse)
async def get_html():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Simli Face Selection</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f9f9f9;
            }
            h1 {
                color: #333;
                text-align: center;
                margin-bottom: 30px;
            }
            .container {
                display: flex;
                flex-direction: column;
                gap: 20px;
            }
            .two-column {
                display: flex;
                gap: 20px;
            }
            .left-column {
                flex: 1;
            }
            .right-column {
                flex: 1;
            }
            .selection-container, .form-container, .session-container {
                background-color: white;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            
            .form-group {
                margin-bottom: 15px;
            }
            
            label {
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
            }
            
            input, select, textarea {
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
            }
            
            textarea {
                min-height: 80px;
                resize: vertical;
            }
            
            .required-field::after {
                content: " *";
                color: #c62828;
            }
            
            .submit-button {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 16px;
                margin-top: 15px;
            }
            
            .success-container {
                background-color: #e8f5e9;
                border-left: 4px solid #4CAF50;
                padding: 15px;
                margin-top: 20px;
                border-radius: 4px;
            }
            
            .agent-details, .token-details {
                margin-top: 10px;
                background-color: #f5f5f5;
                padding: 15px;
                border-radius: 4px;
                font-family: monospace;
            }
            
            .agent-id, .token-value {
                font-weight: bold;
                color: #2e7d32;
                word-break: break-all;
            }
            
            .copy-button {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 12px;
                margin-left: 10px;
            }
            
            .copy-button:hover {
                background-color: #0b7dda;
            }
            select {
                width: 100%;
                padding: 12px;
                margin-bottom: 20px;
                border-radius: 4px;
                border: 1px solid #ddd;
                font-size: 16px;
            }
            .faces-grid {
                display: flex;
                justify-content: center;
                margin-top: 20px;
                flex-wrap: wrap;
                gap: 20px;
            }
            .face-card {
                width: 300px;
                border: 1px solid #eee;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                transition: transform 0.2s, box-shadow 0.2s;
                cursor: pointer;
            }
            .face-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            .face-card.selected {
                border: 3px solid #4CAF50;
            }
            .face-image {
                width: 100%;
                height: 200px;
                object-fit: cover;
            }
            .face-info {
                padding: 15px;
            }
            .face-name {
                font-weight: bold;
                font-size: 18px;
                margin-bottom: 5px;
            }
            .face-id {
                color: #777;
                font-size: 12px;
                word-break: break-all;
            }
            .loading {
                text-align: center;
                padding: 40px;
                font-size: 18px;
                color: #666;
            }
            .error {
                background-color: #ffebee;
                color: #c62828;
                padding: 15px;
                border-radius: 4px;
                margin-bottom: 20px;
                text-align: center;
            }
            .video-container {
                margin-top: 30px;
                background-color: white;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            video {
                max-width: 100%;
                border-radius: 4px;
            }
        </style>
    </head>
    <body>
        <h1>Simli Face Selection</h1>
        
        <div class="container">
            <div id="error" class="error" style="display: none;"></div>
            
            <div class="two-column">
                <div class="left-column">
                    <div class="form-container">
                        <h2>Create Agent</h2>
                        <form id="agentForm">
                            <input type="hidden" id="face_id" name="face_id" value="">
                            
                            <div class="form-group">
                                <label for="name" class="required-field">Name</label>
                                <input type="text" id="name" name="name" value="Untitled Agent" required>
                            </div>
                            
                            <div class="form-group">
                                <label for="first_message">First Message</label>
                                <textarea id="first_message" name="first_message">The first message you want the agent to say</textarea>
                            </div>
                            
                            <div class="form-group">
                                <label for="prompt">Prompt</label>
                                <textarea id="prompt" name="prompt">The persona of the agent and the context of the conversation</textarea>
                            </div>
                            
                            <div class="form-group">
                                <label for="voice_provider">Voice Provider</label>
                                <select id="voice_provider" name="voice_provider">
                                    <option value="elevenlabs">Elevenlabs</option>
                                    <option value="cartesia">Cartesia</option>
                                </select>
                            </div>
                            
                            <div class="form-group">
                                <label for="voice_id">Voice ID</label>
                                <input type="text" id="voice_id" name="voice_id">
                            </div>
                            
                            <div class="form-group">
                                <label for="voice_model">Voice Model</label>
                                <input type="text" id="voice_model" name="voice_model" placeholder="e.g., sonic-english">
                            </div>
                            
                            <div class="form-group">
                                <label for="language">Language</label>
                                <input type="text" id="language" name="language">
                            </div>
                            
                            <div class="form-group">
                                <label for="llm_endpoint">LLM Endpoint</label>
                                <input type="text" id="llm_endpoint" name="llm_endpoint">
                            </div>
                            
                            <div class="form-group">
                                <label for="max_idle_time">Max Idle Time (seconds)</label>
                                <input type="number" id="max_idle_time" name="max_idle_time" value="300">
                            </div>
                            
                            <div class="form-group">
                                <label for="max_session_length">Max Session Length (seconds)</label>
                                <input type="number" id="max_session_length" name="max_session_length" value="3600">
                            </div>
                            
                            <button type="submit" class="submit-button">Create Agent</button>
                        </form>
                        
                        <div id="successContainer" class="success-container" style="display: none;">
                            <h3>Agent Created Successfully!</h3>
                            <p>Your agent has been created with the following details:</p>
                            <div id="agentDetails" class="agent-details">
                                <div>Name: <span id="createdAgentName"></span></div>
                                <div>Face ID: <span id="createdAgentFaceId"></span></div>
                                <div>Agent ID: <span id="createdAgentId" class="agent-id"></span> 
                                    <button onclick="copyAgentId()" class="copy-button">Copy ID</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="right-column">
                    <div class="selection-container">
                        <h2>Select a Face</h2>
                        <select id="faceSelect" onchange="updateSelectedFace()">
                            <option value="">Select a face...</option>
                        </select>
                        
                        <div id="loading" class="loading">Loading faces...</div>
                        <div id="facesGrid" class="faces-grid"></div>
                    </div>
                </div>
            </div>
            
            <div id="videoPreview" class="video-container" style="display: none;">
                <h2>Video Preview</h2>
                <video id="videoPlayer" controls autoplay loop muted></video>
            </div>
            
            <!-- New session token section -->
            <div class="session-container">
                <h2>Create E2E Session Token</h2>
                <form id="sessionTokenForm">
                    <div class="form-group">
                        <label for="simliAPIKey">Simli API Key</label>
                        <input type="text" id="simliAPIKey" name="simliAPIKey" value="SIMLI_API_KEY">
                    </div>
                    
                    <div class="form-group">
                        <label for="ttsAPIKey">TTS API Key</label>
                        <input type="text" id="ttsAPIKey" name="ttsAPIKey" value="TTS_API_KEY">
                    </div>
                    
                    <button type="submit" class="submit-button">Create Session Token</button>
                </form>
                
                <div id="tokenSuccessContainer" class="success-container" style="display: none;">
                    <h3>Session Token Created Successfully!</h3>
                    <div id="tokenDetails" class="token-details">
                        <div>Token: <span id="createdToken" class="token-value"></span> 
                            <button onclick="copyToken()" class="copy-button">Copy Token</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            // Global variables
            let faces = [];
            let selectedFaceId = '';
            
            // API endpoint for agent creation
            const CREATE_AGENT_ENDPOINT = "https://api.simli.ai/agent";
            
            // DOM Elements
            const faceSelect = document.getElementById('faceSelect');
            const facesGrid = document.getElementById('facesGrid');
            const loadingElement = document.getElementById('loading');
            const errorElement = document.getElementById('error');
            const videoPreview = document.getElementById('videoPreview');
            const videoPlayer = document.getElementById('videoPlayer');
            const agentForm = document.getElementById('agentForm');
            const faceIdInput = document.getElementById('face_id');
            const successContainer = document.getElementById('successContainer');
            const createdAgentName = document.getElementById('createdAgentName');
            const createdAgentFaceId = document.getElementById('createdAgentFaceId');
            const createdAgentId = document.getElementById('createdAgentId');
            
            // Session token elements
            const sessionTokenForm = document.getElementById('sessionTokenForm');
            const tokenSuccessContainer = document.getElementById('tokenSuccessContainer');
            const createdToken = document.getElementById('createdToken');
            
            // Load faces on page load
            document.addEventListener('DOMContentLoaded', loadFaces);
            
            // Add form submission handlers
            agentForm.addEventListener('submit', submitAgentForm);
            sessionTokenForm.addEventListener('submit', submitSessionTokenForm);
            
            // Functions to interact with the API
            async function loadFaces() {
                try {
                    showLoading(true);
                    const response = await fetch('/api/faces');
                    
                    if (!response.ok) {
                        throw new Error(`API error: ${response.status} ${response.statusText}`);
                    }
                    
                    faces = await response.json();
                    
                    if (!faces || faces.length === 0) {
                        showError('No faces available. Please check your API key and try again.');
                        return;
                    }
                    
                    // Populate dropdown and face cards
                    populateFaceOptions(faces);
                    createFaceCards(faces);
                    
                    showLoading(false);
                } catch (error) {
                    console.error('Error loading faces:', error);
                    showError(`Failed to load faces: ${error.message}`);
                    showLoading(false);
                }
            }
            
            function populateFaceOptions(faces) {
                // Clear existing options
                faceSelect.innerHTML = '<option value="">Select a face...</option>';
                
                // Add new options
                faces.forEach(face => {
                    const option = document.createElement('option');
                    option.value = face.id;
                    option.textContent = face.name;
                    faceSelect.appendChild(option);
                });
            }
            
            function createFaceCards(faces) {
                facesGrid.innerHTML = '';
                
                faces.forEach(face => {
                    const card = document.createElement('div');
                    card.className = 'face-card';
                    card.dataset.id = face.id;
                    card.onclick = () => selectFace(face.id);
                    
                    card.innerHTML = `
                        <img src="${face.previewImage}" alt="${face.name}" class="face-image" onerror="this.src='https://via.placeholder.com/300x200?text=Image+Not+Available'">
                        <div class="face-info">
                            <div class="face-name">${face.name}</div>
                            <div class="face-id">${face.id}</div>
                        </div>
                    `;
                    
                    facesGrid.appendChild(card);
                });
            }
            
            function selectFace(faceId) {
                selectedFaceId = faceId;
                
                // Update dropdown
                faceSelect.value = faceId;
                
                // Update hidden form field
                faceIdInput.value = faceId;
                
                // Update card selection
                document.querySelectorAll('.face-card').forEach(card => {
                    if (card.dataset.id === faceId) {
                        card.classList.add('selected');
                    } else {
                        card.classList.remove('selected');
                    }
                });
                
                // Find the selected face
                const selectedFace = faces.find(face => face.id === faceId);
                
                // Update video preview
                if (selectedFace && selectedFace.previewVideo) {
                    videoPlayer.src = selectedFace.previewVideo;
                    videoPreview.style.display = 'block';
                    
                    // Automatically scroll to video preview
                    setTimeout(() => {
                        videoPreview.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }, 100);
                } else {
                    videoPreview.style.display = 'none';
                }
            }
            
            function updateSelectedFace() {
                const faceId = faceSelect.value;
                if (faceId) {
                    selectFace(faceId);
                }
            }
            
            function showLoading(isLoading) {
                loadingElement.style.display = isLoading ? 'block' : 'none';
            }
            
            function showError(message) {
                errorElement.textContent = message;
                errorElement.style.display = message ? 'block' : 'none';
            }
            
            async function submitAgentForm(e) {
                e.preventDefault();
                
                // Hide success message if shown previously
                successContainer.style.display = 'none';
                
                // Validate that a face is selected
                if (!selectedFaceId) {
                    showError('Please select a face before creating an agent');
                    return;
                }
                
                // Get form data
                const formData = new FormData(agentForm);
                const agentData = {};
                
                // Convert FormData to JSON object
                for (const [key, value] of formData.entries()) {
                    // Convert numeric values to numbers
                    if (key === 'max_idle_time' || key === 'max_session_length') {
                        agentData[key] = parseInt(value);
                    } else {
                        agentData[key] = value;
                    }
                }
                
                try {
                    const response = await fetch(CREATE_AGENT_ENDPOINT, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'x-simli-api-key': 'SIMLI_API_KEY' // Assuming you need the same API key
                        },
                        body: JSON.stringify(agentData)
                    });
                    
                    if (!response.ok) {
                        const errorData = await response.json();
                        throw new Error(errorData.detail || 'Failed to create agent');
                    }
                    
                    const createdAgent = await response.json();
                    
                    // Display success message with agent details
                    createdAgentName.textContent = createdAgent.name;
                    createdAgentFaceId.textContent = createdAgent.face_id;
                    createdAgentId.textContent = createdAgent.id;
                    successContainer.style.display = 'block';
                    
                    // Scroll to success message
                    successContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    
                } catch (error) {
                    console.error('Error creating agent:', error);
                    showError(`Failed to create agent: ${error.message}`);
                }
            }
            
            async function submitSessionTokenForm(e) {
                e.preventDefault();
                
                // Hide token success message if shown previously
                tokenSuccessContainer.style.display = 'none';
                
                // Get form data
                const formData = new FormData(sessionTokenForm);
                const tokenData = {};
                
                // Convert FormData to JSON object
                for (const [key, value] of formData.entries()) {
                    tokenData[key] = value;
                }
                
                try {
                    const response = await fetch('/api/createE2ESessionToken', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(tokenData)
                    });
                    
                    if (!response.ok) {
                        const errorData = await response.json();
                        throw new Error(errorData.detail || 'Failed to create session token');
                    }
                    
                    const result = await response.json();
                    console.log(result);
                    // Display success message with token
                    createdToken.textContent = result.session_token;
                    tokenSuccessContainer.style.display = 'block';
                    
                    // Scroll to token success message
                    tokenSuccessContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    
                } catch (error) {
                    console.error('Error creating session token:', error);
                    showError(`Failed to create session token: ${error.message}`);
                }
            }
            
            function copyAgentId() {
                const agentId = createdAgentId.textContent;
                navigator.clipboard.writeText(agentId)
                    .then(() => {
                        alert('Agent ID copied to clipboard!');
                    })
                    .catch(err => {
                        console.error('Could not copy text: ', err);
                    });
            }
            
            function copyToken() {
                const token = createdToken.textContent;
                navigator.clipboard.writeText(token)
                    .then(() => {
                        alert('Session token copied to clipboard!');
                    })
                    .catch(err => {
                        console.error('Could not copy text: ', err);
                    });
            }
        </script>
    </body>
    </html>
    """.replace("SIMLI_API_KEY", SIMLI_API_KEY).replace("TTS_API_KEY", TTS_API_KEY)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)