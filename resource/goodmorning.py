import os
from slack_sdk import WebClient
from configparser import ConfigParser
import json

config = ConfigParser()
config.read('allsky.ini')
device_name = config["Paths"]["Camera_ID"]
suffix = config["Camera"]["Suffix"]

used = float(os.popen("df /home/Archive/ | awk '{ print $5 }' | tail -n 1| cut -d'%' -f1").read().strip('\n'))
free = float(os.popen("df /home/Archive/ | awk '{ print $4 }' | tail -n 1| cut -d'%' -f1").read().strip('\n'))/1024/1024
space = 100 - used
files = free / (30000/1024/1024)

in_archive=float(os.popen(f"ls /home/Archive/*/*/*.{suffix} | wc -l").read().strip('\n'))

if files < 300: 
    key = " We need to make sure this transfers today!"
    emoji = "firecracker"
else:
    key = ""
    emoji = "sunny"

message = f"Good Morning! {device_name} has {space:n}% = {free:.2f}GB before file transfer starts. There are {in_archive:n} {suffix} files on the device.{key}"

#blocks_json = '[{"type": "divider"},{"type": "rich_text","elements": \
#    [{"type": "rich_text_section","elements": [{"type": "emoji","name": "' + emoji + '"},{"type": "text","text": "' + message + '"]}]}]}]'

blocks_json = [
		{
			"type": "divider"
		},
		{
			"type": "rich_text",
			"elements": [
				{
					"type": "rich_text_section",
					"elements": [
						{
							"type": "emoji",
							"name": f"{emoji}"
						},
						{
							"type": "text",
							"text": f" {message}"
						}
					]
				}
			]
		}
	]


client = WebClient(token="xoxb-4291898519700-6373490897475-ee2U75HCGbJnylcb6zGXOLpy")
channel_id = "C06729CNQKC" #system-monitor
#channel_id = "C06AK1ZFKBR" #bottest
result = client.chat_postMessage(
    channel=channel_id,
    blocks=json.dumps(blocks_json)
    )
