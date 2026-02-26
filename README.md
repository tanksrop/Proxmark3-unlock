# Proxmark3-unlock
## **Warning:** This project is AI slop and a **proof-of-concept (POC)**.  
**This enture project has been initially written with extremely heavy use of LLMs and this is currently AI slop (even this README was 😅)**  
  
I plan to completely refactor the codebase to clean it all up, add more features such as reading data from cards, password auth on card? , settings (yaml??) and also possibily add some method of pam auth???  
  
To add to the disclaimers, theres the obvious risks from running anything that bypasses authentication

## Why??  
This was just a random idea of how to actually make use of the proxmark3 easy that i currently only use once or twice a year, maybe this will become a nice little project, maybe it'll stay ai slop that i probably (definitely) shouldn't be running on my computer, who knows :P

## Overview
This setup allows you to **unlock your Linux session using a PM3 RFID device**.  

- The **PM3 client runs inside a Distrobox container**, while the watcher script runs in the host user session.
- Currently only tested on an **XSIID card**, but theoretically should work with **any ISO 14443-A (14a) card**.  
- Detects **screen lock/unlock** via DBus  
- Starts **PM3 reader** when the screen is locked  
- Unlocks session automatically if an **authorized UID** is presented  
- Stops scanning when the session is unlocked  
- Can handle **PM3 unplug/replug** via systemd + udev

## File Structure
```
~/rfid/
├── rfid-unlock.py        # Main Python watcher
├── uid-list.txt          # Authorized UIDs (one per line)
~/.config/systemd/user/
├── rfid-unlock.service   # Systemd user service for auto-restart
/etc/udev/rules.d/
├── 99-proxmark3.rules    # Optional udev rule for hotplug restart
```
