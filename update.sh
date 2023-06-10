 #!/bin/bash

# Aggiorna codice raspUI dopo aver fatto push dal pc

sudo -s
cd /home/pi/Project_PLCS_raspUI
git pull https://github.com/simone-torino/Project_PLCS_raspUI master
sudo systemctl restart flask
echo "Code updated and ready to be tested!"