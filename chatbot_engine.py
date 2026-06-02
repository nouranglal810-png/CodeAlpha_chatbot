"""
====================================================
 Smart Chatbot Engine  --  CodeAlpha Internship
====================================================
This module is the "brain" of the chatbot.
It uses 3 layers to answer any question:
  Layer 1: Pattern Matching  (greetings, math, time)
  Layer 2: Wikipedia Search  (knowledge questions)
  Layer 3: Web Search via DuckDuckGo (everything else)

Key Concepts: if-elif, functions, loops, input/output,
              dictionaries, API calls, error handling
====================================================
"""

import re
import datetime

# Wikipedia with error handling for import
try:
    import wikipedia
    WIKI_AVAILABLE = True
except ImportError:
    WIKI_AVAILABLE = False

# DuckDuckGo search - try new 'ddgs' package first, then old name
try:
    from ddgs import DDGS
    DDG_AVAILABLE = True
except ImportError:
    try:
        from duckduckgo_search import DDGS
        DDG_AVAILABLE = True
    except ImportError:
        DDG_AVAILABLE = False


# ──────────────────────────────────────────────
#  LAYER 1 : Pattern Matching (if-elif + functions)
# ──────────────────────────────────────────────
def pattern_match(message):
    """
    Checks user input against predefined patterns.
    Uses if-elif chains and regex for flexible matching.
    Returns (response_text, matched) tuple.
    """
    msg = message.lower().strip()

    # --- Greetings ---
    if msg in ("hello", "hi", "hey", "hola", "namaste"):
        return "Hey there! How can I help you today?", True

    # --- How are you ---
    elif any(phrase in msg for phrase in ["how are you", "how r u", "kaise ho"]):
        return "I'm doing great, thanks for asking! What can I help you with?", True

    # --- Bot identity ---
    elif any(phrase in msg for phrase in ["your name", "who are you", "what are you"]):
        return "I'm SmartBot - your AI assistant powered by web search! Ask me anything.", True

    # --- Thanks ---
    elif any(phrase in msg for phrase in ["thanks", "thank you", "shukriya", "dhanyavad"]):
        return "You're welcome! Happy to help.", True

    # --- Farewell ---
    elif msg in ("bye", "goodbye", "see you", "exit", "quit", "alvida"):
        return "Goodbye! Have an amazing day!", True

    # --- Current time ---
    elif any(phrase in msg for phrase in ["what time", "current time", "time now"]):
        now = datetime.datetime.now().strftime("%I:%M %p")
        return f"The current time is {now}.", True

    # --- Current date ---
    elif any(phrase in msg for phrase in ["what date", "today's date", "current date", "what day"]):
        today = datetime.datetime.now().strftime("%A, %B %d, %Y")
        return f"Today is {today}.", True

    # --- Math calculations ---
    elif msg.startswith("calculate ") or msg.startswith("calc "):
        expr = re.sub(r'^(calculate|calc)\s+', '', msg)
        try:
            # Only allow safe math characters
            if re.match(r'^[\d\s\+\-\*/\.\(\)]+$', expr):
                result = eval(expr)
                return f"The answer is: {result}", True
            else:
                return "I can only calculate basic math (e.g., 'calculate 5 + 3 * 2').", True
        except Exception:
            return "Sorry, I couldn't calculate that. Try something like 'calculate 10 * 5'.", True

    # --- Help ---
    elif msg in ("help", "help me", "what can you do"):
        return (
            "I can do a lot! Try these:\n"
            "- Ask me anything (e.g., 'What is quantum physics?')\n"
            "- Calculate math (e.g., 'calculate 15 * 7')\n"
            "- Ask the time or date\n"
            "- Search the web for latest info\n"
            "- Say hello, bye, or thanks!"
        ), True

    return None, False


# ──────────────────────────────────────────────
#  Helper: Clean up query text for search
# ──────────────────────────────────────────────
def extract_search_query(message):
    """
    Strips question prefixes so Wikipedia/web gets a clean topic.
    'What is quantum physics?' -> 'quantum physics'
    'Who is Elon Musk' -> 'Elon Musk'
    'Tell me about India' -> 'India'
    """
    msg_lower = message.lower().strip().rstrip("?").strip()

    prefixes = [
        "who is ", "who was ", "who are ",
        "what is ", "what is a ", "what is an ", "what is the ",
        "what are ", "what was ", "what were ",
        "tell me about ", "tell me about the ",
        "explain ", "explain the ", "explain me ",
        "define ", "meaning of ",
        "describe ", "describe the ",
        "search for ", "search ",
        "find ", "find me ",
        "look up ", "google ",
    ]

    for prefix in prefixes:
        if msg_lower.startswith(prefix):
            # Return the original case after removing prefix
            return message[len(prefix):].strip().rstrip("?").strip()

    return message.strip().rstrip("?").strip()


# ──────────────────────────────────────────────
#  LAYER 2 : Wikipedia Search (API + functions)
# ──────────────────────────────────────────────
def search_wikipedia(query):
    """
    Searches Wikipedia for knowledge-based questions.
    Returns a summary if found, None otherwise.
    Handles disambiguation by trying multiple approaches.
    """
    if not WIKI_AVAILABLE:
        return None

    if not query or len(query.strip()) < 2:
        return None

    clean_query = query.strip()

    try:
        wikipedia.set_lang("en")

        # Strategy 1: Direct summary
        try:
            summary = wikipedia.summary(clean_query, sentences=3, auto_suggest=True)
            if summary and len(summary) > 30:
                # Clean up any weird characters
                summary = summary.encode('ascii', 'ignore').decode('ascii')
                summary = re.sub(r'\s+', ' ', summary).strip()
                return f"{summary}\n\n(Source: Wikipedia)"
        except wikipedia.exceptions.DisambiguationError as e:
            # Strategy 2: Try first option from disambiguation
            if e.options:
                for option in e.options[:3]:
                    try:
                        summary = wikipedia.summary(option, sentences=3, auto_suggest=False)
                        if summary and len(summary) > 30:
                            summary = summary.encode('ascii', 'ignore').decode('ascii')
                            summary = re.sub(r'\s+', ' ', summary).strip()
                            return f"{summary}\n\n(Source: Wikipedia)"
                    except Exception:
                        continue
        except wikipedia.exceptions.PageError:
            # Strategy 3: Search and try first result
            try:
                search_results = wikipedia.search(clean_query, results=3)
                for result_title in search_results:
                    try:
                        summary = wikipedia.summary(result_title, sentences=3, auto_suggest=False)
                        if summary and len(summary) > 30:
                            summary = summary.encode('ascii', 'ignore').decode('ascii')
                            summary = re.sub(r'\s+', ' ', summary).strip()
                            return f"{summary}\n\n(Source: Wikipedia)"
                    except Exception:
                        continue
            except Exception:
                pass

    except Exception:
        pass

    return None


# ──────────────────────────────────────────────
#  LAYER 3 : Web Search via DuckDuckGo (API)
# ──────────────────────────────────────────────
def search_web(query):
    """
    Searches the web using DuckDuckGo when Wikipedia
    doesn't have the answer. Returns clean, formatted results.
    """
    if not DDG_AVAILABLE:
        return "Web search is not available. Please install: pip install duckduckgo-search"

    try:
        import warnings
        warnings.filterwarnings("ignore")

        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))

        if results:
            response_parts = []
            for i, r in enumerate(results, 1):
                title = r.get('title', 'No title')
                body = r.get('body', 'No description')
                link = r.get('href', '')

                # Clean up text - remove garbled characters
                title = title.encode('ascii', 'ignore').decode('ascii').strip()
                body = body.encode('ascii', 'ignore').decode('ascii').strip()

                # Truncate very long bodies
                if len(body) > 200:
                    body = body[:200].rsplit(' ', 1)[0] + "..."

                if title and body:
                    response_parts.append(f"{i}. **{title}**\n{body}")
                    if link:
                        response_parts.append(f"   Link: {link}")

            if response_parts:
                return "Here's what I found on the web:\n\n" + "\n\n".join(response_parts)

    except Exception as e:
        return "I tried searching the web but encountered an error. Please try again."

    return "I couldn't find anything for that query. Try rephrasing your question."


# ──────────────────────────────────────────────
#  MAIN FUNCTION : get_response (combines all layers)
# ──────────────────────────────────────────────
def get_response(user_input):
    """
    Main function that processes user input through all 3 layers:
    1. First tries pattern matching (instant)
    2. Then tries Wikipedia (knowledge)
    3. Finally falls back to web search (everything else)

    Returns a dict with 'response' and 'source' keys.
    """
    if not user_input or not user_input.strip():
        return {
            "response": "Please type something so I can help you!",
            "source": "system"
        }

    message = user_input.strip()

    # --- LAYER 1: Pattern Matching ---
    response, matched = pattern_match(message)
    if matched:
        return {"response": response, "source": "pattern"}

    # --- Extract clean search query ---
    search_query = extract_search_query(message)

    # --- LAYER 2: Wikipedia ---
    wiki_result = search_wikipedia(search_query)
    if wiki_result:
        return {"response": wiki_result, "source": "wikipedia"}

    # --- LAYER 3: Web Search ---
    # Use the full message for web search (more context = better results)
    web_result = search_web(message)
    return {"response": web_result, "source": "web"}
