import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useRef, useState } from "react";
import { Send, Sparkles } from "lucide-react";
import { PageShell } from "@/components/urja/PageShell";
import { GlassCard } from "@/components/urja/GlassCard";

export const Route = createFileRoute("/chat")({
  head: () => ({
    meta: [
      { title: "Chatbot — Urja" },
      { name: "description", content: "Ask natural-language questions across every Urja agent." },
    ],
  }),
  component: Chat,
});

type Msg = { id: string; role: "user" | "assistant"; text: string; ts: string };

const SUGGESTIONS: { group: string; prompts: string[] }[] = [
  {
    group: "Ask CellSentry",
    prompts: [
      "Which cobalt suppliers exceed HHI threshold?",
      "Trace lithium sourcing for cell batch C-8814.",
    ],
  },
  {
    group: "Ask FleetMind",
    prompts: [
      "Which 10 diesel vehicles should I electrify first?",
      "OEM lead times for medium-duty EVs.",
    ],
  },
  {
    group: "Ask CarbonPulse",
    prompts: [
      "Am I on pace for SBTi Scope-1?",
      "Route-level carbon impact for Depot 3.",
    ],
  },
  {
    group: "Ask Fleet Guardian",
    prompts: [
      "RUL forecast for battery B-2041.",
      "Any voltage anomalies in the last 24h?",
    ],
  },
];

function nowStamp() {
  return new Date().toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" });
}

function Chat() {
  const [messages, setMessages] = useState<Msg[]>([
    {
      id: "welcome",
      role: "assistant",
      text: "I'm Urja. Ask me about supply-chain risk, battery health, electrification opportunities, or your net-zero trajectory.",
      ts: nowStamp(),
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const send = async (text: string) => {
    const t = text.trim();
    if (!t || loading) return;
    setMessages((m) => [...m, { id: crypto.randomUUID(), role: "user", text: t, ts: nowStamp() }]);
    setInput("");
    setLoading(true);
    // TODO: replace with real chat API call
    await new Promise((r) => setTimeout(r, 900));
    setMessages((m) => [
      ...m,
      {
        id: crypto.randomUUID(),
        role: "assistant",
        text:
          "Live agent connection pending — this is a UI preview. Once the chat API is wired, your question will be routed across CellSentry, FleetMind, CarbonPulse, and Fleet Guardian, and the combined answer will stream here.",
        ts: nowStamp(),
      },
    ]);
    setLoading(false);
  };

  return (
    <PageShell orbs="subtle">
      <div className="mx-auto flex h-[calc(100vh-72px)] max-w-[1280px] gap-6 px-6 py-8">
        {/* Suggestions */}
        <aside className="hidden w-[260px] shrink-0 flex-col gap-4 overflow-y-auto pr-1 lg:flex">
          <div className="eyebrow">Suggested prompts</div>
          {SUGGESTIONS.map((s) => (
            <div key={s.group}>
              <div className="mb-2 text-[12px] font-medium text-[color:var(--color-text-secondary)]">
                {s.group}
              </div>
              <div className="flex flex-col gap-2">
                {s.prompts.map((p) => (
                  <button
                    key={p}
                    onClick={() => send(p)}
                    className="glass glass-hover rounded-[12px] px-3 py-2.5 text-left text-[13px] text-[color:var(--color-text-primary)] transition-colors"
                  >
                    {p}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </aside>

        {/* Chat column */}
        <div className="flex min-w-0 flex-1 flex-col">
          <div className="mb-4 flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-[color:var(--color-accent)]" />
            <span className="eyebrow">Urja Chat</span>
          </div>

          <div className="flex-1 overflow-y-auto pr-2">
            <div className="flex flex-col gap-4">
              {messages.map((m) => (
                <MessageBubble key={m.id} msg={m} />
              ))}
              {loading && (
                <div className="flex justify-start">
                  <div className="glass rounded-[16px] px-4 py-3">
                    <TypingDots />
                  </div>
                </div>
              )}
              <div ref={endRef} />
            </div>
          </div>

          {/* Input */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              send(input);
            }}
            className="mt-4"
          >
            <div className="glass flex items-center gap-2 rounded-full py-2 pl-5 pr-2">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask across supply, assets, and carbon…"
                className="min-w-0 flex-1 bg-transparent py-2 text-[15px] outline-none placeholder:text-[color:var(--color-text-tertiary)]"
              />
              <button
                type="submit"
                disabled={!input.trim() || loading}
                className="flex h-10 w-10 items-center justify-center rounded-full text-white transition-all disabled:opacity-40"
                style={{ background: "#5b5fed" }}
                onMouseEnter={(e) => {
                  if (!e.currentTarget.disabled) {
                    e.currentTarget.style.boxShadow = "0 0 20px rgba(91,95,237,0.5)";
                  }
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.boxShadow = "none";
                }}
              >
                <Send className="h-4 w-4" />
              </button>
            </div>
          </form>
        </div>
      </div>
    </PageShell>
  );
}

function MessageBubble({ msg }: { msg: Msg }) {
  const isUser = msg.role === "user";
  return (
    <div className={isUser ? "flex justify-end" : "flex justify-start"}>
      <div className="max-w-[75%]">
        <div
          className="rounded-[16px] px-4 py-3 text-[14.5px] leading-[1.55]"
          style={
            isUser
              ? {
                  background: "rgba(91,95,237,0.18)",
                  border: "1px solid rgba(91,95,237,0.35)",
                  color: "#f5f5f7",
                }
              : {
                  background: "rgba(255,255,255,0.04)",
                  border: "1px solid rgba(255,255,255,0.08)",
                  backdropFilter: "blur(20px)",
                }
          }
        >
          {msg.text}
        </div>
        <div
          className={`mt-1 text-[11px] text-[color:var(--color-text-tertiary)] ${
            isUser ? "text-right" : "text-left"
          }`}
        >
          {msg.ts}
        </div>
      </div>
    </div>
  );
}

function TypingDots() {
  return (
    <div className="flex items-center gap-1.5">
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          className="h-1.5 w-1.5 rounded-full bg-[color:var(--color-text-secondary)]"
          style={{ animation: `typing-pulse 1.2s ease-in-out ${i * 0.15}s infinite` }}
        />
      ))}
    </div>
  );
}

// GlassCard import kept to preserve consistent bundling patterns
void GlassCard;
