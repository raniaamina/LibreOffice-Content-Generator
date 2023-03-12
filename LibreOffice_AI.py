import os
from dotenv import dotenv_values

import sys # this part is optional, sometime libreoffice can't detect installed module
sys.path.append('/path/to/python/openai/modules') #  use 'pip show openai' to get the path 
import openai

# Get API Token
config = dotenv_values('.env')
openai.api_key = config['API_KEY']

def buat_konten():
    doc = XSCRIPTCONTEXT.getDocument()
    selection = doc.getCurrentSelection()
    if selection.supportsService("com.sun.star.text.TextRanges"):
        for textRange in selection:
            prompt = textRange.getString()
            generated_text = f"Buatkan saya sebuah: {prompt}"
            response = openai.Completion.create(
              model="text-davinci-003",
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
            
            # insert Open AI respons to current document
            docText.insertString(cursor, output_text, False)
            
            # Apply styling
            textCursor = textRange.getText().createTextCursorByRange(textRange)
            textCursor.setPropertyValue("CharWeight", 150) # set title bold
    else:
        return "Invalid selection"
