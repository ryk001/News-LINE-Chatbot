# Don't hava a GF? Wake up yourself with a daily news LINE message!

## only 3 steps to activate this daily news LINE chatbot!
- Setup LINE notify token
- Setup your news keywords
- Setup GitHub actions

## Step 0. fork this to your account
Click the Fork project in the upper right corner.

![run](https://s2.loli.net/2022/12/06/1ta8qHFNBWjQuUb.png)

## Step 1. Setup LINE notify token
- go to https://notify-bot.line.me to request your own token
- back to repo page, click `Settings`-->`Secrets`-->`New secret`

![run](https://s2.loli.net/2022/12/07/7lvh9u3ayXZkIAm.png)

- create a secret named `LINE_NOTIFY_TOKEN`, and fillin your LINE Notify token

## Step 2. Setup your news keywords
- back to repo page, edit the `keyword_watchlist.txt` file
- notice: no space between comma and keywords

## Step 3. Setup GitHub actions
- click `Actions` on the top, then click `Sending-News` on the right, and then click `Run workflow`

![run](https://s2.loli.net/2022/12/07/jQufzoTSVdcbsn2.png)

- voila, now you have a daily news LINE chatbot!
