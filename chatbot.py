import os
import time
import pdfplumber
from docx import Document
import PySimpleGUI as sg
import openai
import pandas as pd


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
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            extracted_texts.append(text)

        extracted_text = "\n".join(extracted_texts)
        with open("extracted_text.txt", "w", encoding="utf-8") as text_file:
            text_file.write(extracted_text)

        return extracted_text

    def search_for_answer(self, df, query, n=3):
        df["similarity"] = df.text.apply(lambda x: self.calculate_similarity(x, query))
        results = df.sort_values("similarity", ascending=False, ignore_index=True)

        # Ensure that the number of results is not greater than the length of the DataFrame
        num_results = min(n, len(results))
    
        sources = [{"Page " + str(results.iloc[i]["page"]): results.iloc[i]["text"][:150] + "..."}
            for i in range(num_results)]
    
        return {"results": results, "sources": sources}

    def calculate_similarity(self, text, query):
        # You can use a similarity metric here (e.g., cosine similarity)
        # For simplicity, let's just compare the length of the common words
        common_words = set(text.split()) & set(query.split())
        similarity = len(common_words) / max(len(set(text.split())), len(set(query.split())))
        return similarity

    def create_prompt(self, df, user_input):
       # print('Creating prompt')
        print(user_input)

        result = self.search_for_answer(df, user_input, n=3)
        data = result['results']
        sources = result['sources']
        system_role = """Find an answer for the given query"""

        user_input_lines = [user_input, "Here are the potential answers:"]

        # Check if there are enough rows in the DataFrame before accessing specific indices
        if len(data) > 0:
            user_input_lines.append(f"1. {data.iloc[0]['text']}")

        if len(data) > 1:
            user_input_lines.append(f"2. {data.iloc[1]['text']}")

        if len(data) > 2:
            user_input_lines.append(f"3. {data.iloc[2]['text']}")

        user_input = "\n".join(user_input_lines)

        history = [
            {"role": "system", "content": system_role},
            {"role": "user", "content": user_input}
        ]

       # print('Done creating prompt')
        return {'messages': history, 'sources': sources}


    def gpt(self, context, source):
        #print('Sending request to OpenAI')
        time.sleep(20)
        
        #openai.api_key = '<api_key>'
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=context,
                source=source,
                log_level="info"  # Request log information
            )

            # Extract the token usage from the API response
            usage = response['usage']['total_tokens']
            #print(f'Tokens used: {usage}')

            answer = response.choices[0]["message"]["content"]
            #print('Done sending request to OpenAI')
            return {'answer': answer, 'sources': source, 'tokens_used': usage}

        except openai.error.OpenAIError as e:
            print(f'Error from OpenAI: {e}')
            return {'error': str(e)}


    def create_df(self, data):
        if type(data) == list:
            #print("Creating dataframe")
            df = pd.DataFrame(data, columns=["text"])
            df["page"] = range(1, len(df) + 1)
            df = df[df["text"].apply(lambda x: len(x) >= 30)].drop_duplicates(subset=["text", "page"], keep="first")
            #print("Done creating dataframe")

        elif type(data) == str:
            #print("Creating dataframe")
            df = pd.DataFrame(data.split("\n"), columns=["text"])

        return df

    def process_user_input(self, user_input):
        if not self.extracted_text:
            return "Please select a folder with documents first."

        documents = [{"text": self.extracted_text}]
        df = self.create_df(documents)

        prompt_response = self.create_prompt(df, user_input)
        context = prompt_response['messages']
        source = prompt_response['sources']

        # Call OpenAI API
        response = self.gpt(context=context, source=source)

        if 'error' in response:
            # Handle API error
            return f"Error from OpenAI: {response['error']}"
        elif 'answer' in response:
            # Display the answer
            return f"Answer found: {response['answer']}"
        else:
            # Unexpected response format
            return "Unexpected response from OpenAI."

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

                chatbot_response = self.process_user_input(user_input)
                print(f'User: {user_input}')
                print(f'Chatbot: {chatbot_response}')
                self.window['-IN-'].update('')

if __name__ == "__main__":
    chatbot = FileBasedChatbot()
    chatbot.run()
