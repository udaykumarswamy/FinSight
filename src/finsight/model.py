import os
import time
from typing import Type, List, Optional, Dict

from pydantic import BaseModel
from openai import APIConnectionError, RateLimitError

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, BaseMessage, ToolMessage
from langchain_core.tools import BaseTool

import tiktoken

from finsight.prompts import DEFAULT_SYSTEM_PROMPT

class ConversationHistory:
    def __init__(self):
        # store LangChain message objects
        self.messages: List[BaseMessage] = []

    def add_user_message(self, message: str):
        self.messages.append(HumanMessage(content=message))

    def add_ai_message(self, message):
        # Normalize pydantic model -> AIMessage, accept AIMessage or str
        if isinstance(message, BaseModel):
            text = getattr(message, "answer", None) or getattr(message, "text", None) or str(message)
            ai_msg = AIMessage(content=str(text))
        elif isinstance(message, AIMessage):
            ai_msg = message
        else:
            ai_msg = AIMessage(content=str(message))
        self.messages.append(ai_msg)

        # If AIMessage contains tool_calls, append ToolMessage(s) as needed
        if hasattr(ai_msg, "tool_calls") and ai_msg.tool_calls:
            for tool_call in ai_msg.tool_calls:
                output = None
                try:
                    output = tool_call.get("function", {}).get("output")
                except Exception:
                    output = None
                tm = ToolMessage(
                    tool_call_id=tool_call.get("id"),
                    name=tool_call.get("name"),
                    content=str(output or ""),
                )
                self.messages.append(tm)

    def add_tool_message(self, tool_call_id: str, name: str, content: str):
        # Optionally truncate very large tool outputs before storing
        max_tool_chars = 20000
        if len(content) > max_tool_chars:
            content = content[:max_tool_chars] + "\n\n[truncated]"
        self.messages.append(ToolMessage(tool_call_id=tool_call_id, name=name, content=content))

    def get_recent_messages(self, limit: int = 5) -> List[BaseMessage]:
        return self.messages[-limit:] if limit else list(self.messages)

    def token_count(self, encoding_name: str = "cl100k_base") -> int:
        enc = tiktoken.get_encoding(encoding_name)
        text = "\n".join(
            f"{m.__class__.__name__}: {getattr(m, 'content', str(m))}" for m in self.messages
        )
        return len(enc.encode(text))

    def compress_if_needed(
        self,
        llm_model: str = "gpt-3.5-turbo",
        token_threshold: int = 8000,
        keep_recent: int = 6,
        api_key: Optional[str] = None,
    ):
        """
        If token_count exceeds token_threshold, summarize the older portion using a cheaper model
        and replace it with a single SystemMessage summary. If summarization fails, truncate.
        """
        try:
            if self.token_count() <= token_threshold:
                return

            # Prepare head (to summarize) and tail (keep recent messages)
            head = self.messages[:-keep_recent] if len(self.messages) > keep_recent else []
            tail = self.messages[-keep_recent:] if len(self.messages) >= keep_recent else list(self.messages)

            if not head:
                return

            head_text = "\n".join(
                f"{m.__class__.__name__}: {getattr(m, 'content', str(m))}" for m in head
            )

            if not head_text.strip():
                # Nothing to summarize, fallback to truncation
                self.messages = tail
                return

            summarization_prompt = (
                "Summarize the following conversation history into a concise bulleted summary "
                "that preserves key facts (tickers, numeric results, decisions, actions). "
                "Keep it short (<= 300 tokens):\n\n" + head_text
            )

            summarizer = ChatOpenAI(model=llm_model, temperature=0, api_key=api_key or os.getenv("OPENAI_API_KEY"))
            # retries for RateLimitError
            retries = 3
            backoff = 1.0
            summary_text = None
            for attempt in range(retries):
                try:
                    resp = summarizer.invoke([SystemMessage(content="You are a concise summarizer."), HumanMessage(content=summarization_prompt)])
                    summary_text = getattr(resp, "content", str(resp))
                    break
                except RateLimitError:
                    time.sleep(backoff)
                    backoff *= 2
                except Exception:
                    break

            if summary_text:
                summary_system = SystemMessage(content=f"[Summarized history]\n{summary_text}")
                self.messages = [summary_system] + tail
            else:
                # fallback: keep only recent tail
                self.messages = tail

        except Exception:
            # final safe fallback: keep last `keep_recent` messages
            self.messages = self.messages[-keep_recent:]

def call_llm(
    prompt: str,
    history: Optional[ConversationHistory] = None,
    model: str = "gpt-4.1",
    system_prompt: Optional[str] = None,
    output_schema: Optional[Type[BaseModel]] = None,
    tools: Optional[List[BaseTool]] = None,
    history_token_threshold: int = 8000,
    max_retries: int = 3,
):
    final_system_prompt = system_prompt if system_prompt else DEFAULT_SYSTEM_PROMPT

    # compress history if it's large
    if history:
        history.compress_if_needed(llm_model="gpt-3.5-turbo", token_threshold=history_token_threshold, keep_recent=6)

    # Build messages
    messages: List[BaseMessage] = [SystemMessage(content=final_system_prompt)]
    if history:
        messages.extend(history.get_recent_messages(limit=50))  # limit number of messages included
    user_msg = HumanMessage(content=prompt)
    messages.append(user_msg)

    llm = ChatOpenAI(model=model, temperature=0, api_key=os.getenv("OPENAI_API_KEY"))

    runnable = llm
    if output_schema:
        runnable = llm.with_structured_output(output_schema, method="function_calling")
    elif tools:
        runnable = llm.bind_tools(tools)

    attempt = 0
    backoff = 1.0
    while True:
        try:
            response = runnable.invoke(messages)

            # update history
            if history:
                if isinstance(response, BaseModel):
                    history.add_ai_message(response)
                elif isinstance(response, AIMessage):
                    history.add_ai_message(response)
                else:
                    history.add_ai_message(str(response))

            if output_schema and isinstance(response, BaseModel):
                return response
            if isinstance(response, AIMessage):
                return response
            return AIMessage(content=str(response))

        except (APIConnectionError, RateLimitError) as e:
            attempt += 1
            if attempt > max_retries:
                raise
            time.sleep(backoff)
            backoff *= 2
        except Exception:
            # other exceptions bubble up
            raise

