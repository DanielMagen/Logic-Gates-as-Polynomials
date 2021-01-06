import re
from sympy.polys.polytools import poly_from_expr, LC, Poly, degree
from utils import get_only_poly_equation


def mat_print(matrix):
    for item in matrix:
        print(item)


def print_poly(pol, remove_multiplications_symbol=False):
    to_print = str(get_only_poly_equation(pol))
    if remove_multiplications_symbol:
        to_print = ''.join(c for c in to_print if c != '*')
    print(to_print)


def split_polynomial_by_degree(polynomial_to_split, list_of_polynomials_variables):
    """
    :param polynomial_to_split:
    :return: a list of lists,
    each inner list is of the form [term ,term without coefficient, only coefficients of term]
    if the polynomial is 0, an empty list is returned
    """
    result = list(polynomial_to_split.args[0].args)
    for i in range(len(result)):
        term = poly_from_expr(result[i], gens=list_of_polynomials_variables, expand=False)[0]
        term_coefficients = LC(term)
        term_without_coefficient = term / term_coefficients
        result[i] = [term, term_without_coefficient, term_coefficients]

    return result


def polynomial_equation_to_latex(polynomial_equation):
    if isinstance(polynomial_equation, Poly):
        s = get_only_poly_equation(polynomial_equation)
    else:
        s = polynomial_equation
    s = str(s)
    s = s.replace('**', '^')
    s = s.replace('*', '\\cdot ')
    s = s.replace('(', '\\left(')
    s = s.replace(')', '\\right)')

    # remove leading zeroes from index of x
    s = re.sub('x_\{0+', 'x_{', s)

    # now we removed x_{0}, so enter it back
    s = re.sub('x_\{\}', 'x_{0}', s)

    return s


def get_matrix_in_latex(mat):
    ELEMENT_SEPERATOR = '&'
    ROW_SEPERATOR = '\\\\ \n'
    matrix_latex = '\\begin{matrix} \n'
    for row in mat:
        if isinstance(row, list):
            matrix_latex += ELEMENT_SEPERATOR.join(map(str, row)) + ROW_SEPERATOR
        else:
            matrix_latex += str(row) + ROW_SEPERATOR

    matrix_latex += '\\end{matrix}'

    return matrix_latex


def get_order_key_for_monomial(monomial, list_of_polynomials_variables):
    """
    :param monomial:
    :param list_of_polynomials_variables:

    :return: we wish to order monomials
    we would do so by given them each a key that would simply be the ordered degree
    of the variables in the polynomial
    """
    degrees = [degree(monomial, var) for var in reversed(list_of_polynomials_variables)]
    # first sort by the lowest degree
    result = [sum(degrees)]
    # then sort by the least amount of different variables in them
    result.append(len(degrees) - degrees.count(0))
    # finally sort by the degree of each variable
    result += degrees

    return result


def sort_list_by_monomials(list_containing_monomials, list_of_polynomials_variables, function_to_extract_monomials):
    """
    :param list_containing_monomials:
    :param list_of_polynomials_variables:
    :param function_to_extract_monomials: the list containing the monomials might contain them in a complicated way
    so we use this function to extract the monomials

    :return:
    """
    result = sorted(list_containing_monomials,
                    key=lambda item: get_order_key_for_monomial(function_to_extract_monomials(item),
                                                                list_of_polynomials_variables))
    return result


def to_latex(polynomial, list_of_polynomials_variables):
    """
    :param polynomial:
    :return: converts the polynomial into a LaTeX form and splits it into a matrix
    """

    # split the polynomial by degree
    split_poly = split_polynomial_by_degree(polynomial, list_of_polynomials_variables)

    # order the split poly by the terms if you want
    split_poly = sort_list_by_monomials(split_poly, list_of_polynomials_variables, lambda item: item[1])

    # now get just the terms back
    split_poly = [t[0] for t in split_poly]

    # convert each sub-equation into a latex string
    split_poly = list(map(polynomial_equation_to_latex, split_poly))

    # in the process we removed all the '+' so re enter them
    for i in range(len(split_poly) - 1):
        split_poly[i] += ' + '

    # convert to the final matrix latex form
    final_string = get_matrix_in_latex(split_poly)

    return final_string


def remove_latex(string):
    replaces = [
        ['\\\\', ''],
        ['\\begin{matrix}', ''],
        ['\\end{matrix}', ''],
        ['_{', ''],
        ['}', ''],
        ['\\right)', ')'],
        ['\\left(', '('],
        ['\\cdot', ' *'],
    ]
    for to_replace, by in replaces:
        string = string.replace(to_replace, by)

    return string
