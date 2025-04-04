from aiogram.dispatcher.filters.state import StatesGroup, State


class Learning(StatesGroup):
    zero = State()
    one = State()
    two = State()
    three = State()
    four = State()
    five = State()
    six = State()
    seven = State()
    eight = State()
    nine = State()
    ten = State()


class Form(StatesGroup):
    reason = State()
    two_reason = State()
