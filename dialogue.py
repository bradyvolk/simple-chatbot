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
    list_of_dialog = json.loads(open('dialogue.json').read())
    feedback = []
    
    for dialogue in list_of_dialog:
        
        print("Dialogue:", dialogue)
        feedback_object = { "conversation": [], "rating": None}
        list_of_responses = dialogue['dialogue']

        # Find first human response
        first_h_response_index = None
        i = 0 
        while (not first_h_response_index):
            if list_of_responses[i]['sender_class'] == 'Human':
                first_h_response_index = i
            i += 1
              
        list_of_responses = list_of_responses[first_h_response_index:]      
        
        expecting_human_response = True
        # Find pairs of human - bot responses
        for i in range(len(list_of_responses)):
            (human_responses, bot_responses) = "", ""
            if expecting_human_response and list_of_responses[i]['sender_class'] == 'Human':
                human_responses += list_of_responses[i]['text']
            elif expecting_human_response and list_of_responses[i]['sender_class'] == 'Bot':
                bot_responses += list_of_responses[i]['text']
                expecting_human_response = False
            elif not expecting_human_response and list_of_responses[i]['sender_class'] == 'Bot':
                bot_responses += list_of_responses[i]['text']
            else:
                feedback_object['conversation'].append((human_responses, bot_responses))
                (human_responses, bot_responses) = "", ""
        
        feedback_object["rating"] = dialogue["eval_score"]
        feedback.append(feedback_object)
        print(feedback_object, feedback)
        
if __name__ == "__main__":
    transform_dialogue()    