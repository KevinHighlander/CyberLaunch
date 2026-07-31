package com.cyberlaunch.os.ui

import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Scaffold
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.cyberlaunch.os.data.DataStoreTrainingRepository
import com.cyberlaunch.os.data.TrainingState
import com.cyberlaunch.os.domain.IncidentResponseChecklist
import com.cyberlaunch.os.navigation.Destination
import com.cyberlaunch.os.ui.components.CyberTopBar
import com.cyberlaunch.os.ui.screens.FieldNotesScreen
import com.cyberlaunch.os.ui.screens.HomeScreen
import com.cyberlaunch.os.ui.screens.IncidentResponseScreen
import com.cyberlaunch.os.ui.screens.NetworkBasicsScreen
import com.cyberlaunch.os.ui.screens.PasswordLabScreen
import com.cyberlaunch.os.ui.screens.SettingsScreen
import kotlinx.coroutines.launch

@Composable
fun CyberLaunchApp() {
    val context = LocalContext.current.applicationContext
    val navController = rememberNavController()
    val trainingRepository = remember(context) { DataStoreTrainingRepository(context) }
    val trainingState by trainingRepository.state.collectAsStateWithLifecycle(
        initialValue = TrainingState(),
    )
    val coroutineScope = rememberCoroutineScope()

    Scaffold(
        modifier = Modifier.fillMaxSize(),
        topBar = {
            CyberTopBar(onHomeClick = {
                navController.navigate(Destination.Home.route) {
                    popUpTo(Destination.Home.route) { inclusive = true }
                }
            })
        },
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = Destination.Home.route,
            modifier = Modifier.padding(innerPadding),
        ) {
            composable(Destination.Home.route) {
                HomeScreen(
                    checklistCompleted = trainingState.completedSteps.size,
                    checklistTotal = IncidentResponseChecklist.stepCount,
                    showSafetyReminder = trainingState.showSafetyReminder,
                    onOpenModule = { navController.navigate(it.route) },
                )
            }
            composable(Destination.PasswordLab.route) {
                PasswordLabScreen(onBack = { navController.popBackStack() })
            }
            composable(Destination.IncidentResponse.route) {
                IncidentResponseScreen(
                    completedSteps = trainingState.completedSteps,
                    onStepChanged = { step, isCompleted ->
                        coroutineScope.launch {
                            trainingRepository.setStepCompleted(step, isCompleted)
                        }
                    },
                    onReset = {
                        coroutineScope.launch {
                            trainingRepository.resetChecklist()
                        }
                    },
                    onBack = { navController.popBackStack() },
                )
            }
            composable(Destination.NetworkBasics.route) {
                NetworkBasicsScreen(onBack = { navController.popBackStack() })
            }
            composable(Destination.FieldNotes.route) {
                FieldNotesScreen(
                    savedNotes = trainingState.fieldNotes,
                    onSave = { notes ->
                        coroutineScope.launch {
                            trainingRepository.saveFieldNotes(notes)
                        }
                    },
                    onClear = {
                        coroutineScope.launch {
                            trainingRepository.clearFieldNotes()
                        }
                    },
                    onBack = { navController.popBackStack() },
                )
            }
            composable(Destination.Settings.route) {
                SettingsScreen(
                    showSafetyReminder = trainingState.showSafetyReminder,
                    onShowSafetyReminderChanged = { show ->
                        coroutineScope.launch {
                            trainingRepository.setShowSafetyReminder(show)
                        }
                    },
                    onBack = { navController.popBackStack() },
                )
            }
        }
    }
}
