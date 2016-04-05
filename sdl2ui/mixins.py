import operator


class ImmutableMixin(object):
    eq_operator = operator.is_
