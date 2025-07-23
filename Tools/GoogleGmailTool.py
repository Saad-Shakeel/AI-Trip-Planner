from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.agent_toolkits import GmailToolkit
from langchain_community.tools.gmail.utils import build_resource_service, get_gmail_credentials

@tool(name_or_callable="gmail_tool")
def gmail_tool(input_text: str,subject: str, email: str) -> str:
    """Use this tool to send email messages.
    Args:
    input_text: draft trip itinerary
    subject: subject of the email
    email: recipient email
    """
    # Obtain Gmail credentials
    print("Gmail Tool Call")
    credentials = get_gmail_credentials(
        scopes=["https://mail.google.com/"],
        token_file="Tools/token.json",
        client_secrets_file="Tools/Credentials.json",
    )
    model = ChatGroq(model="llama-3.3-70b-versatile", temperature = 0)
    prompt = ChatPromptTemplate.from_messages(
        [(
            "system", "You are an expert HTML email template designer. your task is to create a html email body template of the given content and make professional, clean, and responsive email template. Template Start with html tages and avoid any other information"),
        ("human","{input}")
        ]
    )

    chain = prompt | model
    response = chain.invoke({"input": input_text})
    body = response.content
    # Build Gmail API resource service
    api_resource = build_resource_service(credentials=credentials)

    # Initialize Gmail toolkit and tools
    toolkit = GmailToolkit(api_resource=api_resource)
    tools = toolkit.get_tools()
    email_data = {
        "to": email,
        "subject": subject,
        "message": body
    }
    for tool in tools:
        if tool.name == "send_gmail_message":
            print("\nEmail Sucessfully Sended\n")
            return tool.invoke(email_data)
    return "Failed to send email; email tool not found."
