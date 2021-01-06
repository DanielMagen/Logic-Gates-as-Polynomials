from mathematical_operations import get_evaluation_matrix, get_independent_polynomials, \
    get_matrix_inverse_transpose_mod, multiply_matrix_by_polynomial_column, apply_operation_to_all_pairs_in_list
from sympy.abc import a, b, c
from printing_utils import to_latex, mat_print, remove_latex
from utils import get_symbols

if __name__ == '__main__':
    # for some reason the technique below only works for prime numbers
    # unless the number is prime, the list of polynomials created is not linearly independent
    number_of_possible_values = 2

    # to use more than 2 variables import more symbols from sympy.abc, for example 'r'
    list_of_polynomials_variables = [a, b, c]

    # the final variables that would be used to create the general formula
    # the x_0 to x_m that are explained in the lyx file
    final_variables = get_symbols(number_of_possible_values ** len(list_of_polynomials_variables))

    # first create all the polynomials
    print("those are all the polynomials that are needed to span the solution space")
    polynomials = get_independent_polynomials(number_of_possible_values, list_of_polynomials_variables)
    mat_print(polynomials)
    print()

    # now find the base that corresponds to the dual base ((0,0),...(k,k)) for k = number_of_possible_values - 1
    print("this is the matrix that would be used in the linear interpolation algorithm")
    evaluation_matrix = get_evaluation_matrix(number_of_possible_values, polynomials, list_of_polynomials_variables)
    mat_print(evaluation_matrix.tolist())
    print()

    print("this is the transposed inverse of the previous matrix")
    evaluation_matrix_inverse_transpose = get_matrix_inverse_transpose_mod(evaluation_matrix, number_of_possible_values)
    mat_print(evaluation_matrix_inverse_transpose.tolist())
    print()

    print("those are the functions that are 1 on a single input and 0 on all others")
    base = multiply_matrix_by_polynomial_column(evaluation_matrix_inverse_transpose, polynomials)
    mat_print(base)
    print()

    # now create the final formula
    final_formula = [base[i] * final_variables[i] for i in range(len(base))]
    # sum all expressions. a direct loop that sums the expressions is too slow, so we sum them in pairs
    # basically what we do here is calculate sum(final_formula)
    while len(final_formula) > 1:
        final_formula = apply_operation_to_all_pairs_in_list(lambda x, y: x + y, final_formula)

    final_formula = final_formula[0]

    print("this is the final formula")
    print(final_formula)
    print()

    print("this is the final formula in latex matrix form")
    latex_formula = to_latex(final_formula, list_of_polynomials_variables)
    print(latex_formula)
    print()

    print("this is the final formula in regular form")
    print(remove_latex(latex_formula))
