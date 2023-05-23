# Capital Position Tracker

This script polls [Capital](https://capital.com/) for changes to your position and post them on a Telegram group using a telegram bot. It's a great way for people in the telegram group to keep track of your positions on Capital.

## Setup

1. Clone this repository to your local machine.

```bash
git clone https://github.com/VisarDomi/capital-position-tracker-telegram-bot.git
```

2. Navigate to the directory of the project.

```bash
cd capital-position-tracker-telegram-bot
```

3. Create a `.env` file in the root directory of the project and add the following environment variables:

```bash
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
CAPITAL_API_KEY=your_capital_api_key
CAPITAL_LOGIN=your_capital_login
CAPITAL_PASSWORD=your_capital_password
```

Replace `your_telegram_bot_token`, `your_telegram_chat_id`, `your_capital_api_key`, `your_capital_login`, and `your_capital_password` with your actual values.

## Running the Script

It's recommended to first create a virtual env, using python 3.10:

```bash
python -m venv .venv
```

Active the virtual env, for example in windows:

```powershell
.\.venv\Scripts\Activate.ps1
```
or linux:

```bash
source .venv/Scripts/activate
```
Install the dependencies from requirements.txt:

```bash
pip install -r requirements.txt
```

Finally, you can now run the script locally:

```bash
python main.py
```

The script will start polling Capital for changes to your position and post them on the specified Telegram group.

The next time you want to run this script in windows, run the file start-script.ps1 with powershell, by right-clicking and selecting run with powershell.

## Logging

The script logs all its activity and saves it into daily log files in the logs folder. The log files are named `app.log.YYYYMMDD`, where `YYYYMMDD` is the date.
