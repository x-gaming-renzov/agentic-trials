from ..tools.retriever_tool import get_retriever_tool
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from ..states.understand_element_state import corrected_field_names_spelling_list
from ..prompts.element_info_prompts import correct_field_names_spellin_prompt
import os
import dotenv
from termcolor import colored
from ..utils.utils import pretty_print_state_enhanced
from ..utils.large_files_ops import return_prompt_adjusted_values
import json

dotenv.load_dotenv()

def retrive_from_knowledge_base(docs):
    retriever_tool_node = ToolNode([get_retriever_tool(docs)])
    return retriever_tool_node

model = ChatOpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"), streaming=True)

correct_field_name_spelling = model.with_structured_output(corrected_field_names_spelling_list)

# Initialize chains for preprocessor, code generation, and code review agents
correct_field_name_spelling_generator = correct_field_names_spellin_prompt | correct_field_name_spelling

def preprocess_field_info_state(FieldInfoState):
    
    with open(FieldInfoState['file_path'], 'r') as file:
            data = json.load(file)

    unique_field_names = set()
    for event in data:
        unique_field_names.update(event.keys())
    
    correct_spelled_field_names = correct_field_name_spelling_generator.invoke({'field_names': unique_field_names})
    if not isinstance(correct_spelled_field_names, corrected_field_names_spelling_list):
            print(colored("Error in correcting field names spelling", 'red'))
    
    #Apply the corrected spelling to the field names in the data
    for event in data:
        for key in event.keys():
            #change key to corrected_field_names_spelling_list[key] if key is in corrected_field_names_spelling_list
            if key in correct_spelled_field_names['corrected_field_names_spelling_list']:
                event[correct_spelled_field_names['corrected_field_names_spelling_list'][key]] = event.pop(key)


    return FieldInfoState


