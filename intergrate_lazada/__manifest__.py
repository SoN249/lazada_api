# -*- coding: utf-8 -*-
{
    'name': "intergrate_lazada",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale',"product",'stock','sale_stock','contacts','account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_setting_lazada.xml',
        "views/s_product_lazada.xml",
        "views/s_order_lazada.xml",
        "views/s_stock_picking.xml",
        "views/s_warehouse.xml",
        "views/s_res_partner.xml",
        "views/s_product_product.xml",
        "views/ecommerce_platform.xml",
        "wizard/type_shipping_document.xml",
        "wizard/infor_customer.xml",
        "data/scheduled_sync_order.xml",
        "data/scheduled_sync_stock.xml",
        "data/scheduled_sync_package.xml",
        "data/scheduled_order_status.xml",
        "data/scheduled_refresh_token.xml",
        "data/customer_lazada_data.xml"
    ],
}
