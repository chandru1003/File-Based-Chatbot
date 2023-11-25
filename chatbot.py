import os
import pdfplumber
from docx import Document
import PySimpleGUI as sg
from transformers import pipeline, T5Tokenizer
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

    def summarize_text(self, combined_text):
        summarization_pipeline = pipeline("summarization", model="t5-base", tokenizer=T5Tokenizer.from_pretrained("t5-base", model_max_length=1024), framework="tf")
        summary = summarization_pipeline(combined_text, max_length=100, min_length=60, do_sample=False)
        return summary[0]['summary_text']

    def search(self, df, query, n=3, pprint=True):
        query_embedding = get_embedding(query, engine="text-embedding-ada-002")
        df["similarity"] = df.embeddings.apply(lambda x: cosine(x, query_embedding))

        results = df.sort_values("similarity", ascending=False, ignore_index=True)
        # make a dictionary of the the first three results with the page number as the key and the text as the value. The page number is a column in the dataframe.
        results = results.head(n)
        sources = []
        for i in range(n):
            # append the page number and the text as a dict to the sources list
            sources.append({"Page " + str(results.iloc[i]["page"]): results.iloc[i]["text"][:150] + "..."})
        return {"results": results, "sources": sources}

    def create_prompt(self, df, user_input):
        print('Creating prompt')
        print(user_input)

        result = self.search(df, user_input, n=3)
        data = result['results']
        sources = result['sources']
        system_role = """You are a AI assistant whose expertise is reading and summarizing doc anf pdf. You are given a query, 
        a series of text embeddings and the title from a paper in order of their cosine similarity to the query. 
        You must take the given embeddings and return a very detailed summary of the paper in the languange of the query:
        """

        user_input = user_input + """
        Here are the embeddings:

        1.""" + str(data.iloc[0]['text']) + """
        2.""" + str(data.iloc[1]['text']) + """
        3.""" + str(data.iloc[2]['text']) + """
        """

        history = [
        {"role": "system", "content": system_role},
        {"role": "user", "content": str(user_input)}]

        print('Done creating prompt')
        return {'messages': history, 'sources': sources}

    def gpt(self, context, source):
        print('Sending request to OpenAI')
        #openai.api_key = os.getenv('apikey')
        r = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=context)
        answer = r.choices[0]["message"]["content"]
        print('Done sending request to OpenAI')
        response = {'answer': answer, 'sources': source}
        return response

    def create_df(self, data):

        if type(data) == list:
            print("Extracting text from pdf")
            print("Creating dataframe")
            filtered_pdf = []
            # print(pdf.pages[0].extract_text())
            for row in data:
                if len(row["text"]) < 30:
                    continue
                filtered_pdf.append(row)
            df = pd.DataFrame(filtered_pdf)
            # remove elements with identical df[text] and df[page] values
            df = df.drop_duplicates(subset=["text", "page"], keep="first")
            # df['length'] = df['text'].apply(lambda x: len(x))
            print("Done creating dataframe")

        elif type(data) == str:
            print("Extracting text from txt")
            print("Creating dataframe")
            # Parse the text and add each paragraph to a column 'text' in a dataframe
            df = pd.DataFrame(data.split("\n"), columns=["text"])

        return df

    def process_user_input(self, user_input):
        if not self.extracted_text:
            return "Please select a folder with documents first."

        # Use Chatbot methods
        documents = [{"text": self.extracted_text}]
        df = self.create_df(documents)
        self.embeddings(df)

        response = self.gpt(context=self.create_prompt(df, user_input))
        return f"Answer found: {response['answer']}"

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
