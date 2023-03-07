# Discord Monitor Docker
This is a simple discord bot to monitor the status of docker containers

## Installation

```
sudo cp discord-docker-monitor.py /usr/local/bin
sudo cp discord-docker-monitor.service /lib/systemd/system/
```

## Configuration

Create a yaml file at `/etc/discord-docker-monitor/config.yaml` with the following:

```
channelid: <channelid>
discord_token: <token>
containers:
- list
- of
- containers
```

Replace the list of containers with the containers you would like to monitor.
