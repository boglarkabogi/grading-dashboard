$$f = x^4 + 4x^3 + x^2 + 2 \in \mathbb{Z}_5[x]$$
$$g = x^5 + x^4 + 3x^3 + x^2 + x + 4 \in \mathbb{Z}_5[x]$$

$$f = 0 \cdot q + f$$
$$q = (x+1) \cdot f + (4x^3 + 4x + 2)$$
$$f = (-x+1)(4x^3 + 4x + 2) + 3x$$
$$4x^3 + 4x + 2 = (3x^2 + 3) \cdot 3x + 2$$
$$3x = (-x) \cdot 2 + 0$$

$$\begin{array}{c|c|c}
i & q^i & r_i \\
\hline
-1 & - & f \\
0 & - & g \\
1 & 0 & f \\
2 & x+1 & 4x^3 + 4x + 2 \\
3 & -x+1 & 3x \\
4 & 3x^2+3 & 2 \\
5 & -x & 0
\end{array}$$

$$\gcd(f,g) = \boxed{2}$$