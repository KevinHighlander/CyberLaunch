package com.cyberlaunch.os.domain

import org.junit.Assert.assertEquals
import org.junit.Test

class ChecklistProgressTest {
    @Test
    fun updateAddsAndRemovesValidSteps() {
        val completed = ChecklistProgress.update(
            completed = setOf(0),
            step = 2,
            isCompleted = true,
            stepCount = 6,
        )

        assertEquals(setOf(0, 2), completed)
        assertEquals(
            setOf(2),
            ChecklistProgress.update(completed, step = 0, isCompleted = false, stepCount = 6),
        )
    }

    @Test
    fun invalidStepsAreIgnoredAndRemoved() {
        assertEquals(
            setOf(0, 5),
            ChecklistProgress.update(
                completed = setOf(-1, 0, 5, 6),
                step = 99,
                isCompleted = true,
                stepCount = 6,
            ),
        )
    }

    @Test
    fun storedValuesRoundTripAndDiscardCorruptEntries() {
        val decoded = ChecklistProgress.decode(
            stored = setOf("0", "2", "not-a-number", "-1", "8"),
            stepCount = 6,
        )

        assertEquals(setOf(0, 2), decoded)
        assertEquals(setOf("0", "2"), ChecklistProgress.encode(decoded, stepCount = 6))
    }
}

