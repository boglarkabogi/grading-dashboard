A képen látható kézzel írt matematikai megoldás transzkripciója:

$$f(x) = x^4+x^3+3x^2+2x+2 \in \mathbb{Z}_5[x]$$
$$g(x) = x^5+x^4+x^3+3x^2+3x+3 \in \mathbb{Z}_5[x]$$

$$g = q_1 \cdot f + r_1$$

$$x^5+x^4+x^3+3x^2+3x+3 : x^4+x^3+3x^2+2x+2 = x$$
$$-x^5+x^4+3x^3+2x^2+2x$$
$$\hline$$
$$+2x^3+x^2+x+3 = 3x^3+x^2+x+3 \quad (-2\equiv 3 \pmod 5)$$

---

### Bal oldali osztás (középen lent / bal oldalon):
$$x^4+x^3+3x^2+2x+2 : x = x^3+x^2+3x+2$$
$$-x^4$$
$$\hline$$
$$x^3+3x^2+2x+2$$
$$-x^3$$
$$\hline$$
$$3x^2+2x+2$$
$$-3x^2$$
$$\hline$$
$$2x+2$$
$$-2x$$
$$\hline$$
$$2$$

### Jobb oldali osztás:
$$x^4+x^3+3x^2+2x+2 : 3x^3+x^2+x+3 = x+x$$
$$-3x^4+x^3+x^2+3x$$
$$\hline$$
$$3x^4+2x^2+4x+2$$
$$-6x^4+x^3+x^2+x$$
$$\hline$$
$$x^3+x^2+x+2$$

### Bal alsó osztás:
$$3x^3+x^2+x+3 : 2 = \frac{1}{2}x^3+\frac{1}{4}x^2+\frac{1}{2}x$$
$$\hline$$
$$x^2+x+3$$
$$-x^2$$
$$\hline$$
$$x+3$$
$$-x$$
$$\hline$$
$$3$$

---

### Jobb oldali megjegyzés (magyarul):
$$\text{Ötétel szerint}$$
$$\text{miből van ?}$$