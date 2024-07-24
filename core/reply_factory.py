
from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")
    if not current_question_id:
        bot_responses.append(BOT_WELCOME_MESSAGE)

    success, error = record_current_answer(message, current_question_id, session)

    if not success:
        return [error]

    next_question, next_question_id = get_next_question(current_question_id)

    if next_question:
        bot_responses.append(next_question)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses


def record_current_answer(answer, current_question_id, session):
    '''
    Validates and stores the answer for the current question to django session.
    '''

    if current_question_id is None:
        return False, "No current question ID found."

    # Validate the answer
    if not isinstance(answer, str) or not answer.strip():
        return False, "Invalid answer. Please provide a non-empty response."

    # Store the answer in the session
    answers = session.get("answers", {})
    answers[current_question_id] = answer.strip()  # Store the answer by question ID
    session["answers"] = answers  # Update the session with new answers
    session.save()

    return True, ""


def get_next_question(current_question_id):
    '''
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_id.
    '''
    # Find the index of the current question
    question_list_length = len(PYTHON_QUESTION_LIST)
    if current_question_id is None:
        # Start with the first question if no current ID is set
        return PYTHON_QUESTION_LIST[0][1], PYTHON_QUESTION_LIST[0][0]

    for index, (question_id, question_text) in enumerate(PYTHON_QUESTION_LIST):
        if question_id == current_question_id:
            next_index = index + 1
            if next_index < question_list_length:
                next_question_id, next_question_text = PYTHON_QUESTION_LIST[next_index]
                return next_question_text, next_question_id
            else:
                # If there is no next question, return None
                return None, None
    
    # Return None if current_question_id wasn't found
    return None, None


def generate_final_response(session):
    '''
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    '''
    
    answers = session.get("answers", {})

    # Assume there's a dictionary with correct answers for each question ID
    correct_answers = {
        1: "A",
        2: "B",
        3: "C",
        # ... (populate with actual correct answers)
    }

    # Calculate score
    score = 0
    total_questions = len(PYTHON_QUESTION_LIST)
    
    for question_id, correct_answer in correct_answers.items():
        user_answer = answers.get(question_id)
        if user_answer and user_answer.lower() == correct_answer.lower():
            score += 1

    # Generate result message
    result_message = f"You have completed the quiz! Your score is {score}/{total_questions}."

    return result_message
