import streamlit as st
import io
import tempfile
import os
from typing import Optional, Dict, Any
import PyPDF2
import docx
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI

# Page configuration
st.set_page_config(
    page_title="ResumeAI - Resume Analysis Tool",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern design
st.markdown("""
<style>
/* Modern CSS Reset and Base Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

/* Custom CSS Variables */
:root {
    --primary-color: #6366f1;
    --primary-hover: #4f46e5;
    --secondary-color: #f8fafc;
    --accent-color: #10b981;
    --text-primary: #1e293b;
    --text-secondary: #64748b;
    --border-color: #e2e8f0;
    --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
    --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
    --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
    --radius: 12px;
    --radius-sm: 8px;
}

/* Global Styles */
.main {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    padding: 0;
}

/* Header Styles */
.header-container {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid var(--border-color);
    padding: 1.5rem 0;
    margin-bottom: 2rem;
    box-shadow: var(--shadow-sm);
}

.header-content {
    text-align: center;
    max-width: 800px;
    margin: 0 auto;
}

.header-title {
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(135deg, var(--primary-color), #8b5cf6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.5rem;
}

.header-subtitle {
    font-size: 1.25rem;
    color: var(--text-secondary);
    font-weight: 500;
}

/* Card Styles */
.card {
    background: white;
    border-radius: var(--radius);
    box-shadow: var(--shadow-md);
    padding: 2rem;
    margin-bottom: 1.5rem;
    border: 1px solid var(--border-color);
    transition: all 0.3s ease;
}

.card:hover {
    box-shadow: var(--shadow-lg);
    transform: translateY(-2px);
}

.card-header {
    display: flex;
    align-items: center;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid var(--secondary-color);
}

.card-icon {
    font-size: 2rem;
    margin-right: 1rem;
    background: linear-gradient(135deg, var(--primary-color), #8b5cf6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.card-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0;
}

/* Button Styles */
.btn-primary {
    background: linear-gradient(135deg, var(--primary-color), #8b5cf6);
    color: white;
    border: none;
    padding: 0.75rem 2rem;
    border-radius: var(--radius-sm);
    font-weight: 600;
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: var(--shadow-sm);
    width: 100%;
    margin-top: 1rem;
}

.btn-primary:hover {
    background: linear-gradient(135deg, var(--primary-hover), #7c3aed);
    transform: translateY(-1px);
    box-shadow: var(--shadow-md);
}

/* Input Styles */
.input-group {
    margin-bottom: 1.5rem;
}

.input-label {
    display: block;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
}

.input-field {
    width: 100%;
    padding: 0.75rem 1rem;
    border: 2px solid var(--border-color);
    border-radius: var(--radius-sm);
    font-size: 1rem;
    transition: all 0.3s ease;
    background: white;
}

.input-field:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

/* Status Indicators */
.status-container {
    display: flex;
    align-items: center;
    margin-bottom: 0.5rem;
}

.status-indicator {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    margin-right: 0.5rem;
}

.status-success {
    background: var(--accent-color);
}

.status-error {
    background: #ef4444;
}

.status-text {
    font-size: 0.9rem;
    font-weight: 500;
}

/* File Upload Area */
.upload-area {
    border: 2px dashed var(--border-color);
    border-radius: var(--radius);
    padding: 2rem;
    text-align: center;
    background: var(--secondary-color);
    transition: all 0.3s ease;
    cursor: pointer;
}

.upload-area:hover {
    border-color: var(--primary-color);
    background: rgba(99, 102, 241, 0.05);
}

.upload-icon {
    font-size: 3rem;
    color: var(--text-secondary);
    margin-bottom: 1rem;
}

/* Results Section */
.results-container {
    background: linear-gradient(135deg, #f8fafc, #f1f5f9);
    border-radius: var(--radius);
    padding: 1.5rem;
    margin-top: 1rem;
}

.suggestion-card {
    background: white;
    border-radius: var(--radius-sm);
    padding: 1.5rem;
    margin-bottom: 1rem;
    border-left: 4px solid var(--primary-color);
    box-shadow: var(--shadow-sm);
}

.suggestion-number {
    display: inline-block;
    background: var(--primary-color);
    color: white;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    text-align: center;
    line-height: 24px;
    font-size: 0.8rem;
    font-weight: 600;
    margin-right: 0.75rem;
}

/* Sidebar Styles */
.sidebar-container {
    background: white;
    border-right: 1px solid var(--border-color);
    padding: 1.5rem;
}

.sidebar-header {
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid var(--secondary-color);
}

.sidebar-section {
    margin-bottom: 2rem;
}

.sidebar-section-title {
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
}

.sidebar-section-icon {
    margin-right: 0.5rem;
    font-size: 1.1rem;
}

/* Loading Animation */
.loading-spinner {
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 3px solid rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    border-top-color: white;
    animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

/* Responsive Design */
@media (max-width: 768px) {
    .header-title {
        font-size: 2rem;
    }
    
    .card {
        padding: 1.5rem;
    }
    
    .upload-area {
        padding: 1.5rem;
    }
}

/* Hide Streamlit default elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Custom scrollbar */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: var(--secondary-color);
}

::-webkit-scrollbar-thumb {
    background: var(--border-color);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--text-secondary);
}
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'azure_doc_endpoint' not in st.session_state:
        st.session_state.azure_doc_endpoint = ""
    if 'azure_doc_key' not in st.session_state:
        st.session_state.azure_doc_key = ""
    if 'azure_openai_endpoint' not in st.session_state:
        st.session_state.azure_openai_endpoint = ""
    if 'azure_openai_key' not in st.session_state:
        st.session_state.azure_openai_key = ""
    if 'azure_openai_deployment' not in st.session_state:
        st.session_state.azure_openai_deployment = ""
    if 'extracted_text' not in st.session_state:
        st.session_state.extracted_text = ""
    if 'feedback_suggestions' not in st.session_state:
        st.session_state.feedback_suggestions = []

def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF using PyPDF2 as fallback"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        return ""

def extract_text_from_docx(file_content: bytes) -> str:
    """Extract text from DOCX file"""
    try:
        doc = docx.Document(io.BytesIO(file_content))
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        st.error(f"Error extracting text from DOCX: {str(e)}")
        return ""

def extract_text_with_document_intelligence(
    file_content: bytes, 
    filename: str,
    endpoint: str, 
    api_key: str
) -> Optional[str]:
    """Extract text using Azure Document Intelligence"""
    try:
        # Create client
        client = DocumentIntelligenceClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(api_key)
        )
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        
        try:
            # Analyze document
            with open(temp_file_path, 'rb') as f:
                poller = client.begin_analyze_document(
                    "prebuilt-read",
                    f,
                    content_type="application/octet-stream"
                )
            
            result = poller.result()
            
            # Extract text
            extracted_text = ""
            if result.content:
                extracted_text = result.content
            
            return extracted_text
        
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    
    except Exception as e:
        st.error(f"Error with Azure Document Intelligence: {str(e)}")
        return None

def get_resume_feedback(
    resume_text: str,
    endpoint: str,
    api_key: str,
    deployment_name: str
) -> Optional[list]:
    """Get resume feedback from Azure OpenAI"""
    try:
        client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version="2024-02-01"
        )
        
        prompt = f"""
        Please analyze the following resume and provide exactly 3 specific, actionable feedback suggestions to improve it. 
        Focus on content, structure, and presentation. Be constructive and specific.
        
        Resume text:
        {resume_text}
        
        Please format your response as a numbered list with exactly 3 suggestions.
        """
        
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": "You are a professional resume reviewer and career advisor."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        feedback_text = response.choices[0].message.content
        
        # Parse the response into individual suggestions
        suggestions = []
        lines = feedback_text.strip().split('\n')
        current_suggestion = ""
        
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('•') or line.startswith('-')):
                if current_suggestion:
                    suggestions.append(current_suggestion.strip())
                current_suggestion = line
            elif line and current_suggestion:
                current_suggestion += " " + line
        
        if current_suggestion:
            suggestions.append(current_suggestion.strip())
        
        return suggestions[:3]  # Ensure we only return 3 suggestions
    
    except Exception as e:
        st.error(f"Error getting feedback from Azure OpenAI: {str(e)}")
        return None

def main():
    initialize_session_state()
    
    # Modern Header
    st.markdown("""
    <div class="header-container">
        <div class="header-content">
            <h1 class="header-title">ResumeAI</h1>
            <p class="header-subtitle">AI-Powered Resume Analysis Tool</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar with modern styling
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-container">
            <div class="sidebar-header">🔑 Azure Configuration</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Azure Document Intelligence
        st.markdown("""
        <div class="sidebar-section">
            <div class="sidebar-section-title">
                <span class="sidebar-section-icon">📄</span>
                Document Intelligence
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.session_state.azure_doc_endpoint = st.text_input(
            "Endpoint",
            value=st.session_state.azure_doc_endpoint,
            placeholder="https://your-resource.cognitiveservices.azure.com/",
            help="Azure Document Intelligence endpoint"
        )
        st.session_state.azure_doc_key = st.text_input(
            "API Key",
            value=st.session_state.azure_doc_key,
            type="password",
            placeholder="Enter your API key"
        )
        
        # Azure OpenAI
        st.markdown("""
        <div class="sidebar-section">
            <div class="sidebar-section-title">
                <span class="sidebar-section-icon">🤖</span>
                Azure OpenAI
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.session_state.azure_openai_endpoint = st.text_input(
            "Endpoint",
            value=st.session_state.azure_openai_endpoint,
            placeholder="https://your-resource.openai.azure.com/",
            help="Azure OpenAI endpoint"
        )
        st.session_state.azure_openai_key = st.text_input(
            "API Key",
            value=st.session_state.azure_openai_key,
            type="password",
            placeholder="Enter your API key"
        )
        st.session_state.azure_openai_deployment = st.text_input(
            "Deployment Name",
            value=st.session_state.azure_openai_deployment,
            placeholder="gpt-35-turbo, gpt-4",
            help="Your deployed model name"
        )
        
        # Configuration status
        st.markdown("---")
        doc_intel_configured = bool(st.session_state.azure_doc_endpoint and st.session_state.azure_doc_key)
        openai_configured = bool(
            st.session_state.azure_openai_endpoint and 
            st.session_state.azure_openai_key and 
            st.session_state.azure_openai_deployment
        )
        
        st.markdown("**Configuration Status:**")
        st.markdown(f"""
        <div class="status-container">
            <div class="status-indicator {'status-success' if doc_intel_configured else 'status-error'}"></div>
            <span class="status-text">Document Intelligence</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="status-container">
            <div class="status-indicator {'status-success' if openai_configured else 'status-error'}"></div>
            <span class="status-text">Azure OpenAI</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Main content area
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("""
        <div class="card">
            <div class="card-header">
                <span class="card-icon">📁</span>
                <h2 class="card-title">Upload Resume</h2>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Choose your resume file",
            type=['pdf', 'docx', 'txt'],
            help="Supported formats: PDF, DOCX, TXT"
        )
        
        if uploaded_file is not None:
            st.markdown(f"""
            <div class="upload-area">
                <div class="upload-icon">✅</div>
                <h3>File Uploaded Successfully</h3>
                <p><strong>{uploaded_file.name}</strong></p>
                <p>Size: {uploaded_file.size} bytes</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Analyze button
            if st.button("🔍 Analyze Resume", type="primary", use_container_width=True):
                if not openai_configured:
                    st.error("❌ Please configure Azure OpenAI credentials in the sidebar first.")
                    return
                
                with st.spinner("Analyzing your resume..."):
                    # Extract text based on file type
                    file_content = uploaded_file.read()
                    file_extension = uploaded_file.name.lower().split('.')[-1]
                    
                    extracted_text = ""
                    
                    if file_extension == 'txt':
                        # Direct text reading for TXT files
                        extracted_text = file_content.decode('utf-8')
                    
                    elif file_extension in ['pdf', 'docx']:
                        # Try Azure Document Intelligence first if configured
                        if doc_intel_configured:
                            extracted_text = extract_text_with_document_intelligence(
                                file_content,
                                uploaded_file.name,
                                st.session_state.azure_doc_endpoint,
                                st.session_state.azure_doc_key
                            )
                        
                        # Fallback to local extraction if Document Intelligence fails or not configured
                        if not extracted_text:
                            if file_extension == 'pdf':
                                extracted_text = extract_text_from_pdf(file_content)
                            elif file_extension == 'docx':
                                extracted_text = extract_text_from_docx(file_content)
                    
                    if extracted_text:
                        st.session_state.extracted_text = extracted_text
                        
                        # Get feedback from Azure OpenAI
                        feedback = get_resume_feedback(
                            extracted_text,
                            st.session_state.azure_openai_endpoint,
                            st.session_state.azure_openai_key,
                            st.session_state.azure_openai_deployment
                        )
                        
                        if feedback:
                            st.session_state.feedback_suggestions = feedback
                            st.success("✅ Resume analysis completed!")
                        else:
                            st.error("❌ Failed to get feedback from Azure OpenAI.")
                    else:
                        st.error("❌ Failed to extract text from the uploaded file.")
    
    with col2:
        st.markdown("""
        <div class="card">
            <div class="card-header">
                <span class="card-icon">📊</span>
                <h2 class="card-title">Analysis Results</h2>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.extracted_text:
            # Display extracted text in expandable section
            with st.expander("📄 Extracted Resume Text", expanded=False):
                st.text_area(
                    "Resume Content",
                    value=st.session_state.extracted_text,
                    height=300,
                    disabled=True
                )
            
            # Display feedback suggestions with modern styling
            if st.session_state.feedback_suggestions:
                st.markdown("""
                <div class="results-container">
                    <h3 style="margin-bottom: 1.5rem; color: var(--text-primary); font-weight: 700;">
                        💡 AI Feedback Suggestions
                    </h3>
                    <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">
                        Here are 3 specific recommendations to improve your resume:
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                for i, suggestion in enumerate(st.session_state.feedback_suggestions, 1):
                    st.markdown(f"""
                    <div class="suggestion-card">
                        <div style="display: flex; align-items: flex-start;">
                            <span class="suggestion-number">{i}</span>
                            <div style="flex: 1;">
                                <p style="margin: 0; line-height: 1.6; color: var(--text-primary);">
                                    {suggestion}
                                </p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="upload-area">
                <div class="upload-icon">👆</div>
                <h3>Ready to Analyze</h3>
                <p>Upload a resume file and click 'Analyze Resume' to see results here.</p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 
