import PySimpleGUI as sg
import pdfplumber
import os
import spacy
from transformers import GPT2LMHeadModel, GPT2Tokenizer

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

    def generate_text_with_gpt2(self, combined_text):
        try:
            input_ids = self.tokenizer.encode(combined_text, return_tensors="pt")
            output = self.model.generate(input_ids, max_length=50, num_return_sequences=1)
            generated_text = self.tokenizer.decode(output[0], skip_special_tokens=True)
            return generated_text
        except Exception as e:
            print(f"An error occurred: {e}")
            return ""
       
    def process_user_input(self, user_input):
        matches = []
        for sentence in self.extracted_text.split('.'):
            if user_input in sentence:
                matches.append(sentence)

        if matches:
            combined_text = ' '.join(matches)
            generated_text = self.generate_text_with_gpt2(combined_text)
            return "Answer found: " + generated_text
        else:
            return "Sorry, I couldn't find an answer related to your query."

    def create_window(self):
        layout = [
            [sg.Text('File-Based Chatbot', font='Any 15')],
            [sg.Output(size=(80, 30), key='-OUTPUT-')],
            [sg.Input(key='-IN-', size=(45, 1), enable_events=True), sg.Button('Send')],
        ]

        self.window = sg.Window('File-Based Chatbot', layout,finalize=True)
        self.window.set_icon('icon\icons8-chat-bot-64.ico')

    def run(self):
        while True:
            try:
                event, values = self.window.read()

                if event == sg.WIN_CLOSED:
                    break
                elif event == 'Send' or (event == '-IN-' and values['-IN-'] == '\r'):
                    user_input = values['-IN-'].strip()

                    print(f'User: {user_input}')
                    chatbot_response = self.process_user_input(user_input)
                    print(f'Chatbot: {chatbot_response}')
                    self.window['-IN-'].update('')  # Clear the input field after processing the input

            except Exception as e:
                print(f"An error occurred: {e}")
             

        self.window.close()

    
    def load_model(self):
        self.tokenizer = GPT2Tokenizer.from_pretrained("distilgpt2")
        self.model = GPT2LMHeadModel.from_pretrained("distilgpt2")
if __name__ == "__main__":
    folder_path = "sample files"
    chatbot = FileBasedChatbot(folder_path)
    chatbot.load_model()
    chatbot.run()
