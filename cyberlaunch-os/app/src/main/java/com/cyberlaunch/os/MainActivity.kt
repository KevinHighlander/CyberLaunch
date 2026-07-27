package com.cyberlaunch.os

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import com.cyberlaunch.os.ui.CyberLaunchApp
import com.cyberlaunch.os.ui.theme.CyberLaunchTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            CyberLaunchTheme {
                CyberLaunchApp()
            }
        }
    }
}
