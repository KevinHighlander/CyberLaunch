package com.cyberlaunch.os.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.selection.toggleable
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Checkbox
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.semantics.LiveRegionMode
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.liveRegion
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp
import com.cyberlaunch.os.domain.IncidentResponseChecklist
import com.cyberlaunch.os.ui.components.ScreenHeader

@Composable
fun IncidentResponseScreen(
    completedSteps: Set<Int>,
    onStepChanged: (step: Int, isCompleted: Boolean) -> Unit,
    onReset: () -> Unit,
    onBack: () -> Unit,
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        ScreenHeader("IR Checklist", onBack)
        Text(
            "A practice checklist for staying methodical under pressure.",
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        IncidentResponseChecklist.steps.forEachIndexed { index, step ->
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .toggleable(
                        value = index in completedSteps,
                        role = Role.Checkbox,
                        onValueChange = { checked -> onStepChanged(index, checked) },
                    ),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Checkbox(
                    checked = index in completedSteps,
                    onCheckedChange = null,
                )
                Text("${index + 1}. $step", modifier = Modifier.padding(start = 8.dp))
            }
        }
        Text(
            "${completedSteps.size}/${IncidentResponseChecklist.stepCount} practice steps complete",
            style = MaterialTheme.typography.labelLarge,
            color = MaterialTheme.colorScheme.primary,
            modifier = Modifier
                .padding(top = 12.dp)
                .semantics {
                    liveRegion = LiveRegionMode.Polite
                    contentDescription =
                        "Incident response: ${completedSteps.size} of " +
                        "${IncidentResponseChecklist.stepCount} steps completed"
                },
        )
        TextButton(
            onClick = onReset,
            enabled = completedSteps.isNotEmpty(),
            modifier = Modifier.align(Alignment.End),
        ) {
            Text("Reset checklist")
        }
    }
}
