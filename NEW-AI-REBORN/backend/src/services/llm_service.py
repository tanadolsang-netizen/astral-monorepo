"""
LLM Service — DeepSeek ผ่าน OpenRouter API + Hermes Memory
"""
import logging
import os
import json
import requests

logger = logging.getLogger("astral.llm")

# OpenRouter API
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "deepseek/deepseek-r1"


class LLMService:
    def __init__(self):
        self.token = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENROUTER_TOKEN")
        self.use_api = bool(self.token)

        if self.use_api:
            logger.info("Using DeepSeek via OpenRouter API")
        else:
            logger.warning("OPENROUTER_API_KEY not set — LLM will return None")

    def _get_hermes_memory(self) -> str:
        """อ่าน Hermes memory มาเป็น context"""
        try:
            from src.services.hermes_memory_service import read_entries
            memory_entries = read_entries("memory")
            user_entries = read_entries("user")
            
            context_parts = []
            if user_entries:
                context_parts.append("=== ข้อมูลผู้ใช้ ===")
                for e in user_entries[-10:]:
                    context_parts.append(f"- {e.content}")
            
            if memory_entries:
                context_parts.append("=== บันทึกก่อนหน้า ===")
                for e in memory_entries[-5:]:
                    context_parts.append(f"- {e.content}")
            
            return "\n".join(context_parts) if context_parts else ""
        except Exception as e:
            logger.warning(f"Hermes memory read failed: {e}")
            return ""

    def _save_to_hermes_memory(self, role: str, content: str, target: str = "memory"):
        """บันทึก conversation ลง Hermes memory"""
        try:
            from src.services.hermes_memory_service import append_entry
            prefix = "User" if role == "user" else "Assistant"
            append_entry(target, f"[{prefix}] {content[:500]}")
        except Exception as e:
            logger.warning(f"Hermes memory write failed: {e}")

    def generate(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.7,
                 use_memory: bool = True) -> str:
        """Generate text ผ่าน DeepSeek (OpenRouter)"""
        if not self.use_api:
            return None

        try:
            messages = []
            
            if use_memory:
                memory_context = self._get_hermes_memory()
                if memory_context:
                    messages.append({
                        "role": "system",
                        "content": f"Context from memory:\n{memory_context}"
                    })
            
            messages.append({"role": "user", "content": prompt})

            response = requests.post(
                OPENROUTER_API_URL,
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:8000",
                    "X-Title": "Astral",
                },
                json={
                    "model": OPENROUTER_MODEL,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                },
                timeout=60,
            )

            if response.status_code != 200:
                logger.error(f"OpenRouter API error {response.status_code}: {response.text[:200]}")
                return None

            data = response.json()
            choice = data["choices"][0]
            message = choice["message"]
            
            # DeepSeek R1 ใช้ reasoning field ถ้า content เป็น null ให้ใช้ reasoning
            reply = message.get("content") or message.get("reasoning") or ""
            
            if use_memory and reply:
                self._save_to_hermes_memory("user", prompt)
                self._save_to_hermes_memory("assistant", reply)
            
            return reply

        except Exception as e:
            logger.error(f"OpenRouter API error: {e}")
            return None

    def chat(self, messages: list[dict], max_tokens: int = 1000, temperature: float = 0.8) -> str:
        """Chat completion — รับ messages list เต็ม"""
        if not self.use_api:
            return None

        try:
            if not any(m.get("role") == "system" for m in messages):
                memory_context = self._get_hermes_memory()
                if memory_context:
                    messages = [{"role": "system", "content": f"Context:\n{memory_context}"}] + messages

            response = requests.post(
                OPENROUTER_API_URL,
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:8000",
                    "X-Title": "Astral",
                },
                json={
                    "model": OPENROUTER_MODEL,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                },
                timeout=60,
            )

            if response.status_code != 200:
                logger.error(f"OpenRouter API error {response.status_code}: {response.text[:200]}")
                return None

            data = response.json()
            message = data["choices"][0]["message"]
            return message.get("content") or message.get("reasoning") or ""

        except Exception as e:
            logger.error(f"OpenRouter API error: {e}")
            return None

    def generate_narrative(self, chart_data: dict, lang: str = "th") -> str:
        """Generate personalized astrology narrative"""
        if lang == "th":
            prompt = f"""คุณคือนักโหราศาสตร์ที่เชี่ยวชาญ วิเคราะห์ดวงชะตาต่อไปนี้และเขียน narrative ที่ลึกซึ้งเจาะจงบุคคล:

ดวงอาทิตย์: {chart_data.get('sun', '?')}
ดวงจันทร์: {chart_data.get('moon', '?')}
ลัคนา: {chart_data.get('ascendant', '?')}

เขียน 3 ย่อหน้า:
1. ภาพรวมตัวตนและบุคลิก
2. ความกลัวและเงาที่ซ่อนอยู่
3. บทเรียนชีวิตและทิศทางการเติบโต"""
        else:
            prompt = f"""You are an expert astrologer. Analyze this birth chart and write a deep, personalized narrative:

Sun: {chart_data.get('sun', '?')}
Moon: {chart_data.get('moon', '?')}
Ascendant: {chart_data.get('ascendant', '?')}

Write 3 paragraphs:
1. Core identity and personality
2. Hidden fears and shadows
3. Life lessons and growth direction"""

        return self.generate(prompt, max_tokens=2000, temperature=0.8)


llm_service = LLMService()
