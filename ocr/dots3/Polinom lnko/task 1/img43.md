$$f = x^4 + 3x^3 + 2x^2 + x + 4 \qquad g = x^5 + x^4 + x^2 + x + 2$$

$$x^5 + x^4 + 0x^3 + x^2 + x + 2 : x^4 + 3x^3 + 2x^2 + x + 4 = x - 2$$
$$-(x^5 \quad 3x^4 \quad 2x^3 \quad x^2 \quad 4x)$$
$$\hline$$
$$-2x^4 - 2x^3 \quad -3x^2 + 2x$$
$$-(-2x^4 - 6x^3 - 4x^2 - 2x - 8)$$
$$\hline$$
$$0 \quad 4x^3 \quad 4x^2 \quad -x + 10$$

$$q = x - 2$$

$$(x-2)f = x^5 + x^4 + x^3 + 2x^2 + 2x + 2 \quad \text{mod } 5$$

$$r_1 = g - (x-2)f = (x^5+x^4+x^2+x+2) - (x^5+x^4+x^3+2x^2+2x+2) = -x^3-x^2-x-1 \equiv 4 \pmod 5$$
$$r_1 = 4x^3 + 4x^2 + 4x$$

$$g = (x-2)f + r_1 \quad \text{deg } r_1 = 3$$

$$(-x-2)r_1 = x^4 + 3x^3 + 3x^2 + 2x \quad \text{mod } 5$$

$$f_2 = f - (-x-2)r_1 = -x^2 - x + 4$$
$$-1 \equiv 4$$
$$r_2 = 4x^2 + 4x + 4$$

$$f = (-x-2)r_1 + r_2 \quad \text{deg } r_2 = 2$$

$$4^{-1} r_2 = 4 \cdot (4x^2 + 4x + 4) = x^2 + x + 1$$

$$\gcd(f,g) = x^2 + x + 1$$

$$f = (x^2+x+1)(x^2+2x+4) \qquad g = (x^2+x+1)(x^3+4x+2)$$