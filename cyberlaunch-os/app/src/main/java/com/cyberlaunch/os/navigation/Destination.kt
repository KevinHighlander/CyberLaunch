package com.cyberlaunch.os.navigation

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.Home
import androidx.compose.material.icons.outlined.Hub
import androidx.compose.material.icons.outlined.Password
import androidx.compose.material.icons.outlined.Rule
import androidx.compose.ui.graphics.vector.ImageVector

sealed class Destination(
    val route: String,
    val title: String,
    val icon: ImageVector,
) {
    data object Home : Destination("home", "Command Center", Icons.Outlined.Home)
    data object PasswordLab : Destination("password-lab", "Password Lab", Icons.Outlined.Password)
    data object IncidentResponse : Destination("incident-response", "IR Checklist", Icons.Outlined.Rule)
    data object NetworkBasics : Destination("network-basics", "Network Basics", Icons.Outlined.Hub)
}
