apt-get update
apt-get install -y git python-pip python-dev python-gevent python-gunicorn python-pil libevent-dev

pip install flask flask-cors grequests markupsafe pillow

cd /tmp
git clone https://github.com/ccp0101/streetview-pano.git

cd streetview-pano
NUM_WORKERS=$(curl http://metadata/computeMetadata/v1/instance/attributes/num-workers -H "Metadata-Flavor: Google")

re='^[0-9]+$'
if ! [[ $NUM_WORKERS =~ $re ]] ; then
   echo "error: Metadata num-workers is not an integer."
   NUM_WORKERS=4
fi

gunicorn app:app --workers $NUM_WORKERS --bind 0.0.0.0:80 --access-logfile /tmp/access.log 2>&1 1>/tmp/gunicorn.log
