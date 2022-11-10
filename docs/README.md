<!-- @format -->

<img src="bouncer-dark.png" alt="Bouncer hand logo" align="right" width="250" height="250" style="padding: 1rem"/>

# Bouncer FAQ

### What is Bouncer? How does it work?

Interlock-Bouncer is an [open-source](https://github.com/interlock-network/interlock-bouncer) Discord bot that scans your server for malicious links and neutralizes them. It does this by querying our database of known-malicious sites. If the site is new, we use our proprietary visual AI to identify 0-day phishing sites. Setup takes just a minute or two and it begins protecting your server instantly.

### Who makes Bouncer?

Bouncer is a project of [Interlock](https://www.interlock.network/), a web3 company that is decentralizing security.

### Is Bouncer in beta?

Yes! We are actively fixing bugs and making incremental improvements in existing features. But we are not currently adding new features.

### How much does Bouncer cost?

While in testing, Bouncer is free to use in exchange for an occasional Interlock partnership post. In the future, Bouncer will be powered by $ILOCK, Interlock's token launching early 2023.

### Where can I see the source code?

The Bouncer repo is at [https://github.com/interlock-network/interlock-bouncer](https://github.com/interlock-network/interlock-bouncer). The pipeline that scans URLs is proprietary, because if hackers could read the code they could figure out new ways to circumvent it.

### Do I have to install any software to get Bouncer running?

Nope! Bouncer clients are run on Interlock's DigitalOcean droplet.

### How can I get Bouncer for my Discord server?

To get Bouncer for your server, email dan@interlock.network. You can also message Magnitude on the [Interlock Discord](https://discord.gg/ezraXYD8).

### What are my next steps after inviting Bouncer?

1. Add Bouncer as a friend to receive DMs, like links to the web editor.
2. Assign a role to Bouncer (if users need a role to participate in public channels)
3. Use `/add_to_allowlist https://your_url1.com https://your_url2.com` to add your URLs to Bouncer's allowlist

### How do I get Bouncer to protect a channel?

First, click on settings for the channel.

<img width="421" alt="Clicking on a channel's settings" src="edit_channel.png">

Then, invite Bouncer to the channel and give it Admin access. That's so Bouncer can delete unsafe messages and do what it needs to protect the channel.

<img width="421" alt="Invite Bouncer to the channel" src="invite.png">

### I've installed Bouncer! How can I make sure it's working as expected?

Post the following known-unsafe link in a channel Bouncer is monitoring:
`http://phishing.com`

Your message should immediately be deleted and Bouncer
should post the following:

```
Message contains dangerous links! NAME: http://phishing.com
```

Here's a screenshot of the expected behavior:

<img width="421" alt="Interlock-Bouncer reacting to a malicious link" src="screenshot.png">

### Where can I see Bouncer's actions?

Bouncer logs its activity to the channel "#bouncer-log". There you can see when:

- Bouncer deletes a malicious URL, complete with:
  - Username of who posted the URL
  - Channel it was posted in
  - The malicious URL
  - The message it was in (for context)
- A mod adds to an allowlist (or removes from one)
  - And mod name
- A mod blocks all URLs from a channel (or vice versa)
  - And mod name

### What's an allowlist? How can I add to my server's allowlist?

The allowlist is a set of URLs that are marked as safe by a server. In
order to add an element to the allowlist invoke the following command:

`/add_to_allowlist https://url1.com https://url2.com`

where `url1.com` and `url2.com` represent URLs that you wish to add to
the allowlist. Allowlists are not shared between servers.

### How can I remove URLs from the allowlist?

Use the slash command `/remove_from_allowlist https://url1.com` to remove just `url1.com` from the allowlist.

### How can I show all the URLs on the allowlist?

Use the slash command `/show_allowlist` to list all the URLs on the allowlist.

### How can I block all links in a channel?

To block all URLs in a channel, do this:

`/block_links`

To cancel this action and allow URLs again in a channel, do this:

`/unblock_links`

### Can you show me a flowchart of how Bouncer works?

I'm glad you asked. The flowchart below will give you an idea of how Bouncer works.

<img width="421" alt="Flowchart of how Bouncer works" src="flowchart.png">
