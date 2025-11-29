// API service for KiteInfi backend integration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * Market Chatbot - Synchronous endpoint
 * @param {string} userQuery - The user's query
 * @returns {Promise<{response: string}>}
 */
export async function marketChatbotSync(userQuery) {
    try {
        const response = await fetch(`${API_BASE_URL}/market_chatbot/sync`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ user_query: userQuery }),
        });

        if (!response.ok) {
            let errorBody = '';
            try {
                errorBody = await response.text();
            } catch (e) {
                // Ignore error reading body
            }
            throw new Error(
                `Server error ${response.status}${errorBody ? `: ${errorBody}` : ''}`
            );
        }

        const data = await response.json();

        // Validate response structure
        if (!data || typeof data.response !== 'string') {
            throw new Error('Invalid response format from server');
        }

        return data;
    } catch (error) {
        console.error('Market chatbot sync error:', error);
        throw error;
    }
}

/**
 * Portfolio Chatbot - Synchronous endpoint
 * @param {string} userQuery - The user's query
 * @returns {Promise<{response: string}>}
 */
export async function portfolioChatbotSync(userQuery) {
    try {
        const response = await fetch(`${API_BASE_URL}/portfolio_chatbot/sync`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ user_query: userQuery }),
        });

        if (!response.ok) {
            let errorBody = '';
            try {
                errorBody = await response.text();
            } catch (e) {
                // Ignore error reading body
            }
            throw new Error(
                `Server error ${response.status}${errorBody ? `: ${errorBody}` : ''}`
            );
        }

        const data = await response.json();

        // Validate response structure
        if (!data || typeof data.response !== 'string') {
            throw new Error('Invalid response format from server');
        }

        return data;
    } catch (error) {
        console.error('Portfolio chatbot sync error:', error);
        throw error;
    }
}

/**
 * Portfolio Chatbot Stream - Initialize streaming connection (triggers Kite login)
 * @param {string} userQuery - The user's query
 * @param {Function} onChunk - Callback function for each chunk of data
 * @param {Function} onComplete - Callback function when stream completes
 * @param {Function} onError - Callback function for errors
 */
export async function portfolioChatbotStream(userQuery, onChunk, onComplete, onError) {
    try {
        const response = await fetch(`${API_BASE_URL}/portfolio_chatbot/stream`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ user_query: userQuery }),
        });

        if (!response.ok) {
            let errorBody = '';
            try {
                errorBody = await response.text();
            } catch (e) {
                // Ignore error reading body
            }
            throw new Error(
                `Server error ${response.status}${errorBody ? `: ${errorBody}` : ''}`
            );
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();

            if (done) {
                if (onComplete) onComplete();
                break;
            }

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    try {
                        const data = JSON.parse(line.slice(6));
                        if (data.error) {
                            if (onError) onError(new Error(data.error));
                            return;
                        }
                        if (data.done) {
                            if (onComplete) onComplete();
                            return;
                        }
                        if (data.content && onChunk) {
                            onChunk(data.content);
                        }
                    } catch (e) {
                        console.error('Error parsing SSE data:', e);
                    }
                }
            }
        }
    } catch (error) {
        console.error('Portfolio chatbot stream error:', error);
        if (onError) onError(error);
        throw error;
    }
}

/**
 * Portfolio Report - Generate and email portfolio report
 * @returns {Promise<{status: string, message: string}>}
 */
export async function generatePortfolioReport() {
    try {
        const response = await fetch(`${API_BASE_URL}/portfolio_report`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            let errorBody = '';
            try {
                errorBody = await response.text();
            } catch (e) {
                // Ignore error reading body
            }
            throw new Error(
                `Server error ${response.status}${errorBody ? `: ${errorBody}` : ''}`
            );
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Portfolio report error:', error);
        throw error;
    }
}
