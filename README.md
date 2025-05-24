# Emergency Medicine Case Simulator

A FastAPI-based clinical management simulation platform for assessing physicians on emergency medicine cases to understand factors underlying reasoning under uncertainty.

## Overview

This web application provides an interactive simulation environment where medical trainees can work through emergency medicine cases, interact with an AI physician, and have their performance assessed through both conversation logs and survey responses.

## Features

### Frontend
- **Clean, modern design** using shadcn UI components
- **Multi-page webapp** with three main interfaces:
  1. **Login screen** - User ID authentication
  2. **Case interface** - Split-screen layout with chat (75%) and live case summary (25%)
  3. **Final summary** - Two-column layout with case summaries and Likert scale survey

### Backend
- **FastAPI** for robust API architecture
- **OpenAI integration** for LLM-powered case interactions
- **Google Drive integration** for automatic data logging
- **Session management** for user progress tracking
- **Real-time case summarization**

### Data Collection
- **Chat logs** saved to Google Drive in CSV format for each case
- **Survey responses** collected using 1-5 Likert scales
- **Comprehensive data export** for research analysis

## Technology Stack

- **Backend**: FastAPI, Python 3.12+
- **Frontend**: HTML, CSS (Tailwind), JavaScript (Vanilla)
- **UI Components**: shadcn design system
- **LLM**: OpenAI GPT models
- **Storage**: Google Drive API
- **Deployment**: Docker, ready for Render.com

## Quick Start

### Prerequisites

- Python 3.12 or higher
- uv package manager
- OpenAI API key
- Google Drive service account key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd managementsim
   ```

2. **Set up Python environment**
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -r pyproject.toml
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

4. **Update configuration files**
   - Add authorized user IDs to `config/valid_user_ids.py`
   - Update survey questions in `config/survey_questions.py`
   - Modify cases in `config/case_config.py` as needed

5. **Run the application**
   ```bash
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Access the application**
   - Open http://localhost:8000 in your web browser
   - Use an authorized user ID to log in

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_SERVICE_ACCOUNT_KEY={"type":"service_account",...}
GOOGLE_DRIVE_FOLDER_ID=your_folder_id_here
```

### User Management

Add authorized user IDs to `config/valid_user_ids.py`:

```python
VALID_USER_IDS = [
    "dwu",
    "new_user_id",
    # Add more user IDs as needed
]
```

### Survey Questions

Update the survey questions in `config/survey_questions.py`:

```python
SURVEY_QUESTIONS = [
    "Your question 1 here",
    "Your question 2 here", 
    "Your question 3 here",
    "Your question 4 here"
]
```

### Case Configuration

Cases are defined in `config/case_config.py`. Each case includes:
- **ID**: Unique identifier
- **Title**: Display name
- **Description**: Brief summary
- **Content**: Detailed case information for the AI

## Docker Deployment

### Build and run locally

```bash
docker build -t em-case-simulator .
docker run -p 8000:8000 --env-file .env em-case-simulator
```

### Deploy to Render.com

1. Connect your GitHub repository to Render.com
2. Create a new Web Service
3. Use the following settings:
   - **Build Command**: `docker build -t em-case-simulator .`
   - **Start Command**: `docker run -p $PORT:8000 em-case-simulator`
   - **Environment Variables**: Add your API keys and configuration

## Project Structure

```
managementsim/
├── config/                 # Configuration files
│   ├── case_config.py     # Case definitions
│   ├── survey_questions.py # Survey configuration
│   └── valid_user_ids.py  # User authentication
├── models/                # Pydantic data models
│   └── schemas.py
├── services/              # Business logic
│   ├── auth_service.py    # Authentication
│   ├── google_drive_service.py # Google Drive integration
│   ├── openai_service.py  # OpenAI API interactions
│   └── session_service.py # Session management
├── src/                   # Main application
│   └── main.py           # FastAPI application
├── static/               # Static files
│   ├── css/style.css    # Custom styles
│   └── js/app.js        # JavaScript utilities
├── templates/           # HTML templates
│   ├── base.html       # Base template
│   ├── login.html      # Login page
│   ├── case.html       # Case interface
│   └── summary.html    # Final summary
├── Dockerfile          # Docker configuration
├── pyproject.toml     # Dependencies
└── README.md         # This file
```

## API Endpoints

### Authentication
- `POST /api/auth/login` - User authentication

### Cases
- `GET /api/cases` - List available cases
- `POST /api/cases/{case_id}/start/{user_id}` - Start a case
- `POST /api/cases/{case_id}/chat/{user_id}` - Send chat message
- `POST /api/cases/{case_id}/complete/{user_id}` - Complete case

### Summary & Survey
- `GET /api/summary/{user_id}` - Get final summary data
- `POST /api/survey/submit/{user_id}` - Submit survey responses

### Utilities
- `GET /api/next-case/{user_id}` - Get next available case

## Data Collection

### Chat Logs
- Saved automatically when cases are completed
- CSV format with columns: role, content, timestamp
- Filename format: `{user_id}_{case_id}_{case_title}_chat_log_{timestamp}.csv`

### Survey Responses
- Collected on final summary page
- CSV format with columns: user_id, case_id, question_index, rating, timestamp
- Filename format: `{user_id}_survey_responses_{timestamp}.csv`

## Development

### Adding New Cases

1. Define the case in `config/case_config.py`:
   ```python
   CASE_4 = {
       "id": "case_4",
       "title": "New Case Title",
       "description": "Case description",
       "content": "Detailed case information..."
   }
   ```

2. Add to the `AVAILABLE_CASES` dictionary:
   ```python
   AVAILABLE_CASES = {
       case["id"]: case for case in [CASE_1, CASE_2, CASE_3, CASE_4]
   }
   ```

### Customizing UI

- Modify templates in `templates/` directory
- Update styles in `static/css/style.css`
- Extend JavaScript functionality in `static/js/app.js`

### API Extensions

- Add new endpoints in `src/main.py`
- Create new services in `services/` directory
- Define new data models in `models/schemas.py`

## Troubleshooting

### Common Issues

1. **OpenAI API errors**: Check your API key and quota
2. **Google Drive upload failures**: Verify service account permissions
3. **User authentication issues**: Ensure user ID is in `valid_user_ids.py`
4. **Template not found**: Check that templates directory exists and contains all files

### Logging

The application logs to console by default. For production, consider configuring proper logging to files or external services.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational and research purposes. Please ensure compliance with your institution's guidelines when using for medical education.

## Support

For technical issues or questions about the simulation platform, please create an issue in the repository or contact the development team.
