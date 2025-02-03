from firecrawl import FirecrawlApp
import os
import autogen
import openai

#Defining the OEPN AI Keys
api_key = os.getenv("OPENAI_API_KEY")

llm_config1 = {"model":"gpt-4o","api_key":api_key,"temperature":0}
#Defining the Firecrawl
app = FirecrawlApp(api_key = os.getenv("FIRECRAWL_API_KEY"))

#Defining the Autogen Agents
#Agent1
user_proxy = autogen.AssistantAgent(
    name="user_proxy",
    system_message="Human Admin. Once the task is completed, answer TERMINATE",
    human_input_mode="ALWAYS",
    is_termination_msg=lambda msg: "TERMINATE" in msg["content"],
    code_execution_config=False
)

#Agent2
Retrieval_Agent = autogen.AssistantAgent(
    name="Retrieval_Agent",
    llm_config=llm_config1,
    system_message="""
    You will url of different websites from the user.
    You will all those urls to the retrieval tool one by one for scraping the website.
	""",
    human_input_mode="NEVER",
    code_execution_config=False
)

#Agent3
Retriever_Tool = autogen.AssistantAgent(
    name="Retriever Tool",
    llm_config=None,  # Set LLM config if needed
    human_input_mode="NEVER",
    code_execution_config=False,
)

#Registering the tools
@Retriever_Tool.register_for_execution()
@Retrieval_Agent.register_for_llm(description="Scrape the website for the given url")

#Function to scrape the website
def scrape_url(website_url:str)->str:
    try:
        response = app.scrape_url(url=website_url, params={
            'formats': ['markdown'],
        })
        if response is None:
            print("No response received from the API")
            return ""
        # Extract the markdown content from the response dictionary
        if isinstance(response, dict) and 'markdown' in response:
            return response['markdown']
        return str(response)  # Fallback to string conversion if not in expected format
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return ""

#Agent4
Report_Agent = autogen.AssistantAgent(
    name="Report_Agent",
    llm_config=llm_config1,
    system_message="""
    You will get the scraped data from the retrieval tool.
    You will generate a report on Women Empowerment without missing any information from the scraped data.
    The report should be in the below format:
    ------------------------------Website Title--------------------------------
    1)Article Title:
    2)Article Information:
    3)Your analysis based on the article information.
    ----------------------------------------------------------- (Line Break for Next Report)--------------------------------
    If you are getting multiple scraped data, you will generate a report on all of them.
    You will append all the reports below the previous report and give the final report to the user.
    After generating the report, you will pass the complete report to the File_Agent for file creation.
	""",
    human_input_mode="NEVER",
    code_execution_config=False
)

#Agent5
File_Agent = autogen.AssistantAgent(
    name="File_Agent",
    llm_config=None,
    human_input_mode="NEVER",
    code_execution_config=False
)

@File_Agent.register_for_execution()
@Report_Agent.register_for_llm(description="Generate a text file with the report content")

#Function to generate the text file
def generate_text_file(content: str, filename: str = "women_empowerment_report.txt") -> str:
    """Creates a downloadable text file with the given content."""
    try:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(content)
        return f"File '{filename}' has been created successfully."
    except Exception as e:
        print(f"An error occurred while creating the file: {str(e)}")
        return f"Failed to create file: {str(e)}"

#Function to define the state transition
def state_transititon(last_speaker,groupchat):
    message = groupchat.messages
    last_message = message[-1]["content"]
    if last_speaker is user_proxy:
        return Retrieval_Agent
    if last_speaker is Retrieval_Agent:
        return Retriever_Tool
    if last_speaker is Retriever_Tool:
        return Report_Agent
    if last_speaker is Report_Agent:
        return File_Agent
	

#Group Chat
groupchat = autogen.GroupChat(
    agents=[user_proxy,Retrieval_Agent,Retriever_Tool,Report_Agent,File_Agent],
    messages=[],
    max_round=50,
    speaker_selection_method=state_transititon,
)

#Group Chat Manager
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=None)

# Start the chat from User Proxy with a query
#user_proxy.initiate_chat(manager, message="https://www.ndtv.com/topic/women-empowerment,https://indianexpress.com/about/women-empowerment")



