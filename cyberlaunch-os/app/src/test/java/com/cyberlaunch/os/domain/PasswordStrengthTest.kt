package com.cyberlaunch.os.domain

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class PasswordStrengthTest {
    @Test
    fun emptyValueWaitsForInput() {
        assertEquals("Waiting", assessPassword("").label)
    }

    @Test
    fun shortSimplePasswordIsWeak() {
        val result = assessPassword("password")
        assertEquals("Weak", result.label)
        assertTrue(result.feedback.any { it.contains("12 characters") })
    }

    @Test
    fun longVariedPassphraseIsStrong() {
        val result = assessPassword("Orbit-River-92!Comet")
        assertEquals("Strong", result.label)
        assertEquals(5, result.score)
    }
}
