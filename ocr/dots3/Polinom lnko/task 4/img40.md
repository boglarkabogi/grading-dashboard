Beadvány 6.

számolja ki az $f = x^4+4x^3+x^2+2 \in \mathbb{Z}_5[x]$  
$g = x^5+x^4+3x^3+x^2+x+4 \in \mathbb{Z}_5[x]$  
legnagyobb közös osztóját.

$\deg(f) < \deg(g)$  

$\frac{g}{f} = \frac{x^5}{x^4} = x \quad \text{pl. } x \cdot f(x) = (x^5+4x^4+x^3+2x) - \dots$ (crossed out)

$$\begin{array}{r}
x^5+x^4+3x^3+x^2+x+4 \\
- x^5+4x^4+x^3+2x \\ \hline
= 2x^4+2x^3+x^2+4x+4 \leftarrow V_1
\end{array}$$

$\text{A meg } \frac{f}{V_1} = \frac{x^4+4x^3+x^2+2}{2x^4+2x^3+x^2+4x+4} = \frac{1}{2} + \dots$

$\text{mivel } f(x) - 3V_1(x) =$  
$$\begin{array}{r}
x^4+4x^3+x^2+2 \\
- x^4+x^3+3x^2+2x+2 \\ \hline
3x^3+3x^2+3x \leftarrow V_2
\end{array}$$

$V_2 = 3x(x^2+x+1)$  

$\frac{V_1}{V_2} = \dots = 4x \quad V_2 : 4x = 4x(3x^3+3x^2+3x)$  
$= 12x^4+12x^3+12x^2$  
$= 2x^4+2x^3+2x^2$

$V_1 - (4x)V_2 = 2x^4+2x^3+x^2+4x+4$  
$= 2x^4+2x^3+2x^2$  
$= 4x^2+4x+4 \leftarrow V_3$  
$= 4(x^2+x+1)$

$\gcd(f,g) = x^2+x+1$