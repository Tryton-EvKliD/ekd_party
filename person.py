# -*- coding: utf-8 -*-. 
#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
'Address'
from trytond.model import ModelView, ModelSQL, fields
from strings_ru import *
from trytond.pyson import Not, Bool, Eval

STATES = {
    'readonly': Not(Bool("active")),
}

class Person(ModelSQL, ModelView):
    'Person'
    _name = 'ekd.party.person'
    _description = __doc__
    _inherits = {'party.party': 'party'}

#    party = fields.Many2One('party.party', 'Party', required=True)
#    birthday = fields.Date('Birthday')

    def default_individual(self):
        return True

Person()
