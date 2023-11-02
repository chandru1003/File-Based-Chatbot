import PySimpleGUI as sg
import os
from PyPDF2 import PdfReader
import spacy

class FileBasedChatbot:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.extracted_text = self.extract_text_from_pdfs()
        self.nlp = spacy.load("en_core_web_sm")
        self.doc = self.nlp(self.extracted_text)
        self.create_window()

    def extract_text_from_pdfs(self):
        extracted_text = ""
        for filename in os.listdir(self.folder_path):
            if filename.endswith(".pdf"):
                with open(os.path.join(self.folder_path, filename), 'rb') as file:
                    pdf_reader = PdfReader(file)
                    for page in pdf_reader.pages:
                        extracted_text += page.extract_text()
                        print(extracted_text)
        return extracted_text

    def process_user_input(self, user_input):
        processed_user_input = self.nlp(user_input)
        matches = []
        for sentence in self.doc.sents:
            if processed_user_input.text in sentence.text:
                matches.append(sentence.text)

        if matches:
            return "Answer found: " + matches[0]
        else:
            return "Sorry, I couldn't find an answer related to your query."

    def create_window(self):
        layout = [
            [sg.Text('File-Based Chatbot', font='Any 15')],
            [sg.Output(size=(80, 30), key='-OUTPUT-')],
            [sg.Input(key='-IN-', size=(45, 1), enable_events=True), sg.Button('Send')],
        ]

        self.window = sg.Window('File-Based Chatbot', layout)
        self.window.set_icon('icon\icons8-chat-bot-64.ico')

    def run(self):
        while True:
            event, values = self.window.read()

            if event == sg.WIN_CLOSED:
                break
            elif event == 'Send' or (event == '-IN-' and values['-IN-'] == '\r'):
                user_input = values['-IN-'].strip()
                chatbot_response = self.process_user_input(user_input)

                print(f'User: {user_input}')
                print(f'Chatbot: {chatbot_response}')
                self.window['-IN-'].update('')  # Clear the input field after processing the input

        self.window.close()

if __name__ == "__main__":
    folder_path = "sample files"
    chatbot = FileBasedChatbot(folder_path)
    chatbot.run()
