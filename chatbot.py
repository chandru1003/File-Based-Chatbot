import PySimpleGUI as sg
import os
from PyPDF2 import PdfReader
import spacy

def process_user_input(user_input, folder_path):
    # Read PDFs from the specified folder and extract text
    extracted_text = ""
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            with open(os.path.join(folder_path, filename), 'rb') as file:
                pdf_reader = PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    extracted_text += page.extract_text()

    # Process the extracted text using spaCy for NLP tasks
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(extracted_text)

    # Search for answers based on the user's input
    processed_user_input = nlp(user_input)
    matches = []
    for sentence in doc.sents:
        if processed_user_input.text in sentence.text:
            matches.append(sentence.text)

    if matches:
        return "Answer found: " + matches[0]
    else:
        return "Sorry, I couldn't find an answer related to your query."
folder_path = "sample files"
# Define the layout for the chatbot UI
layout = [
    [sg.Text('File-Based Chatbot', font='Any 15')],
    [sg.Output(size=(80, 30), key='-OUTPUT-')],
    [sg.Input(key='-IN-', size=(45, 1), enable_events=True), sg.Button('Send')],
]

# Create the window with defined layout
window = sg.Window('File-Based Chatbot', layout)
window.set_icon('icon\icons8-chat-bot-64.ico')

# Event loop to handle interactions
while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break
    elif event == 'Send' or (event == '-IN-' and values['-IN-'] == '\r'):
        user_input = values['-IN-'].strip()
        chatbot_response = process_user_input(user_input,folder_path)

        print(f'User: {user_input}')
        print(f'Chatbot: {chatbot_response}')
        window['-IN-'].update('')  # Clear the input field after processing the input

window.close()

