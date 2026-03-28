---
description: GenAI unified LLM interface — factory function covering OpenAI, Anthropic, Google, Groq, DeepSeek, Perplexity, and Llama with cost tracking.
---

# GenAI

`stx.ai.GenAI` is a lazy-loaded factory function that returns a provider-specific client instance. All providers share the same call interface.

## GenAI (factory)

```python
def genai_factory(
    model="gpt-3.5-turbo",
    stream=False,
    api_key=None,
    seed=None,
    temperature=1.0,
    n_keep=1,
    chat_history=None,
    max_tokens=4096,
)
```

Accessed as `stx.ai.GenAI` (lazy import; heavy dependencies are only loaded on first access).

### Parameters
- `model` — Model name string (see table below). Default: `"gpt-3.5-turbo"`
- `stream` — Whether to stream responses. Default: `False`
- `api_key` — API key string or list of keys (one is chosen randomly from a list). If `None`, reads from environment variable
- `seed` — Integer seed for reproducible outputs. Default: `None`
- `temperature` — Sampling temperature (0.0–2.0). Default: `1.0`
- `n_keep` — Number of recent history messages to keep. Default: `1`
- `chat_history` — Pre-existing chat history list. Default: `None`
- `max_tokens` — Maximum output tokens. Default: `4096`

### Return value
Returns an instance of the appropriate provider class (`OpenAI`, `Anthropic`, `Google`, `Groq`, `DeepSeek`, `Perplexity`, or `Llama`).

## Calling the client

```python
def __call__(
    self,
    prompt=None,
    prompt_file=None,
    images=None,
    format_output=False,
    return_stream=False,
)
```

### Parameters
- `prompt` — Text prompt string
- `prompt_file` — Path to a text file whose contents are appended to `prompt`
- `images` — List of image file paths or base64-encoded strings
- `format_output` — Apply output formatting. Default: `False`
- `return_stream` — Return raw stream object instead of yielding. Default: `False`

### Return value
`str` (static mode) or generator yielding chunks (stream mode).

## Supported Providers and Models

### OpenAI (env: `OPENAI_API_KEY`)
| Model | Input $/1M | Output $/1M |
|---|---|---|
| `o3` | 10.00 | 40.00 |
| `o4-mini` | 1.10 | 4.40 |
| `gpt-4.1` | 2.00 | 8.00 |
| `gpt-4.1-mini` | 0.40 | 1.60 |
| `gpt-4.1-nano` | 0.10 | 0.40 |
| `gpt-4o` | 5.00 | 15.00 |
| `gpt-4o-mini` | 0.15 | 0.60 |
| `gpt-3.5-turbo` | 0.50 | 1.50 |

### Anthropic (env: `ANTHROPIC_API_KEY`)
| Model | Input $/1M | Output $/1M |
|---|---|---|
| `claude-opus-4-20250514` | 15.00 | 75.00 |
| `claude-sonnet-4-20250514` | 3.00 | 15.00 |
| `claude-3-7-sonnet-20250219` | 3.00 | 15.00 |
| `claude-3-5-sonnet-20241022` | 3.00 | 15.00 |
| `claude-3-5-haiku-20241022` | 0.80 | 4.00 |

### Google (env: `GOOGLE_API_KEY`)
| Model | Input $/1M | Output $/1M |
|---|---|---|
| `gemini-2.5-pro` | 2.50 | 10.00 |
| `gemini-2.5-flash` | 0.30 | 2.50 |
| `gemini-2.0-flash` | 0.10 | 0.40 |

### DeepSeek (env: `DEEPSEEK_API_KEY`)
| Model | Input $/1M | Output $/1M |
|---|---|---|
| `deepseek-reasoner` | 0.14 | 2.19 |
| `deepseek-chat` | 0.014 | 0.28 |

### Groq (env: `GROQ_API_KEY`)
| Model | Input $/1M | Output $/1M |
|---|---|---|
| `llama-3.3-70b-versatile` | 0.04 | 0.04 |
| `deepseek-r1-distill-llama-70b` | 0.01 | 0.01 |

## Cost Tracking

Every client instance tracks token usage and exposes a `.cost` property.

```python
gen = stx.ai.GenAI(model="gpt-4o")
response = gen("Hello world")
print(f"Cost so far: ${gen.cost:.6f}")
print(f"Input tokens: {gen.input_tokens}")
print(f"Output tokens: {gen.output_tokens}")
```

`cost` calls `calc_cost(model, input_tokens, output_tokens)` which uses the pricing table in `_PARAMS.py`. Cost is in USD.

## Chat History Management

```python
gen = stx.ai.GenAI(model="gpt-4o", n_keep=10)
gen("First message")
gen("Second message")  # History kept up to n_keep messages
gen.reset()            # Clear history
gen.history            # List of dicts: [{"role": ..., "content": ...}]
```

## Multi-key Round Robin

```python
# Randomly selects one key per instantiation
keys = ["sk-key1", "sk-key2", "sk-key3"]
gen = stx.ai.GenAI(model="gpt-4o", api_key=keys)
```

## Streaming

```python
gen = stx.ai.GenAI(model="gpt-4o", stream=True)
# Prints chunks as they arrive, returns full string
response = gen("Tell me about UMAP")

# Get raw stream object
stream_obj = gen("...", return_stream=True)
```

## Model Discovery

```python
# List all available models
stx.ai.GenAI.list_models()

# List by provider
stx.ai.GenAI.list_models(provider="Anthropic")
```

## Examples

### Basic usage

```python
import scitex as stx

gen = stx.ai.GenAI(model="gpt-4o-mini")
summary = gen("Summarize the key findings of this study in 3 bullet points.")
print(summary)
```

### With image input

```python
gen = stx.ai.GenAI(model="gpt-4o")
description = gen(
    "Describe what you see in this figure.",
    images=["./fig1.png"]
)
```

### From file prompt

```python
gen = stx.ai.GenAI(model="claude-3-5-sonnet-20241022")
response = gen(
    prompt="Review the following code:",
    prompt_file="./my_script.py"
)
```
