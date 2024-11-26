# -*- coding: utf-8 -*-
{
    "name": "PO Three Level Approval",
    "summary": "PO Three Level Approval",
    "description": """PO Three Level Approval""",
    "author": "Codetrade.io",
    "website": "https://www.codetrade.io/",
    "category": "Uncategorized",
    "version": "17.0.1.0.0",
    "license": "LGPL-3",
    "depends": ["base", "purchase", "mail", "stock"],
    "data": [
        "security/purchase_security.xml",
        "security/ir.model.access.csv",
        "views/inherit_purchase_order_view.xml",
        "views/inherit_res_company_view.xml",
        "wizard/refuse_reason_wizard.xml",
    ],
    
}
