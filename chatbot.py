import PySimpleGUI as sg
import pdfplumber
import os
from transformers import pipeline, AutoModel, AutoTokenizer
from docx import Document
import subprocess

# Clone the GitHub repository
repo_url = "https://github.com/patil-suraj/question_generation.git"
clone_folder = "question_generation"
if not os.path.exists(clone_folder):
    subprocess.run(["git", "clone", repo_url, clone_folder])

import sys
sys.path.append(clone_folder)

from pipelines import pipeline
class FileBasedChatbot:
    def __init__(self):
        self.folder_path = ""
        self.create_window()
        self.model_name = "valhalla/t5-base-qg-hl"
        self.model = AutoModel.from_pretrained(self.model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)        
        self.question_answering_pipeline = pipeline("question-generation", model=self.model_name)
      

    def extract_text_from_documents(self):
        extracted_texts = []

        for filename in os.listdir(self.folder_path):
            file_path = os.path.join(self.folder_path, filename)

            if filename.endswith(".pdf"):
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            extracted_texts.append(text)

            elif filename.endswith((".doc", ".docx")):
                doc = Document(file_path)
                paragraphs = [paragraph.text for paragraph in doc.paragraphs]
                text = "\n".join(paragraphs)
                if text:
                    extracted_texts.append(text)

        extracted_text = "\n".join(extracted_texts)   

    '''def summarize_text(self, combined_text):        
        summary = self.summarization_pipeline(combined_text, max_length=100, min_length=60, do_sample=False)
        return summary[0]['summary_text']'''

  
    def process_user_input(self, user_input):
        answer = self.question_answering_pipeline(question=user_input, context=self.extracted_text)
   
        if answer['score'] > 0.5:
            return f"Answer found: {answer['answer']}"
        else:
            return "Sorry, I couldn't find an answer related to your query."

    def create_window(self):
        layout = [
            [sg.Text('File-Based Chatbot', font='Any 15')],
            [sg.Text('Folder Path:'), sg.Input(key='-FOLDER_PATH-', size=(50, 1)), sg.FolderBrowse()],
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
                self.folder_path = values['-FOLDER_PATH-']
                if user_input and self.folder_path:
                    self.extracted_text = self.extract_text_from_documents()
                    chatbot_response = self.process_user_input(user_input)
                    print(f'User: {user_input}')                    
                    print(f'Chatbot: {chatbot_response}')
                    self.window['-IN-'].update('')

        self.window.close()

if __name__ == "__main__":
    chatbot = FileBasedChatbot()
    chatbot.run()







