import streamlit as st
import os
import tempfile
import PyPDF2
import docx2txt
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def extract_text_from_pdf(file):
    """Extract text from PDF file"""
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(file):
    """Extract text from DOCX file"""
    return docx2txt.process(file)

def generate_cover_letter(resume_text, job_description):
    """Generate cover letter using OpenAI's API"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional career advisor who helps write compelling cover letters."},
                {"role": "user", "content": f"Based on the following resume and job description, write a professional and compelling cover letter.\n\nResume:\n{resume_text}\n\nJob Description:\n{job_description}"}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating cover letter: {str(e)}"

def improve_cover_letter(cover_letter, instructions):
    """Improve the cover letter based on user instructions"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional career advisor who helps improve cover letters."},
                {"role": "user", "content": f"Here's a cover letter that needs improvement based on these instructions: {instructions}\n\nCurrent Cover Letter:\n{cover_letter}"}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error improving cover letter: {str(e)}"

def main():
    st.set_page_config(page_title="Cover Letter Generator", page_icon="📝", layout="wide")
    
    st.title("📝 AI-Powered Cover Letter Generator")
    st.write("Upload your resume and enter a job description to generate a personalized cover letter.")
    
    # Initialize session state
    if 'cover_letter' not in st.session_state:
        st.session_state.cover_letter = ""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Sidebar for file upload
    with st.sidebar:
        st.header("1. Upload Your Resume")
        uploaded_file = st.file_uploader("Choose a file (PDF or DOCX)", type=["pdf", "docx"])
        
        st.header("2. Enter Job Description")
        job_description = st.text_area("Paste the job description here", height=200)
        
        if st.button("Generate Cover Letter"):
            if uploaded_file is not None and job_description.strip() != "":
                with st.spinner('Generating your cover letter...'):
                    # Extract text from resume
                    if uploaded_file.type == "application/pdf":
                        resume_text = extract_text_from_pdf(uploaded_file)
                    else:
                        resume_text = extract_text_from_docx(uploaded_file)
                    
                    # Generate cover letter
                    st.session_state.cover_letter = generate_cover_letter(resume_text, job_description)
                    st.session_state.messages = [{"role": "assistant", "content": st.session_state.cover_letter}]
                    st.experimental_rerun()
            else:
                st.warning("Please upload a resume and enter a job description.")
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("Generated Cover Letter")
        if st.session_state.cover_letter:
            st.markdown(st.session_state.cover_letter)
            
            # Download button
            st.download_button(
                label="Download as Text",
                data=st.session_state.cover_letter,
                file_name="cover_letter.txt",
                mime="text/plain"
            )
        else:
            st.info("Your generated cover letter will appear here after you upload a resume and job description.")
    
    with col2:
        st.header("Refine with AI")
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("How would you like to improve the cover letter?"):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate AI response
            with st.spinner('Improving your cover letter...'):
                # Get the current cover letter
                current_letter = st.session_state.cover_letter
                
                # Improve the cover letter based on user instructions
                improved_letter = improve_cover_letter(current_letter, prompt)
                
                # Update the cover letter in session state
                st.session_state.cover_letter = improved_letter
                
                # Add AI response to chat history
                st.session_state.messages.append({"role": "assistant", "content": improved_letter})
                
                # Rerun to update the UI
                st.experimental_rerun()

if __name__ == "__main__":
    main()
