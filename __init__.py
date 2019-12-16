# This file is part sale_move_relation module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from . import move

def register():
    Pool.register(
        move.Move,
        module='sale_move_relation', type_='model')
