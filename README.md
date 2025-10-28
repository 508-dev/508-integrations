# 508 Integrations

Integration service for EspoCRM webhooks with automated resume skills extraction using Gemini Flash.

## Features

- **EspoCRM Webhook Processing**: Handles Contact create/update webhooks
- **Resume Skills Extraction**: Automatically extracts skills from attached resumes using Gemini 1.5 Flash
- **Document Processing**: Supports PDF, DOCX, DOC, and TXT resume formats
- **Skills Management**: Adds new skills to contacts without removing existing ones
- **Background Processing**: Async processing with FastAPI background tasks
- **Content Caching**: Avoids reprocessing identical documents
- **Comprehensive Logging**: Structured logging with request tracing

## Quick Start

### 1. Environment Setup

```bash
# Clone the repository
git clone <repo-url>
cd 508-integrations

# Install dependencies with uv
uv pip install -e .[dev]

# Copy environment template
cp .env.example .env
```

### 2. Configure Environment

Edit `.env` with your settings:

```bash
# EspoCRM Configuration
ESPOCRM_URL=https://your-espocrm-instance.com
ESPOCRM_API_KEY=your_api_key_here

# Gemini Configuration (using OpenAI interface)
OPENAI_API_KEY=your_gemini_api_key_here
OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
OPENAI_MODEL=gemini-1.5-flash

# Security
WEBHOOK_SECRET=your_webhook_secret_here
```

### 3. Run the Service

```bash
# Development server
python scripts/dev.py dev

# Or use the run script
./scripts/run-server.sh

# Production server
./scripts/run-server.sh --workers 4
```

The service runs on port **5080** by default.

## API Endpoints

### Webhooks

- `POST /webhooks/espocrm` - EspoCRM webhook endpoint
- `POST /process-contact/{contact_id}` - Manual contact processing

### Health & Info

- `GET /health` - Service health check
- `GET /` - Service information
- `GET /docs` - Interactive API documentation

## Webhook Setup

Configure EspoCRM to send webhooks to:
```
POST https://your-service.com/webhooks/espocrm
```

Expected payload format:
```json
[
  {
    "id": "contact_id_123",
    "name": "John Doe"
  }
]
```

## Skills Extraction Process

1. **Webhook Reception**: Service receives Contact create/update webhook
2. **Attachment Discovery**: Searches for resume-like attachments (PDF, DOCX, etc.)
3. **Text Extraction**: Extracts text from documents using specialized parsers
4. **Skills Analysis**: Uses Gemini 1.5 Flash to identify technical and professional skills
5. **Skills Update**: Adds new skills to the contact (preserves existing skills)
6. **Content Caching**: Caches extracted content to avoid reprocessing

## Development

### Commands

```bash
# Install dependencies
python scripts/dev.py install

# Install pre-commit hooks (recommended)
python scripts/dev.py hooks

# Run development server
python scripts/dev.py dev

# Code quality checks
python scripts/dev.py lint          # Run linting
python scripts/dev.py format        # Format code
python scripts/dev.py typecheck     # Type checking
python scripts/dev.py test          # Run tests
python scripts/dev.py test-cov      # Run tests with coverage
python scripts/dev.py check-all     # Run all checks
```

### Project Structure

```
src/
├── main.py              # FastAPI application
├── settings.py          # Configuration management
├── models.py            # Pydantic models
└── crm/                 # CRM-related modules
    ├── espocrm_client.py    # EspoCRM API client
    ├── document_processor.py # Document text extraction
    ├── skills_extractor.py  # Gemini-based skills extraction
    └── processor.py         # Main processing logic

tests/                   # Comprehensive test suite
scripts/                 # Development and deployment scripts
```

## Deployment

### Environment Variables

Required:
- `ESPOCRM_URL` - Your EspoCRM instance URL
- `ESPOCRM_API_KEY` - EspoCRM API key
- `OPENAI_API_KEY` - Gemini API key
- `WEBHOOK_SECRET` - Webhook security secret

Optional:
- `HOST` - Server host (default: 0.0.0.0)
- `PORT` - Server port (default: 8000)
- `DEBUG` - Debug mode (default: false)
- `LOG_LEVEL` - Logging level (default: INFO)

### Coolify Deployment

This service is designed for easy deployment with Coolify:

1. Add your environment variables to Coolify
2. Deploy directly from the repository
3. The service will start automatically on the configured port

### Production Considerations

- Set appropriate resource limits based on expected volume
- Monitor document processing performance
- Configure log aggregation for structured logs
- Set up health check monitoring on `/health` endpoint

## Security

- API key authentication for EspoCRM integration
- Webhook secret validation
- Input validation and sanitization
- Secure document processing with size limits
- No sensitive data logging

## Contributing

1. Follow the existing code style (ruff formatting)
2. Add tests for new functionality
3. Ensure all checks pass: `python scripts/dev.py check-all`
4. Update documentation as needed

## License

MIT License
