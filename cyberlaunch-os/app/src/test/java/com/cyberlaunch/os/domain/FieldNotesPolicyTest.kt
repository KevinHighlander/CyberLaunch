package com.cyberlaunch.os.domain

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Test

class FieldNotesPolicyTest {
    @Test
    fun preservesReadableFormatting() {
        assertEquals(
            "DNS notes:\n\tCheck the resolver",
            FieldNotesPolicy.sanitize("DNS notes:\n\tCheck the resolver"),
        )
    }

    @Test
    fun removesUnsupportedControlCharacters() {
        val sanitized = FieldNotesPolicy.sanitize("safe\u0000note\u0007")

        assertEquals("safenote", sanitized)
        assertFalse(sanitized.any { it.isISOControl() })
    }

    @Test
    fun limitsStoredNoteLength() {
        val sanitized = FieldNotesPolicy.sanitize("x".repeat(FieldNotesPolicy.maxLength + 25))

        assertEquals(FieldNotesPolicy.maxLength, sanitized.length)
    }
}
