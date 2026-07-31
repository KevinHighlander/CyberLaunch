package com.cyberlaunch.os.domain

object FieldNotesPolicy {
    const val maxLength = 4_000

    fun sanitize(value: String): String =
        value
            .filter { character ->
                character == '\n' || character == '\t' || !character.isISOControl()
            }
            .take(maxLength)
}
