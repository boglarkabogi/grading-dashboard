A képen látható kézzel írt matematikai megoldás transzkripciója:

$$f = x^4 + 2x^3 + 3x^2 + 2x + 1 \in \mathbb{Z}_5[x]$$
$$g = x^5 + x^4 + 2x^3 + 4x^2 + 4x + 3 \in \mathbb{Z}_5[x]$$

$$\text{polinomok lko-ja :}$$

### Fő lépések (Euclid-i algoritmus):

$$g = f \cdot (x) + (4x^4 + 4x^3 + 2x^2 + 3x + 3)$$
$$f = (4x^4 + 4x^3 + 2x^2 + 3x + 3) \cdot (4) + (x^3 + 4)$$
$$4x^4 + 4x^3 + 2x^2 + 3x + 3 = (x^3 + 4) \cdot (4x) + (4x^3 + 2x^2 + 2x + 3)$$
$$x^3 + 4 = (4x^3 + 2x^2 + 2x + 3) \cdot (4) + (2x^2 + 2x + 2)$$
$$4x^3 + 2x^2 + 2x + 3 = (2x^2 + 2x + 2) \cdot 2x + \boxed{(3x^2 + 3x + 3)}$$
$$2x^2 + 2x + 2 = (3x^2 + 3x + 3) \cdot 4 + 0$$

$$\underline{\underline{\text{lko}(f,g) = 3x^2 + 3x + 3}}$$

---

### Részletes osztások (bal oldal alsó része):

$$(4x^3 + 2x^2 + 2x + 3) : (2x^2 + 2x + 2) = 2x$$
$$-(4x^3 + 4x^2 + 4x)$$
$$---------------------$$
$$-2x^2 - 2x + 3$$
$$\Rightarrow 3x^2 + 3x + 3 \pmod 5$$

$$(2x^2 + 2x + 2) : (3x^2 + 3x + 3) = 4$$
$$-(2x^2 + 2x + 2)$$
$$---------------------$$
$$0$$

---

### Hosszú polinomiosztások (jobb oldal):

#### 1. lépés:
$$(x^5 + x^4 + 2x^3 + 4x^2 + 4x + 3) : (4x^4 + 4x^3 + 2x^2 + 3x + 3) = x$$
$$-(x^5 + 4x^4 + 3x^3 + 3x^2 + x)$$
$$--------------------------------$$
$$-x^4 - x^3 + 2x^2 + 3x + 3$$
$$\Rightarrow 4x^4 + 4x^3 + 2x^2 + 3x + 3 \pmod 5$$

#### 2. lépés:
$$(x^4 + 2x^3 + 3x^2 + 2x + 1) : (4x^4 + 4x^3 + 2x^2 + 3x + 3) = 4$$
$$-(16x^4 + 8x^3 + 8x^2 + 12x + 12)$$
$$-----------------------------------$$
$$2x^4 + x^3 + 3x^2 + 2x + 2$$
$$\Rightarrow x^3 + 4 \pmod 5$$

#### 3. lépés:
$$(4x^4 + 4x^3 + 2x^2 + 3x + 3) : (x^3 + 4) = 4x$$
$$-(4x^4 + 16x)$$
$$----------------$$
$$\Rightarrow -(4x + x)$$
$$4x^3 + 2x^2 + 2x + 3$$

#### 4. lépés:
$$(x^3 + 4) , (4x^3 + 2x^2 + 2x + 3) = 4$$
$$-((16x^3 + 8x^2 + 8x + 12))$$
$$------------------------------$$
$$\Rightarrow -(x^3 + 3x^2 + 3x + 2) \pmod 5$$
$$------------------------------$$
$$\Rightarrow 2x^2 + 2x + 2 \pmod 5$$

---

### Kiegészítő megjegyzések (jobb szélen):

$$\frac{x^5}{x^4} = x$$
$$\frac{x^4}{x^3} = 4x$$
$$4x \equiv 1 \pmod 5$$
$$4x \equiv 4 \pmod 5$$
$$\Rightarrow x \equiv 4$$