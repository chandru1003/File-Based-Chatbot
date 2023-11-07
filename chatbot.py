import PySimpleGUI as sg
import pdfplumber
import os
from transformers import GPT2Tokenizer, GPT2LMHeadModel

class FileBasedChatbot:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.extracted_text = self.extract_text_from_pdfs()
        self.load_model()  
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

    def load_model(self):
        self.tokenizer = GPT2Tokenizer.from_pretrained("distilgpt2")
        self.model = GPT2LMHeadModel.from_pretrained("distilgpt2")

    def generate_text_with_gpt2(self, combined_text):
        try:
            self.tokenizer.padding_side = 'left'       
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token        
            encoding = self.tokenizer.encode_plus(
                combined_text,
                return_tensors="pt",
                padding='max_length',  
                truncation=True,  
                max_length=50  
            )
            input_ids = encoding['input_ids']
            attention_mask = encoding['attention_mask']

            max_new_tokens = 50
            output = self.model.generate(
                input_ids,
                attention_mask=attention_mask,
                max_length=len(input_ids[0]) + max_new_tokens, 
                pad_token_id=self.tokenizer.pad_token_id,  
                num_return_sequences=1
            )
            return self.tokenizer.decode(output[0], skip_special_tokens=True)
        except Exception as e:
            print(f"An error occurred: {e}")
            return "An error occurred during text generation."




    def process_user_input(self, user_input):
        matches = [sentence for sentence in self.extracted_text.split('.') if user_input.lower() in sentence.lower()]
        return "Answer found: " + self.generate_text_with_gpt2(' '.join(matches)) if matches else "Sorry, I couldn't find an answer related to your query."

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
                    print(f'User: {user_input}')
                    chatbot_response = self.process_user_input(user_input)
                    print(f'Chatbot: {chatbot_response}')
                    self.window['-IN-'].update('')

        self.window.close()

if __name__ == "__main__":
    folder_path = "sample files"
    chatbot = FileBasedChatbot(folder_path)
    chatbot.run()
