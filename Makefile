.PHONY: start stop logs install uninstall

# Start all services
start:
	@echo "🚀 Starting Kira..."
	@docker-compose up -d redis chromadb
	@sleep 2
	@cd agent && source .venv/bin/activate && uvicorn main:app --host 127.0.0.1 --port 8765 > /tmp/wa-agent.log 2>&1 &
	@cd baileys && node client.js > /tmp/wa-baileys.log 2>&1 &
	@echo "✅ All services started. Logs: /tmp/wa-agent.log and /tmp/wa-baileys.log"

# Stop all services
stop:
	@pkill -f "uvicorn main:app" || true
	@pkill -f "node client.js"   || true
	@docker-compose stop redis chromadb
	@echo "🛑 All services stopped."

# Tail logs from both services
logs:
	@tail -f /tmp/wa-agent.log /tmp/wa-baileys.log

# Install LaunchAgents so Kira starts automatically at login
install:
	@echo "📦 Installing LaunchAgents..."
	@cp launchagents/com.kira.wa-agent.plist   ~/Library/LaunchAgents/
	@cp launchagents/com.kira.wa-baileys.plist ~/Library/LaunchAgents/
	@launchctl load ~/Library/LaunchAgents/com.kira.wa-agent.plist
	@launchctl load ~/Library/LaunchAgents/com.kira.wa-baileys.plist
	@echo "✅ Auto-start configured. Kira will start at login."

# Remove LaunchAgents
uninstall:
	@launchctl unload ~/Library/LaunchAgents/com.kira.wa-agent.plist   || true
	@launchctl unload ~/Library/LaunchAgents/com.kira.wa-baileys.plist || true
	@rm -f ~/Library/LaunchAgents/com.kira.wa-*.plist
	@echo "✅ Auto-start removed."
