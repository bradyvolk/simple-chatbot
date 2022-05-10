# Simple Chatbot

Empabot is a simple chatbot that uses retrieval responses and generated sequence-to-sequence responses to help college students through emotions.

<br>

## Installation Instructions

Make sure you have python3 installed and install the requirements:

```bash
pip install -r requirements.txt
```

Be sure to download the model.npz for the Seq2Seq model from here (this has to go into the main chatbot folder):
https://drive.google.com/file/d/1tjdcNVQQF_EYwCQ4cA_b6kzGesqzVYv7/view?usp=sharing

<br>

## Running

To train the retrieval model:

```bash
python train_retrieval.py
```

To run Empabot:

```bash
python empabot.py
```
