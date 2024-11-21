from langchain.prompts import PromptTemplate

# Preprocessor Agent Prompt
preprocessor_prompt_template = PromptTemplate(
    template="""
    You have to fetch the first few elements from a file json file. 
    The file is located at {file_path}.
    The first few lines of the file are:
    {first_few_lines}
    User information about the data: {user_info_about_data}

    Provide instructions on how to save the first few elements of the file in a list of dictionaries as {first_few_elements_path_name} using Python.
    NOTE: keep in mind possible data types and structures in the file. Address structure, fields, and any other relevant information code generation agent might need to know.
    Your instructions will be given to a Python code generation agent to write code.

    Steps:
    1. Read the JSON file from path {file_path}.
    2. Extract the first few elements from the file.
    3. Save the extracted elements in a list of dictionaries.
    4. Always include print statements to log each step.
    5. Save the list of dictionaries in a new file with path {first_few_elements_path_name}.
    6. Always use os module to handle file paths.
    """,
    input_variables=["file_path", "first_few_lines", "user_info_about_data", "first_few_elements_path_name"],
)


# Code Generation Agent Prompt (ensuring consistent use of triple backticks)
code_generation_prompt_template = PromptTemplate(
    template="""
    You are a Python code generation agent. Your goal is to generate fully executable Python code based on the given task.
    
    Requirements:
    - The code must include all necessary imports, functions, and main logic.
    - You must return ONLY Python code wrapped in **triple backticks (```)**.
    - Do NOT include the word 'python' or any other text inside the triple backticks—just the code itself.
    - Do NOT use single backticks or any other format. ONLY triple backticks (```) should be used.
    - The response must be ONLY the code. No explanations, comments, alternative solutions, or unnecessary newlines.
    - Ensure that the code is concise, correct, and optimized for readability.

    First few lines of the file:
    {first_few_lines}

    User information about the data: {user_info_about_data}
    import json file path: {file_path}

    Instructions:
    {instructions_to_code}

    Task: Extract the first few elements from a JSON file and save them in a list of dictionaries in {first_few_elements_path_name} file.
    
    """,
    input_variables=["first_few_lines", "user_info_about_data", "file_path", "instructions_to_code", "first_few_elements_path_name"],
)

# Enhanced Code Review Agent Prompt with Initial Request Check
code_review_prompt_template = PromptTemplate(
    template="""
    You are a code review agent. Your goal is to review Python code and determine whether it is correct, fully executable, and whether it solves the initial request.

    Guidelines:
    - If the input contains anything other than Python code (e.g., comments, backticks, markdown syntax), return the comment 'incorrect' and a message stating the issue.
    - If the code is correct, return the comment 'correct' and message as why you evaluated that the code is correct.
    - If the code has issues (e.g., syntax errors, missing imports, inefficient logic), return the comment 'incorrect' with a message suggesting how to fix the code.
    - If the code does not appear to solve the initial request, return 'incorrect' with a message that the code doesn't solve the task.

    Few-shot examples:

    Example 1:
    Initial Request: Calculate the sum of two numbers.
    Code: 
    def add(a, b):
        return a + b
    Review:
    comment: correct
    message: Code correctly calculates the sum of two numbers. It does not contain backticks or markdown syntax and is fully executable. It solves the initial request.

    Example 2:
    Initial Request: Multiply two numbers.
    Code:
    def multiply(a, b):
    return a * b  # IndentationError: expected an indented block
    Review:
    comment: incorrect
    message: Syntax Error: IndentationError on line 2, expected an indented block.

    Example 3:
    Initial Request: Divide two numbers.
    Code: 
    ```python
    def divide(a, b):
        return a / b
    ```
    Review:
    comment: incorrect
    message: Non-code content detected: backticks and markdown-style formatting are not allowed.

    Example 4:
    Initial Request: Calculate the factorial of a number.
    Code:
    def add(a, b):
        return a + b
    Review:
    comment: incorrect
    message: The code does not appear to solve the initial request to calculate the factorial.

    Python Code to Review:
    {extracted_python_code}

    Initial Request:
    Follow these Steps:
    1. Read the JSON file from path {file_path}.
    2. Extract the first few elements from the file.
    3. Save the extracted elements in a list of dictionaries.
    4. Always include print statements to log each step.
    5. Save the list of dictionaries in a new file with path {first_few_elements_path_name}.
    6. Always use os module to handle file paths.
    """,
    input_variables=["extracted_python_code", "file_path", "first_few_elements_path_name"],
)