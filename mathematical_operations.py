from sympy import poly
from sympy import Matrix
from sympy import Rational
import sympy as sy
import numpy as np
import fractions
from copy import deepcopy
import math

from utils import get_only_poly_equation


class ConstantPoly:
    """
    for some reason sympy won't allow constant polynomials
    so I created this small class to allow me to do stuff
    without taking into account that I might have an int
    instead of a polynomial object

    """

    def __init__(self, val):
        self.val = val
        self.args = [str(val)]
        self.gens = ()

    def degree(self):
        return 0

    def total_degree(self):
        return 0

    def __str__(self):
        return str(self.val)

    def __repr__(self):
        return str(self)

    def __mod__(self, b):
        return self.val % b

    def __mul__(self, b):
        return self.val * b


def get_independent_polynomials(number_of_possible_values, list_of_polynomials_variables):
    current_degrees = [0 for _ in range(len(list_of_polynomials_variables))]

    def up_current_degrees():
        i = 0
        while i < len(current_degrees):
            current_degrees[i] += 1

            if current_degrees[i] < number_of_possible_values:
                return True

            current_degrees[i] = 0
            i += 1

        return False

    def get_polynomial_from_degrees():
        poly_expression = 1
        for j in range(len(list_of_polynomials_variables)):
            poly_expression *= list_of_polynomials_variables[j] ** current_degrees[j]

        return poly(poly_expression)

    polynomials = [ConstantPoly(1)]

    while up_current_degrees():
        polynomials.append(get_polynomial_from_degrees())

    # sort the polynomials by their degree and total_degree
    polynomials.sort(key=lambda pol: pol.degree())
    polynomials.sort(key=lambda pol: pol.total_degree())
    return polynomials


class EvaluatePolynomial:
    def __init__(self, list_of_values, list_of_polynomials_variables):
        self.list_of_values = deepcopy(list_of_values)
        self.list_of_polynomials_variables = list_of_polynomials_variables

    @staticmethod
    def evaluate_poly_with_vals(pol, list_of_polynomials_variables, list_of_values):
        """
        :param pol:
        :param list_of_polynomials_variables: a list of polynomials variables to evaluate
        :param list_of_values: a list the same length of the symbols to evaluate
        such that each value i would be put to symbol i
        :return: the evaluated polynomial
        """
        symbols_in_poly = pol.gens

        for i in range(len(list_of_polynomials_variables)):
            if list_of_polynomials_variables[i] in symbols_in_poly:
                pol = pol.eval(list_of_values[i])

        return pol

    def __call__(self, pol):
        return EvaluatePolynomial.evaluate_poly_with_vals(pol, self.list_of_polynomials_variables, self.list_of_values)


def get_dual_base(number_of_possible_values, list_of_polynomials_variables):
    """
    :param number_of_possible_values:
    :return: a list of size number_of_possible_values**(number of variables in polynomials)
    of functions that would evaluate polynomials

    for example if (number of variables in polynomials)=2 then it would return

    the first function would evaluate all polynomials at 0,0
    the second function would evaluate all polynomials at 0,1
    .
    .
    (we set k = number_of_possible_values - 1)
    the k'th function would evaluate all polynomials at 0,k
    the k+1 function would evaluate all polynomials at 1,0
    .
    .
    .
    the k**2 function would evaluate all polynomials at k,k
    """
    current_evaluation = [0 for _ in range(len(list_of_polynomials_variables))]

    def up_current_evaluation():
        i = 0
        while i < len(current_evaluation):
            current_evaluation[i] += 1

            if current_evaluation[i] < number_of_possible_values:
                return True

            current_evaluation[i] = 0
            i += 1

        return False

    dual_base = [EvaluatePolynomial(current_evaluation, list_of_polynomials_variables)]

    while up_current_evaluation():
        dual_base.append(EvaluatePolynomial(current_evaluation, list_of_polynomials_variables))

    return dual_base


def get_evaluation_matrix(number_of_possible_values, list_of_polynomials, list_of_polynomials_variables):
    """

    :param number_of_possible_values:
    :return: a matrix such that
    for example if len(list_of_polynomials)=2 then it would return
    the first row would be the all the polynomials evaluated at 0,0 mod number_of_possible_values
    the second row would be the all the polynomials evaluated at 0,1 mod number_of_possible_values
    .
    .
    (we set k = number_of_possible_values - 1)
    the k'th row would be the all the polynomials evaluated at 0,k mod number_of_possible_values
    the k+1 row would be the all the polynomials evaluated at 1,0 mod number_of_possible_values
    .
    .
    .
    the k**2 row would be the all the polynomials evaluated at k,k mod number_of_possible_values
    """
    dual_base = get_dual_base(number_of_possible_values, list_of_polynomials_variables)
    rows = []
    for eval_func in dual_base:
        new_row = map(eval_func, list_of_polynomials)
        new_row = map(lambda m: m % number_of_possible_values, new_row)
        rows.append(list(new_row))

    return Matrix(rows)


def sympy_rational_to_int_modulus_number(sympy_rational, modulus_number):
    def additive_inverse(negative_num):
        return modulus_number + negative_num

    # taken from https://en.wikibooks.org/wiki/Algorithm_Implementation/Mathematics/Extended_Euclidean_algorithm
    def multiplicative_inverse(num):
        def egcd(a, b):
            if a == 0:
                return (b, 0, 1)
            else:
                g, y, x = egcd(b % a, a)
                return (g, x - (b // a) * y, y)

        def modinv(a, m):
            g, x, y = egcd(a, m)
            if g != 1:
                raise Exception('modular inverse does not exist')
            else:
                return x % m

        return modinv(num, modulus_number)

    def multiplicative_inverse_of_prime(num):
        return pow(num, modulus_number - 2, modulus_number)

    def is_prime(num):
        return all(num % l for l in range(2, math.ceil(math.sqrt(num))))

    numerator, denominator = sympy_rational.p, sympy_rational.q
    if numerator < 0:
        numerator = additive_inverse(numerator)

    if is_prime(modulus_number):
        denominator = multiplicative_inverse_of_prime(denominator)
    else:
        denominator = multiplicative_inverse(denominator)

    return (numerator * denominator) % modulus_number


def get_matrix_inverse_transpose_mod(matrix, modulus):
    # for some reason the inverse in modulus operation takes a really long time
    # but the regular inverse is really fast
    # so perhaps it would be better to calculate the regular inverse and then convert it to a modulus one
    # this is the way to do the inverse + transpose using modulus
    # return (matrix.inv_mod(modulus)).T

    # it seems like even the usual sympy matrix inverse is seriously slow
    # I think its because it keeps the numbers rational
    # if you want here is the operation used to calculate regular inverse + transpose
    # inverse_transposed = (matrix ** -1).T

    # my solution would be to calculate the inverse in numpy and then convert the result into a sympy matrix
    # of rational numbers

    # first calculate the inverse using numpy
    numpy_matrix = np.array(matrix).astype(np.float64)
    inverse_matrix = (np.linalg.inv(numpy_matrix))

    # now convert the floats in the matrix to their rational form
    vfunc = np.vectorize(lambda x: Rational(fractions.Fraction(x).limit_denominator()))
    inverse_matrix = vfunc(inverse_matrix)

    # now convert the matrix back to a sympy matrix and apply modulus operation
    inverse_matrix = Matrix(inverse_matrix)
    inverse_matrix = inverse_matrix.applyfunc(
        lambda num: sympy_rational_to_int_modulus_number(num, modulus))

    # sanity check - check that the inverse is really the inverse modulus
    assert (inverse_matrix * matrix) % modulus == sy.eye(len(numpy_matrix))

    return inverse_matrix.T


def multiply_matrix_by_polynomial_column(matrix, polynomial_list):
    """

    :param matrix:
    :param polynomial_list:
    :return:
    the result of matrix * polynomial_list such that polynomial_list is a column vector
    """
    # first get rid of all the constant polynomials which are object I created
    new_polynomial_list = []
    for i in range(len(polynomial_list)):
        polynomial = polynomial_list[i]
        if not polynomial.gens:
            polynomial = polynomial.val
        new_polynomial_list.append(polynomial)

    to_return = []
    for row in matrix.tolist():
        summ = 0
        for i in range(len(row)):
            summ += row[i] * new_polynomial_list[i]

        to_return.append(summ)

    return to_return


def apply_operation_to_all_pairs_in_list(operation, lis):
    result = [operation(lis[i], lis[i + 1]) for i in range(0, len(lis) - 1, 2)]
    if len(lis) % 2 == 1:
        result.append(lis[-1])

    return result
