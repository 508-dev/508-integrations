# AI Agents Configuration

This document describes the AI agents and LLM integrations used in the 508 Integrations service.

## Primary Agent: Skills Extractor

### Purpose
Extracts technical and professional skills from resume text using Gemini 1.5 Flash.

### Configuration
- **Model**: `gemini-1.5-flash`
- **Interface**: OpenAI-compatible API
- **Base URL**: `https://generativelanguage.googleapis.com/v1beta/openai/`
- **Temperature**: `0.1` (low for consistent extraction)
- **Max Tokens**: `2000`

### Input Processing
- Accepts plain text extracted from resume documents
- Handles multiple document formats (PDF, DOCX, TXT)
- Processes up to 8000 characters per request (truncated if longer)

### Prompt Engineering
The skills extraction prompt is designed to:
- Focus on technical skills (programming languages, frameworks, tools)
- Identify professional skills (project management, leadership)
- Extract certifications and domain expertise
- Return structured JSON output for parsing

### Output Format
```json
{
  "skills": ["Python", "JavaScript", "React", "Docker", "AWS"],
  "confidence": 0.85
}
```

### Error Handling
- Validates JSON response format
- Handles API timeouts and rate limits
- Provides fallback processing for malformed responses
- Logs all extraction attempts for debugging

## Content Caching Strategy

### Cache Implementation
- **Hash-based**: SHA256 content hashing for document deduplication
- **TTL**: 24 hours (configurable via `CACHE_TTL_HOURS`)
- **Storage**: In-memory cache (suitable for low-volume deployment)
- **Key Format**: `sha256(document_content)`

### Cache Benefits
- Avoids reprocessing identical resumes
- Reduces API costs for duplicate documents
- Improves response times for repeated processing
- Prevents rate limit issues

### Cache Invalidation
- Automatic expiration after TTL
- Manual cache clearing on service restart
- Content change detection via hash comparison

## Rate Limiting & Performance

### API Quotas
- Gemini 1.5 Flash: High rate limits for free tier
- Request batching: Process multiple attachments per contact
- Async processing: Non-blocking webhook responses

### Performance Optimizations
- Background task processing
- Parallel document processing (up to 3 attachments per contact)
- Efficient text extraction pipelines
- Minimal memory footprint

### Monitoring
- Request/response logging
- Processing time metrics
- Error rate tracking
- API usage monitoring

## Skills Processing Logic

### Extraction Process
1. **Document Discovery**: Find resume-like attachments
2. **Text Extraction**: Convert documents to plain text
3. **Content Hashing**: Check cache for previous processing
4. **LLM Processing**: Send to Gemini for skills extraction
5. **Result Validation**: Parse and validate JSON response
6. **Skills Merging**: Combine with existing contact skills

### Skills Deduplication
- Case-insensitive skill comparison
- Whitespace normalization
- Addition-only policy (no skill removal)
- Preserve existing skill formatting

### Quality Assurance
- Confidence scoring for extraction quality
- Multiple document aggregation
- Error handling for processing failures
- Fallback to manual processing when needed

## Configuration Management

### Environment Variables
```bash
# LLM Configuration
OPENAI_API_KEY=your_gemini_api_key
OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
OPENAI_MODEL=gemini-1.5-flash

# Processing Configuration
MAX_FILE_SIZE_MB=10
ALLOWED_FILE_TYPES=pdf,doc,docx
ENABLE_CACHE=true
CACHE_TTL_HOURS=24
```

### Model Switching
The system supports switching between different models by changing:
- `OPENAI_MODEL`: Model identifier
- `OPENAI_BASE_URL`: API endpoint
- `OPENAI_API_KEY`: Authentication credentials

### Alternative Models
Compatible with any OpenAI-compatible API:
- OpenRouter models
- Together.ai models
- Local LLM endpoints (LM Studio, Ollama)
- Azure OpenAI

## Security Considerations

### API Key Management
- Environment variable storage
- No hardcoded credentials
- Secure key rotation support
- API key validation on startup

### Content Security
- Document size limits
- File type restrictions
- Content sanitization
- No persistent storage of document content

### Privacy Protection
- No logging of resume content
- Anonymized error reporting
- GDPR-compliant processing
- Secure content disposal

## Troubleshooting

### Common Issues
1. **API Authentication Errors**: Check `OPENAI_API_KEY` format
2. **Rate Limiting**: Implement exponential backoff
3. **JSON Parsing Errors**: Validate prompt engineering
4. **Document Processing Failures**: Check file format support

### Debug Configuration
```bash
DEBUG=true
LOG_LEVEL=DEBUG
```

### Monitoring Endpoints
- `/health`: Service health including LLM connectivity
- Structured logs: Request tracing and performance metrics
- Error aggregation: Centralized error reporting

## Future Enhancements

### Planned Features
- Multi-language resume support
- Skill taxonomy standardization
- Confidence-based filtering
- Batch processing optimization

### Scalability Options
- Redis-based caching
- Database-backed skill storage
- Distributed processing
- Advanced retry mechanisms
