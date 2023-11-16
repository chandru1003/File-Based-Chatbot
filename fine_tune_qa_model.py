from transformers import BertTokenizer, BertForQuestionAnswering
from torch.utils.data import DataLoader, Dataset
from transformers import AdamW

class CustomDataset(Dataset):
    def __init__(self, questions, contexts, answers, tokenizer, max_length):
        self.encodings = tokenizer(questions, contexts, truncation=True, padding='max_length', max_length=max_length, return_tensors='pt')
        self.answers = answers

    def __getitem__(self, idx):
        return {key: tensor[idx] for key, tensor in self.encodings.items()}, self.answers[idx]

    def __len__(self):
        return len(self.answers)

questions = ["What is the capital of France?", "Who wrote Hamlet?", ...]
contexts = ["France is a country in Western Europe...", "Hamlet is a tragedy by William Shakespeare...", ...]
answers = ["The capital of France is Paris.", "Hamlet was written by William Shakespeare.", ...]

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertForQuestionAnswering.from_pretrained('bert-base-uncased')

dataset = CustomDataset(questions, contexts, answers, tokenizer, max_length=256)
loader = DataLoader(dataset, batch_size=8, shuffle=True)

optimizer = AdamW(model.parameters(), lr=5e-5)

# Fine-tuning loop
for epoch in range(3):
    for batch in loader:
        inputs, targets = batch
        outputs = model(**inputs, labels=targets)
        loss = outputs.loss
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

# Save the fine-tuned model
model.save_pretrained('fine_tuned_qa_model')
tokenizer.save_pretrained('fine_tuned_qa_model')
