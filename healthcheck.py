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

def get_record_id(cf: CloudFlare.CloudFlare) -> str:
  records = cf.zones.dns_records.get(CF_ZONE_ID, params={
    'name': BLOG_DOMAIN,
    'type': 'CNAME'
  })
  return records.result[0].id

def switch(mode: str):  
  cf = CloudFlare.CloudFlare()
  response = cf.zones.dns_records.put(CF_ZONE_ID, get_record_id(cf), data={
    'type': 'CNAME', 
    'name': BLOG_DOMAIN,
    'content': SERVER_ADDR if mode == 'fallback' else FALLBACK_ADDR,
    'proxied': False
  })
  with open('health.status', 'w') as fw:
    fw.write(mode)
  return response

def main():
  healthy = health_check()
  if healthy and mode == 'fallback':
    switch('default')
  elif not healthy and mode == 'default':
    switch('fallback')