import os
import time
import pdfplumber
from docx import Document
import PySimpleGUI as sg
import openai
import pandas as pd
from scipy.spatial.distance import cosine
from openai.embeddings_utils import get_embedding

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

        return extracted_text

    def search(self, df, query, n=3, pprint=True):
        query_embedding = get_embedding(query, engine="text-embedding-ada-002")
        df["similarity"] = df.embeddings.apply(lambda x: cosine(x, query_embedding))

        results = df.sort_values("similarity", ascending=False, ignore_index=True)
        results = results.head(n)
        sources = [{"Page " + str(results.iloc[i]["page"]): results.iloc[i]["text"][:150] + "..."}
                   for i in range(n)]
        return {"results": results, "sources": sources}

    def create_prompt(self, df, user_input):
        print('Creating prompt')
        print(user_input)

        result = self.search(df, user_input, n=3)
        data = result['results']
        sources = result['sources']
        system_role = """Find answer for  given a query"""

        user_input = user_input + """
        Here are the embeddings:

        1. {}\n2. {}\n3. {}
        """.format(data.iloc[0]['text'], data.iloc[1]['text'], data.iloc[2]['text'])

        history = [
            {"role": "system", "content": system_role},
            {"role": "user", "content": str(user_input)}
        ]

        print('Done creating prompt')
        return {'messages': history, 'sources': sources}

    def gpt(self, context, source):
        print('Sending request to OpenAI')
        time.sleep(20)
        #openai.api_key = os.getenv('')
        r = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=context)
        answer = r.choices[0]["message"]["content"]
        print('Done sending request to OpenAI')
        response = {'answer': answer, 'sources': source}
        return response

    def create_df(self, data):
        if type(data) == list:
            print("Extracting text from pdf")
            print("Creating dataframe")
            filtered_pdf = [row for row in data if len(row["text"]) >= 30]
            df = pd.DataFrame(filtered_pdf)
            df["page"] = range(1, len(df) + 1)
            df = df.drop_duplicates(subset=["text", "page"], keep="first")
            print("Done creating dataframe")

        elif type(data) == str:
            print("Extracting text from txt")
            print("Creating dataframe")
            df = pd.DataFrame(data.split("\n"), columns=["text"])

        return df

    def process_user_input(self, user_input):
        if not self.extracted_text:
            return "Please select a folder with documents first."

        documents = [{"text": self.extracted_text}]
        df = self.create_df(documents)
        self.embeddings(df)

        response = self.gpt(context=self.create_prompt(df, user_input))
        return f"Answer found: {response['answer']}"

    def embeddings(self, df):
        print("Calculating embeddings")
        time.sleep(20)
        #openai.api_key = ""
        embedding_model = "text-embedding-ada-002"
        embeddings = df.text.apply(lambda x: get_embedding(x, engine=embedding_model))
        df["embeddings"] = embeddings
        print("Done calculating embeddings")

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
