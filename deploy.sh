
# Setup steps to be done manually:
# - sudo apt-get install libxml2-dev libxslt-dev
# - sudo pip install requests lxml pandas fuzzywuzzy

ssh ubuntu@colourfulpast.org /bin/bash -e <<REMOTE_COMMANDS
    cd /home/ubuntu
    sudo rm -rf information-acquisition

    git clone git@github.com:colourful-past/information-acquisition.git
    # cd information-acquisition

REMOTE_COMMANDS
