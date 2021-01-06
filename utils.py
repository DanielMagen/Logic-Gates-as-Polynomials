from sympy import symbols


def get_only_poly_equation(pol):
    return pol.args[0]


def get_symbols(how_many_symbols):
    """
    :param how_many_symbols:
    :return: a list of symbols of the form: x_{0}, x_{1}, ...

    if we simply wanted to return symbols we would have used
    symbols(f'x:{how_many_symbols}')

    buy sympy suck and it orders the variables alphabetically, so x10 would be listed before x2 for example

    so we use a simple "trick" of creating variables with leading zeros in their names
    """
    length_of_each_index = len(str(how_many_symbols))
    symbols_to_return = []
    for i in range(how_many_symbols):
        str_i = str(i)
        length_of_current_i = len(str_i)
        str_i = '0' * (length_of_each_index - length_of_current_i) + str_i
        symbols_to_return.append(symbols('x_{' + str_i + '}'))

    return symbols_to_return
