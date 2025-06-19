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

if files < 400: 
    key = "WARNING: Low Data Space"
    emoji = "warning"
    colour = "#9b111e"
else:
    key = "System OK"
    emoji = "ok"
    colour = "#228b22"

if in_archive > 0:
    key = "Files Remain - Check Transfers?"
    emoji = "face_with_monocle"
    colour = "#eed202"

#message = f"{key} Data space remaining for {device_name} is {space:n}% = {free:.2f}GB, space for approximately {files:.0f} images.\
#    There are {in_archive:n} {suffix} files on the device."

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
							"text": f" Data space check from {device_name}"
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
                "title": "Files on Device",
                "value": f"{in_archive:n}",
                "short": True
            },
            {
                "title": "File Space",
                "value": f"{files:.0f}",
                "short": True
            }
        ],
        "text": key
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
