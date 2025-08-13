export default async function handler(req, res) {
  const serverStartTime = Date.now()
  
  // 🔥 SET TTFB HEADERS IMMEDIATELY (before any processing)
  res.setHeader('Access-Control-Allow-Origin', '*')
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS')
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-Start-Time')
  res.setHeader('Access-Control-Expose-Headers', 'X-First-Byte-Time, X-Server-Start')
  res.setHeader('X-First-Byte-Time', serverStartTime.toString())
  res.setHeader('X-Server-Start', serverStartTime.toString())
  res.setHeader('Content-Type', 'text/event-stream')
  res.setHeader('Cache-Control', 'no-cache')
  res.setHeader('Connection', 'keep-alive')

  if (req.method === 'OPTIONS') {
    res.status(200).end()
    return
  }

  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' })
    return
  }

  try {
    const { prompt } = req.body
    if (!prompt) {
      res.status(400).json({ error: 'Prompt is required' })
      return
    }

    const geminiApiKey = process.env.GEMINI_API_KEY
    if (!geminiApiKey) {
      res.status(500).json({ error: 'Gemini API key not configured' })
      return
    }

    // ✅ IMMEDIATE SSE RESPONSE (bypasses buffering)
    const firstEvent = `event: first_byte\ndata: ${JSON.stringify({
      type: 'first_byte',
      server_time: serverStartTime,
      method: 'serverless_sse',
      cold_start_detected: serverStartTime > 1000
    })}\n\n`
    res.write(firstEvent) // Immediate write

    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 25000)

    try {
      // ✅ PROPERLY CALL GEMINI STREAMING API
      const geminiResponse = await fetch(
        `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:streamGenerateContent?key=${geminiApiKey}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'User-Agent': 'Vercel-Serverless-Streaming/1.0'
          },
          body: JSON.stringify({
            contents: [{ parts: [{ text: prompt }] }],
            generationConfig: {
              temperature: 0.7,
              topK: 40,
              topP: 0.95,
              maxOutputTokens: 4096,
              thinkingConfig: {
                thinkingBudget: 0,
                includeThoughts: false
              }
            }
          }),
          signal: controller.signal
        }
      )

      clearTimeout(timeoutId)

      if (!geminiResponse.ok) {
        const errorEvent = `event: error\ndata: ${JSON.stringify({
          type: 'error',
          error: 'Gemini API error',
          status: geminiResponse.status,
          timestamp: Date.now()
        })}\n\n`
        res.write(errorEvent)
        res.end()
        return
      }

      // ✅ PROPERLY STREAM GEMINI'S RESPONSE AS SSE
      const reader = geminiResponse.body.getReader()
      const decoder = new TextDecoder()
      let chunkIndex = 0
      let contentBuffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value, { stream: true })
        const lines = chunk.split('\n').filter(line => line.trim())

        for (const line of lines) {
          try {
            // ✅ Parse Gemini's streaming JSON response
            const parsed = JSON.parse(line)
            if (parsed.candidates && parsed.candidates[0]?.content?.parts) {
              const text = parsed.candidates[0].content.parts[0].text || ''
              contentBuffer += text

              // 📦 SEND ACTUAL CONTENT CHUNK AS SSE EVENT
              const contentEvent = `event: content\ndata: ${JSON.stringify({
                type: 'content_chunk',
                chunk_index: chunkIndex++,
                chunk_text: text,
                timestamp: Date.now(),
                elapsed_ms: Date.now() - serverStartTime
              })}\n\n`
              res.write(contentEvent)
            }
          } catch (parseError) {
            console.error('Failed to parse Gemini chunk:', parseError)
          }
        }
      }

      // 🏁 SEND COMPLETION EVENT
      const completeEvent = `event: complete\ndata: ${JSON.stringify({
        type: 'completion',
        total_chunks: chunkIndex,
        total_time_ms: Date.now() - serverStartTime,
        content_length: contentBuffer.length,
        timestamp: Date.now(),
        method: 'serverless_function_sse',
        execution_time_ms: Date.now() - serverStartTime
      })}\n\n`
      res.write(completeEvent)
      res.end()

    } catch (fetchError) {
      clearTimeout(timeoutId)
      const errorEvent = `event: error\ndata: ${JSON.stringify({
        type: 'error',
        error: fetchError.name === 'AbortError' ? 'Request timeout' : fetchError.message,
        timestamp: Date.now()
      })}\n\n`
      res.write(errorEvent)
      res.end()
    }

  } catch (error) {
    console.error('Serverless streaming error:', error)
    const errorEvent = `event: error\ndata: ${JSON.stringify({
      type: 'error',
      error: 'Internal server error',
      message: error.message,
      execution_time_ms: Date.now() - serverStartTime,
      timestamp: Date.now()
    })}\n\n`
    try {
      res.write(errorEvent)
      res.end()
    } catch (writeError) {
      console.error('Failed to write error response:', writeError)
    }
  }
}
