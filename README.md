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

Finally, the bot will not loop through profiles in case you've already contacted 20 potential cofounders in a particular week.

## Requirements

Install [Python](https://www.python.org/downloads/) and [Docker](https://docs.docker.com/engine/install/) before you test the bot.

## Setup

Clone this repository and `cd` into it. Then, set up your virtual environment:

```
pip<version> install virtualenv
python<version> -m venv venv
source venv/bin/activate
```

You should now be inside your virtual environment. You can install all the bot dependencies using:

```
pip<version> install -r requirements.txt
```

### Environment Variables

You'll need to create a `.env` file and place it at the root of the directory. In it, you need to put the following variables:

- `USE_PROXY`: whether to use a [SmartProxy proxy](https://smartproxy.com/) or not. Totally optional. Values are `true` or `false`
- `SMART_PROXY_USERNAME`, `SMART_PROXY_PASSWORD`, `SMART_PROXY_ENDPOINT`, `SMART_PROXY_PORT`: you get all these params once you create a SmartProxy account and pick a Residential Proxy. Check this [video guide](https://smartproxy.com/blog/how-to-set-up-and-use-residential-proxies) for more information about Residential Proxies
- `YC_USERNAME` and `YC_PASSWORD`: the username and password you use to log into YC Cofounder Matching
- `YC_CITIES`: a list of cities separated by semicolons. These are all the cities that the bot will loop through, from left to right, and search for cofounders. **Make sure to write each city name exactly like you see it on your Cofounder Matching profile section**. You can search for cities under My Profile > Basics > Location. Also, pro tip: you can omit this environment var and the bot will only search for founders in the current Location you set for your profile
- `CITY_TO_RETURN_TO`: this is the city your profile will be set to after the bot finishes searching for cofounders
- `BOT_MAX_RUN_TIME`: this is the max amount of time (in seconds) that the bot will search for. Set this to a value anywhere between `600` (10 minutes) and `1500` (25 minutes)
- `CONTACT_COFOUNDERS`: `true` or `false`. Determines whether the bot will send messages to cofounders that it deems as a good fit. If this is set to `false`, the bot will save promising profiles under Revisit Profiles > Saved Profiles so you can check them out later
- `MAX_PROFILES_TO_CONTACT`: this is the max number of promising cofounders that the bot will contact in a single run. You can set this to a more conservative value (less than 20) in case you want to double-check profiles before you reach out. **NOTE** that if the bot finds a promising profile and it cannot contact founders anymore, it will save the profile under Revisit Profiles > Saved Profiles
- `SKIP_YC_ALUMNI`: `true` or `false`. A flag that tells the bot whether it should skip founders who already went through YC
- `IMPORTANT_SHARED_INTERESTS`: groups of interests that a potential cofounder must share with you. Each group must be separated by semicolons. Each element in a group must be separated by commas. Example: `Marketplace,Travel / Tourism;Gaming` has two groups: Marketplace + Travel / Tourism is the first one and Gaming is the second
- `ANALYZE_PROFILES_WITH_GPT`: `true` or `false`. Whether the bot will use GPT to analyze founder profiles and determine if they are a fit or not
- `OPENAI_API_KEY`: your OpenAI API key, in case you want to use GPT for your cofounder search
- `CHAT_GPT_ORGANIZATION` and `CHAT_GPT_PROJECT_ID`: your GPT org and project IDs
- `CHAT_GPT_QUESTIONS`: questions that you want GPT to answer about a profile in order to determine if the bot should save or contact a founder. **GPT must be be able to answer each question with a simple yes or no**. An example of a good question is `"Does this person have less than 3 years of coding/programming experience?"`. An example of a bad question is: `"How many years of experience does this person have?"`. If GPT answers at least one question with Yes, it will save the founder's profile. If, instead, GPT answers all questions with No (and if you allow the bot to contact founders), it will contact the founder.
- `EMAIL_FROM`, `EMAIL_FROM_PASSWORD`, `EMAIL_TO`: sender and receiver data used by the bot to send reports to your email after it's done searching
- `SENDGRID_API_KEY`: the bot uses SendGrid to send you emails. Sign up for a free SendGrid API key [here](https://signup.sendgrid.com/)

For more details about environment variables, check the [example file](./.env.example).

### Founder Messages
Before you run the bot and start to contact founders, check [this comment](https://github.com/stefanionescu/yc-cofounder-matching-bot/blob/6d0bd4c32fa20581de7fc0112b93a7dcfde7f4f2/example_founder_messages.py#L2) from `example_founder_messages.py`. The position of each message inside `founder_messages` is linked to the position of each shared interest group from `IMPORTANT_SHARED_INTERESTS`. Make sure to match messages and interest groups properly.

If you want the bot to message founders, create a file called `founder_messages.py` at the root of the project and place your messages in it, similar to how it's done in [`example_founder_messages.py`](./example_founder_messages.py). Otherwise, put the following code in `founder_messages.py`:

```
founder_messages = []
```

### Founder Profile Data

The bot always checks the `Our shared interests` section to determine if a cofounder is a potential fit. If you set `ANALYZE_PROFILES_WITH_GPT` to `true`, the bot will also use information from `Intro`, `Life Story`, `Free Time`, `Other`, `Impressive accomplishment`, `Equity expectations` and `Potential ideas` to check for cofounder compatibility.

### Run the Bot

The simplest way to run the bot is to execute the following:

```
python<version> get_cofounder.py
```

If you want to see the bot interact with the browser, comment the following lines from [`get_cofounder.py`](./get_cofounder.py):

```
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--headless=new')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-infobars')
chrome_options.add_experimental_option("useAutomationExtension", False)
```

In order to run the bot with Docker, execute the following:

```
docker build -t yc-cofounder-matching-bot .
docker run -it yc-cofounder-matching-bot
```
