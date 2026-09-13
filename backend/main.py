import os

from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel, Field

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI


# ==================================================
# 1. LOAD ENVIRONMENT VARIABLES
# ==================================================

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY is missing from .env")


# ==================================================
# 2. CREATE FASTAPI APPLICATION
# ==================================================

app = FastAPI(
    title="AI Email Writer",
    description="AI Email Writer using FastAPI, LangChain and Gemini",
    version="1.0.0"
)


# ==================================================
# 3. CORS
# ==================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================================================
# 4. CREATE GEMINI MODEL
# ==================================================

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.7,
)


# ==================================================
# 5. CREATE EMAIL PROMPT
# ==================================================

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a professional email writing assistant.

Your job is to write clear, natural and professional emails
based on the information provided by the user.

Rules:

- Follow the requested tone.
- Clearly communicate the user's purpose.
- Include all important points.
- Do not invent facts.
- Keep the email easy to read.
- Use an appropriate greeting.
- Use an appropriate closing.
- Do not explain what you are doing.
- Return only the complete email.
"""
        ),

        (
            "human",
            """
Write an email using the following information.

Recipient:
{recipient}

Purpose:
{purpose}

Tone:
{tone}

Important points:
{key_points}

Write the complete email.
"""
        ),
    ]
)


# ==================================================
# 6. CREATE LANGCHAIN CHAIN
# ==================================================

email_chain = prompt | llm


# ==================================================
# 7. REQUEST MODEL
# ==================================================

class EmailRequest(BaseModel):

    recipient: str = Field(
        ...,
        min_length=1,
        max_length=200
    )

    purpose: str = Field(
        ...,
        min_length=3,
        max_length=500
    )

    tone: str = Field(
        ...,
        min_length=2,
        max_length=50
    )

    key_points: str = Field(
        ...,
        min_length=3,
        max_length=5000
    )


# ==================================================
# 8. RESPONSE MODEL
# ==================================================

class EmailResponse(BaseModel):

    email: str


# ==================================================
# 9. ROOT ENDPOINT
# ==================================================

@app.get("/")
async def root():

    return {
        "message": "AI Email Writer API is running"
    }


# ==================================================
# 10. HEALTH CHECK
# ==================================================

@app.get("/health")
async def health():

    return {
        "status": "healthy"
    }


# ==================================================
# 11. EMAIL GENERATION ENDPOINT
# ==================================================

@app.post(
    "/generate-email",
    response_model=EmailResponse
)
async def generate_email(request: EmailRequest):

    try:

        # Send user information to LangChain
        response = await email_chain.ainvoke(
            {
                "recipient": request.recipient,
                "purpose": request.purpose,
                "tone": request.tone,
                "key_points": request.key_points
            }
        )

        # Get Gemini's actual response
        email = response.content

        # Make sure the response is a string
        if isinstance(email, list):

            email = " ".join(
                str(item)
                for item in email
            )

        return EmailResponse(
            email=str(email)
        )

    except Exception as e:

        print("ERROR:", e)

        raise HTTPException(
            status_code=500,
            detail="Failed to generate email."
        )