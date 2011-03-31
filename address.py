# -*- encoding: utf-8 -*-. 
#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
'Address'
from trytond.model import ModelView, ModelSQL, fields
from trytond.pyson import If, Greater, Eval, Not, Bool, Eval

STATES = {
    'readonly': Not(Bool("active")),
}

class Address(ModelSQL, ModelView):
    "Address"
    _name = 'party.address'
    _description = __doc__

    type_address = fields.Selection('type_address_get', 'Type Address')
    area_residence = fields.Many2One('country.subdivision', 'Area of residence', domain=[('parent', '=', Eval("subdivision"))],
            context={'country': Eval("country"), 'parent': Eval("subdivision")})

    date_end = fields.Date('Date End')

    def get_rec_name(self,  ids, name):
        if not ids:
            return {}
        res = {}
        for address in self.browse( ids):
            res[address.id] = ", ".join(x for x in [address.name,
                address.party.rec_name, address.zip, address.city, address.street, address.streetbis] if x)
        return res

    def type_address_get(self):
        dictions_obj = self.pool.get('ir.dictions')
        res = []
        diction_ids = dictions_obj.search([
                ('model', '=', 'party.address'),
                ('pole', '=', 'type_address'),
                ])
        for diction in dictions_obj.browse(diction_ids):
            res.append([diction.key, diction.value])
        return res

Address()
