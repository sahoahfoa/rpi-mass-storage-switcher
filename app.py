import os
import time
import glob
import pathlib
import subprocess
from flask import Flask, request, render_template

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
mass_storage_path = r'/media/mass_storage/'

@app.before_first_request
def init_mass_storage():
    remove_usb_gadget()
    init_usb_gadget()
    
def remove_usb_gadget():
    subprocess.Popen('/opt/mass-storage-switcher/remove-usb-gadget', shell=True).wait()

def init_usb_gadget():
    subprocess.Popen('/opt/mass-storage-switcher/init-usb-gadget', shell=True).wait()

def get_backing_files():
    images = {}
    cdroms = {}
    
    for full_path in glob.glob(mass_storage_path + '*.img'):
        images[os.path.basename(full_path)] = full_path
    for full_path in glob.glob(mass_storage_path + '*.iso'):
        cdroms[os.path.basename(full_path)] = full_path
    return images, cdroms

@app.route('/', methods = ['GET'])
def index():
    images, cdroms = get_backing_files()
    return render_template('index.html', images=list(images.keys()), cdroms=list(cdroms.keys()))

@app.route('/', methods = ['POST'])
def switch():
  backing_type = request.args.get('type')
  backing_name = request.args.get('filename')
  
  if backing_type == "clear":
      subprocess.Popen('/opt/mass-storage-switcher/clearmount', shell=True)
      return f'Unmounted', 200
  
  images, cdroms = get_backing_files()
  backing_files = {**images, **cdroms}
  
  if backing_name in backing_files:
      subprocess.Popen('/opt/mass-storage-switcher/clearmount', shell=True)
      time.sleep(3)
      subprocess.Popen(f'/opt/mass-storage-switcher/mountimage {backing_type} {backing_files[backing_name]}', shell=True)
      return f'{backing_name} mounted', 200
  
  return 'FAILED', 400



if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0')
