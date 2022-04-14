import feedback
import seq2seq
import retrieval

# Initialize Feedback datastructure
user_feedback = feedback.Feedback()

# Initialize conversation tracker for user feedback
time_since_feedback = 0
is_feedback = False
responses_between_feedback = 5

def generative_response(msg):
    return seq2seq.output(msg)

def chatbot_response(msg):    
    (res1, confidence) = retrieval.get_response(msg)
    if not res1 or confidence < 0.9:
        res2 = generative_response(msg)
        if not res2: return "Sorry, I'm not sure how to respond to that."
        return res2
    return res1

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
                if (rating > 5) and (rating <= 10): empabot_says("Thank you! I'm glad I can help. Anyways, what were you saying?")
                if (rating <= 5) and (rating >= 1): empabot_says("I'm sorry you're not satisfied. I'll work to get better! Anyways, what were you saying?")
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
