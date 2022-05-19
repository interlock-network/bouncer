# Authorizing Interlock-bouncer for your server

Visit the following URL to authorize Interlock-bouncer to run on your own
server:
https://discord.com/api/oauth2/authorize?client_id=966558765799342131&permissions=1641751637056&scope=bot

# Testing Interlock-bouncer

To test if Interlock-bouncer is working, post the following
known-unsafe link in a channel Interlock-bouncer is monitoring:
`http://phishing.com`

Your message should immediately be deleted and Interlock-bouncer
should post the following:

```
Message contains dangerous links! NAME: http://phishing.com
```
