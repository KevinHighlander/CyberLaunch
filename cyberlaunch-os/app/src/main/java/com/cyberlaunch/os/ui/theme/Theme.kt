package com.cyberlaunch.os.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

private val CyberLaunchColors = darkColorScheme(
    primary = TerminalGreen,
    onPrimary = Night,
    secondary = SignalBlue,
    tertiary = WarningAmber,
    background = Night,
    onBackground = SoftWhite,
    surface = NightRaised,
    onSurface = SoftWhite,
    surfaceVariant = Color(0xFF142820),
    onSurfaceVariant = MutedGreen,
)

@Composable
fun CyberLaunchTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = CyberLaunchColors,
        typography = CyberLaunchTypography,
        content = content,
    )
}
