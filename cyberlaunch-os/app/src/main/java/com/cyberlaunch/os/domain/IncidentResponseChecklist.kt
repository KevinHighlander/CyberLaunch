package com.cyberlaunch.os.domain

object IncidentResponseChecklist {
    val steps = listOf(
        "Pause and write down what you observed.",
        "Disconnect the affected device if active harm is occurring.",
        "Preserve evidence; avoid wiping or reinstalling immediately.",
        "Notify the responsible owner or incident lead.",
        "Change exposed credentials from a known-safe device.",
        "Record actions and times for the incident timeline.",
    )

    val stepCount: Int
        get() = steps.size
}

object ChecklistProgress {
    fun sanitize(completed: Set<Int>, stepCount: Int): Set<Int> =
        completed.filterTo(sortedSetOf()) { it in 0 until stepCount }

    fun update(
        completed: Set<Int>,
        step: Int,
        isCompleted: Boolean,
        stepCount: Int,
    ): Set<Int> {
        val validCompleted = sanitize(completed, stepCount)
        if (step !in 0 until stepCount) return validCompleted

        return if (isCompleted) {
            validCompleted + step
        } else {
            validCompleted - step
        }
    }

    fun encode(completed: Set<Int>, stepCount: Int): Set<String> =
        sanitize(completed, stepCount).mapTo(sortedSetOf()) { it.toString() }

    fun decode(stored: Set<String>, stepCount: Int): Set<Int> =
        sanitize(stored.mapNotNullTo(mutableSetOf(), String::toIntOrNull), stepCount)
}

