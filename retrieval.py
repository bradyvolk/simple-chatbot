import nltk
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import pickle, json, random
import numpy as np

from keras.models import load_model
model = load_model('chatbot_model.h5')

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

def parse_inference(ints, intents_json, msg, userID='123', show_details=False):
    result = ("", 0)
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for intent in list_of_intents:
        # if highest probability intent matches tag in intents.json
        if (intent['tag'] == tag):
            # set context for this intent if context exists
            if 'context_set' in intent:
                if show_details: print('context:', intent['context_set'])
                context[userID] = intent['context_set']

            # check if this intent is contextual and applies to this user's conversation
            if not 'context_filter' in intent or \
                (userID in context and 'context_filter' in intent and intent['context_filter'] == context[userID]):
                if show_details:
                    print('-------------------')
                    print('tag:', intent['tag'])
                    print('ints:', ints)
                    print('userID:', userID)
                    print('context:', context)
                    print('-------------------')
                # a random response from the intent
                result = (random.choice(intent['responses']), float(ints[0]["probability"]))   
            result = (random.choice(intent['responses']), float(ints[0]["probability"]))
            break
    return result
  
def get_response(msg):
    # ints is a list with intent/tag and its probability
    ints = predict_class(msg, model) # example is [{'intent': 'greeting', 'probability': '0.999597'}]
    return parse_inference(ints, intents, msg, show_details=True)
  
