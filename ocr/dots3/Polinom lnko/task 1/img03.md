$$f = x^4 + 3x^3 + 2x^2 + x + 4 \in \mathbb{Z}_5[x] \qquad g = x^5 + x^4 + x^2 + x + 2 \in \mathbb{Z}_5[x]$$

$$g = \boxed{?} \cdot f + r_1$$
$$\text{(crossed-out line below)}$$

$$x^5 + x^4 + x^2 + x + 2 : x^4 + 3x^3 + 2x^2 + x + 4 = x$$
$$x^5 + 3x^4 + 2x^3 + x^2 + 4x \ominus$$
$$\hline$$
$$2x^4 + 3x^3 + 2x + 2 \quad (r_1) \qquad g = x \cdot f + 3x^4 + 3x^2 + 2x + 2$$
$$\hline$$
$$f = \boxed{?} \cdot r_1 + r_2$$

$$x^4 + 3x^3 + 2x^2 + x + 4 : 3x^4 + 3x^3 + 2x + 2 = 2$$
$$x^4 + x^3 + 4x + 4 \ominus$$
$$\hline$$
$$2x^3 + 2x^2 + 2x \quad (r_2) \qquad f = 2 \cdot r_1 + r_2$$
$$\hline$$
$$r_1 = \boxed{?} r_2 + r_3$$

$$3x^4 + 3x^3 + 2x + 2 : 2x^3 + 2x^2 + 2x = 4x$$
$$3x^4 + 3x^3 + 3x^2 \ominus$$
$$\hline$$
$$2x^2 + 2x + 2 \quad (r_3) \qquad r_1 = 4x \cdot r_2 + r_3$$
$$\hline$$
$$r_2 = \boxed{?} r_3 + r_4$$

$$2x^3 + 2x^2 + 2x : 2x^2 + 2x + 2 = x$$
$$2x^3 + 2x^2 + 2x \ominus$$
$$\hline$$
$$0 \quad (r_4) \qquad r_2 = x \cdot r_3 + r_4 \to 0$$

$$\# \quad \text{lnko}(f,g) = r_3 = 2x^2 + 2x + 2$$