# File-Based Chatbot: Answering Questions from Documents
 This project is designed to extract text from  PDF file within a specified folder path and generate responses to user-input questions using natural language processing (NLP) techniques.

## Overview
<p>This is a simple File-Based Chatbot built using Python and various libraries such as PySimpleGUI, pdfplumber, transformers, and docx. The chatbot analyzes text data extracted from PDFs and Word documents in a specified folder and responds to user queries.</p>

## Features
- Extracts text data from PDF and Word documents.
- Summarizes extracted text using the T5 transformer model.
- Provides answers to user questions using the Question-Answering (QA) transformer model.

## Requirements
To run this project, ensure you have the following installed:

- Python 3.x
- Required Python libraries: <b>PySimpleGUI, pdfplumber,python-docx,transformers </b>

## Notes
- The summarization model uses the T5 transformer with a predefined configuration.
- The question-answering model is a pretrained model from the Hugging Face transformers library.
- The chatbot considers the context of the extracted text for both summarization and question-answering.

# License
This project is licensed under the [MIT License](https://opensource.org/license/mit/) - see the LICENSE file for details.