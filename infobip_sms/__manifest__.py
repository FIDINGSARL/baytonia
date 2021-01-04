# -*- coding: utf-8 -*-
##############################################################################
#
#    Sahil Navadiya
#    Copyright (C) 2018-TODAY (<navadiyasahil@gmail.com>).
#
##############################################################################
{
    "name":  "Infobip SMS",
    "summary":  "Module for sending SMS through Infobip",
    #"description": """Infobip SMS : 
    #    1> https://github.com/infobip/infobip-api-python-client
    #    2> Command to install : pip install infobip-api-python-client
    #    3> https://pypi.org/project/infobip-api-python-client/""",
    "version":  "1.1.0",
    "sequence":  1,
    "author":  "Sahil Navadiya <navadiyasahil@gmail.com>",
    "website":  "http://thefuturelens.com/",
    "depends":  ['base'],
    #"external_dependencies": {'python': ['infobip']},
    "data":  [
        'security/ir.model.access.csv',
        'infobip_sms_view.xml',
        'infobip_sms_history_view.xml',
        ],
    "images":  [],
    "application":  True,
    "installable":  True,
    "auto_install":  False,
}
