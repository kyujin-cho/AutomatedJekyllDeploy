import os
import requests
import CloudFlare

BLOG_DOMAIN=os.environ['BLOG_DOMAIN']
SERVER_ADDR=os.environ['BLOG_SERVER_ADDR']
FALLBACK_ADDR=os.environ['BLOG_FALLBACK_ADDR']
CF_API_KEY=os.environ['CF_API_KEY']
CF_API_EMAIL=os.environ['CF_API_EMAIL']
CF_ZONE_ID=os.environ['CF_ZONE_ID']
HEALTHCHECK_URL=os.environ['HEALTHCHECK_URL']

notify_telegram = False
if 'TG_API_KEY' in os.environ.keys() and 'TG_USERID' in os.environ.keys():
  notify_telegram = True
  TG_API_KEY = os.environ['TG_API_KEY']
  TG_USERID = os.environ['TG_USERID']

mode = 'default'

def health_check() -> bool:
  try:
    res = requests.get(HEALTHCHECK_URL)
    return True
  except Exception as e:
    print(e)
    return False

def get_record(cf: CloudFlare.CloudFlare) -> str:
  records = cf.zones.dns_records.get(CF_ZONE_ID, params={
    'name': BLOG_DOMAIN,
    'type': 'CNAME'
  })
  print(records[0])
  return records[0]['id'], records[0]['content']

def send_tg_message(mode: str):
  msg_type = '꺼졌' if mode == 'fallback' else '돌아왔'
  res = requests.post(f'https://api.telegram.org/bot{TG_API_KEY}/sendMessage', {
    'chat_id': TG_USERID,
    'text': f'{SERVER_ADDR} 서버가 {msg_type}어요.'
  })
  print(res)

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
      'content': FALLBACK_ADDR if mode == 'fallback' else SERVER_ADDR,
      'proxied': False
    })
    if notify_telegram:
      send_tg_message(mode)
    print(response)

def main():
  healthy = health_check()
  switch('default' if healthy else 'fallback')

if __name__ == '__main__':
    main()
