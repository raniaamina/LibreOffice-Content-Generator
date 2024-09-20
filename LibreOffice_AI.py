import os
import sys
sys.path.append('/path/to/python/openai/modules') #  use 'pip show openai' to get the path 

import openai
import tkinter as tk
from dotenv import dotenv_values
import threading
import subprocess
import platform

# Load API key from .env file
config = dotenv_values(os.environ['HOME'] + "/.create-caption/.env")
openai.api_key = config['API_KEY']

zenity_process = None

def is_zenity_available():
    """Check if Zenity is available on Linux."""
    if platform.system() == "Linux":
        result = subprocess.run(['which', 'zenity'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    return False

def update_status(message):
    """Update status message using Zenity if available."""
    global zenity_process
    if is_zenity_available():
        progress_command = [
            "bash", "-c", "GDK_BACKEND=x11 zenity --progress --text='%s' --pulsate --auto-close" % message
        ]
        zenity_process = subprocess.Popen(progress_command)

def close_zenity():
    """Ensure Zenity is closed after processing."""
    global zenity_process
    if zenity_process:
        zenity_process.terminate()
        try:
            zenity_process.kill()
        except Exception as e:
            print(f"Error closing Zenity: {e}")

def proses_teks(tugas, textRange, bahasa=None, custom_prompt=None):
    """Fungsi generik untuk memproses teks dengan berbagai tugas."""
    doc = XSCRIPTCONTEXT.getDocument()
    prompt = textRange.getString()

    genericRule = """
    the response should be in Bahasa Indonesia by default otherwise I ask to use a specific language.
    ONLY ANSWER CONTENT
    DO NOT ADD ANY COMMENT INSIDE YOUR RESPONSES
    DO NOT ANSWER BY REPEATING THE REQUEST
    DO NOT REPLY WITH MARKDOWN FORMAT WITHOUT REQUEST
    REPLY WITH NONFORMATED PLAIN TEXT ONLY
    ONLY REGULAR TEXT ALLOWED, 
    DO NOT REPLY WITH COMPLEX SYMBOL.
    DO NOT REPLY WITH MATH NOTATION WITHOUT REQUEST.
    DO NOT REPLY WITH LATEXT NOTATION LIKE '\frac', '\right', etc OR SYMBOL WITHOUT REQUEST.
    """

    if tugas == "Generate Content":
        generated_text = f"Please help me to make content about: {prompt}. {genericRule}"
    elif tugas == "Translate" and bahasa:
        generated_text = f"Please translate the following content to {bahasa}: {prompt}. {genericRule}"
    elif tugas == "Summarize":
        generated_text = f"Please summarize the following content: {prompt} as simple as possible. {genericRule}"
    elif tugas == "Improve":
        generated_text = f"Please improve the sentence structure, fix typo, more efficient, and more understandable of the following content: {prompt}. REMOVE UNUSED PART IF POSSIBLE. {genericRule}"
    elif tugas == "Custom Action" and custom_prompt:
        generated_text = f"{custom_prompt} {prompt} {genericRule}"
    else:
        return "Invalid task"

    update_status("Please wait ...")

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": generated_text}],
            temperature=0.85,
            max_tokens=1024,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        output_text = "\n" + response.choices[0].message.content + "\n"
    except openai.OpenAIError as e:
        output_text = f"\nError: {str(e)}"
        print(output_text)

    # Sisipkan hasil ke dokumen
    cursor = doc.getCurrentController().getViewCursor()
    textRange.setString(textRange.getString() + "\n")  # Tambahkan newline untuk memisahkan input dan output

    # Insert OpenAI response to current document
    start_position = cursor.getText().getEnd()  # Save current cursor position before inserting text
    doc.Text.insertString(cursor, output_text, False)
    
    # Set the cursor to select the newly inserted text (from start_position to the current position)
    end_position = doc.getCurrentController().getViewCursor().getText().getEnd()  # Get end position after inserting
    cursor.goLeft(len(output_text), False)  # Move cursor left by the length of the inserted text
    cursor.goRight(len(output_text), True)  # Select the newly inserted text
    
    # Set the color of the selected text to red
    cursor.setPropertyValue("CharColor", 16711680)  # Merah

    close_zenity()

def show_task_dialog(textRange):
    def on_submit():
        selected_task = task_var.get()
        selected_language = language_var.get()
        custom_prompt = custom_entry.get()
        
        if selected_task == "Translate" and not selected_language:
            status_label.config(text="Please enter a language/country name.")
        elif selected_task == "Custom Action" and not custom_prompt:
            status_label.config(text="Please enter custom prompt action.")
        else:
            root.destroy()
            if selected_task == "Translate":
                proses_teks(selected_task, textRange, bahasa=selected_language)
            elif selected_task == "Custom Action":
                proses_teks(selected_task, textRange, custom_prompt=custom_prompt)
            else:
                proses_teks(selected_task, textRange)

    # Setup Tkinter dialog
    root = tk.Tk()
    root.title("Choose Action")

    task_label = tk.Label(root, text="Choose Action:")
    task_label.grid(row=0, column=0, padx=10, pady=10)

    task_var = tk.StringVar()
    task_choices = ["Generate Content", "Translate", "Summarize", "Improve", "Custom Action"]
    task_var.set(task_choices[0])
    task_dropdown = tk.OptionMenu(root, task_var, *task_choices)
    task_dropdown.grid(row=0, column=1, padx=10, pady=10)

    language_label = tk.Label(root, text="Type Target Language (exm. English):")
    language_var = tk.StringVar()
    language_entry = tk.Entry(root, textvariable=language_var)

    custom_label = tk.Label(root, text="Enter custom request:")
    custom_entry = tk.Entry(root)

    def on_task_change(*args):
        if task_var.get() == "Translate":
            language_label.grid(row=2, column=0, padx=10, pady=5)
            language_entry.grid(row=2, column=1, padx=10, pady=5)
            custom_label.grid_forget()
            custom_entry.grid_forget()
        elif task_var.get() == "Custom Action":
            custom_label.grid(row=2, column=0, padx=10, pady=5)
            custom_entry.grid(row=2, column=1, padx=10, pady=5)
            language_label.grid_forget()
            language_entry.grid_forget()
        else:
            language_label.grid_forget()
            language_entry.grid_forget()
            custom_label.grid_forget()
            custom_entry.grid_forget()

    task_var.trace("w", on_task_change)  # Lacak perubahan pilihan tugas

    submit_button = tk.Button(root, text="Apply", command=on_submit)
    submit_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

    status_label = tk.Label(root, text="")
    status_label.grid(row=4, column=0, columnspan=2, padx=10, pady=5)

    root.mainloop()

def run_dialog_thread(textRange):
    dialog_thread = threading.Thread(target=show_task_dialog, args=(textRange,))
    dialog_thread.start()

def buat_konten():
    doc = XSCRIPTCONTEXT.getDocument()
    selection = doc.getCurrentSelection()
    if selection.supportsService("com.sun.star.text.TextRanges"):
        textRange = selection.getByIndex(0)
        run_dialog_thread(textRange)
    else:
        print("Tidak ada teks yang dipilih.")
