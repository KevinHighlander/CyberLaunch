package com.cyberlaunch.os.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Checkbox
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.cyberlaunch.os.ui.components.ScreenHeader

private val responseSteps = listOf(
    "Pause and write down what you observed.",
    "Disconnect the affected device if active harm is occurring.",
    "Preserve evidence; avoid wiping or reinstalling immediately.",
    "Notify the responsible owner or incident lead.",
    "Change exposed credentials from a known-safe device.",
    "Record actions and times for the incident timeline.",
)

@Composable
fun IncidentResponseScreen(onBack: () -> Unit) {
    val completed = remember { mutableStateListOf<Int>() }

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
        responseSteps.forEachIndexed { index, step ->
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Checkbox(
                    checked = index in completed,
                    onCheckedChange = { checked ->
                        if (checked) completed.add(index) else completed.remove(index)
                    },
                )
                Text("${index + 1}. $step", modifier = Modifier.padding(start = 8.dp))
            }
        }
        Text(
            "${completed.size}/${responseSteps.size} practice steps complete",
            style = MaterialTheme.typography.labelLarge,
            color = MaterialTheme.colorScheme.primary,
            modifier = Modifier.padding(top = 12.dp),
        )
    }
}
