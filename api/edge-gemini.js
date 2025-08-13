export default async function handler(request) {
  const serverStartTime = Date.now()
  
  // ✅ SOLUTION 1: Immediate headers + multiple content types
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, X-Start-Time',
    'Access-Control-Expose-Headers': 'X-First-Byte-Time, X-Server-Start, X-Processing-Time',
    'X-First-Byte-Time': serverStartTime.toString(),
    'X-Server-Start': serverStartTime.toString(),
    'X-Processing-Time': '0', // Will be updated
    'Content-Type': 'text/plain', // ✅ Use plain text instead of SSE
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive'
  }

  if (request.method === 'OPTIONS') {
    return new Response(null, { status: 200, headers: corsHeaders })
  }

  if (request.method !== 'POST') {
    return new Response('Method not allowed', { status: 405, headers: corsHeaders })
  }

  try {
    const { prompt } = await request.json()
    
    // ✅ SOLUTION 2: Send immediate response with processing indicator
    const stream = new ReadableStream({
      async start(controller) {
        try {
          // 🔥 IMMEDIATE FIRST BYTE - Plain text format
          const firstByte = `TTFB:${serverStartTime}\n`
          controller.enqueue(new TextEncoder().encode(firstByte))
          
          // Small delay to ensure first byte is sent
          await new Promise(resolve => setTimeout(resolve, 10))
          
          // Call Gemini API
          const geminiResponse = await fetch(
            `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:streamGenerateContent?key=${process.env.GEMINI_API_KEY}`,
            {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                contents: [{ parts: [{ text: prompt }] }],
                generationConfig: {
                  temperature: 0.1,
                  maxOutputTokens: 4096,
                  topK: 40,
                  topP: 0.95
                }
              }),
              signal: AbortSignal.timeout(25000)
            }
          )

          if (!geminiResponse.ok) {
            controller.enqueue(new TextEncoder().encode(`ERROR:${geminiResponse.status}\n`))
            controller.close()
            return
          }

          // Stream response
          const reader = geminiResponse.body.getReader()
          const decoder = new TextDecoder()
          let contentBuffer = ''

          while (true) {
            const { done, value } = await reader.read()
            if (done) break

            const chunk = decoder.decode(value, { stream: true })
            const lines = chunk.split('\n').filter(line => line.trim())

            for (const line of lines) {
              try {
                const parsed = JSON.parse(line)
                if (parsed.candidates?.[0]?.content?.parts) {
                  const text = parsed.candidates[0].content.parts[0].text || ''
                  contentBuffer += text
                  // Send content directly
                  controller.enqueue(new TextEncoder().encode(text))
                }
              } catch (parseError) {
                console.error('Parse error:', parseError)
              }
            }
          }

          // End marker
          controller.enqueue(new TextEncoder().encode(`\nEND:${Date.now() - serverStartTime}ms`))

        } catch (error) {
          controller.enqueue(new TextEncoder().encode(`ERROR:${error.message}\n`))
        } finally {
          controller.close()
        }
      }
    })

    return new Response(stream, { headers: corsHeaders })

  } catch (error) {
    return new Response(`ERROR: ${error.message}`, {
      status: 500,
      headers: corsHeaders
    })
  }
}
