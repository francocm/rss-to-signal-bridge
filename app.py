import feedparser
import logging
import os
import requests
import sys
import time
from datetime import datetime
from time import mktime
from os.path import exists

SIGNAL_API_URL=os.getenv('SIGNAL_API_URL')
DESTINATIONS_RAW=os.getenv('SIGNAL_DESTINATIONS')
DESTINATIONS=[a.strip() for a in DESTINATIONS_RAW.split(',')]
SOURCE=os.getenv('SIGNAL_SENDER_NUMBER')
FAKE=os.getenv('SIGNAL_FAKE_SEND') is not None and os.getenv('SIGNAL_FAKE_SEND').lower() == "true"
RSS_FEED_URL=os.getenv('RSS_FEED_URL')
MESSAGE_TEMPLATE=os.getenv('MESSAGE_TEMPLATE')
POLL_INTERVAL=int(os.getenv('RSS_POLL_INTERVAL'))

STATE_FILEPATH="/data/state.dat"

def create_logger() :
    log = logging.getLogger('')
    log.setLevel(logging.INFO)
    format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(format)
    log.addHandler(ch)
    return log

log = create_logger()

def send_message(body):
    if FAKE:
        log.info("Sending message to: %s" % DESTINATIONS)
        log.info("Body:\n%s" % body)
    else:
        r = requests.post(SIGNAL_API_URL, headers={"Content-Type":"application/json"},
                json={"message": body, "text_mode": "styled", "recipients": DESTINATIONS, "number": SOURCE})
        log.info("Message sent to Signal with HTTP response code %s and content %s" % (r.status_code, r.content))

def format_message(template, title, link, publish_timestamp):
    result = template
    result = result.replace('\\n', '\n')
    result = result.replace('{title}', title)
    result = result.replace('{link}', link)
    result = result.replace('{publish_timestamp}', publish_timestamp)
    return result

def time_struct_to_epoch(time_struct):
    return int(datetime.fromtimestamp(mktime(time_struct)).timestamp())

def get_last_processed_entry():
    if not exists(STATE_FILEPATH):
        return 0
    with open(STATE_FILEPATH, "r") as state_file:
        return int(state_file.read())

def set_last_processed_entry(epoch_value):
    with open(STATE_FILEPATH, "w") as state_file:
        state_file.write(str(epoch_value))

def is_newer_than_saved_state(epoch_value):
    return get_last_processed_entry() < epoch_value

def sort_feed_entries_oldest_first(feed_entries):
    return sorted(feed_entries, key=lambda x: time_struct_to_epoch(x.published_parsed))

def process_feed_response(feed):
    sorted_entries = sort_feed_entries_oldest_first(feed.entries)
    last_processed_timestamp = get_last_processed_entry()
    new_messages_count = 0
    for entry in sorted_entries:
        epoch_publish_time = time_struct_to_epoch(entry.published_parsed)
        if epoch_publish_time <= last_processed_timestamp:
            continue
        last_processed_timestamp = epoch_publish_time
        message = format_message(MESSAGE_TEMPLATE, entry.title, entry.link, entry.published)
        send_message(message)
        new_messages_count = new_messages_count + 1
    set_last_processed_entry(last_processed_timestamp)
    log.info("Found %s entries in RSS feed of which %s were new. Last processed entry set to %s." %
                (len(sorted_entries), new_messages_count, last_processed_timestamp))

def process_feed():
    feed = feedparser.parse(RSS_FEED_URL)
    process_feed_response(feed)

log.info("Initialised rss-to-signal-bridge with poll interval of %s seconds." % POLL_INTERVAL)
while True:
    process_feed()
    time.sleep(POLL_INTERVAL)
