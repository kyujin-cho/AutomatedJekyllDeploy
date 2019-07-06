import os
import requests
import CloudFlare

BLOG_DOMAIN=os.environ['BLOG_DOMAIN']
SERVER_ADDR=os.environ['BLOG_SERVER_ADDR']
FALLBACK_ADDR=os.environ['BLOG_FALLBACK_ADDR']
CF_API_KEY=os.environ['CF_API_KEY']
CF_API_EMAIL=os.environ['CF_API_EMAIL']
CF_ZONE_ID=os.environ['CF_ZONE_ID']

mode = 'default'

def health_check() -> bool:
  try:
    requests.get(SERVER_ADDR)
    return True
  except:
    return False

def get_record(cf: CloudFlare.CloudFlare) -> str:
  records = cf.zones.dns_records.get(CF_ZONE_ID, params={
    'name': BLOG_DOMAIN,
    'type': 'CNAME'
  })
  return records.result[0].id, records.result[0].content

def switch(mode: str):  
  cf = CloudFlare.CloudFlare()
  record_id, current_domain = get_record(cf)
  current_mode = 'fallback' if current_domain == FALLBACK_ADDR else 'default'
  print('Current Mode:', current_mode)
  if current_mode != mode:
    print('Switching to', mode)
    response = cf.zones.dns_records.put(CF_ZONE_ID, record_id, data={
      'type': 'CNAME', 
      'name': BLOG_DOMAIN,
      'content': SERVER_ADDR if mode == 'fallback' else FALLBACK_ADDR,
      'proxied': False
    })
  return response

def main():
  healthy = health_check()
  switch('default' if healthy else 'fallback')