
# setup tweepy 4.0.0
git clone https://github.com/tweepy/tweepy.git
cd tweepy
pip install .

pip install -r requirements.txt

# install Datadog
DD_AGENT_MAJOR_VERSION=7 DD_API_KEY=b0ae5318efafd03311ce8b5c13918431 DD_SITE="datadoghq.com" bash -c "$(curl -L https://s3.amazonaws.com/dd-agent/scripts/install_script.sh)"
