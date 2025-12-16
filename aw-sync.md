     Plan: Create systemd user timer for aw-sync

     Overview

     Create a systemd user service and timer to automatically run the aw-sync command every 5 minutes.

     Context

     - Binary location: /home/alx/code/aw-server-rust/target/release/aw-sync
     - Command to run: aw-sync --port 5600 sync-advanced --mode push
     - Similar existing service: ~/.config/systemd/user/aw-bookmark.service
     - User systemd directory exists: ~/.config/systemd/user/

     Implementation Steps

     1. Create systemd service file

     File: ~/.config/systemd/user/aw-sync-push.service

     Service unit that executes the aw-sync command. Key properties:
     - Type=oneshot - suitable for one-time execution tasks
     - No Restart directive needed (timer handles re-execution)
     - Absolute path to binary
     - Proper working directory set to aw-sync project root

     2. Create systemd timer file

     File: ~/.config/systemd/user/aw-sync-push.timer

     Timer unit that triggers the service every 5 minutes. Key properties:
     - OnBootSec=2min - first run 2 minutes after boot
     - OnUnitActiveSec=5min - run every 5 minutes after service completes
     - Persistent=true - catch up on missed runs if system was off

     3. Enable and start the timer

     Commands to execute:
     systemctl --user daemon-reload
     systemctl --user enable aw-sync-push.timer
     systemctl --user start aw-sync-push.timer

     4. Verification commands

     Provide commands to verify the timer is working:
     systemctl --user status aw-sync-push.timer
     systemctl --user list-timers
     journalctl --user -u aw-sync-push.service -f

     Files to Create

     1. ~/.config/systemd/user/aw-sync-push.service
     2. ~/.config/systemd/user/aw-sync-push.timer

     Notes

     - Using Type=oneshot for service since this is a task that runs and completes
     - Timer uses OnUnitActiveSec to ensure 5 minutes between completions (not starts)
     - User systemd services run when user is logged in
     - No manual systemctl --user commands will be executed; instructions will be provided to the user

● Write(/home/alx/.config/systemd/user/aw-sync-push.service)
  ⎿  Wrote 13 lines to /home/alx/.config/systemd/user/aw-sync-push.service
     [Unit]
     Description=ActivityWatch Sync Push
     Documentation=https://github.com/ActivityWatch/aw-server-rust
     After=network.target

     [Service]
     Type=oneshot
     WorkingDirectory=/home/alx/code/aw-server-rust/aw-sync
     ExecStart=/home/alx/code/aw-server-rust/target/release/aw-sync --port 5600 sync-advanced --mode push

     [Install]
     WantedBy=default.target


● Write(/home/alx/.config/systemd/user/aw-sync-push.timer)
  ⎿  Wrote 12 lines to /home/alx/.config/systemd/user/aw-sync-push.timer
     [Unit]
     Description=Run ActivityWatch Sync Push every 5 minutes
     Documentation=https://github.com/ActivityWatch/aw-server-rust

     [Timer]
     OnBootSec=2min
     OnUnitActiveSec=5min
     Persistent=true

     [Install]
     WantedBy=timers.target


● Done! I've created the systemd user service and timer files. Here's what was created:

  Files Created

  1. ~/.config/systemd/user/aw-sync-push.service - The service that runs the sync command
  2. ~/.config/systemd/user/aw-sync-push.timer - The timer that triggers the service every 5 minutes

  Next Steps

  To enable and start the timer, run these commands:

  # Reload systemd to recognize the new files
  systemctl --user daemon-reload

  # Enable the timer to start automatically on boot
  systemctl --user enable aw-sync-push.timer

  # Start the timer now
  systemctl --user start aw-sync-push.timer

  Verification

  To verify the timer is working:

  # Check timer status
  systemctl --user status aw-sync-push.timer

  # List all timers to see when next run is scheduled
  systemctl --user list-timers

  # Follow the service logs in real-time
  journalctl --user -u aw-sync-push.service -f

  The timer will:
  - Run first time 2 minutes after boot
  - Then run every 5 minutes after each sync completes
  - Catch up on missed runs if the system was off (persistent mode)

