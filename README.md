## Telegram bot to choose a "winner of a day"

### Build
- Clone repo
- Put your telegram bot token inside `token.txt` and place it in repo root
- `docker build -t bot .`

### Run
`docker run  -d  -e  MEMORY_DIR=/data  -v /home/docker/mount/system/pidorbot_data:/data —restart=always —name bot_1 bot`
