# 🚦 API Rate Limiting Guide

## Overview

The testing suite now includes intelligent rate limiting to handle Google's API limits gracefully.

## Google API Limits

- **Free Tier**: 15 requests per minute
- **Our Setting**: 8-10 requests per minute (conservative approach)
- **Auto-retry**: Built into LangChain with exponential backoff

## Rate Limiting Features

### 🔧 **Automatic Rate Limiting**
- Tracks API requests over a 60-second window
- Automatically waits when approaching limits
- Prevents API quota exhaustion

### ⏱️ **Smart Timing**
- Conservative limits (8 requests/min by default)
- 1-second delays between tests
- Real-time rate limit monitoring

### 📊 **Sequential Processing**
- Tests run one at a time (no more concurrent processing)
- Predictable execution time
- Better error handling

## Updated Test Execution

### Quick Test (10 questions)
- **Time**: ~2-3 minutes
- **Rate**: 8 requests per minute
- **Safety**: Built-in delays

### Full Test (50 questions)
- **Time**: ~5-8 minutes  
- **Rate**: Conservative limiting
- **Progress**: Real-time status updates

## Configuration Options

### Command Line (run_tests.py)
```python
# Default: 8 requests per minute
runner = TestRunner(df, rate_limit_requests=8)
```

### Streamlit Interface
```python
# Configurable slider: 5-12 requests/min
rate_limit = st.slider("API Rate Limit", 5, 12, 8)
```

### Manual Override
```python
# For paid API tiers
runner = TestRunner(df, rate_limit_requests=25)  # Higher limits
```

## Rate Limiting Logic

```python
class RateLimiter:
    def __init__(self, max_requests=12, time_window=60):
        # Conservative default: 12 requests per 60 seconds
        
    async def wait_if_needed(self):
        # Automatically waits when approaching limits
        # Cleans up old requests
        # Records new requests
```

## Benefits

### ✅ **Reliability**
- No more "429 Rate Exceeded" errors
- Automatic retry with backoff
- Graceful degradation

### ✅ **Predictability** 
- Known execution times
- Progress tracking
- Clear status updates

### ✅ **Cost Control**
- Prevents API abuse
- Conservative usage
- Quota management

## Usage Examples

### Basic Usage
```bash
python run_tests.py
# Automatically rate limited to 8 requests/min
```

### Streamlit Dashboard
```bash
streamlit run src/testing/test_app.py
# Configure rate limits via UI slider
```

### Custom Rate Limits
```python
# For higher API tiers
runner = TestRunner(df, rate_limit_requests=20)
await runner.run_all_tests()
```

## Monitoring

### Console Output
```
⏳ Rate limit approached. Waiting 12.3 seconds...
🚀 Running Question 15 (15/50): Create a bar chart showing...
✅ PASS (Score: 87.5%, Time: 3.2s)
```

### Streamlit Progress
- Real-time progress bars
- Status updates
- Time estimates

## Best Practices

1. **Start with Quick Tests**: Test 10 questions first
2. **Use Conservative Limits**: Default 8 req/min works well
3. **Monitor Progress**: Watch for rate limit warnings
4. **Plan for Time**: Full tests take 5-8 minutes
5. **Save Results**: Auto-save prevents data loss

## Troubleshooting

### Still Getting Rate Limit Errors?
- Reduce `rate_limit_requests` to 5-6
- Check for other API usage
- Wait longer between tests

### Tests Taking Too Long?
- Use quick tests for development
- Run full tests during breaks
- Consider upgrading API tier

### Need Faster Testing?
- Upgrade to paid Google API tier
- Increase `rate_limit_requests`
- Use batch processing (if available)

---

**Rate limiting ensures reliable, consistent testing while respecting API limits!** 🚦✨
