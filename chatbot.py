import os
import pdfplumber
from docx import Document
import PySimpleGUI as sg
from transformers import pipeline, T5Tokenizer
from haystack import Pipeline
from haystack.reader.farm import FARMReader
from haystack.retriever.dense import DensePassageRetriever
from haystack.document_store.memory import InMemoryDocumentStore


class FileBasedChatbot:
    def __init__(self):
        self.folder_path = ""
        self.extracted_text = ""
        self.document_store = InMemoryDocumentStore()
        self.reader = FARMReader(model_name_or_path="distilbert-base-uncased-distilled-squad")
        self.retriever = DensePassageRetriever(document_store=self.document_store,
                                               query_embedding_model="facebook/dpr-question_encoder-single-nq-base",
                                               passage_embedding_model="facebook/dpr-ctx_encoder-single-nq-base")
        self.pipeline = Pipeline(reader=self.reader, retriever=self.retriever)

        self.create_window()

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

    def index_documents(self, documents):
        self.document_store.write_documents(documents)

    def summarize_text(self, combined_text):
        summarization_pipeline = pipeline("summarization", model="t5-base", tokenizer=T5Tokenizer.from_pretrained("t5-base", model_max_length=1024), framework="tf")
        summary = summarization_pipeline(combined_text, max_length=100, min_length=60, do_sample=False)
        return summary[0]['summary_text']

    def process_user_input(self, user_input):
        if not self.extracted_text:
            return "Please select a folder with documents first."

        documents = [{"text": self.extracted_text}]
        self.index_documents(documents)

        reader_results = self.pipeline.run(query=user_input, top_k_retriever=5)
        if reader_results["answers"] and reader_results["answers"][0]["probability"] > 0.5:
            return f"Answer found: {reader_results['answers'][0]['answer']}"
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

                chatbot_response = self.process_user_input(user_input)
                print(f'User: {user_input}')
                print(f'Chatbot: {chatbot_response}')
                self.window['-IN-'].update('')

if __name__ == "__main__":
    chatbot = FileBasedChatbot()
    chatbot.run()
