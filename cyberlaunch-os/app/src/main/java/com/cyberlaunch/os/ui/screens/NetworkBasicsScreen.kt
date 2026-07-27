package com.cyberlaunch.os.ui.screens

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.cyberlaunch.os.ui.components.ScreenHeader

private data class NetworkConcept(val name: String, val summary: String, val defense: String)

private val concepts = listOf(
    NetworkConcept("DNS · 53", "Translates names into IP addresses.", "Use a trusted resolver and investigate unexpected answers."),
    NetworkConcept("HTTPS · 443", "Encrypts web traffic with TLS.", "Check certificate warnings instead of clicking through them."),
    NetworkConcept("SSH · 22", "Provides encrypted remote administration.", "Prefer keys, disable unused access, and restrict who can connect."),
    NetworkConcept("Least privilege", "Limits access to what a person or service needs.", "Review permissions and remove stale accounts regularly."),
)

@Composable
fun NetworkBasicsScreen(onBack: () -> Unit) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        ScreenHeader("Network Basics", onBack)
        Text(
            "Defensive reference cards—no device access or network scanning.",
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.padding(bottom = 4.dp),
        )
        concepts.forEach { concept ->
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                border = BorderStroke(1.dp, MaterialTheme.colorScheme.secondary.copy(alpha = 0.24f)),
            ) {
                Column(Modifier.padding(18.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                    Text(concept.name, style = MaterialTheme.typography.titleMedium, color = MaterialTheme.colorScheme.secondary)
                    Text(concept.summary)
                    Text("DEFENSE // ${concept.defense}", color = MaterialTheme.colorScheme.onSurfaceVariant)
                }
            }
        }
    }
}
