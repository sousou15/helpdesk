from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta


class HelpdeskTicketState(models.Model):
    _name = "helpdesk.ticket.state"
    _description = "Helpdesk State"
    name = fields.Char()


class HelpdeskTag(models.Model):
    _name = "helpdesk.tag"
    _description = "Helpdesk Tag"

    name = fields.Char()
    ticket_ids = fields.Many2many(
        comodel_name='helpdesk.ticket',
        relation='helpdesk_ticket_tag_rel',
        column2='ticket_id',
        column1='tag_id',
        string='Tickets',)

    @api.model
    def _clean_tags_all(self):
        tags_to_delete = self.search([('ticket_ids', '=', False)])
        tags_to_delete.unlink()


class HelpdeskTicketAction(models.Model):
    _name = 'helpdesk.ticket.action'
    _description = 'Helpdesk Action'

    name = fields.Char()
    date = fields.Date()
    dedicated_time = fields.Float(
        string='Time',
    )
    ticket_id = fields.Many2one(
        comodel_name='helpdesk.ticket')


class HelpdeskTicket(models.Model):
    _name = "helpdesk.ticket"
    _description = "Helpdesk Ticket"
    # _inherit = [
    #     'mail.thread', 'mail.thread.blacklist', 'mail.activity.mixin'
    # ]
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _default_user_id(self):
        return self.env.user

    barcode = fields.Char(string="Barcode")

    name = fields.Char(
        string="Name",
        required=True)

    description = fields.Text(string="Description")

    date = fields.Date(string="Date", track_visibility='onchange' )

    state = fields.Selection(
        [('new', 'New'),
         ('assigned', 'Assigned'),
         ('progress', 'Progress'),
         ('pending', 'Pending'),
         ('done', 'Done'),
         ('cancel', 'Cancel')],
        string='State',
        default='new'
    )

    state_id = fields.Many2one(
        comodel_name='helpdesk.ticket.state',
        string='State')

    dedicated_time = fields.Float(
        string="Time",
        compute="_compute_dedicated_time",
        inverse="_set_dedicated_time",
        search="_search_dedicated_time")

    assigned = fields.Boolean(
        string="Assigned",
        compute='_compute_assigned',
        store=True)
    assigned_qty = fields.Integer(
        string='Assigned QTY',
        compute='_compute_assigned_qty'
    )

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string="Customer")

    date_due = fields.Date(string="Date Due")

    corrective_action = fields.Html(
        help="Detail of corrective action after the issue")

    preventive_action = fields.Html(
        help="Detail of corrective before the issue."
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Assigned to',
        default=_default_user_id)

    # def set_assigned(self):
    #     self.ensure_one()
    #     self.write({
    #         'assigned': True,
    #         'state': 'assigned',
    #         'user_id': self.env.user.id
    #     })

    # # Change Assigned boolean through an external button.
    # # View hides this button in case we are not creating a New ticket.
    # def set_progress(self):
    #     self.ensure_one()
    #     self.state = 'progress'

    # def set_waiting(self):
    #     self.ensure_one()
    #     # Set the state to 'waiting'
    #     self.state = 'pending'

    # def set_done(self):
    #     self.ensure_one()
    #     # Set the state to 'done'
    #     self.state = 'done'

    # def set_cancel(self):
    #     self.ensure_one()
    #     # Set the state to 'cancel'
    #     self.state = 'cancel'

    action_ids = fields.One2many(
        comodel_name='helpdesk.ticket.action',
        inverse_name='ticket_id',
        string='Actions'
    )

    tag_ids = fields.Many2many(
        comodel_name='helpdesk.tag',
        relation='helpdesk_ticket_tag_rel',
        column1='ticket_id',
        column2='tag_id',
        string='Tags',
        domain=[('name', 'like', 'a')]
    )

    related_tag_ids = fields.Many2many(
        comodel_name='helpdesk.tag',
        string='Related tags',
        compute='_compute_related_tag_ids'
    )
    new_tag_name = fields.Char(
        string='New tag',
    )

    def _search_dedicated_time(self, operator, value):
        action_ids = self.env['helpdesk.ticket.action'].search(
            [('dedicated_time', operator, value)]
            )
        return [('id', 'in', action_ids.mapped('ticket_id').ids)]

    def _set_dedicated_time(self):
        for record in self:
            computed_time = sum(record.action_ids.mapped('dedicated_time'))
            if self.dedicated_time != computed_time:
                values = {
                    'name': "Auto time",
                    'date': fields.Date.today(),
                    'ticket_id': record.id,
                    'dedicated_time': self.dedicated_time - computed_time
                }
                self.update({'action_ids': [(0, 0, values)]})

    @api.depends('action_ids.dedicated_time')
    def _compute_dedicated_time(self):
        for record in self:
            record.dedicated_time = sum(
                record.action_ids.mapped('dedicated_time')
            )

    def create_new_tag(self):
        self.ensure_one()
        action = self.env.ref('prueba.helpdesk_tag_new_action').read()[0]
        action['context'] = {
            'default_name': self.new_tag_name,
            'default_ticket_ids': [(6, 0, self.ids)],
        }
        return action

    def create_new_tag_back(self):
        self.ensure_one()
        tag = self.env['helpdesk.tag'].create({
            'name': self.new_tag_name
        })
        self.write({
            'tag_ids': [(4, tag.id, 0)]
        })

    @api.depends('user_id')
    def _compute_assigned(self):
        for record in self:
            record.assigned = record.user_id and True

    @api.depends('user_id')
    def _compute_assigned_qty(self):
        for record in self:
            user = record.user_id
            other_tickets = self.env['helpdesk.ticket'].search([
                ('user_id', '=', user.id)

            ])
            record.assigned_qty = len(other_tickets)

    @api.depends('user_id')
    def _compute_related_tag_ids(self):
        for record in self:
            user = record.user_id
            other_tickets = self.env['helpdesk.ticket'].search([
                ('user_id', '=', user.id)

            ])
            all_tag = other_tickets.mapped('tag_ids')
            # self.related_tag_ids = all_tag
            self.update({
                'related_tag_ids': [(6, 0, all_tag.ids)]
            })

    @api.constrains('dedicated_time')
    def _verify_dedicated_time(self):
        for ticket in self:
            if ticket.dedicated_time and ticket.dedicated_time < 0:
                raise ValidationError(("Time must be a poisitve value."))

    @api.onchange('date')
    def _onchange_date(self):
        if not self.date:
            self.date_due = False
        else:
            if self.date < fields.Date.today():
                raise UserError(("The date must be today's date "
                                "or a future date."))
            date_datetime = fields.Date.from_string(self.date)
            self.date_due = date_datetime + timedelta(1)
