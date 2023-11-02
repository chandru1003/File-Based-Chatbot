import PyPDF2
from transformers import pipeline
import transformers
import PySimpleGUI as sg
import os
import spacy

class FileBasedChatbot:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.create_window()

    def extract_text_from_pdfs(self):
        extracted_text = ""
        for filename in os.listdir(self.folder_path):
            if filename.endswith(".pdf"):
                with open(os.path.join(self.folder_path, filename), 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        extracted_text += page.extract_text()
                        print(extracted_text)
        return extracted_text

    def summarize_text(self, text):
        summarizer = pipeline("summarization",  model="T5-small", tokenizer="T5-small", framework="tf")
        summary = summary = summarizer(text, max_length=100, min_length=30, do_sample=False)
        return summary[0]['summary_text']

    def process_user_input(self, user_input):
        extracted_text = self.extract_text_from_pdfs()
        summarized_text = self.summarize_text(extracted_text)
        return summarized_text

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
                self.window['-OUTPUT-'].update(chatbot_response)
                self.window['-IN-'].update('')  # Clear the input field after processing the input

        self.window.close()

if __name__ == "__main__":
    folder_path = "sample files"
    chatbot = FileBasedChatbot(folder_path)
    chatbot.run()
