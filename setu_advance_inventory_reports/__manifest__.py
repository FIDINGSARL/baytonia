# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Advance Inventory Reports',
    'version' : '11.0',
    'price' : 299,
    'currency'  :'EUR',
    'category': 'stock',
    'summary': """	
        Advance Inventory Reports / Inventory Analysis Reports
        - Inventory Turnover Analysis Report / Inventory Turnover Ratio
        - Inventory FSN Analysis Report / non moving report
        - Inventory XYZ Analysis Report
        - Inventory FSN with XYZ Analysis Report / FSN-XYZ Analysis / FSN XYZ Analysis
        - Inventory Age Report / stock ageing / Inventory ageing / stock age
        - Inventory Age Breakdown Report
        - Inventory Overtsock Report / Excess Inventory Report  
        - Stock Movement Report / Stock Rotation Report 
        - Inventory Out Of Stock Report / inventory coverage report / outofstock report
        Advanced Inventory Reports / All in one inventory reports / all in one reports
		""",
    'website' : 'https://www.setuconsulting.com' ,
    'support' : 'support@setuconsulting.com',
    'description' : """
        Advance Inventory Reports / Inventory Analysis Reports
        - Inventory Turnover Analysis Report / Inventory Turnover Ratio
        - Inventory FSN Analysis Report / non moving report
        - Inventory XYZ Analysis Report
        - Inventory FSN with XYZ Analysis Report / FSN-XYZ Analysis / FSN XYZ Analysis
        - Inventory Age Report / stock ageing / Inventory ageing / stock age
        - Inventory Age Breakdown Report
        - Inventory Overtsock Report / Excess Inventory Report  
        - Stock Movement Report / Stock Rotation Report 
        - Inventory Out Of Stock Report / inventory coverage report / outofstock report
        Advanced Inventory Reports / All in one inventory reports / all in one reports
    """,
    'author' : 'Setu Consulting',
    'license' : 'OPL-1',
    'sequence': 25,
    'depends' : ['sale_stock'],
    'images': ['static/description/banner.gif'],
    'data' : [
        'views/setu_stock_movement_report.xml',
        'views/setu_inventory_turnover_analysis_report.xml',
        'views/setu_inventory_fsn_analysis_report.xml',
        'views/setu_inventory_xyz_analysis_report.xml',
        'views/setu_inventory_fsn_xyz_analysis_report.xml',
        'views/setu_inventory_overstock_report.xml',
        'views/setu_inventory_outofstock_report.xml',
        'views/setu_inventory_age_report.xml',
        'views/setu_inventory_age_breakdown_report.xml',
    ],
    'application': True,
    'pre_init_hook': 'pre_init',
}