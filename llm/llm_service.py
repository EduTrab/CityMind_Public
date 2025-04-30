import os
import torch
import google.generativeai as genai
import openai
import anthropic
import ollama
import io
import base64

from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
from openai import OpenAI
from llm.moondream_wrapper import MoondreamWrapper
from PIL import Image
from transformers import AutoTokenizer, AutoModelForCausalLM


class MultiLLMService:
    def __init__(
        self,
        models_to_query,
        openai_api_key=None,
        anthropic_api_key=None,
        google_genai_api_key=None,
        moondream_ft_ckpt_path: str = "./checkpoints/moondream-ft_17-1_10k-v2-epoch3",
        device: str = "cuda",
        md_revision: str = "2024-07-23",
    ):
        """
        Initialize the MultiLLMService with API keys.
        Note: API key checks are performed only when a query is made.
        """
        self.models_to_query = models_to_query
        self.openai_api_key = openai_api_key
        self.anthropic_api_key = anthropic_api_key
        self.google_genai_api_key = google_genai_api_key

        # Do not enforce API key existence at initialization.
        # Instead, we'll check for keys when sending queries.

        # Configure environment for OpenAI if key is provided.
        if self.openai_api_key:
            os.environ["OPENAI_API_KEY"] = self.openai_api_key
            openai.api_key = self.openai_api_key

        # Configure Google Generative AI if key is provided.
        if self.google_genai_api_key:
            genai.configure(api_key=self.google_genai_api_key)

        # Initialize Anthropic client if key is provided.
        if self.anthropic_api_key:
            self.anthropic_client = anthropic.Anthropic(api_key=self.anthropic_api_key)
        else:
            self.anthropic_client = None

        # Initialize Moondream wrapper if required.
        if "moondream-standard" in models_to_query:
            self.moondream_wrapper = MoondreamWrapper(
                base_model="vikhyatk/moondream2",
                revision=md_revision,
                device=device,
                finetuned_checkpoint=False,
            )
        if "moondream-finetuned" in models_to_query:
            self.moondream_wrapper = MoondreamWrapper(
                base_model="vikhyatk/moondream2",
                revision=md_revision,
                device=device,
                finetuned_checkpoint=moondream_ft_ckpt_path,
            )

    def compress_image(
        self,
        image_path: str,
        max_size: int = 5 * 1024 * 1024,
        max_dimension: int = 1024,
    ):
        with Image.open(image_path) as img:
            aspect_ratio = img.width / img.height
            if img.width > img.height:
                new_width = max_dimension
                new_height = int(new_width / aspect_ratio)
            else:
                new_height = max_dimension
                new_width = int(new_height * aspect_ratio)
            img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            buffer = io.BytesIO()
            img_format = img.format if img.format else "JPEG"
            img_resized.save(buffer, format=img_format)
            while buffer.getbuffer().nbytes > max_size and max_dimension > 256:
                max_dimension = int(max_dimension * 0.9)
                if img.width > img.height:
                    new_width = max_dimension
                    new_height = int(new_width / aspect_ratio)
                else:
                    new_height = max_dimension
                    new_width = int(new_height * aspect_ratio)
                img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                buffer = io.BytesIO()
                img_resized.save(buffer, format=img_format)
            return base64.b64encode(buffer.getvalue()).decode("utf-8"), img_format.lower()

    def _infer_moondream(self, image_path: str, prompt: str) -> str:
        image = Image.open(image_path)
        answer = self.moondream_wrapper.query(
            image=image,
            question=prompt,
            num_beams=4,
            no_repeat_ngram_size=5,
            early_stopping=True
        )
        return answer

    def _send_query_ollama(self, image_path: str, prompt: str, model: str) -> str:
        response = ollama.chat(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                    "images": [image_path]
                }
            ],
        )
        if isinstance(response, dict):
            return response.get("message", {}).get("content", "Error: No response received")
        return str(response)

    def _send_query_openai(self, image_path: str, prompt: str, model: str) -> str:
        if not self.openai_api_key:
            raise ValueError(f"Please insert your OpenAI API key for {model}.")
        with open(image_path, 'rb') as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                    ]
                }
            ]
        )
        return response.choices[0].message.content

    def _send_query_anthropic(self, image_path: str, prompt: str, model: str) -> str:
        if not self.anthropic_api_key:
            raise ValueError("Please insert your Anthropic API key for Claude-3.")
        image_data, img_format = self.compress_image(image_path)
        media_type = f"image/{img_format}"
        response = self.anthropic_client.messages.create(
            model=model,
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": image_data}}
                    ]
                }
            ]
        )
        return response.content[0].text

    def _send_query_moondream(self, image_path: str, prompt: str, model: str) -> str:
        return self._infer_moondream(image_path, prompt)

    def _send_query_gemini(self, image_path: str, prompt: str, model: str) -> str:
        if not self.google_genai_api_key:
            raise ValueError("Please insert your Google Gemini API key for Gemini-Reasining.")
        try:
            image = Image.open(image_path)
            # Resize image to have width of 512 pixels while maintaining aspect ratio
            # width, height = image.size
            # new_width = 512
            # new_height = int((new_width / width) * height)
            # image = image.resize((new_width, new_height))
            model_instance = genai.GenerativeModel("gemini-2.0-flash-thinking-exp-01-21")
            response = model_instance.generate_content([prompt, image])
            return response.text
        except Exception as e:
            return f"Error querying Google Gemini: {e}"

    def send_query(self, image_path: str, prompt: str, model: str = "gpt-4o") -> str:
        try:
            if model in ["llama3.2-vision", "llava", "qnguyen3/nanollava", "llava-phi3", "moondream"]:
                return self._send_query_ollama(image_path, prompt, model)
            elif model in ["gpt-4o", "gpt-4-turbo", "gpt-4o-mini"]:
                return self._send_query_openai(image_path, prompt, model)
            elif model == "claude-3-opus-20240229":
                return self._send_query_anthropic(image_path, prompt, model)
            elif model in ["moondream-standard", "moondream-finetuned"]:
                return self._send_query_moondream(image_path, prompt, model)
            elif model in ["gemini-reasoning","gemini-2.5-flash-preview-04-17", "gemini-2.0-flash-lite", "gemini-1.5-flash-002"]:
                return self._send_query_gemini(image_path, prompt, model)
            else:
                return "Error: Unsupported model specified."
        except Exception as e:
            return f"Error: {e}"

