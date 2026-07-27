package com.cyberlaunch.os.ui

import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Scaffold
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.cyberlaunch.os.navigation.Destination
import com.cyberlaunch.os.ui.components.CyberTopBar
import com.cyberlaunch.os.ui.screens.HomeScreen
import com.cyberlaunch.os.ui.screens.IncidentResponseScreen
import com.cyberlaunch.os.ui.screens.NetworkBasicsScreen
import com.cyberlaunch.os.ui.screens.PasswordLabScreen

@Composable
fun CyberLaunchApp() {
    val navController = rememberNavController()

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
                HomeScreen(onOpenModule = { navController.navigate(it.route) })
            }
            composable(Destination.PasswordLab.route) {
                PasswordLabScreen(onBack = { navController.popBackStack() })
            }
            composable(Destination.IncidentResponse.route) {
                IncidentResponseScreen(onBack = { navController.popBackStack() })
            }
            composable(Destination.NetworkBasics.route) {
                NetworkBasicsScreen(onBack = { navController.popBackStack() })
            }
        }
    }
}
