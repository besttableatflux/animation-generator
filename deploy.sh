
# Setup steps to be done manually:
# - sudo apt-get install libxml2-dev libxslt-dev
# - sudo pip install requests lxml pandas fuzzywuzzy

SERVERS=( 52.42.187.96 52.41.100.249 )

for SERVER in "${SERVERS[@]}"
do
    echo "----------------------------------------"
    echo "Deploying to $SERVER"
    echo "----------------------------------------"

    ssh ubuntu@$SERVER /bin/bash -e <<REMOTE_COMMANDS
      cd /home/ubuntu
      sudo rm -rf information-acquisition

      git clone git@github.com:colourful-past/information-acquisition.git
      # cd information-acquisition

REMOTE_COMMANDS
