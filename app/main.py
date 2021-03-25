import os
from datetime import datetime

import stripe
from dhooks import Embed, Webhook
from dotenv import load_dotenv
from flask import Flask, request

load_dotenv()

app = Flask(__name__)

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_ENDPOINT_SECRET')
DISCORD_WEBHOOK = Webhook(os.environ.get('DISCORD_WEBHOOK'))

EVENTS = [
	'customer.created',
	'customer.updated',
	'customer.deleted',
	'customer.subscription.created',
	'customer.subscription.updated',
	'invoice.paid'
]

@app.route('/', methods=['POST'])
def stripe_endpoint():
	body = request.data.decode('utf-8')
	signature_header = request.headers.get('Stripe-Signature', None)

	try:
		event = stripe.Webhook.construct_event(
			body, signature_header, STRIPE_WEBHOOK_SECRET
		)

		if event['type'] in EVENTS:
			embed = Embed(
				title=' '.join(event['type'].split('.')).title(),
				color=0x646EDE,
				timestamp='now'
			)
			embed.set_footer(text=event['data']['object']['id'], icon_url='https://i.imgur.com/FpXfweu.png')

			if 'subscription' in event['type']:
				subscription = event['data']['object']

				embed.description = '> [**Customer**](https://dashboard.stripe.com/customers/{})\n'\
									'> [**Subscription**](https://dashboard.stripe.com/subscriptions/{})'.format(
										subscription['customer'],
										subscription['id']
									)

				if subscription.get('canceled_at'):
					embed.add_field(name='**Status**', value=subscription['status'].title())
					embed.add_field(
						name='**Canceled**',
						value=datetime.fromtimestamp(subscription['canceled_at']).strftime('%B %-d, %Y')
					)
					embed.add_field(
						name='**Ends**',
						value=datetime.fromtimestamp(subscription['cancel_at']).strftime('%B %-d, %Y')
					)
				else:
					embed.add_field(name='**Status**', value=subscription['status'].title())
					embed.add_field(
						name='**Starts**',
						value=datetime.fromtimestamp(subscription['current_period_start']).strftime('%B %-d, %Y')
					)
					embed.add_field(
						name='**Renews**',
						value=datetime.fromtimestamp(subscription['current_period_end']).strftime('%B %-d, %Y')
					)

			elif 'customer' in event['type']:
				customer = event['data']['object']
				embed.description = '> [**Customer**](https://dashboard.stripe.com/customers/{})'.format(customer['id'])

				if customer.get('description'):
					embed.description = customer['description']
				if customer.get('name'):
					embed.add_field(name='**Name**', value=customer['name'])
				if customer.get('email'):
					embed.add_field(name='**Email**', value=customer['email'])
				if customer.get('address'):
					embed.add_field(name='**Address**', value=customer['address'], inline=False)

			elif 'invoice' in event['type']:
				invoice = event['data']['object']
				embed.description = '> [**Customer**](https://dashboard.stripe.com/customers/{})\n'\
									'> [**Invoice**](https://dashboard.stripe.com/invoices/{})'.format(
										invoice['customer'],
										invoice['id']
									)

				embed.add_field(name='**Status**', value=invoice['status'].title())
				embed.add_field(
					name='**Amount Paid**',
					value='{} {}'.format(float(invoice['amount_paid']) / 100, invoice['currency'].upper())
				)
				embed.add_field(name='**Attempts**', value=str(invoice['attempt_count']))
				embed.add_field(name='**Customer Email**', value=invoice['customer_email'])

			DISCORD_WEBHOOK.send(embed=embed, username='StripeCord')

		return '', 200
	except stripe.error.SignatureVerificationError:
		return 'Bad Request', 400
	except:
		return 'Internal Server Error', 500

@app.errorhandler(404)
def page_not_found(e):
	return 'Not Found', 404
