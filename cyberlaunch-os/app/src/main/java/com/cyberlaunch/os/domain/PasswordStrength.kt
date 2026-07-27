package com.cyberlaunch.os.domain

data class PasswordAssessment(
    val score: Int,
    val label: String,
    val feedback: List<String>,
)

fun assessPassword(value: String): PasswordAssessment {
    if (value.isEmpty()) {
        return PasswordAssessment(0, "Waiting", listOf("Enter a made-up password or passphrase."))
    }

    val checks = listOf(
        value.length >= 12,
        value.length >= 16,
        value.any(Char::isLowerCase) && value.any(Char::isUpperCase),
        value.any(Char::isDigit),
        value.any { !it.isLetterOrDigit() },
    )
    val score = checks.count { it }
    val feedback = buildList {
        if (value.length < 12) add("Use at least 12 characters; longer is better.")
        if (value.length in 12..15) add("Try 16+ characters for a stronger passphrase.")
        if (value.all(Char::isLetter)) add("Mix in numbers or symbols when the site allows it.")
        if (size == 0) add("Good length and character variety. Keep it unique.")
    }
    val label = when (score) {
        5 -> "Strong"
        3, 4 -> "Developing"
        else -> "Weak"
    }
    return PasswordAssessment(score, label, feedback)
}
