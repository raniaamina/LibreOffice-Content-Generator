import os
import sys
import sysconfig
# sys.path.append('/home/sherlock/.local/pipx/venvs/google-generativeai/lib/python3.9/site-packages')

## Hint:  use 'pip show openai' to get the path. This part usually used/needed when you're using Pyenv or Virtualenv in your system

import openai
import google.generativeai as genai
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
from dotenv import dotenv_values
import threading
import subprocess
import platform
import configparser
import tempfile



def check_python_version():
    document = XSCRIPTCONTEXT.getDocument().getText()
    python_version = f"Python Version: {sys.version}\n"
    python_executable = f"Python Executable: {sys.executable}\n"

    python_prefix = f"sys.prefix: {sys.prefix}\n"
    python_base_prefix = f"sys.base_prefix: {sys.base_prefix}\n"
    python_paths = f"Python Paths: {sysconfig.get_paths()}\n"

    document.insertString(document.End, python_version, False)
    document.insertString(document.End, python_executable, False)
    document.insertString(document.End, python_prefix, False)
    document.insertString(document.End, python_base_prefix, False)
    document.insertString(document.End, python_paths, False)

def get_env_file_path():
    if platform.system() == "Linux":
        return os.path.join(os.environ['HOME'], ".config/libreoffice/4/user/Scripts/python/.env")
    elif platform.system() == "Windows":
        return os.path.join(os.environ['APPDATA'], "LibreOffice", "4", "user", "Scripts", "python", ".env")
    elif platform.system() == "Darwin":
        return os.path.join(os.environ['HOME'], "Library", "Application Support", "LibreOffice", "4", "user", "Scripts", "python", ".env")
    else:
        raise NotImplementedError("Unsupported OS")

# Load environment variables from the determined path
env_file_path = get_env_file_path()
config = dotenv_values(env_file_path)
openai.api_key = config['OPENAI_API_KEY']
openaimodel = config['OPENAIMODEL']
gemini_api_key = config['GEMINI_API_KEY']
geminimodel = config['GEMINIMODEL']

### Config Files
# Path to configuration file
def get_config_path():
    temp_dir = tempfile.gettempdir()
    return os.path.join(temp_dir, 'libreai-user.conf')

# Load the configuration
def load_config():
    config = configparser.ConfigParser()
    config_path = get_config_path()

    if os.path.exists(config_path):
        config.read(config_path)
    else:
        # Create default config if not found
        config['Settings'] = {
            'zenity_enabled': 'true',
            'platform': 'OpenAI'
        }
        save_config(config)
    return config

# Save the configuration
def save_config(config):
    with open(get_config_path(), 'w') as configfile:
        config.write(configfile)

def toggle_zenity_in_config(enable_zenity):
    config = load_config() 
    config.set('Settings', 'zenity_enabled', str(enable_zenity)) 
    save_config(config)  

def is_zenity_enabled():
    config = load_config()
    zenity_enabled = config.get('Settings', 'zenity_enabled', fallback='false') 
    return zenity_enabled == 'True'

def save_platform_in_config(selected_platform):
    config = load_config()  # Load the existing configuration
    config['Settings']['platform'] = selected_platform  # Save the selected platform
    save_config(config)  # Use the existing save function

def load_platform_from_config():
    config_path = os.path.join(tempfile.gettempdir(), 'libreai-user.conf')
    config = configparser.ConfigParser()

    # Read the config file if it exists
    if os.path.exists(config_path):
        config.read(config_path)
        # Use get method with a fallback to 'OpenAI' if not found
        return config.get('Settings', 'platform', fallback='OpenAI')
    return 'OpenAI' 
config = load_config()
## End of Config Files


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
    if is_zenity_available() and is_zenity_enabled():
        progress_command = [
            "bash", "-c", "GDK_BACKEND=x11 QT_QPA_PLATFORM=xcb zenity --progress --text='%s' --pulsate --auto-close" % message
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
    doc = XSCRIPTCONTEXT.getDocument()
    prompt = textRange.getString()

    genericRule = """
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

    if is_zenity_enabled():
        update_status("Please wait ...")

    try:
        selected_platform = load_platform_from_config()  # Get the selected platform

        if selected_platform == "OpenAI":
            response = openai.chat.completions.create(
                model=openaimodel,
                messages=[{"role": "user", "content": generated_text}],
                temperature=0.85,
                max_tokens=1024,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            output_text = "\n" + response.choices[0].message.content + "\n"

        elif selected_platform == "Gemini":
            # Create the model
            genai.configure(api_key=gemini_api_key)
            generation_config = {
                "temperature": 0.85,
                "top_p": 0.95,
                "top_k": 64,
                "max_output_tokens": 8192,
                "response_mime_type": "text/plain",
            }

            model = genai.GenerativeModel(
                model_name=geminimodel,
                generation_config=generation_config,
                system_instruction="""
                JANGAN MENAMBAHKAN PADA BALASAN
                DILARANG MENGGUNAKAN FORMAT MARKDOWN
                DILARANG MENGGUNAKAN SIMBOL-SIMBOL LATEXT
                HANYA BALAS DENGAN PLAIN TEXT
                SELALU BALAS DENGAN BAHASA YANG DIGUNAKAN OLEH PENGGUNA KECUALI ADA INSTRUKSI KHUSUS
                """,
            )

            chat_session = model.start_chat(history=[])
            response = chat_session.send_message(generated_text)

            output_text = "\n" + response.text + "\n"

    except openai.OpenAIError as e:
        output_text = f"\nError: {str(e)}"
        print(output_text)
    except Exception as e:
        output_text = f"\nError: {str(e)}"
        print(output_text)

    # Insert output to the document
    cursor = doc.getCurrentController().getViewCursor()
    textRange.setString(textRange.getString() + "\n")

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
    def load_settings():
        zenity_enabled = is_zenity_enabled()
        zenity_var.set(zenity_enabled)

    def on_submit():
        selected_task = task_var.get()
        selected_language = language_var.get()
        custom_prompt = custom_text.get("1.0", tk.END).strip()  # Get text from textarea

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
    root = ThemedTk()
    root.title("Choose Action")

    os_name = platform.system()
    root.set_theme("black")

    root.geometry("500x300")
    root.resizable(False, False)
    root.attributes('-topmost', True)

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    main_tab = tk.Frame(notebook)
    about_tab = tk.Frame(notebook)
    settings_tab = tk.Frame(notebook)
    notebook.add(main_tab, text="Main")
    notebook.add(settings_tab, text="Settings")
    notebook.add(about_tab, text="About")

    # Configure the grid to expand columns and rows
    main_tab.grid_columnconfigure(0, weight=1)
    main_tab.grid_columnconfigure(1, weight=1)
    main_tab.grid_rowconfigure(3, weight=1)

    settings_tab.grid_columnconfigure(0, weight=1)
    settings_tab.grid_columnconfigure(1, weight=1)
    settings_tab.grid_rowconfigure(3, weight=1)

    # Task selection components
    task_label = tk.Label(main_tab, text="Choose Action:")
    task_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

    task_var = tk.StringVar()
    task_choices = ["Generate Content", "Translate", "Summarize", "Improve", "Custom Action"]
    task_var.set(task_choices[0])
    task_dropdown = tk.OptionMenu(main_tab, task_var, *task_choices)
    task_dropdown.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

    # Language input for translation
    language_label = tk.Label(main_tab, text="Type Target Language (ex. English):")
    language_var = tk.StringVar()
    language_entry = tk.Entry(main_tab, textvariable=language_var)

    # Custom prompt input as a textarea
    custom_label = tk.Label(main_tab, text="What should AI do with this selected text?")
    custom_text = tk.Text(main_tab, height=4)

    def on_task_change(*args):
        if task_var.get() == "Translate":
            language_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
            language_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
            custom_label.grid_forget()
            custom_text.grid_forget()
        elif task_var.get() == "Custom Action":
            custom_label.grid(row=2, column=0, padx=10, pady=0, sticky="w")
            custom_text.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
            language_label.grid_forget()
            language_entry.grid_forget()
        else:
            language_label.grid_forget()
            language_entry.grid_forget()
            custom_label.grid_forget()
            custom_text.grid_forget()

    task_var.trace("w", on_task_change)  # Track changes to the task option

    # Apply button at the bottom with full width
    submit_button = tk.Button(main_tab, text="Apply", command=on_submit)
    submit_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="ew")


    # Status label
    status_label = tk.Label(main_tab, text="")
    status_label.grid(row=5, column=0, columnspan=2, padx=10, pady=5, sticky="ew")


    # Settings tab content
    initial_platform = load_platform_from_config()  # Load saved platform
    zenity_enabled = config.getboolean('Settings', 'zenity_enabled')

    platform_var = tk.StringVar(value=initial_platform)  # Set initial value from config
    zenity_var = tk.BooleanVar(value=zenity_enabled)  # Set initial value for Zenity checkbox from config

    platform_label = tk.Label(settings_tab, text="Select AI Platform:")
    platform_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

    platform_dropdown = tk.OptionMenu(settings_tab, platform_var, "OpenAI", "Gemini")
    platform_dropdown.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

    zenity_checkbox = tk.Checkbutton(settings_tab, text="Enable Progressbar for Linux (EXPERIMENTAL)", variable=zenity_var)
    zenity_checkbox.grid(row=1, column=0, columnspan=2, padx=5, pady=10, sticky="w")


    def on_apply_settings():
        toggle_zenity_in_config(zenity_var.get())
        save_platform_in_config(platform_var.get())


    save_button = tk.Button(settings_tab, text="Save Settings", command=on_apply_settings)
    save_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")


    # About tab content
    about_label = tk.Label(about_tab, text="This is simple python macro script for LibreOffice by Rania Amina \nto help you generate content from selected words/sentences \nwith OpenAI. For more info, visit:")
    about_label.pack(padx=10, pady=10)

    github_link = tk.Label(about_tab, text="LibreOffice Content Generator GitHub Repository", fg="blue", cursor="hand2")
    github_link.pack(padx=10, pady=10)
    github_link.bind("<Button-1>", lambda e: os.system("xdg-open https://github.com/raniaamina/LibreOffice-Content-Generator"))
    
    sponsorLink = tk.Label(about_tab, text="Support Dev", fg="green", cursor="hand2")
    sponsorLink.pack(padx=10, pady=10)
    sponsorLink.bind("<Button-1>", lambda e: os.system("xdg-open https://saweria.co/raniaamina"))


    load_settings()
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
        print("Please select text first!")
