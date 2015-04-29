import os
import urllib
import cgi
import StringIO
import re
import webapp2
from parse_vcd import *
from django.utils import simplejson as json

from google.appengine.ext import blobstore
from google.appengine.ext.blobstore import BlobInfo
from google.appengine.api import files
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template


class MainPage(webapp2.RequestHandler):
    def get(self):
        upload_url = blobstore.create_upload_url('/upload')
        # The method must be "POST" and enctype must be set to "multipart/form-data".
        self.response.out.write('<html><body>')
        self.response.out.write('<form action="%s" method="POST" enctype="multipart/form-data">' % upload_url)
        self.response.out.write('''Upload File: <input type="file" name="file"><br> <input type="submit"
            name="submit" value="Submit"> </form></body></html>''')

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        upload_files = self.get_uploads('file')
        blob_info = upload_files[0]        
        self.redirect('/serve/%s' % blob_info.key())
       
class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, blob_key):
        blob_key=str(urllib.unquote(blob_key)) #extracting the blob_key from blob info
        blob_reader = blobstore.BlobReader(blob_key) #blob_reader is similar to the file pointer
        value = blob_reader.read() #The complete file is read in a string
        valuelines = value.splitlines() #It is obtained as a list of lines
        if not blobstore.get(blob_key):
            self.error(404)
        else:
            vcdread = vcd_reader(valuelines) #The file is parsed
            signal_dict = vcdread.signal_symbol_dict
            transaction_dict = vcdread.transitions_dict
            signals = signal_dict.keys() #The value of all the signals
            trans_details=vcdread.create_json_to_display_waveforms(signals,signal_dict,transaction_dict)
            template_values = {
            'signals':signals,
            'trans_details':trans_details,
            }
            path = os.path.join(os.path.dirname(__file__),'index.htm')
            self.response.out.write(template.render(path, template_values))
    
application = webapp.WSGIApplication([('/', MainPage),('/upload', UploadHandler),
           ('/serve/([^/]+)?', ServeHandler)], debug=True)


def main():
    run_wsgi_app(application)
