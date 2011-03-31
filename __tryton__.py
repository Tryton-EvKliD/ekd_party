# -*- coding: utf-8 -*-
#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
{
    'name' : 'Party Russia',
    'name_ru_RU': 'Расширение организаций для России',
    'version' : '1.8.0',
    'author' : 'B2CK, Dmitry Klimanov',
    'email': 'k-dmitry2@narod.ru',
    'website': 'http://www.tryton.org/',
    'description': 'Extentions field for Russian',
    'description_ru_RU': 'Добавление полей в организации, банковских счетов, код статистической отчетности, регистрационные документы',
    'depends' : [
        'ir',
        'res',
        'ekd_system',
        'country',
        'currency',
        'party',
    ],
    'xml' : [
        'xml/ekd_system.xml',
        'xml/party.xml',
        'xml/person.xml',
        'xml/bank_account.xml',
        'xml/bank.xml',
        'xml/contact.xml',
        'xml/legal_form.xml',
        'xml/jobfunction.xml',
    ],
    'translation': [
        'ru_RU.csv',
        'de_DE.csv',
        'es_CO.csv',
        'es_ES.csv',
        'fr_FR.csv',
    ],
}
