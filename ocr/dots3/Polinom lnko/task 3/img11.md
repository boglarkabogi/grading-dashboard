$f = x^4 + 2x^3 + x^2 + 4 \in \mathbb{Z}_5[x]$

$g = x^5 + x^4 + 2x^3 + 2x^2 + 2x + 1 \in \mathbb{Z}_5[x]$

$g / f \quad\quad\quad x^5 / x^4 = x$

$x \cdot f = x^5 + 2x^4 + x^3 + 4x$

$g - x \cdot f = (x^5 + x^4 + 2x^3 + 2x^2 + 2x + 1) - (x^5 + 2x^4 + x^3 + 4x) \pmod 5$

$r_1 = 4x^4 + x^3 + 2x^2 + 3x + 1$

$4x^4 / x^4 = 4$

$4f = 4x^4 + 3x^3 + 4x^2 + 1$

$r_1 - 4f = (4x^4 + x^3 + 2x^2 + 3x + 1) - (4x^4 + 3x^3 + 4x^2 + 1) \pmod 5$

$r_2 = 3x^3 + 3x^2 + 3x$

$f / r_2 \quad\quad\quad 2x$

$2x \cdot r_2 = x^4 + x^3 + x^2$

$f - (2x) r_2 = (x^4 + 2x^3 + x^2 + 4) - (x^4 + x^3 + x^2) = x^3 + 4$

$\frac{1}{3} \quad\quad\quad 2 \cdot r_2 = x^3 + x^2 + x$

$(x^3 + 4) - (x^3 + x^2 + x) = 4x^2 + 4x + 4 \pmod 5$

$f = (2x + 2) r_2 + 4(x^2 + x + 1)$

$\operatorname{lnko}(f,g) = x^2 + x + 1 \in \mathbb{Z}_5[x]$