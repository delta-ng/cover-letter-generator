import streamlit as st
import os
import json
import hashlib
import secrets
import string
from pathlib import Path
import PyPDF2
import docx2txt
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Initialize OpenAI client
try:
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
except TypeError:
    # Fallback for older versions
    import openai
    openai.api_key = os.getenv('OPENAI_API_KEY')
    client = openai

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
        if hasattr(client, 'chat') and hasattr(client.chat, 'completions'):
            # New client format (v1.0.0+)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that writes professional cover letters."},
                    {"role": "user", "content": f"Write a professional cover letter based on this resume:\n\n{resume_text}\n\nAnd this job description:\n\n{job_description}"}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
        else:
            # Old client format
            response = client.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that writes professional cover letters."},
                    {"role": "user", "content": f"Write a professional cover letter based on this resume:\n\n{resume_text}\n\nAnd this job description:\n\n{job_description}"}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            return response['choices'][0]['message']['content']
    except Exception as e:
        st.error(f"Error generating cover letter: {str(e)}")
        return ""

def improve_cover_letter(cover_letter, instructions):
    """Improve the cover letter based on user instructions"""
    try:
        if hasattr(client, 'chat') and hasattr(client.chat, 'completions'):
            # New client format (v1.0.0+)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that improves cover letters."},
                    {"role": "user", "content": f"Here's my current cover letter:\n\n{cover_letter}\n\nPlease make these improvements: {instructions}"}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
        else:
            # Old client format
            response = client.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that improves cover letters."},
                    {"role": "user", "content": f"Here's my current cover letter:\n\n{cover_letter}\n\nPlease make these improvements: {instructions}"}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            return response['choices'][0]['message']['content']
    except Exception as e:
        st.error(f"Error improving cover letter: {str(e)}")
        return ""

def main():
    st.set_page_config(page_title="Cover Letter Generator", page_icon="📝", layout="wide")
    
    st.title("📝 AI-Powered Cover Letter Generator")
    st.write("Upload your resume and enter a job description to generate a personalized cover letter.")
    
    # Initialize session state
        # Initialize session state
    if 'cover_letter' not in st.session_state:
        st.session_state.cover_letter = ""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'generations_left' not in st.session_state:
        st.session_state.generations_left = 0

# User data storage
USER_DATA_FILE = 'user_data.json'
ACCESS_CODES_FILE = 'access_codes.json'
MAX_GENERATIONS = 5  # Number of cover letter generations per code
MAX_IMPROVEMENTS = 10  # Number of improvements allowed per generation
CREDITS_PER_CODE = 5  # Default number of generations per access code

# Ensure access_codes.json exists with an initial admin code
if not os.path.exists(ACCESS_CODES_FILE):
    initial_codes = {"ADMIN01": CREDITS_PER_CODE}
    with open(ACCESS_CODES_FILE, 'w') as f:
        json.dump(initial_codes, f)
    print(f"Created initial access code: ADMIN01 with {CREDITS_PER_CODE} generations")

def generate_access_code(length=8):
    """Generate a random alphanumeric access code."""
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_access_codes(count=100, credits=5):
    """Generate new access codes with specified credits."""
    try:
        with open(ACCESS_CODES_FILE, 'r') as f:
            codes = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        codes = {}
    
    new_codes = {}
    for _ in range(count):
        while True:
            code = generate_access_code(CODE_LENGTH)
            if code not in codes and code not in new_codes:
                new_codes[code] = credits
                break
    
    # Save new codes
    codes.update(new_codes)
    with open(ACCESS_CODES_FILE, 'w') as f:
        json.dump(codes, f, indent=2)
    
    return new_codes

def load_user_data():
    """Load user data from file."""
    if not os.path.exists(USER_DATA_FILE):
        return {}
    try:
        with open(USER_DATA_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_user_data(data):
    """Save user data to file."""
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_access_codes():
    """Load access codes from file."""
    if not os.path.exists(ACCESS_CODES_FILE):
        return {}
    try:
        with open(ACCESS_CODES_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def use_access_code(code):
    """Use an access code and return remaining credits and improvements."""
    users = load_user_data()
    code = code.upper()  # Make code case-insensitive
    
    if code not in users:
        # New user with this code
        users[code] = {
            'remaining_generations': MAX_GENERATIONS,
            'remaining_improvements': 0,
            'active_generation': False
        }
        save_user_data(users)
        return users[code]
    
    return users[code] if users[code]['remaining_generations'] > 0 or users[code]['remaining_improvements'] > 0 else None

def show_auth_section():
    """Show the authentication section in the sidebar."""
    st.sidebar.title("🔑 Access Code")
    access_code = st.sidebar.text_input("Enter your access code")
    
    if st.sidebar.button("Activate"):
        if access_code:
            user_data = use_access_code(access_code.strip())
            if user_data is not None:
                st.session_state.authenticated = True
                st.session_state.access_code = access_code.upper()
                st.session_state.user_data = user_data
                st.sidebar.success("Access granted!")
                st.experimental_rerun()
            else:
                st.sidebar.error("No credits remaining for this access code")
        else:
            st.sidebar.warning("Please enter an access code")
    
    # Admin section to generate new codes (only show in development)
    if os.getenv('ENV') == 'development':
        if st.sidebar.button("Generate New Access Codes"):
            new_codes = generate_access_codes(100, CREDITS_PER_CODE)
            st.sidebar.success(f"Generated {len(new_codes)} new access codes")
            st.sidebar.json({k: v for i, (k, v) in enumerate(new_codes.items()) if i < 5})
            if len(new_codes) > 5:
                st.sidebar.info(f"... and {len(new_codes) - 5} more")
    
    return False

# Main app starts here
def main():
    # This must be the first Streamlit command
    st.set_page_config(page_title="Cover Letter Generator", page_icon="📝", layout="wide")
    
    # Initialize all session state variables first
    if 'cover_letter' not in st.session_state:
        st.session_state.cover_letter = ""
    if 'cover_letter_history' not in st.session_state:
        st.session_state.cover_letter_history = []
    if 'show_history' not in st.session_state:
        st.session_state.show_history = False
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'access_code' not in st.session_state:
        st.session_state.access_code = None
    if 'user_data' not in st.session_state:
        st.session_state.user_data = {
            'remaining_generations': 0,
            'remaining_improvements': 0,
            'active_generation': False
        }
    
    # Add version info to sidebar
    with open('VERSION', 'r') as f:
        version = f.read().strip()
    st.sidebar.markdown(f"**Version:** {version}")
    
    # Add link to view cover letter in main panel if in chat view
    if st.session_state.messages and not st.session_state.show_history:
        st.sidebar.markdown("---")
        st.sidebar.info("💡 View the latest generated cover letter in the left panel")
    
    # Add timestamp to messages if not present (for backward compatibility)
    for msg in st.session_state.messages:
        if "timestamp" not in msg:
            msg["timestamp"] = datetime.now().isoformat()
    
    st.title("📝 AI-Powered Cover Letter Generator")
    st.write("Upload your resume and enter a job description to generate a personalized cover letter.")
    
    # Session state is now initialized at the start of main()

    # Check authentication
    if not st.session_state.authenticated:
        show_auth_section()
        st.warning("Please enter a valid access code to use the Cover Letter Generator")
        return

    # Show welcome message and credits
    st.sidebar.success(f"Access Code: {st.session_state.access_code}")
    
    # Sidebar for file upload
    with st.sidebar:
        st.info(f"Generations left: {st.session_state.user_data['remaining_generations']}")
        if st.session_state.user_data['active_generation']:
            st.info(f"Improvements left: {st.session_state.user_data['remaining_improvements']}")
            
        if st.session_state.user_data['remaining_generations'] <= 0:
            st.error("You've used all your generations. Please contact support for more.")
            return

        st.markdown("---")
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
                    
                    # Check if user has generation credits left
                    if st.session_state.user_data['remaining_generations'] > 0:
                        # Generate cover letter
                        st.session_state.cover_letter = generate_cover_letter(resume_text, job_description)
                        st.session_state.messages = [{
                            "role": "assistant", 
                            "content": "Cover letter generated! Try these quick actions or type your own request:\n• Make it more professional\n• Make it more concise\n• Emphasize leadership experience\n• Highlight technical skills\n• Make it more enthusiastic"
                        }]
                        
                        # Update user data
                        users = load_user_data()
                        if st.session_state.access_code in users:
                            users[st.session_state.access_code]['remaining_generations'] -= 1
                            users[st.session_state.access_code]['remaining_improvements'] = MAX_IMPROVEMENTS
                            users[st.session_state.access_code]['active_generation'] = True
                            save_user_data(users)
                            st.session_state.user_data = users[st.session_state.access_code]
                        
                        st.experimental_rerun()
                    else:
                        st.error("You've used all your cover letter generations. Please get a new access code.")
            else:
                st.warning("Please upload a resume and enter a job description.")
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("Generated Cover Letter")
        
        # History view toggles in the Generated Cover Letter section
        if st.session_state.cover_letter_history:
            if st.button("📜 View History" if not st.session_state.show_history else "📝 Back to Editor"):
                st.session_state.show_history = not st.session_state.show_history
                st.experimental_rerun()
        
        if st.session_state.show_history and st.session_state.cover_letter_history:
            st.subheader("Cover Letter History")
            selected_index = st.radio(
                "Select a version to view:",
                range(len(st.session_state.cover_letter_history)),
                format_func=lambda i: f"Version {i+1}"
            )
            st.text_area("Selected Version", st.session_state.cover_letter_history[selected_index], height=350, key="history_display")
            
            if st.button("Restore This Version"):
                st.session_state.cover_letter = st.session_state.cover_letter_history[selected_index]
                st.session_state.show_history = False
                st.experimental_rerun()
        else:
            # Regular cover letter view
            if st.session_state.cover_letter:
                st.text_area(
                    "Current Cover Letter", 
                    st.session_state.cover_letter, 
                    height=400, 
                    key="cover_letter_display"
                )
                
                # Add to history if not already there
                if not st.session_state.cover_letter_history or st.session_state.cover_letter != st.session_state.cover_letter_history[-1]:
                    st.session_state.cover_letter_history.append(st.session_state.cover_letter)
                
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
        
        # Show example prompts when there are no messages yet or after a cover letter is generated
        if not st.session_state.messages or (len(st.session_state.messages) == 1 and 
                                          st.session_state.messages[0]["role"] == "assistant" and 
                                          "Cover letter generated" in st.session_state.messages[0]["content"]):
            with st.chat_message("assistant"):
                st.markdown("💡 **Try these quick actions or type your own request:**")
                st.markdown("• Make it more professional")
                st.markdown("• Make it more concise")
                st.markdown("• Emphasize leadership experience")
                st.markdown("• Highlight technical skills")
                st.markdown("• Make it more enthusiastic")
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                # Only format assistant messages that contain full cover letters
                if (message["role"] == "assistant" and 
                    len(message["content"]) > 100 and 
                    "Cover letter updated" not in message["content"] and
                    "Try these quick actions" not in message["content"]):
                    preview = message["content"][:100] + "... [View in main panel]"
                    st.markdown(preview)
                else:
                    st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("How would you like to improve the cover letter?"):
            # Add user message to chat
            st.session_state.messages.append({
                "role": "user",
                "content": prompt,
                "timestamp": datetime.now().isoformat()
            })
            
            # Get the current cover letter
            current_letter = st.session_state.cover_letter
            
            # Improve the cover letter
            improved_letter = improve_cover_letter(current_letter, prompt)
            
            # Update the cover letter
            st.session_state.cover_letter = improved_letter
            
            # Add to history if not already there
            if not st.session_state.cover_letter_history or improved_letter != st.session_state.cover_letter_history[-1]:
                st.session_state.cover_letter_history.append(improved_letter)
            
            # Add assistant response to chat
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"✅ Cover letter updated based on: *{prompt}*",
                "timestamp": datetime.now().isoformat()
            })
            
            # Check if user has improvement credits left
            if st.session_state.user_data['remaining_improvements'] > 0:
                # Update user data
                users = load_user_data()
                if st.session_state.access_code in users:
                    users[st.session_state.access_code]['remaining_improvements'] -= 1
                    save_user_data(users)
                    st.session_state.user_data = users[st.session_state.access_code]
                    
                    # Rerun to update the UI
                    st.experimental_rerun()
                else:
                    st.error("You've used all improvements for this cover letter. Please generate a new one.")
                    st.experimental_rerun()

if __name__ == "__main__":
    main()
