Based on the handwritten solution on the page, here is the transcription of the mathematical steps of the Euclidean algorithm as written by the student (ordered by the steps of the division):

### First division ($g(x)$ divided by $f(x)$):
$$(x^5 + x^4 + 2x^3 + 2x^2 + x + 4) : (x^4 + 2x^3 + x^2 + x + 4)$$
$$x^5 + 2x^4 + x^3 + 4x$$
$$4x^4 + x^3 + 2x^2 + 3x + 4$$
$$4x^4 + 3x^3 + 4x^2 + 4$$
$$3x^3 + 3x^2 + 3x$$

### Second division ($f(x)$ divided by the remainder $3x^3 + 3x^2 + 3x$):
$$(x^4 + 2x^3 + x^2 + 4) : (3x^3 + 3x^2 + 3x)$$

*Note: The student wrote some crossed-out lines here due to a calculation error:*
$$x^4 + 3x^3 + x^2 + 3x \quad \text{(crossed out)}$$
$$x^3 - 3x + 4 \quad \text{(crossed out)}$$
$$x^3 + x^2 + x \quad \text{(crossed out)}$$

### Third division (remainder $3x^3 + 3x^2 + 3x$ divided by the next remainder $4x^2 + 4x + 4$):
$$(3x^3 + 3x^2 + 3x) : (4x^2 + 4x + 4)$$
$$3x^3 + 3x^2 + 3x$$
$$0$$

### Greatest Common Divisor (circled):
$$4x^2 + 4x + 4 \quad \text{(circled)}$$

### Additional division on the far right (simplification/further step):
$$\frac{x+1}{x^4 + x^3 + x^2 + x}$$ (or similar division structure)