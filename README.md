# backup_postgres
Scripts that back up the PostgreSQL database in the exact period.

# pg_backup.service unit in the /etc/systemd/system/ 
```bash
[Unit]
Description=Run Python Script Every Month

[Service]
Type=oneshot
User=root
ExecStart=/usr/bin/python3 /home/pahtto/backup_postgres/main.py
```
# and in the same directory, the timer for this service
```bash
[Unit]
Description=Run Python Script Every Month
Wants=pg_backup.service

[Timer]
OnCalendar=monthly
Persistent=true

[Install]
WantedBy=timers.target
```
# Then run the next commands:
```bash
sudo systemctl enable pg_backup.timer
sudo systemctl start pg_backup.timer
sudo systemctl status pg_backup.timer
systemctl list-timers --all # to check if the timer runs

sudo systemctl daemon-reload
```

