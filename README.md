<!-- @format -->

# Interlock-Bouncer

<img src="./bouncer-dark.png" align="right" width="250" height="250"/>

Interlock-Bouncer is a Discord bot that scans your server for
malicious links and neutralizes them. It does this by querying our
database of known-malicious sites. If the site is new, we use our
proprietary visual AI to identify 0-day phishing sites. Setup takes
just a minute or two and it begins protecting your server instantly.

Bouncer is a project of [Interlock](https://www.interlock.network/), a web3 company that is
decentralizing security. It's free to use in exchange for an
occasional Interlock partnership post. In the future,
Bouncer will be powered by $ILOCK, Interlock's token
launching later this year. The repo is at
[https://github.com/interlock-network/interlock-bouncer](https://github.com/interlock-network/interlock-bouncer).

You can check out our [FAQ](https://interlock-network.github.io/interlock-bouncer/) for more information.

# Status

Bouncer is in alpha. It occasionally shows false positives -- safe links marked as dangerous.
We're also adding new features all the time.

# Authorizing for your server

If you are an alpha user, contact us for the URL to authorize Bouncer to run on your own server.

Not yet an alpha user? Contact Magnitude on our [Discord server](https://discord.gg/ezraXYD8) and let's talk!

# Testing

To test if Bouncer is working, post the following
known-unsafe link in a channel Bouncer is monitoring:
`http://phishing.com`

Your message should immediately be deleted and Bouncer should post the following:

```
Message contains dangerous links! NAME: http://phishing.com
```

Here's a screenshot of the expected behavior:

<img width="421" alt="Interlock-Bouncer reacting to a malicious link" src="screenshot.png">

# Adding to the allowlist

The allowlist is a set of URLs that are marked as safe by a server. In
order to add an element to the allowlist invoke the following command:

`!allow_domains url1.com url2.com`

where `url1.com` and `url2.com` represent URLs that you wish to add to
the allowlist. Allowlists are not shared between servers.

# Flowchart

The flowchart below will give you an idea of how Bouncer works.

```mermaid
graph TD;
A([Bouncer detects message with a URL]) --> B{Is URL allowlisted by guild owner?}
B --> |Yes|M[Bouncer leaves message untouched]
B -.- |No|F["Bouncer sends URL to backend (BE)"]
F --> P{Is URL listed in BE?}
P -.- |Yes|G[URL known safe]
P -.- |No|I{Is URL found safe through visual AI?}
G --> J[BE sends safe]
H --> K[BE sends unsafe]
I -.-> |Yes|J[BE sends safe]
I -.-> |No|K
P -.- |Yes|H[URL known unsafe]
J --> M[Bouncer leaves message untouched]
M --> O([Bouncer done])
E --> O
K --> E[Bouncer blocks URL by deleting original message <br> and posts new message alerting users]
```

# Important files

To understand what Bouncer does in code, the best place to start is in `source/bouncer.py` .

# Infrastructure

Bouncer clients are run on AWS EC2 instances in the us-west-2 region.

# Maintainer

The maintainer for Bouncer is [@jmercouris](https://github.com/jmercouris).
