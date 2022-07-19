# -*- coding: utf-8 -*- 
from odoo import models, fields, api, _
from odoo.exceptions import Warning, ValidationError, UserError
from jinja2 import Environment, BaseLoader
from odoo.tools import float_is_zero, float_compare, safe_eval, date_utils, email_split, email_escape_char, email_re
import logging
_logger = logging.getLogger(__name__)

class AccPayExt(models.Model):
	_inherit = 'account.payment'

	invoice_tree = fields.One2many('payment.invoice.tree', 'tree_link', ondelete='cascade')
	# deleted_tree = fields.Many2many('payment.invoice.tree', "temp")
	bank_acc_id = fields.Many2one('account.account', string = "Bank Charges Account")
	journal_entry_id = fields.Many2one('account.move', string = "Bank Charges JE")
	inv_recs = fields.Integer(string="Is Invoices")
	not_register_payment = fields.Boolean(string = "Not Register Payment")



	# def action_register_payment(self):
		# res = super(AccPayExt, self).action_register_payment()

		# active_ids = self.env.context.get('active_ids')
		# amount = 0
		# moves = self.env['account.move'].search([('id','in',active_ids)])
		# for move in moves:
		#   amount += move.amount_residual

		# res['default_amount'] = amount

		# print ("RRRRRRRRRRR")
		# print (res)
		# print ("RRRRRRRRRRR")

		# return res
	# def action_register_payment(self):
	# 	active_ids = self.env.context.get('active_ids')
	# 	if not active_ids:
	# 		return ''

	# 	custom_context = self.env.context
	# 	print ("CCCCCCCCCCCCCCCCCCCCCCCCCCCCC")
	# 	print (custom_context)
	# 	print (active_ids)
	# 	print ("CCCCCCCCCCCCCCCCCCCCCCCCCCCCC")
	# 	if active_ids:
	# 		invoice_tree_recs = []
	# 		amount = 0
	# 		moves = self.env['account.move'].search([('id','in',active_ids)])
	# 		for move in moves:
	# 			amount += move.amount_residual
	# 		  # invoice_tree_recs.append((0,0,{
	# 		  #     'reconcile':True,
	# 		  #     'invoice_id':move.id,
	# 		  #     'invoice_amount':move.amount_total,
	# 		  #     'invoice_residual_amount':move.amount_residual,
	# 		  #     # 'partner_id':self.partner_id.id,
	# 		  #     }))

	# 	  # custom_context["default_invoice_tree"] = invoice_tree_recs
	# 	  # custom_context['default_invoice_ids']= active_ids
	# 	  # custom_context['default_currency_id']=moves[0].currency_id.id
	# 		custom_context['amount'] = amount

	#   # print ("22222222222222222222222222")
	#   # print (custom_context)
	#   # print (active_ids)
	#   # print ("22222222222222222222222222")
	# 	return {
	# 	  'name': _('Register Payment'),
	# 	  'res_model': len(active_ids) == 1 and 'account.payment' or 'account.payment.register',
	# 	  'view_mode': 'form',
	# 	  'view_id': len(active_ids) != 1 and self.env.ref('account.view_account_payment_form_multi').id or self.env.ref('account.view_account_payment_invoice_form').id,
	# 	  # 'context': self.env.context,
	# 	  'context': custom_context,
	# 	  'target': 'new',
	# 	  'type': 'ir.actions.act_window',
	#   }

	@api.onchange('payment_type')
	def get_tree_invoices_clean(self):
		if self.payment_type == 'transfer':
			self.invoice_tree = False

	def _prepare_payment_moves(self):
		''' Prepare the creation of journal entries (account.move) by creating a list of python dictionary to be passed
		to the 'create' method.

		Example 1: outbound with write-off:

		Account             | Debit     | Credit
		---------------------------------------------------------
		BANK                |   900.0   |
		RECEIVABLE          |           |   1000.0
		WRITE-OFF ACCOUNT   |   100.0   |

		Example 2: internal transfer from BANK to CASH:

		Account             | Debit     | Credit
		---------------------------------------------------------
		BANK                |           |   1000.0
		TRANSFER            |   1000.0  |
		CASH                |   1000.0  |
		TRANSFER            |           |   1000.0

		:return: A list of Python dictionary to be passed to env['account.move'].create.
		'''
		all_move_vals = []
		for payment in self:
			company_currency = payment.company_id.currency_id
			move_names = payment.move_name.split(payment._get_move_name_transfer_separator()) if payment.move_name else None

			# Compute amounts.
			write_off_amount = payment.payment_difference_handling == 'reconcile' and -payment.payment_difference or 0.0
			if payment.payment_type in ('outbound', 'transfer'):
				counterpart_amount = payment.amount
				liquidity_line_account = payment.journal_id.default_debit_account_id
			else:
				counterpart_amount = -payment.amount
				liquidity_line_account = payment.journal_id.default_credit_account_id

			# Manage currency.
			if payment.currency_id == company_currency:
				# Single-currency.
				balance = counterpart_amount
				write_off_balance = write_off_amount
				counterpart_amount = write_off_amount = 0.0
				currency_id = False
			else:
				# Multi-currencies.
				balance = payment.currency_id._convert(counterpart_amount, company_currency, payment.company_id, payment.payment_date)
				write_off_balance = payment.currency_id._convert(write_off_amount, company_currency, payment.company_id, payment.payment_date)
				currency_id = payment.currency_id.id

			# Manage custom currency on journal for liquidity line.
			if payment.journal_id.currency_id and payment.currency_id != payment.journal_id.currency_id:
				# Custom currency on journal.
				if payment.journal_id.currency_id == company_currency:
					# Single-currency
					liquidity_line_currency_id = False
				else:
					liquidity_line_currency_id = payment.journal_id.currency_id.id
				liquidity_amount = company_currency._convert(
					balance, payment.journal_id.currency_id, payment.company_id, payment.payment_date)
			else:
				# Use the payment currency.
				liquidity_line_currency_id = currency_id
				liquidity_amount = counterpart_amount

			# Compute 'name' to be used in receivable/payable line.
			rec_pay_line_name = ''
			if payment.payment_type == 'transfer':
				rec_pay_line_name = payment.name
			else:
				if payment.partner_type == 'customer':
					if payment.payment_type == 'inbound':
						rec_pay_line_name += _("Customer Payment")
					elif payment.payment_type == 'outbound':
						rec_pay_line_name += _("Customer Credit Note")
				elif payment.partner_type == 'supplier':
					if payment.payment_type == 'inbound':
						rec_pay_line_name += _("Vendor Credit Note")
					elif payment.payment_type == 'outbound':
						rec_pay_line_name += _("Vendor Payment")
				if payment.invoice_ids:
					rec_pay_line_name += ': %s' % ', '.join(payment.invoice_ids.mapped('name'))

			# Compute 'name' to be used in liquidity line.
			if payment.payment_type == 'transfer':
				liquidity_line_name = _('Transfer to %s') % payment.destination_journal_id.name
			else:
				liquidity_line_name = payment.name

			# ==== 'inbound' / 'outbound' ====

			move_vals = {
				'date': payment.payment_date,
				'ref': payment.communication,
				'journal_id': payment.journal_id.id,
				'currency_id': payment.journal_id.currency_id.id or payment.company_id.currency_id.id,
				'partner_id': payment.partner_id.id,
				'line_ids': [
					# Receivable / Payable / Transfer line.
					(0, 0, {
						'name': rec_pay_line_name,
						'amount_currency': counterpart_amount + write_off_amount if currency_id else 0.0,
						'currency_id': currency_id,
						'debit': balance + write_off_balance > 0.0 and balance + write_off_balance or 0.0,
						'credit': balance + write_off_balance < 0.0 and -balance - write_off_balance or 0.0,
						'date_maturity': payment.payment_date,
						'partner_id': payment.partner_id.commercial_partner_id.id,
						'account_id': payment.destination_account_id.id,
						'payment_id': payment.id,
					}),
					# Liquidity line.
					(0, 0, {
						'name': liquidity_line_name,
						'amount_currency': -liquidity_amount if liquidity_line_currency_id else 0.0,
						'currency_id': liquidity_line_currency_id,
						'debit': balance < 0.0 and -balance or 0.0,
						'credit': balance > 0.0 and balance or 0.0,
						'date_maturity': payment.payment_date,
						'partner_id': payment.partner_id.commercial_partner_id.id,
						'account_id': liquidity_line_account.id,
						'payment_id': payment.id,
					}),
				],
			}
			if write_off_balance:
				# Write-off line.
				move_vals['line_ids'].append((0, 0, {
					'name': payment.writeoff_label,
					'amount_currency': -write_off_amount,
					'currency_id': currency_id,
					'debit': write_off_balance < 0.0 and -write_off_balance or 0.0,
					'credit': write_off_balance > 0.0 and write_off_balance or 0.0,
					'date_maturity': payment.payment_date,
					'partner_id': payment.partner_id.commercial_partner_id.id,
					'account_id': payment.writeoff_account_id.id,
					'payment_id': payment.id,
				}))

			if move_names:
				move_vals['name'] = move_names[0]

			all_move_vals.append(move_vals)

			# ==== 'transfer' ====
			if payment.payment_type == 'transfer':
				journal = payment.destination_journal_id

				# Manage custom currency on journal for liquidity line.
				if journal.currency_id and payment.currency_id != journal.currency_id:
					# Custom currency on journal.
					liquidity_line_currency_id = journal.currency_id.id
					transfer_amount = company_currency._convert(balance, journal.currency_id, payment.company_id, payment.payment_date)
				else:
					# Use the payment currency.
					liquidity_line_currency_id = currency_id
					transfer_amount = counterpart_amount

				transfer_move_vals = {
					'date': payment.payment_date,
					'ref': payment.communication,
					'partner_id': payment.partner_id.id,
					'journal_id': payment.destination_journal_id.id,
					'line_ids': [
						# Transfer debit line.
						(0, 0, {
							'name': payment.name,
							'amount_currency': -counterpart_amount if currency_id else 0.0,
							'currency_id': currency_id,
							'debit': balance < 0.0 and -balance or 0.0,
							'credit': balance > 0.0 and balance or 0.0,
							'date_maturity': payment.payment_date,
							'partner_id': payment.partner_id.commercial_partner_id.id,
							'account_id': payment.company_id.transfer_account_id.id,
							'payment_id': payment.id,
						}),
						# Liquidity credit line.
						(0, 0, {
							'name': _('Transfer from %s') % payment.journal_id.name,
							'amount_currency': transfer_amount if liquidity_line_currency_id else 0.0,
							'currency_id': liquidity_line_currency_id,
							'debit': balance > 0.0 and balance or 0.0,
							'credit': balance < 0.0 and -balance or 0.0,
							'date_maturity': payment.payment_date,
							'partner_id': payment.partner_id.commercial_partner_id.id,
							'account_id': payment.destination_journal_id.default_credit_account_id.id,
							'payment_id': payment.id,
						}),
					],
				}

				if move_names and len(move_names) == 2:
					transfer_move_vals['name'] = move_names[1]

				all_move_vals.append(transfer_move_vals)
		return all_move_vals



	def post(self):
		""" Create the journal items for the payment and update the payment's state to 'posted'.
			A journal entry is created containing an item in the source liquidity account (selected journal's default_debit or default_credit)
			and another in the destination reconcilable account (see _compute_destination_account_id).
			If invoice_ids is not empty, there will be one reconcilable move line per invoice to reconcile with.
			If the payment is a transfer, a second journal entry is created in the destination journal to receive money from the transfer account.
		"""

		AccountMove = self.env['account.move'].with_context(default_type='entry')
		for rec in self:
			if rec.not_register_payment:

				if rec.state != 'draft':
					raise UserError(_("Only a draft payment can be posted."))

				if any(inv.state != 'posted' for inv in rec.invoice_ids):
					raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))

				# keep the name in case of a payment reset to draft
				if not rec.name:
					# Use the right sequence to set the name
					if rec.payment_type == 'transfer':
						sequence_code = 'account.payment.transfer'
					else:
						if rec.partner_type == 'customer':
							if rec.payment_type == 'inbound':
								sequence_code = 'account.payment.customer.invoice'
							if rec.payment_type == 'outbound':
								sequence_code = 'account.payment.customer.refund'
						if rec.partner_type == 'supplier':
							if rec.payment_type == 'inbound':
								sequence_code = 'account.payment.supplier.refund'
							if rec.payment_type == 'outbound':
								sequence_code = 'account.payment.supplier.invoice'
					rec.name = self.env['ir.sequence'].next_by_code(sequence_code, sequence_date=rec.payment_date)
					if not rec.name and rec.payment_type != 'transfer':
						raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))
				payment_rec = rec._prepare_payment_moves()
				if rec.invoice_tree:

					new_payments = []
					payment_id = 0
					debit_account_id = 0
					credit_account_id = 0
					for x in payment_rec[0]['line_ids']:
						if x[2]['debit'] != 0:
							debit_account_id = x[2]['account_id']
						else:
							credit_account_id = x[2]['account_id']
						payment_id = x[2]['payment_id']
					

					company_currency = rec.company_id.currency_id
					for x in rec.invoice_tree:
						if x.invoice_id.currency_id != rec.currency_id and rec.not_register_payment:
							raise ValidationError("Please re-generate invoices first.")
						converted_amount = rec.currency_id._convert(x.reconciled_amount, company_currency, rec.company_id, rec.payment_date)
						if payment_id != 0 and credit_account_id != 0 and x.reconciled_amount > 0:
							# new_payments.append(x)

							balance = -(x.reconciled_amount)
							balance = rec.currency_id._convert(balance, company_currency, rec.company_id, rec.payment_date or fields.Date.today())

							val_debit = balance > 0 and balance or 0.0
							val_credit = balance < 0 and -balance or 0.0
							new_payments.append((0, 0,
								{
									# 'name': 'Customer Payment',
									'name': x.invoice_id.name,
									'amount_currency': -(x.reconciled_amount),
									'currency_id': rec.currency_id.id,
									'debit': val_debit,
									'credit': val_credit,
									'date_maturity': rec.payment_date,
									'partner_id': rec.partner_id.id,
									'account_id': credit_account_id,
									'payment_id': payment_id
								}))
						if payment_id != 0 and debit_account_id != 0 and x.reconciled_amount > 0:
							balance = x.reconciled_amount
							balance = rec.currency_id._convert(balance, company_currency, rec.company_id, rec.payment_date or fields.Date.today())
							val_debit = balance > 0 and balance or 0.0
							val_credit = balance < 0 and -balance or 0.0
							new_payments.append((0,0,
								{
									'name': "Payment",
									'amount_currency': x.reconciled_amount,
									'currency_id': rec.currency_id.id,
									'debit': val_debit,
									'credit': val_credit,
									'date_maturity': rec.payment_date,
									'partner_id': rec.partner_id.id,
									'account_id': debit_account_id,
									'payment_id': payment_id
								}))

					# managing writeoff
					if rec.payment_difference_handling == 'reconcile':
						if payment_rec:
							for wo in payment_rec[0]['line_ids']:
								if wo[2]['name'] == rec.writeoff_label:
									new_payments.append((0,0,
										{
										'name': wo[2]['name'],
										'amount_currency': wo[2]['amount_currency'],
										'currency_id': wo[2]['currency_id'],
										# 'debit': wo[2]['debit'],
										# 'credit': 0,
										'date_maturity': wo[2]['date_maturity'],
										'partner_id': wo[2]['partner_id'],
										'account_id': wo[2]['account_id'],
										'payment_id': wo[2]['payment_id'],
										}))

									payment_account = 0
									if rec.partner_type == 'customer':
										payment_account = rec.partner_id.property_account_receivable_id.id
									else:
										payment_account = wo[2]['account_id']

									new_payments.append((0,0,
										{
										'name': wo[2]['name'],
										'amount_currency': -wo[2]['amount_currency'],
										'currency_id': wo[2]['currency_id'],
										# 'debit': 0,
										# 'credit': wo[2]['debit'],
										'date_maturity': wo[2]['date_maturity'],
										'partner_id': wo[2]['partner_id'],
										'account_id': payment_account,
										'payment_id': wo[2]['payment_id'],
										}))



								# new_payments.append((0,0,{'name': 'CUST.IN/2021/0001', 'amount_currency': 0.0, 'currency_id': False, 'debit': 920.46, 'credit': 0.0, 'date_maturity': datetime.date(2021, 1, 12), 'partner_id': 14, 'account_id': 35, 'payment_id': 2}))
					# if not len(new_payments) >= 2 and self.not_register_payment:
					#   raise ValidationError("No Invoice for Reconciliation.")

					payment_rec[0]['line_ids'] = new_payments
					moves = AccountMove.create(payment_rec)
					print ("NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN")
					print (moves.line_ids)
					print ("NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN")

					# recomputing debit credit according to amount currency

					# for line in moves.line_ids:
					# for line in moves.line_ids:
					#   if not line.currency_id:
					#       continue
					#   if not line.move_id.is_invoice(include_receipts=True):
					#       line._recompute_debit_credit_from_amount_currency()
					#       continue
					#   line.update(line._get_fields_onchange_balance(
					#       balance=line.amount_currency,
					#       ))
					#   line.update(line._get_price_total_and_subtotal())
					#   print ("RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR")
					#   print (line)
					#   print ("RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR")

				else:
					moves = AccountMove.create(rec._prepare_payment_moves())
				moves.filtered(lambda move: move.journal_id.post_at != 'bank_rec').post()

				# Update the state / move before performing any reconciliation.
				move_name = self._get_move_name_transfer_separator().join(moves.mapped('name'))
				rec.write({'state': 'posted', 'move_name': move_name})

				if rec.payment_type in ('inbound', 'outbound'):
					# ==== 'inbound' / 'outbound' ====
					if rec.invoice_ids:
						print ("Overpass default reconciling")
						# (moves[0] + rec.invoice_ids).line_ids \
						#   .filtered(lambda line: not line.reconciled and line.account_id == rec.destination_account_id and not (line.account_id == line.payment_id.writeoff_account_id and line.name == line.payment_id.writeoff_label))\
						#   .reconcile()
				elif rec.payment_type == 'transfer':
					# ==== 'transfer' ====
					moves.mapped('line_ids')\
						.filtered(lambda line: line.account_id == rec.company_id.transfer_account_id)\
						.reconcile()


				# reconciling payment against invoices
				if rec.payment_type in ('inbound', 'outbound'):
					for payments in rec.invoice_tree:
						je_line = self.env['account.move.line'].search([('payment_id', 'in', rec.ids)])
						for inv_line in je_line:
							if not inv_line.reconciled:
								# if rec.payment_type == 'outbound':
								#   print ("aaaaaaaaaaaaaaaaaaa")
								#   if inv_line.amount_currency == -(payments.reconciled_amount):
								#       print ("bbbbbbbbbbbbbbbbbb")
								#       print (inv_line)
								#       test = payments.invoice_id.js_assign_outstanding_line(inv_line.id)
								#       print (test)
								# if rec.payment_type == 'inbound':
								if abs(inv_line.amount_currency) == abs(payments.reconciled_amount) and rec.journal_id.default_debit_account_id != inv_line.account_id and payments.reconcile:
									test = payments.invoice_id.js_assign_outstanding_line(inv_line.id)
								# if inv_line.amount_currency == -(payments.reconciled_amount) and rec.payment_type == "inbound" and payments.reconcile:
								#   test = payments.invoice_id.js_assign_outstanding_line(inv_line.id)
						rec.state = 'reconciled'
			else:

				if rec.state != 'draft':
					raise UserError(_("Only a draft payment can be posted."))

				if any(inv.state != 'posted' for inv in rec.invoice_ids):
					raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))

				# keep the name in case of a payment reset to draft
				if not rec.name:
					# Use the right sequence to set the name
					if rec.payment_type == 'transfer':
						sequence_code = 'account.payment.transfer'
					else:
						if rec.partner_type == 'customer':
							if rec.payment_type == 'inbound':
								sequence_code = 'account.payment.customer.invoice'
							if rec.payment_type == 'outbound':
								sequence_code = 'account.payment.customer.refund'
						if rec.partner_type == 'supplier':
							if rec.payment_type == 'inbound':
								sequence_code = 'account.payment.supplier.refund'
							if rec.payment_type == 'outbound':
								sequence_code = 'account.payment.supplier.invoice'
					rec.name = self.env['ir.sequence'].next_by_code(sequence_code, sequence_date=rec.payment_date)
					if not rec.name and rec.payment_type != 'transfer':
						raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))

				moves = AccountMove.create(rec._prepare_payment_moves())
				moves.filtered(lambda move: move.journal_id.post_at != 'bank_rec').post()

				# Update the state / move before performing any reconciliation.
				move_name = self._get_move_name_transfer_separator().join(moves.mapped('name'))
				rec.write({'state': 'posted', 'move_name': move_name})

				if rec.payment_type in ('inbound', 'outbound'):
					# ==== 'inbound' / 'outbound' ====
					if rec.invoice_ids:
						(moves[0] + rec.invoice_ids).line_ids \
							.filtered(lambda line: not line.reconciled and line.account_id == rec.destination_account_id and not (line.account_id == line.payment_id.writeoff_account_id and line.name == line.payment_id.writeoff_label))\
							.reconcile()
				elif rec.payment_type == 'transfer':
					# ==== 'transfer' ====
					moves.mapped('line_ids')\
						.filtered(lambda line: line.account_id == rec.company_id.transfer_account_id)\
						.reconcile()

		return True


	def get_total(self):
		total =0
		for x in self.invoice_tree:
			if x.reconcile ==True:
				total += x.invoice_amount
		return total

	def send_by_mail(self):
		self.ensure_one()
		if not self.invoice_tree:
			raise ValidationError("Please add invoices.")
		if self.invoice_tree:
			mail_obj = self.env['mail.mail']
			dear = 'Dear'+ ' ' +str(self.partner_id.name) + ':'
			liste = []
			for x in self.invoice_tree:
				liste.append(x)

			client_name=[]
			for client in self.partner_id:
				client_name.append(client)
			table ="""
			{%for person in client_name%}
				<span style="font-weight:bold">{{person.name}}</span>
			{%endfor%}
			<br/>
			{%for person in client_name%}
				<span style="font-weight:bold">{{person.street}}</span>
			{%endfor%}
			<br/>
			{%for person in client_name%}
				<span style="font-weight:bold">{{person.street2}}</span>
			{%endfor%}
			<br/>
			{%for person in client_name%}
				<span style="font-weight:bold">{{person.zip}}</span>
			{%endfor%}
			<br/>
			<p>
			<span>This email is to notify you that a payment for the following invoice(s) was processed.</span>
			</p>
			<br/>
			<table width="100%" style="border: 1px solid black;border-collapse: collapse;">
							<tr>
								<th style="border: 1px solid black;border-collapse: collapse;background-color: lightgray;">
									<span>Invoice No#</span>
								</th>
								<th style="border: 1px solid black;border-collapse: collapse;background-color: lightgray;">
									<span>PO#</span>
								</th>
								<th style="border: 1px solid black;border-collapse: collapse;background-color: lightgray;">
									<span> Amount</span>
								</th>
							
							</tr>

							{%for i in liste%} 
								<tr>
									<td style="border: 1px solid black;border-collapse: collapse;padding: 10px;">
									   <span> {{i.invoice_id.name}}</span>
									</td>
									<td style="border: 1px solid black;border-collapse: collapse;padding: 10px;">
									   <span> {{i.invoice_id.customer_po_no}}</span>
									</td>
									<td style="border: 1px solid black;border-collapse: collapse;padding: 10px;">
									   <span> {{i.invoice_amount}}</span>
									</td>
									
								</tr>
							{%endfor%}
							<tr>
								<td style="border: 1px solid black;border-collapse: collapse;padding: 10px;">
									<span>Total</span>
								</td>
								<td style="border: 1px solid black;border-collapse: collapse;padding: 10px;">
									<span></span>
								</td>
								<td style="border: 1px solid black;border-collapse: collapse;padding: 10px;">
								</td>
							</tr> 
						</table>
						<br/>
						<p>
						<span>Should you have any questions, please contact accounts@euroitsolution.co.uk</span>
						</p>
						<br/>
						<p>
						<span>Disclaimer: This email and any files transmitted with it are confidential and intended solely for the use of the individual or entity to whom they are addressed. If you are not the named addressee you should not disseminate, distribute, or copy this e-mail. Please notify the sender immediately by e-mail if you have received this e-mail by mistake and delete this e-mail from your system.</span>
						</p>

						"""

			template = Environment(loader=BaseLoader).from_string(table)
			template_vars = {"liste": liste ,}
			html_out = template.render(template_vars)

			test = '''<span  style="font-size:14px"><br/>
			  <br/>%s </span> 
			  <br/>%s </span>
			  <br/>%s </span>
			  <br/><br/>''' % (dear,self.communication,html_out)

			# 66666666666666666666666666666666666666666
			
			ir_model_data = self.env['ir.model.data']
			try:
				template_id = ir_model_data.get_object_reference('accounts_payment_ext', 'account_payment_email_template')[1]
				temp = self.env['mail.mail'].search([('id','=',template_id)])
				temp.body_html = test
			except ValueError:
				template_id = False

			
			try:
				compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
			except ValueError:
				compose_form_id = False
			ctx = {
			   'default_model': 'account.payment',
			   'default_res_id': self.ids[0],
			   'default_use_template': bool(template_id),
			   'default_template_id': template_id,
			   'default_composition_mode': 'comment',
			}
			return {
			   'name': _('Payment Email'),
			   'type': 'ir.actions.act_window',
			   'view_mode': 'form',
			   'res_model': 'mail.compose.message',
			   'views': [(compose_form_id, 'form')],
			   'view_id': compose_form_id,
			   'target': 'new',
			   'context': ctx,
			}
			# 66666666666666666666666666666666666666666






			
			# send_to = self.env['res.partner'].search([('id','=',self.partner_id.id)])
			# ir_model_data = self.env['ir.model.data']
			# try:
			#   compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
			# except ValueError:
			#   compose_form_id = False
			# ctx = {
			#    'default_model': 'account.payment',
			#    'default_res_id': self.ids[0],
			#    'default_use_template': bool(template),
			#    'default_template_id': template,
			#    'default_composition_mode': 'comment',
			# }
			# return {
			#    'name': _('Voucher Email'),
			#    'type': 'ir.actions.act_window',
			#    'view_mode': 'form',
			#    'res_model': 'mail.compose.message',
			#    'views': [(compose_form_id, 'form')],
			#    'view_id': compose_form_id,
			#    'target': 'new',
			#    'context': ctx,
			# }
			# mail_obj.create({
			# 'email_to': send_to.email,
			# 'subject': "Paid Invoices",
			# 'body_html':
			# '''<span  style="font-size:14px"><br/>
			#   <br/>%s </span> 
			#   <br/>%s </span>
			#   <br/>%s </span>
			#   <br/><br/>''' % (dear,self.communication,html_out)}).send(self)

	# def send_by_mail(self):
	#   self.ensure_one()
 #          ir_model_data = self.env['ir.model.data']
 #          try:
 #              template_id = \
 #              ir_model_data.get_object_reference('account_payment', 'email_template')[1]
 #          except ValueError:
 #              template_id = False
 #          try:
 #              compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
 #          except ValueError:
 #              compose_form_id = False
 #          ctx = {
	#        'default_model': 'test.email',
	#        'default_res_id': self.ids[0],
	#        'default_use_template': bool(template_id),
	#        'default_template_id': template_id,
	#        'default_composition_mode': 'comment',
	#    }
	#       return {
	#        'name': _('Compose Email'),
	#        'type': 'ir.actions.act_window',
	#        'view_mode': 'form',
	#        'res_model': 'mail.compose.message',
	#        'views': [(compose_form_id, 'form')],
	#        'view_id': compose_form_id,
	#        'target': 'new',
	#        'context': ctx,
	#       }

	# @api.onchange('partner_id', 'currency_id')
	def get_invoices(self):
		temp_list = []
		invoice_ids = []
		if self.invoice_tree:
			for x in self.invoice_tree:
				temp_list.append(x.id)
			# self.invoice_tree.unlink()
			self.invoice_tree = False
			self.invoice_tree = None
			self.inv_recs = 0
		if self.partner_id:
			if self.partner_type == "customer":
				invoice_recs = self.env['account.move'].search([('partner_id','=',self.partner_id.id),('state','=','posted'),('type','=','out_invoice'),('currency_id','=',self.currency_id.id),('invoice_payment_state','in',['not_paid','in_payment'])])
				invoice_ids = self.env['account.move'].search([('partner_id','=',self.partner_id.id),('state','=','posted'),('type','=','out_invoice'),('currency_id','=',self.currency_id.id),('invoice_payment_state','in',['not_paid','in_payment'])]).ids
			if self.partner_type == "supplier":
				invoice_recs = self.env['account.move'].search([('partner_id','=',self.partner_id.id),('state','=','posted'),('type','=','in_invoice'),('currency_id','=',self.currency_id.id),('invoice_payment_state','in',['not_paid','in_payment'])])
				invoice_ids = self.env['account.move'].search([('partner_id','=',self.partner_id.id),('state','=','posted'),('type','=','in_invoice'),('currency_id','=',self.currency_id.id),('invoice_payment_state','in',['not_paid','in_payment'])]).ids

			# if not invoice_recs:

			#     raise ValidationError("No open invoice against this partner.")
			# else:
			payment_tree_recs = []
			for index in invoice_recs:
				self.inv_recs = 1
				payment_tree_recs.append((0,0, {
					'invoice_id':index.id,
					'invoice_amount':index.amount_total,
					'invoice_residual_amount':index.amount_residual,
					'partner_id':self.partner_id.id,
					}))

			self.invoice_tree = payment_tree_recs
			self.invoice_ids = [(6, 0, invoice_ids)]

	# @api.onchange('amount',)
	def get_invoices_reg_pay(self):
		invoice_ids = []
		if self.invoice_tree:
			self.invoice_tree = False
		if self.invoice_ids:
			self.invoice_ids = False

		invoice_recs = self.env['account.move'].search([('id','in',self.env.context.get('active_ids'))])
				
		payment_tree_recs = []
		for index in invoice_recs:
			self.inv_recs = 1
			payment_tree_recs.append((0,0, {
				'reconcile':True,
				'invoice_id':index.id,
				'invoice_amount':index.amount_total,
				'invoice_residual_amount':index.amount_residual,
				'partner_id':index.partner_id.id,
				}))

			invoice_ids.append(index.id)

		print ("IIIIIIIIIIIIIII")
		print (self.env.context.get('active_ids'))
		print (self.invoice_tree)
		print (self.invoice_ids)
		print ("--------------")
		self.invoice_tree = payment_tree_recs
		self.invoice_ids = [(6, 0, invoice_ids)]
		print (self.invoice_tree)
		print (self.invoice_ids)
		print ("IIIIIIIIIIIIIII")

		return {
		"type": "ir.actions.do_nothing",
		}


	# def write(self, vals):
	#   before=self.write_date
	#   rec = super(AccPayExt, self).write(vals)
	#   after = self.write_date
	#   if before != after:
	#       if self.deleted_tree:
	#           for x in self.deleted_tree:
	#               x.unlink()
			
	#   return rec

	# @api.model
	# def create(self, vals):
	#   new_rec = super(AccPayExt, self).create(vals)
	#   if new_rec.deleted_tree:
	#       for x in new_rec.deleted_tree:
	#           x.unlink()
		
	#   return new_rec   


	# @api.onchange('amount')
	# def insert_amount(self):
	
	#   if self.amount:
	#       if self.invoice_tree:
	#           value = self.amount
	#           for j in self.invoice_tree:
	#               if value > 0:
	#                   if j.invoice_residual_amount > 0:
	#                       if value <= j.invoice_residual_amount:
	#                           j.reconciled_amount = value
	#                           value = 0
	#                       if value >= j.invoice_residual_amount:
	#                           value = value - j.invoice_residual_amount
	#                           j.reconciled_amount = j.invoice_residual_amount
	#               else:
	#                   if j.reconciled_amount > 0:
	#                       j.reconciled_amount = 0

	#           if value > 0:
	#               raise ValidationError('Amount is greater than pending amount.')

	@api.depends('invoice_ids', 'amount', 'payment_date', 'currency_id', 'payment_type')
	def _compute_payment_difference(self):
		draft_payments = self.filtered(lambda p: p.invoice_ids and p.state == 'draft')
		for pay in draft_payments:
			payment_amount = -pay.amount if pay.payment_type == 'outbound' else pay.amount

			pay.payment_difference = pay._compute_payment_amount(pay.invoice_ids, pay.currency_id, pay.journal_id, pay.payment_date) - payment_amount
		(self - draft_payments).payment_difference = 0


	@api.onchange('invoice_tree')
	def get_reconciled_amount(self):
		for x in self:
			amount_total = 0
			residual_amount_total = 0
			for index in x.invoice_tree:
				amount_total = amount_total + index.reconciled_amount
				residual_amount_total = residual_amount_total + index.invoice_residual_amount
			
			# x.amount = amount_total
			# x.payment_difference = residual_amount_total - amount_total
			x.write({
			'amount':amount_total,
			# 'payment_difference':residual_amount_total - amount_total,
			})

		# if self.amount > 0:
		#   temp_amount = self.amount
		#   for index in self.invoice_tree:

		#       if temp_amount > 0:
		#           if temp_amount < index.invoice_residual_amount:
		#               index.reconciled_amount = temp_amount
		#               temp_amount = 0
		#           if temp_amount > index.invoice_residual_amount:
		#               index.reconciled_amount = index.invoice_residual_amount
		#               temp_amount -= index.invoice_residual_amount
		#           if temp_amount == index.invoice_residual_amount:
		#               index.reconciled_amount = temp_amount
		#               temp_amount = 0
		# else:
		#   for index in self.invoice_tree:
		#       index.reconciled_amount = 0


	def reconcile_invoices(self):
		# invoice_recs = self.env['account.move'].search([('number','=',self.communication)])
		invoice_recs = self.env['account.move'].browse(self._context.get('active_id'))
		if invoice_recs:
			create_payment_lines = self.env['invoice.payment.tree'].create({
					'date':self.payment_date,
					'amount':self.amount,
					'invoice_id':invoice_recs.id,
					'payment_id':self.id,
					})

		if self.invoice_tree:
			for inv in self.invoice_tree:
				create_payment_lines = self.env['invoice.payment.tree'].create({
					'date':self.payment_date,
					'amount':inv.reconciled_amount,
					'invoice_id':inv.invoice_id.id,
					'payment_id':self.id,
					})

	def create_journal_entry_form(self):
		bank_charges = 0
		if self.invoice_tree:
			for bank in self.invoice_tree:
				bank_charges = bank_charges + bank.bank_charges

		if bank_charges > 0:

			if not self.bank_acc_id:
				raise ValidationError('Please set Bank Charges Account for Bank Charges.')

			journal_entries = self.env['account.move']
			journal_entries_lines = self.env['account.move.line']

			if not self.journal_entry_id:   
				create_journal_entry = journal_entries.create({
						'journal_id': self.journal_id.id,
						'date':self.payment_date,
						'ref' : self.name,                        
						})

				self.journal_entry_id = create_journal_entry.id

	def generate_entry_lines(self):

		bank_charges = 0
		if self.invoice_tree:
			for bank in self.invoice_tree:
				bank_charges = bank_charges + bank.bank_charges

		if bank_charges > 0:

			create_debit = self.create_entry_lines(self.bank_acc_id.id,bank_charges,0,self.journal_entry_id.id)
			create_credit = self.create_entry_lines(self.journal_id.default_debit_account_id.id,0,bank_charges,self.journal_entry_id.id)


	def create_entry_lines(self,account,debit,credit,entry_id):
		self.env['account.move.line'].create({
				'account_id':account,
				'partner_id':self.partner_id.id,
				'name':self.name,
				'debit':debit,
				'credit':credit,
				'move_id':entry_id,
				})
	
	@api.onchange('partner_id')
	def get_vendor_currency(self):
		# if self.payment_type == 'outbound' and self.partner_id:
		if self.partner_id:
			if self.partner_id.vendor_currency:
				self.currency_id = self.partner_id.vendor_currency.id

	# def post(self):
	#   rec = super(AccPayExt, self).post()
	#   invoices_list = []
	#   for index in self.invoice_tree:
	#       if index.reconcile:
	#           invoices_list.append(index.invoice_id.id)
	#   self.invoice_ids = [(6,0,invoices_list)]
	#   self.reconcile_invoices()
	#   if self.journal_id.type == "bank":
	#       self.create_journal_entry_form()
	#       self.generate_entry_lines()
	#       self.journal_entry_id.post()
	#   # self.invoice_lines = [(6,0,inv_lines_list)]
	#   return rec

	def unlink_payment(self):

		single_move = 0
		if self.move_line_ids:
			line_move = self.move_line_ids[0]
			single_move = line_move.move_id.id

		partials = self.env['account.partial.reconcile'].search(['|',('credit_move_id.move_id.id','=',single_move),('debit_move_id.move_id.id','=',single_move)])
		if partials:
			for par in partials:
				par_value = par.id
				self.env.cr.execute("DELETE from account_partial_reconcile WHERE id = "+str(par_value)+" ")

		value_id = single_move
		self.env.cr.execute("DELETE from account_move WHERE id = "+str(value_id)+" ")

		value = self.id
		self.env.cr.execute("DELETE from account_payment WHERE id = "+str(value)+" ")


		self.env.cr.execute("DELETE from invoice_payment_tree WHERE invoice_id = "+str(value)+" ")

	# @api.onchange('invoice_tree')
	# def set_reconcile(self):
	#   for inv in self.invoice_tree:
	#       if inv.reconcile:
	#           inv.reconciled_amount = inv.invoice_residual_amount
	#       else:
	#           inv.reconciled_amount = 0 
		
class PaymentInvoiceTree(models.Model):
	_name = 'payment.invoice.tree'
	_description = 'This tree will get all invoices against partner'

	invoice_id = fields.Many2one('account.move', string="Invoice")
	# partner_id = fields.Integer(string="Partner", related="tree_link.partner_id")
	partner_id = fields.Integer(string="Partner")
	invoice_amount = fields.Float(string="Invoice Amount")
	invoice_residual_amount = fields.Float(string="Invoice Residual Amount")
	reconciled_amount = fields.Float(string="Reconciled Amount")
	bank_charges = fields.Float(string="Bank Charges")
	reconcile = fields.Boolean(string="Reconciled")

	tree_link = fields.Many2one('account.payment', ondelete='cascade')

	@api.onchange('invoice_id')
	def get_domain(self):
		self.partner_id = self.tree_link.partner_id.id

	# @api.onchange('reconcile')
	# def set_reconcile(self):
	#   if self.reconcile:
	#       self.reconciled_amount = self.invoice_residual_amount
	#   else:
	#       self.reconciled_amount = 0
	@api.onchange('reconcile')
	def set_reconcile_value(self):
		if self.reconcile:
			self.reconciled_amount = self.invoice_residual_amount
		else:
			self.reconciled_amount = 0 

class InvoicePaymentTree(models.Model):

	_name = 'invoice.payment.tree'
	
	date=fields.Date('Date')
	amount =fields.Float('Amount')
	payment_id = fields.Many2one('account.payment', string = "Payment Id")
	invoice_id=fields.Many2one('account.move')

class InvoicePaymentExtension(models.Model):
	_inherit = 'account.move'
	payments    = fields.One2many('invoice.payment.tree','invoice_id')
	
	@api.depends(
		'state', 'currency_id', 'invoice_line_ids.price_subtotal',
		'move_id.line_ids.amount_residual',
		'move_id.line_ids.currency_id','payments','move_id.ref')
	def _compute_residual(self):
		residual = 0.0
		residual_company_signed = 0.0
		# sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
		# for line in self.sudo().move_id.line_ids:
		#   if line.account_id.internal_type in ('receivable', 'payable'):
		#       residual_company_signed += line.amount_residual
		#       if line.currency_id == self.currency_id:
		#           residual += line.amount_residual_currency if line.currency_id else line.amount_residual
		#       else:
		#           from_currency = (line.currency_id and line.currency_id.with_context(date=line.date)) or line.company_id.currency_id.with_context(date=line.date)
		#           residual += from_currency.compute(line.amount_residual, self.currency_id)
		total_payments = 0
		for lines in self.payments:
			total_payments = total_payments + lines.amount 
		self.residual_company_signed = self.amount_total - total_payments
		self.amount_residual_signed = self.amount_total - total_payments
		self.amount_residual = self.amount_total - total_payments
		# digits_rounding_precision = self.currency_id.rounding
		# if float_is_zero(self.residual, precision_rounding=digits_rounding_precision):
		if self.amount_residual == 0:
			self.has_reconciled_entries = True
		else:
			self.has_reconciled_entries = False


	def unlink_invoice(self):


		# partials = self.env['account.partial.reconcile'].search([])
		# for x in partials:
		#   print x.credit_move_id.move_id.id
		#   print x.debit_move_id.move_id.id
		single_move = 0
		if self.move_id:
			single_move = self.move_id.id

		partials = self.env['account.partial.reconcile'].search(['|',('credit_move_id.move_id.id','=',single_move),('debit_move_id.move_id.id','=',single_move)])
		if partials:
			for par in partials:
				par_value = par.id
				self.env.cr.execute("DELETE from account_partial_reconcile WHERE id = "+str(par_value)+" ")

		value = self.id
		self.env.cr.execute("DELETE from account_invoice WHERE id = "+str(value)+" ")

		self.env.cr.execute("DELETE from payment_invoice_tree WHERE invoice_id = "+str(value)+" ")

		value_id = single_move
		self.env.cr.execute("DELETE from account_move WHERE id = "+str(value_id)+" ")

		
		# self.action_invoice_cancel()
		# self.unlink()

	def invoice_print(self):
		""" Print the invoice and mark it as sent, so that we can see more
			easily the next step of the workflow
		"""
		self.ensure_one()
		self.sent = True
		return self.env['report'].get_action(self, 'logistic_vision.logistic_invoice')


class AccountMoveRemoveValidation(models.Model):
	_inherit = "account.move"
	def assert_balanced(self):
		if not self.ids:
						return True
		prec = self.env['decimal.precision'].precision_get('Account')

		self._cr.execute("""\
						SELECT      move_id
						FROM        account_move_line
						WHERE       move_id in %s
						GROUP BY    move_id
						HAVING      abs(sum(debit) - sum(credit)) > %s
						""", (tuple(self.ids), 10 ** (-max(5, prec))))
		
		return True


class AccMoveLineTestExt(models.Model):
	_inherit='account.move.line'




	# copying below function for debugging
	def reconcile(self, writeoff_acc_id=False, writeoff_journal_id=False):
		# Empty self can happen if the user tries to reconcile entries which are already reconciled.
		# The calling method might have filtered out reconciled lines.
		if not self:
			return

		# List unpaid invoices
		not_paid_invoices = self.mapped('move_id').filtered(
			# lambda m: m.is_invoice(include_receipts=True) and m.invoice_payment_state not in ('paid', 'in_payment')
			lambda m: m.is_invoice(include_receipts=True) and m.invoice_payment_state not in ('paid')
		)

		reconciled_lines = self.filtered(lambda aml: float_is_zero(aml.balance, precision_rounding=aml.move_id.company_id.currency_id.rounding) and aml.reconciled)
		(self - reconciled_lines)._check_reconcile_validity()
		#reconcile everything that can be
		remaining_moves = self.auto_reconcile_lines()

		writeoff_to_reconcile = self.env['account.move.line']
		#if writeoff_acc_id specified, then create write-off move with value the remaining amount from move in self
		if writeoff_acc_id and writeoff_journal_id and remaining_moves:
			all_aml_share_same_currency = all([x.currency_id == self[0].currency_id for x in self])
			writeoff_vals = {
				'account_id': writeoff_acc_id.id,
				'journal_id': writeoff_journal_id.id
			}
			if not all_aml_share_same_currency:
				writeoff_vals['amount_currency'] = False
			writeoff_to_reconcile = remaining_moves._create_writeoff([writeoff_vals])
			#add writeoff line to reconcile algorithm and finish the reconciliation
			remaining_moves = (remaining_moves + writeoff_to_reconcile).auto_reconcile_lines()
		# Check if reconciliation is total or needs an exchange rate entry to be created
		(self + writeoff_to_reconcile).check_full_reconcile()

		# Trigger action for paid invoices
		not_paid_invoices.filtered(
			lambda m: m.invoice_payment_state in ('paid', 'in_payment')
		).action_invoice_paid()

		return True
