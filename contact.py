# -*- coding: utf-8 -*-
#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
'Address'
from trytond.model import ModelView, ModelSQL, fields
from trytond.pyson import Not, Bool, Eval

STATES = {
    'readonly': Not(Bool(Eval('active'))),
}

class JobFunction(ModelSQL, ModelView):
    'Contact'
    _name = 'ekd.party.job_function'
    _description = __doc__

    name = fields.Char('Name', size=None, required=True)
    shortname = fields.Char('Short Name', size=32, required=True)

JobFunction()

class Contact(ModelSQL, ModelView):
    'Contact'
    _name = 'ekd.party.contact'
    _description = __doc__
    _rec_name = 'contact'

    party = fields.Many2One('party.party', 'Party', required=True)
    type_contact = fields.Selection([
            ('general','Chief Officer'),
            ('accountant','Chief Accountant'),
            ('manager','Manager'),
            ('employee','Employee'),
            ],'Type Contact Person')
    job_function = fields.Many2One('ekd.party.job_function', 'Job Function')
    function = fields.Char('Job Function', size=None )
    contact = fields.Many2One('party.party', 'Contact Person', required=True)
    date_end = fields.Date('Date End')
#    name = fields.Function('get_mechanism', arg='name', type='char',
#                string='Name')
    phone = fields.Function(fields.Char('Phone'), 'get_mechanism')
    mobile = fields.Function(fields.Char('Mobile'), 'get_mechanism')
    fax = fields.Function(fields.Char('Fax'), 'get_mechanism')
    email = fields.Function(fields.Char('E-Mail'), 'get_mechanism')
    website = fields.Function(fields.Char('Website'), 'get_mechanism')
    note = fields.Text('Notes')
    active = fields.Boolean('Active')

    def default_active(self):
        return True

    def get_mechanism(self, ids, name):
        if not ids:
            return []
        res = {}
        for contact in self.browse(ids):
            res[contact.id] = ''
            for mechanism in contact.contact.contact_mechanisms:
                if mechanism.type == name:
                    res[contact.id] = mechanism.value
                    break
        return res

    def get_rec_name(self, ids, name):
        if not ids:
            return []
        res = {}
        for contact in self.browse(ids):
            res[contact.id] = contact.contact.shortname
        return res

Contact()
