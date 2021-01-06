# Logic Gates as Polynomials

## Binary logic Prelude

Binary logic gates are usually represented in their truth table form. However, there is a way to express those gates in a pure algebraic form. 
This representation would be done using polynomials 

`P : F2 X F2 -> F2` 

For example lets take a look at the following binary gates and their polynomial representation:

|  b   |  a   | b and a = b*a |
| :--: | :--: | :-----------: |
|  0   |  0   |       0       |
|  0   |  1   |       0       |
|  1   |  0   |       0       |
|  1   |  1   |       1       |

|  b   |  a   | b xor a= b+a |
| :--: | :--: | :----------: |
|  0   |  0   |      0       |
|  0   |  1   |      1       |
|  1   |  0   |      1       |
|  1   |  1   |      0       |

|  b   |  a   | b or a = b*a+b+a |
| :--: | :--: | :--------------: |
|  0   |  0   |        0         |
|  0   |  1   |        1         |
|  1   |  0   |        1         |
|  1   |  1   |        1         |

|  b   |  a   | not a = a+1 |
| :--: | :--: | :---------: |
|  0   |  0   |      1      |
|  0   |  1   |      0      |
|  1   |  0   |      1      |
|  1   |  1   |      0      |

### why is it useful?
By using the polynomial representation of a logic gate, Boolean algebra can be done using modular arithmetic while 
using De Morgan laws as arithmetic tricks when working over F2. 

## This work
Boolean logic is one variant of many such systems including, for example, Ternary Logic. 
This work's purpose is to enable the creation of polynomial representation for logic gates of all sorts in an efficient manner. 
The main problem facing an efficient implementation is the number of possible gates. 
Using nth-logic gates with 2 inputs and 1 output, the number of possible logic gates would be n^(n^2). 
As such simply calculating all gates and storing them is not scalable in the least. 
Moreover, it is not clear at all how one should even calculate all possible gates polynomials.

### Naive approach
Use a simple genetic algorithm to derive all equations.
Start with a population of all monomials of the form `b^k*a^s` for `0<=k,s<=n-1`.
create an array of size n^(n^2) that would represent all possible gates.

to demonstrate how each gate would be mapped to a different cell in the array we use the following example using ternary logic:

| b | a | output |
|:-:|:-:|:------:|
| 0 | 0 |    0   |
| 0 | 1 |    1   |
| 0 | 2 |    2   |
| 1 | 0 |    1   |
| 1 | 1 |    1   |
| 1 | 2 |    0   |
| 2 | 0 |    0   |
| 2 | 1 |    2   |
| 2 | 2 |    1   |

take the output and concatenate it from top to bottom. the resulting number in base 3 converted to base 10 would be the index of the cell.

in our example, the number we got is 012110021 which in base 3 is equal to 3976 in base 10.

in each iteration:
go over all the individuals in the current generation.
calculate the gate that this individual corresponds to. 
if the gate was already taken - the individual dies.
else, mark the gate as "taken".

to create the next generation go over each pair of surviving individuals and combine them using + or * operations. 

This approach works but is not scalable as it has a complexity of Omega(n^(n^2)).


### Using Polynomial Interpolation
The polynomial interpolation approach works only for prime `n`, however it does support generating polynomials for gates with arbitrary number of inputs.

Using nth logic gates with D inputs and 1 output, the number of possible logic gates is n^(n^D). 
The polynomial interpolation approach running time complexity is O(n^3D) as in essence it just creates a `n^D X n^D` matrix and finds its inverse.

Using that approach with D=2, we again start with an array containing all monomials of the form `b^s*a^k` for `0<=k,s<=n-1` 
which would serve as the basis for the linear space spanned by them. The dual space basis would be `(s,k)` for `0<=k,s<=n-1`. 

the matrix we would create, `M`, would be such that 

`M[i,j]` = the `monomial_array[j]` evaluated using `dual_space[i]`

inverting `M` and taking the transpose of the result we get a new matrix, `M_2`.
treating `monomial_array` as a vertical vector, we use matrix multiplication to calculate a new vector `polynomial_basis = M_2 * monomial_array`.
`polynomial_basis` is such that `polynomial_basis[j]` evaluated on `dual_space[i]` is `1` iff `i==j` and `0` otherwise.

now we can use `polynomial_basis` to get every gate polynomial.

for example with n=3 and D=2 to get the polynomial corresponding to the gate

| b | a | output |
|:-:|:-:|:------:|
| 0 | 0 |    x_0   |
| 0 | 1 |    x_1   |
| 0 | 2 |    x_2   |
| 1 | 0 |    x_3   |
| 1 | 1 |    x_4   |
| 1 | 2 |    x_5   |
| 2 | 0 |    x_6   |
| 2 | 1 |    x_7   |
| 2 | 2 |    x_8   |

we take `(x_0 * polynomial_basis[0]) + (x_1 * polynomial_basis[1]) + ... + (x_8 * polynomial_basis[8])`
and get a general equation for all such gates which given `x_0,...,x_8` gives a polynomial corresponding to that gate.

