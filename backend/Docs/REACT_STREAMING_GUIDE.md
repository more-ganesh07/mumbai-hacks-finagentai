# 🚀 React Streaming Integration Guide

## Backend Endpoint

**New Streaming Endpoint:** `/chatbot_query_stream`

**Old Non-Streaming Endpoint:** `/chatbot_query` (still available)

---

## React Implementation

### Option 1: Using Fetch API with EventSource-like parsing

```javascript
const handleStreamingQuery = async (userQuery) => {
  const response = await fetch('http://localhost:8000/chatbot_query_stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ user_query: userQuery }),
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  let fullResponse = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop(); // Keep incomplete line in buffer

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const data = JSON.parse(line.slice(6));
          
          if (data.error) {
            console.error('Error:', data.error);
            break;
          }
          
          if (data.content) {
            fullResponse += data.content;
            // Update UI with streaming content
            setResponse(fullResponse);
          }
          
          if (data.done) {
            console.log('Streaming complete');
            break;
          }
        } catch (e) {
          console.error('Parse error:', e);
        }
      }
    }
  }
};
```

### Option 2: Using axios with responseType: 'stream'

```javascript
import axios from 'axios';

const handleStreamingQuery = async (userQuery) => {
  try {
    const response = await axios.post(
      'http://localhost:8000/chatbot_query_stream',
      { user_query: userQuery },
      {
        responseType: 'stream',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    let buffer = '';
    let fullResponse = '';

    response.data.on('data', (chunk) => {
      buffer += chunk.toString();
      const lines = buffer.split('\n');
      buffer = lines.pop();

      lines.forEach((line) => {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6));
            
            if (data.content) {
              fullResponse += data.content;
              setResponse(fullResponse); // Update React state
            }
            
            if (data.done) {
              console.log('Streaming complete');
            }
          } catch (e) {
            console.error('Parse error:', e);
          }
        }
      });
    });

    response.data.on('end', () => {
      console.log('Stream ended');
    });
  } catch (error) {
    console.error('Request error:', error);
  }
};
```

### Option 3: Complete React Component Example

```jsx
import React, { useState } from 'react';

function Chatbot() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setResponse('');
    setIsStreaming(true);

    try {
      const res = await fetch('http://localhost:8000/chatbot_query_stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_query: query }),
      });

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let fullResponse = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          setIsStreaming(false);
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop();

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              if (data.error) {
                setResponse(`Error: ${data.error}`);
                setIsStreaming(false);
                return;
              }
              
              if (data.content) {
                fullResponse += data.content;
                setResponse(fullResponse);
              }
              
              if (data.done) {
                setIsStreaming(false);
              }
            } catch (e) {
              console.error('Parse error:', e);
            }
          }
        }
      }
    } catch (error) {
      setResponse(`Error: ${error.message}`);
      setIsStreaming(false);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask about stocks..."
          disabled={isStreaming}
        />
        <button type="submit" disabled={isStreaming}>
          {isStreaming ? 'Streaming...' : 'Send'}
        </button>
      </form>
      
      <div className="response">
        {response}
        {isStreaming && <span className="cursor">▋</span>}
      </div>
    </div>
  );
}

export default Chatbot;
```

---

## Response Format

Each chunk from the server follows Server-Sent Events (SSE) format:

```
data: {"content": "chunk text", "done": false}

data: {"content": "", "done": true}
```

**Fields:**
- `content`: Text chunk (empty string when done)
- `done`: Boolean indicating if streaming is complete
- `error`: Error message (if any)

---

## Testing

### Test with curl:
```bash
curl -N -X POST http://localhost:8000/chatbot_query_stream \
  -H "Content-Type: application/json" \
  -d '{"user_query": "What is the price of TCS?"}'
```

### Test in browser console:
```javascript
fetch('http://localhost:8000/chatbot_query_stream', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ user_query: 'What is the price of TCS?' })
})
.then(res => {
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  
  function readChunk() {
    reader.read().then(({ done, value }) => {
      if (done) return;
      const text = decoder.decode(value);
      console.log(text);
      readChunk();
    });
  }
  readChunk();
});
```

---

## Notes

- ✅ Streaming works in real-time
- ✅ Memory is updated after streaming completes
- ✅ Works with tools (price, analysis, etc.)
- ✅ Fallback queries also work (non-streaming)
- ✅ Error handling included

---

**Your React frontend will now receive streaming responses! 🎉**

