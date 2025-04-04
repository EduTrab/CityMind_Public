import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

class MoondreamWrapper:
    def __init__(
        self,
        base_model: str = "vikhyatk/moondream2",
        revision: str = "2024-07-23",
        device: str = "cuda",
        finetuned_checkpoint: str = "./checkpoints/moondream-ft_16-1"
    ):
        self.dtype = torch.float16 if device == "cuda" else torch.float32
        self.device = device
        self.tokenizer = AutoTokenizer.from_pretrained(
            base_model,
            revision=revision,
            trust_remote_code=True
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            base_model,
            revision=revision,
            trust_remote_code=True,
            attn_implementation=("flash_attention_2" if device == "cuda" else None),
            torch_dtype=self.dtype,
            device_map={"": device},
        )
        if finetuned_checkpoint and os.path.isdir(finetuned_checkpoint):
            self.model = self.model.from_pretrained(
                finetuned_checkpoint,
                revision=revision,
                trust_remote_code=True,
                attn_implementation=("flash_attention_2" if device == "cuda" else None),
                torch_dtype=self.dtype,
                device_map={"": device},
            )
            print("checkpoints loaded")
        self.model.eval()
        print("Moondream loaded!")

    def query(
        self,
        image,
        question: str,
        num_beams: int = 4,
        no_repeat_ngram_size: int = 5,
        early_stopping: bool = True
    ) -> str:
        encoded_img = self.model.encode_image(image)
        md_answer = self.model.answer_question(
            encoded_img,
            question,
            tokenizer=self.tokenizer,
            num_beams=num_beams,
            no_repeat_ngram_size=no_repeat_ngram_size,
            early_stopping=early_stopping
        )
        return md_answer
