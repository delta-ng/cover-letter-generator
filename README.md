# AI-Powered Cover Letter Generator

A Streamlit web application that generates personalized cover letters based on your resume and job descriptions, with an interactive chat interface for refinements.

## Features

- Upload your resume in PDF or DOCX format
- Input job descriptions via text area
- Generate a personalized cover letter using AI
- Interactive chat interface to refine and improve the cover letter
- Download the final cover letter as a text file

## Prerequisites

- Python 3.8 or higher
- OpenAI API key

## Setup and Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd cover-letter-generator
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Running the Application

1. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

2. Open your web browser and navigate to the URL shown in the terminal (usually http://localhost:8501)

## How to Use

1. **Upload Your Resume**: Use the sidebar to upload your resume in PDF or DOCX format.
2. **Enter Job Description**: Paste the job description in the text area provided.
3. **Generate Cover Letter**: Click the "Generate Cover Letter" button to create your initial cover letter.
4. **Refine with AI**: Use the chat interface to make improvements to your cover letter. You can ask the AI to make it more professional, adjust the tone, or focus on specific skills.
5. **Download**: Once satisfied, download your cover letter as a text file.

## Dependencies

- Streamlit - For the web interface
- PyPDF2 - For extracting text from PDF files
- python-docx - For working with DOCX files
- openai - For AI-powered text generation
- python-dotenv - For managing environment variables

## License

This project is open source and available under the [MIT License](LICENSE).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
