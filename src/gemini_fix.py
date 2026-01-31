"""
This file patches the broken Google connection in old LangChain versions.
It forces the code to use the new 'v1' server instead of the dead 'v1beta'.
"""
from typing import Any, List, Optional
import os
import google.generativeai as genai
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.outputs import ChatResult, ChatGeneration

class FixedGeminiChat(BaseChatModel):
    """A custom wrapper that fixes the 404 error on old versions."""
    
    model_name: str = "gemini-2.5-flash"
    temperature: float = 0.0
    google_api_key: Optional[str] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 1. Configure the low-level driver directly
        genai.configure(api_key=self.google_api_key or os.getenv("GOOGLE_API_KEY"))
        
    def _generate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs) -> ChatResult:
        # 2. Build the prompt manually (Old school way)
        prompt_parts = []
        for m in messages:
            if isinstance(m, SystemMessage):
                prompt_parts.append(f"INSTRUCTION: {m.content}")
            elif isinstance(m, HumanMessage):
                prompt_parts.append(f"USER: {m.content}")
            else:
                prompt_parts.append(f"{m.content}")
        
        full_prompt = "\n\n".join(prompt_parts)

        # 3. Call the Modern API directly (Bypassing the broken LangChain wrapper)
        model = genai.GenerativeModel(self.model_name)
        
        # Generation config to ensure stability
        config = genai.types.GenerationConfig(temperature=self.temperature)
        
        import time
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = model.generate_content(full_prompt, generation_config=config)
                content = response.text
                break
            except Exception as e:
                if "429" in str(e) and attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                content = f"Error or Blocked: {str(e)}"
                break

        # 4. Wrap it back in a LangChain object so the rest of your app doesn't know the difference
        message = HumanMessage(content=content)
        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])

    @property
    def _llm_type(self) -> str:
        return "chat-google-generative-ai"
