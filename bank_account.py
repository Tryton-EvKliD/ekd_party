# -*- coding: utf-8 -*-
#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
'Address'
from trytond.model import ModelView, ModelSQL, fields
from trytond.transaction import Transaction
from trytond.pyson import If, Greater, Eval, Not, Bool, Eval

STATES = {
    'readonly': Not(Bool("active")),
}

class BankAccount(ModelSQL, ModelView):
    "Bank"
    _name = 'ekd.party.bank_account'
    _description = __doc__

    party = fields.Many2One('party.party', 'Party', required=True,
            ondelete='CASCADE', select=1,  states={
                'readonly': If(Not(Bool(Eval('active'))),
                            True, Greater(Eval('active_id', 0), 0)),
            })
    type_account = fields.Char('Type Account', size=None, states=STATES)
    name = fields.Char('Bank Name', size=None, states=STATES)
    address = fields.Char('Bank Street', size=None, states=STATES)
    account = fields.Char('Account', size=None, states=STATES)
    corr_account = fields.Char('Corr Account', size=None, states=STATES)
    bic = fields.Char('BIC', size=None, states=STATES, on_change=['bic'])
    bank = fields.Many2One('ekd.party.bank', 'Bank')
    currency = fields.Many2One('currency.currency', 'Currency')
    currency_digits = fields.Function(fields.Integer('Currency Digits', on_change_with=['currency']), 'get_currency_digits')
    end_date = fields.Date('Date End')
    active = fields.Boolean('Active')
    full_name = fields.Function(fields.Text("Full Name"), 'get_full_name')

    def __init__(self):
        super(BankAccount, self).__init__()
        self._order.insert(0, ('account', 'ASC'))
        self._order.insert(1, ('bic', 'ASC'))
        self._error_messages.update({
            'write_party': 'You can not modify the party of an address!',
            })

    def default_active(self):
        return True

    def default_currency_digits(self):
        return 2

    def get_currency_digits(self, ids, name):
        assert name in ('currency_digits'), 'Invalid name %s' % (name)
        res={}.fromkeys(ids, 2)
        for document in self.browse( ids):
            if document.currency:
                res[document.id] = document.currency.digits
        return res

    def get_full_name(self,  ids, name):
        if not ids:
            return {}
        res = {}
        for bank in self.browse( ids):
            res[bank.id] = ", ".join(x for x in [bank.account, bank.name,
                 bank.bic] if x)
        return res

    def get_rec_name(self,  ids, name):
        if not ids:
            return {}
        res = {}
        for bank in self.browse( ids):
            res[bank.id] = ", ".join(x for x in [bank.account,
                 bank.name, bank.bic] if x)
        return res

    def search_rec_name(self,  name, args):
        args2 = []
        i = 0
        while i < len(args):
            ids = self.search( ['OR',
                ('account', args[i][1], args[i][2]),
                ('bic', args[i][1], args[i][2]),
                ('name', args[i][1], args[i][2]),
                ])
            if ids:
                args2.append(('id', 'in', ids))
            else:
                args2.append(('party', args[i][1], args[i][2]))
            i += 1
        return args2

    def on_change_bic(self, vals):
        if vals.get('bic', False):
            bank_obj = self.pool.get('ekd.party.bank')
            bank_id = bank_obj.search([('bic','=',vals.get('bic'))])
            for bank in bank_obj.browse(bank_id):
                #if bank.active:
                return {
                        'corr_account': bank.corr_account,
                        'name': bank.name,
                        'address': bank.address,
                        'bank': bank.id,
                        }

BankAccount()
