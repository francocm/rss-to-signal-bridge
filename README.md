# rss-to-signal-bridge

Polls RSS feed and publishes message onto Signal using [signal-cli-rest-api](https://github.com/bbernhard/signal-cli-rest-api).

## Configuration

| Key | Type | Required | Description | Example |
| --- | ---- | -------- | ----------- | ------- |
| `SIGNAL_API_URL` | String | Yes | `http://127.0.0.1:8080/v2/send` | The message send endpoint of your hosted [signal-cli-rest-api](https://github.com/bbernhard/signal-cli-rest-api) instance. | 
| `SIGNAL_SENDER_NUMBER` | String | Yes | `+44xxxxxxxxxx` | The sender number as configured on your [signal-cli-rest-api](https://github.com/bbernhard/signal-cli-rest-api) instance. | 
| `SIGNAL_DESTINATIONS` | String | Yes | `group.xxxxxxxxxxxxx=` (just 1 group) or comma separated numbers ex: `+44xxxxxxxxxx,+44yyyyyyyyyy` | The recipients of the message. If the recipient is a group, put just 1 group ID here, else comma separated list of numbers. For details on how to obtain the group ID follow the [signal-cli-rest-api documentation](https://github.com/bbernhard/signal-cli-rest-api/blob/master/doc/EXAMPLES.md). | 
| `SIGNAL_FAKE_SEND` | Python Boolean | No | `False` | If `True`, no message is sent to Signal, and instead each message is printed into the logs. This is important whilst debugging / testing, to avoid overuse of the service. | 
| `RSS_FEED_URL` | String | Yes | `https://xxxxxxxxxxxxx` | The RSS feed URL to poll. | 
| `MESSAGE_TEMPLATE` | String | Yes | `NEW STOCK ALERT\n\n{title}\n\n{summary}\n\n{link}\n\n{publish_timestamp}` | The message template, The placeholders show in the example are replaced with the RSS content. Move these around / use these in whichever way you want. | 
| `RSS_POLL_INTERVAL` | int | Yes | `120` | Number of seconds between each RSS poll interval. | 

## Running (via docker-compose)

1. `cp docker-compose.yml.example docker-compose.yml`
2. Configure the environment variables (and any other relevant configuration) inside [docker-compose.yml](docker-compose.yml).
3. `docker-compose up -d`

### Important

* This script saves the state under `data/state.dat`.
    * It's important:
        * that this file is mounted from the host into the container (the example [docker-compose.yml](docker-compose.yml.example) already has this set up)
        * for the container to have write permissions into this folder so as to be able to create this file.
    * This file is used to save the last processed RSS entry from the RSS feed, so as not to end up re-sending the same alerts over and over.
    * If this file is corrupted, lost, or somehow broken, it can lead to the script either breaking, or flooding Signal / recipients with alerts.

***EOF***   
