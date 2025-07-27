# ResumeAI - AI-Powered Resume Analysis Tool

ResumeAI is a Streamlit application that helps users analyze their resumes using Azure AI services. Upload your resume in PDF, DOCX, or TXT format and get intelligent feedback to improve it.

## Features

- **Multi-format Support**: Upload resumes in PDF, DOCX, or TXT formats
- **Azure Document Intelligence**: Automatic text extraction from PDF and DOCX files
- **Azure OpenAI Integration**: Get 3 specific, actionable feedback suggestions
- **Clean UI**: Intuitive interface with expandable sections
- **Session State Management**: Remembers your Azure credentials during the session
- **Fallback Text Extraction**: Local text extraction when Azure Document Intelligence is not configured

## Prerequisites

Before running the application, you'll need:

1. **Python 3.8+** installed on your system
2. **Azure Document Intelligence resource** (optional but recommended for better PDF/DOCX text extraction)
3. **Azure OpenAI resource** (required for feedback generation)

## Azure Services Setup

### Azure Document Intelligence (Optional)

1. Create an Azure Document Intelligence resource in the Azure portal
2. Note down the **Endpoint** and **API Key** from the resource

### Azure OpenAI (Required)

1. Create an Azure OpenAI resource in the Azure portal
2. Deploy a model (e.g., `gpt-35-turbo` or `gpt-4`) 
3. Note down:
   - **Endpoint** (e.g., `https://your-resource.openai.azure.com/`)
   - **API Key**
   - **Deployment Name** (the name you gave to your deployed model)

## Installation

1. Clone or download this repository:
   ```bash
   git clone <repository-url>
   cd ResumeAI
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start the Streamlit application:
   ```bash
   streamlit run app.py
   ```

2. Open your web browser and navigate to the provided URL (typically `http://localhost:8501`)

3. **Configure Azure Credentials** in the sidebar:
   - Enter your Azure Document Intelligence endpoint and API key (optional)
   - Enter your Azure OpenAI endpoint, API key, and deployment name (required)

4. **Upload Your Resume**:
   - Click "Choose your resume file" and select a PDF, DOCX, or TXT file
   - Click "🔍 Analyze Resume" to start the analysis

5. **View Results**:
   - The extracted text will appear in an expandable section
   - AI-generated feedback suggestions will be displayed below

## Application Flow

1. **File Upload**: Users upload their resume in supported formats
2. **Text Extraction**: 
   - For TXT files: Direct text reading
   - For PDF/DOCX files: Azure Document Intelligence (if configured) or local extraction
3. **Text Display**: Extracted text is shown in an expandable section
4. **AI Analysis**: Text is sent to Azure OpenAI for feedback generation
5. **Results**: 3 specific improvement suggestions are displayed

## Features Explained

### Smart Text Extraction
- **Azure Document Intelligence**: Superior text extraction with OCR capabilities
- **Local Fallback**: PyPDF2 for PDFs and python-docx for DOCX files when Azure service is unavailable

### Session State Management
- Credentials are remembered during your session
- Extracted text and feedback persist until you refresh the page

### Clean UI Design
- Two-column layout for optimal space usage
- Configuration status indicators in the sidebar
- Expandable sections to keep the interface clean
- Loading spinners and progress indicators

## Troubleshooting

### Common Issues

1. **"Failed to extract text"**:
   - Check if your file is corrupted
   - Try using Azure Document Intelligence for better results
   - Ensure the file format is supported (PDF, DOCX, TXT)

2. **"Failed to get feedback from Azure OpenAI"**:
   - Verify your Azure OpenAI endpoint, API key, and deployment name
   - Check if your deployment is active and has sufficient quotas
   - Ensure the deployment name matches exactly (case-sensitive)

3. **"Error with Azure Document Intelligence"**:
   - Verify your endpoint and API key
   - Check if the resource is active
   - The app will fallback to local extraction automatically

### File Requirements

- **Maximum file size**: Depends on your Streamlit configuration (default ~200MB)
- **Supported formats**: PDF, DOCX, TXT
- **Text content**: Files should contain readable text (not just images)

## Security Notes

- API keys are stored in session state (not persistent)
- Temporary files are automatically cleaned up after processing
- Consider using environment variables for API keys in production

## Dependencies

- `streamlit>=1.28.0`: Web application framework
- `azure-ai-documentintelligence>=1.0.0`: Azure Document Intelligence client
- `openai>=1.3.0`: Azure OpenAI client
- `python-docx>=0.8.11`: DOCX file processing
- `PyPDF2>=3.0.1`: PDF file processing
- `python-multipart>=0.0.6`: File upload support

## License

This project is provided as-is for educational and development purposes. 