# StripeCord - Stripe Events to Discord Webhook

Easily receive Stripe events in a Discord channel.

### Prerequisites

* Discord webhook.
* Heroku application.
* Stripe webhook and signing secret. Use <https://your-app.herokuapp.com> as endpoint URL.

### Setup

1. Clone this repository.
2. Run `cp .env.sample .env` to create your `.env` file.
3. Input your Discord webhook, Stripe secret key and webhook signing secret in the new `.env` file.
4. Commit changes to a private repository in your account.
5. Create a new app on Heroku.
6. Go to Deploy, then link your GitHub and connect your repository.
7. Select and deploy `main` branch.
