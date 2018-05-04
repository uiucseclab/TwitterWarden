# Twitter Warden

Code for the CS 460 final project of Tristan Gurtler. Designed as a weak and open-source replication of [Botometer](https://botometer.iuni.iu.edu/). A more detailed report of the work done for the project is also in this repository as "report.pdf" (with significant analysis of projects like Botometer, Twitter's current efforts to abate fraudulent and abusive behavior, and the ecosystem of abusive behavior on Twitter over the past few years).

This code expects twitter credentials to be placed in a file named "credentials.py" like so: it should define two functions -- one named APP_KEY() and one named ACCESS_TOKEN() -- which each return a string as named. If you do not have credentials or do not remember them, you can obtain them [here](https://apps.twitter.com/).

This code makes alterations upon work done by Tristan Gurtler for a previous project [seen here](https://github.com/tristangurtler/twitter-influence-propagation-code). The code used Twython in order to download tweets and user data from Twitter; alterations were made in order to collect the relevant information used for this project.

This code uses work done by [Nick Galbreath](https://github.com/client9) in translating between Twitter Snowflake IDs and UTC timecodes, which is released to the public domain.

## Running this code

Assuming that credentials.py is correctly set up, this code also expects that a file named "varol-2017.dat" is present (it is [available here](https://botometer.iuni.iu.edu/bot-repository/datasets.html)). This repository represents a gold standard for determining the status of 2573 as bot accounts or human accounts. The code also expects two folders to be present to receive data ("bot_data" and "real_data"); this is necessary because collecting data from Twitter is very slow, and if an error is made partway through (or internet connection lost, etc.), it would be preferred not to lose the data already collected.

With this in place, merely run ```python collectData.py``` from the folder in which the program resides. If you stop it early, running it again should not incur any loss, although since it currently randomly selects users, there is no guarantee it will select the same user again (some modification may be necessary, such as loading the user list from file by uncommenting some lines, or allowing for files not in the random selection to be used for feature collection)

## Success of this code

In the [original study](https://aaai.org/ocs/index.php/ICWSM/ICWSM17/paper/view/15587/14817) of the Botometer system, the gold standard data (which I reuse here) had an inter-annotator agreement of 75%. This seems relatively unsurprising, since determining if an account is a bot or not is not significantly easy. It is remarkable (and suspect) that the authors of the paper report success rates significantly above this inter-annotator agreement (how can you trust a gold standard if you outperform the people involved in deciding it?). While my replication does not have as high a degree of success as they report (accuracy of approximately 80%, precision of approximate 79.5%, recall of approximately 78.6% versus their reported accuracy of 89%), this is not unexpected considering the smaller data pool I was using (only 64 humans and 48 bots, versus their total of 2573 users) and the limited features I was using to attempt the replication (details of the limitations I encountered are in the report).
