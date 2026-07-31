package com.cyberlaunch.os.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.cyberlaunch.os.domain.FieldNotesPolicy
import com.cyberlaunch.os.ui.components.ScreenHeader

@Composable
fun FieldNotesScreen(
    savedNotes: String,
    onSave: (String) -> Unit,
    onClear: () -> Unit,
    onBack: () -> Unit,
) {
    var draft by rememberSaveable(savedNotes) { mutableStateOf(savedNotes) }
    var showClearConfirmation by rememberSaveable { mutableStateOf(false) }
    val hasSavedOrDraftNotes = savedNotes.isNotEmpty() || draft.isNotEmpty()
    val hasUnsavedChanges = draft != savedNotes

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        ScreenHeader("Field Notes", onBack)
        Text(
            "Saved only on this device. Do not enter passwords, API keys, personal data, or real incident evidence.",
            color = MaterialTheme.colorScheme.tertiary,
            style = MaterialTheme.typography.bodyMedium,
        )
        OutlinedTextField(
            value = draft,
            onValueChange = { draft = FieldNotesPolicy.sanitize(it) },
            modifier = Modifier.fillMaxWidth(),
            label = { Text("Training notes") },
            placeholder = {
                Text("Record a command, concept, observation, or question to revisit.")
            },
            minLines = 10,
        )
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
        ) {
            Text(
                text = if (hasUnsavedChanges) "Unsaved changes" else "Saved locally",
                color = if (hasUnsavedChanges) {
                    MaterialTheme.colorScheme.tertiary
                } else {
                    MaterialTheme.colorScheme.primary
                },
                style = MaterialTheme.typography.labelLarge,
            )
            Text(
                "${draft.length}/${FieldNotesPolicy.maxLength}",
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                style = MaterialTheme.typography.bodyMedium,
            )
        }
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            Button(
                onClick = { onSave(draft) },
                enabled = hasUnsavedChanges,
                modifier = Modifier.weight(1f),
            ) {
                Text("Save notes")
            }
            OutlinedButton(
                onClick = { showClearConfirmation = true },
                enabled = hasSavedOrDraftNotes,
                modifier = Modifier.weight(1f),
            ) {
                Text("Clear")
            }
        }
    }

    if (showClearConfirmation) {
        AlertDialog(
            onDismissRequest = { showClearConfirmation = false },
            title = { Text("Clear field notes?") },
            text = { Text("This removes the saved note from this device.") },
            confirmButton = {
                TextButton(
                    onClick = {
                        draft = ""
                        onClear()
                        showClearConfirmation = false
                    },
                ) {
                    Text("Clear notes")
                }
            },
            dismissButton = {
                TextButton(onClick = { showClearConfirmation = false }) {
                    Text("Cancel")
                }
            },
        )
    }
}
