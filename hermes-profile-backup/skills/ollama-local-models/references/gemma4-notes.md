# Gemma 4 family — quick facts (from ollama.com/library/gemma4)

Google DeepMind's open model family. Multimodal (text + image; E2B/E4B also audio), reasoning-first with configurable thinking modes. Native `system` role support (new vs Gemma 3).

## Tags on Ollama

| Tag | Class | Notes |
|---|---|---|
| `gemma4:e2b` / `gemma4:e4b` | Edge ("effective" params) | On-device laptops/mobile |
| `gemma4:12b` | Workstation dense | ~7.4 GB Q4 download; deployed locally 2026-08-23 on RTX 5060 8 GB |
| `gemma4:26b` | MoE, 25.2B total / 3.8B active | 256K context |
| `gemma4:31b` | Dense flagship | 256K context |
| `gemma4:31b-cloud` | Ollama cloud variant | Runs remotely, no local VRAM |

Context windows: small models 128K; medium (26B/31B) 256K.

## Thinking mode

- Enable thinking: start system prompt with `<|think|>` token. Disable: omit it.
- With thinking on, output = internal reasoning then final answer, structured as `<|channel>thought\n[reasoning]<channel|>` [final answer].
- Non-E models with thinking OFF still emit an empty thought block before the answer.
- Multi-turn: strip thought content from history — keep only final responses in prior assistant turns.

## Sampling defaults

`temperature=1.0`, `top_p=0.95`, `top_k=64`.

## Multimodal prompting

- Place image/audio content BEFORE the text in the prompt.
- Variable image resolution via visual token budget: 70 / 140 / 280 / 560 / 1120 tokens. Low budget for captioning/classification speed; high budget for OCR / small-text reading.

## Benchmarks of note (instruction-tuned)

12B-class sits far above Gemma 3 27B on coding/reasoning (LiveCodeBench v6 ~52–80% across sizes vs 29.1%); 31B: MMLU Pro 85.2%, GPQA Diamond 84.3%. Vision strong across the line (MMMU Pro 44–77%).
