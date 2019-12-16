# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import Pool, PoolMeta

__all__ = ['Move']


class Move(metaclass=PoolMeta):
    __name__ = 'stock.move'
    sale_planned_date = fields.Function(fields.Date(
        'Sale Planned Date'), 'get_sale_relation',
        searcher='search_sale_planned_date')
    warehouse_customer = fields.Function(fields.Many2One('stock.location',
        'Warehouse', domain=[('type', '=', 'warehouse')]),
        'get_sale_relation', searcher='search_warehouse_customer')
    shipment_customer = fields.Function(fields.Many2One('party.party', 'Customer'),
        'get_sale_relation', searcher='search_shipment_customer')

    @classmethod
    def get_sale_relation(cls, moves, names):
        res = {n: {m.id: None for m in moves} for n in names}

        for name in names:
            for move in moves:
                if name == 'sale_planned_date':
                    if (move.origin and move.origin.__name__ == 'sale.line'):
                        if hasattr(move.origin, 'manual_delivery_date'):
                            delivery_date = (move.origin.manual_delivery_date
                                or move.origin.shipping_date)
                        else:
                            delivery_date = move.origin.shipping_date
                        res[name][move.id] = delivery_date
                elif name == 'warehouse_customer':
                    if move.shipment and move.shipment.__name__ == 'stock.shipment.out':
                        res[name][move.id] = (move.from_location.warehouse.id
                            if move.from_location.warehouse else None)
                    elif move.shipment and move.shipment.__name__ == 'stock.shipment.out.return':
                        res[name][move.id] = (move.to_location.warehouse.id
                            if move.to_location.warehouse else None)
                    else:
                        res[name][move.id] = (move.from_location.warehouse.id
                            if move.from_location.warehouse else None)
                elif name == 'shipment_customer':
                    res[name][move.id] = (move.shipment.customer.id
                            if move.shipment else None)
        return res

    @classmethod
    def search_sale_planned_date(cls, name, clause):
        Line = Pool().get('sale.line')

        if hasattr(Line, 'manual_delivery_date'):
            return ['OR',
                ('origin.manual_delivery_date',) + tuple(clause[1:3])
                    + ('sale.line',) + tuple(clause[3:]),
                [
                    ('planned_date',) + tuple(clause[1:]),
                    ('origin.manual_delivery_date', '=', None, 'sale.line'),
                    ]
                ]

    @classmethod
    def search_warehouse_customer(cls, name, clause):
        return ['OR',
            ('to_location.warehouse',) + tuple(clause[1:]),
            ('from_location.warehouse',) + tuple(clause[1:])]

    @classmethod
    def search_shipment_customer(cls, name, clause):
        return ['OR',
            ('shipment.customer' + clause[0].lstrip(name),)
                + tuple(clause[1:3]) + ('stock.shipment.out.return',)
                + tuple(clause[3:]),
            ('shipment.customer' + clause[0].lstrip(name),)
                + tuple(clause[1:3]) + ('stock.shipment.out',)
                + tuple(clause[3:])]
