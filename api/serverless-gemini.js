/**
 * Vercel Serverless Function for Gemini API
 * Optimized for complex tasks with longer execution times
 */

export default async function handler(req, res) {
  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*')
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS')
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type')
  res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate')

  // Handle preflight requests
  if (req.method === 'OPTIONS') {
    res.status(200).end()
    return
  }

  // Only allow POST requests
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' })
    return
  }

  const startTime = Date.now()

  try {
    // Parse request
    const { prompt } = req.body
    if (!prompt) {
      res.status(400).json({ error: 'Prompt is required' })
      return
    }

    // Get Gemini API key from environment
    const geminiApiKey = process.env.GEMINI_API_KEY
    if (!geminiApiKey) {
      res.status(500).json({ error: 'Gemini API key not configured' })
      return
    }

    // Enhanced timeout for serverless functions
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 25000) // 25 second timeout

    try {
      // Call Gemini API with timeout
      const geminiResponse = await fetch(
        `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${geminiApiKey}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'User-Agent': 'Vercel-Serverless-Function/1.0',
          },
          body: JSON.stringify({
            contents: [
              {
                parts: [
                  {
                    text: prompt,
                  },
                ],
              },
            ],
            generationConfig: {
              temperature: 0.7,
              topK: 40,
              topP: 0.95,
              maxOutputTokens: 4096,
            },
          }),
          signal: controller.signal,
        }
      )

      clearTimeout(timeoutId)

      if (!geminiResponse.ok) {
        const errorText = await geminiResponse.text()
        console.error('Gemini API error:', {
          status: geminiResponse.status,
          statusText: geminiResponse.statusText,
          body: errorText
        })
        
        res.status(geminiResponse.status).json({
          error: 'Gemini API error',
          status: geminiResponse.status,
          details: errorText
        })
        return
      }

      // Parse Gemini response
      const geminiData = await geminiResponse.json()
      const generatedText = geminiData.candidates?.[0]?.content?.parts?.[0]?.text || ''

      // Calculate execution metrics
      const executionTime = Date.now() - startTime

      // Return enhanced response with metrics
      res.status(200).json({
        success: true,
        response: generatedText,
        method: 'serverless_function',
        metrics: {
          execution_time_ms: executionTime,
          timestamp: new Date().toISOString(),
          region: process.env.VERCEL_REGION || 'unknown',
          character_count: generatedText.length,
          token_usage: geminiData.usageMetadata || null,
        },
        // Cold start detection (approximate)
        is_cold_start: executionTime > 1000,
      })

    } catch (fetchError) {
      clearTimeout(timeoutId)
      
      if (fetchError.name === 'AbortError') {
        res.status(504).json({
          error: 'Request timeout',
          message: 'Gemini API request timed out',
          method: 'serverless_function'
        })
      } else {
        throw fetchError
      }
    }

  } catch (error) {
    console.error('Serverless Function error:', {
      message: error.message,
      stack: error.stack,
      timestamp: new Date().toISOString()
    })
    
    const executionTime = Date.now() - startTime
    
    res.status(500).json({
      error: 'Internal server error',
      message: error.message,
      method: 'serverless_function',
      execution_time_ms: executionTime,
      // Include error type for debugging
      error_type: error.name || 'UnknownError',
    })
  }
}
