# -*- coding: utf-8 -*-
#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
from trytond.model import ModelStorage, ModelView, ModelSQL, fields
from trytond.wizard import Wizard
from trytond.pyson import Not, Bool, Eval
from trytond.transaction import Transaction
import datetime
import logging
from images import female, male, logotype
def check_vat_ru(vat):
    '''
        Check Russia VAT number.
    '''
    if vat is NoneType:
        return True

    if len(vat) != 10 and len(vat) != 12:
        return False

    try:
        int(vat)
    except ValueError:
        return False
    if len(vat) == 10:
        check_sum = 2 * int(vat[0]) + 4 * int(vat[1]) + 10 * int(vat[2]) + \
                    3 * int(vat[3]) + 5 * int(vat[4]) + 9 * int(vat[5]) + \
                    4 * int(vat[6]) + 6 * int(vat[7]) + 8 * int(vat[8])
        check = check_sum % 11
        if check % 10 != int(vat[9]):
            return False

    else:
        check_sum1 = 7 * int(vat[0]) + 2 * int(vat[1]) + 4 * int(vat[2]) + \
                    10 * int(vat[3]) + 3 * int(vat[4]) + 5 * int(vat[5]) + \
                     9 * int(vat[6]) + 4 * int(vat[7]) + 6 * int(vat[8]) + \
                     8 * int(vat[9])
        check = check_sum1 % 11
        if check > 9:
            check = check % 10
        if check != int(vat[10]):
            return False

        check_sum2 = 3 * int(vat[0]) + 7 * int(vat[1]) + 2 * int(vat[2]) + \
                     4 * int(vat[3]) + 10 * int(vat[4]) + 3 * int(vat[5]) + \
                     5 * int(vat[6]) + 9 * int(vat[7]) + 4 * int(vat[8]) + \
                     6 * int(vat[9]) + 8 * int(vat[10])
        check = check_sum2 % 11
        if check > 9:
            check = check % 10
        if check != int(vat[11]):
            return False

    return True

HAS_VATNUMBER = False
VAT_COUNTRIES = [('', '')]

try:
    import vatnumber
    HAS_VATNUMBER = True
    for country in vatnumber.countries():
        VAT_COUNTRIES.append((country, country))
except ImportError:
    logging.getLogger('party').warning(
            'Unable to import vatnumber. VAT number validation disabled.')

#VAT_COUNTRIES.append(('RU', 'RU'))

STATES = {
    'readonly': Not(Bool(Eval('active'))),
}

class PartyLegalForm(ModelSQL, ModelView):
    "Party Legal Form"
    _name = 'ekd.party.legal'
    _description ='Legal form of Partner '

    name = fields.Char('Full Name', size=200)
    shortname = fields.Char('Shortname', size=64)
    date_end = fields.Date('End of document')
    active = fields.Boolean('Active')

    def default_active(self):
        return True

PartyLegalForm()

class Party(ModelSQL, ModelView):
    "Party"
    _description = __doc__
    _name = "party.party"
    _rec_name = 'shortname'

    name = fields.Char('Full Name', on_change=['name', 'shortname', 'individual'],
                states=STATES, required=True)
    shortname = fields.Char('Short Name', on_change_with=[
                'name', 'shortname', 'individual'
                ], required=True, states=STATES)
    code = fields.Char('Code', required=True, select=1,
                readonly=True, order_field="%(table)s.code_length %(order)s, "\
                    "%(table)s.code %(order)s")
    code_length = fields.Integer('Code Length', select=1, readonly=True)
    lang = fields.Many2One("ir.lang", 'Language', states=STATES)
    legal_form = fields.Many2One("ekd.party.legal", 'Legal Form', states=STATES)
    parent_party = fields.Many2One('party.party','Parent', select=1)
    childs_party = fields.One2Many('party.party', 'parent', string='Children Party')
    photo = fields.Function(fields.Binary('Person Photo or Logo'), 'get_photo' , setter='set_photo')
    photo_file = fields.Binary('Person Photo or Logo')
    vat_number = fields.Char('VAT Number', help="Value Added Tax number",
            states=STATES)
    vat_country = fields.Selection(VAT_COUNTRIES, 'VAT Country', states=STATES,
        help="Setting VAT country will enable validation of the VAT number.")
    vat_code = fields.Function( fields.Char("VAT Code",
            on_change_with=['vat_number', 'vat_country']), 'get_vat_code', 
            searcher='search_vat_code')
    banks = fields.One2Many('ekd.party.bank_account', 'party', 'Accounts in Banks', states=STATES)
    bank_name = fields.Function(fields.Char("Bank name"), 'get_bank')
    bank_bic = fields.Function(fields.Char("Bank BIC"), 'get_bank')
    bank_corr_account = fields.Function(fields.Char("Bank Corr account"), 'get_bank')
    bank_account = fields.Function(fields.Char("Party account"), 'get_bank')
    addresses = fields.One2Many('party.address', 'party', 'Addresses', states=STATES)
    contact_mechanisms = fields.One2Many('party.contact_mechanism', 'party', 'Contact Mechanisms', states=STATES)
    contacts = fields.One2Many('ekd.party.contact', 'party',
            'Contact', states={'invisible': Bool(Eval("individual")),})
    categories = fields.Many2Many('party.party-party.category', 'party', 'category', 'Categories', states=STATES)
    active = fields.Boolean('Active', select=1)
    full_name = fields.Function(fields.Char("Full Name"), 'get_full_name')
    phone = fields.Function(fields.Char('Phone'), 'get_mechanism')
    mobile = fields.Function(fields.Char('Mobile'), 'get_mechanism')
    fax = fields.Function(fields.Char('Fax'), 'get_mechanism')
    email = fields.Function(fields.Char('E-Mail'), 'get_mechanism')
    website = fields.Function(fields.Char('Website'), 'get_mechanism')
# Идентификационный налоговый номер
#    inn = fields.Char('VAT Identification Number')
# Код причины постановки 
    kpp_number = fields.Char('Reason code setting',
            states={'invisible': Bool(Eval("individual")),})
# Общий государственный регистрационный номер 
    ogrn_number = fields.Char('OGRN registration number',
            states={'invisible': Bool(Eval("individual")),})
# Общий государственный регистрационный номер 
    okpo_number = fields.Char('OKPO registration number',
            states={'invisible': Bool(Eval("individual")),})

# Общий государственный регистрационный номер 
    okved_number = fields.Char('OKVED registration number',
            states={'invisible': Bool(Eval("individual")),})

    individual = fields.Boolean('Individual', help="Check this box if the party is a Individual.")
    customer = fields.Boolean('Customer', help="Check this box if the party is a Cusmomer.")
    supplier = fields.Boolean('Supplier', help="Check this box if the party is a Supplier.")
    document = fields.One2Many('ekd.party.document', 'party', 'Legal Documents')
    document_active = fields.Function(fields.Char('Legal Documents'), 'get_document')
    birthday = fields.Date('Birthday', states={'invisible': Not(Bool(Eval("individual"))),})
    note = fields.Text('Notes')
    id_1c = fields.Char("ID import from 1C", size=None, select=1)
    deleted = fields.Boolean('Deleted')

    def create(self, vals):
        new_id = super(Party, self).create(vals)
        if vals.get('customer', False):
            customer_obj = self.pool.get('party.customer')
            customer_obj.create({
                                'party': new_id,
                                })
        if vals.get('supplier', False):
            supplier_obj = self.pool.get('party.supplier')
            supplier_obj.create({
                                'party': new_id,
                                })
        return new_id

    def write(self, ids, vals):
        if vals.get('customer'):
            customer_obj = self.pool.get('party.customer')
            if not customer_obj.search([('party','=', ids[0])]):
                customer_obj.create({
                                'party': ids[0],
                                })
        else:
            if vals.get('customer', True):
                pass
            else:
                customer_obj = self.pool.get('party.customer')
                if customer_obj.search([('party','=', ids[0])]):
                    customer_obj.delete(ids)

        if vals.get('supplier'):
            supplier_obj = self.pool.get('party.supplier')
            if not supplier_obj.search([('party','=', ids[0])]):
                supplier_obj.create({
                                'party': ids[0],
                                })
        else:
            if vals.get('supplier', True):
                pass
            else:
                supplier_obj = self.pool.get('party.supplier')
                if supplier_obj.search([('party','=', ids[0])]):
                    supplier_obj.delete(ids)

        return super(Party, self).write(ids, vals)

    def default_active(self):
        return True

    def default_categories(self):
        return Transaction().context.get('categories', [])

#    def default_photo_file(self):
#        return logotype

    def default_individual(self):
        return Transaction().context.get('individual', False)

#    def default_vat_country(self):
#        return 'RU'

    def default_photo(self):
        return logotype

    def get_full_name(self, ids, name):
        if not ids:
            return []
        res = {}
        for party in self.browse(ids):
            res[party.id] = party.name
        return res

    def get_document(self, ids, names):
        if not ids:
            return []
        res = {}
        for party in self.browse(ids):
            for name in names:
                res.setdefault(name, {}.fromkeys(ids, False))
                for document in party.document:
                    if document.active:
                        res[name][party.id] = document.rec_name
                        break
        return res

    def get_bank(self, ids, names):
        if not ids:
            return []
        res = {}
        for name in names:
            res.setdefault(name, {}.fromkeys(ids, False))
        for party in self.browse(ids):
            for bank in party.banks:
                if bank.active:
                    for name in names:
                        if name == 'bank_name':
                            res[name][party.id] = bank.name
                        elif name == 'bank_account':
                            res[name][party.id] = bank.account
                        if name == 'bank_corr_account':
                            res[name][party.id] = bank.corr_account
                        if name == 'bank_bic':
                            res[name][party.id] = bank.bic
                    break
        return res

    def get_rec_name(self, ids, name):
        if not ids:
            return []
        res = {}
        for party in self.browse(ids):
            if party.shortname:
                res[party.id] = party.shortname
            else:
                res[party.id] = party.name
        return res

    def get_photo(self, ids, name):
        if not ids:
            return []
        res = {}.fromkeys(ids, logotype)
        for party in self.browse(ids):
            if party.photo_file:
                res[party.id] = party.photo_file
            elif party.individual:
                res[party.id] = female
#            elif party.individual:
#                res[party.id] = male
#            else:
#                res[party.id] = logotype
        return res

    def set_photo(self, ids, name, values):
        if values and name == 'photo' and\
            'iVBORw0KGgoAAAANSUhEUgAAASwAAAEdCAYAAAC2' != values[0:40] and\
            'iVBORw0KGgoAAAANSUhEUgAAASwAAADhCAYAAABy' != values[0:40] and\
            'iVBORw0KGgoAAAANSUhEUgAAASwAAAEsCAYAAAB5' != values[0:40]:
            #raise Exception(values[0:40], values)
            self.write(ids, {'photo_file': values})
#        elif not values:
#            self.write(ids, {'photo_file': values})

    def on_change_name(self, vals):
        if vals.get('name', False):
            if vals.get('individual', False):
                s = unicode(vals.get('name'), 'utf8').lower()
                #raise Exception(s)
                return { 'name': " ".join([x[0:1].upper()+x[1:len(x)] for x in s.split()]), }
            elif not vals.get('individual', False):
                return { 'shortname': vals.get('name')}

    def on_change_with_shortname(self, vals):
        if vals.get('name', False):
            if vals.get('shortname'):
                return vals.get('shortname')
            elif vals.get('individual', False):
                s = vals.get('name').lower()
                #s = unicode(vals.get('name'), 'utf8').lower()
                name = "".join([x[0:1].upper()+x[1:len(x)]+' ' for x in s.split()])
                shortname = name.split()[0]
                if len(name.split())==1:
                    return shortname
                return "%s %s"%(shortname, "".join([name.split()[x+1][0:1].upper()+'. ' for x in range(len(name.split())-1) ]))
            else:
                return vals.get('name')

    def delete(self, ids):
        for party in self.browse(ids):
            if party.deleted:
                return super(Party, self).delete(party.id)
            else:
                return self.write(party.id, {'deleted':True})


    def copy(self, ids, default=None):
        address_obj = self.pool.get('party.address')
        int_id = False
        if isinstance(ids, (int, long)):
            int_id = True
            ids = [ids]

        if default is None:
            default = {}
        default = default.copy()
        default['code'] = False
        default['addresses'] = False
        default['document'] = False
        new_ids = []
        for party in self.browse(ids):
            new_id = super(Party, self).copy(party.id, default=default)
            address_obj.copy([x.id for x in party.addresses],
                    default={
                        'party': new_id,
                        })
            new_ids.append(new_id)

        if int_id:
            return new_ids[0]
        return new_ids

Party()

class PartySupplier(ModelSQL, ModelView):
    "Party Supplier"
    _description = __doc__
    _name = "party.supplier"
    _rec_name = 'shortname'
    _inherits = {'party.party': 'party'}

    party = fields.Many2One('party.party', 'Party', required=True)

    def create(self, vals):
        cursor = Transaction().cursor
        later = {}
        vals = vals.copy()
        for field in vals:
            if field in self._columns\
                and hasattr(self._columns[field], 'set'):
                    later[field] = vals[field]
        for field in later:
            del vals[field]
        if cursor.nextid(self._table):
            cursor.setnextid(self._table, cursor.currid(self._table))
        new_id = super(PartySupplier, self).create(vals)
        supplier = self.browse(new_id)
        new_id = supplier.party.id
        cursor.execute('UPDATE "' + self._table + '" SET id = %s '\
                        'WHERE id = %s', (supplier.party.id, supplier.id))
        ModelStorage.delete(self, supplier.id)
        self.write(new_id, later)
        res = self.browse(new_id)
        return res.id

PartySupplier()

class PartyCustomer(ModelSQL, ModelView):
    "Party Customer"
    _description = __doc__
    _name = "party.customer"
    _rec_name = 'shortname'
    _inherits = {'party.party': 'party'}

    party = fields.Many2One('party.party', 'Party', ondelete="CASCADE", required=True)

    def create(self, vals):
        cursor = Transaction().cursor
        later = {}
        vals = vals.copy()
        for field in vals:
            if field in self._columns\
                and hasattr(self._columns[field], 'set'):
                    later[field] = vals[field]
        for field in later:
            del vals[field]
        if cursor.nextid(self._table):
            cursor.setnextid(self._table, cursor.currid(self._table))
        new_id = super(PartyCustomer, self).create(vals)
        customer = self.browse(new_id)
        new_id = customer.party.id
        cursor.execute('UPDATE "' + self._table + '" SET id = %s '\
                        'WHERE id = %s', (customer.party.id, customer.id))
        ModelStorage.delete(self, customer.id)
        self.write(new_id, later)
        res = self.browse(new_id)
        return res.id

PartyCustomer()

class PartyDocumentType(ModelSQL, ModelView):
    "Party Document Type"
    _name = 'ekd.party.document.type'
    _description ='Type Document registrations of Partner '

    name = fields.Char('Name')
    shortname = fields.Char('Shortname')
    code01 = fields.Char('Code 01',size=10)
    code02 = fields.Char('Code 02',size=10)
    type_document = fields.Selection('type_document_get', 'Type Document')
    active = fields.Boolean('Valid')

    def default_active(self):
        return True

    def type_document_get(self):
        dictions_obj = self.pool.get('ir.dictions')
        res = []
        diction_ids = dictions_obj.search([
                ('model', '=', 'ekd.party.document.type'),
                ('pole', '=', 'type_document'),
                ])
        for diction in dictions_obj.browse(diction_ids):
            res.append([diction.key, diction.value])
        return res

PartyDocumentType()

class PartyDocument(ModelSQL, ModelView):
    "Person Document"
    _name = 'ekd.party.document'
    _description ='Documents of state registrations of Partner '

    party = fields.Many2One('party.party', 'Party')
    type_document = fields.Many2One('ekd.party.document.type', 'Type Document')
    full_name = fields.Char('Full Name in Document')
    name = fields.Char('Name', size=128)
    code = fields.Char('Code',size=64)
    number = fields.Char('Number',size=64)
    date_reg = fields.Date('Registered')
    date_end = fields.Date('End of document')
    active = fields.Boolean('Valid')
    issued = fields.Char('Issued',size=128)

    def default_active(self):
        return True

    def get_rec_name(self, ids, name):
        res={}

        for document in self.browse(ids):
            if document.typedoc:
                res[document.id] = document.type_document.name

            if document.number:
                res[document.id] += u', '+document.number
            else:
                DocumentNumber = u' без номера '

            if document.date_reg:
                res[document.id] += u', '+document.date_reg.strftime('%d.%m.%Y')
            else:
                DocumentDate = u' без даты '

            if document.issued:
                 res[document.id] += u', '+document.issued

        return res

PartyDocument()
