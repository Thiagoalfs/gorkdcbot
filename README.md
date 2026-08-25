# GorkBot

A feature-rich Discord bot built on python with `discord.py`, featuring music playback, moderation, fun games, and League of Legends utility commands.

Yes, its name comes from the AI agent.

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+** (or **Docker**)
- **FFmpeg**: Required for audio processing and downloads. Ensure it is added to your system's `PATH` (already included in the Docker image).
- **MySQL/MariaDB**: A database instance to store server settings and user profiles.

---

## ⚙️ Configuration

Create a `.env` file in the root directory to store your sensitive credentials:

```env
TOKEN=your_discord_bot_token_here

# Database Configuration
DB_HOST=your_database_host
DB_PORT=3306
DB_USER=your_database_user
DB_PASS=your_database_password
DB_NAME=your_database_name

# League of Legends Profile Configuration
RIOT_API_KEY=your_riot_api_key
```

### Database Setup
The bot uses an asynchronous MySQL pool (`aiomysql`). Upon startup, the bot will automatically execute the `create_tables()` method from `database.py` to initialize:
- `botsettings`: Stores per-guild prefixes.
- `leagueconfig`: Maps Discord IDs to Riot IDs.

---

## 🐳 Running with Docker / Docker Compose (Homelab)

1. Make sure your `.env` file is filled in the root directory.
2. Build and start the container in background:
   ```bash
   docker compose up -d --build
   ```
3. To view real-time logs:
   ```bash
   docker compose logs -f
   ```
4. To stop the bot:
   ```bash
   docker compose down
   ```

---

## 🛠️ Running Locally (without Docker)

1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the bot:
   ```bash
   python main.py
   ```
