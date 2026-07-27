package com.cyberlaunch.os.ui.components

import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.Security
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.semantics.Role
import androidx.compose.foundation.clickable
import androidx.compose.ui.unit.dp

@Composable
fun CyberTopBar(onHomeClick: () -> Unit) {
    Surface(color = MaterialTheme.colorScheme.background.copy(alpha = 0.96f)) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .clickable(role = Role.Button, onClick = onHomeClick)
                .padding(horizontal = 20.dp, vertical = 16.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Icon(
                imageVector = Icons.Outlined.Security,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.primary,
            )
            Text(
                text = " CYBERLAUNCH // OS",
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.primary,
            )
        }
    }
}
