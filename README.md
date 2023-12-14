# LibreOffice AI Content Generator

This is simple python macro script for LibreOffice to help you generate content from selected words/sentences with OpenAI.  

## Requirements
- APSO (Alternative Python Script Organizer), get here [Apso Gitlab](https://gitlab.com/jmzambon/apso/)
- OpenAI API Key, get here: [OpenAI Platform](https://platform.openai.com/account/api-keys)
- zenity for handle progressbar
- Some Python Modules;
    - python-dotenv
    - openai
- Little knowledge of LibreOffice macros and python

## Usage
- Install APSO extension first, if you don't know how to install LibreOffice extension DDG-ing first!
- Rename sample.env to .env and save it to your $HOME directory. Don't forget to replace API Key with your own.
- Open LibreOffice Writer then, open Macros in Tools > Macros > Organize Python Scripts
- Create new module, then copy and past content of LibreOffice_AI.py to your new module. Set the openai module path inside script if needed, and save it!
- Write a sentences, select it, then run macro, [see this video](https://youtu.be/riSqE-5o8is)

## Need Help to Improve 
- [ ] Add loading dialog or progressbar while macro waiting respons
- [ ] Convert this script as extension(?)

## Disclaimers
- Do with your own risk, i give no any warranty with this script, ('-_-').
- I just test this macros on Debian Linux (unstable) with latest LibreOffice, i can't sure this macro can run every where. Please ping me on ticket issue if you can run this macro on your operating system.
