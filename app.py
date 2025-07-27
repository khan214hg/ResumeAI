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
    
    # Header
    st.title("📄 ResumeAI")
    st.markdown("**AI-Powered Resume Analysis Tool**")
    st.markdown("Upload your resume and get intelligent feedback to improve it!")
    
    # Sidebar for Azure credentials
    with st.sidebar:
        st.header("🔑 Azure Configuration")
        st.markdown("Configure your Azure services credentials:")
        
        # Azure Document Intelligence
        st.subheader("Document Intelligence")
        st.session_state.azure_doc_endpoint = st.text_input(
            "Azure Document Intelligence Endpoint",
            value=st.session_state.azure_doc_endpoint,
            type="default",
            help="e.g., https://your-resource.cognitiveservices.azure.com/"
        )
        st.session_state.azure_doc_key = st.text_input(
            "Azure Document Intelligence API Key",
            value=st.session_state.azure_doc_key,
            type="password"
        )
        
        # Azure OpenAI
        st.subheader("Azure OpenAI")
        st.session_state.azure_openai_endpoint = st.text_input(
            "Azure OpenAI Endpoint",
            value=st.session_state.azure_openai_endpoint,
            type="default",
            help="e.g., https://your-resource.openai.azure.com/"
        )
        st.session_state.azure_openai_key = st.text_input(
            "Azure OpenAI API Key",
            value=st.session_state.azure_openai_key,
            type="password"
        )
        st.session_state.azure_openai_deployment = st.text_input(
            "Azure OpenAI Deployment Name",
            value=st.session_state.azure_openai_deployment,
            type="default",
            help="e.g., gpt-35-turbo, gpt-4"
        )
        
        # Validation status
        st.markdown("---")
        doc_intel_configured = bool(st.session_state.azure_doc_endpoint and st.session_state.azure_doc_key)
        openai_configured = bool(
            st.session_state.azure_openai_endpoint and 
            st.session_state.azure_openai_key and 
            st.session_state.azure_openai_deployment
        )
        
        st.markdown("**Configuration Status:**")
        st.markdown(f"Document Intelligence: {'✅' if doc_intel_configured else '❌'}")
        st.markdown(f"Azure OpenAI: {'✅' if openai_configured else '❌'}")
    
    # Main content area
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.header("📁 Upload Resume")
        uploaded_file = st.file_uploader(
            "Choose your resume file",
            type=['pdf', 'docx', 'txt'],
            help="Supported formats: PDF, DOCX, TXT"
        )
        
        if uploaded_file is not None:
            st.success(f"File uploaded: {uploaded_file.name}")
            st.info(f"File size: {uploaded_file.size} bytes")
            
            # Analyze button
            analyze_button = st.button(
                "🔍 Analyze Resume",
                type="primary",
                use_container_width=True
            )
            
            if analyze_button:
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
        st.header("📊 Analysis Results")
        
        if st.session_state.extracted_text:
            # Display extracted text in expandable section
            with st.expander("📄 Extracted Resume Text", expanded=False):
                st.text_area(
                    "Resume Content",
                    value=st.session_state.extracted_text,
                    height=300,
                    disabled=True
                )
            
            # Display feedback suggestions
            if st.session_state.feedback_suggestions:
                st.subheader("💡 AI Feedback Suggestions")
                st.markdown("Here are 3 specific recommendations to improve your resume:")
                
                for i, suggestion in enumerate(st.session_state.feedback_suggestions, 1):
                    with st.container():
                        st.markdown(f"**Suggestion {i}:**")
                        st.markdown(suggestion)
                        st.markdown("---")
        else:
            st.info("👆 Upload a resume file and click 'Analyze Resume' to see results here.")

if __name__ == "__main__":
    main() 
