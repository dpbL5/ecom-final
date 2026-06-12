import { FormEvent, useMemo, useRef, useState } from "react";
import { Bot, MessageCircle, Send, UserRound, X } from "lucide-react";

import { api } from "../api";
import { useAuth } from "../contexts/AuthContext";
import type { AIProductSuggestion } from "../types";

type MessageRole = "assistant" | "user";

interface ChatMessage {
  id: string;
  role: MessageRole;
  text: string;
  source?: string;
  products?: AIProductSuggestion[];
}

function nextId() {
  return typeof crypto !== "undefined" && "randomUUID" in crypto
    ? crypto.randomUUID()
    : `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

export default function AIChatbot() {
  const { session, token } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState("");
  const [isThinking, setIsThinking] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      role: "assistant",
      text: "Hi, I can help you find products by need, type or keyword. Try: laptop gaming, fashion shoes, or a book for students.",
      source: "AI advisor demo"
    }
  ]);
  const formRef = useRef<HTMLFormElement>(null);

  const canSend = useMemo(() => input.trim().length > 1 && !isThinking, [input, isThinking]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const query = input.trim();
    if (!query || isThinking) return;

    setMessages((current) => [...current, { id: nextId(), role: "user", text: query }]);
    setInput("");
    setIsThinking(true);

    try {
      let customerId: string | undefined;
      if (session && token) {
        const profiles = await api.listProfiles(token);
        customerId = profiles.find((profile) => profile.user_id === session.user.id)?.id;
      }
      const response = await api.askAIAdvisor(token || undefined, query, customerId);
      setMessages((current) => [
        ...current,
        {
          id: nextId(),
          role: "assistant",
          text: response.answer,
          source: response.source,
          products: response.suggestions
        }
      ]);
    } catch {
      setMessages((current) => [
        ...current,
        {
          id: nextId(),
          role: "assistant",
          text: "I could not reach the search service right now. Please check whether the backend or API gateway is running.",
          source: "Search service request failed"
        }
      ]);
    } finally {
      setIsThinking(false);
      formRef.current?.querySelector("input")?.focus();
    }
  }

  if (!isOpen) {
    return (
      <button className="chatbot-fab" type="button" onClick={() => setIsOpen(true)} title="Open AI product advisor">
        <span className="fab-pulse" />
        <MessageCircle size={26} />
      </button>
    );
  }

  return (
    <section className="chatbot-panel" aria-label="AI product advisor">
      <header className="chatbot-header">
        <div className="chatbot-header-info">
          <Bot size={24} />
          <div>
            <strong>AI Product Advisor</strong>
            <small>Search + recommendation demo</small>
          </div>
        </div>
        <button className="chatbot-close" type="button" onClick={() => setIsOpen(false)} title="Close chatbot">
          <X size={18} />
        </button>
      </header>

      <div className="chatbot-messages">
        {messages.map((message) => (
          <article className={`chat-msg chat-msg-${message.role}`} key={message.id}>
            <div className="chat-avatar">
              {message.role === "assistant" ? <Bot size={16} /> : <UserRound size={16} />}
            </div>
            <div className="chat-bubble">
              <div className="chat-text">{message.text}</div>
              {message.source ? <span className="chat-source">{message.source}</span> : null}
              {message.products?.length ? (
                <div className="chat-products">
                  {message.products.map((product) => (
                    <div className="chat-product-card" key={`${message.id}-${product.product_id}`}>
                      <strong>{product.name}</strong>
                      <span>{product.product_type} / {product.sku}</span>
                      <small>{product.reason || product.brand || "Catalog product"}</small>
                    </div>
                  ))}
                </div>
              ) : null}
            </div>
          </article>
        ))}
        {isThinking ? (
          <article className="chat-msg chat-msg-assistant">
            <div className="chat-avatar"><Bot size={16} /></div>
            <div className="chat-bubble">
              <div className="chat-typing"><span /><span /><span /></div>
            </div>
          </article>
        ) : null}
      </div>

      <form className="chatbot-input" onSubmit={handleSubmit} ref={formRef}>
        <input
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Ask for a product..."
          aria-label="Ask for a product"
        />
        <button className="chatbot-send" type="submit" disabled={!canSend} title="Send">
          <Send size={18} />
        </button>
      </form>
    </section>
  );
}
