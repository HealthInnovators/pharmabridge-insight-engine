import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ChatMessage } from "@/components/ChatMessage";
import { AgentStatus } from "@/components/AgentStatus";
import { ConversationList } from "@/components/ConversationList";
import { useToast } from "@/hooks/use-toast";
import { Send, LogOut, Menu, X } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Sheet, SheetContent } from "@/components/ui/sheet";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  metadata?: any;
}

const Index = () => {
  const [user, setUser] = useState<any>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [currentConversationId, setCurrentConversationId] = useState<string>();
  const [activeAgent, setActiveAgent] = useState<string>();
  const [completedAgents, setCompletedAgents] = useState<string[]>([]);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();
  const { toast } = useToast();

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (!session) {
        navigate("/auth");
      } else {
        setUser(session.user);
      }
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
      if (!session) {
        navigate("/auth");
      } else {
        setUser(session.user);
      }
    });

    return () => subscription.unsubscribe();
  }, [navigate]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSignOut = async () => {
    await supabase.auth.signOut();
  };

  const loadConversation = async (conversationId: string) => {
    const { data, error } = await supabase
      .from("messages")
      .select("*")
      .eq("conversation_id", conversationId)
      .order("created_at", { ascending: true });

    if (error) {
      console.error("Error loading messages:", error);
      return;
    }

    setMessages((data || []) as Message[]);
    setCurrentConversationId(conversationId);
    setIsSidebarOpen(false);
  };

  const createNewConversation = async (title: string) => {
    const { data, error } = await supabase
      .from("conversations")
      .insert({ title, user_id: user.id })
      .select()
      .single();

    if (error) {
      console.error("Error creating conversation:", error);
      return null;
    }

    return data;
  };

  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput("");
    setIsLoading(true);
    setCompletedAgents([]);

    try {
      let conversationId = currentConversationId;

      if (!conversationId) {
        const newConv = await createNewConversation(
          userMessage.substring(0, 50) + (userMessage.length > 50 ? "..." : "")
        );
        if (!newConv) throw new Error("Failed to create conversation");
        conversationId = newConv.id;
        setCurrentConversationId(conversationId);
      }

      const { error: userMsgError } = await supabase
        .from("messages")
        .insert({
          conversation_id: conversationId,
          role: "user",
          content: userMessage,
        });

      if (userMsgError) throw userMsgError;

      const { data: allMessages } = await supabase
        .from("messages")
        .select("*")
        .eq("conversation_id", conversationId)
        .order("created_at", { ascending: true });

      setMessages((allMessages || []) as Message[]);
      const backendUrl = import.meta.env.VITE_BACKEND_URL as string | undefined;
      let agentsUsed: string[] | undefined;
      let reportId: string | undefined;

      if (backendUrl) {
        const resp = await fetch(`${backendUrl}/api/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            conversationId,
            message: userMessage,
            history: (allMessages || []).map((m) => ({ id: m.id, role: m.role, content: m.content, metadata: m.metadata || null })),
          }),
        });

        if (!resp.ok) {
          const t = await resp.text();
          throw new Error(`Backend error: ${t}`);
        }
        const data = await resp.json();
        const assistantMessage = data.content as string;
        agentsUsed = data.agentsUsed as string[] | undefined;
        reportId = data.report_id as string | undefined;

        const { error: assistantMsgError } = await supabase
          .from("messages")
          .insert({
            conversation_id: conversationId,
            role: "assistant",
            content: assistantMessage,
            metadata: { agents: agentsUsed, report_id: reportId },
          });
        if (assistantMsgError) throw assistantMsgError;
      } else {
        // Fallback: Call Groq API directly
        const groqResponse = await fetch('https://api.groq.com/openai/v1/chat/completions', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${import.meta.env.VITE_GROQ_API_KEY}`
          },
          body: JSON.stringify({
            model: 'llama-3.3-70b-versatile',
            messages: [
              ...(allMessages?.map(msg => ({
                role: msg.role,
                content: msg.content
              })) || []),
              { role: 'user', content: userMessage }
            ],
            temperature: 0.7,
            max_tokens: 2000
          })
        });

        if (!groqResponse.ok) {
          const error = await groqResponse.text();
          throw new Error(`Groq API error: ${error}`);
        }
        const groqData = await groqResponse.json();
        const assistantMessage = groqData.choices[0].message.content;

        const { error: assistantMsgError } = await supabase
          .from("messages")
          .insert({
            conversation_id: conversationId,
            role: "assistant",
            content: assistantMessage,
          });
        if (assistantMsgError) throw assistantMsgError;
      }

      // Refresh messages after either path
      const { data: updatedMessages } = await supabase
        .from("messages")
        .select("*")
        .eq("conversation_id", conversationId)
        .order("created_at", { ascending: true });

      setMessages((updatedMessages || []) as Message[]);
      if (agentsUsed) setCompletedAgents(agentsUsed);
    } catch (error: any) {
      console.error("Error:", error);
      toast({
        variant: "destructive",
        title: "Error",
        description: error.message || "Failed to send message",
      });
    } finally {
      setIsLoading(false);
      setActiveAgent(undefined);
    }
  };

  const handleNewConversation = () => {
    setCurrentConversationId(undefined);
    setMessages([]);
    setCompletedAgents([]);
    setIsSidebarOpen(false);
  };

  if (!user) return null;

  return (
    <div className="h-screen flex bg-background">
      {/* Desktop Sidebar */}
      <div className="hidden md:block w-80 border-r bg-card">
        <div className="h-14 border-b flex items-center justify-between px-4">
          <h1 className="text-lg font-semibold gradient-primary bg-clip-text text-transparent">
            Pharmabridge AI
          </h1>
          <Button variant="ghost" size="icon" onClick={handleSignOut}>
            <LogOut className="w-4 h-4" />
          </Button>
        </div>
        <ConversationList
          currentConversationId={currentConversationId}
          onSelectConversation={loadConversation}
          onNewConversation={handleNewConversation}
        />
      </div>

      {/* Mobile Sidebar */}
      <Sheet open={isSidebarOpen} onOpenChange={setIsSidebarOpen}>
        <SheetContent side="left" className="w-80 p-0">
          <div className="h-14 border-b flex items-center justify-between px-4">
            <h1 className="text-lg font-semibold gradient-primary bg-clip-text text-transparent">
              Pharmabridge AI
            </h1>
            <Button variant="ghost" size="icon" onClick={handleSignOut}>
              <LogOut className="w-4 h-4" />
            </Button>
          </div>
          <ConversationList
            currentConversationId={currentConversationId}
            onSelectConversation={loadConversation}
            onNewConversation={handleNewConversation}
          />
        </SheetContent>
      </Sheet>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        <div className="h-14 border-b flex items-center px-4 justify-between">
          <div className="flex items-center gap-2">
            <Button 
              variant="ghost" 
              size="icon" 
              className="md:hidden" 
              onClick={() => setIsSidebarOpen(true)}
            >
              <Menu className="w-5 h-5" />
            </Button>
            <h2 className="text-sm font-medium text-muted-foreground">
              Drug Repurposing Intelligence
            </h2>
          </div>
          <Button variant="ghost" size="icon" onClick={handleSignOut} className="md:hidden">
            <LogOut className="w-4 h-4" />
          </Button>
        </div>

        <ScrollArea className="flex-1 p-4">
          {messages.length === 0 ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-center max-w-2xl">
                <h2 className="text-3xl font-bold mb-4 gradient-primary bg-clip-text text-transparent">
                  Welcome to Pharmabridge AI
                </h2>
                <p className="text-muted-foreground mb-6">
                  Your conversational intelligence platform for drug repurposing research.
                  Ask complex questions and get comprehensive insights from multiple data sources.
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                  <div className="p-3 rounded-lg bg-muted/50 text-left">
                    <p className="font-medium mb-1">Market Analysis</p>
                    <p className="text-muted-foreground">Get IQVIA market data and trends</p>
                  </div>
                  <div className="p-3 rounded-lg bg-muted/50 text-left">
                    <p className="font-medium mb-1">Patent Intelligence</p>
                    <p className="text-muted-foreground">Check patent status and FTO</p>
                  </div>
                  <div className="p-3 rounded-lg bg-muted/50 text-left">
                    <p className="font-medium mb-1">Clinical Trials</p>
                    <p className="text-muted-foreground">Search ongoing and completed trials</p>
                  </div>
                  <div className="p-3 rounded-lg bg-muted/50 text-left">
                    <p className="font-medium mb-1">Trade Data</p>
                    <p className="text-muted-foreground">Analyze EXIM trends and volumes</p>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div>
              {messages.map((msg) => (
                <ChatMessage key={msg.id} {...msg} />
              ))}
              {isLoading && (
                <AgentStatus activeAgent={activeAgent} completedAgents={completedAgents} />
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </ScrollArea>

        <div className="border-t p-4">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="flex gap-2"
          >
            <Input
              placeholder="Ask about drug repurposing opportunities..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={isLoading}
              className="flex-1"
            />
            <Button type="submit" disabled={isLoading || !input.trim()}>
              <Send className="w-4 h-4" />
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Index;
