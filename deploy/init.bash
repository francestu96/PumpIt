curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install nodejs

mkdir /home/ubuntu/pump_it
chown ubuntu:ubuntu /home/ubuntu/pump_it

sudo echo "[Unit]
Description="PUMP IT!"

[Service]
ExecStart=/usr/bin/node pump_it.mjs
WorkingDirectory=/home/ubuntu/pump_it
Restart=always
RestartSec=10
StandardOutput=file:/var/log/pump_it.log
StandardError=file:/var/log/pump_it.log
SyslogIdentifier=PumpIt

[Install]
WantedBy=multi-user.target" >> /etc/systemd/system/pump_it.service

sudo systemctl enable pump_it