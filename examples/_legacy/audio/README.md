# Audio Examples

Text-to-Speech examples with smart routing and multiple backends.

## Examples

| File | Description |
|------|-------------|
| `01_basic_usage.py` | Basic TTS, backends, voice options, save to file |
| `02_smart_routing.py` | Auto local/relay routing, environment config |

## Quick Start

```bash
# Run all examples
python examples/audio/01_basic_usage.py
python examples/audio/02_smart_routing.py

# Or via CLI
scitex audio speak "Hello world"
scitex audio speak "Bonjour" --backend gtts --voice fr
```

## Prerequisites

```bash
# Install audio dependencies
pip install scitex[audio]

# For pyttsx3 (offline TTS)
sudo apt install espeak-ng
```

## Smart Routing

The `speak()` function automatically routes audio:

| Local Sink | Relay Available | Result |
|------------|-----------------|--------|
| SUSPENDED | Yes | Uses relay |
| SUSPENDED | No | Returns error |
| RUNNING | Yes | Prefers relay |
| RUNNING | No | Uses local |

## Environment Variables

```bash
# Mode selection
export SCITEX_AUDIO_MODE=auto  # auto, local, remote

# Relay configuration (for remote audio)
export SCITEX_AUDIO_RELAY_URL=http://localhost:31293
```

## Remote Audio Setup

To play audio on your local machine from a remote server:

```bash
# 1. Local machine - start relay
scitex audio relay --port 31293

# 2. SSH with reverse tunnel
ssh -R 31293:localhost:31293 remote-server

# 3. Remote server - audio routes through tunnel
python -c "import scitex.audio; scitex.audio.speak('Hello from remote!')"
```
