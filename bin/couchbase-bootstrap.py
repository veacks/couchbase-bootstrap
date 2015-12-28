import json
import httplib2
from urllib import urlencode
import time
import subprocess
import os
import netifaces as ni
import traceback

def get_ip_address(ifname):
  ni.ifaddresses(ifname)
  return ni.ifaddresses(ifname)[2][0]['addr']

os.environ["PRIVATE_IP"] = get_ip_address('lo0')
os.environ["PUBLIC_IP"] = get_ip_address('lo0')

PRIVATE_IP = None
PUBLIC_IP = None

PRIVATE_IP = os.environ.get("PRIVATE_IP")
PUBLIC_IP = os.environ.get("PUBLIC_IP")

CB_USERNAME = "Administrator"
CB_PASSWORD = "password"

if os.environ.get("CB_USERNAME") != None:
  CB_USERNAME = os.environ.get("CB_USERNAME")

if os.environ.get("CB_PASSWORD") != None:
  CB_PASSWORD = os.environ.get("CB_PASSWORD")

CB_JSON_CONFIG = os.environ.get("CB_JSON_CONFIG")
CB_JSON_FILE_CONFIG = os.environ.get("CB_JSON_FILE_CONFIG")
print os.environ.get("CB_JSON_HTTP_CONFIG")
CB_JSON_HTTP_CONFIG = os.environ.get("CB_JSON_HTTP_CONFIG")

if PUBLIC_IP == None:
  PUBLIC_IP = PRIVATE_IP
  os.environ["PUBLIC_IP"] = PRIVATE_IP

def no_config_required():
  print ''
  print '#'
  print '# Couchbase is installed without any configuration'
  print '#'
  print "# Dashboard: http://"+PUBLIC_IP+":8091"
  print "# Internal IP: "+PRIVATE_IP
  print "# username="+CB_USERNAME
  print "# password="+CB_PASSWORD
  print '#'
  raise SystemExit

def installed():
  print ''
  print '#'
  print '# Couchbase is installed and configured'
  print '#'
  print "# Dashboard: http://"+PUBLIC_IP+":8091"
  print "# Internal IP: "+PRIVATE_IP
  print "# username="+CB_USERNAME
  print "# password="+CB_PASSWORD
  print '#'
  raise SystemExit

def test_if_couchbase_is_running():
  print ''

# Define JSON config object
if CB_JSON_CONFIG:
  try:
    print ''
    print '#'
    print '# Try to load json from CB_JSON_CONFIG'
    print '#'
    CONFIG = json.loads(CB_JSON_CONFIG)
  except Exception, err:
    traceback.print_exc()
    no_config_required()

elif CB_JSON_FILE_CONFIG:
  try:
    print ''
    print '#'
    print '# Try to load json from local file at CB_JSON_FILE_CONFIG absolute path'
    with open(CB_JSON_FILE_CONFIG) as config_file:
      CONFIG = json.loads(config_file)
  except Exception, err:
    traceback.print_exc()
    no_config_required()

elif CB_JSON_HTTP_CONFIG:
    print ''
    print '# Try to load json from url at CB_JSON_HTTP_CONFIG'
    h = httplib2.Http(".cache")
    resp, content = h.request(CB_JSON_HTTP_CONFIG, "GET")
    if resp.status == 200:
      try:
        CONFIG = json.loads(content)
      except Exception, err:
        traceback.print_exc()
        no_config_required()
    else:
      print '# configuration address not found'

else:
  no_config_required()

print ''
print '#'
print '# Testing to see if Couchbase is running yet'
print '#'

COUCHBASERESPONSIVE = 0
while COUCHBASERESPONSIVE != 1:
  print '.'
  return_code = subprocess.call("couchbase-cli server-info -c 127.0.0.1:8091 -u access -p password", shell=True)
  
  if return_code == 0:
    COUCHBASERESPONSIVE = 1

  return_code = subprocess.call("couchbase-cli server-info -c 127.0.0.1:8091 -u {0} -p {1}".format(CB_USERNAME, CB_PASSWORD), shell=True)
  
  if return_code == 0:
    COUCHBASERESPONSIVE = 1
  else:
    time.sleep(5)

time.sleep(1)

# it's responsive, is it already configured?
return_code = subprocess.call("couchbase-cli server-list -c 127.0.0.1:8091 -u {0} -p {1}".format(CB_USERNAME, CB_PASSWORD), shell=True)

if return_code == 0:
  print ''
  print '#'
  print '# Already joined to cluster...'
  print '#'
  installed()

COUCHBASERESPONSIVE = 0
while COUCHBASERESPONSIVE != 1:
  print '.'
  return_code = subprocess.call("couchbase-cli server-info -c 127.0.0.1:8091 -u access -p password", shell=True)
  
  if return_code == 0:
    COUCHBASERESPONSIVE = 1

  return_code = subprocess.call("couchbase-cli server-info -c 127.0.0.1:8091 -u {0} -p {1}".format(CB_USERNAME, CB_PASSWORD), shell=True)
  
  if return_code == 0:
    COUCHBASERESPONSIVE = 1
  else:
    time.sleep(5)

time.sleep(10)

print ''
print '#'
print '# Initializing node'
print '#'

COUCHBASERESPONSIVE = 0
while COUCHBASERESPONSIVE != 1:
  print '.'

  h = httplib2.Http(".cache")
  h.add_credentials(CB_USERNAME, CB_PASSWORD)
  resp, content = h.request("http://127.0.0.1:8091/nodes/self/controller/settings", "POST", urlencode({ 'path': '/opt/couchbase/var/lib/couchbase/data', 'index_path': '/opt/couchbase/var/lib/couchbase/data' }))
  resp, content = h.request("http://127.0.0.1:8091/node/controller/rename", "POST", urlencode({ 'hostname': PRIVATE_IP }))

  if resp.status == 200:
    COUCHBASERESPONSIVE = 1
  else:
    time.sleep(7)


os.environ["CB_SERVICES"] = ""

if os.environ["COUCHBASE_SERVICE_INDEX"] == "True":
  os.environ["CB_SERVICES"] += ",index"

if os.environ["COUCHBASE_SERVICE_QUERY"] == "True":
  os.environ["CB_SERVICES"] += ",n1ql"

if os.environ["COUCHBASE_SERVICE_DATA"] == "True":
  os.environ["CB_SERVICES"] += ",kv"

if bootstrap:
  print ''
  print '#'
  print '# Bootstrapping cluster'
  print '#'

  COUCHBASERESPONSIVE = 0
  while COUCHBASERESPONSIVE != 1:
    print '.'

    h = httplib2.Http(".cache")
    h.add_credentials(CB_USERNAME, CB_PASSWORD)
    status_list = []

    resp, content = h.request("http://127.0.0.1:8091/pools/default", "POST", urlencode({ 'memoryQuota': CONFIG.amountMemory }))
    status_list.append(resp.status)

    resp, content = h.request("http://127.0.0.1:8091/pools/default", "POST", urlencode({ 'indexMemoryQuota': CONFIG.indexMemory }))
    status_list.append(resp.status)

    resp, content = h.request("http://127.0.0.1:8091/settings/indexes", "POST", urlencode({ 'indexerThreads': CONFIG.indexerThreads }))
    status_list.append(resp.status)

    resp, content = h.request("http://127.0.0.1:8091/node/controller/setupServices", "POST", urlencode({ 'services': os.environ["CB_SERVICES"] }))
    status_list.append(resp.status)

    resp, content = h.request("http://127.0.0.1:8091/settings/web", "GET", urlencode({ 'password': CB_PASSWORD, 'username': CB_USERNAME, 'port': 8091 }))
    status_list.append(resp.status)

    succeed = True
    for status in status_list:
      if status != 200:
        succeed = False

    if succeed:
      COUCHBASERESPONSIVE=1
    else:
      time.sleep(7)

  print ''
  print '#'
  print '# Creating Buckets'
  print '#'

  # Creating buckets
  COUCHBASERESPONSIVE = 0
  while COUCHBASERESPONSIVE != 1:
    print '.'

    h = httplib2.Http(".cache")
    h.add_credentials(CB_USERNAME, CB_PASSWORD)
    status_list = []

    for bucket in CONFIG.buckets:
      resp, content = h.request("http://127.0.0.1:8091/pools/default/buckets", "POST", urlencode(bucket))
      status_list.append(resp.status)

    succeed = True
    for status in status_list:
      if status != 200:
        succeed = False

    if succeed:
      COUCHBASERESPONSIVE=1
    else:
      time.sleep(7)

  print ''
  print '#'
  print '# Creating XDCR connections'
  print '#'

  # Creating buckets
  COUCHBASERESPONSIVE = 0
  while COUCHBASERESPONSIVE != 1:
    print '.'

    h = httplib2.Http(".cache")
    h.add_credentials(CB_USERNAME, CB_PASSWORD)

    for xdcr in CONFIG.XDCR:
      resp, content = h.request("http://127.0.0.1:8091/pools/default/remoteClusters", "POST", urlencode(xdcr))

      if resp.status == 200:
        COUCHBASERESPONSIVE=1
      else:
        time.sleep(7)

else:
  print ''
  print '#'
  print '# Joining cluster...'
  print '#'

  COUCHBASERESPONSIVE=0
  while COUCHBASERESPONSIVE != 1:
    print '.'

    return_code = subprocess.call("couchbase-cli server-add -c {0}:8091 \
       --server-add={1}:8091 \
       --server-add-username={2} \
       --server-add-password={3} \
       --services={4} \
       -u {2} -p {3}".format(CONFIG.clusterId, PRIVATE_IP, CB_USERNAME, CB_PASSWORD, os.environ["CB_SERVICES"]), shell=True)

    if return_code == 0:
      COUCHBASERESPONSIVE=1
    else:
      time.sleep(7)

  print ''
  print '#'
  print '# Rebalancing cluster'
  print '#'

  # doing this in a loop in case multiple containers are started at once
  # it seems the rebalance command cannot be called while a rebalance is in progress
  COUCHBASERESPONSIVE=0
  while COUCHBASERESPONSIVE != 1:
    print '.'

    return_code = subprocess.call("couchbase-cli rebalance -c 127.0.0.1:8091 -u {0} -p {1}".format(CB_USERNAME, CB_PASSWORD), shell=True)
    if return_code == 0:
      COUCHBASERESPONSIVE=1
    else:
      time.sleep(7)

print ''
print '#'
print '# Confirming cluster health...'
print '#'

COUCHBASERESPONSIVE=0
while COUCHBASERESPONSIVE != 1:
  print '.'

  return_code = subprocess.call("couchbase-cli server-list -c 127.0.0.1:8091 -u {0} -p {1}".format(CB_USERNAME, CB_PASSWORD), shell=True)
  if return_code == 0:
    COUCHBASERESPONSIVE=1
  else:
    time.sleep(7)

  # if this never exits, then it will never register as a healthy node in the cluster
  # watch the logs for that...

installed()