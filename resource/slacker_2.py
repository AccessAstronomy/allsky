import os
from slack_sdk import WebClient
from configparser import ConfigParser
import json
import sys

lenarg = len(sys.argv)
slack = " ".join(sys.argv[1:lenarg-2])
emoji = sys.argv[lenarg-2]
colour = sys.argv[lenarg-1]

with open("/home/LDST_EOSRP/slackerlog.txt", "a") as f:
    f.write(f"Python: ({slack} {emoji} {colour})\n")

config = ConfigParser()
config.read('allsky.ini')
device_name = config["Paths"]["Camera_ID"]
suffix = config["Camera"]["Suffix"]
token = config["Slack"]["Key"]
used = float(os.popen("df /home/Archive/ | awk '{ print $5 }' | tail -n 1| cut -d'%' -f1").read().strip('\n'))
free = float(os.popen("df /home/Archive/ | awk '{ print $4 }' | tail -n 1| cut -d'%' -f1").read().strip('\n'))/1024/1024
space = 100 - used
in_archive=float(os.popen(f"ls /home/Archive/*/*/*.{suffix} | wc -l").read().strip('\n'))

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
							"text": f" {device_name} says:"
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
        "title": f"{slack}",
        "fields":
        [
            {
                "title": "Archive Space", 
                "value": f"{space:.0f}%",
                "short": True
            },
            {
                "title": "Current Storage",
                "value": f"{in_archive:n} {suffix} files",
                "short": True
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
