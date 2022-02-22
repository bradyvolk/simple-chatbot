import time
import nltk
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import pickle
import numpy as np
import feedback

from keras.models import load_model
model = load_model('chatbot_model.h5')
import json
import random
intents = json.loads(open('intents.json').read())
words = pickle.load(open('words.pkl','rb'))
classes = pickle.load(open('classes.pkl','rb'))


def clean_up_sentence(sentence):
    # tokenize the pattern - split words into array
    sentence_words = nltk.word_tokenize(sentence)
    # stem each word - create short form for word
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence

def bow(sentence, words, show_details=True):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0]*len(words)  
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s: 
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % w)
    return(np.array(bag))

def predict_class(sentence, model):
    # filter out predictions below a threshold
    p = bow(sentence, words, show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list

# create a data structure to hold user context
context = {}

# Initialize Feedback datastructure
user_feedback = feedback.Feedback()

# Initialize conversation tracker for user feedback
time_since_feedback = 0
is_feedback = False
responses_between_feedback = 5

# show_details is for debugging purposes
def getResponse(ints, intents_json, userID='123', show_details=False):
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        # if highest probability intent matches tag in intents.json
        if (i['tag'] == tag):
            # set context for this intent if context exists
            if 'context_set' in i:
                if show_details: print('context:', i['context_set'])
                context[userID] = i['context_set']

            # check if this intent is contextual and applies to this user's conversation
            if not 'context_filter' in i or \
                (userID in context and 'context_filter' in i and i['context_filter'] == context[userID]):
                if show_details:
                    print('-------------------')
                    print('tag:', i['tag'])
                    print('ints:', ints)
                    print('userID:', userID)
                    print('context:', context)
                    print('-------------------')
                # a random response from the intent
                result = random.choice(i['responses'])
            result = random.choice(i['responses'])
            break
    return result

def chatbot_response(msg):    
    # ints is a list with intent/tag and its probability
    ints = predict_class(msg, model) # example is [{'intent': 'greeting', 'probability': '0.999597'}]
    res = getResponse(ints, intents, show_details=True)
    return res


# Creating GUI with tkinter
import tkinter
from tkinter import *

def user_says(msg, tag=None):
    ChatLog.insert(END, "You: " + msg + "\n\n", tag)
    
def empabot_says(msg, tag=None):
    ChatLog.insert(END, "EmpaBot: " + msg + "\n\n", tag)

def send(event=None):
    global is_feedback, time_since_feedback, user_feedback
    msg = EntryBox.get("1.0", 'end-1c').strip()
    EntryBox.delete("1.0", END)

    if msg != '':
        ChatLog.config(state=NORMAL)

        # Parse user feedback
        if is_feedback:
            user_says(msg)
            try:
                rating = int(msg)
                if (rating > 5) and (rating <= 10): empabot_says("Thank you! I'm glad I can help.")
                if (rating <= 5) and (rating >= 1): empabot_says("I'm sorry you're not satisfied. I'll work to get better!")
                user_feedback.log_rating(rating)
                user_feedback.process_user_feedback()
                user_feedback.clear_log()
                is_feedback = False
            except ValueError:
                empabot_says("Oh sorry, can you please enter a number between 1 and 10!")
                
        # Handle normal Response
        else:
            ChatLog.insert(END, "You: " + msg + '\n\n')
            ChatLog.config(foreground="#2a4d69", font=("Lato", 12))
        
            res = chatbot_response(msg)
            ChatLog.insert(END, "EmpaBot: " + res + '\n\n')
            
            user_feedback.log_message(msg, res)
            time_since_feedback += 1
            
            # Check if we need to ask for feedback
            if time_since_feedback - 10 >= responses_between_feedback:
                time_since_feedback = 0
                empabot_says("EmpaBot: Would you please rate how I'm doing on a scale from 1 (the worst) to 10 (the best)?", "feedback")
                is_feedback = True
            
        ChatLog.config(state=DISABLED)
        ChatLog.yview(END)
    return 'break'
 

base = Tk()
base.title("Chat with EmpaBot!")
base.geometry("400x500")
base.resizable(width=FALSE, height=FALSE)
 
#Create Chat window
ChatLog = Text(base, highlightthickness=0, bd=0, bg="white", height="8", width="50", font="Lato")
ChatLog.tag_config('feedback', background="#e8f1ff", foreground="#406bad")


ChatLog.config(state=DISABLED)

#Bind scrollbar to Chat window
scrollbar = Scrollbar(base, command=ChatLog.yview, cursor="heart")
ChatLog['yscrollcommand'] = scrollbar.set

# #Create Button to send message
SendButton = Button(base, font=("Lato", 14, 'bold'), text="Send", width="12", height="5",
                    highlightthickness=0, bd=0, bg="#2a4d69", activebackground="#2a4d69", fg='#2a4d69',
                    command=send)

#Create the box to enter message
EntryBox = Text(base, highlightthickness=0, bd=0, bg="white", width="29", height="5", font="Lato")
EntryBox.bind("<Return>", send)

#Place all components on the screen
scrollbar.place(x=376, y=6, height=426)
ChatLog.place(x=6, y=6, height=426, width=370)
EntryBox.place(x=128, y=441, height=50, width=265)
SendButton.place(x=13, y=441, height=50, width=108)

base.mainloop()
