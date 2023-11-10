import PySimpleGUI as sg
import pdfplumber
import os
from transformers import pipeline

class FileBasedChatbot:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.extracted_text = self.extract_text_from_pdfs()
        self.summarization_pipeline = pipeline("summarization",model="t5-base", tokenizer="t5-base", framework="tf")         
        self.create_window()

    def extract_text_from_pdfs(self):
        extracted_texts = []
        for filename in os.listdir(self.folder_path):
            if filename.endswith(".pdf"):
                with pdfplumber.open(os.path.join(self.folder_path, filename)) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:  
                            extracted_texts.append(text)
        extracted_text = "\n".join(extracted_texts)
        with open("extracted_text.txt", "w", encoding="utf-8") as text_file:
            text_file.write(extracted_text)
        return extracted_text   


    def summarize_text(self, combined_text):        
        summary = self.summarization_pipeline(combined_text, max_length=60, min_length=30, do_sample=False)

        return summary[0]['summary_text']

    def process_user_input(self, user_input):
        matches = [sentence for sentence in self.extracted_text.split('.') if user_input.lower() in sentence.lower()]
        return "Answer found: " + self.summarize_text(' '.join(matches)) if matches else "Sorry, I couldn't find an answer related to your query."

    def create_window(self):
        layout = [
            [sg.Text('File-Based Chatbot', font='Any 15')],
            [sg.Output(size=(80, 30), key='-OUTPUT-')],
            [sg.Input(key='-IN-', size=(70, 1)), sg.Button('Send', bind_return_key=True)]
        ]
        self.window = sg.Window('File-Based Chatbot', layout, finalize=True)
        self.window.set_icon('icon\icons8-chat-bot-64.ico')

    def run(self):
        while True:
            event, values = self.window.read()
            if event in (sg.WIN_CLOSED, 'Exit'):
                break
            elif event == 'Send':
                user_input = values['-IN-'].strip()
                if user_input:
                    chatbot_response = self.process_user_input(user_input)
                    print(f'User: {user_input}')                    
                    print(f'Chatbot: {chatbot_response}')
                    self.window['-IN-'].update('')

        self.window.close()

if __name__ == "__main__":
    folder_path = "sample files"
    chatbot = FileBasedChatbot(folder_path)
    chatbot.run()
