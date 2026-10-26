
package com.example;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class CalculatorTest {

    private final Calculator calculator = new Calculator();

    @Test
    void testAdd() {
        assertEquals(5, calculator.add(2, 3));
        assertEquals(0, calculator.add(-1, 1));
    }

    @Test
    void testMultiply() {
        assertEquals(12, calculator.multiply(3, 4));
        assertEquals(0, calculator.multiply(2, 0));
    }
}
