---
title: llm_alter_ego
app_file: app.py
sdk: gradio
sdk_version: 5.38.2
---
# Enhanced LLM Alter Ego

An AI-powered personal assistant chatbot with real-time GitHub integration and professional data sources.

## Features

### 🚀 Core Capabilities
- **Real-time GitHub Integration**: Automatically pulls your latest repositories, programming languages, and project data
- **LinkedIn PDF Integration**: Extracts your professional background from LinkedIn exports
- **Personal Summary**: Custom professional narrative and career highlights
- **Professional Tool Integration**: Pushover notifications for lead tracking
- **Clean Architecture**: Simple, maintainable code structure
- **Dynamic System Prompts**: Context-aware responses based on current data

### 📊 Data Sources
1. **GitHub API**: Live repository data, language statistics, project information
2. **LinkedIn PDF**: Professional background and experience (from LinkedIn export)
3. **Summary Text**: Personal summary and career highlights  

### 🛠️ Tools & Integrations
- **Contact Recording**: Automatically records interested visitors via Pushover
- **Unknown Question Tracking**: Logs questions you couldn't answer for improvement
- **Data Refresh**: Manual refresh button for updating live data

## Setup Instructions

### 1. Environment Configuration

**Quick Setup:**
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your actual API keys
# At minimum, you need OPENAI_API_KEY
```

**Required Variables:**
```bash
OPENAI_API_KEY=sk-your-openai-api-key-here
```

**Optional but Recommended:**
```bash
# GitHub token for higher rate limits (5000 vs 60 requests/hour)
GITHUB_TOKEN=ghp_your-github-token-here

# Pushover for contact notifications
PUSHOVER_USER=your-pushover-user-key
PUSHOVER_TOKEN=your-pushover-app-token
```

See `.env.example` for complete setup instructions and additional optional variables.

### 2. Personal Configuration

Update the configuration in `data_sources.py` or directly in `app.py`:

```python
config = {
    "name": "Your Name",
    "github_username": "your-github-username",
    "github_token": None,  # Uses env var if not set
    "linkedin_pdf_path": "me/linkedin.pdf",
    "summary_path": "me/summary.txt"
}
```

### 3. Profile Data Setup

#### a. Update Personal Files
- Replace `me/linkedin.pdf` with your LinkedIn profile export
- Edit `me/summary.txt` with your professional summary

#### b. LinkedIn PDF Export
To get your LinkedIn PDF:
1. Go to your LinkedIn profile
2. Click "More" → "Save to PDF"
3. Save as `linkedin.pdf` in the `me/` folder

### 4. Run the Application

```bash
# From the project directory
cd personal/llm_alter_ego
uv run python app.py
```

## Project Structure

```
personal/llm_alter_ego/
├── .env.example           # Environment variables template
├── .gitignore            # Git ignore rules
├── app.py                # Main application with enhanced UI
├── utils.py              # Tool functions and definitions
├── github_api.py         # GitHub API integration
├── data_sources.py       # PDF, summary, and GitHub data management
├── prompts.py            # System prompts and conversation styles
├── requirements.txt      # Python dependencies
├── me/                   # Personal profile data
│   ├── linkedin.pdf      # LinkedIn profile export
│   └── summary.txt       # Professional summary
├── README.md            # User documentation (this file)
└── PROJECT_OVERVIEW.md  # Technical overview for recruiters
```

## Module Overview

### `app.py` - Main Application
- `EnhancedMe`: Core chatbot class with GitHub integration
- `create_interface()`: Gradio UI with refresh controls
- `main()`: Application entry point

### `utils.py` - Tool Management
- Push notification functions
- Contact and question recording tools
- Tool call handler with error management

### `github_api.py` - GitHub Integration
- `GitHubAPI`: Comprehensive GitHub data fetching
- Repository analysis and language statistics
- User activity and contribution tracking
- Formatted output for LLM consumption

### `data_sources.py` - Data Management
- `DataSourceManager`: Coordinates PDF, summary, and GitHub data
- Caching system for GitHub data
- Simple, clean data loading
- Fallback handling for unavailable sources

### `prompts.py` - System Prompts
- `get_system_prompt()`: Main conversational prompt (default)
- `get_professional_prompt()`: Business-focused interactions
- `get_casual_prompt()`: Friendly, personal conversations
- `get_prompt()`: Style selector function

## Customization Options

### 1. GitHub Integration
```python
# Disable GitHub integration
config["github_username"] = None

# Custom GitHub token for higher rate limits
config["github_token"] = "your-token"
```

### 2. Conversation Style
Choose from three different prompt styles:

```python
# In your config
config["prompt_style"] = "main"         # Balanced professional + personal
config["prompt_style"] = "professional" # Business-focused
config["prompt_style"] = "casual"       # Friendly, conversational
```

**Prompt Styles:**
- **Main** (default): Balanced tone with personality while staying professional
- **Professional**: Focused on technical skills and career achievements
- **Casual**: Friendly, personal conversations about life and work

### 3. Custom Prompts
Add new prompt styles in `prompts.py`:
```python
def get_custom_prompt(name: str) -> str:
    return f"""Your custom prompt for {name}..."""

# Then use in config:
config["prompt_style"] = "custom"
```

### 4. Additional Data Sources
Extend `DataSourceManager` to add:
- Google Sheets integration
- Blog RSS feeds
- Portfolio website APIs
- Additional PDF documents

### 5. Custom Tools
Add new tools in `utils.py`:
```python
def your_custom_tool(param1, param2):
    # Your tool logic
    return {"result": "success"}

YOUR_TOOL_SCHEMA = {
    "name": "your_custom_tool",
    "description": "Description of what your tool does",
    "parameters": {
        # OpenAI function calling schema
    }
}
```

### 6. UI Enhancements
Modify `create_interface()` in `app.py` to add:
- Additional control buttons
- Status indicators
- Custom themes
- File upload capabilities

## Cost-Effective Solution

This implementation focuses on **free and low-cost solutions**:

✅ **Free**: GitHub API, LinkedIn PDF, manual summary file  
✅ **Low-cost**: OpenAI API (~$0.50-2.00/day typical usage)  
✅ **Optional**: Pushover ($5 one-time), GitHub token (free)  

❌ **Avoided**: Expensive LinkedIn API alternatives ($49+/month)

## Deployment Options

### Development
```bash
uv run python app.py
# Runs locally on http://127.0.0.1:7860
```

### Production (HuggingFace Spaces)
1. Create HuggingFace account
2. Set up secrets (OPENAI_API_KEY, etc.)
3. Deploy with: `uv run gradio deploy`

### Self-Hosted
- Docker containerization
- Cloud deployment (AWS, GCP, Azure)
- VPS hosting

## Troubleshooting

### Common Issues

**GitHub API Rate Limits**
- Add `GITHUB_TOKEN` to your `.env` file
- Reduce refresh frequency in config

**Missing Dependencies**
```bash
# From project root
uv sync
```

**Module Import Errors**
```bash
# Run from the project subdirectory
cd personal/llm_alter_ego
uv run python app.py
```

**PDF Not Loading**
- Ensure `linkedin.pdf` exists in `me/` directory
- Check file permissions
- Try re-exporting from LinkedIn

**Summary Not Loading**
- Ensure `summary.txt` exists in `me/` directory
- Check the file contains text content

## Data Sources Testing

Test individual components:
```bash
cd personal/llm_alter_ego
uv run python data_sources.py
```

This will show you:
- Summary content length and preview
- LinkedIn PDF content length and preview  
- GitHub data retrieval
- Combined profile output

## Contributing

This is a personal project template, but improvements are welcome:

1. Fork the repository
2. Create a feature branch
3. Test your changes thoroughly
4. Submit a pull request with clear description
---

**Built with**: Python, OpenAI API, Gradio, GitHub API, and lots of ☕

**Key Design Decision**: Simplified to three reliable data sources (PDF + summary + GitHub) for maximum maintainability and minimum complexity.

## Acknowledgments

This project was inspired by and builds upon the foundational concepts from **Ed Donner's "The Complete Agentic AI Engineering Course" on Udemy**. The original chatbot implementation (from Lab 4) provided the starting point for this enhanced version.

**Original Course**: The Complete Agentic AI Engineering Course by Ed Donner  
**Platform**: Udemy  
**Initial Concept**: Personal AI assistant with tool integration

**Enhancements and Extensions Added:**
- Real-time GitHub API integration for live repository data
- Modular architecture with separated concerns (utils, data sources, prompts)
- Multiple conversation personalities and prompt management system
- Enhanced data source management combining PDF, summary, and live APIs
- Professional deployment setup with comprehensive documentation
- Production-ready code structure with proper error handling

The evolution from course concept to production-ready application demonstrates practical software development skills and the ability to extend foundational ideas into robust, deployable solutions.

For questions or suggestions, feel free to reach out! # Force update Fri Jul 25 14:15:50 CEST 2025
