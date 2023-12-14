import os
from dotenv import dotenv_values
import subprocess

import sys
sys.path.append('/path/to/python/openai/modules') #  use 'pip show openai' to get the path 
import openai

config = dotenv_values(os.environ['HOME'] + "/.create-caption/.env")
openai.api_key = config['API_KEY']

def update_status(message):
    """Update status message in LibreOffice using Zenity."""
    progress_command = [
        "zenity",
        "--progress",
        "--text=%s" % message,
        "--pulsate",
        "--auto-close",
    ]
    subprocess.Popen(progress_command)

def buat_konten():
    doc = XSCRIPTCONTEXT.getDocument()
    selection = doc.getCurrentSelection()
    if selection.supportsService("com.sun.star.text.TextRanges"):
        total_ranges = len(selection)
        for i, textRange in enumerate(selection):
            message = f"Mohon tunggu sejenak ..."
            update_status(message)

            prompt = textRange.getString()
            generated_text = f"Buatkan saya sebuah: {prompt}"
            response = openai.Completion.create(
                model="gpt-3.5-turbo-instruct",
                prompt=generated_text,
                temperature=0.85,
                max_tokens=1024,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            output_text = response.choices[0].text
            cursor = doc.getCurrentController().getViewCursor()
            docText = doc.Text

            # Set Selected Text as Title
            text = textRange.getString()
            text_with_newline = text + "\n"
            textRange.setString(text_with_newline)

            # Insert Open AI response to current document
            docText.insertString(cursor, output_text, False)

            # Apply styling
            textCursor = textRange.getText().createTextCursorByRange(textRange)
            textCursor.setPropertyValue("CharWeight", 150)  # set title bold

        # Close the Zenity progress dialog when processing is complete
        subprocess.run(["pkill", "zenity"])
    else:
        return "Invalid selection"
