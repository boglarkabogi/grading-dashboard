Here is the transcription of the handwritten mathematical solution on the page, oriented in the standard reading direction (rotated 90 degrees clockwise):

### Definitions
$$ f = x^4+3x^3+2x^2+x+4 \in \mathbb{Z}_5[x] $$
$$ g = x^5+x^4+x^2+x+2 \in \mathbb{Z}_5[x] $$

---

### Evaluation Table
$$\begin{array}{c|c}
c & \text{Value} \\
\hline
-1 & x^4+x^3-2x^2+x \\
0 & x^4+x^3-2x^2+x+4 \\
1 & 4x^3+4x+2 \\
2 & x+1 \\
3 & 3 \\
4 & 0
\end{array}$$

---

### Euclidean Algorithm Remainders / Key Polynomials
$$\begin{aligned}
&x+3 \\
&4x+3 \\
&4x^2+13x+3 \\
&2x+3
\end{aligned}$$

$$ (f,g) = 3 = 3 = 1 $$

---

### Division Steps

#### First Division Block:
Dividing $x^5+x^4+0x^3+2x^2+x+2$ by $x^4+3x^3+2x^2+x+4$:
* Quotient: $x+3$
* Product of $x$ and divisor:
  $$ x^5+3x^4+2x^3+x^2+4x $$
* Subtraction line:
  $$ -2x^4-2x^3+x^2-3x+2 $$
* Product of $3$ and divisor:
  $$ 3x^4+4x^3+x^2+3x+2 $$
* Subtraction line:
  $$ 3x^4+3x^3+3x^2+3x+2 $$
* Remainder starts with:
  $$ 4x^3+... $$

#### Second Division Block (with circled quotient $x+4$):
* Dividend: $4x^4+x^3+2x^2+x+1$
* Divisor: $4x^3+...$
* Steps include:
  $$ 4x^4+4x^3+... $$
  $$ 2x^2+2x+4 $$
  $$ 2x^2+2x $$
  $$ 4 $$

#### Third Division Block (with circled $3$):
* Dividend: $3x^2+3x+2$
* Divisor: $3x$
* Quotient: $x+2$
* Steps:
  $$ 3x^2+2x $$
  $$ x+2 $$
  $$ 3x+2 $$
  $$ 3 $$
  $$ 0 $$

---

### Bottom Right Relation
$$ x+4 : 3 = 2x+3 $$
With a small division layout:
$$ x \cdot \frac{4}{0} $$