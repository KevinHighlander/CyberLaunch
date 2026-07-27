package com.cyberlaunch.os.ui.theme

import androidx.compose.material3.Typography
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp

val CyberLaunchTypography = Typography(
    displaySmall = TextStyle(
        fontFamily = FontFamily.Monospace,
        fontWeight = FontWeight.Bold,
        fontSize = 32.sp,
        letterSpacing = (-1).sp,
    ),
    headlineSmall = TextStyle(
        fontFamily = FontFamily.Monospace,
        fontWeight = FontWeight.Bold,
        fontSize = 22.sp,
    ),
    titleMedium = TextStyle(
        fontFamily = FontFamily.Monospace,
        fontWeight = FontWeight.SemiBold,
        fontSize = 16.sp,
    ),
    bodyLarge = TextStyle(fontSize = 16.sp, lineHeight = 24.sp),
    bodyMedium = TextStyle(fontSize = 14.sp, lineHeight = 20.sp),
    labelLarge = TextStyle(
        fontFamily = FontFamily.Monospace,
        fontWeight = FontWeight.Bold,
        fontSize = 13.sp,
    ),
)
