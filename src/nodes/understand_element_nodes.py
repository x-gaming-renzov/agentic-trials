from ..states.understand_element_state import ElementInfoState
from ..tools.retriever_tool import get_retriever_tool
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from ..states.understand_element_state import CodeReviewResult, AgentState
from ..prompts.element_info_prompts import preprocessor_prompt_template, code_generation_prompt_template, code_review_prompt_template
import os
import dotenv
from termcolor import colored
import re
import docker
import tempfile
import os
from ..utils.utils import pretty_print_state_enhanced
from pydantic import BaseModel, Field, ValidationError
import tarfile, json, io

dotenv.load_dotenv()

def retrive_from_knowledge_base():
    retriever_tool_node = ToolNode([get_retriever_tool()])
    return retriever_tool_node

model = ChatOpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"), streaming=True)

preprocessor_model = model
code_generator_model = model
code_review_model = model.with_structured_output(CodeReviewResult)

# Initialize chains for preprocessor, code generation, and code review agents
preprocessor_agent_generator = preprocessor_prompt_template | preprocessor_model
agent_code_generator = code_generation_prompt_template | code_generator_model
code_review_agent_generator = code_review_prompt_template | code_review_model

def agent_preprocessor(state: AgentState):
    print(colored("DEBUG: Preprocessing User Request...", "magenta"))
    result = preprocessor_agent_generator.invoke({"file_path": state["file_path"], 
                                                  "first_few_lines": state["first_few_lines"], 
                                                  "user_info_about_data": state["user_info_about_data"], 
                                                  "first_few_elements_path_name": state["first_few_elements_path_name"]
                                                })
    print(colored(f"DEBUG: Preprocessor Result: {result.content}", "magenta"))
    state["instructions_to_code"] = result.content
    print(colored("DEBUG: agent_preprocessor state", "magenta"))
    pretty_print_state_enhanced(state)
    return state

def agent_code_generation(state: AgentState):
    print(colored("DEBUG: Generating Python Code...", "blue"))

    # Check and reset the state at the beginning of the method if needed
    if (state["code_extraction_status"] == "regenerate" or 
        state["code_review_result"] == "regenerate") or state["code_review_status"] == "regenerate":
        print(colored("DEBUG: Resetting agent state due to regenerate flag...", "yellow"))
        reset_keys = [
            "generated_code", 
            "extracted_python_code", 
            "code_review_result"
        ]
        for key in reset_keys:
            state[key] = ""
    else:
        print(colored("DEBUG: Initial Generation of code. No need to reset agent state.", "green"))
    
    # Continue with the rest of your code generation logic...
    result = agent_code_generator.invoke({"first_few_lines": state["first_few_lines"],
                                          "user_info_about_data": state["user_info_about_data"],
                                          "file_path": state["file_path"],
                                          "instructions_to_code": state["instructions_to_code"],
                                          "first_few_elements_path_name": state["first_few_elements_path_name"]
                                         })
    print(colored(f"DEBUG: Code Generation Result: {result.content}", "blue"))
    state["generated_code"] = result.content
    
    # Continue with the rest of your code generation logic...
    print(colored("DEBUG: agent_code_generation state", "magenta"))
    pretty_print_state_enhanced(state)
    return state

def agent_extract_code(state: AgentState):
    # print(colored("DEBUG: Extracting Python Code...", "green"))
    # print(colored(f"DEBUG: Generated Code Result: {state['generated_code_result']}", "green"))

    code_result = state["generated_code"]

    code_block = re.search(r"```(?!python)(.*?)```", code_result, re.DOTALL)
    code_block_with_lang = re.search(r"```python(.*?)```", code_result, re.DOTALL)
    single_backtick_code = re.search(r"`(.*?)`", code_result, re.DOTALL)
    
    # 1. Try to extract code from triple backticks without the word 'python'
    if code_block:
        extracted_code = code_block.group(1).strip()
        state["extracted_python_code"] = extracted_code
        # print(colored(f"DEBUG: Extracted Python Code from triple backticks: {state['extracted_python_code']}", "green"))
        print(colored("DEBUG: Extracted Python Code from triple backticks", "green"))
        state["code_extraction_status"] = "continue"
    
    # 2. If that fails, try to extract from triple backticks with 'python'
    elif code_block_with_lang:
        extracted_code = code_block_with_lang.group(1).strip()
        state["extracted_python_code"] = extracted_code
        # print(colored(f"DEBUG: Extracted Python Code from triple backticks with 'python': {state['extracted_python_code']}", "green"))
        print(colored("DEBUG: Extracted Python Code from triple backticks with 'python'", "green"))
    
        state["code_extraction_status"] = "continue"
    
    # 3. If that fails, try to extract from single backticks
    elif single_backtick_code:
        extracted_code = single_backtick_code.group(1).strip()
        state["extracted_python_code"] = extracted_code
        # print(colored(f"DEBUG: Extracted Python Code from single backticks: {state['extracted_python_code']}", "green"))
        print(colored("DEBUG: Extracted Python Code from single backtick", "green"))
        state["code_extraction_status"] = "continue"
    
    # 4. Fallback: Assume the entire result is the code if no backticks are found
    elif code_result:
        print(colored("DEBUG: No backticks found. Assuming entire result is the code.", "yellow"))
        state["extracted_python_code"] = code_result.strip()
        # print(colored(f"DEBUG: Fallback Extracted Python Code: {state['extracted_python_code']}", "yellow"))
        print(colored("DEBUG: Fallback Extraction", "green"))
        state["code_extraction_status"] = "continue"
    else:
        state["code_extraction_status"] = "regenerate"  # Extraction failed, regenerate
    
    print(colored("DEBUG: agent_extract_code state", "magenta"))
    pretty_print_state_enhanced(state)

    return state  # Always return state

def conditional_should_continue_after_extraction(state: AgentState):
    # Check if the extraction was successful and we have some code to work with
    if state["code_extraction_status"] == "continue":
        return "continue"
    else:
        return "regenerate"
    
def agent_code_review(state: AgentState):
    print(colored("DEBUG: Reviewing Python Code...", "yellow"))
    
    code_review_result = code_review_agent_generator.invoke({"extracted_python_code": state["extracted_python_code"], "file_path": state["file_path"], "first_few_elements_path_name": state["first_few_elements_path_name"]})

    try:
        
        # Print and store in agent state
        # print(colored("Reviewed Code:", "yellow"))
        if isinstance(code_review_result, CodeReviewResult):
            # print(f"Result: {code_review_result.result}")
            # print(f"Message: {code_review_result.message}")
            state["code_review_result"] = code_review_result
        else:
            print("Unexpected response format from code review agent.")
        
        # Update the review status based on the result
        if code_review_result.result == "correct":
            state["code_review_status"] = "continue"
        else:
            state["code_review_status"] = "regenerate"

    except ValidationError as e:
        print(colored(f"ERROR: Code review validation failed with error: {e}", "red"))
        state["code_review_status"] = "regenerate"
    
    except Exception as e:
        print(colored(f"ERROR: Error parsing JSON: {e}", "red"))
        state["code_review_status"] = "regenerate"
    
    print(colored("DEBUG: agent_code_review state", "magenta"))
    pretty_print_state_enhanced(state)

    return state  # Always return state

def conditional_should_continue_after_code_review(state: AgentState):
    # Check if the extraction was successful and we have some code to work with
    if state["code_review_status"] == "continue":
        return "continue"
    else:
        return "regenerate"
    
def agent_execute_code_in_docker(state: AgentState):
    print(colored("DEBUG: Running code in Docker...", "cyan"))
    # print(colored(f"DEBUG: Final Python Code to run: {state['extracted_python_code']}", "cyan"))

    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as temp_code_file:
        temp_code_file.write(state["extracted_python_code"].encode('utf-8'))
        temp_code_filename = temp_code_file.name

    client = docker.from_env()
    try:
        container = client.containers.run(
            image="python:3.9-slim",
            command=f"python {os.path.basename(temp_code_filename)}",
            volumes={os.path.dirname(temp_code_filename): {'bind': '/usr/src/app', 'mode': 'rw'},
                     os.path.dirname(state['file_path']): {'bind': '/usr/src/app', 'mode': 'rw'}},
            working_dir="/usr/src/app",
            remove=True,
            stdout=True,
            stderr=True,
            detach=True
        )
        container.wait()

        # Access the file inside the container
        output_file_path = state["first_few_elements_path_name"]
        tar_stream, _ = container.get_archive(output_file_path)
        tar_bytes = io.BytesIO(b"".join(tar_stream))  # Combine chunks into a single byte stream

        # Open the TAR file from the byte stream
        with tarfile.open(fileobj=tar_bytes, mode="r") as tar:
            # Extract the JSON file
            for member in tar.getmembers():
                if member.name.endswith(".json"):  # Ensure it's the desired JSON file
                    json_file = tar.extractfile(member)  # Extract the file as a file-like object
                    json_data = json_file.read().decode("utf-8")  # Read and decode JSON content
                    json_list = json.loads(json_data)  # Parse JSON into a Python object (list or dict)
                    break

        container.remove()  # Clean up container after retrieving the file

        # Update the state with the extracted JSON data
        state["first_few_elements"] = json_list
    except docker.errors.ContainerError as e:
        print(colored(f"ERROR: Error running code in container: {str(e)}", "red"))
    
    os.remove(temp_code_filename)

    print(colored("DEBUG: agent_execute_code_in_docker state", "magenta"))
    pretty_print_state_enhanced(state)


    return state