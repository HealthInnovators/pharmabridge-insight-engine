import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";
import { agentTools, executeToolCall } from "./agentTools.ts";

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const { conversationId, message, history } = await req.json();
    console.log('Request Body:', { conversationId, message, history });
    const GROQ_API_KEY = Deno.env.get('GROQ_API_KEY'); // Changed from OPENAI_API_KEY
    console.log('GROQ_API_KEY:', GROQ_API_KEY ? ('Set and starts with ' + GROQ_API_KEY.substring(0, 5) + '...') : 'Not Set');
    
    if (!GROQ_API_KEY) {
      return new Response(JSON.stringify({ error: 'GROQ_API_KEY is not set in environment variables.' }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }

    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? '' // Changed to use SERVICE_ROLE_KEY
    );

    const systemPrompt = `You are Pharmabridge AI, a drug repurposing intelligence assistant. You have access to multiple specialized agents:
- IQVIA Insights: Market data and trends
- Patent Landscape: Patent status and FTO analysis
- Clinical Trials: Trial information
- EXIM Trends: Trade data
- Internal Knowledge: Company research
- Web Intelligence: Scientific publications

Analyze the user's question and use the appropriate tools to gather comprehensive information. Synthesize the results into a clear, actionable response.`;

    const messages = [
      { role: "system", content: systemPrompt },
      ...history.slice(-10).map((m: any) => ({ role: m.role, content: m.content })),
      { role: "user", content: message }
    ];

    const response = await fetch('https://api.groq.com/openai/v1/chat/completions', { // Changed API endpoint to Groq
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${GROQ_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'llama-3.3-70b-versatile', // Changed model to Groq's llama-3.3-70b-versatile
        messages,
        tools: agentTools,
        tool_choice: 'auto',
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('AI Gateway initial response not OK:', response.status, errorText);
      throw new Error(`AI Gateway initial response not OK: ${response.status} - ${errorText}`);
    }
    const data = await response.json();
    console.log('AI Gateway Initial Response:', data);

    if (!data.choices || data.choices.length === 0 || !data.choices[0].message) {
      console.error('AI Gateway initial response missing expected data:', data);
      throw new Error('AI Gateway initial response missing expected choices data.');
    }
    let assistantMessage = data.choices[0].message;
    const agentsUsed: string[] = [];

    // Handle tool calls
    while (assistantMessage.tool_calls) {
      for (const toolCall of assistantMessage.tool_calls) {
        const result = executeToolCall(toolCall.function.name, JSON.parse(toolCall.function.arguments));
        console.log(`Tool Call Result for ${toolCall.function.name}:`, result);
        agentsUsed.push(toolCall.function.name);
        
        messages.push(assistantMessage);
        messages.push({
          role: "tool",
          tool_call_id: toolCall.id,
          content: JSON.stringify(result)
        });
      }

      const followUp = await fetch('https://api.groq.com/openai/v1/chat/completions', { // Changed API endpoint to Groq
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${GROQ_API_KEY}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: 'llama-3.3-70b-versatile', // Changed model to Groq's llama-3.3-70b-versatile
          messages,
          tools: agentTools,
        }),
      });

      if (!followUp.ok) {
        const errorText = await followUp.text();
        console.error('AI Gateway follow-up response not OK:', followUp.status, errorText);
        throw new Error(`AI Gateway follow-up response not OK: ${followUp.status} - ${errorText}`);
      }
      const followUpData = await followUp.json();
      console.log('AI Gateway Follow-up Response:', followUpData);

      if (!followUpData.choices || followUpData.choices.length === 0 || !followUpData.choices[0].message) {
        console.error('AI Gateway follow-up response missing expected data:', followUpData);
        throw new Error('AI Gateway follow-up response missing expected choices data.');
      }
      assistantMessage = followUpData.choices[0].message;
    }

    console.log('Attempting to insert assistant message into Supabase:', { conversation_id: conversationId, role: 'assistant', content: assistantMessage.content, metadata: { agents: agentsUsed } });
    const { data: insertData, error: insertError } = await supabaseClient.from('messages').insert({
      conversation_id: conversationId,
      role: 'assistant',
      content: assistantMessage.content,
      metadata: { agents: agentsUsed }
    });

    if (insertError) {
      console.error('Supabase Insert Error:', insertError);
      throw new Error(`Failed to insert assistant message: ${insertError.message}`);
    }
    console.log('Supabase Insert Successful:', insertData);

    return new Response(JSON.stringify({ content: assistantMessage.content, agentsUsed }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  } catch (error) {
    console.error('Error:', error);
    return new Response(JSON.stringify({ error: error instanceof Error ? error.message : String(error) }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  }
});
