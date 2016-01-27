from flask import Flask, make_response, Response, request
from flask.ext.cors import CORS
import grequests
from PIL import Image
import random
import StringIO as StringIO
from werkzeug.routing import BaseConverter
import time



app = Flask(__name__)
app.debug = True
CORS(app)


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

app.url_map.converters['regex'] = RegexConverter



def make_pano_image(pano, tile_size=512, x_range=16,
        y_range=8, trim_black_background=True, max_parallel_requests=40):
    temporary = Image.new('RGB', (tile_size * x_range, tile_size * y_range))

    urls = list()
    tile_indices = list()

    for x in xrange(x_range):
        for y in xrange(y_range):
            url = "https://cbks%i.googleapis.com/cbk?output=tile&cb_client=apiv3&v=4&gl=US&zoom=4&x=%s&y=%s&panoid=%s&fover=2&onerr=3" % (
                random.randint(0, 3), x, y, pano)
            urls.append(url)
            tile_indices.append((x, y))

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'
    }

    reqs = (grequests.get(u, headers=headers) for u in urls)
    responses = grequests.map(reqs, stream=True, size=max_parallel_requests)

    for ((x, y), r) in zip(tile_indices, responses):
        io = StringIO.StringIO(r.raw.read())
        tile = Image.open(io)
        temporary.paste(tile, (x * tile_size, y * tile_size))
        io.close()

    if trim_black_background:
        output = temporary.crop(temporary.getbbox())
    else:
        output = temporary

    return output


@app.route('/<regex("[a-zA-Z0-9-_]{22}"):pano>')
def get_pano(pano):
    started_at = time.time()
    image = make_pano_image(pano)
    f = StringIO.StringIO()
    image.save(f, "JPEG")
    data = f.getvalue()
    f.close()
    ended_at = time.time()
    print "Stitched pano %s, size = %s, bytes = %s, time taken = %.2fs" % (
        pano, image.size, len(data), ended_at - started_at)
    response = make_response(data)
    response.headers['Content-Type'] = 'image/jpeg'
    return response


HELP = """
This API retrieves tiles of a Google StreetView Panorama and stitches them together.
The result is a JPEG in equirectangular projection.

Example: 
  {prefix}dGpXpL7DzCoIro-3w0yGeA

- Changping Chen
"""

@app.route('/')
def hello():
    return Response(HELP.strip().format(prefix=request.url_root), mimetype="text/plain", status=200)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
