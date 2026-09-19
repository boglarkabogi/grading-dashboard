$$f = x^4+3x^3+2x^2+x+4 \in \mathbb{Z}_5[x] \quad g = x^5+x^4+x^2+x+2 \in \mathbb{Z}_5[x]$$

$$\begin{aligned}
&f = g \cdot q + (-x^5+3x^3+4) && \text{lnko}(f,g)=? \\
&g = q_0(x-2) + (-x^3-x^2-x)^{v_1} && \ominus x^5+3x^4+2x^3+x^2+4x \\
&&&\hline \\
&&&-2x^4-2x^3-3x+2 \\
&&&\ominus -2x^4-6x^3-4x^2-2x-q \\
&&&\hline \\
&&&4x^3+4x^2-x+10 = 4x^3+4x^2+4x \\
&&&\quad \small{-x^3-x^2-x} \\
&f = v_1(-x-2) + (-x^2-x-1)^{v_2} && f : v_1 \\
&&&\ominus x^4+x^3+x^2 \\
&&&\hline \\
&&&2x^3+x^2+x+4 \\
&&&\ominus 2x^3+2x^2+2x \\
&&&\hline \\
&&&-x^2-x+4 = -x^2-x-1 \\
&v_1 = v_2(x) + 0 && v_1 : v_2 \\
&&&\ominus -x^3-x^2-x \\
&&&\hline \\
&&&0 \\
&\text{lnko}(f,g) = 4x^2+4x+4
\end{aligned}$$