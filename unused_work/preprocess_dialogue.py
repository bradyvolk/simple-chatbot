import json

def transform_dialogue():
    """
    Transforms raw dialogue to format similar to feedback.json schema
    
    ::dialogue : raw JSON string
    ::output   : raw JSON string
    
    [
    {
      ""
    }
    ]
    
    """  
    with open('dialogue.json', encoding='utf-8') as fh:
        list_of_dialog = json.load(fh)
          
    # list_of_dialog = json.loads(open('dialogue.json').read())
    feedback = []
    
    for dialogue in list_of_dialog:
        
        # print("Dialogue:", dialogue)
        feedback_object = { "conversation": [], "rating": None}
        list_of_responses = dialogue['dialog']

        # Find first human response
        first_h_response_index = None
        i = 0 
        while not first_h_response_index and i < len(list_of_responses):
            if list_of_responses[i]['sender_class'] == 'Human':
                first_h_response_index = i
            i += 1
              
        list_of_responses = list_of_responses[first_h_response_index:]      
        
        expecting_human_response = True
        logged = False
        # Find pairs of human - bot responses
        (human_responses, bot_responses) = "", ""
        for response in list_of_responses:
            logged = False
            if expecting_human_response and response['sender_class'] == 'Human':
                human_responses += " " +  response['text'].strip()
            elif expecting_human_response and response['sender_class'] == 'Bot':
                bot_responses += " " + response['text'].strip()
                expecting_human_response = False
            elif not expecting_human_response and response['sender_class'] == 'Bot':
                bot_responses += " " + response['text'].strip()
            elif not expecting_human_response and response['sender_class'] == 'Human':
                feedback_object['conversation'].append((human_responses.strip(), bot_responses.strip()))
                (human_responses, bot_responses) = response['text'].strip(), ""
                logged = True
        
        if not logged:    
            feedback_object['conversation'].append((human_responses, bot_responses))
        
        feedback_object["rating"] = dialogue["eval_score"]
        feedback.append(feedback_object)
        
    feedback_json = json.dumps(feedback)
    
    with open('processed_training_data.json', 'w') as outfile:
        outfile.write(feedback_json)
        
if __name__ == "__main__":
    transform_dialogue()    