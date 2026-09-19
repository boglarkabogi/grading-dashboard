$$f = x^4 + x^3 + 3x^2 + 2x + 2 \in \mathbb{Z}_5[x]$$
$$g = x^5 + x^4 + x^3 + 3x^2 + 3x + 3 \in \mathbb{Z}_5[x] \quad (f, g) = ?$$

$$g = \dots \cdot f + r_1$$

$$\begin{array}{r}
x^5 + x^4 + x^3 + 3x^2 + 3x + 3 : x^4 + x^3 + 3x^2 + 2x + 2 \\
-(x^5 + x^4 + 3x^3 + 2x^2 + 2x) \\
\hline
3x^3 + x^2 + x + 3 \quad \longrightarrow r_1
\end{array} \quad = x$$

$$g = (3x^3 + x^2 + x + 3) \cdot f + x \quad (\text{crossed out})$$
$$g = x \cdot f + (3x^3 + x^2 + x + 3)$$

$$f = \dots \cdot r_1 + r_2$$
$$f = (2x + 3) \cdot r_1 + r_2$$

$$\begin{array}{r}
3x^3 + x^2 + x + 3 : \\
x^4 + x^3 + 3x^2 + 2x + 2 : 3x^3 + x^2 + x + 3 = 2x + 3 \\
-(x^4 + 2x^3 + 2x^2 + x) \\
\hline
4x^3 + x^2 + x + 2 \\
-(4x^3 + 3x^2 + 3x + 4) \\
\hline
3x^2 + 3x + 5 \quad \longrightarrow r_2
\end{array}$$

$$r_1 = \dots \cdot r_2 + r_3$$
$$r_1 = (x + 1) \cdot r_2 + 0$$

$$\begin{array}{r}
3x^3 + x^2 + x + 3 : 3x^2 + 3x + 3 = x + 1 \\
-(3x^3 + 3x^2 + 3x) \\
\hline
3x^2 + 3x + 3 \\
-(3x^2 + 3x + 3) \\
\hline
0 \quad \longrightarrow r_3
\end{array}$$

$$\text{tehát}$$
$$(f, g) = r_2 = \underline{\underline{3x^2 + 3x + 3}}$$