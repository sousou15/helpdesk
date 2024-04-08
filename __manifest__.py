# Copyright <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Helpdesk Youssef",
    "summary": "Helpdesk my first module",
    "version": "11.0.1.0.0",
    # see https://odoo-community.org/page/development-status
    "category": "Helpdesk",
    "website": "https://github.com/OCA/helpdesk",
    "author": "Youssef, Odoo Community Association (OCA)",
    # see https://odoo-community.org/page/maintainer-role for a description of the maintainer role and responsibilities
    "maintainers": ["sousou15"],
    "license": "AGPL-3",
    "application": True,
    "installable": True,
    "depends": [
        "base",
        "mail",
    ],
    "data": [
        "security/helpdesk_security.xml",
        "security/ir.model.access.csv",
        "wizards/new_ticket_from_tag_views.xml",
        "views/helpdesk_ticket_views.xml",
        "views/helpdesk_tag_views.xml",
        "views/helpdesk_action_views.xml",
        "data/helpdesk_data.xml",
        "reports/helpdesk_ticket_templates.xml"
    ],
    "demo": [
        "data/helpdesk_demo.xml",
    ]
}
