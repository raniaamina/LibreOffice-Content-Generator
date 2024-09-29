# LibreOffice AI Content Generator


This is simple python macro script for LibreOffice to help you generate content from selected words/sentences with OpenAI or Google AI. 
The latest update allow you to do more;
- Generate Content
- Translate to other language
- Summarize long content
- Improve content
- Other custom task (solve math question and much more)

|   |   |
|---|---|
|![Screenshot](/LibreOfficexOpenAI.png)   |![Screenshot](/LibreOfficexAI.png)   |


## Requirements
- APSO (Alternative Python Script Organizer), get here [Apso Gitlab](https://gitlab.com/jmzambon/apso/)
- OpenAI API Key, get here: [OpenAI Platform](https://platform.openai.com/account/api-keys)
- Google AI API Key, get here [Google AI](https://aistudio.google.com/app/apikey)
- zenity for handle progressbar (optional)
- Some Python Modules;
    - python-dotenv
    - openai
    - google-generativeai
    - ttkthemes
- Little knowledge of LibreOffice macros and python

## Usage
- Install APSO extension first, if you don't know how to install LibreOffice extension DDG-ing first!
- Rename sample.env to .env and save it to following directory (you may need create Scripts/python directory by yourself if not exist yet):
    - Linux: `$HOME/.config/libreoffice/4/user/Scripts/python/.env`
    - Windows: `%APPDATA%\LibreOffice\4\user\Scripts\python\.env`
    - MacOS: `$HOME/Library/'Application Support'/LibreOffice/4/user/Scripts/python/.env`
- Don't forget to replace API Key with your own.
- Open LibreOffice Writer then, open Macros in Tools > Macros > Organize Python Scripts
- Just copy and paste LibreOfficexAi.py to following directory:
    - Linux: `$HOME/.config/libreoffice/4/user/Scripts/python`
    - Windows: `%APPDATA%\LibreOffice\4\user\Scripts\python`
    - MacOS: `$HOME/Library/'Application Support'/LibreOffice/4/user/Scripts/python`
- Write a sentences, select it, then run macro, [see this video](https://youtu.be/riSqE-5o8is)
- [Update Video](https://youtu.be/nJqgQcosNjc)

## Need Help to Improve 
- [x] Add loading dialog or progressbar while macro waiting respons
- [ ] Convert this script as extension(?)

## Known Issues
### Windows
- I found that this script does not work well if the python version used on windows is not the same as the python that comes with LibreOffice by default. So the safest option to run this macro script on Windows (with the latest LibreOffice) is to install Python 3.9 standalone. You can directly download here: [Python 3.9.13](https://www.python.org/ftp/python/3.9.13/python-3.9.13-amd64.exe)

- You can move .env file to any place as you want, then just edit the script like this (make sure to use double backslash in Windows when you write a path);

```python 
config = dotenv_values('''C:\\Users\\dev\\AppData\\Roaming\\LibreOffice\\4\\user\\.env''') 
```

## Disclaimers
- Do with your own risk, i give no any warranty with this script, ('-_-').
- I just test this macros on Debian Linux (unstable) with latest LibreOffice, i can't sure this macro can run every where. Please ping me on ticket issue if you can run this macro on your operating system.
