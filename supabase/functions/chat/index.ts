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
    const LOVABLE_API_KEY = Deno.env.get('LOVABLE_API_KEY');
    
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_ANON_KEY') ?? ''
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

    const response = await fetch('https://ai.gateway.lovable.dev/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${LOVABLE_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'google/gemini-2.5-flash',
        messages,
        tools: agentTools,
        tool_choice: 'auto',
      }),
    });

    const data = await response.json();
    let assistantMessage = data.choices[0].message;
    const agentsUsed: string[] = [];

    // Handle tool calls
    while (assistantMessage.tool_calls) {
      for (const toolCall of assistantMessage.tool_calls) {
        const result = executeToolCall(toolCall.function.name, JSON.parse(toolCall.function.arguments));
        agentsUsed.push(toolCall.function.name);
        
        messages.push(assistantMessage);
        messages.push({
          role: "tool",
          tool_call_id: toolCall.id,
          content: JSON.stringify(result)
        });
      }

      const followUp = await fetch('https://ai.gateway.lovable.dev/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${LOVABLE_API_KEY}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: 'google/gemini-2.5-flash',
          messages,
          tools: agentTools,
        }),
      });

      const followUpData = await followUp.json();
      assistantMessage = followUpData.choices[0].message;
    }

    await supabaseClient.from('messages').insert({
      conversation_id: conversationId,
      role: 'assistant',
      content: assistantMessage.content,
      metadata: { agents: agentsUsed }
    });

    return new Response(JSON.stringify({ content: assistantMessage.content, agentsUsed }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  } catch (error) {
    console.error('Error:', error);
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  }
});
