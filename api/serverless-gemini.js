export default async function handler(req, res) {
  const serverStartTime = Date.now()
  
  // ✅ IMMEDIATE HEADERS
  res.setHeader('Access-Control-Allow-Origin', '*')
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS')
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-Start-Time')
  res.setHeader('Access-Control-Expose-Headers', 'X-First-Byte-Time, X-Server-Start')
  res.setHeader('X-First-Byte-Time', serverStartTime.toString())
  res.setHeader('X-Server-Start', serverStartTime.toString())
  res.setHeader('Content-Type', 'text/plain')
  res.setHeader('Cache-Control', 'no-cache')

  if (req.method === 'OPTIONS') {
    res.status(200).end()
    return
  }

  if (req.method !== 'POST') {
    res.status(405).send('Method not allowed')
    return
  }

  try {
    const { prompt } = req.body
    
    // 🔥 IMMEDIATE FIRST BYTE
    res.write(`TTFB:${serverStartTime}\n`)
    
    // Call Gemini API and stream response
    const geminiResponse = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:streamGenerateContent?key=${process.env.GEMINI_API_KEY}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ parts: [{ text: prompt }] }],
          generationConfig: {
            temperature: 0.7,
            topK: 40,
            topP: 0.95,
            maxOutputTokens: 4096
          }
        }),
        signal: AbortSignal.timeout(25000)
      }
    )

    if (!geminiResponse.ok) {
      res.write(`ERROR:${geminiResponse.status}\n`)
      res.end()
      return
    }

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
            res.write(text)
          }
        } catch (parseError) {
          console.error('Parse error:', parseError)
        }
      }
    }

    res.write(`\nEND:${Date.now() - serverStartTime}ms`)
    res.end()

  } catch (error) {
    res.write(`ERROR: ${error.message}`)
    res.end()
  }
}
