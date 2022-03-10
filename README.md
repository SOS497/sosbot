[![Pylint](https://github.com/SOS497/sosbot/actions/workflows/pylint.yml/badge.svg)](https://github.com/SOS497/sosbot/actions/workflows/pylint.yml)
[![CodeQL](https://github.com/SOS497/sosbot/actions/workflows/codeql-analysis.yml/badge.svg?branch=main)](https://github.com/SOS497/sosbot/actions/workflows/codeql-analysis.yml)
[![Snyk Scan](https://github.com/SOS497/sosbot/actions/workflows/snyk-scan.yml/badge.svg)](https://github.com/SOS497/sosbot/actions/workflows/snyk-scan.yml)

# sosbot - SOS 497's Discord bot

This bot is designed to work with Google Sheets to track definitions for terms and links + descriptions associated with different datasets or topics.


## Configuration

Configuration is designed to be in `$HOME/.config/sauced` and include a `config.yaml` file along with a Google service account credential, referenced from the YAML configuration file. The configuration file format is:

```yaml
---
discord:
  token: "SOME-TOKEN"

google:
  creds-json: "/home/USER/.config/sosbot/google-creds.json"

  definitions-sheet: "SHEET-ID-FROM-URL"
  datasets-sheet: "SHEET-ID-FROM-URL"
```


### A Note on Setting Up the Service Account and Spreadsheets

Once you have a Google service account, you'll need to click on the `Keys` tab for the service account and create a new key. Choose the JSON option, and save the file in a path that you'll reference from `config.yaml` (see above).

**NOTE:** You'll also need to authorize this service account to modify your chosen spreadsheets, by sharing the spreadsheets with the account and marking it as an Editor. You can find the service account email address in the JSON file you downloaded.


## Running This Bot

Currently, to run this bot, you have to setup a virtualenv and install the dependencies:

```bash
$ python -m venv sosbot-venv
[...]
$ source sosbot-venv/bin/activate
$ pip install -r ./requirements.txt
````

Then, you can run the bot itself with:

```bash
$ source ./sosbot-venv/bin/activate
$ ./start.py
```
