$$\text{(Közös gyök: ...)}$$
$$\text{Vagyis } \lnko(f,g) = x^2-x$$
$$r_1 = \text{[scribbled]} = x^3 - x = x(x^2-1) \Rightarrow \left. \begin{array}{l} x_1=0 \\ x_2=1 \\ x_3=-1 \end{array} \right\}$$
$$\text{Közös gyök: } 0, 1, -1$$

$$\text{folytat... (crossed out)}$$
$$(4)\quad r_2 = q_4 r_3 + r_4 \text{ (crossed out)}$$
$$-(r_1)_1 = r_2 - (2x \cdot r_3) = r_2 - (-2x) = 0 \Rightarrow q_4 - 2x \quad r_4=0 \text{ (crossed out)}$$

---

$$\text{6. Beadandó}$$
$$f = x^4+x^3+4x+4 \in \mathbb{Z}_5[x] \qquad g = x^5+x^4+4x^3+2 \in \mathbb{Z}_5[x]$$

$$(1)\quad g = q_1 \cdot f + r_1$$
$$g_1 = g - (x \cdot f) = g - (x^5+x^4+4x^2+4x) = 4x^3 - 4x^2 - 4x + 2$$
$$\deg g_1 < \deg f \Rightarrow \text{öll} \Rightarrow q_1 = x \quad r_1 = 4x^3 - 4x^2 - 4x + 2$$

$$(2)\quad f = q_2 \cdot r_1 + r_2$$
$$f_2 = f - (4x \cdot r_1) = f - (x^4 - x^3 - x^2 + 3x) = 2x^3 + x^2 + x + 4$$
$$\deg f_2 < \deg r_1$$
$$f_2 = f_1 - (3 \cdot r_1) = f_1 - (2x^3 - 2x^2 - 2x + 1) = 3x^2 + 3x + 3$$
$$\deg f_2 < \deg r_1 \Rightarrow \text{öll} \Rightarrow q_2 = 4x+3 \quad r_2 = 3x^2+3x+3$$

$$(3)\quad r_1 = q_3 \cdot r_2 + r_3$$
$$(r_1)_1 = r_1 - (3x \cdot r_2) = r_1 - (4x^3 + 4x^2 + 4x) = 3x^2 + 3x + 2$$
$$(r_1)_2 = (r_1)_1 - (1 \cdot r_2) = (r_1)_1 - (3x^2 + 3x + 3) = -1$$
$$\deg (r_1)_2 < \deg r_2 \Rightarrow \text{öll} \Rightarrow q_3 = 3x+1 \quad r_3 = -1$$

---

$$(4)\quad r_2 = q_4 r_3 + r_4$$
$$(r_2)_1 = r_2 - (-3x^2 \cdot r_3) = r_2 - (3x^2) = 3x+3$$
$$(r_2)_2 = (r_2)_1 - (-3x \cdot r_3) = (r_2)_1 - (3x) = 3$$
$$(r_2)_3 = (r_2)_2 - (-3 \cdot r_3) = (r_2)_2 - 3 = 0$$

$$\text{Tehát } \lnko(f,g) = -1$$