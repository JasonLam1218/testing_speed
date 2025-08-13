/**
 * Vercel Edge Function with TRUE STREAMING support
 * Enables real first byte time measurement
 */

export const config = {
    runtime: 'edge',
    regions: ['sfo1', 'iad1'],
    maxDuration: 30
}

export default async function handler(request) {
    const corsHeaders = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
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

        // ⚡ CREATE STREAMING RESPONSE
        const stream = new ReadableStream({
            async start(controller) {
                const startTime = Date.now()
                
                try {
                    // 🔥 SEND FIRST BYTE IMMEDIATELY WITH METADATA
                    const firstBytePayload = JSON.stringify({
                        type: 'first_byte',
                        timestamp: startTime,
                        server_time: Date.now(),
                        method: 'edge_function_streaming'
                    }) + '\n'
                    
                    controller.enqueue(new TextEncoder().encode(firstBytePayload))

                    // 📡 CALL GEMINI STREAMING API
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
                        const errorPayload = JSON.stringify({
                            type: 'error',
                            error: 'Gemini API error',
                            status: geminiResponse.status,
                            timestamp: Date.now()
                        }) + '\n'
                        controller.enqueue(new TextEncoder().encode(errorPayload))
                        controller.close()
                        return
                    }

                    // 🌊 STREAM GEMINI RESPONSE CHUNKS
                    const reader = geminiResponse.body.getReader()
                    let contentBuffer = ''
                    let chunkIndex = 0

                    while (true) {
                        const { done, value } = await reader.read()
                        if (done) break

                        chunkIndex++
                        const chunkText = new TextDecoder().decode(value)
                        contentBuffer += chunkText

                        // 📦 SEND CHUNK WITH METADATA
                        const chunkPayload = JSON.stringify({
                            type: 'content_chunk',
                            chunk_index: chunkIndex,
                            chunk_size: value.length,
                            chunk_text: chunkText,
                            timestamp: Date.now(),
                            elapsed_ms: Date.now() - startTime
                        }) + '\n'
                        
                        controller.enqueue(new TextEncoder().encode(chunkPayload))
                    }

                    // 🏁 SEND FINAL COMPLETION METADATA
                    const completionPayload = JSON.stringify({
                        type: 'completion',
                        total_chunks: chunkIndex,
                        total_time_ms: Date.now() - startTime,
                        content_length: contentBuffer.length,
                        timestamp: Date.now(),
                        method: 'edge_function_streaming'
                    }) + '\n'
                    
                    controller.enqueue(new TextEncoder().encode(completionPayload))

                } catch (error) {
                    const errorPayload = JSON.stringify({
                        type: 'error',
                        error: error.message,
                        timestamp: Date.now()
                    }) + '\n'
                    controller.enqueue(new TextEncoder().encode(errorPayload))
                } finally {
                    controller.close()
                }
            }
        })

        return new Response(stream, {
            headers: {
                'Content-Type': 'application/x-ndjson', // Newline-delimited JSON
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Transfer-Encoding': 'chunked',
                ...corsHeaders
            }
        })

    } catch (error) {
        console.error('Edge Function streaming error:', error)
        return new Response(JSON.stringify({
            error: 'Internal server error',
            message: error.message,
            method: 'edge_function_streaming'
        }), {
            status: 500,
            headers: { 'Content-Type': 'application/json', ...corsHeaders }
        })
    }
}
