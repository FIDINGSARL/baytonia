# -*- coding: utf-8 -*-
##############################################################################
#
#    Sahil Navadiya
#    Copyright (C) 2018-TODAY (<navadiyasahil@gmail.com>).
#
##############################################################################
{
    "name":  "SMS - Sale",
    "summary":  "Module for sending SMS when order confirm and delivery is ready",
    "version":  "1.1.0",
    "sequence":  1,
    "author":  "Sahil Navadiya <navadiyasahil@gmail.com>",
    "website":  "http://thefuturelens.com/",
    "depends":  ['sale','stock','infobip_sms','delivery'],
    "data":  [
        'security/ir.model.access.csv',
        'infobip_sms_view.xml',
        ],
    "images":  [],
    "application":  True,
    "installable":  True,
    "auto_install":  False,
}
