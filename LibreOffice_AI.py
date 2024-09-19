import os
import subprocess
import threading
import time

import sys
sys.path.append('/path/to/python/openai/modules') #  use 'pip show openai' to get the path 

from dotenv import dotenv_values
import openai

# Load API key from .env file
config = dotenv_values(os.environ['HOME'] + "/.create-caption/.env")
openai.api_key = config['API_KEY']

def update_status(message):
    """Update status message in LibreOffice using Zenity."""
    global zenity_process
    progress_command = [
        "zenity",
        "--progress",
        "--text=%s" % message,
        "--pulsate",
        "--auto-close",
    ]
    zenity_process = subprocess.Popen(progress_command)

def close_zenity():
    """Ensure Zenity is closed after processing."""
    if zenity_process:
        zenity_process.terminate()  # Try to terminate Zenity
        time.sleep(1)  # Give it a short time to close
        zenity_process.kill()  # Force kill if necessary
        print("Zenity closed")

# Initialize global variable
zenity_process = None

def buat_konten():
    doc = XSCRIPTCONTEXT.getDocument()
    selection = doc.getCurrentSelection()
    if selection.supportsService("com.sun.star.text.TextRanges"):
        total_ranges = len(selection)
        for i, textRange in enumerate(selection):
            message = f"Mohon tunggu sejenak ..."
            update_status(message)

            prompt = textRange.getString()
            generated_text = f"""Please help me to make content about:
                {prompt}
                
                the response should be in Bahasa Indonesia by default otherwise I ask to use a specific language.
                ONLY ANSWER CONTENT
                DO NOT ADD ANY COMMENT INSIDE YOUR RESPONSES
                DO NOT REPEAT THE REQUEST
                DO NOT REPLY WITH MARKDOWN FORMAT WITHOUT REQUEST
                """
            
            try:
                # Create a chat completion using the new API
                response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "user", "content": generated_text}
                    ],
                    temperature=0.85,
                    max_tokens=1024,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0
                )
                output_text = response.choices[0].message.content
            except openai.OpenAIError as e:
                output_text = f"Error: {str(e)}"
                print(output_text)
            
            cursor = doc.getCurrentController().getViewCursor()
            docText = doc.Text

            # Set Selected Text as Title
            text = textRange.getString()
            text_with_newline = text + "\n"
            textRange.setString(text_with_newline)

            # Insert OpenAI response to current document
            docText.insertString(cursor, output_text, False)

            # Apply styling
            textCursor = textRange.getText().createTextCursorByRange(textRange)
            textCursor.setPropertyValue("CharWeight", 150)  # set title bold

        # Close the Zenity progress dialog when processing is complete
        close_zenity()
    else:
        return "Invalid selection"


