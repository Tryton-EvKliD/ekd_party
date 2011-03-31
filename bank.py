# -*- encoding: utf-8 -*-. 
#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
'Address'
from trytond.model import ModelView, ModelSQL, fields
from trytond.transaction import Transaction
from trytond.pyson import If, Greater, Eval, Not, Bool, Eval

STATES = {
    'readonly': Not(Bool("active")),
}

class Bank(ModelSQL, ModelView):
    "Bank"
    _name = 'ekd.party.bank'
    _description = __doc__

    name = fields.Char('Name', size=None, states=STATES)
    shortname = fields.Char('ShortName', size=None, states=STATES)
    city = fields.Char('City', size=None, states=STATES)
    zip = fields.Char('Zip', size=6, states=STATES)
    phone = fields.Char('Phones', size=None, states=STATES)
    address = fields.Char('Address', size=None, states=STATES)
    rkc = fields.Char('RKC', size=9, states=STATES)
    okpo = fields.Char('OKPO', size=8, states=STATES)
    corr_account = fields.Char('Corr Account', size=None, states=STATES)
    bic = fields.Char('BIC', size=9, states=STATES)
    start_date = fields.Date('Date Start')
    change_date = fields.Date('Date Change')
    end_date = fields.Date('Date End')
    active = fields.Boolean('Active')
    full_name = fields.Function(fields.Text("Full Name"), 'get_full_name')

    def __init__(self):
        super(Bank, self).__init__()

        self._error_messages.update({
            'write_party': 'You can not modify the party of an address!',
            })

    def default_active(self):
        return True


Bank()
