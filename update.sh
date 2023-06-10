 #!/bin/bash

# Aggiorna codice raspUI dopo aver fatto push dal pc

sudo -s
cd /home/pi/Project_PLCS_raspUI
git pull
sudo systemctl restart flask
echo "Code updated and ready to be tested!"