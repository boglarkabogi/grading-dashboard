Házi feladat:

$$f = x^4+x^3+3x^2+2x+2 \in \mathbb{Z}_5[x] \quad , \quad g = x^5+x^4+x^3+3x^2+3x+3 \in \mathbb{Z}_5[x]$$

$$\lnko(f,g) = 4$$

$$(g:f)$$
$$\Theta(x^5+x^4+3x^3+2x^2+2x) \qquad q_1 = x$$
$$-2x^3+x^2+x+3 = r_1$$

$$f = x^4+x^3+3x^2+2x+2$$
$$\Theta(x^4-3x^3\dots-3x^2-9x) \qquad q_2 = -3x+1$$
$$= -2x^3+\Theta x^2+x+2$$
$$= 3x^3+x^2+x+2$$

$$\Theta(3x^3+x^2)\Theta(3x^3+x^2+x+3)$$
$$-1 = \textcircled{r}_2 \qquad q_3 = 2x^3-x^2-x-3$$
*(with "lnko" written above the circled $r_2$)*

$$(\mathbb{Z}_5 \Rightarrow) r_1 = (3x^3)+x^2+x+3$$
$$\text{és } \Theta(-2x^3)$$
$$x^2+x+3$$
$$\Theta(x^2)$$
$$x+3$$
$$\dots$$

On the right side column (connected by a curved arrow):
$$\Theta(x)$$
$$3$$
$$\Theta(3)$$
$$0$$