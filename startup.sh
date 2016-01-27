apt-get update
apt-get install -y python-pip python-dev

pip install -U flask flask-cors grequests gunicorn

cd /tmp
git clone git@github.com:ccp0101/streetview-pano.git

cd streetview-pano
NUM_WORKERS=$(curl http://metadata/computeMetadata/v1/instance/attributes/num-workers -H "Metadata-Flavor: Google")

re='^[0-9]+$'
if ! [[ $NUM_WORKERS =~ $re ]] ; then
   echo "error: Metadata num-workers is not an integer."
   NUM_WORKERS=4
fi

gunicorn app:app --workers $NUM_WORKERS --bind 0.0.0.0:80
