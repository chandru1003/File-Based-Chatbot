import os
import pdfplumber
from docx import Document
import PySimpleGUI as sg
import google.generativeai as genai

genai.configure(api_key=os.getenv("Apikey"))

class FileBasedChatbot:
    def __init__(self):
        self.folder_path = ""
        self.extracted_text = ""
        self.create_window()

    def create_window(self):
        layout = [
            [sg.Text('File-Based Chatbot', font='Any 15')],
            [sg.Text('Folder Path:'), sg.Input(key='-FOLDER_PATH-', size=(50, 1)), sg.FolderBrowse()],
            [sg.Output(size=(80, 30), key='-OUTPUT-')],
            [sg.Input(key='-IN-', size=(70, 1)), sg.Button('Send', bind_return_key=True)]
        ]
        self.window = sg.Window('File-Based Chatbot', layout, finalize=True)
        self.window.set_icon('icon\icons8-chat-bot-64.ico')

    def extract_text_from_documents(self):
        extracted_texts = []

        for filename in os.listdir(self.folder_path):
            file_path = os.path.join(self.folder_path, filename)

            if filename.endswith((".pdf", ".doc", ".docx")):
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
        with open("extracted_text.txt", "w", encoding="utf-8") as text_file:
            text_file.write(extracted_text)
        print("extracted...")
        self.extracted_text = extracted_text
        return extracted_text
    
    def get_gemini_response(self, extracted_text, question):
        prompt = f"Answer the question from the extracted text, question is: {question} and extracted text is {extracted_text}"
        model = genai.GenerativeModel('gemini-pro-vision')
        response = model.generate_content([prompt])
        return response.text

    def run(self):
        print("Running...")
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

                chatbot_response = self.get_gemini_response(self.extracted_text, user_input)
                print(f'User: {user_input}')
                print(f'Chatbot: {chatbot_response}')
                self.window['-IN-'].update('')

if __name__ == "__main__":
    chatbot = FileBasedChatbot()
    chatbot.run()
