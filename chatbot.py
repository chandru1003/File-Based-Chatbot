import PySimpleGUI as sg
import pdfplumber
import os
from transformers import pipeline, T5Tokenizer
from docx import Document

class FileBasedChatbot:
    def __init__(self):
        self.folder_path = ""
        self.create_window()
        self.summarization_pipeline = pipeline("summarization", model="t5-base", tokenizer=T5Tokenizer.from_pretrained("t5-base", model_max_length=1024), framework="tf")
        self.qa_pipeline = pipeline("question-answering")  

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

        return extracted_text   


    def summarize_text(self, combined_text):        
        summary = self.summarization_pipeline(combined_text, max_length=100, min_length=60, do_sample=False)
        return summary[0]['summary_text']

    def process_user_input(self, user_input):
        answer = self.qa_pipeline(question=user_input, context=self.extracted_text)

        if answer['score'] > 0.5:
            return f"Answer found: {answer['answer']}"
        else:
            matches = [sentence for sentence in self.extracted_text.split('.') if user_input.lower() in sentence.lower()]
            return "Answer found: " + self.summarize_text(' '.join(matches)) if matches else "Sorry, I couldn't find an answer related to your query."

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
                new_folder_path = values['-FOLDER_PATH-']

                if new_folder_path:
                    self.folder_path = new_folder_path                    
                    self.extracted_text = self.extract_text_from_documents()

                if user_input and self.folder_path:
                    chatbot_response = self.process_user_input(user_input)
                    print(f'User: {user_input}')
                    print(f'Chatbot: {chatbot_response}')
                    self.window['-IN-'].update('')

if __name__ == "__main__":
    chatbot = FileBasedChatbot()
    chatbot.run()
