def refine_question(record, llm_server, current_model):
    """
    Given a record with a previously generated MCQ, this function uses the LLM to refine
    the question according to the user-provided feedback. It sends the original question,
    the image, and the feedback to the LLM and parses the refined response.

    The refined question is returned for visualization only.
    """
    feedback = record.get("feedback", "").strip()
    if not feedback:
        return record  # Nothing to do

    refine_prompt = (
        "The following multiple-choice question was generated from an image:\n"
        f"Question: {record['mc_question']}\n\n"
        f"QUESTION: {record['mc_question']}\n" \
        f"A) {record['mc_options'].get('A', '')}\n" \
        f"B) {record['mc_options'].get('B', '')}\n" \
        f"C) {record['mc_options'].get('C', '')}\n" \
        f"D) {record['mc_options'].get('D', '')}\n" \
        f"E) {record['mc_options'].get('E', '')}\n" \
        f"F) {record['mc_options'].get('F', '')}\n\n"

        "User feedback to refine the question:\n"
        f"{feedback}\n\n"
        "------------------------------------------------------------\n"
        "Role: You are an advanced AI model with deep expertise in urban studies. Your task is to analyze a Street View image (provided separately) and  examine the provided Street View image meticulously and the user feedback. "
        "The refined question must follow those costrain"
        "**Constraints:**\n"
        "1. **Directly Observable:** The question and its answer choices MUST be answerable solely from the information visible in the provided image. Do not assume or introduce any information that is not directly observable.\n"
        "2. **Image-Dependent:** The question must require examination of the image to determine the correct answer; the image is essential for answering the question.\n"
        "3. **Challenging:** The question should require careful observation and analysis, going beyond a superficial description.\n"
        "4. **Unambiguous Correct Answer:** There must be exactly one answer that is definitively correct based solely on the image.\n"
        "5. **Clear Reasoning:** Provide a brief explanation of why the chosen answer is correct, referencing specific elements in the image, and also explain why the other options are incorrect (including clearly identifying which option is the absurdum).\n\n"
        "YOUR OUTPUT MUST FOLLOW THIS STRUCTURE, otherwise we will not be able to parse it and we will get an error\n"
        "**Output Format:**\n"
        "QUESTION: [Your question text]\n"
        "A) [Option 1]\n"
        "B) [Option 2]\n"
        "C) [Option 3]\n"
        "D) [Option 4]\n"
        "E) [Option 5]\n"
        "F) [Option 6]\n"
        "CORRECT_ANSWER: [A, B, C, D, E, or F]\n"
        "REASON: [Short explanation of why the answer is correct (referencing specific visual elements in the image), and why the other options are incorrect, including which option is the absurdum.]\n"
        "------------------------------------------------------------\n\n"
        "IMPORTANT: Based on the user feedback, update only the specific elements requested. For example, if the feedback says 'give me a new option C' or 'make options A and D more relevant', then change only those parts and leave all other components (the remaining answer choices, the question text, the correct answer, and the reasoning) unchanged. If the feedback requests a change in focus (e.g., to emphasize urban accessibility), adjust the entire question accordingly while still preserving the original format and criteria.\n\n"
        "Please refine the question accordingly. Your refined question must strictly adhere to the following prompt instructions and output format:\n\n"

    )


    refined_response = llm_server.send_query(
        image_path=record["image_path"],
        prompt=refine_prompt,
        model=current_model
    )
    print(f"i am refining following this user request: {feedback}")

    # Parse the refined response (similar to the original parsing)
    lines = refined_response.splitlines()
    refined_mc_question = None
    refined_mc_options = {"A": "", "B": "", "C": "", "D": "", "E": "", "F": ""}
    refined_mc_correct = "?"
    refined_mc_reason = ""

    for ind, line in enumerate(lines):
        line_strip = line.strip()
        lcase = line_strip.lower()

        if lcase.startswith("question:"):
            refined_mc_question = line_strip.split(":", 1)[1].strip()
        elif lcase.startswith("a)"):
            refined_mc_options["A"] = line_strip[2:].strip()
        elif lcase.startswith("b)"):
            refined_mc_options["B"] = line_strip[2:].strip()
        elif lcase.startswith("c)"):
            refined_mc_options["C"] = line_strip[2:].strip()
        elif lcase.startswith("d)"):
            refined_mc_options["D"] = line_strip[2:].strip()
        elif lcase.startswith("e)"):
            refined_mc_options["E"] = line_strip[2:].strip()
        elif lcase.startswith("f)"):
            refined_mc_options["F"] = line_strip[2:].strip()
        elif lcase.startswith("correct_answer:"):
            chunk = line_strip.split(":", 1)[1].strip()
            if chunk and chunk[0].upper() in ["A", "B", "C", "D", "E", "F"]:
                refined_mc_correct = chunk[0].upper()
        elif lcase.startswith("reason:"):
            refined_mc_reason = "\n".join(lines[ind:])
            break

    # For visualization only, we return a dictionary with the refined fields.
    return {
        "mc_question": refined_mc_question,
        "mc_options": refined_mc_options,
        "mc_correct": refined_mc_correct,
        "mc_reason": refined_mc_reason
    }

def build_refinement_prompt(record, refined_record):
    """
    Build a refinement prompt that instructs the LLM to make only the minimal changes
    requested by the user.

    It uses:
      - The original MCQ (stored in record["original_mcq"] or record["mc_question"] if missing)
      - The current refined MCQ (from refined_record)
      - The user feedback (record["feedback"])

    Returns a string prompt.
    """
    original_question = record.get("original_mcq", record.get("mc_question", ""))
    original_options = record.get("original_options", {
        "A": record.get("mc_options", {}).get("A", ""),
        "B": record.get("mc_options", {}).get("B", ""),
        "C": record.get("mc_options", {}).get("C", ""),
        "D": record.get("mc_options", {}).get("D", ""),
        "E": record.get("mc_options", {}).get("E", ""),
        "F": record.get("mc_options", {}).get("F", ""),
    })
    # If you haven't stored original options separately, you could store them at first refinement.
    # For now we assume original_options is available in record or defaults to the current ones.

    refined_question = refined_record.get("mc_question", "")
    refined_options = refined_record.get("mc_options", {"A": "", "B": "", "C": "", "D": "", "E": "", "F": ""})
    refined_correct = refined_record.get("mc_correct", "?")
    refined_reason = refined_record.get("mc_reason", "")
    user_feedback = record.get("feedback", "").strip()

    prompt = (
        "You are an advanced AI model tasked with refining a multiple-choice question (MCQ) based on specific user feedback.\n\n"
        "IMPORTANT:\n"
        "- If the user feedback only specifies changes for a particular option (e.g., 'change option A to ...'), make only that change and leave all other parts unchanged.\n"
        "- If the user feedback requests a completely new or 'better' question, then change the entire MCQ.\n"
        "- If the user feedback asks to modify the question text itself, change only the question text.\n"
        "- Always output the final MCQ in the following structured format exactly:\n\n"
        "QUESTION: [Refined question text]\n"
        "A) [Option A]\n"
        "B) [Option B]\n"
        "C) [Option C]\n"
        "D) [Option D]\n"
        "E) [Option E]\n"
        "F) [Option F]\n"
        "CORRECT_ANSWER: [A, B, C, D, E, or F]\n"
        "REASON: [Short explanation]\n\n"
        "Here is the current MCQ information:\n\n"
        "Original MCQ:\n"
        f"Question: {original_question}\n"
        f"A) {original_options.get('A', '')}\n"
        f"B) {original_options.get('B', '')}\n"
        f"C) {original_options.get('C', '')}\n"
        f"D) {original_options.get('D', '')}\n"
        f"E) {original_options.get('E', '')}\n"
        f"F) {original_options.get('F', '')}\n\n"
        "Refined MCQ so far:\n"
        f"Question: {refined_question}\n"
        f"A) {refined_options.get('A', '')}\n"
        f"B) {refined_options.get('B', '')}\n"
        f"C) {refined_options.get('C', '')}\n"
        f"D) {refined_options.get('D', '')}\n"
        f"E) {refined_options.get('E', '')}\n"
        f"F) {refined_options.get('F', '')}\n"
        f"Correct Answer: {refined_correct}\n"
        f"Reason: {refined_reason}\n\n"
        "User Feedback:\n"
        f"{user_feedback}\n\n"
        "Your task: Based on the user feedback, make only the minimal changes necessary to satisfy the feedback. "
        "Leave any parts not mentioned in the feedback exactly as they are.\n\n"
        "Please output the updated MCQ in the exact structured format above."
    )
    return prompt

def iterative_refinement(record, llm_server, current_model, max_iterations=5):
    """
    Iteratively refines the MCQ until the LLM confirms that the user feedback is satisfied
    or until max_iterations is reached.
    If the refined question text remains identical to the original, append an instruction
    to force a complete change.

    Returns a tuple (final_record, warning).
    """
    iteration = 0
    warning = ""

    # Save the original MCQ if not already stored.
    if "original_mcq" not in record:
        record["original_mcq"] = record.get("mc_question", "")
        # Optionally, store the original options as well:
        record["original_options"] = record.get("mc_options", {}).copy()

    refined_record = refine_question(record, llm_server, current_model)

    while iteration < max_iterations:
        # Compare refined question with the original.
        if (refined_record.get("mc_question") or "").strip() == (record.get("original_mcq") or "").strip():
            record["feedback"] += "\nNote: The question text is identical to the original. Please create a completely new question that addresses the user feedback."

        # Build the validation prompt using the helper.
        validation_prompt = build_refinement_prompt(record, refined_record)

        # Query the LLM for validation, passing the image context.
        validation_response = llm_server.send_query(
            image_path=record["image_path"],
            prompt=validation_prompt,
            model=current_model
        )

        if validation_response.strip().lower().startswith("yes"):
            break  # The refined MCQ now satisfies the feedback.
        else:
            record["feedback"] += "\nAdditional refinement needed: " + validation_response.strip()
            refined_record = refine_question(record, llm_server, current_model)
            iteration += 1
            #print(f"iteration in iterative_refinement n= {iteration}")

    if iteration == max_iterations:
        warning = "Warning: The model could not fully satisfy the requested modifications. (This is just a model—maybe try skipping this question.)"
        refined_record["mc_reason"] += "\n" + warning

    return refined_record, warning
