import os
from slack_sdk import WebClient
from configparser import ConfigParser
import json

config = ConfigParser()
config.read('allsky.ini')
device_name = config["Paths"]["Camera_ID"]
suffix = config["Camera"]["Suffix"]
token = config["Slack"]["Key"]

used = float(os.popen("df /home/Archive/ | awk '{ print $5 }' | tail -n 1| cut -d'%' -f1").read().strip('\n'))
free = float(os.popen("df /home/Archive/ | awk '{ print $4 }' | tail -n 1| cut -d'%' -f1").read().strip('\n'))/1024/1024
space = 100 - used
files = free / (30000/1024/1024)

in_archive=float(os.popen(f"ls /home/Archive/*/*/*.{suffix} | wc -l").read().strip('\n'))

if files < 300: 
    key = "We need to make sure this transfers today!"
    emoji = "firecracker"
    colour = "#9b111e"
else:
    key = ""
    emoji = "sunny"
    colour = "#228b22"
    
if in_archive < 20:
    key = "Too few files saved last night!"
    emoji = "face_with_monocle"
    colour = "EED202"

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
							"text": f" Good Morning from {device_name}"
						}
					]
				}
			]
		}
	]

attachments_json = [
    {
        "mrkdwn_in": ["text"],
        "color": colour,
        "title": f" Current Data Health",
        "fields":
        [
            {
                "title": "Space Available",
                "value": f"{space:n}%",
                "short": True
            },
            {
                "title": "Archive Capacity",
                "value": f"{free:.2f}GB",
                "short": True
            },
            {
                "title": "Device Archive Content",
                "value": f"{in_archive:n} {suffix} files",
                "short": False
            },
            {
                "title": "Additional Messages:",
                "value": f"{key}",
                "short": False
            }
        ]
    }
]


client = WebClient(token=token)
channel_id = "C06729CNQKC" #system-monitor
#channel_id = "C06AK1ZFKBR" #bottest
result = client.chat_postMessage(
    channel=channel_id,
    blocks=json.dumps(blocks_json),
    attachments=json.dumps(attachments_json)
    )
