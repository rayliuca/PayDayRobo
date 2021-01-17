# PayDayRobo

## Inspiration
There are many popular tools around to help people contribute to their passive investment, i.e. Passiv, but there is no tool around (that I know of) that helps people manage their investment withdrawal. Thus, the goal of this project is to help the retired populations to manage their assets.

## What it does
This program retrieves the account data from Questrade, then calculate the number of ETF/ stock shares to sell while maintaining the pre-defined portfolio allocation, withdrawal goal, and minimize the commission fees. These optimizations are achieved through a genetic algorithm. The resulting solution is then sent through either SMS, email, or both.

## How we built it
This project is built using Python with ❤️
## Dependencies:
  - sendgrid
  - qtrade
  - twilio
  - pyeasyga

## Deployment (as a cron job):
1. open the crontab: crontab -e
2. add an entry so it runs on the first day of every month:

  0 0 1 * * /full_path/PayDayRobo/script.py

3. save the crontab file

## Accomplishments that we're proud of
Got the script working!

## What's next for PayDayRobo
Dockerize the script

## Notification Sample
SMS:
![SMS message](./assets/SMS.png)

Email:
![Email message](./assets/email.png)
