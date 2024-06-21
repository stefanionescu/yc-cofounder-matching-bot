# YC Cofounder Matching Bot

This repo hosts a Selenium bot that can help you find, save and contact potential cofounders on [YC Cofounder Matching](https://www.ycombinator.com/cofounder-matching).

* Automatically change your profile location and **search for cofounders in different cities**
* **Filter potential cofounders** depending on your shared interests
* **Save founder profiles** and **contact them** using your own template messages
* **Use ChatGPT to filter profiles**, depending on your cofounder criteria
* Receive **reports on your email** and see how many founder profiles were skipped, saved and contacted
* Run the bot with or without Docker

## Caveats
This bot works best if you set up your Cofounder Matching profile in such a way that it already filters for the right candidates. For example, the bot doesn't check (by default) if a founder is technical or not. You can specify that requirement on your profile or use the ChatGPT integration to filter for tech cofounders.

Moreover, the current version of the bot doesn't check whether a founder has a specific idea, has the same timing as you or if they fall within a specific age range. If you'd like any of these features to be added, let me know by [creating an Issue](https://github.com/stefanionescu/yc-cofounder-matching-bot/issues).

Finally, the bot will not search for cofounders in case you've already contacted 20 potential cofounders in a particular week.

## Requirements

Install [Python](https://www.python.org/downloads/) and [Docker](https://docs.docker.com/engine/install/) before you test the bot.

## Setup

Clone this repository and `cd` into it. Then, set up your virtual environment:

```pip<version> install virtualenv
python<version> -m venv venv
source venv/bin/activate
```

You should now be inside your virtual environment. You can install all the bot dependencies using:

```pip<version> install -r requirements.txt
```

### Environment Variables
You'll need to create a `.env` file and place it at the root of the directory. In it, you need to put the following variables:

- `USE_PROXY`: whether to use a [SmartProxy proxy](https://smartproxy.com/) or not. Totally optional. Values are `true` or `false`
- `SMART_PROXY_USERNAME`, `SMART_PROXY_PASSWORD`, `SMART_PROXY_ENDPOINT`, `SMART_PROXY_PORT`: you get all these params once you create a SmartProxy account and pick Residential Proxies. Check this [video guide](https://smartproxy.com/blog/how-to-set-up-and-use-residential-proxies) for more information about Residential Proxies
- `YC_USERNAME` and `YC_PASSWORD`: the username and password you use to log into YC Cofounder Matching
- `YC_CITIES`: a list of cities separated by commas. These are all the cities that the bot will loop through, from left to right, and search for cofounders. **Make sure to write each city name exactly like you see it on your Cofounder Matching profile section**. You can search for cities under My Profile > Basics > Location. Also, pro tip: you can omit this environment var and the bot will only search for founders in the current Location you set for your profile
- `CITY_TO_RETURN_TO`: this is the city your profile will be set to after the bot finishes searching for cofounders
- `BOT_MAX_RUN_TIME`: this the the max amount of time (in seconds) that the bot will search for. Set this to a value anywhere between `600` (10 minutes) and `1500` (25 minutes)
- `CONTACT_COFOUNDERS`: `true` or `false`. Determines whether the bot will send messages to cofounders that it deems as a good fit. If this is set to `false`, the bot will save promising profiles under Revisit Profiles > Saved Profiles so you can check them out later
- `MAX_PROFILES_TO_CONTACT`: this is the max number of promising cofounders that the bot will contact in a single run. You can set this to a more conservative value (less than 20) in case you want to double-check profiles before you reach out. NOTE that if the bot finds a promising profile and it cannot contact founders anymore, it will save the profile under Revisit Profiles > Saved Profiles

For more details about environment variables, check the [example file](./.env.example).

