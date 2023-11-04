import PySimpleGUI as sg
import pdfplumber
import os
import spacy
from colorama import Fore ,Style


class FileBasedChatbot:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.extracted_text = self.extract_text_from_pdfs()
        self.nlp = spacy.load("en_core_web_sm")
        self.create_window()

    def extract_text_from_pdfs(self):
        extracted_text = ""
        for filename in os.listdir(self.folder_path):
            if filename.endswith(".pdf"):
                 with pdfplumber.open(os.path.join(self.folder_path, filename)) as pdf:
                    for page in pdf.pages:
                        extracted_text += page.extract_text()
        with open("extracted_text.txt", "w", encoding="utf-8") as text_file:
            text_file.write(extracted_text)           
        return extracted_text

    def process_user_input(self, user_input):
        matches = []
        for sentence in self.extracted_text.split('.'):
            if user_input in sentence:
                matches.append(sentence)
        
        nlp_matches = self.nlp(' '.join(matches))

        if matches:
            return "Answer found: " + str(nlp_matches)
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
                '''sg.Print('User: ', text_color='red')
                sg.Print(user_input)
                sg.Print('Chatbot: ', text_color='red')
                sg.Print(chatbot_response) 
                print(Fore.RED + 'User:')
                print(f'{Fore.RED}User:{Style.RESET_ALL} {user_input}')
                print(f'{Fore.RED}Chatbot:{Style.RESET_ALL} {chatbot_response}')'''
                
                print(f'User: {user_input}')
                print(f'Chatbot: {chatbot_response}')
                self.window['-IN-'].update('')  # Clear the input field after processing the input

        self.window.close()

if __name__ == "__main__":
    folder_path = "sample files"
    chatbot = FileBasedChatbot(folder_path)
    chatbot.run()
