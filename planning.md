# Key notes
I am using VSCode and have created a venv in this project directory under .venv.
I am using uv to manage my package dependencies. Please use uv to add dependencies when necessary (uv add).
My API keys are stored via environment variables OPENAI_API_KEY, GEMINI_API_KEY, ANTHROPIC_API_KEY.
No unit tests are required for this project.
The deployed app will be stored in src/app.py.

# Overarching Plan
This project is a  webapp for a LLM-based clinical management simulation for assessing physicians on emergency medicine cases to understand factors underlying reasoning under uncertainty. 

## Desired Output
A multi-page webapp with a LLM chat interface. 
There will be a series of interactive cases. After all cases are completed, there will be a summary of each case followed by a few questions on a Likert scale from 1 to 5.

### Frontend
The webapp will have a clean, modern design using shadcn elements.
The webapp will consist of multiple "pages":
1.  Login screen: A field to enter the user ID and a button that says "Start Simulation"
2.  Case interface
-This page will consist of 2 containers. The left container will be 75% of the total width and be the main chat interface between the user and the LLM, with a chat input bar at the bottom. 
-The right container will be 25% of the total width and be a concise "Live Case Summary" of any case details that are presented (e.g., ID, PMH, Meds, Vitals, Exam, etc).
-There will be two buttons, "Admit" and "Discharge." Clicking either will end the case and proceed to the next case.
3. After all cases are concluded, the final page will be presented. This consists of a two-column format. The left side will be a concise summary of each case and the right side will be 4 Likert scale questions (repeated for each case) that the user can click to save their score.
 
### Backend
-Powered by FastAPI.
-The LLM will be OpenAI models only. Please maintain flexibility for using their text-to-speech and transcription models in the future.
-For every user, the following will be saved in csv format to Google Drive:
    -Chat log for each case (including timestamps)
    -Survey questions responses
-
-Dockerize the project when complete so that it can be deployed on a hosting service such as render.com