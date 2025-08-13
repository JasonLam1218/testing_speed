export default async function handler(request) {
  const serverStartTime = Date.now()
  
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, X-Start-Time',
    'Access-Control-Expose-Headers': 'X-First-Byte-Time, X-Server-Start', // ✅ EXPOSE TTFB HEADERS
    'X-First-Byte-Time': serverStartTime.toString(), // 🔥 IMMEDIATE TTFB HEADER
    'X-Server-Start': serverStartTime.toString(),
    'Content-Type': 'text/event-stream', // ✅ USE SSE FORMAT
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive'
  }

  if (request.method === 'OPTIONS') {
    return new Response(null, { status: 200, headers: corsHeaders })
  }

  if (request.method !== 'POST') {
    return new Response(JSON.stringify({ error: 'Method not allowed' }), {
      status: 405,
      headers: { 'Content-Type': 'application/json', ...corsHeaders }
    })
  }

  try {
    const { prompt } = await request.json()
    if (!prompt) {
      return new Response(JSON.stringify({ error: 'Prompt is required' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json', ...corsHeaders }
      })
    }

    const geminiApiKey = process.env.GEMINI_API_KEY
    if (!geminiApiKey) {
      return new Response(JSON.stringify({ error: 'Gemini API key not configured' }), {
        status: 500,
        headers: { 'Content-Type': 'application/json', ...corsHeaders }
      })
    }

    // ✅ CREATE SSE STREAM (bypasses JSON buffering)
    const stream = new ReadableStream({
      async start(controller) {
        try {
          // 🔥 SEND IMMEDIATE SSE EVENT
          const firstEvent = `event: first_byte\ndata: ${JSON.stringify({
            type: 'first_byte',
            server_time: serverStartTime,
            method: 'edge_sse'
          })}\n\n`
          controller.enqueue(new TextEncoder().encode(firstEvent))

          // ✅ PROPERLY CALL GEMINI STREAMING API
          const geminiResponse = await fetch(
            `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:streamGenerateContent?key=${geminiApiKey}`,
            {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                contents: [{ parts: [{ text: prompt }] }],
                generationConfig: {
                  temperature: 0.1,
                  maxOutputTokens: 4096,
                  topK: 40,
                  topP: 0.95,
                  thinkingConfig: {
                    thinkingBudget: 0,
                    includeThoughts: false
                  }
                }
              }),
              signal: AbortSignal.timeout(25000)
            }
          )

          if (!geminiResponse.ok) {
            const errorEvent = `event: error\ndata: ${JSON.stringify({
              type: 'error',
              error: 'Gemini API error',
              status: geminiResponse.status,
              timestamp: Date.now()
            })}\n\n`
            controller.enqueue(new TextEncoder().encode(errorEvent))
            controller.close()
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
                  controller.enqueue(new TextEncoder().encode(contentEvent))
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
            method: 'edge_function_sse'
          })}\n\n`
          controller.enqueue(new TextEncoder().encode(completeEvent))

        } catch (error) {
          const errorEvent = `event: error\ndata: ${JSON.stringify({
            type: 'error',
            error: error.message,
            timestamp: Date.now()
          })}\n\n`
          controller.enqueue(new TextEncoder().encode(errorEvent))
        } finally {
          controller.close()
        }
      }
    })

    return new Response(stream, { headers: corsHeaders })

  } catch (error) {
    console.error('Edge Function streaming error:', error)
    return new Response(JSON.stringify({
      error: 'Internal server error',
      message: error.message,
      method: 'edge_function_sse'
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json', ...corsHeaders }
    })
  }
}
