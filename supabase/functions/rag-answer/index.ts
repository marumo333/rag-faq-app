// Setup type definitions for built-in Supabase Runtime APIs
import "jsr:@supabase/functions-js/edge-runtime.d.ts"
// @ts-ignore Deno is provided by the Edge runtime
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

console.log("RAG Answer Edge Function started")

// @ts-ignore Deno is provided by the Edge runtime
// deno-lint-ignore no-unused-vars
Deno.serve(async (req: Request) => {
  // CORS対応（プリフライトリクエスト）
  if (req.method === 'OPTIONS') {
    return new Response('ok', {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST',
        'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
      }
    })
  }

  try {
    // 1. Authorization ヘッダーの確認
    const authHeader = req.headers.get('Authorization')
    if (!authHeader) {
      return new Response(
        JSON.stringify({ error: 'Missing authorization header' }),
        { status: 401, headers: { 'Content-Type': 'application/json' } }
      )
    }

    // 2. JWT トークンを抽出
    const token = authHeader.replace('Bearer ', '')

    // 3. Supabase クライアントを作成してJWT検証
    // @ts-ignore Deno is provided by the Edge runtime
    const supabaseUrl = Deno.env.get('SUPABASE_URL') ?? ''
    // @ts-ignore Deno is provided by the Edge runtime
    const supabaseAnonKey = Deno.env.get('SUPABASE_ANON_KEY') ?? ''
    
    const supabase = createClient(supabaseUrl, supabaseAnonKey)
    
    // JWTを使ってユーザー情報を取得
    const { data: { user }, error: authError } = await supabase.auth.getUser(token)
    
    if (authError || !user) {
      console.error('Authentication error:', authError)
      return new Response(
        JSON.stringify({ error: 'Invalid or expired token' }),
        { status: 401, headers: { 'Content-Type': 'application/json' } }
      )
    }

    console.log('Authenticated user for answer:', user.id, user.email)

    // 4. Python API のURL取得
    // @ts-ignore Deno is provided by the Edge runtime
    const pythonApiUrl = Deno.env.get('PYTHON_API_URL')
    
    // 5. リクエストボディを取得
    const requestBody = await req.text()

    // 6. Python API に転送
    console.log(`Forwarding request to: ${pythonApiUrl}/answer`)
    
    const response = await fetch(`${pythonApiUrl}/answer`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-User-Id': user.id,
        'X-User-Email': user.email || '',
      },
      body: requestBody
    })

    // 7. Python API のレスポンスを返す
    const responseData = await response.text()
    
    return new Response(responseData, {
      status: response.status,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
      }
    })

  } catch (error) {
    console.error('Edge Function error (answer):', error)
    return new Response(
      JSON.stringify({ 
        error: 'Internal server error',
        message: (error as Error).message 
      }),
      { 
        status: 500, 
        headers: { 'Content-Type': 'application/json' } 
      }
    )
  }
})

