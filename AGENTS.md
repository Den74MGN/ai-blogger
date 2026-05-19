# OpenClaw Integration — ai-blogger project

## OpenClaw
- **CLI**: `openclaw` (v2026.5.7, npm global)
- **Gateway**: `ws://127.0.0.1:18789` (loopback only, auth=token)
- **Dashboard**: `http://127.0.0.1:18789/` (localhost only)
- **Config**: `C:\Users\denk0\.openclaw\openclaw.json`
- **Browser control**: `http://127.0.0.1:18791/` (localhost only)
- **Logs**: `C:\Users\denk0\AppData\Local\Temp\openclaw\openclaw-*.log`

## Management
```powershell
.\openclaw.ps1 start      # Start Ollama + Gateway
.\openclaw.ps1 stop       # Stop all
.\openclaw.ps1 restart    # Restart all
.\openclaw.ps1 status     # Show status + ports
.\openclaw.ps1 log        # Show last 30 log lines
```

## Local Models (Ollama)
Default: `qwen2.5-coder:7b` (4.7GB, 32k ctx, tool support)
Others: gemma4, qwen2.5-coder:14b, llama3.2, qwen3-coder:30b, deepseek-r1:8b

## Security
- All services bound to 127.0.0.1 only
- OLLAMA_HOST=127.0.0.1
- No cloud models configured
- No external channels (Telegram disabled)
- No Tailscale exposure
- Gateway auth = token (loopback only)

## Tools & Integrations
- **Web Search**: DuckDuckGo (free, no API key) — `openclaw infer web search --query "..."`  
- **Browser Control**: `http://127.0.0.1:18791/` (auth=token, localhost only)  
- **MCP Bridge**: OpenCode ↔ OpenClaw через `openclaw mcp serve` (настроен в opencode.json)  
- **Git**: Доступен через OpenCode (`gh`, `git`)

## Dev Workflow
1. Start: `.\openclaw.ps1 start`
2. OpenCode uses Ollama `llama3.2` for chat, OpenClaw for agent mode
3. OpenCode config at `C:\Users\denk0\.config\opencode\opencode.json`
4. Query OpenClaw: `openclaw infer model run --model ollama/qwen2.5-coder:7b --prompt "..." --local`
5. Web search: `openclaw infer web search --query "..."` (через DuckDuckGo)
6. Stop: `.\openclaw.ps1 stop`

## ai-blogger Project Commands
```powershell
# TTS генерация
python -c "import edge_tts, asyncio; asyncio.run(edge_tts.Communicate('Текст','ru-RU-SvetlanaNeural').save('out.mp3'))"

# Wav2Lip запуск
python D:\OpenCode\Wav2Lip\run_inference.py --checkpoint D:\OpenCode\Wav2Lip\checkpoints\wav2lip_gan.pth --face video.mp4 --audio audio.wav --outfile result.mp4

# FFmpeg обрезка
ffmpeg -i input.mp4 -t 5.5 -c copy output.mp4
```
