/**
 * FIXED: True streaming Serverless Function for accurate TTFB measurement
 */
export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*')
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS')
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type')
  res.setHeader('Cache-Control', 'no-cache')

  if (req.method === 'OPTIONS') {
      res.status(200).end()
      return
  }

  if (req.method !== 'POST') {
      res.status(405).json({ error: 'Method not allowed' })
      return
  }

  const startTime = Date.now()

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

      // ✅ SET STREAMING HEADERS
      res.setHeader('Content-Type', 'application/x-ndjson')
      res.setHeader('Transfer-Encoding', 'chunked')
      res.setHeader('Connection', 'keep-alive')

      // 🔥 SEND FIRST BYTE IMMEDIATELY
      const firstBytePayload = JSON.stringify({
          type: 'first_byte',
          timestamp: startTime,
          server_time: Date.now(),
          method: 'serverless_function_streaming',
          cold_start_detected: startTime > 1000
      }) + '\n'
      
      res.write(firstBytePayload)

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
              const errorPayload = JSON.stringify({
                  type: 'error',
                  error: 'Gemini API error',
                  status: geminiResponse.status,
                  timestamp: Date.now()
              }) + '\n'
              res.write(errorPayload)
              res.end()
              return
          }

          // ✅ PROPERLY STREAM GEMINI'S RESPONSE
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
                          
                          // 📦 SEND ACTUAL CONTENT CHUNK
                          const chunkPayload = JSON.stringify({
                              type: 'content_chunk',
                              chunk_index: chunkIndex++,
                              chunk_text: text,
                              timestamp: Date.now(),
                              elapsed_ms: Date.now() - startTime
                          }) + '\n'
                          
                          res.write(chunkPayload)
                      }
                  } catch (parseError) {
                      console.error('Failed to parse Gemini chunk:', parseError)
                  }
              }
          }

          // 🏁 SEND COMPLETION
          const completionPayload = JSON.stringify({
              type: 'completion',
              total_chunks: chunkIndex,
              total_time_ms: Date.now() - startTime,
              content_length: contentBuffer.length,
              timestamp: Date.now(),
              method: 'serverless_function_streaming',
              execution_time_ms: Date.now() - startTime
          }) + '\n'
          
          res.write(completionPayload)
          res.end()

      } catch (fetchError) {
          clearTimeout(timeoutId)
          if (fetchError.name === 'AbortError') {
              const timeoutPayload = JSON.stringify({
                  type: 'error',
                  error: 'Request timeout',
                  timestamp: Date.now()
              }) + '\n'
              res.write(timeoutPayload)
          } else {
              throw fetchError
          }
          res.end()
      }

  } catch (error) {
      console.error('Serverless streaming error:', error)
      const errorPayload = JSON.stringify({
          type: 'error',
          error: 'Internal server error',
          message: error.message,
          execution_time_ms: Date.now() - startTime,
          timestamp: Date.now()
      }) + '\n'
      
      try {
          res.write(errorPayload)
          res.end()
      } catch (writeError) {
          console.error('Failed to write error response:', writeError)
      }
  }
}
