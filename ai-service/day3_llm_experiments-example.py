import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

model = os.getenv("OPENAI_MODEL")
if not model:
    raise ValueError("OPENAI_MODEL is not configured")

client = OpenAI()

response = client.responses.create(
    model=model,
    instructions=(
        "You are an assistant supporting a healthcare prior-authorization "
        "reviewer. Use only the facts supplied in the request. "
        "Do not make a final coverage decision."
    ),
    input=(
        "Case PA-1001 requests a lumbar spine MRI. "
        "The member is eligible. The submitted information contains lower-back "
        "pain but does not specify the symptom duration or prior conservative "
        "treatment. Summarize the case and identify missing information."
    ),
    max_output_tokens=300,
)

print(response.output_text)

'''
**Response:**
 
**Case summary:**  
- Case PA-1001 requests authorization for a lumbar spine MRI.  
- The member is eligible.  
- The submitted information documents lower-back pain.

**Missing information:**  
- Duration of the lower-back pain/symptoms.  
- Details of any prior conservative treatment, including what was tried and for how long.

'''