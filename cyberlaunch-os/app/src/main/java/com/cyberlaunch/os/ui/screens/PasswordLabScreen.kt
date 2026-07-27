package com.cyberlaunch.os.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import com.cyberlaunch.os.domain.assessPassword
import com.cyberlaunch.os.ui.components.ScreenHeader

@Composable
fun PasswordLabScreen(onBack: () -> Unit) {
    var password by remember { mutableStateOf("") }
    val assessment = assessPassword(password)

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        ScreenHeader("Password Lab", onBack)
        Text(
            "Use a made-up example only. This training field never saves or sends what you type.",
            color = MaterialTheme.colorScheme.tertiary,
            style = MaterialTheme.typography.bodyMedium,
        )
        OutlinedTextField(
            value = password,
            onValueChange = { password = it },
            modifier = Modifier.fillMaxWidth(),
            label = { Text("Practice passphrase") },
            singleLine = true,
            visualTransformation = PasswordVisualTransformation(),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
        )
        LinearProgressIndicator(
            progress = { assessment.score / 5f },
            modifier = Modifier.fillMaxWidth(),
        )
        Text(
            "${assessment.label} · ${assessment.score}/5",
            style = MaterialTheme.typography.headlineSmall,
            color = MaterialTheme.colorScheme.primary,
        )
        assessment.feedback.forEach { Text("• $it") }
        Text(
            "Best practice: use a password manager, create a unique password for every account, and turn on multi-factor authentication.",
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}
