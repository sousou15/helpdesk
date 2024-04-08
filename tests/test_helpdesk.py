from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from odoo.fields import Date


class TestHelpdesk(TransactionCase):
    def setUp(self):
        super(TestHelpdesk, self).setUp()
        self.ticket = self.env.ref('prueba.helpdesk_ticket_demo_01')
        self.tag = self.env.ref('prueba.helpdesk_ticket_tag_demo_01')
        self.ticket.tag_ids = [(6, 0, self.tag.ids)]

    def test_10_tag_assign(self):
        self.assertEqual(self.ticket.tag_ids, self.tag)

    def test_20_raise_exceptions(self):
        self.ticket.dedicated_time = 2
        self.assertEqual(self.ticket.dedicated_time, 2)
        with self.assertRaises(ValidationError):
            self.ticket.dedicated_time = -2

    def test_30_set_dedicated_time(self):
        self.ticket.dedicated_time = 10
        self.ticket._set_dedicated_time()
        computed_time = sum(self.ticket.action_ids.mapped('dedicated_time'))
        self.assertEqual(self.ticket.dedicated_time, computed_time)
        self.assertTrue(self.ticket.action_ids)
        self.assertEqual(self.ticket.action_ids.date, Date.today())

    def test_40_dedicated_time_positive(self):
        # Verificamos que la restricción permita un valor positivo
        self.ticket.dedicated_time = 5
        # Si no se lanza una excepción, la prueba pasa
        # Si se lanza una excepción, la prueba falla
        try:
            self.ticket._verify_dedicated_time()
        except ValidationError:
            self.fail("ValidationError raised unexpectedly")


