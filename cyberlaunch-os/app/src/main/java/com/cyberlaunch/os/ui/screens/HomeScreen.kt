package com.cyberlaunch.os.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp
import com.cyberlaunch.os.navigation.Destination
import com.cyberlaunch.os.ui.components.ModuleCard

private val modules = listOf(
    Destination.PasswordLab to "Learn what makes a passphrase resilient.",
    Destination.IncidentResponse to "Practice the first steps of a calm response.",
    Destination.NetworkBasics to "Review ports, protocols, and defensive concepts.",
)

@Composable
fun HomeScreen(
    checklistCompleted: Int,
    checklistTotal: Int,
    onOpenModule: (Destination) -> Unit,
) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(
                Brush.verticalGradient(
                    listOf(MaterialTheme.colorScheme.background, MaterialTheme.colorScheme.surface),
                ),
            ),
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 20.dp, vertical = 24.dp),
        ) {
            Text("COMMAND CENTER", style = MaterialTheme.typography.displaySmall)
            Text(
                "A safe training environment for building practical cyber instincts.",
                style = MaterialTheme.typography.bodyLarge,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.padding(top = 8.dp),
            )

            Spacer(Modifier.height(24.dp))
            StatusPanel(
                checklistCompleted = checklistCompleted,
                checklistTotal = checklistTotal,
            )
            Spacer(Modifier.height(28.dp))

            Text("TRAINING MODULES", style = MaterialTheme.typography.labelLarge)
            Column(
                modifier = Modifier.padding(top = 12.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                modules.forEach { (destination, description) ->
                    ModuleCard(
                        title = destination.title,
                        description = description,
                        icon = destination.icon,
                        onClick = { onOpenModule(destination) },
                    )
                }
            }
        }
    }
}

@Composable
private fun StatusPanel(
    checklistCompleted: Int,
    checklistTotal: Int,
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .background(
                color = MaterialTheme.colorScheme.primary.copy(alpha = 0.08f),
                shape = MaterialTheme.shapes.large,
            )
            .padding(18.dp),
    ) {
        Text("SYSTEM STATUS", style = MaterialTheme.typography.labelLarge)
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(top = 12.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
        ) {
            StatusValue("MODE", "TRAINING")
            StatusValue(
                label = "IR PROGRESS",
                value = "$checklistCompleted/$checklistTotal",
                description = "Incident response: $checklistCompleted of $checklistTotal steps completed",
            )
            StatusValue("NETWORK", "OFFLINE")
        }
    }
}

@Composable
private fun StatusValue(
    label: String,
    value: String,
    description: String? = null,
) {
    Column(
        modifier = Modifier.semantics(mergeDescendants = true) {
            description?.let { contentDescription = it }
        },
    ) {
        Text(label, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
        Text(value, style = MaterialTheme.typography.titleMedium, color = MaterialTheme.colorScheme.primary)
    }
}
