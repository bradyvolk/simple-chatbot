import json

# Data structure to hold user feedback
class Feedback():
  def __init__(self):
    self.conversation = []
    self.rating = None

  def clear_log(self):
    self.conversation = []
    self.rating = None
    
  def log_message(self, msg, res):
    self.conversation.append((msg, res))
    
  def log_rating(self, rating):
      self.rating = rating

  def process_user_feedback(self):
    data_file = open('feedback.json').read()
    feedback = json.loads(data_file)
    if not feedback: feedback = []
    
    new_feedback = {
        "conversation": self.conversation,
        "rating": self.rating
      }
    
    feedback.append(new_feedback)
    feedback_json = json.dumps(feedback)
        
    with open('feedback.json', 'w') as outfile:
      outfile.write(feedback_json)
    
  